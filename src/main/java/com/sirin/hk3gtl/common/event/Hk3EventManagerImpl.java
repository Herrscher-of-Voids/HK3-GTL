package com.sirin.hk3gtl.common.event;



import com.gregtechceu.gtceu.api.data.chemical.ChemicalHelper;
import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.gaze.Hk3GazeManager;
import com.sirin.hk3gtl.common.item.abyss.AbyssCircuitItems;
import com.sirin.hk3gtl.common.item.abyss.AbyssFunctionalItems;
import com.sirin.hk3gtl.common.item.finality.FinalityCircuitItems;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import com.sirin.hk3gtl.common.item.imaginary.ImaginaryCircuitItems;
import com.sirin.hk3gtl.common.item.quantum.QuantumCircuitItems;
import com.sirin.hk3gtl.common.material.SouliumMaterial;
import com.sirin.hk3gtl.common.research.Hk3ResearchManager;
import com.sirin.hk3gtl.common.dimension.Hk3Dimensions;
import com.sirin.hk3gtl.common.dimension.Hk3GraduationData;
import com.sirin.hk3gtl.common.entity.VoidQueenSirinEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.tags.TagKey;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.Level;
import net.minecraftforge.event.AnvilUpdateEvent;
import net.minecraftforge.event.entity.player.AnvilRepairEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

import java.time.LocalDate;
import java.util.Locale;

/**
 * 事件管理器：监听玩家行为并触发一次性里程碑/多方块事件。
 *
 * 当前定位：
 * - 以“轻量、稳定、可联调”为优先
 * - 事件状态直接存放在玩家 persistentData 中
 * - 与研究系统桥接，作为研究自动完成节点的事件来源
 *
 * 这不是最终事件框架的终态，但已经足够承担：
 * - P1 里程碑提示
 * - 多方块首次建成
 * - P2 第一版研究事件桥接
 */
