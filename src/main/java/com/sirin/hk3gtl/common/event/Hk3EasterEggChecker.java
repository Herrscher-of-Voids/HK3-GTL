package com.sirin.hk3gtl.common.event;



import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.data.chemical.ChemicalHelper;
import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.dimension.Hk3Dimensions;
import com.sirin.hk3gtl.common.dimension.Hk3GraduationData;
import com.sirin.hk3gtl.common.entity.Hk3Entities;
import com.sirin.hk3gtl.common.gaze.Hk3GazeManager;
import com.sirin.hk3gtl.common.item.abyss.AbyssCircuitItems;
import com.sirin.hk3gtl.common.item.abyss.AbyssFunctionalItems;
import com.sirin.hk3gtl.common.item.finality.FinalityCircuitItems;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import com.sirin.hk3gtl.common.item.imaginary.ImaginaryCircuitItems;
import com.sirin.hk3gtl.common.item.quantum.QuantumCircuitItems;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import com.sirin.hk3gtl.common.machine.multiblock.part.HonkaiEnergyHatchPartMachine;
import com.sirin.hk3gtl.common.material.SouliumMaterial;
import com.sirin.hk3gtl.common.research.Hk3ResearchManager;
import com.sirin.hk3gtl.common.research.Hk3ResearchNodes;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.phys.AABB;

import java.util.function.Consumer;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingAttackEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

import java.time.LocalDate;
import java.time.LocalTime;
import java.util.Locale;

/**
 * 彩蛋事件 E-EG-001~100 监听与触发（对应设计文档彩蛋事件总表）。
 */
