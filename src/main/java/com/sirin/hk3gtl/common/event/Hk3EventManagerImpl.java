package com.sirin.hk3gtl.common.event;


/** 中文说明：该处说明已按当前代码行为整理。*/
import com.gregtechceu.gtceu.api.data.chemical.ChemicalHelper;
import com.sirin.hk3gtl.common.communication.Hk3FirstContactService;
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
/**
 * 【变更记录 #3】2026-09-30 15:49:23（第3次编号备注 · 内测5修订109）
 * 删除：过期的计算或无运行依据的分支；保留历史备注。
 * 新增／修改：原有注视事件增加明确来源键和持久去重；数值与触发条件不变，不追补旧记录，不以此完成新课题。
 * 用途：统一注视与研究联动，服务端判定；不新增结构或贴图。
 */
/**
 * 【变更记录 #4】2026-09-30 16:20:43（内测5修订110）
 * 删除：被新版通知读取流程替代的旧分支，历史备注保留。
 * 新增／修改：事件后附带提示持久入箱并按键去重；物品操作与命令反馈保持原入口。
 * 用途：通知与业务结果分离，服务端授权和个人持久化；不改结构、贴图和贸易。
 */
@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
/**
 * 【变更记录 #1】2026-09-26 23:56:20（第 1 次备注 · 内测5修订76）
 * - 删除：无，保留存档、历史备注和所有能量数值。
 * - 新增：本地崩坏能仓余额与容量的 HW 单位。
 * - 修改：仅右键查询显示文字，与双能源 GUI 单位一致。
 * - 用途：统一玩家可见单位，不改变充放电、换算或持久化逻辑。
 */
/**
 * 【变更记录 #2】2026-09-30 02:17:47（第2次备注 · 内测5修订107）
 * 删除：本文件可执行代码中的旧电压键及常量引用，不保留旧键注册别名。
 * 新增：16档正式缩写作为唯一电压标识；逐文件映射见logs/voltage-keys-r107。
 * 修改：注册、配方、查询或标签引用按原tier序号一一迁移；数值、层级与资源内容保持原义。
 * 用途：避免显示名与实际注册键不一致；历史备注保留，旧存档不自动改写。
 */
