package com.sirin.hk3gtl.common.registration;

import com.google.gson.*;
import com.mojang.logging.LogUtils;
import com.sirin.hk3gtl.common.recipe.*;
import com.sirin.hk3gtl.common.research.Hk3ResearchRuntimeComparison;
import net.minecraft.commands.Commands;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.level.material.FlowingFluid;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.server.*;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.loading.FMLPaths;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.time.*;
import java.time.format.DateTimeFormatter;
import java.util.*;

 







 




 




@Mod.EventBusSubscriber(modid = "hk3gtl")
 






 





public final class Hk3ResearchRuntimeAudit {
     
     
     




    private static final Gson JSON = new GsonBuilder().disableHtmlEscaping().create();
    private static Job active;
    private static String lastStatus = "尚未运行实例配方核验";
    private Hk3ResearchRuntimeAudit() {}

    @SubscribeEvent public static void started(ServerStartedEvent event) { start(event.getServer()); }
    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || active == null || active.server != event.getServer()) return;
        try { if (active.step()) active = null; }
        catch (Exception failure) { active.fail(failure); active = null; }
    }
    @SubscribeEvent public static void stopped(ServerStoppingEvent event) {
        if (active != null && active.server == event.getServer()) {
            active.fail(new IOException("Server stopped before export completed")); active = null;
        }
    }
    @SubscribeEvent public static void commands(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("hk3researchaudit").requires(s -> s.hasPermission(2))
                .then(Commands.literal("status").executes(c -> {
                    c.getSource().sendSuccess(() -> Component.literal(status()), false); return 1;
                }))
                .then(Commands.literal("export").executes(c -> {
                    boolean accepted = start(c.getSource().getServer());
                    c.getSource().sendSuccess(() -> Component.literal(status()), false); return accepted ? 1 : 0;
                })));
    }
    private static String status() {
        return active == null ? lastStatus : "只读导出中：" + active.index + "/" + active.recipes.size() + "；" + active.directory;
    }
    private static boolean start(MinecraftServer server) {
        if (active != null) return false;
        try { active = new Job(server); return true; }
        catch (Exception failure) {
            lastStatus = "实例核验导出未启动：" + failure.getMessage();
            LogUtils.getLogger().error("[HK3GTL-RESEARCH-AUDIT] Could not start", failure); return false;
        }
    }

    private static final class Job {
        final MinecraftServer server;
        final int revision;
        final Path directory;
        final String processTableHash;
        final List<Recipe<?>> recipes;
        final Map<String, Hk3ResearchProcessPlans.Plan> plans = new TreeMap<>();
        final Set<String> seen = new HashSet<>();
        final JsonArray checks = new JsonArray(), errors = new JsonArray();
        final JsonArray researchGates = new JsonArray(), invalidResearchGates = new JsonArray();
        final JsonArray recipeCopyChecks = new JsonArray(), invalidRecipeCopies = new JsonArray();
        final Map<ResourceLocation, List<String>> gateSnapshot = com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate.snapshot();
        final BufferedWriter writer;
        int index, passed;
        Job(MinecraftServer server) throws Exception {
            this.server = server;
            try (var source = Hk3ResearchRuntimeAudit.class.getResourceAsStream("/assets/hk3gtl/changelog.json")) {
                if (source == null) throw new IOException("Missing bundled changelog");
                var entries = JsonParser.parseReader(new InputStreamReader(source, StandardCharsets.UTF_8))
                        .getAsJsonObject().getAsJsonArray("entries");
                revision = entries.get(0).getAsJsonObject().get("revision").getAsInt();
                if (revision < 1) throw new IOException("Invalid bundled revision");
            }
            try (var source = Hk3ResearchProcessPlans.class.getResourceAsStream("/data/hk3gtl/research/industrial_processes.json")) {
                if (source == null) throw new IOException("Missing bundled process table");
                processTableHash = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(source.readAllBytes()));
            }
            directory = FMLPaths.GAMEDIR.get().resolve("logs/hk3gtl-research-audit")
                    .resolve(LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd-HHmmss")) + "-" + UUID.randomUUID());
            Files.createDirectories(directory);
            recipes = new ArrayList<>(server.getRecipeManager().getRecipes());
            recipes.sort(Comparator.comparing(r -> r.getId().toString()));
            for (var plan : Hk3ResearchProcessPlans.all()) {
                var type = Hk3ResearchProcessTypes.get(plan.role());
                plans.put("hk3gtl:" + type.registryName.getPath() + "/" + plan.id(), plan);
            }
            write(directory.resolve("manifest.json"), manifest());
            write(directory.resolve("registries.json"), registries());
            writer = Files.newBufferedWriter(directory.resolve("recipes.jsonl"), StandardCharsets.UTF_8, StandardOpenOption.CREATE_NEW);
            LogUtils.getLogger().info("[HK3GTL-RESEARCH-AUDIT] Started read-only export: {}", directory);
        }
        // 只在服务器线程读取最终配方；单个不支持的第三方配方保留错误，不伪装成完整候选库。
        boolean step() throws Exception {
            long deadline = System.nanoTime() + 8_000_000L;
            int processed = 0;
            while (index < recipes.size() && processed++ < 64 && System.nanoTime() < deadline) {
                Recipe<?> recipe = recipes.get(index++);
                JsonObject row;
                try {
                    row = Hk3RuntimeRecipeSnapshot.read(recipe, server);
                    inspectResearchGates(recipe);
                    var plan = plans.get(recipe.getId().toString());
                    if (plan != null) { seen.add(recipe.getId().toString()); inspect(plan, row); }
                } catch (Exception failure) {
                    row = new JsonObject(); row.addProperty("id", recipe.getId().toString());
                    row.addProperty("export_error", failure.toString()); errors.add(row.deepCopy());
                }
                writer.write(JSON.toJson(row)); writer.newLine();
            }
            if (index < recipes.size()) return false;
            writer.close();
            for (var entry : plans.entrySet()) if (!seen.contains(entry.getKey())) inspect(entry.getValue(), null);
            boolean unchanged = server.getRecipeManager().getRecipes().size() == recipes.size()
                    && recipes.stream().allMatch(r -> server.getRecipeManager().byKey(r.getId()).orElse(null) == r);
            boolean gatesUnchanged = gateSnapshot.equals(com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate.snapshot());
            inspectRecipeCopies();
            JsonArray orphanBindings = new JsonArray();
            for (var key : gateSnapshot.keySet()) {
                ResourceLocation alternate = new ResourceLocation(key.getNamespace().equals("gtceu") ? "hk3gtl" : "gtceu", key.getPath());
                if (server.getRecipeManager().byKey(key).isEmpty() && server.getRecipeManager().byKey(alternate).isEmpty())
                    orphanBindings.add(key.toString());
            }
            JsonObject gateReport = new JsonObject();
            gateReport.addProperty("schema", 1); gateReport.addProperty("revision", revision);
            gateReport.addProperty("registered_gated_recipes", researchGates.size());
            gateReport.addProperty("snapshot_unchanged", gatesUnchanged);
            gateReport.add("recipes", researchGates); gateReport.add("invalid", invalidResearchGates);
            gateReport.add("orphan_bindings", orphanBindings);
            gateReport.add("recipe_copy_checks", recipeCopyChecks); gateReport.add("invalid_recipe_copies", invalidRecipeCopies);
            boolean gatesPassed = unchanged && errors.isEmpty() && gatesUnchanged && invalidResearchGates.isEmpty()
                    && orphanBindings.isEmpty() && invalidRecipeCopies.isEmpty();
            gateReport.addProperty("passed", gatesPassed);
            write(directory.resolve("research-gates.json"), gateReport);
            JsonObject report = new JsonObject();
            report.addProperty("schema", 1); report.addProperty("revision", revision);
            report.addProperty("export_complete", true); report.addProperty("recipe_snapshot_unchanged", unchanged);
            report.addProperty("expected_process_recipes", plans.size()); report.addProperty("passed_process_recipes", passed);
            report.addProperty("expected_research_recipe_copies", recipeCopyChecks.size());
            report.addProperty("passed_research_recipe_copies", recipeCopyChecks.size() - invalidRecipeCopies.size());
            report.addProperty("process_recipe_audit_pass", unchanged && passed == plans.size() && invalidRecipeCopies.isEmpty());
            report.addProperty("registered_recipe_export_complete", unchanged && errors.isEmpty());
            report.addProperty("research_gate_audit_pass", gatesPassed);
            report.addProperty("survival_catalog_verified", false); report.addProperty("gameplay_verified", false);
            report.addProperty("process_table_sha256", processTableHash);
            report.add("checks", checks); report.add("export_errors", errors);
            JsonObject hashes = new JsonObject();
            for (String file : List.of("manifest.json", "registries.json", "recipes.jsonl", "research-gates.json"))
                hashes.addProperty(file, sha256(directory.resolve(file)));
            report.add("sha256", hashes);
            report.addProperty("boundary", "Only recipe registration is checked. Survival sources, structures, actual task execution and delivery still need verification.");
            // 最后原子发布完成标志；异常目录仅保留failure.json，不会产生伪成功报告。
            Path temporary = directory.resolve("report.json.tmp"); write(temporary, report);
            try { Files.move(temporary, directory.resolve("report.json"), StandardCopyOption.ATOMIC_MOVE); }
            catch (AtomicMoveNotSupportedException e) { Files.move(temporary, directory.resolve("report.json")); }
            lastStatus = "研究配方核验 " + passed + "/" + plans.size() + "；快照" + (unchanged ? "有效" : "已因重载失效")
                    + "；第三方导出错误 " + errors.size() + "；报告：" + directory;
            LogUtils.getLogger().info("[HK3GTL-RESEARCH-AUDIT] {}", lastStatus);
            return true;
        }
        private void inspectRecipeCopies() {
            for (var source : gateSnapshot.entrySet()) {
                if (server.getRecipeManager().byKey(source.getKey()).isEmpty()) continue;
                for (var copyId : com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate.copiesOf(source.getKey())) {
                    var copy = server.getRecipeManager().byKey(copyId);
                    var actual = copy.map(recipe -> recipe instanceof com.gregtechceu.gtceu.api.recipe.GTRecipe gt
                            ? com.sirin.hk3gtl.common.research.Hk3RecipeAccess.effectiveRequirements(gt).requirements()
                            : com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate.getAllRequiredResearch(copyId)).orElse(List.of());
                    var row = new JsonObject();
                    row.addProperty("source", source.getKey().toString()); row.addProperty("copy", copyId.toString());
                    var expectedGates = new JsonArray(); source.getValue().stream().sorted().forEach(expectedGates::add);
                    var actualGates = new JsonArray(); actual.stream().sorted().forEach(actualGates::add);
                    row.add("expected_requirements", expectedGates); row.add("actual_requirements", actualGates);
                    boolean valid = copy.isPresent() && actual.containsAll(source.getValue());
                    row.addProperty("passed", valid); recipeCopyChecks.add(row);
                    if (!valid) invalidRecipeCopies.add(row.deepCopy());
                }
            }
        }
        /** 同时检查批次元数据和注册表；只读核验，不补研究、物品或团队权限。 */
        private void inspectResearchGates(Recipe<?> recipe) {
            var effective = recipe instanceof com.gregtechceu.gtceu.api.recipe.GTRecipe gt
                    ? com.sirin.hk3gtl.common.research.Hk3RecipeAccess.effectiveRequirements(gt)
                    : com.sirin.hk3gtl.common.research.Hk3ResearchRequirementPolicy.collect(
                            com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate.getAllRequiredResearch(recipe.getId()),
                            List.of(), false, com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate::isCurrentResearchId);
            if (effective.requirements().isEmpty() && effective.valid()) return;
            JsonObject row = new JsonObject(); row.addProperty("id", recipe.getId().toString());
            JsonArray requirements = new JsonArray(), invalid = new JsonArray();
            effective.requirements().forEach(requirements::add); effective.invalid().forEach(invalid::add);
            row.add("requirements", requirements); row.add("invalid", invalid); researchGates.add(row);
            if (!effective.valid()) invalidResearchGates.add(row.deepCopy());
        }
        private void inspect(Hk3ResearchProcessPlans.Plan plan, JsonObject actual) {
            JsonObject check = new JsonObject(); check.addProperty("plan", plan.id()); check.addProperty("role", plan.role());
            try {
                var expectedRecipe = Hk3ResearchProcessRecipes.expected(plan);
                JsonObject expected = Hk3RuntimeRecipeSnapshot.read(expectedRecipe, server);
                check.addProperty("base_duration_ticks", plan.ticks());
                check.addProperty("expected_serialized_duration_ticks", expectedRecipe.duration);
                JsonArray gates = new JsonArray(); plan.requirements().stream().sorted().forEach(gates::add);
                expected.add("gates", gates); // 必须来自批准目录，不能把运行时门槛当作期望值。
                var differences = Hk3ResearchRuntimeComparison.compare(expected, actual);
                JsonArray failures = new JsonArray(); differences.forEach(failures::add);
                check.add("failures", failures); check.add("expected", expected);
                if (differences.isEmpty()) passed++;
            } catch (Exception failure) { check.addProperty("audit_error", failure.toString()); }
            checks.add(check);
        }
        private JsonObject manifest() {
            JsonObject m = new JsonObject(); m.addProperty("schema", 1); m.addProperty("revision", revision);
            m.addProperty("captured_at", OffsetDateTime.now().toString());
            m.addProperty("recipe_count", recipes.size());
            m.addProperty("process_table_sha256", processTableHash);
            // 增强版3.5已删除旧倍率字段；真实耗时仍由独立计划序列化核验。
            m.addProperty("gtlcore_duration_multiplier_source", "不读取已退出的旧版配置字段；以本轮独立计划序列化耗时核验");
            m.addProperty("duration_expectation_source", "Independent plan builder.toJson; actual recipe never supplies expected duration");
            JsonArray planIds = new JsonArray(); plans.values().stream().map(Hk3ResearchProcessPlans.Plan::id).sorted().forEach(planIds::add);
            m.add("expected_process_plan_ids", planIds);
            JsonArray mods = new JsonArray();
            ModList.get().getMods().stream().sorted(Comparator.comparing(mod -> mod.getModId())).forEach(mod -> {
                JsonObject v = new JsonObject(); v.addProperty("id", mod.getModId());
                v.addProperty("version", mod.getVersion().toString()); mods.add(v);
            });
            m.add("mods", mods);
            m.addProperty("catalog_status", "CANDIDATES_ONLY_NOT_AN_APPROVED_DROP_POOL");
            m.addProperty("not_exported", "Loot tables, world generation and dynamic machine recipes require separate survival-source review.");
            m.addProperty("ordinary_recipe_limit", "Generic ingredient/result view may omit custom recipe constraints. Review before survival classification.");
            m.addProperty("excluded_private_data", "No player inventories, account IDs, world seed or world name exported.");
            return m;
        }
        void fail(Exception failure) {
            try { writer.close(); } catch (Exception ignored) { }
            try {
                JsonObject error = new JsonObject(); error.addProperty("export_complete", false);
                error.addProperty("error", failure.toString()); error.addProperty("exported_rows", index);
                write(directory.resolve("failure.json"), error);
            } catch (Exception ignored) { }
            lastStatus = "核验未完成：" + directory;
            LogUtils.getLogger().error("[HK3GTL-RESEARCH-AUDIT] Export incomplete: {}", directory, failure);
        }
    }
    private static JsonObject registries() {
        JsonObject result = new JsonObject(); JsonArray items = new JsonArray(), fluids = new JsonArray();
        BuiltInRegistries.ITEM.keySet().stream().sorted(Comparator.comparing(Object::toString)).forEach(id -> items.add(id.toString()));
        BuiltInRegistries.FLUID.keySet().stream().sorted(Comparator.comparing(Object::toString)).forEach(id -> {
            var fluid = BuiltInRegistries.FLUID.get(id); JsonObject row = new JsonObject();
            row.addProperty("id", id.toString());
            row.addProperty("canonical_source", BuiltInRegistries.FLUID.getKey(fluid instanceof FlowingFluid flowing ? flowing.getSource() : fluid).toString());
            fluids.add(row);
        });
        JsonArray recipeTypes = new JsonArray(), recipeSerializers = new JsonArray();
        BuiltInRegistries.RECIPE_TYPE.keySet().stream().sorted(Comparator.comparing(Object::toString))
                .forEach(id -> recipeTypes.add(id.toString()));
        BuiltInRegistries.RECIPE_SERIALIZER.keySet().stream().sorted(Comparator.comparing(Object::toString))
                .forEach(id -> recipeSerializers.add(id.toString()));
        result.add("items", items); result.add("fluids", fluids);
        result.add("recipe_types", recipeTypes); result.add("recipe_serializers", recipeSerializers);
        return result;
    }
    private static void write(Path path, JsonObject value) throws IOException {
        try (var out = Files.newBufferedWriter(path, StandardCharsets.UTF_8, StandardOpenOption.CREATE_NEW)) { JSON.toJson(value, out); }
    }
    private static String sha256(Path path) throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        try (var in = Files.newInputStream(path)) { byte[] bytes = new byte[65536]; int n; while ((n = in.read(bytes)) != -1) digest.update(bytes, 0, n); }
        return HexFormat.of().formatHex(digest.digest());
    }
}

 

 
 