@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class Hk3EasterEggChecker {

    private static final String LAST_SOULIUM = "last_soulium";
    private static final String LAST_CRYSTAL = "last_crystal";
    private static final String LAST_BUBBLE = "last_bubble";
    private static final String LIFETIME_SOULIUM = "lifetime_soulium";
    private static final String LIFETIME_CRYSTAL = "lifetime_crystal";
    private static final String LIFETIME_BUBBLE = "lifetime_bubble";
    private static final String ONLINE_TICKS = "online_ticks";
    private static final String STILL_IMAGINARY_TICKS = "still_imaginary_ticks";
    private static final String NEAR_MATRIX_TICKS = "near_matrix_ticks";
    private static final String NEAR_GATEWAY_TICKS = "near_gateway_ticks";
    private static final String NEAR_MEMORIAL_TICKS = "near_memorial_ticks";
    private static final String ANCHOR_WORK_TICKS = "anchor_work_ticks";
    private static final String JUMP_NEAR_FLAGSHIP = "jump_near_flagship";
    private static final String DIALOGUE_OPEN_TICK = "dialogue_open_tick";
    private static final String MIN_RESEARCH_SPEED = "min_research_speed";
    private static final String HATCH_TYPES_USED = "hatch_types_used";
    private static final String FIRST_GAZE_DONE = "first_gaze_done";
    private static final String DUAL_ENERGY_SEEN = "dual_energy_seen";
    private static final String WIRELESS_BUILT = "wireless_built";
    private static final String TRAIN_OUTPUT = "train_output";
    private static final String QT_COMPUTER_RAN = "qt_computer_ran";

    private static final String[] ABYSS_MACHINES = {
            "large_honkai_reactor", "abyss_deep_smeltery", "abyss_precision_workshop", "abyss_particle_research_ring"
    };
    private static final String[] IMAGINARY_MACHINES = {
            "imaginary_dimension_gateway", "imaginary_tree_observation_array", "imaginary_anchor_device",
            "sea_of_quanta_observatory", "imaginary_circuit_computation_sanctum", "soulium_superstructure_forge",
            "civilization_exchange_council_hub", "precivilization_database_decoder", "honkai_phase_purification_plant",
            "dual_energy_stable_supply_station", "imaginary_dream_furnace", "imaginary_matter_weaver"
    };
    private static final String[] QUANTUM_MACHINES = {
            "quantum_entanglement_computer", "thousand_realms_train", "world_bubble_meltdown_furnace",
            "quantum_superconductor_lattice_factory", "honkai_wireless_transit_hub", "quantum_thought_forge",
            "divine_key_gallery",
            "quantum_civilization_trade_port", "quantum_honkai_fusion_ring", "finality_pressure_buffer_array",
            "wonder_construction_simulation_platform", "quantum_precision_assembly_factory"
    };
    private static final String[] FINALITY_MACHINES = {
            "hyperion_flagship", "shipboard_finality_observation", "shipboard_dual_energy_reactor_deck",
            "shipboard_civilization_coordination_hall", "shipboard_divine_key_shrine",
            "finality_civilization_construction_works", "civilization_validation_matrix",
            "finality_civilization_power_hub", "finality_ultimate_material_forge",
            "finality_honkai_annihilation_ring", "graduation_permission_verification_altar",
            "civilization_wonder_sanctum"
    };
    private static final String[] WONDER_MACHINES = {
            "honkai_ultimate_fusion_core", "divine_key_grand_cathedral", "civilization_judgment_corridor",
            "civilization_memory_eternal_monument", "myriad_realms_communication_nexus", "destiny_loom",
            "civilization_eye_observation_array", "cycle_narrator_platform", "civilization_starship_museum",
            "proof_of_existence_memorial"
    };
    private static final String[] SHIPBOARD_MODULES = {
            "shipboard_finality_observation", "shipboard_dual_energy_reactor_deck",
            "shipboard_civilization_coordination_hall", "shipboard_divine_key_shrine"
    };

    private Hk3EasterEggChecker() {}

    // ── 对外挂钩 ──

    /** 由 Hk3EventManagerImpl 每秒调用 */
    public static void onPlayerTick(ServerPlayer player) {
        trackPlayTime(player);
        trackInventoryDeltas(player);
        checkTimeEggs(player);
        checkGazeEggs(player);
        checkExactInventoryEggs(player);
        checkResearchCountEggs(player);
        checkIndustrialEggs(player);
        checkDimensionBehavior(player);
        checkGraduatedReturn(player);
        trackResearchSpeedFloor(player);
        scanNearbyMachines(player);
    }

    public static void onMultiblockFormed(ServerPlayer player, String machineId) {
        Hk3EasterEggStats.markMachineBuilt(player, machineId);
        int built = Hk3EasterEggStats.countBuiltMachines(player);
        if (built >= 60) {
            tryEgg(player, 45);
        }
        if (Hk3EasterEggStats.getMultiblockFormedTotal(player) == 100) {
            tryEgg(player, 67);
        }
        switch (machineId) {
            case "honkai_wireless_transit_hub" -> {
                Hk3EasterEggStats.setFlag(player, WIRELESS_BUILT, true);
                tryEgg(player, 8);
            }
            case "dual_energy_stable_supply_station" -> {
                Hk3EasterEggStats.setFlag(player, DUAL_ENERGY_SEEN, true);
                tryEgg(player, 38);
            }
            case "divine_key_gallery" -> tryEgg(player, 16);
            case "shipboard_finality_observation" -> tryEgg(player, 17);
            case "proof_of_existence_memorial" -> tryEgg(player, 29);
            case "civilization_validation_matrix" -> tryEgg(player, 19);
            case "quantum_entanglement_computer" -> Hk3EasterEggStats.setFlag(player, QT_COMPUTER_RAN, true);
            case "thousand_realms_train" -> Hk3EasterEggStats.setFlag(player, TRAIN_OUTPUT, true);
            default -> { }
        }
        if (Hk3EasterEggStats.hasBuiltAll(player, SHIPBOARD_MODULES)) {
            tryEgg(player, 49);
        }
        if (Hk3EasterEggStats.hasBuiltAll(player, WONDER_MACHINES)) {
            tryEgg(player, 44);
        }
        if (Hk3EasterEggStats.hasBuiltAll(player, ABYSS_MACHINES)) {
            tryEgg(player, 40);
        }
        if (Hk3EasterEggStats.hasBuiltAll(player, IMAGINARY_MACHINES)) {
            tryEgg(player, 41);
        }
        if (Hk3EasterEggStats.hasBuiltAll(player, QUANTUM_MACHINES)) {
            tryEgg(player, 42);
        }
        if (Hk3EasterEggStats.hasBuiltAll(player, FINALITY_MACHINES)) {
            tryEgg(player, 43);
        }
    }

    public static void onResearchCompleted(ServerPlayer player, String researchId) {
        int count = countCompletedResearch(player);
        if (count >= 50) {
            tryEgg(player, 26);
        }
        if (count >= 90) {
            tryEgg(player, 27);
        }
        if (count == 42) {
            tryEgg(player, 66);
        }
        if ("R-FN-003".equals(researchId)) {
            tryEgg(player, 18);
        }
        if ("R-IM-001".equals(researchId) || inventoryHas(player, ImaginaryCircuitItems.CIRCUIT_IMAGINARY_1.get())) {
            tryEgg(player, 11);
        }
    }

    public static void onFinaleDialogueOpened(ServerPlayer player) {
        Hk3EasterEggStats.putInt(player, DIALOGUE_OPEN_TICK, player.tickCount);
    }

    public static void onGraduationComplete(ServerPlayer player) {
        tryEgg(player, 20);
        tryEgg(player, 30);
    }

    public static void onAbsorptionTowerGuiOpened(ServerPlayer player) {
        tryEgg(player, 1);
    }

  // ── Forge 事件 ──

    @SubscribeEvent
    public static void onContainerOpen(PlayerEvent.PlayerLoggedInEvent event) {
        // 登录时检查日期类彩蛋
        if (!(event.getEntity() instanceof ServerPlayer player)) return;
        checkDateEggsOnLogin(player);
    }

    @SubscribeEvent
    public static void onLivingAttack(LivingAttackEvent event) {
        if (!(event.getSource().getEntity() instanceof ServerPlayer player)) return;
        if (event.getEntity().getType() == Hk3Entities.VOID_QUEEN_SIRIN.get()) {
            tryEgg(player, 22);
        }
    }

    @SubscribeEvent
    public static void onRightClickBlock(PlayerInteractEvent.RightClickBlock event) {
        if (event.getLevel().isClientSide() || !(event.getEntity() instanceof ServerPlayer player)) return;
        BlockPos pos = event.getPos();
        ItemStack held = player.getMainHandItem();

        if (isControllerAt(event.getLevel(), pos, "honkai_absorption_tower")) {
            tryEgg(player, 1);
        }
        if (isControllerAt(event.getLevel(), pos, "sea_of_quanta_observatory") && held.is(Items.OAK_BOAT)) {
            tryEgg(player, 91);
        }
        if (isControllerAt(event.getLevel(), pos, "imaginary_tree_observation_array") && held.is(Items.OAK_SAPLING)) {
            tryEgg(player, 92);
        }
        if (isControllerAt(event.getLevel(), pos, "civilization_memory_eternal_monument") && held.is(Items.BOOK)) {
            tryEgg(player, 93);
        }
        if (isControllerAt(event.getLevel(), pos, "myriad_realms_communication_nexus") && held.is(Blocks.NOTE_BLOCK.asItem())) {
            tryEgg(player, 94);
        }
        if (isControllerAt(event.getLevel(), pos, "honkai_ultimate_fusion_core") && held.is(Blocks.ICE.asItem())) {
            tryEgg(player, 95);
        }
        if (isControllerAt(event.getLevel(), pos, "hyperion_flagship")
                && ItemStack.isSameItemSameTags(held, ChemicalHelper.get(TagPrefix.ingot, SouliumMaterial.SOULIUM, 1))) {
            tryEgg(player, 96);
        }
        if (isControllerAt(event.getLevel(), pos, "civilization_judgment_corridor") && held.is(Blocks.REDSTONE_TORCH.asItem())) {
            tryEgg(player, 97);
        }
        if (isControllerAt(event.getLevel(), pos, "finality_honkai_annihilation_ring")
                && (held.is(Blocks.POPPY.asItem()) || held.is(Blocks.DANDELION.asItem()))) {
            tryEgg(player, 98);
        }
        if (isControllerAt(event.getLevel(), pos, "graduation_permission_verification_altar") && held.is(Items.DIAMOND)) {
            tryEgg(player, 99);
        }
        if (held.is(AbyssFunctionalItems.ARTIFACT_VOID_ARCHIVES.get())) {
            tryEgg(player, 79);
        }
        if (isControllerAt(event.getLevel(), pos, "motion_key_grand_cathedral")
                && held.is(Items.FIREWORK_ROCKET)) {
            tryEgg(player, 85);
        }
    }

    @SubscribeEvent
    public static void onBlockPlace(BlockEvent.EntityPlaceEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) return;
        BlockPos placed = event.getPos();
        ItemStack held = player.getMainHandItem();
        if (isNearController(player.level(), placed, "proof_of_existence_memorial", 3)
                && held.is(Blocks.TORCH.asItem())) {
            tryEgg(player, 76);
        }
        if (isNearController(player.level(), placed, "soulium_smeltery", 4)
                && held.is(Blocks.CRAFTING_TABLE.asItem())) {
            tryEgg(player, 78);
        }
        if (isNearController(player.level(), placed, "large_honkai_reactor", 4)
                && held.is(Blocks.TNT.asItem())) {
            tryEgg(player, 80);
        }
    }

    @SubscribeEvent
    public static void onBlockBreak(BlockEvent.BreakEvent event) {
        if (!(event.getPlayer() instanceof ServerPlayer player)) return;
        if (player.level().dimension() == Hk3Dimensions.IMAGINARY) {
            tryEgg(player, 73);
        }
        for (String wonderId : WONDER_MACHINES) {
            if (isNearController(player.level(), event.getPos(), wonderId, 12)
                    && Hk3EasterEggStats.getBuiltMachines(player).contains(wonderId)) {
                tryEgg(player, 75);
                break;
            }
        }
    }

    // ── 内部检测 ──

    private static void trackPlayTime(ServerPlayer player) {
        Hk3EasterEggStats.addLong(player, ONLINE_TICKS, 20);
        long hours6 = 6L * 60 * 60 * 20;
        if (Hk3EasterEggStats.getLong(player, ONLINE_TICKS) >= hours6) {
            tryEgg(player, 54);
        }
        long hours100 = 100L * 60 * 60 * 20;
        if (Hk3EasterEggStats.getLong(player, ONLINE_TICKS) >= hours100) {
            tryEgg(player, 50);
        }
    }

    private static void trackInventoryDeltas(ServerPlayer player) {
        int soulium = countSouliumIngots(player.getInventory());
        int crystal = countItem(player.getInventory(), HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get());
        int bubble = countItem(player.getInventory(), HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get());

        int lastSoulium = Hk3EasterEggStats.getInt(player, LAST_SOULIUM);
        int lastCrystal = Hk3EasterEggStats.getInt(player, LAST_CRYSTAL);
        int lastBubble = Hk3EasterEggStats.getInt(player, LAST_BUBBLE);

        if (soulium > lastSoulium) {
            Hk3EasterEggStats.addLong(player, LIFETIME_SOULIUM, soulium - lastSoulium);
        }
        if (crystal > lastCrystal) {
            Hk3EasterEggStats.addLong(player, LIFETIME_CRYSTAL, crystal - lastCrystal);
        }
        if (crystal < lastCrystal && player.level().dimension() == Hk3Dimensions.IMAGINARY) {
            tryEgg(player, 84);
        }
        if (bubble > lastBubble) {
            Hk3EasterEggStats.addLong(player, LIFETIME_BUBBLE, bubble - lastBubble);
        }

        Hk3EasterEggStats.putInt(player, LAST_SOULIUM, soulium);
        Hk3EasterEggStats.putInt(player, LAST_CRYSTAL, crystal);
        Hk3EasterEggStats.putInt(player, LAST_BUBBLE, bubble);

        if (Hk3EasterEggStats.getLong(player, LIFETIME_SOULIUM) >= 100) {
            tryEgg(player, 2);
        }
        if (Hk3EasterEggStats.getLong(player, LIFETIME_CRYSTAL) >= 1000) {
            tryEgg(player, 3);
        }
        if (Hk3EasterEggStats.getLong(player, LIFETIME_BUBBLE) >= 10) {
            tryEgg(player, 13);
        }
        if (Hk3EasterEggStats.getLong(player, LIFETIME_SOULIUM) >= 10000) {
            tryEgg(player, 36);
        }
        if (Hk3EasterEggStats.getLong(player, LIFETIME_CRYSTAL) >= 50000) {
            tryEgg(player, 37);
        }

        if (inventoryHas(player, AbyssCircuitItems.CIRCUIT_ABYSS_1.get())) {
            tryEgg(player, 6);
        }

        int lastFuel = Hk3EasterEggStats.getInt(player, "last_fuel_rod");
        int fuel = countItem(player.getInventory(), HonkaiMaterialItems.HONKAI_FUEL_ROD.get());
        if (fuel < lastFuel) {
            trackFuelConsumed(player, lastFuel - fuel);
        }
        Hk3EasterEggStats.putInt(player, "last_fuel_rod", fuel);

        int lastSuppress = Hk3EasterEggStats.getInt(player, "last_suppressant");
        int suppress = countItem(player.getInventory(), HonkaiMaterialItems.HONKAI_SUPPRESSANT.get());
        if (suppress < lastSuppress) {
            for (int i = 0; i < lastSuppress - suppress; i++) {
                trackSuppressantUsed(player);
            }
        }
        Hk3EasterEggStats.putInt(player, "last_suppressant", suppress);

        int lastBuffer = Hk3EasterEggStats.getInt(player, "last_gaze_buffer");
        int buffer = countItem(player.getInventory(), HonkaiMaterialItems.GAZE_BUFFER_UNIT.get());
        if (buffer < lastBuffer) {
            for (int i = 0; i < lastBuffer - buffer; i++) {
                trackGazeBufferUsed(player);
            }
        }
        Hk3EasterEggStats.putInt(player, "last_gaze_buffer", buffer);
    }

    private static void checkTimeEggs(ServerPlayer player) {
        // eg053 为“现实世界”时间彩蛋（与 eg051/052/058/059 同类）：真实凌晨 3:00~3:59 在线触发。
        // 历史实现误用游戏内 getDayTime()（dayTime 3000~4000 实为游戏内上午 9~10 点），与文案“凌晨3~4点在线”不符，此处改用现实时钟。
        if (LocalTime.now().getHour() == 3) {
            tryEgg(player, 53);
        }
        long dayTime = player.serverLevel().getDayTime() % 24000L;
        if (dayTime >= 6000L && dayTime <= 6100L) {
            tryEgg(player, 70);
        }
        long day = player.serverLevel().getDayTime() / 24000L;
        if (day == 0) {
            tryEgg(player, 55);
        } else if (day == 100) {
            tryEgg(player, 56);
        } else if (day == 365) {
            tryEgg(player, 57);
        }
        LocalDate now = LocalDate.now();
        if (now.getMonthValue() == 4 && now.getDayOfMonth() == 1) {
            tryEgg(player, 51);
        }
        if (now.getMonthValue() == 12 && now.getDayOfMonth() == 25) {
            tryEgg(player, 52);
        }
        if (now.getMonthValue() == 2 && now.getDayOfMonth() == 14) {
            tryEgg(player, 58);
        }
        if (now.getMonthValue() == 10 && now.getDayOfMonth() == 1) {
            tryEgg(player, 59);
        }
        if (now.getDayOfWeek().getValue() == 7) {
            tryEgg(player, 60);
        }
    }

    private static void checkDateEggsOnLogin(ServerPlayer player) {
        checkTimeEggs(player);
    }

    private static void checkGazeEggs(ServerPlayer player) {
        int gaze = Hk3GazeManager.getGaze(player);
        if (gaze > 0 && !Hk3EasterEggStats.getFlag(player, FIRST_GAZE_DONE)) {
            Hk3EasterEggStats.setFlag(player, FIRST_GAZE_DONE, true);
            tryEgg(player, 4);
        }
        if (gaze == 666) {
            tryEgg(player, 5);
        }
        if (gaze == 42) {
            tryEgg(player, 61);
        }
        if (gaze == 314) {
            tryEgg(player, 62);
        }
        if (gaze == 777) {
            tryEgg(player, 63);
        }
        if (gaze == 0 && Hk3EasterEggStats.getLong(player, "gaze_was_positive") > 0) {
            tryEgg(player, 69);
        }
        if (gaze > 0) {
            Hk3EasterEggStats.putInt(player, "gaze_was_positive", 1);
        }
        if (gaze >= 800) {
            // 与正式事件 E-HQ-001 共用注视阈值，彩蛋 5 已在 666 处理
        }
        if (gaze >= 100) {
            tryEgg(player, 54);
        }
    }

    private static void checkExactInventoryEggs(ServerPlayer player) {
        if (countSouliumIngots(player.getInventory()) == 64) {
            tryEgg(player, 64);
        }
        if (countItem(player.getInventory(), HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get()) == 999) {
            tryEgg(player, 65);
        }
    }

    private static void checkResearchCountEggs(ServerPlayer player) {
        // 在 onResearchCompleted 中处理
    }

    private static void checkIndustrialEggs(ServerPlayer player) {
        int active = countActiveMultiblocksNearby(player, 96);
        if (active >= 10) {
            tryEgg(player, 31);
        }
        if (active >= 30) {
            tryEgg(player, 32);
        }
        if (active >= 50) {
            tryEgg(player, 33);
        }
        long honkaiStored = sumHonkaiEnergyNearby(player, 64);
        if (honkaiStored >= 1_000_000L) {
            tryEgg(player, 35);
        }
        if (Hk3EasterEggStats.getLong(player, "fuel_consumed") >= 1000) {
            tryEgg(player, 46);
        }
        if (honkaiStored == 1_234_567_890L) {
            tryEgg(player, 68);
        }
        if (isNearController(player.level(), player.blockPosition(), "finality_civilization_power_hub", 16)
                && countActiveMultiblocksNearby(player, 16) > 0
                && inventoryHas(player, FinalityCircuitItems.CIRCUIT_FINALITY_4.get())) {
            tryEgg(player, 34);
        }
    }

    private static void checkDimensionBehavior(ServerPlayer player) {
        if (player.level().dimension() == Hk3Dimensions.IMAGINARY) {
            if (player.getDeltaMovement().lengthSqr() < 0.001) {
                Hk3EasterEggStats.addInt(player, STILL_IMAGINARY_TICKS, 20);
                if (Hk3EasterEggStats.getInt(player, STILL_IMAGINARY_TICKS) >= 600) {
                    tryEgg(player, 21);
                }
            } else {
                Hk3EasterEggStats.putInt(player, STILL_IMAGINARY_TICKS, 0);
            }
        } else {
            Hk3EasterEggStats.putInt(player, STILL_IMAGINARY_TICKS, 0);
        }

        if (player.onGround() && player.getDeltaMovement().y > 0.3 && isNearController(player.level(), player.blockPosition(), "hyperion_flagship", 32)) {
            Hk3EasterEggStats.addInt(player, JUMP_NEAR_FLAGSHIP, 1);
            if (Hk3EasterEggStats.getInt(player, JUMP_NEAR_FLAGSHIP) >= 100) {
                tryEgg(player, 72);
            }
        }

        int dialogueTick = Hk3EasterEggStats.getInt(player, DIALOGUE_OPEN_TICK);
        if (dialogueTick > 0 && player.tickCount - dialogueTick > 20 * 60) {
            tryEgg(player, 23);
        }

        if (isNearController(player.level(), player.blockPosition(), "civilization_validation_matrix", 8)) {
            Hk3EasterEggStats.addInt(player, NEAR_MATRIX_TICKS, 20);
            if (Hk3EasterEggStats.getInt(player, NEAR_MATRIX_TICKS) >= 60 * 20) {
                tryEgg(player, 81);
            }
        } else {
            Hk3EasterEggStats.putInt(player, NEAR_MATRIX_TICKS, 0);
        }

        if (isNearController(player.level(), player.blockPosition(), "imaginary_dimension_gateway", 6)) {
            Hk3EasterEggStats.addInt(player, NEAR_GATEWAY_TICKS, 20);
            if (Hk3EasterEggStats.getInt(player, NEAR_GATEWAY_TICKS) >= 100) {
                tryEgg(player, 82);
            }
        } else {
            Hk3EasterEggStats.putInt(player, NEAR_GATEWAY_TICKS, 0);
        }

        if (isOnAbsorptionTowerTop(player)) {
            tryEgg(player, 71);
        }

        if (player.isSleeping() && isNearController(player.level(), player.blockPosition(), "civilization_wonder_sanctum", 16)) {
            tryEgg(player, 83);
        }

        if (player.getDeltaMovement().lengthSqr() > 0.01
                && isNearController(player.level(), player.blockPosition(), "civilization_judgment_corridor", 8)) {
            tryEgg(player, 77);
        }
    }

    private static void checkGraduatedReturn(ServerPlayer player) {
        if (!Hk3GraduationData.get(player.serverLevel()).isGraduated()) {
            return;
        }
        if (isNearController(player.level(), player.blockPosition(), "proof_of_existence_memorial", 6)) {
            Hk3EasterEggStats.addInt(player, NEAR_MEMORIAL_TICKS, 20);
            if (Hk3EasterEggStats.getInt(player, NEAR_MEMORIAL_TICKS) >= 100) {
                tryEgg(player, 100);
            }
        } else {
            Hk3EasterEggStats.putInt(player, NEAR_MEMORIAL_TICKS, 0);
        }
    }

    private static void trackResearchSpeedFloor(ServerPlayer player) {
        double factor = Hk3GazeManager.getResearchSpeedFactor(player);
        float stored = Hk3EasterEggStats.root(player).getFloat(MIN_RESEARCH_SPEED);
        if (stored == 0f || factor < stored) {
            Hk3EasterEggStats.root(player).putFloat(MIN_RESEARCH_SPEED, (float) factor);
        }
        if (factor <= Hk3Constants.RESEARCH_SPEED_FLOOR + 0.01) {
            tryEgg(player, 47);
        }
    }

    private static void scanNearbyMachines(ServerPlayer player) {
        Level level = player.level();
        BlockPos center = player.blockPosition();
        boolean[] anchorWorking = new boolean[1];
        int[] wirelessNodes = new int[1];
        forEachBlockEntityInRadius(level, center, 64, be -> {
            if (!(be instanceof IMachineBlockEntity mbe)) return;
            MetaMachine machine = mbe.getMetaMachine();
            if (machine == null) return;
            ResourceLocation id = machine.getDefinition().getId();
            if (!Hk3Constants.MOD_ID.equals(id.getNamespace())) return;
            if (machine instanceof Hk3WorkableMultiblockMachine workable) {
                RecipeLogic logic = workable.getRecipeLogic();
                if (logic != null && logic.isWorking()) {
                    if ("imaginary_anchor_device".equals(id.getPath())) {
                        anchorWorking[0] = true;
                    }
                    if ("quantum_entanglement_computer".equals(id.getPath()) && !Hk3EasterEggStats.getFlag(player, QT_COMPUTER_RAN)) {
                        Hk3EasterEggStats.setFlag(player, QT_COMPUTER_RAN, true);
                        tryEgg(player, 14);
                    }
                    if ("thousand_realms_train".equals(id.getPath()) && !Hk3EasterEggStats.getFlag(player, TRAIN_OUTPUT)) {
                        Hk3EasterEggStats.setFlag(player, TRAIN_OUTPUT, true);
                        tryEgg(player, 15);
                    }
                }
            }
            if (machine instanceof HonkaiEnergyHatchPartMachine hatch) {
                String type = hatch.getHatchType().id;
                String used = Hk3EasterEggStats.root(player).getString(HATCH_TYPES_USED);
                if (!used.contains(type)) {
                    Hk3EasterEggStats.root(player).putString(HATCH_TYPES_USED, used + "," + type);
                    if (used.split(",").length >= 4) {
                        tryEgg(player, 48);
                    }
                }
                if (hatch.getHatchType().wireless) {
                    wirelessNodes[0]++;
                }
                if (!hatch.getHatchType().wireless && !Hk3EasterEggStats.getFlag(player, "dual_hatch_used")) {
                    Hk3EasterEggStats.setFlag(player, "dual_hatch_used", true);
                    if (Hk3EasterEggStats.getFlag(player, DUAL_ENERGY_SEEN)) {
                        tryEgg(player, 7);
                    }
                }
            }
        });
        if (wirelessNodes[0] >= 5) {
            tryEgg(player, 39);
        }
        if (anchorWorking[0]) {
            Hk3EasterEggStats.addInt(player, ANCHOR_WORK_TICKS, 20);
            if (Hk3EasterEggStats.getInt(player, ANCHOR_WORK_TICKS) >= 72000) {
                tryEgg(player, 12);
            }
        }
    }

    // ── 工具 ──

    public static void tryEgg(ServerPlayer player, int index) {
        String eventId = String.format(Locale.ROOT, "E-EG-%03d", index);
        String langKey = String.format(Locale.ROOT, "hk3gtl.event.eg%03d", index);
        Hk3EventService.tryTriggerFirstTime(player, eventId, langKey);
    }

    public static void trackFuelConsumed(ServerPlayer player, int amount) {
        Hk3EasterEggStats.addLong(player, "fuel_consumed", amount);
        if (Hk3EasterEggStats.getLong(player, "fuel_consumed") >= 100) {
            tryEgg(player, 10);
        }
    }

    public static void trackSuppressantUsed(ServerPlayer player) {
        Hk3EasterEggStats.addInt(player, "suppressant_used", 1);
        if (Hk3EasterEggStats.getInt(player, "suppressant_used") >= 50) {
            tryEgg(player, 24);
        }
    }

    public static void trackGazeBufferUsed(ServerPlayer player) {
        Hk3EasterEggStats.addInt(player, "gaze_buffer_used", 1);
        if (Hk3EasterEggStats.getInt(player, "gaze_buffer_used") >= 20) {
            tryEgg(player, 25);
        }
    }

    /** 终局对话中反复点击选项时由对话系统调用 */
    public static void onDialogueSpamClick(ServerPlayer player) {
        if (Hk3EasterEggStats.getInt(player, DIALOGUE_OPEN_TICK) <= 0) {
            return;
        }
        Hk3EasterEggStats.addInt(player, "dialogue_clicks", 1);
        if (Hk3EasterEggStats.getInt(player, "dialogue_clicks") >= 8) {
            tryEgg(player, 74);
        }
    }

    private static int countCompletedResearch(ServerPlayer player) {
        int n = 0;
        for (var node : Hk3ResearchNodes.allNodes()) {
            if (Hk3ResearchManager.isCompleted(player, node.id())) {
                n++;
            }
        }
        return n;
    }

    private static int countActiveMultiblocksNearby(ServerPlayer player, int radius) {
        int[] count = new int[1];
        forEachBlockEntityInRadius(player.level(), player.blockPosition(), radius, be -> {
            if (!(be instanceof IMachineBlockEntity mbe)) return;
            MetaMachine machine = mbe.getMetaMachine();
            if (machine instanceof Hk3WorkableMultiblockMachine workable) {
                RecipeLogic logic = workable.getRecipeLogic();
                if (logic != null && logic.isWorking()) {
                    count[0]++;
                }
            }
        });
        return count[0];
    }

    private static long sumHonkaiEnergyNearby(ServerPlayer player, int radius) {
        long[] sum = new long[1];
        forEachBlockEntityInRadius(player.level(), player.blockPosition(), radius, be -> {
            if (be instanceof IMachineBlockEntity mbe) {
                MetaMachine machine = mbe.getMetaMachine();
                if (machine instanceof HonkaiEnergyHatchPartMachine hatch) {
                    sum[0] += hatch.getContainer().getAmount();
                }
            }
        });
        return sum[0];
    }

    private static void forEachBlockEntityInRadius(Level level, BlockPos center, int radius, Consumer<BlockEntity> consumer) {
        if (!(level instanceof ServerLevel serverLevel)) {
            return;
        }
        int chunkRadius = (radius >> 4) + 1;
        int cx = center.getX() >> 4;
        int cz = center.getZ() >> 4;
        long radiusSq = (long) radius * radius;
        for (int dx = -chunkRadius; dx <= chunkRadius; dx++) {
            for (int dz = -chunkRadius; dz <= chunkRadius; dz++) {
                LevelChunk chunk = serverLevel.getChunk(cx + dx, cz + dz);
                for (BlockEntity be : chunk.getBlockEntities().values()) {
                    if (be.getBlockPos().distSqr(center) <= radiusSq) {
                        consumer.accept(be);
                    }
                }
            }
        }
    }

    private static boolean isControllerAt(Level level, BlockPos pos, String machinePath) {
        BlockEntity be = level.getBlockEntity(pos);
        if (be instanceof IMachineBlockEntity mbe) {
            MetaMachine machine = mbe.getMetaMachine();
            return machine != null && machinePath.equals(machine.getDefinition().getId().getPath());
        }
        return false;
    }

    private static boolean isNearController(Level level, BlockPos pos, String machinePath, int range) {
        boolean[] found = new boolean[1];
        forEachBlockEntityInRadius(level, pos, range, be -> {
            if (be instanceof IMachineBlockEntity mbe) {
                MetaMachine machine = mbe.getMetaMachine();
                if (machine != null && machinePath.equals(machine.getDefinition().getId().getPath())) {
                    found[0] = true;
                }
            }
        });
        return found[0];
    }

    private static boolean isOnAbsorptionTowerTop(ServerPlayer player) {
        if (!isNearController(player.level(), player.blockPosition(), "honkai_absorption_tower", 4)) {
            return false;
        }
        BlockPos feet = player.blockPosition();
        return player.getY() > feet.getY() + 2;
    }

    private static int countSouliumIngots(Inventory inv) {
        ItemStack ref = ChemicalHelper.get(TagPrefix.ingot, SouliumMaterial.SOULIUM);
        if (ref.isEmpty()) return 0;
        int total = 0;
        for (int i = 0; i < inv.getContainerSize(); i++) {
            ItemStack stack = inv.getItem(i);
            if (ItemStack.isSameItemSameTags(stack, ref)) {
                total += stack.getCount();
            }
        }
        return total;
    }

    private static int countItem(Inventory inv, Item item) {
        int total = 0;
        for (int i = 0; i < inv.getContainerSize(); i++) {
            if (inv.getItem(i).is(item)) {
                total += inv.getItem(i).getCount();
            }
        }
        return total;
    }

    private static boolean inventoryHas(Player player, Item item) {
        return player.getInventory().contains(new ItemStack(item));
    }
}
