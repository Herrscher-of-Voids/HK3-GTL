package com.sirin.hk3gtl.common.integration;

import appeng.api.crafting.PatternDetailsHelper;
import appeng.api.stacks.AEItemKey;
import appeng.api.stacks.GenericStack;
import com.google.gson.JsonParser;
import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.registry.GTRegistries;
import com.gregtechceu.gtceu.common.block.LampBlock;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LiquidLineLayout;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3StructureBlocks;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.BedBlock;
import net.minecraft.world.level.block.DoorBlock;
import net.minecraft.world.level.block.LightBlock;
import net.minecraft.world.level.block.LiquidBlock;
import net.minecraft.world.level.block.SlabBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BedPart;
import net.minecraft.world.level.block.state.properties.DoubleBlockHalf;
import net.minecraft.world.level.block.state.properties.Property;
import net.minecraft.world.level.block.state.properties.SlabType;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import org.gtlcore.gtlcore.integration.ae2.pattern.MultiblockPatternEncoding;

import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@Mod.EventBusSubscriber(modid = "hk3gtl", bus = Mod.EventBusSubscriber.Bus.MOD)
public final class Hk3MultiblockPatternLibrary {
    private static final String PREFIX = "hk3gtl:multiblock_pattern:";

    private record Material(String state, long count) {}
    private record Blueprint(String controller, List<Material> materials) {}

    private Hk3MultiblockPatternLibrary() {}

    @SubscribeEvent
    public static void setup(FMLCommonSetupEvent event) {
        if (ModList.get().isLoaded("ftbquests")) event.enqueueWork(Ftb::register);
    }

    private static final class Catalog {
        static final Map<String, Blueprint> ENTRIES = read();

        private static Map<String, Blueprint> read() {
            var result = new LinkedHashMap<String, Blueprint>();
            try (var input = Hk3MultiblockPatternLibrary.class.getResourceAsStream(
                    "/data/hk3gtl/catalog/multiblock_pattern_library.json");
                 var reader = new InputStreamReader(input, StandardCharsets.UTF_8)) {
                for (var raw : JsonParser.parseReader(reader).getAsJsonArray()) {
                    var row = raw.getAsJsonObject();
                    var materials = new ArrayList<Material>();
                    for (var value : row.getAsJsonArray("materials")) {
                        var material = value.getAsJsonObject();
                        materials.add(new Material(material.get("state").getAsString(), material.get("count").getAsLong()));
                    }
                    result.put(row.get("key").getAsString(), new Blueprint(row.get("controller").getAsString(), materials));
                }
            } catch (IOException failure) {
                throw new IllegalStateException("读取多方块样板库失败", failure);
            }
            return result;
        }
    }

    private static List<ItemStack> patterns(String key) {
        var blueprint = Catalog.ENTRIES.get(key);
        var materials = new LinkedHashMap<AEItemKey, Long>();
        for (var material : blueprint.materials()) {
            if (!material.state().split("\\[", 2)[0].equals(blueprint.controller()))
                add(materials, state(material.state()), material.count());
        }
        if (key.equals("network_injector")) {
            var layout = Hk3LiquidLineLayout.create(Hk3LiquidLineLayout.Kind.INJECTION);
            layout.counts().forEach((symbol, count) -> {
                if (layout.materials().containsKey(symbol))
                    add(materials, Hk3StructureBlocks.require(layout.materials().get(symbol)).defaultBlockState(), count);
            });
        }
        var inputs = materials.entrySet().stream().map(entry -> new GenericStack(entry.getKey(), entry.getValue())).toList();
        var definition = (MultiblockMachineDefinition) GTRegistries.MACHINES.get(new ResourceLocation(blueprint.controller()));
        var output = (AEItemKey) MultiblockPatternEncoding.outputs(definition).get(0).what();
        int parts = (inputs.size() + 80) / 81;
        var result = new ArrayList<ItemStack>();
        for (int part = 0; part < parts; part++) {
            var book = output.toStack();
            if (parts > 1) book.setHoverName(Component.translatable("hk3gtl.pattern_library.order_part",
                    Component.translatable(definition.getId().toLanguageKey("block")), part + 1, parts));
            var pattern = PatternDetailsHelper.encodeProcessingPattern(
                    inputs.subList(part * 81, Math.min(inputs.size(), (part + 1) * 81)).toArray(GenericStack[]::new),
                    new GenericStack[]{GenericStack.fromItemStack(book)});
            pattern.setHoverName(Component.translatable("hk3gtl.pattern_library.pattern",
                    Component.translatable(definition.getId().toLanguageKey("block")), part + 1, parts));
            result.add(pattern);
        }
        return result;
    }

    private static void add(Map<AEItemKey, Long> materials, BlockState state, long count) {
        if (state.getBlock() instanceof DoorBlock && state.getValue(DoorBlock.HALF) == DoubleBlockHalf.UPPER
                || state.getBlock() instanceof BedBlock && state.getValue(BedBlock.PART) == BedPart.HEAD) return;
        ItemStack stack = new ItemStack(state.getBlock());
        if (state.getBlock() instanceof LampBlock lamp) stack.setTag(lamp.getTagFromState(state));
        if (state.getBlock() instanceof LightBlock)
            stack = LightBlock.setLightOnStack(stack, state.getValue(LightBlock.LEVEL));
        if (state.getBlock() instanceof SlabBlock && state.getValue(SlabBlock.TYPE) == SlabType.DOUBLE) count *= 2;
        if (state.getBlock() instanceof LiquidBlock && state.getFluidState().isSource())
            stack = new ItemStack(state.getFluidState().getType().getBucket());
        if (!stack.isEmpty()) materials.merge(AEItemKey.of(stack), count, Long::sum);
    }

    private static BlockState state(String text) {
        int bracket = text.indexOf('[');
        var state = Hk3StructureBlocks.require(bracket < 0 ? text : text.substring(0, bracket)).defaultBlockState();
        if (bracket >= 0) for (var entry : text.substring(bracket + 1, text.length() - 1).split(",")) {
            var pair = entry.split("=");
            state = property(state, state.getBlock().getStateDefinition().getProperty(pair[0]), pair[1]);
        }
        return state;
    }

    private static <T extends Comparable<T>> BlockState property(BlockState state, Property<T> property, String value) {
        return state.setValue(property, property.getValue(value).orElseThrow());
    }

    private static final class Ftb {
        static void register() {
            dev.ftb.mods.ftbquests.events.CustomRewardEvent.EVENT.register(event -> {
                for (var tag : event.getReward().getTags()) if (tag.startsWith(PREFIX)) {
                    var patterns = patterns(tag.substring(PREFIX.length()));
                    for (var pattern : patterns) {
                        event.getPlayer().getInventory().add(pattern);
                        if (!pattern.isEmpty()) event.getPlayer().drop(pattern, false);
                    }
                }
                return dev.architectury.event.EventResult.pass();
            });
        }
    }
}
