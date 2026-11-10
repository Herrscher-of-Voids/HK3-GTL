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

/**
 * 【文件职责】整包启动后分帧导出真实注册表和最终配方，核对研究配方；不改研究、存档或玩家物品。
 * 【变更记录 #1】2026-09-30 00:54:01（第1次备注 · 内测5修订103）
 * 删除：无。新增：自动导出、管理员手动重导出、状态命令和中断/异常记录。
 * 修改：每帧最多64配方，软预算8ms；重载导致快照失效时拒绝通过。
 * 用途：给原版/增强版各自资源池提供可追溯候选；没有完成报告的目录一律不算验收通过。
 * 边界：配方存在不证明生存可得；不授予证据，不注册新结构，不读取玩家账户或世界种子。
 */
/**
 * 【变更记录 #2】2026-09-30 01:18:22（第2次备注 · 内测5修订104）
 * 删除：无。新增：配方表SHA256与预期计划ID清单；修改：报告修订号104。
 * 用途：新增合法配方后按实际清单核验，避免把旧250条常量当成永久完成标准。
 */
/**
 * 【变更记录 #3】2026-09-30 01:42:00（第3次备注 · 内测5修订106）
 * - 删除：无。新增：基础与序列化预期耗时及清单中的GTLCore倍率。
 * - 修改：报告修订号106；用途：追溯实例配置，继续严格核验，不修改旧报告。
 */
@Mod.EventBusSubscriber(modid = "hk3gtl")
/**
 * 【变更记录 #4】2026-09-30 02:20:26（第4次备注 · 内测5修订107）
 * 删除：本文件可执行代码中的旧电压键及常量引用，不保留旧键注册别名。
 * 新增：16档正式缩写作为唯一电压标识；逐文件映射见logs/voltage-keys-r107。
 * 修改：注册、配方、查询或标签引用按原tier序号一一迁移；数值、层级与资源内容保持原义。
 * 用途：避免显示名与实际注册键不一致；历史备注保留，旧存档不自动改写。
 */
/**
 * 【变更记录 #5】2026-09-30 03:24:34（内测5修订108）
 * 删除：无。新增：批准色卡接线及版本追溯。
 * 修改：导出报告修订号同步108，比较规则保持不变。
 * 用途：正确显示与核验，不修改研究逻辑。
 */
public final class Hk3ResearchRuntimeAudit {
    /** 【变更记录 #6】2026-10-17 17:12:35（第6次备注 · 修订165）：删除导出仍标163的旧修订身份；新增无；修改报告版本为165；用途：本轮新增材料与配方证据不得混记为旧实例验收，其他只读导出逻辑不变。 */
    /** 【变更记录 #7】2026-10-17 21:50:18（第7次备注 · 修订166）：删除固定165身份；新增无；修改只读导出修订为166；用途：新高度包的实例证据不可冒充旧包，其他合同保持原有核验。 */
    /**
     * 【变更记录 #8】2026-11-04 00:12:20（第8次备注 · 内测5修订193）
     * 删除：导出修订号固定为166的常量。新增：每轮从包内变更记录读取实际修订身份。
     * 修改：三个报告使用同一轮捕获值，资源缺失或无效时拒绝启动；用途：新包证据不得冒称历史版本，保留只读及分帧预算。
     */
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
            boolean gatesPassed = unchanged && errors.isEmpty() && gatesUnchanged && invalidResearchGates.isEmpty() && orphanBindings.isEmpty();
            gateReport.addProperty("passed", gatesPassed);
            write(directory.resolve("research-gates.json"), gateReport);
            JsonObject report = new JsonObject();
            report.addProperty("schema", 1); report.addProperty("revision", revision);
            report.addProperty("export_complete", true); report.addProperty("recipe_snapshot_unchanged", unchanged);
            report.addProperty("expected_process_recipes", plans.size()); report.addProperty("passed_process_recipes", passed);
            report.addProperty("process_recipe_audit_pass", unchanged && passed == plans.size());
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

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。

// 【变更记录 · 修订162】2026-10-17 14:41:11：新增完整配方类型及序列化器只读快照，以核验退役类型本身未注册；沿用分帧导出、哈希和现行工艺比对，不以配方数量为零代替类型退役。
// 【变更记录 · 修订163】2026-10-17 15:08:01：新增全配方全部研究门槛与批次元数据核验，单独列出非法条件及孤立绑定并校验导出期间不变；报告与新增文件一并哈希，不将注册通过冒充生存执行通过。