/** 【变更记录 #5】2026-09-30 23:34:26（修订119）：删除：世界级结果对所有玩家的隐式授权；新增/修改：毕业/传送/彩蛋/调试改为查询当前玩家，实体避免在已有坏结局演出时开启新会面；用途：个人结算不覆盖其他玩家，未完成的资格采集仍单独接入。 */
/** 【变更记录 #6】2026-10-01 01:56:49（修订127）：删除：被替代的旧分支；新增/修改：移除未调用且日期错误的旧彩蛋时间副本，保留统一时钟入口与命名彩蛋；用途：个人收藏与正式资格分离，保留历史记录。 */
/** 【变更记录 #7】2026-10-01 03:55:10（修订128）：删除：旧固定上限或被替代的分支；新增/修改：铁砧彩蛋取出时复核成品真实名称，非目标名立即清预览缓存，防取消改名后误触发；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #8】2026-10-01 04:09:54（修订128）：删除：旧固定上限或被替代的分支；新增/修改：真实铁砧取出后按成品精确中文名匹配独立规则，不承认预览或英文别名；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #9】2026-10-01 04:21:47（修订128）：删除：旧固定上限或被替代的分支；新增/修改：停止已退役的旧彩蛋轮询，其余正式剧情事件原样保留；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #10】2026-10-01 16:49:18（修订135）：删除E-MS-006持电路自动传送及孤立传送函数；新增无；修改仅保留原里程碑提示，正式终审由权威资格申请进入；用途：避免跳过100课题、工程及个人经历，旧实现保存在修订定向备份。 */
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
        // 修订128：500目录改由独立原生事件执行，不再运行旧彩蛋附近机器/库存差分轮询。
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

        // 内测5首信仅记录情报，禁止调用旧奖励/研究桥接；旧触发完整源码已归档。
        // 中文备注：该处说明已按当前代码行为整理。
        Hk3FirstContactService.checkInventory(player);

        // E-MS-002: 魂钢文明诞生 — 首次获得魂钢锭
        if (!Hk3EventService.isEventMarked(data, "E-MS-002") && inventoryContainsSouliumIngot(inv)) {
            Hk3EventService.tryTriggerFirstTime(player, "E-MS-002", "hk3gtl.event.ms002");
        }

        // E-MS-003: 海渊突破 — 首次获得海渊I电路（仅里程碑与凝视，不再传送虚数维度）
        if (!Hk3EventService.isEventMarked(data, "E-MS-003")
                && inventoryContains(inv, AbyssCircuitItems.CIRCUIT_HBV.get())) {
            if (Hk3EventService.tryTriggerFirstTime(player, "E-MS-003", "hk3gtl.event.ms003")) {
                Hk3GazeManager.addGazeOnce(player, 50, "milestone:E-MS-003");
            }
        }

        // E-MS-004: 深海征服 — 首次获得海渊IV电路
        if (!Hk3EventService.isEventMarked(data, "E-MS-004")
                && inventoryContains(inv, AbyssCircuitItems.CIRCUIT_HDV.get())) {
            Hk3EventService.tryTriggerFirstTime(player, "E-MS-004", "hk3gtl.event.ms004");
        }

        // E-MS-005: 虚数觉醒 — 首次获得虚数I电路
        if (!Hk3EventService.isEventMarked(data, "E-MS-005")
                && inventoryContains(inv, ImaginaryCircuitItems.CIRCUIT_QSV.get())) {
            Hk3EventService.tryTriggerFirstTime(player, "E-MS-005", "hk3gtl.event.ms005");
        }

        // E-MS-006仅记录电路里程碑，不作为终审工程或个人资格。
        if (!Hk3EventService.isEventMarked(data, "E-MS-006")
                && inventoryContains(inv, ImaginaryCircuitItems.CIRCUIT_QAV.get())) {
            Hk3EventService.tryTriggerFirstTime(player, "E-MS-006", "hk3gtl.event.ms006");
        }

        // E-MS-007: 量子跃迁 — 首次获得量子I电路
        if (!Hk3EventService.isEventMarked(data, "E-MS-007")
                && inventoryContains(inv, QuantumCircuitItems.CIRCUIT_IMV.get())) {
            Hk3EventService.tryTriggerFirstTime(player, "E-MS-007", "hk3gtl.event.ms007");
        }

        // E-MS-009: 量子极限 — 首次获得量子IV电路
        if (!Hk3EventService.isEventMarked(data, "E-MS-009")
                && inventoryContains(inv, QuantumCircuitItems.CIRCUIT_IWV.get())) {
            Hk3EventService.tryTriggerFirstTime(player, "E-MS-009", "hk3gtl.event.ms009");
        }

        // E-MS-010: 终焉降临 — 首次获得终焉I电路
        if (!Hk3EventService.isEventMarked(data, "E-MS-010")
                && inventoryContains(inv, FinalityCircuitItems.CIRCUIT_WFV.get())) {
            Hk3EventService.tryTriggerFirstTime(player, "E-MS-010", "hk3gtl.event.ms010");
        }

        // E-MS-012: 终焉极限 — 首次获得终焉III电路
        if (!Hk3EventService.isEventMarked(data, "E-MS-012")
                && inventoryContains(inv, FinalityCircuitItems.CIRCUIT_CIV.get())) {
            Hk3EventService.tryTriggerFirstTime(player, "E-MS-012", "hk3gtl.event.ms012");
        }

        // E-MS-013: 超越极限 — 首次获得终焉IV电路
        if (!Hk3EventService.isEventMarked(data, "E-MS-013")
                && inventoryContains(inv, FinalityCircuitItems.CIRCUIT_CEV.get())) {
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
                player.sendSystemMessage(Component.literal(String.format("§b[%s] §f崩坏能: §a%d §f/ §e%d HW", typeStr, amount, capacity)));
            }

            event.setCanceled(true);
            event.setCancellationResult(net.minecraft.world.InteractionResult.SUCCESS);
        }
    }

    @SubscribeEvent
    public static void onAnvilUpdate(AnvilUpdateEvent event) {
        if (!(event.getPlayer() instanceof ServerPlayer player)) return;
        String mapped = mapAnvilNameToEvent(event.getName());
        if (mapped == null) { player.getPersistentData().remove(ANVIL_PENDING_EVENT_TAG); return; }
        player.getPersistentData().putString(ANVIL_PENDING_EVENT_TAG, mapped);
    }

    @SubscribeEvent
    public static void onAnvilRepair(AnvilRepairEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) return;
        CompoundTag data = player.getPersistentData();
        data.remove(ANVIL_PENDING_EVENT_TAG);
        var output=event.getOutput();
        if(output.isEmpty()||!output.hasCustomHoverName())return;
        com.sirin.hk3gtl.common.easter.Hk3EggRuntime.observe(player,"anvil_taken",
            java.util.Map.of("name",output.getHoverName().getString()));
        String eventId = mapAnvilNameToEvent(output.getHoverName().getString());
        if (eventId==null) return;
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
                    Hk3GazeManager.addGazeOnce(player, 20, "milestone:E-FB-005");
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
                    Hk3GazeManager.addGazeOnce(player, 50, "milestone:E-FB-013");
                }
            }
            case "hyperion_flagship" -> {
                boolean first = !Hk3EventService.isEventMarked(data, "E-FB-015");
                tryTrigger(player, data, "E-FB-015", "hk3gtl.event.fb015");
                tryTrigger(player, data, "E-MS-011", "hk3gtl.event.ms011");
                if (first) {
                    Hk3GazeManager.addGazeOnce(player, 80, "milestone:E-FB-015");
                }
            }
            case "civilization_validation_matrix" -> {
                boolean first = !Hk3EventService.isEventMarked(data, "E-FB-016");
                tryTrigger(player, data, "E-FB-016", "hk3gtl.event.fb016");
                tryTrigger(player, data, "E-MS-014", "hk3gtl.event.ms014");
                if (first) {
                    Hk3GazeManager.addGazeOnce(player, 100, "milestone:E-FB-016");
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
        Hk3GazeManager.addGazeOnce(player, 30, "voltage:" + current);
        if (hasAllVoltageCircuits(inv)) {
            Hk3EventService.tryTriggerFirstTime(player, "E-EG-028", "hk3gtl.event.eg028");
        }
    }

    private static int detectVoltageTier(Inventory inv) {
        boolean[] tiers = new boolean[] {
                inventoryContains(inv, AbyssCircuitItems.CIRCUIT_HBV.get()),
                inventoryContains(inv, AbyssCircuitItems.CIRCUIT_HCV.get()),
                inventoryContains(inv, AbyssCircuitItems.CIRCUIT_HRV.get()),
                inventoryContains(inv, AbyssCircuitItems.CIRCUIT_HDV.get()),
                inventoryContains(inv, ImaginaryCircuitItems.CIRCUIT_QSV.get()),
                inventoryContains(inv, ImaginaryCircuitItems.CIRCUIT_QCV.get()),
                inventoryContains(inv, ImaginaryCircuitItems.CIRCUIT_QEV.get()),
                inventoryContains(inv, ImaginaryCircuitItems.CIRCUIT_QAV.get()),
                inventoryContains(inv, QuantumCircuitItems.CIRCUIT_IMV.get()),
                inventoryContains(inv, QuantumCircuitItems.CIRCUIT_ICV.get()),
                inventoryContains(inv, QuantumCircuitItems.CIRCUIT_IRV.get()),
                inventoryContains(inv, QuantumCircuitItems.CIRCUIT_IWV.get()),
                inventoryContains(inv, FinalityCircuitItems.CIRCUIT_WFV.get()),
                inventoryContains(inv, FinalityCircuitItems.CIRCUIT_WSV.get()),
                inventoryContains(inv, FinalityCircuitItems.CIRCUIT_CIV.get()),
                inventoryContains(inv, FinalityCircuitItems.CIRCUIT_CEV.get())
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
        return inventoryContains(inv, AbyssCircuitItems.CIRCUIT_HBV.get())
                && inventoryContains(inv, AbyssCircuitItems.CIRCUIT_HCV.get())
                && inventoryContains(inv, AbyssCircuitItems.CIRCUIT_HRV.get())
                && inventoryContains(inv, AbyssCircuitItems.CIRCUIT_HDV.get())
                && inventoryContains(inv, ImaginaryCircuitItems.CIRCUIT_QSV.get())
                && inventoryContains(inv, ImaginaryCircuitItems.CIRCUIT_QCV.get())
                && inventoryContains(inv, ImaginaryCircuitItems.CIRCUIT_QEV.get())
                && inventoryContains(inv, ImaginaryCircuitItems.CIRCUIT_QAV.get())
                && inventoryContains(inv, QuantumCircuitItems.CIRCUIT_IMV.get())
                && inventoryContains(inv, QuantumCircuitItems.CIRCUIT_ICV.get())
                && inventoryContains(inv, QuantumCircuitItems.CIRCUIT_IRV.get())
                && inventoryContains(inv, QuantumCircuitItems.CIRCUIT_IWV.get())
                && inventoryContains(inv, FinalityCircuitItems.CIRCUIT_WFV.get())
                && inventoryContains(inv, FinalityCircuitItems.CIRCUIT_WSV.get())
                && inventoryContains(inv, FinalityCircuitItems.CIRCUIT_CIV.get())
                && inventoryContains(inv, FinalityCircuitItems.CIRCUIT_CEV.get());
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

    /** 中文说明：该处说明已按当前代码行为整理。*/
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

    /** 中文说明：该处说明已按当前代码行为整理。*/
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
        com.sirin.hk3gtl.common.phone.Hk3PhoneService.notify(player,"hint_"+key,"记录补充",Component.translatable(key).getString());
    }

}
