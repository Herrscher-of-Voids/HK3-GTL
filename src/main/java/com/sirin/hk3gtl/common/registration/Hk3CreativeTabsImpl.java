package com.sirin.hk3gtl.common.registration;



import com.gregtechceu.gtceu.api.data.chemical.ChemicalHelper;
import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.sirin.hk3gtl.common.block.Hk3Blocks;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.item.Hk3CircuitItems;
import com.sirin.hk3gtl.common.material.SouliumMaterial;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

import java.util.Arrays;
import java.util.Comparator;
import java.util.HashSet;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * 创造模式物品栏注册 —— 模组只暴露一个主 Tab（hk3gtl.main），其余分类不再强制分组。
 *
 * <h3>展示顺序</h3>
 * <ol>
 *   <li>电路（崩坏能 + 正式 16 档细分电路；其余注册物为归档占位，不出现在本 Tab）</li>
 *   <li>部件（八大件：马达/活塞/泵/传送带/机械臂/力场/发射器/传感器）</li>
 *   <li>多方块控制器</li>
 *   <li>方块（机壳/玻璃/线圈/结构/仓）</li>
 *   <li>物品（材料/功能性/杂项）</li>
 * </ol>
 */
public class Hk3CreativeTabsImpl {

    private static final Logger LOGGER = LogUtils.getLogger();
    private static int hk3gtl$displayInvocationCount;
    private static volatile List<ItemStack> cachedDisplayItems;

