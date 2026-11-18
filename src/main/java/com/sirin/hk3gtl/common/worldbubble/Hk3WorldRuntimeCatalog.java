package com.sirin.hk3gtl.common.worldbubble;

import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.gregtechceu.gtceu.api.capability.recipe.FluidRecipeCapability;
import com.gregtechceu.gtceu.api.capability.recipe.ItemRecipeCapability;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.recipe.RecipeHelper;
import com.mojang.brigadier.exceptions.CommandSyntaxException;
import com.mojang.logging.LogUtils;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.RegistryAccess;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.RecipeManager;
import net.minecraft.world.level.material.FlowingFluid;
import net.minecraftforge.event.OnDatapackSyncEvent;
import net.minecraftforge.event.server.ServerStartedEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.loading.FMLPaths;

import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Stream;

/** 以当前服务端最终配方构造资源池，重载后同步新配方与完整栈数据。 */
@Mod.EventBusSubscriber(modid = "hk3gtl")
public final class Hk3WorldRuntimeCatalog {
    public static final Hk3WorldResourceCatalog.Sampling SAMPLING =
            new Hk3WorldResourceCatalog.Sampling(120, 131072, 24, 131072);
    private record Supply(String kind, Hk3WorldResourceCatalog.Entry entry, boolean natural) {}
    private static final Map<MinecraftServer, Hk3WorldResourceCatalog> CATALOGS = new ConcurrentHashMap<>();
    private static final Set<String> EXCLUDED_TYPES = Set.of("gtceu:research_station", "gtceu:scanner",
            "ae2:matter_cannon", "ad_astra:space_station_recipe");
    private static final Set<String> ADMIN = Set.of("minecraft:air", "minecraft:barrier", "minecraft:command_block",
            "minecraft:chain_command_block", "minecraft:repeating_command_block", "minecraft:structure_block",
            "minecraft:structure_void", "minecraft:jigsaw", "minecraft:light", "minecraft:debug_stick", "minecraft:knowledge_book");
    private static final Map<String, Integer> AMOUNTS = Map.of(
            "gtceu:white_dwarf_mtter_dust", 16384, "gtceu:black_dwarf_mtter_dust", 16384,
            "gtceu:spacetime", 256, "gtceu:raw_star_matter_plasma", 1310720,
            "gtceu:quark_gluon_plasma", 1310720, "gtceu:heavy_quark_degenerate_matter_plasma", 1310720,
            "gtceu:neutronium", 13107200, "gtceu:heavy_lepton_mixture", 13107200);

    private Hk3WorldRuntimeCatalog() {}

    public static Hk3WorldResourceCatalog get(MinecraftServer server) {
        return CATALOGS.computeIfAbsent(server, Hk3WorldRuntimeCatalog::build);
    }

    @SubscribeEvent public static void started(ServerStartedEvent event) { get(event.getServer()); }
    @SubscribeEvent public static void stopped(ServerStoppedEvent event) { CATALOGS.remove(event.getServer()); }
    @SubscribeEvent public static void reloaded(OnDatapackSyncEvent event) {
        if (event.getPlayer() == null) {
            var server = event.getPlayerList().getServer();
            CATALOGS.put(server, build(server));
        }
    }

    private static Hk3WorldResourceCatalog build(MinecraftServer server) {
        return build(server.getRecipeManager(), server.registryAccess(), true);
    }

    public static Hk3WorldResourceCatalog preview(RecipeManager recipes, RegistryAccess registries) {
        return build(recipes, registries, false);
    }

    private static Hk3WorldResourceCatalog build(RecipeManager manager, RegistryAccess registries, boolean writeSnapshot) {
        var supplies = new TreeMap<String, Supply>();
        natural(supplies);
        var recipes = new ArrayList<>(manager.getRecipes());
        recipes.sort(java.util.Comparator.comparing(recipe -> recipe.getId().toString()));
        for (var recipe : recipes) {
            String type = BuiltInRegistries.RECIPE_TYPE.getKey(recipe.getType()).toString();
            if (recipe.getId().toString().contains("hk3gtl") || EXCLUDED_TYPES.contains(type)
                    || !Hk3RecipeResearchGate.getAllRequiredResearch(recipe.getId()).isEmpty()) continue;
            if (recipe instanceof GTRecipe gt) collect(gt, supplies);
            else if (!recipe.isSpecial() && recipe.getIngredients().stream().anyMatch(input -> !input.isEmpty())
                    && recipe.getIngredients().stream().filter(input -> !input.isEmpty())
                    .noneMatch(input -> Arrays.stream(input.getItems()).allMatch(Hk3WorldRuntimeCatalog::internal))) {
                var stack = recipe.getResultItem(registries);
                if (!stack.isEmpty()) add(supplies, "item", BuiltInRegistries.ITEM.getKey(stack.getItem()),
                        Hk3WorldResourceCatalog.itemData(stack), 0, recipe.getId() + "；当前注册生产配方，执行电压Tier0", false);
            }
        }
        var items = new ArrayList<Hk3WorldResourceCatalog.Entry>();
        var fluids = new ArrayList<Hk3WorldResourceCatalog.Entry>();
        supplies.values().forEach(supply -> (supply.kind().equals("item") ? items : fluids).add(supply.entry()));
        var mods = mods();
        var catalog = new Hk3WorldResourceCatalog("gtl-ulv-max-survival-runtime", version(mods), items, fluids, SAMPLING);
        if (writeSnapshot) export(catalog, supplies.values(), mods, recipes.size());
        return catalog;
    }