@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public class Hk3EventManagerImpl {

    private static final Logger LOGGER = LogUtils.getLogger();

    /**
     * 延迟初始化的魂钢锭 ItemStack 引用（GT 材料物品需要对比 NBT 才能正确匹配）。
     * volatile 保证多线程可见性；首次使用时通过 ChemicalHelper 获取。
     */
    private static volatile ItemStack souliumIngotRef;
    private static final String VOLTAGE_TIER_TAG = "hk3gtl_voltage_tier";
    private static final String ANVIL_PENDING_EVENT_TAG = "hk3gtl_pending_anvil_event";
    /** 瓦尔特馈赠：检测背包是否持有 MAX 级 GT 电路（标签 gtceu:circuits/max）。 */
    private static final TagKey<Item> GTCEU_MAX_CIRCUIT_TAG =
            TagKey.create(Registries.ITEM, new ResourceLocation("gtceu", "circuits/max"));

    // ═══════════════════════════════════════════
    //  里程碑事件 — 每秒检查一次玩家背包
    // ═══════════════════════════════════════════

    /**
     * 每 tick 监听玩家事件，但仅在 END 阶段、服务端、每20tick(1秒)执行一次检查。
     * 触发条件：玩家必须为 ServerPlayer，且 tickCount 为20的倍数。
     * 修改要点：如需调整检查频率，修改 % 20 的值即可。
     */
    @SubscribeEvent
    public static void onPlayerTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        if (!(event.player instanceof ServerPlayer player)) return;
        if (player.tickCount % 20 != 0) return;

        checkMilestoneEvents(player);
        Hk3EasterEggChecker.onPlayerTick(player);
        Hk3FactionEventChecker.checkFactionEvents(player);
        // 事件检查完成后再同步事件型研究，避免依赖 Forge 订阅顺序并合并每秒入口。
        Hk3ResearchManager.onPlayerSecond(player);
    }

    /**
     * 每秒扫描一次玩家背包，检查最基础的里程碑触发条件。
     *
     * 之所以先用轮询而不是复杂事件分发，是因为这批条件都比较简单，
     * 而轮询方式更稳定，调试成本更低。
     */
    private static void checkMilestoneEvents(ServerPlayer player) {
        CompoundTag data = player.getPersistentData();
        Inventory inv = player.getInventory();

        // E-MS-001: 崩坏能时代开启 — 首次获得崩坏能结晶
        if (!Hk3EventService.isEventMarked(data, "E-MS-001")
                && inventoryContains(inv, HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get())) {
            Hk3EventService.tryTriggerFirstTime(player, "E-MS-001", "hk3gtl.event.ms001");
            sendHint(player, "hk3gtl.event.ms001.hint");
            player.addItem(new ItemStack(HonkaiMaterialItems.RAW_HONKAI_PARTICLE.get(), 8));
        }

        // E-OT-001: 奥托邀请 — 背包持有星门底座时触发，并赠送虚空万藏（唯一获取途径）
        if (!Hk3EventService.isEventMarked(data, "E-OT-001")
                && inventoryContainsByItemId(inv, "sgjourney", "classic_stargate_base_block")) {
            if (Hk3EventService.tryTriggerFirstTime(player, "E-OT-001", "hk3gtl.event.ot001")) {
                grantVoidArchives(player);
            }
            sendHint(player, "hk3gtl.event.ot001.hint");
        }

        // E-WL-001: 瓦尔特馈赠 — 首次在背包获得 MAX 级电路板（gtceu:circuits/max）
        if (!Hk3EventService.isEventMarked(data, "E-WL-001")
                && inventoryContainsTag(inv, GTCEU_MAX_CIRCUIT_TAG)) {
            Hk3EventService.tryTriggerFirstTime(player, "E-WL-001", "hk3gtl.event.wl001");
        }

        // E-MS-002: 魂钢文明诞生 — 首次获得魂钢锭
        if (!Hk3EventService.isEventMarked(data, "E-MS-002") && inventoryContainsSouliumIngot(inv)) {
            Hk3EventService.tryTriggerFirstTime(player, "E-MS-002", "hk3gtl.event.ms002");
        }

        // E-MS-003: 海渊突破 — 首次获得海渊I电路（仅里程碑与凝视，不再传送虚数维度）
        if (!Hk3EventService.isEventMarked(data, "E-MS-003")
                && inventoryContains(inv, AbyssCircuitItems.CIRCUIT_ABYSS_1.get())) {
            if (Hk3EventService.tryTriggerFirstTime(player, "E-MS-003", "hk3gtl.event.ms003")) {
                Hk3GazeManager.addGaze(player, 50);
            }
        }

        // E-MS-004: 深海征服 — 首次获得海渊IV电路
        if (!Hk3EventService.isEventMarked(data, "E-MS-004")
                && inventoryContains(inv, AbyssCircuitItems.CIRCUIT_ABYSS_4.get())) {
            Hk3EventService.tryTriggerFirstTime(player, "E-MS-004", "hk3gtl.event.ms004");
        }

        // E-MS-005: 虚数觉醒 — 首次获得虚数I电路
        if (!Hk3EventService.isEventMarked(data, "E-MS-005")
                && inventoryContains(inv, ImaginaryCircuitItems.CIRCUIT_IMAGINARY_1.get())) {
            Hk3EventService.tryTriggerFirstTime(player, "E-MS-005", "hk3gtl.event.ms005");
        }

        // E-MS-006: 虚数掌控 — 背包持有虚数四·虚序主脑 → 里程碑 + 传送虚数维度（未完成终局对话时）
        if (!Hk3EventService.isEventMarked(data, "E-MS-006")
                && inventoryContains(inv, ImaginaryCircuitItems.CIRCUIT_IMAGINARY_4.get())) {
            Hk3EventService.tryTriggerFirstTime(player, "E-MS-006", "hk3gtl.event.ms006");
            if (!Hk3GraduationData.get(player.serverLevel()).isGraduated()
                    && !player.getPersistentData().getBoolean("hk3gtl_dialogue_done")) {
                teleportToImaginaryDimension(player);
            }
        }

        // E-MS-007: 量子跃迁 — 首次获得量子I电路
        if (!Hk3EventService.isEventMarked(data, "E-MS-007")
                && inventoryContains(inv, QuantumCircuitItems.CIRCUIT_QUANTUM_1.get())) {
            Hk3EventService.tryTriggerFirstTime(player, "E-MS-007", "hk3gtl.event.ms007");
        }

        // E-MS-009: 量子极限 — 首次获得量子IV电路
        if (!Hk3EventService.isEventMarked(data, "E-MS-009")
                && inventoryContains(inv, QuantumCircuitItems.CIRCUIT_QUANTUM_4.get())) {
            Hk3EventService.tryTriggerFirstTime(player, "E-MS-009", "hk3gtl.event.ms009");
        }

        // E-MS-010: 终焉降临 — 首次获得终焉I电路
        if (!Hk3EventService.isEventMarked(data, "E-MS-010")
                && inventoryContains(inv, FinalityCircuitItems.CIRCUIT_FINALITY_1.get())) {
            Hk3EventService.tryTriggerFirstTime(player, "E-MS-010", "hk3gtl.event.ms010");
        }

        // E-MS-012: 终焉极限 — 首次获得终焉III电路
        if (!Hk3EventService.isEventMarked(data, "E-MS-012")
                && inventoryContains(inv, FinalityCircuitItems.CIRCUIT_FINALITY_3.get())) {
            Hk3EventService.tryTriggerFirstTime(player, "E-MS-012", "hk3gtl.event.ms012");
        }

        // E-MS-013: 超越极限 — 首次获得终焉IV电路
        if (!Hk3EventService.isEventMarked(data, "E-MS-013")
                && inventoryContains(inv, FinalityCircuitItems.CIRCUIT_FINALITY_4.get())) {
            Hk3EventService.tryTriggerFirstTime(player, "E-MS-013", "hk3gtl.event.ms013");
        }

        // E-MS-008/011/014: 由多方块建成触发（见 onMultiblockFormed）
        // E-MS-015: 毕业 — 由毕业系统外部触发
        checkVoltageTierProgress(player, data, inv);
    }

    // ═══════════════════════════════════════════
    //  右键事件拦截
    // ═══════════════════════════════════════════
    @SubscribeEvent
    public static void onRightClick(net.minecraftforge.event.entity.player.PlayerInteractEvent.RightClickBlock event) {
        if (event.getHand() != net.minecraft.world.InteractionHand.MAIN_HAND || event.getLevel().isClientSide()) return;

        net.minecraft.world.level.block.entity.BlockEntity be = event.getLevel().getBlockEntity(event.getPos());
        if (!(be instanceof com.gregtechceu.gtceu.api.machine.IMachineBlockEntity mbe)) return;
        com.gregtechceu.gtceu.api.machine.MetaMachine machine = mbe.getMetaMachine();

        if (machine instanceof com.sirin.hk3gtl.common.machine.multiblock.part.HonkaiEnergyHatchPartMachine hatch) {
            Player player = event.getEntity();
            if (player.isShiftKeyDown()) return;

            if (hatch.getHatchType().wireless) {
                if (hatch.getOwnerId() == null) {
                    if (hatch.ensureOwner(player.getUUID())) {
                        player.sendSystemMessage(Component.literal("§a已将此无线仓绑定至玩家: " + player.getName().getString()));
                    }
                } else {
                    player.sendSystemMessage(Component.literal("§c此无线仓已绑定至其他玩家，无法更改"));
                }
            } else {
                long amount = hatch.getContainer().getAmount();
                long capacity = hatch.getContainer().getCapacity();
                String typeStr = hatch.getHatchType().id;
                player.sendSystemMessage(Component.literal(String.format("§b[%s] §f崩坏能: §a%d §f/ §e%d", typeStr, amount, capacity)));
            }

            event.setCanceled(true);
            event.setCancellationResult(net.minecraft.world.InteractionResult.SUCCESS);
        }
    }

    @SubscribeEvent
    public static void onAnvilUpdate(AnvilUpdateEvent event) {
        if (!(event.getPlayer() instanceof ServerPlayer player)) return;
        String mapped = mapAnvilNameToEvent(event.getName());
        if (mapped == null) return;
        player.getPersistentData().putString(ANVIL_PENDING_EVENT_TAG, mapped);
    }

    @SubscribeEvent
    public static void onAnvilRepair(AnvilRepairEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) return;
        CompoundTag data = player.getPersistentData();
        String eventId = data.getString(ANVIL_PENDING_EVENT_TAG);
        if (eventId.isEmpty()) return;
        String langKey = langKeyForEvent(eventId);
        Hk3EventService.tryTriggerFirstTime(player, eventId, langKey);
        data.remove(ANVIL_PENDING_EVENT_TAG);
    }

    // ═══════════════════════════════════════════
    //  多方块首次建成事件
    //  由 Hk3WorkableMultiblockMachine 在成型时调用
    // ═══════════════════════════════════════════

    /**
     * 由多方块基类在成型成功后调用。
     * 当前所有“首次建成”事件统一从这里分发。
     */
    /**
     * 多方块首次建成事件入口，由 Hk3WorkableMultiblockMachine 在成型后调用。
     * 修改要点：新增机器建成事件时在 switch 中添加 case，machineId 为机器注册ID。
     */
    public static void onMultiblockFormed(ServerPlayer player, String machineId) {
        CompoundTag data = player.getPersistentData();

        switch (machineId) {
            // ── P1 / Max 起始核心 ──
            case "honkai_absorption_tower" ->
                    tryTrigger(player, data, "E-FB-001", "hk3gtl.event.fb001");
            case "soulium_smeltery" ->
                    tryTrigger(player, data, "E-FB-002", "hk3gtl.event.fb002");
            case "honkai_crystal_condenser" -> { /* 凝结厂无独立建成事件 */ }
            case "large_honkai_reactor" -> {
                tryTrigger(player, data, "E-FB-003", "hk3gtl.event.fb003");
                boolean first = !Hk3EventService.isEventMarked(data, "E-FB-005");
                tryTrigger(player, data, "E-FB-005", "hk3gtl.event.fb005");
                if (first) {
                    Hk3GazeManager.addGaze(player, 20);
                }
            }
            case "abyss_research_analysis_matrix" ->
                    tryTrigger(player, data, "E-FB-007", "hk3gtl.event.fb007");
            case "void_archives_analysis_chamber" ->
                    tryTrigger(player, data, "E-FB-021", "hk3gtl.event.fb021");
            case "abyss_circuit_foundry" -> {
                    tryTrigger(player, data, "E-FB-022", "hk3gtl.event.fb022");
                    tryTrigger(player, data, "E-FB-029", "hk3gtl.event.fb029");
            }
            case "reason_reconstruction_array" ->
                    tryTrigger(player, data, "E-FB-023", "hk3gtl.event.fb023");
            case "honkai_eu_converter" ->
                    tryTrigger(player, data, "E-FB-027", "hk3gtl.event.fb027");

            case "civilization_memory_eternal_monument" ->
                    tryTrigger(player, data, "E-FB-014", "hk3gtl.event.fb014");

            // ── 海渊阶段 ──
            case "abyss_precision_workshop" ->
                    tryTrigger(player, data, "E-FB-006", "hk3gtl.event.fb006");
            case "abyss_deep_smeltery" ->
                    tryTrigger(player, data, "E-FB-039", "hk3gtl.event.fb039");
            case "abyss_particle_research_ring" ->
                    tryTrigger(player, data, "E-FB-041", "hk3gtl.event.fb041");
            case "sea_of_quanta_observatory" ->
                    tryTrigger(player, data, "E-FB-008", "hk3gtl.event.fb008");

            // ── 虚数阶段（解锁量子入口的关键 4 个事件）──
            case "imaginary_tree_observation_array" ->
                    tryTrigger(player, data, "E-FB-009", "hk3gtl.event.fb009");
            case "imaginary_anchor_device" ->
                    tryTrigger(player, data, "E-FB-010", "hk3gtl.event.fb010");
            case "precivilization_database_decoder" ->
                    tryTrigger(player, data, "E-FB-011", "hk3gtl.event.fb011");
            case "imaginary_circuit_computation_sanctum" ->
                    tryTrigger(player, data, "E-FB-031", "hk3gtl.event.fb031");
            case "soulium_superstructure_forge" ->
                    tryTrigger(player, data, "E-FB-032", "hk3gtl.event.fb032");
            case "civilization_exchange_council_hub" ->
                    tryTrigger(player, data, "E-FB-004", "hk3gtl.event.fb004");
            case "honkai_phase_purification_plant" ->
                    tryTrigger(player, data, "E-FB-033", "hk3gtl.event.fb033");
            case "dual_energy_stable_supply_station" ->
                    tryTrigger(player, data, "E-FB-028", "hk3gtl.event.fb028");
            case "imaginary_dream_furnace" ->
                    tryTrigger(player, data, "E-FB-034", "hk3gtl.event.fb034");
            case "imaginary_matter_weaver" ->
                    tryTrigger(player, data, "E-FB-035", "hk3gtl.event.fb035");

            // ── 量子阶段（量子纠缠计算机 = 量子研究台，必触发 E-FB-012）──
            case "quantum_entanglement_computer" ->
                    tryTrigger(player, data, "E-FB-012", "hk3gtl.event.fb012");
            case "world_bubble_meltdown_furnace" ->
                    tryTrigger(player, data, "E-FB-036", "hk3gtl.event.fb036");
            case "quantum_superconductor_lattice_factory" ->
                    tryTrigger(player, data, "E-FB-037", "hk3gtl.event.fb037");
            case "honkai_wireless_transit_hub" ->
                    tryTrigger(player, data, "E-FB-038", "hk3gtl.event.fb038");
            case "quantum_thought_forge" ->
                    tryTrigger(player, data, "E-FB-040", "hk3gtl.event.fb040");
            case "divine_key_gallery" ->
                    tryTrigger(player, data, "E-FB-042", "hk3gtl.event.fb042");
            case "quantum_civilization_trade_port" ->
                    tryTrigger(player, data, "E-FB-043", "hk3gtl.event.fb043");
            case "quantum_honkai_fusion_ring" ->
                    tryTrigger(player, data, "E-FB-044", "hk3gtl.event.fb044");
            case "finality_pressure_buffer_array" ->
                    tryTrigger(player, data, "E-FB-045", "hk3gtl.event.fb045");
            case "wonder_construction_simulation_platform" ->
                    tryTrigger(player, data, "E-FB-046", "hk3gtl.event.fb046");
            case "quantum_precision_assembly_factory" ->
                    tryTrigger(player, data, "E-FB-047", "hk3gtl.event.fb047");

            // ── 终焉阶段 ──
            case "shipboard_finality_observation" ->
                    tryTrigger(player, data, "E-FB-048", "hk3gtl.event.fb048");
            case "shipboard_dual_energy_reactor_deck" ->
                    tryTrigger(player, data, "E-FB-049", "hk3gtl.event.fb049");
            case "shipboard_civilization_coordination_hall" ->
                    tryTrigger(player, data, "E-FB-050", "hk3gtl.event.fb050");
            case "shipboard_divine_key_shrine" ->
                    tryTrigger(player, data, "E-FB-051", "hk3gtl.event.fb051");
            case "finality_civilization_construction_works" ->
                    tryTrigger(player, data, "E-FB-052", "hk3gtl.event.fb052");
            case "finality_civilization_power_hub" ->
                    tryTrigger(player, data, "E-FB-053", "hk3gtl.event.fb053");
            case "finality_ultimate_material_forge" ->
                    tryTrigger(player, data, "E-FB-054", "hk3gtl.event.fb054");
            case "graduation_permission_verification_altar" ->
                    tryTrigger(player, data, "E-FB-055", "hk3gtl.event.fb055");
            case "imaginary_dimension_gateway" ->
                    tryTrigger(player, data, "E-FB-017", "hk3gtl.event.fb017");
            case "civilization_wonder_sanctum" ->
                    tryTrigger(player, data, "E-FB-018", "hk3gtl.event.fb018");
            case "finality_honkai_annihilation_ring" ->
                    tryTrigger(player, data, "E-FB-020", "hk3gtl.event.fb020");
            case "proof_of_existence_memorial" ->
                    tryTrigger(player, data, "E-FB-019", "hk3gtl.event.fb019");

            // ── 里程碑多方块（同时触发 FB 和 MS 事件） ──
            case "thousand_realms_train" -> {
                boolean first = !Hk3EventService.isEventMarked(data, "E-FB-013");
                tryTrigger(player, data, "E-FB-013", "hk3gtl.event.fb013");
                tryTrigger(player, data, "E-MS-008", "hk3gtl.event.ms008");
                if (first) {
                    Hk3GazeManager.addGaze(player, 50);
                }
            }
            case "hyperion_flagship" -> {
                boolean first = !Hk3EventService.isEventMarked(data, "E-FB-015");
                tryTrigger(player, data, "E-FB-015", "hk3gtl.event.fb015");
                tryTrigger(player, data, "E-MS-011", "hk3gtl.event.ms011");
                if (first) {
                    Hk3GazeManager.addGaze(player, 80);
                }
            }
            case "civilization_validation_matrix" -> {
                boolean first = !Hk3EventService.isEventMarked(data, "E-FB-016");
                tryTrigger(player, data, "E-FB-016", "hk3gtl.event.fb016");
                tryTrigger(player, data, "E-MS-014", "hk3gtl.event.ms014");
                if (first) {
                    Hk3GazeManager.addGaze(player, 100);
                }
            }
        }

        Hk3EasterEggChecker.onMultiblockFormed(player, machineId);
        Hk3FactionEventChecker.onMultiblockFormedFaction(player, machineId);
    }

    /**
     * 尝试触发事件（仅在未触发时执行）。
     * @param eventId 事件唯一ID（如 E-FB-001）
     * @param langKey 对应的语言文件 key，用于向玩家发送消息
     */
    private static void tryTrigger(ServerPlayer player, CompoundTag data, String eventId, String langKey) {
        Hk3EventService.tryTriggerFirstTime(player, eventId, langKey);
    }

    private static void checkVoltageTierProgress(ServerPlayer player, CompoundTag data, Inventory inv) {
        int previous = data.getInt(VOLTAGE_TIER_TAG);
        int current = detectVoltageTier(inv);
        if (current <= previous) {
            return;
        }
        data.putInt(VOLTAGE_TIER_TAG, current);
        Hk3GazeManager.addGaze(player, 30);
        if (hasAllVoltageCircuits(inv)) {
            Hk3EventService.tryTriggerFirstTime(player, "E-EG-028", "hk3gtl.event.eg028");
        }
    }

    private static int detectVoltageTier(Inventory inv) {
        boolean[] tiers = new boolean[] {
                inventoryContains(inv, AbyssCircuitItems.CIRCUIT_ABYSS_1.get()),
                inventoryContains(inv, AbyssCircuitItems.CIRCUIT_ABYSS_2.get()),
                inventoryContains(inv, AbyssCircuitItems.CIRCUIT_ABYSS_3.get()),
                inventoryContains(inv, AbyssCircuitItems.CIRCUIT_ABYSS_4.get()),
                inventoryContains(inv, ImaginaryCircuitItems.CIRCUIT_IMAGINARY_1.get()),
                inventoryContains(inv, ImaginaryCircuitItems.CIRCUIT_IMAGINARY_2.get()),
                inventoryContains(inv, ImaginaryCircuitItems.CIRCUIT_IMAGINARY_3.get()),
                inventoryContains(inv, ImaginaryCircuitItems.CIRCUIT_IMAGINARY_4.get()),
                inventoryContains(inv, QuantumCircuitItems.CIRCUIT_QUANTUM_1.get()),
                inventoryContains(inv, QuantumCircuitItems.CIRCUIT_QUANTUM_2.get()),
                inventoryContains(inv, QuantumCircuitItems.CIRCUIT_QUANTUM_3.get()),
                inventoryContains(inv, QuantumCircuitItems.CIRCUIT_QUANTUM_4.get()),
                inventoryContains(inv, FinalityCircuitItems.CIRCUIT_FINALITY_1.get()),
                inventoryContains(inv, FinalityCircuitItems.CIRCUIT_FINALITY_2.get()),
                inventoryContains(inv, FinalityCircuitItems.CIRCUIT_FINALITY_3.get()),
                inventoryContains(inv, FinalityCircuitItems.CIRCUIT_FINALITY_4.get())
        };
        int highest = 0;
        for (int i = 0; i < tiers.length; i++) {
            if (tiers[i]) {
                highest = i + 1;
            }
        }
        return highest;
    }

    private static boolean hasAllVoltageCircuits(Inventory inv) {
        return inventoryContains(inv, AbyssCircuitItems.CIRCUIT_ABYSS_1.get())
                && inventoryContains(inv, AbyssCircuitItems.CIRCUIT_ABYSS_2.get())
                && inventoryContains(inv, AbyssCircuitItems.CIRCUIT_ABYSS_3.get())
                && inventoryContains(inv, AbyssCircuitItems.CIRCUIT_ABYSS_4.get())
                && inventoryContains(inv, ImaginaryCircuitItems.CIRCUIT_IMAGINARY_1.get())
                && inventoryContains(inv, ImaginaryCircuitItems.CIRCUIT_IMAGINARY_2.get())
                && inventoryContains(inv, ImaginaryCircuitItems.CIRCUIT_IMAGINARY_3.get())
                && inventoryContains(inv, ImaginaryCircuitItems.CIRCUIT_IMAGINARY_4.get())
                && inventoryContains(inv, QuantumCircuitItems.CIRCUIT_QUANTUM_1.get())
                && inventoryContains(inv, QuantumCircuitItems.CIRCUIT_QUANTUM_2.get())
                && inventoryContains(inv, QuantumCircuitItems.CIRCUIT_QUANTUM_3.get())
                && inventoryContains(inv, QuantumCircuitItems.CIRCUIT_QUANTUM_4.get())
                && inventoryContains(inv, FinalityCircuitItems.CIRCUIT_FINALITY_1.get())
                && inventoryContains(inv, FinalityCircuitItems.CIRCUIT_FINALITY_2.get())
                && inventoryContains(inv, FinalityCircuitItems.CIRCUIT_FINALITY_3.get())
                && inventoryContains(inv, FinalityCircuitItems.CIRCUIT_FINALITY_4.get());
    }

    private static void checkTimeAndDateEvents(ServerPlayer player) {
        long dayTime = player.serverLevel().getDayTime() % 24000L;
        if (dayTime >= 21000L && dayTime <= 22000L) {
            Hk3EventService.tryTriggerFirstTime(player, "E-EG-053", "hk3gtl.event.eg053");
        }
        LocalDate now = LocalDate.now();
        if (now.getMonthValue() == 4 && now.getDayOfMonth() == 1) {
            Hk3EventService.tryTriggerFirstTime(player, "E-EG-051", "hk3gtl.event.eg051");
        }
        if (now.getMonthValue() == 12 && now.getDayOfMonth() == 25) {
            Hk3EventService.tryTriggerFirstTime(player, "E-EG-052", "hk3gtl.event.eg052");
        }
        if (now.getMonthValue() == 6 && now.getDayOfMonth() == 9) {
            Hk3EventService.tryTriggerFirstTime(player, "E-EG-058", "hk3gtl.event.eg058");
        }
    }

    private static String mapAnvilNameToEvent(String name) {
        if (name == null || name.isBlank()) {
            return null;
        }
        String normalized = name.toLowerCase(Locale.ROOT).replace(" ", "");
        return switch (normalized) {
            case "西琳", "sirin" -> "E-EG-086";
            case "琪亚娜", "kiana" -> "E-EG-087";
            case "芽衣", "mei" -> "E-EG-088";
            case "崩坏", "honkai" -> "E-EG-089";
            case "终焉", "finality" -> "E-EG-090";
            default -> null;
        };
    }

    private static String langKeyForEvent(String eventId) {
        String suffix = eventId.substring(2).toLowerCase(Locale.ROOT).replace("-", "");
        return "hk3gtl.event." + suffix;
    }

    // ═══════════════════════════════════════════
    //  工具方法
    // ═══════════════════════════════════════════

    /** 外部查询接口：检查指定服务端玩家是否已触发某事件 */
    public static boolean hasTriggered(ServerPlayer player, String eventId) {
        return Hk3EventService.hasTriggered(player, eventId);
    }

    /** 外部查询接口：通用 Player 版本（客户端也可调用） */
    public static boolean hasTriggered(Player player, String eventId) {
        return Hk3EventService.hasTriggered(player, eventId);
    }

    /** 向玩家发放虚空万藏；背包满则掉落地面。 */
    private static void grantVoidArchives(ServerPlayer player) {
        ItemStack gift = new ItemStack(AbyssFunctionalItems.ARTIFACT_VOID_ARCHIVES.get(), 1);
        if (!player.addItem(gift)) {
            player.drop(gift, false);
        }
    }

    /** 扫描背包是否包含指定物品标签 */
    private static boolean inventoryContainsTag(Inventory inv, TagKey<Item> tag) {
        for (int i = 0; i < inv.getContainerSize(); i++) {
            if (inv.getItem(i).is(tag)) {
                return true;
            }
        }
        return false;
    }

    /** 扫描背包是否包含指定物品（精确匹配 Item） */
    private static boolean inventoryContains(Inventory inv, Item item) {
        for (int i = 0; i < inv.getContainerSize(); i++) {
            if (inv.getItem(i).is(item)) return true;
        }
        return false;
    }

    /** 按物品 ID 检查背包。目标物品未注册（返回 AIR）时直接判定 false。 */
    private static boolean inventoryContainsByItemId(Inventory inv, String namespace, String path) {
        Item item = BuiltInRegistries.ITEM.get(new ResourceLocation(namespace, path));
        if (item == null || item == Items.AIR) {
            return false;
        }
        return inventoryContains(inv, item);
    }

    /**
     * 检查背包是否包含魂钢锭（需要通过 NBT 对比，因为 GT 材料物品的 Item 相同，靠 NBT 区分）。
     * 首次调用时通过 ChemicalHelper 获取标准参考 ItemStack 并缓存。
     */
    private static boolean inventoryContainsSouliumIngot(Inventory inv) {
        if (souliumIngotRef == null) {
            souliumIngotRef = ChemicalHelper.get(TagPrefix.ingot, SouliumMaterial.SOULIUM);
        }
        if (souliumIngotRef.isEmpty()) return false;
        for (int i = 0; i < inv.getContainerSize(); i++) {
            ItemStack stack = inv.getItem(i);
            if (ItemStack.isSameItemSameTags(stack, souliumIngotRef)) return true;
        }
        return false;
    }

    /** 向玩家发送灰色提示消息（通常紧随事件消息之后） */
    private static void sendHint(ServerPlayer player, String key) {
        player.sendSystemMessage(
                Component.literal("§7").append(Component.translatable(key)));
    }

    /**
     * 将玩家传送至虚数维度（确保平台和西琳已生成，强制冒险模式）。
     * 触发条件：背包检测到虚数四·虚序主脑且 E-MS-006 尚未标记、终局对话未完成。
     */
    private static void teleportToImaginaryDimension(ServerPlayer player) {
        if (Hk3GraduationData.get(player.serverLevel()).isGraduated()) {
            LOGGER.debug("[HK3GTL] 世界已毕业，跳过虚数维度传送");
            return;
        }
        ServerLevel imaginary = player.server.getLevel(Hk3Dimensions.IMAGINARY);
        if (imaginary == null) {
            LOGGER.warn("[HK3GTL] 虚数维度未加载，无法传送玩家");
            return;
        }
        VoidQueenSirinEntity.ensurePlatformAndEntity(imaginary);
        player.setGameMode(GameType.ADVENTURE);
        player.teleportTo(imaginary,
                Hk3Dimensions.SPAWN_X + 0.5, Hk3Dimensions.SPAWN_Y, Hk3Dimensions.SPAWN_Z + 0.5,
                0f, 0f);
        LOGGER.info("[HK3GTL] 玩家 {} 持有虚数四·虚序主脑，已传送至虚数维度", player.getName().getString());
    }
}