    /** 创造页签延迟注册器 */
    public static final DeferredRegister<CreativeModeTab> TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, Hk3Constants.MOD_ID);

    /** 部件物品前缀列表，用于识别哪些物品属于"部件"类别 */
    private static final String[] COMPONENT_PREFIXES = {
            "electric_motor_", "electric_piston_", "electric_pump_",
            "conveyor_module_", "robot_arm_", "field_generator_",
            "emitter_", "sensor_"
    };

    /** 崩坏能电路按电压等级排序（ULV~MAX） */
    private static final String[] HONKAI_CIRCUIT_TIER_ORDER = {
            "ulv", "lv", "mv", "hv", "ev",
            "iv", "luv", "zpm", "uv", "uhv",
            "uev", "uiv", "uxv", "opv", "max"
    };

    /** 正式细分电路 16 档（与语言/标签 canonical 一致；创造栏只展示这些，其余 48 个注册物不列出） */
    private static final String[] CANONICAL_DETAILED_CIRCUIT_PATHS = {
            "abyss_1_processor",
            "abyss_2_assembly",
            "abyss_3_computer",
            "abyss_4_processor_mainframe",
            "imaginary_1_processor",
            "imaginary_2_assembly",
            "imaginary_3_computer",
            "imaginary_4_processor_mainframe",
            "quantum_1_processor",
            "quantum_2_assembly",
            "quantum_3_computer",
            "quantum_4_processor_mainframe",
            "finality_1_processor",
            "finality_2_assembly",
            "finality_3_computer",
            "finality_4_processor_mainframe"
    };

    private static final String[] COMPONENT_TYPE_ORDER = {
            "electric_motor", "electric_piston", "electric_pump", "conveyor_module",
            "robot_arm", "field_generator", "emitter", "sensor"
    };

    private static final String[] COMPONENT_STAGE_ORDER = {
            "abyss_1", "abyss_2", "abyss_3", "abyss_4",
            "imaginary_1", "imaginary_2", "imaginary_3", "imaginary_4",
            "quantum_1", "quantum_2", "quantum_3", "quantum_4",
            "finality_1", "finality_2", "finality_3", "finality_4"
    };

    private static final String[] BLOCK_ORDER = {
            "casing_soulium",
            "casing_reinforced_soulium",
            "casing_abyss_mechanical",
            "casing_abyss_research",
            "casing_abyss_energy",
            "casing_imaginary_tree",
            "casing_imaginary_lattice",
            "casing_imaginary_core",
            "casing_imaginary_anchor",
            "casing_imaginary_weave",
            "casing_quantum_sea",
            "casing_quantum_bubble",
            "casing_quantum_flux",
            "casing_quantum_entangle",
            "casing_quantum_shipboard",
            "casing_finality_void",
            "casing_finality_sanctum",
            "casing_finality_dominion",
            "casing_finality_hyperion",
            "casing_finality_wonder",
            "glass_honkai_stabilized",
            "coil_abyss_flux",
            "structure_abyss_cooling_unit",
            "structure_communication_array",
            "structure_data_pillar"
    };

    private static final String[] PRIMARY_ITEM_ORDER = {
            "raw_honkai_particle",
            "honkai_energy_crystal",
            "stabilized_honkai_crystal",
            "compressed_honkai_core",
            "honkai_fuel_rod",
            "dense_honkai_fuel_rod",
            "honkai_suppressant",
            "gaze_buffer_unit",
            "advanced_gaze_buffer_unit",
            "schicksal_imaginary_core",
            "anti_entropy_imaginary_core",
            "fluid_alloy",
            "fluid_alloy_block",
            "nano_ceramic",
            "phase_transfer_mirror",
            "einstein_ringmagnet",
            "superconductive_metal_hydrogen",
            "soulium_precursor_mix",
            "activated_nano_matrix",
            "soulium_proto_mass",
            "stabilized_soulium_proto_mass",
            "oriented_soulium_component",
            "artifact_void_archives",
            "data_precivilization_fragment",
            "abyss_energy_modulator",
            "abyss_data_core",
            "abyss_stable_frame",
            "abyss_reactor_core",
            "abyss_measurement_array",
            "reactor_stabilizer",
            "ancient_legacy",
            "ancient_will",
            "data_research_package",
            "world_bubble_sample"
    };

    /** 60 台多方块控制器清单（v0.3，与 Hk3Machines*Stage 注册严格一致） */
    private static final String[] MULTIBLOCK_CONTROLLER_PATHS = {
            // ── P1 核心 4 台 ──
            "honkai_absorption_tower",
            "honkai_crystal_condenser",
            "soulium_smeltery",
            "abyss_research_analysis_matrix",
            // ── Max 4 台 ──
            "void_archives_analysis_chamber",
            "reason_reconstruction_array",
            "honkai_eu_converter",
            "honkai_network_injector",
            "abyss_circuit_foundry",
            // ── 海渊 4 台 ──
            "large_honkai_reactor",
            "abyss_deep_smeltery",
            "abyss_precision_workshop",
            "abyss_particle_research_ring",
            // ── 虚数 12 台 ──
            "imaginary_dimension_gateway",
            "imaginary_tree_observation_array",
            "imaginary_anchor_device",
            "sea_of_quanta_observatory",
            "imaginary_circuit_computation_sanctum",
            "soulium_superstructure_forge",
            "civilization_exchange_council_hub",
            "precivilization_database_decoder",
            "honkai_phase_purification_plant",
            "dual_energy_stable_supply_station",
            "imaginary_dream_furnace",
            "imaginary_matter_weaver",
            // ── 量子 12 台 ──
            "quantum_entanglement_computer",
            "thousand_realms_train",
            "world_bubble_meltdown_furnace",
            "quantum_superconductor_lattice_factory",
            "honkai_wireless_transit_hub",
            "quantum_thought_forge",
            "divine_key_gallery",
            "quantum_civilization_trade_port",
            "quantum_honkai_fusion_ring",
            "finality_pressure_buffer_array",
            "wonder_construction_simulation_platform",
            "quantum_precision_assembly_factory",
            // ── 终焉 12 台 ──
            "hyperion_flagship",
            "shipboard_finality_observation",
            "shipboard_dual_energy_reactor_deck",
            "shipboard_civilization_coordination_hall",
            "shipboard_divine_key_shrine",
            "finality_civilization_construction_works",
            "civilization_validation_matrix",
            "finality_civilization_power_hub",
            "finality_ultimate_material_forge",
            "finality_honkai_annihilation_ring",
            "graduation_permission_verification_altar",
            "civilization_wonder_sanctum",
            // ── 奇观 12 台 ──
            "honkai_ultimate_fusion_core",
            "divine_key_grand_cathedral",
            "civilization_judgment_corridor",
            "civilization_memory_eternal_monument",
            "myriad_realms_communication_nexus",
            "destiny_loom",
            "civilization_eye_observation_array",
            "cycle_narrator_platform",
            "civilization_starship_museum",
            "proof_of_existence_memorial",
            "ultimate_meditation_sanctum",
            "grand_convergence_altar"
    };

    // ═══════════════════════════════════════
    //  唯一的主 Tab
    // ═══════════════════════════════════════
    public static final RegistryObject<CreativeModeTab> MAIN_TAB = TABS.register("main",
            () -> CreativeModeTab.builder()
                    .title(Component.translatable("itemGroup.hk3gtl.main"))
                    .icon(() -> {
                        RegistryObject<Item> hv = Hk3CircuitItems.getHonkaiCircuit("hv");
                        if (hv != null && hv.isPresent()) return new ItemStack(hv.get());
                        try {
                            ItemStack ingot = ChemicalHelper.get(TagPrefix.ingot, SouliumMaterial.SOULIUM);
                            if (!ingot.isEmpty()) return ingot;
                        } catch (Exception ignored) {}
                        return new ItemStack(Items.IRON_INGOT);
                    })
                    .displayItems((params, output) -> {
                        long started = System.nanoTime();
                        List<ItemStack> items = cachedDisplayItems;
                        if (items == null) {
                            synchronized (Hk3CreativeTabsImpl.class) {
                                items = cachedDisplayItems;
                                if (items == null) {
                                    items = buildDisplayItems();
                                    cachedDisplayItems = items;
                                }
                            }
                        }
                        items.forEach(stack -> output.accept(stack.copy()));
                        int invocation = ++hk3gtl$displayInvocationCount;
                        if (invocation <= 3) {
                            LOGGER.info("[DEBUG] 创造页签 displayItems 耗时={}ms, invocation={}",
                                    (System.nanoTime() - started) / 1_000_000L, invocation);
                        }
                    })
                    .build()
    );

    // ═══════════════════════════════════════
    //  辅助方法
    // ═══════════════════════════════════════

    private static List<ItemStack> buildDisplayItems() {
        List<ItemStack> items = new java.util.ArrayList<>();
        appendItems(items, Hk3CreativeTabsImpl::emitOrderedCircuitItems);
        appendItems(items, Hk3CreativeTabsImpl::emitOrderedComponentItems);
        collectMultiblockPaths().forEach(path -> addItem(items, path));
        appendItems(items, list -> emitOrderedPaths(list, Arrays.asList(BLOCK_ORDER)));
        Set<String> excludedPaths = collectExcludedItemPaths();
        appendItems(items, list -> emitOrderedPaths(list, Arrays.asList(PRIMARY_ITEM_ORDER)));
        collectRemainingItemPaths(excludedPaths).forEach(path -> addItem(items, path));
        addMaterialItems(items, SouliumMaterial.SOULIUM);
        return List.copyOf(items);
    }

    private static void appendItems(List<ItemStack> items, java.util.function.Consumer<List<ItemStack>> appender) {
        appender.accept(items);
    }

    private static void addItem(List<ItemStack> items, String path) {
        Item item = BuiltInRegistries.ITEM.get(asResource(path));
        if (item != Items.AIR) items.add(new ItemStack(item));
    }

    private static void emitOrderedCircuitItems(List<ItemStack> items) {
        for (String tier : HONKAI_CIRCUIT_TIER_ORDER) {
            RegistryObject<Item> circuit = Hk3CircuitItems.getHonkaiCircuit(tier);
            if (circuit != null && circuit.isPresent()) items.add(new ItemStack(circuit.get()));
        }
        for (String path : CANONICAL_DETAILED_CIRCUIT_PATHS) addItem(items, path);
    }

    private static void emitOrderedComponentItems(List<ItemStack> items) {
        for (String componentType : COMPONENT_TYPE_ORDER) {
            for (String stage : COMPONENT_STAGE_ORDER) addItem(items, componentType + "_" + stage);
        }
    }

    private static void emitOrderedPaths(List<ItemStack> items, List<String> orderedPaths) {
        orderedPaths.forEach(path -> addItem(items, path));
    }

    private static void addMaterialItems(List<ItemStack> items,
                                         com.gregtechceu.gtceu.api.data.chemical.material.Material material) {
        TagPrefix[] prefixes = {
                TagPrefix.ingot, TagPrefix.plate, TagPrefix.rod, TagPrefix.rodLong,
                TagPrefix.bolt, TagPrefix.screw, TagPrefix.gear, TagPrefix.gearSmall,
                TagPrefix.ring, TagPrefix.foil, TagPrefix.wireGtSingle,
                TagPrefix.dust, TagPrefix.dustSmall, TagPrefix.dustTiny,
                TagPrefix.nugget, TagPrefix.frameGt, TagPrefix.block,
        };
        for (TagPrefix prefix : prefixes) {
            try {
                ItemStack stack = ChemicalHelper.get(prefix, material);
                if (!stack.isEmpty()) {
                    ResourceLocation id = BuiltInRegistries.ITEM.getKey(stack.getItem());
                    if (!id.getNamespace().equals(Hk3Constants.MOD_ID)) items.add(stack.copy());
                }
            } catch (Exception ignored) {}
        }
    }

    private static Set<String> collectCircuitPaths() {
        Set<String> paths = new HashSet<>();
        Hk3CircuitItems.HONKAI_CIRCUITS.values()
                .forEach(reg -> paths.add(reg.getId().getPath()));
        Hk3CircuitItems.DETAILED_CIRCUITS.values()
                .forEach(reg -> paths.add(reg.getId().getPath()));
        return paths;
    }

    private static Set<String> collectMultiblockPaths() {
        return new LinkedHashSet<>(Arrays.asList(MULTIBLOCK_CONTROLLER_PATHS));
    }

    private static Set<String> collectExcludedItemPaths() {
        Set<String> paths = new HashSet<>(collectCircuitPaths());
        Hk3Blocks.BLOCK_ITEMS.getEntries().forEach(reg -> paths.add(reg.getId().getPath()));
        paths.addAll(collectMultiblockPaths());
        paths.addAll(Arrays.asList(PRIMARY_ITEM_ORDER));
        paths.addAll(Arrays.asList(BLOCK_ORDER));

        BuiltInRegistries.ITEM.forEach(item -> {
            ResourceLocation id = BuiltInRegistries.ITEM.getKey(item);
            if (id.getNamespace().equals(Hk3Constants.MOD_ID) && isComponentItem(id.getPath())) {
                paths.add(id.getPath());
            }
        });
        return paths;
    }

    private static void emitOrderedCircuitItems(CreativeModeTab.Output output) {
        for (String tier : HONKAI_CIRCUIT_TIER_ORDER) {
            RegistryObject<Item> circuit = Hk3CircuitItems.getHonkaiCircuit(tier);
            if (circuit != null && circuit.isPresent()) {
                output.accept(circuit.get());
            }
        }
        for (String path : CANONICAL_DETAILED_CIRCUIT_PATHS) {
            ItemStack stack = findItemByPath(path);
            if (!stack.isEmpty()) {
                output.accept(stack);
            }
        }
    }

    private static void emitOrderedComponentItems(CreativeModeTab.Output output) {
        for (String componentType : COMPONENT_TYPE_ORDER) {
            for (String stage : COMPONENT_STAGE_ORDER) {
                ItemStack stack = findItemByPath(componentType + "_" + stage);
                if (!stack.isEmpty()) {
                    output.accept(stack);
                }
            }
        }
    }

    private static void emitOrderedPaths(CreativeModeTab.Output output, List<String> orderedPaths) {
        for (String path : orderedPaths) {
            ItemStack stack = findItemByPath(path);
            if (!stack.isEmpty()) {
                output.accept(stack);
            }
        }
    }

    private static List<String> collectRemainingItemPaths(Set<String> excludedPaths) {
        return BuiltInRegistries.ITEM.stream()
                .map(BuiltInRegistries.ITEM::getKey)
                .filter(id -> id.getNamespace().equals(Hk3Constants.MOD_ID))
                .map(ResourceLocation::getPath)
                .filter(path -> !excludedPaths.contains(path))
                .sorted(Comparator.naturalOrder())
                .collect(Collectors.toList());
    }

    private static boolean isComponentItem(String path) {
        for (String prefix : COMPONENT_PREFIXES) {
            if (path.startsWith(prefix)) return true;
        }
        return false;
    }

    private static ItemStack findItemByPath(String path) {
        ResourceLocation id = asResource(path);
        Item item = BuiltInRegistries.ITEM.get(id);
        if (item != Items.AIR) return new ItemStack(item);
        return ItemStack.EMPTY;
    }

    private static ResourceLocation asResource(String path) {
        return new ResourceLocation(Hk3Constants.MOD_ID, path);
    }

    private static void addMaterialItems(CreativeModeTab.Output output,
                                         com.gregtechceu.gtceu.api.data.chemical.material.Material material) {
        TagPrefix[] prefixes = {
                TagPrefix.ingot, TagPrefix.plate, TagPrefix.rod, TagPrefix.rodLong,
                TagPrefix.bolt, TagPrefix.screw, TagPrefix.gear, TagPrefix.gearSmall,
                TagPrefix.ring, TagPrefix.foil, TagPrefix.wireGtSingle,
                TagPrefix.dust, TagPrefix.dustSmall, TagPrefix.dustTiny,
                TagPrefix.nugget, TagPrefix.frameGt, TagPrefix.block,
        };
        for (TagPrefix prefix : prefixes) {
            try {
                ItemStack stack = ChemicalHelper.get(prefix, material);
                if (!stack.isEmpty()) {
                    ResourceLocation id = BuiltInRegistries.ITEM.getKey(stack.getItem());
                    if (!id.getNamespace().equals(Hk3Constants.MOD_ID)) {
                        output.accept(stack);
                    }
                }
            } catch (Exception ignored) {}
        }
    }

    /** 将创造页签注册器绑定到 MOD 事件总线。在模组构造时调用 */
    public static void register(IEventBus modEventBus) {
        TABS.register(modEventBus);
    }
}