    private static void collect(GTRecipe recipe, Map<String, Supply> supplies) {
        int tier = recipe.data.contains("euTier", Tag.TAG_ANY_NUMERIC)
                ? recipe.data.getInt("euTier") : RecipeHelper.getRecipeEUtTier(recipe);
        if (tier > 14) return;
        var ic = ItemRecipeCapability.CAP;
        var fc = FluidRecipeCapability.CAP;
        var itemInputs = Stream.concat(recipe.getInputContents(ic).stream(), recipe.getTickInputContents(ic).stream()).toList();
        var fluidInputs = Stream.concat(recipe.getInputContents(fc).stream(), recipe.getTickInputContents(fc).stream()).toList();
        if (itemInputs.isEmpty() && fluidInputs.isEmpty()) return;
        if (itemInputs.stream().anyMatch(content -> ic.of(content.content).getItems().length == 0)
                || fluidInputs.stream().anyMatch(content -> fc.of(content.content).getStacks().length == 0)) return;
        if (itemInputs.stream().anyMatch(content -> Arrays.stream(ic.of(content.content).getItems())
                .allMatch(Hk3WorldRuntimeCatalog::internal))
                || fluidInputs.stream().anyMatch(content -> Arrays.stream(fc.of(content.content).getStacks())
                .allMatch(stack -> BuiltInRegistries.FLUID.getKey(stack.getFluid()).getNamespace().equals("hk3gtl")))) return;
        String source = recipe.id + "；当前注册生产配方，执行电压Tier" + tier;
        Stream.concat(recipe.getOutputContents(ic).stream(), recipe.getTickOutputContents(ic).stream())
                .filter(content -> content.chance > 0).forEach(content -> {
                    for (var stack : ic.of(content.content).getItems()) if (!stack.isEmpty())
                        add(supplies, "item", BuiltInRegistries.ITEM.getKey(stack.getItem()),
                                Hk3WorldResourceCatalog.itemData(stack), tier, source, false);
                });
        Stream.concat(recipe.getOutputContents(fc).stream(), recipe.getTickOutputContents(fc).stream())
                .filter(content -> content.chance > 0).forEach(content -> {
                    for (var stack : fc.of(content.content).getStacks()) if (stack.getAmount() > 0) {
                        var fluid = stack.getFluid();
                        var sourceFluid = fluid instanceof FlowingFluid flowing ? flowing.getSource() : fluid;
                        add(supplies, "fluid", BuiltInRegistries.FLUID.getKey(sourceFluid),
                                Hk3WorldResourceCatalog.fluidData(stack), tier, source, false);
                    }
                });
    }

    private static boolean internal(ItemStack stack) {
        return BuiltInRegistries.ITEM.getKey(stack.getItem()).getNamespace().equals("hk3gtl");
    }

    private static void natural(Map<String, Supply> supplies) {
        try (var reader = new InputStreamReader(Hk3WorldRuntimeCatalog.class.getResourceAsStream(
                "/data/hk3gtl/catalog/natural_supply_sources.json"), StandardCharsets.UTF_8)) {
            for (var raw : JsonParser.parseReader(reader).getAsJsonObject().getAsJsonArray("roots")) {
                var row = raw.getAsJsonObject();
                var id = new ResourceLocation(row.get("id").getAsString());
                String kind = row.get("kind").getAsString();
                if (kind.equals("item") ? BuiltInRegistries.ITEM.containsKey(id) : BuiltInRegistries.FLUID.containsKey(id))
                    add(supplies, kind, id, new CompoundTag(), row.get("tier").getAsInt(), row.get("source").getAsString(), true);
            }
        } catch (IOException failure) {
            throw new IllegalStateException("读取世界泡自然资源来源失败", failure);
        }
    }

    private static void add(Map<String, Supply> supplies, String kind, ResourceLocation id, CompoundTag stackData,
            int tier, String source, boolean natural) {
        if (id.getNamespace().equals("hk3gtl") || ADMIN.contains(id.toString())) return;
        int amount = AMOUNTS.getOrDefault(id.toString(), kind.equals("item") ? 131072 : 131072000);
        var entry = new Hk3WorldResourceCatalog.Entry(id.toString(), tier, source, amount, stackData);
        String key = kind + "/" + Hk3WorldResourceCatalog.identity(id.toString(), stackData);
        supplies.merge(key, new Supply(kind, entry, natural), (previous, next) ->
                previous.natural() || previous.entry().tier() <= next.entry().tier() ? previous : next);
    }

    private static JsonArray mods() {
        var mods = new JsonArray();
        ModList.get().getMods().stream().sorted(java.util.Comparator.comparing(mod -> mod.getModId())).forEach(mod -> {
            var row = new JsonObject(); row.addProperty("id", mod.getModId()); row.addProperty("version", mod.getVersion().toString());
            mods.add(row);
        });
        return mods;
    }

    private static String version(JsonArray mods) {
        var parts = new ArrayList<String>(); parts.add("runtime-v1");
        for (var raw : mods) {
            var row = raw.getAsJsonObject();
            if (Set.of("gtceu", "gtlcore", "gtl_enhancedcore").contains(row.get("id").getAsString()))
                parts.add(row.get("id").getAsString() + "=" + row.get("version").getAsString());
        }
        return String.join("/", parts);
    }

    private static void export(Hk3WorldResourceCatalog catalog, java.util.Collection<Supply> supplies,
            JsonArray mods, int recipeCount) {
        var data = new JsonObject(); data.addProperty("schema", 3); data.addProperty("profile", catalog.profile());
        data.addProperty("version", catalog.version()); data.addProperty("catalog_hash", catalog.hash());
        data.addProperty("generated_at", Instant.now().toString()); data.addProperty("recipe_manager_count", recipeCount);
        data.addProperty("scope", "当前服务端最终ULV～MAX生产配方与明确自然来源，完整栈数据区分变体；Tier为所列来源实际执行电压。");
        var sampling = new JsonObject(); sampling.addProperty("itemKinds", 120); sampling.addProperty("itemMax", 131072);
        sampling.addProperty("fluidKinds", 24); sampling.addProperty("fluidMaxBuckets", 131072); data.add("sampling", sampling);
        var roots = new JsonArray(); var processed = new JsonArray();
        int tagged = 0;
        for (var supply : supplies) {
            var entry = supply.entry(); var row = new JsonObject();
            row.addProperty("id", entry.id()); row.addProperty("kind", supply.kind()); row.addProperty("tier", entry.tier());
            row.addProperty("source", entry.survivalSource()); row.addProperty("amount", entry.amount());
            row.addProperty("stack_data", Hk3WorldResourceCatalog.canonical(entry.stackData()));
            row.addProperty("nbt", Hk3WorldResourceCatalog.canonical(entry.stackData().getCompound("tag")));
            if (!entry.stackData().isEmpty()) tagged++;
            (supply.natural() ? roots : processed).add(row);
        }
        data.add("roots", roots); data.add("processed", processed); data.add("mods", mods);
        var counts = new JsonObject(); counts.addProperty("items", catalog.items().size()); counts.addProperty("fluids", catalog.fluids().size());
        counts.addProperty("stack_data_variants", tagged); data.add("counts", counts);
        var directory = FMLPaths.GAMEDIR.get().resolve("logs/hk3gtl-world-resources");
        try {
            Files.createDirectories(directory);
            write(directory.resolve("current.json"), data);
            write(directory.resolve("current-diff.json"), Hk3WorldCatalogDiff.create(data));
        } catch (IOException | CommandSyntaxException failure) {
            LogUtils.getLogger().error("[HK3GTL] 写出当前世界泡资源目录失败", failure);
        }
    }

    private static void write(Path file, JsonObject data) throws IOException {
        var temporary = file.resolveSibling(file.getFileName() + ".tmp");
        Files.writeString(temporary, new GsonBuilder().setPrettyPrinting().disableHtmlEscaping().create().toJson(data), StandardCharsets.UTF_8);
        Files.move(temporary, file, StandardCopyOption.REPLACE_EXISTING, StandardCopyOption.ATOMIC_MOVE);
    }
}
