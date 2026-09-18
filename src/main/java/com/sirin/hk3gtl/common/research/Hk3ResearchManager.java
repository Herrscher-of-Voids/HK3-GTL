package com.sirin.hk3gtl.common.research;



import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.civ.Hk3CivExchange;
import com.sirin.hk3gtl.common.event.Hk3EventManager;
import com.sirin.hk3gtl.common.event.Hk3EasterEggChecker;
import com.sirin.hk3gtl.common.event.Hk3FactionEventChecker;
import com.sirin.hk3gtl.common.gaze.Hk3GazeManager;
import com.sirin.hk3gtl.common.machine.research.Hk3ResearchMatrixMachine;
import com.sirin.hk3gtl.common.network.Hk3Network;
import com.sirin.hk3gtl.common.network.ResearchOpenS2CPacket;
import com.sirin.hk3gtl.common.network.ResearchStateSyncS2CPacket;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.network.PacketDistributor;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

import java.util.List;
import java.util.stream.Collectors;

/**
 * P2 研究系统第一版管理器（Forge 事件订阅 + 外部桥接入口）。
 *
 * <h3>系统定位</h3>
 * 当前实现目标不是完整的容器菜单，而是先把"研究状态流"做稳定：
 * <ul>
 *   <li>状态存储：玩家 persistentData（跟随玩家数据持久化）</li>
 *   <li>触发方式：事件自动完成 + 满足条件后的自动提交</li>
 *   <li>奖励方式：写入研究完成标记，并发放对应研究许可物</li>
 * </ul>
 *
 * <h3>设计原因</h3>
 * <ul>
 *   <li>先验证研究节点、前置、提交物、许可物门槛是否跑通</li>
 *   <li>避免系统尚未稳定前就把 GUI、时间公式、复杂研究台一起堆上</li>
 *   <li>持久化依托玩家数据而不是单独 WorldSavedData —— 便于跨存档迁移、单玩家独立进度</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li><b>新增研究节点</b>：在 {@link Hk3ResearchNodes} 中添加，不在此文件新增</li>
 *   <li><b>新增提交方式</b>：在 {@link #submitResearchById(ServerPlayer, String)} 前后拓展，保持校验顺序：节点合法 → 前置 → 物品 → 扣除 → 完成</li>
 *   <li><b>新增事件驱动</b>：在 {@link #onEventTriggered(ServerPlayer, String)} 分发；兜底扫描在 {@link #syncEventResearches(ServerPlayer)}</li>
 *   <li><b>客户端同步</b>：任何研究状态变更后必须调用 {@link #syncClientResearchState(ServerPlayer)}，否则客户端 GUI 灰度不准</li>
 *   <li><b>不要改 TAG_PREFIX 常量值</b>：旧存档依赖 {@code hk3gtl_res_} 前缀，修改将导致所有玩家研究进度丢失</li>
 *   <li><b>许可物发放</b>：当前版本通过 {@code unlockDescriptionKey} 翻译文本提示，真正的许可物作为 GT 配方 notConsumable 输入使用</li>
 *   <li><b>线程安全</b>：所有公开方法均应在服务端主线程调用；persistentData 非线程安全</li>
 *   <li><b>矩阵交互</b>：修改 {@link #ABYSS_RESEARCH_MATRIX_ID} 以替换研究矩阵方块 ID</li>
 * </ul>
 */
@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public class Hk3ResearchManager {

    private static final Logger LOGGER = LogUtils.getLogger();

    /** 研究状态在 persistentData 中的键前缀，完整格式: "hk3gtl_res_R-AB-001" = true/false */
    private static final String TAG_PREFIX = "hk3gtl_res_";

    /** 玩家当前选中研究目标的键 */
    private static final String SELECTED_RESEARCH_TAG = "hk3gtl_res_selected";

    /** 研究矩阵控制器方块 ID，用于拦截右键交互并打开 GUI */
    private static final ResourceLocation ABYSS_RESEARCH_MATRIX_ID =
            new ResourceLocation(Hk3Constants.MOD_ID, "abyss_research_analysis_matrix");

    /**
     * 第一版研究系统采用“每秒扫描一次”的低频策略。
     *
     * 这样做的好处：
     * - 简单稳定，便于联调
     * - 不需要先做复杂的研究台容器逻辑
     *
     * 后续若改为正式研究矩阵 GUI，可把这里的自动推进逻辑收缩为兜底或调试逻辑。
     */
    /** 由统一玩家每秒入口调用，保留事件型研究的兜底同步。 */
    public static void onPlayerSecond(ServerPlayer player) {
        syncEventResearches(player);
    }

    @SubscribeEvent
    public static void onPlayerLoggedIn(PlayerEvent.PlayerLoggedInEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) {
            syncEventResearches(player);
            syncClientResearchState(player);
        }
    }

    /**
     * 服务端权威打开研究矩阵 GUI：先同步状态，再发打开包，避免客户端绕过服务端状态。
     */
    @SubscribeEvent
    public static void onResearchMatrixInteract(PlayerInteractEvent.RightClickBlock event) {
        if (event.getHand() != InteractionHand.MAIN_HAND) return;
        if (event.getLevel().isClientSide()) return;
        if (!(event.getEntity() instanceof ServerPlayer player)) return;

        ResourceLocation clickedId = BuiltInRegistries.BLOCK.getKey(event.getLevel().getBlockState(event.getPos()).getBlock());
        if (!ABYSS_RESEARCH_MATRIX_ID.equals(clickedId)) return;

        // Shift+右键留给终端自动搭建和其它 GT 原生交互。
        if (player.isShiftKeyDown()) return;

        event.setCanceled(true);
        event.setCancellationResult(InteractionResult.SUCCESS);
        syncClientResearchState(player);
        Hk3Network.CHANNEL.send(
                PacketDistributor.PLAYER.with(() -> player),
                new ResearchOpenS2CPacket()
        );
    }

    /** 检查指定玩家是否已完成某研究节点（服务端 ServerPlayer 版本） */
    public static boolean isCompleted(ServerPlayer player, String researchId) {
        return player.getPersistentData().getBoolean(TAG_PREFIX + researchId);
    }

    /** 检查指定玩家是否已完成某研究节点（通用 Player 版本，客户端/服务端均可用） */
    public static boolean isCompleted(Player player, String researchId) {
        return player.getPersistentData().getBoolean(TAG_PREFIX + researchId);
    }

    /** 检查 CompoundTag 中是否已完成某研究（用于批量检查时避免重复获取 persistentData） */
    public static boolean isCompleted(CompoundTag data, String researchId) {
        return data.getBoolean(TAG_PREFIX + researchId);
    }

    /** 事件触发时调用，遍历所有自动完成型节点并尝试完成（由 Hk3EventManager 桥接） */
    public static void onEventTriggered(ServerPlayer player, String eventId) {
        boolean changed = false;
        for (Hk3ResearchNode node : Hk3ResearchNodes.ordered()) {
            if (node.isAutoComplete()
                    && eventId.equals(node.autoCompleteEventId())
                    && !isCompleted(player, node.id())
                    && prerequisitesMet(player, node)) {
                completeResearch(player, node, false);
                changed = true;
            }
        }
        if (changed) {
            syncClientResearchState(player);
        }
    }

    /**
     * 兜底同步“事件型研究”。
     *
     * 理论上事件触发时会立刻调用 onEventTriggered，
     * 这里再扫一次是为了防止：
     * - 历史存档里事件先于研究系统存在
     * - 某次触发过程中桥接没有及时执行
     */
    private static void syncEventResearches(ServerPlayer player) {
        boolean changed = false;
        for (Hk3ResearchNode node : Hk3ResearchNodes.ordered()) {
            if (!node.isAutoComplete()) continue;
            if (isCompleted(player, node.id())) continue;
            if (!prerequisitesMet(player, node)) continue;
            if (!Hk3EventManager.hasTriggered(player, node.autoCompleteEventId())) continue;
            completeResearch(player, node, false);
            changed = true;
        }
        if (changed) {
            syncClientResearchState(player);
        }
    }

    /** 获取玩家可选择的未完成手动研究节点列表 */
    private static List<Hk3ResearchNode> getSelectableResearches(Player player) {
        return Hk3ResearchNodes.ordered().stream()
                .filter(Hk3ResearchNode::isManualResearch)
                .filter(node -> !isCompleted(player, node.id()))
                .collect(Collectors.toList());
    }

    /** 获取所有手动提交型节点（供 GUI 展示，不过滤已完成） */
    public static List<Hk3ResearchNode> getManualResearchNodes() {
        return Hk3ResearchNodes.ordered().stream()
                .filter(Hk3ResearchNode::isManualResearch)
                .collect(Collectors.toList());
    }

    /** 前置检查的公开版本，供客户端 GUI 显示灰度/可用状态 */
    public static boolean prerequisitesMetForDisplay(Player player, Hk3ResearchNode node) {
        return prerequisitesMet(player, node);
    }

    /** 提交物检查的公开版本，供客户端 GUI 显示"材料是否齐全" */
    public static boolean hasRequirementsForDisplay(Player player, Hk3ResearchNode node) {
        return hasRequirements(player.getInventory(), node);
    }

    /** 获取玩家当前选中的研究目标，若无效则自动回退到第一个可选节点 */
    private static Hk3ResearchNode getSelectedResearch(Player player) {
        CompoundTag data = player.getPersistentData();
        String selectedId = data.getString(SELECTED_RESEARCH_TAG);
        Hk3ResearchNode selected = Hk3ResearchNodes.get(selectedId);
        if (selected != null && selected.isManualResearch() && !isCompleted(player, selected.id())) {
            return selected;
        }

        List<Hk3ResearchNode> selectable = getSelectableResearches(player);
        if (selectable.isEmpty()) {
            return null;
        }

        Hk3ResearchNode fallback = selectable.get(0);
        data.putString(SELECTED_RESEARCH_TAG, fallback.id());
        return fallback;
    }

    /** 循环切换研究目标（旧版命令行交互用，现已由 GUI 替代） */
    private static void cycleSelectedResearch(Player player) {
        List<Hk3ResearchNode> selectable = getSelectableResearches(player);
        if (selectable.isEmpty()) {
            player.sendSystemMessage(Component.literal("§7")
                    .append(Component.translatable("hk3gtl.research.no_manual_targets")));
            return;
        }

        CompoundTag data = player.getPersistentData();
        String currentId = data.getString(SELECTED_RESEARCH_TAG);
        int currentIndex = -1;
        for (int i = 0; i < selectable.size(); i++) {
            if (selectable.get(i).id().equals(currentId)) {
                currentIndex = i;
                break;
            }
        }

        int nextIndex = (currentIndex + 1) % selectable.size();
        Hk3ResearchNode next = selectable.get(nextIndex);
        data.putString(SELECTED_RESEARCH_TAG, next.id());

        player.sendSystemMessage(Component.literal("§b[崩坏三-GTL] §f")
                .append(Component.translatable("hk3gtl.research.selected",
                        Component.translatable(next.nameKey()))));
    }

    /** 尝试提交当前选中研究：校验前置 → 校验物品 → 扣除物品 → 标记完成 */
    private static void trySubmitSelectedResearch(ServerPlayer player) {
        Hk3ResearchNode node = getSelectedResearch(player);
        if (node == null) {
            player.sendSystemMessage(Component.literal("§7")
                    .append(Component.translatable("hk3gtl.research.no_manual_targets")));
            return;
        }

        if (!prerequisitesMet(player, node)) {
            if (node.requiresEvent() && !Hk3EventManager.hasTriggered(player, node.requiredEventId())) {
                player.sendSystemMessage(Component.literal("§c")
                        .append(Component.translatable("hk3gtl.research.matrix_required")));
                return;
            }

            for (String prerequisite : node.prerequisites()) {
                if (!isCompleted(player, prerequisite)) {
                    Hk3ResearchNode prerequisiteNode = Hk3ResearchNodes.get(prerequisite);
                    Component prerequisiteName = prerequisiteNode == null
                            ? Component.literal(prerequisite)
                            : Component.translatable(prerequisiteNode.nameKey());
                    player.sendSystemMessage(Component.literal("§c")
                            .append(Component.translatable("hk3gtl.research.missing_prerequisite", prerequisiteName)));
                    return;
                }
            }
        }

        if (!hasRequirements(player.getInventory(), node)) {
            player.sendSystemMessage(Component.literal("§c")
                    .append(Component.translatable("hk3gtl.research.missing_items",
                            Component.translatable(node.nameKey()))));
            return;
        }

        consumeRequirements(player.getInventory(), node);
        completeResearch(player, node, true);
    }

    /**
     * GUI 使用的服务端提交入口。
     *
     * <p>新版流程（改由研究矩阵机器承担研究过程）：</p>
     * <ol>
     *   <li>校验：节点存在 / 为手动型 / 前置满足 / 未完成 / 玩家背包足够</li>
     *   <li>查找玩家附近已成型的研究矩阵（{@link Hk3ResearchMatrixMachine#findNearest}）</li>
     *   <li>若找到且空闲 → 委托 {@code tryStart}，机器自行 tick 推进进度、消耗能量、完成时扣物品</li>
     *   <li>若找不到或机器忙 → 报错（不再走旧版"立即完成"逻辑）</li>
     * </ol>
     *
     * <p>物品消耗时机变化：旧版 GUI 提交就扣物品；新版"开始研究"时不扣，研究完成时才扣，
     * 给玩家反悔余地（研究中断不会丢材料）。</p>
     */
    public static void submitResearchById(ServerPlayer player, String researchId) {
        Hk3ResearchNode node = Hk3ResearchNodes.get(researchId);
        if (node == null || !node.isManualResearch()) {
            player.sendSystemMessage(Component.literal("§c")
                    .append(Component.translatable("hk3gtl.research.invalid_target")));
            return;
        }
        if (isCompleted(player, researchId)) {
            player.sendSystemMessage(Component.literal("§7")
                    .append(Component.translatable("hk3gtl.research.already_completed",
                            Component.translatable(node.nameKey()))));
            return;
        }
        if (!prerequisitesMet(player, node)) {
            player.sendSystemMessage(Component.literal("§c")
                    .append(Component.translatable("hk3gtl.research.missing_prerequisite_generic",
                            Component.translatable(node.nameKey()))));
            return;
        }
        if (!hasRequirements(player.getInventory(), node)) {
            player.sendSystemMessage(Component.literal("§c")
                    .append(Component.translatable("hk3gtl.research.missing_items",
                            Component.translatable(node.nameKey()))));
            return;
        }

        Hk3ResearchMatrixMachine matrix = Hk3ResearchMatrixMachine.findNearest(player);
        if (matrix == null) {
            player.sendSystemMessage(Component.literal("§c")
                    .append(Component.translatable("hk3gtl.research.matrix.no_nearby",
                            Hk3Constants.RESEARCH_MATRIX_SEARCH_RADIUS)));
            return;
        }

        boolean ok = matrix.tryStart(player, node);
        if (ok) {
            player.getPersistentData().putString(SELECTED_RESEARCH_TAG, node.id());
            syncClientResearchState(player);
        }
    }

    /**
     * 研究前置检查包含两类门槛：
     * - 研究节点依赖
     * - 事件依赖（例如研究矩阵已激活）
     */
    private static boolean prerequisitesMet(Player player, Hk3ResearchNode node) {
        CompoundTag data = player.getPersistentData();
        for (String prerequisite : node.prerequisites()) {
            if (!isCompleted(data, prerequisite)) return false;
        }
        if (node.requiresEvent() && !Hk3EventManager.hasTriggered(player, node.requiredEventId())) {
            return false;
        }
        if (Hk3CivExchange.getLevel(player) < node.requiredCivLevel()) {
            return false;
        }
        return true;
    }

    /**
     * 检查玩家背包是否包含节点所需的全部提交物。
     * 公开可见：研究矩阵机器在"研究完成时"需要二次校验（防止启动后玩家把材料扔掉）。
     */
    public static boolean hasRequirements(Inventory inventory, Hk3ResearchNode node) {
        for (Hk3ResearchRequirement requirement : node.requirements()) {
            if (!hasRequirement(inventory, requirement)) {
                return false;
            }
        }
        return true;
    }

    /**
     * 从玩家背包扣除节点所需的全部提交物。
     * 公开可见：研究矩阵机器在"研究完成时"消耗物品（研究期间物品留在玩家手上，给玩家留反悔余地）。
     */
    public static void consumeRequirements(Inventory inventory, Hk3ResearchNode node) {
        for (Hk3ResearchRequirement requirement : node.requirements()) {
            if (requirement.isTagMode()) {
                removeMatchingItems(inventory, requirement, ItemStack.EMPTY, requirement.tagCount());
                continue;
            }
            ItemStack matched = firstAvailableRequirement(inventory, requirement);
            if (!matched.isEmpty()) {
                removeMatchingItems(inventory, requirement, matched, matched.getCount());
            }
        }
        inventory.setChanged();
    }

    private static boolean hasRequirement(Inventory inventory, Hk3ResearchRequirement requirement) {
        if (requirement.isTagMode()) {
            return inventoryContains(inventory, requirement, ItemStack.EMPTY, requirement.tagCount());
        }
        return !firstAvailableRequirement(inventory, requirement).isEmpty();
    }

    private static ItemStack firstAvailableRequirement(Inventory inventory, Hk3ResearchRequirement requirement) {
        for (ItemStack candidate : requirement.createCandidates()) {
            if (candidate.isEmpty()) continue;
            if (inventoryContains(inventory, requirement, candidate, candidate.getCount())) {
                return candidate;
            }
        }
        return ItemStack.EMPTY;
    }

    /** 检查背包是否包含满足需求的物品（精确 Item+NBT 或 Tag 匹配，累计数量） */
    private static boolean inventoryContains(Inventory inventory, Hk3ResearchRequirement requirement,
                                             ItemStack candidate, int required) {
        int remaining = required;
        for (int i = 0; i < inventory.getContainerSize(); i++) {
            ItemStack stack = inventory.getItem(i);
            if (!requirement.matchesStack(candidate, stack)) continue;
            remaining -= stack.getCount();
            if (remaining <= 0) return true;
        }
        return false;
    }

    /** 从背包移除指定数量的匹配物品（跨格位累计扣除，Tag 模式跨物品种类扣除） */
    private static void removeMatchingItems(Inventory inventory, Hk3ResearchRequirement requirement,
                                            ItemStack candidate, int required) {
        int remaining = required;
        for (int i = 0; i < inventory.getContainerSize() && remaining > 0; i++) {
            ItemStack stack = inventory.getItem(i);
            if (!requirement.matchesStack(candidate, stack)) continue;

            int taken = Math.min(stack.getCount(), remaining);
            stack.shrink(taken);
            remaining -= taken;
        }
    }

    /**
     * 统一收口“研究完成”的副作用。
     *
     * 当前完成研究后会：
     * - 写研究标记
     * - 发聊天提示
     * - 按节点定义发放研究许可物
     *
     * 许可物是当前研究门槛系统的关键：
     * 它们作为 GT 配方的 notConsumable 输入使用，能在不深改 GT 核心配方匹配逻辑的前提下提供阶段门槛。
     */
    private static void completeResearch(ServerPlayer player, Hk3ResearchNode node, boolean consumedItems) {
        CompoundTag data = player.getPersistentData();
        data.putBoolean(TAG_PREFIX + node.id(), true);

        LOGGER.info("[HK3GTL] 研究完成: {} (consumed={})", node.id(), consumedItems);
        Hk3GazeManager.addGaze(player, 5);

        // ── 三行剧情化聊天（由 ResearchAcademyChatter 提供人物 + 台词池）──
        String researcher = ResearchAcademyChatter.randomResearcher();
        // 聊天里同样隐藏内部编号 "R-XX-NNN"，只显示中文研究名。
        String researchName = Hk3ResearchNodes.stripIdPrefix(
                Component.translatable(node.nameKey()).getString());
        String progress = ResearchAcademyChatter.randomProgressLine("§e§l" + researchName + "§r");

        // 头行：研究院电台抬头 + 研究员名牌 + 进展台词
        player.sendSystemMessage(Component.literal("§6[崩坏能研究院] " + researcher + " " + progress));

        // 次行：节点 unlockDescription 作为成果详情，灰色斜体呈现
        player.sendSystemMessage(Component.literal("§7§o  ▸ ")
                .append(Component.translatable(node.unlockDescriptionKey())));

        // 尾行：内部花絮 / 彩蛋台词，营造研究院"有人味"的氛围
        player.sendSystemMessage(Component.literal(ResearchAcademyChatter.randomFlavorLine()));

        Hk3FactionEventChecker.onResearchCompleted(player, node.id());
        Hk3EasterEggChecker.onResearchCompleted(player, node.id());
    }

    /**
     * 外部调用入口：跳过前置/提交物检查，直接标记研究节点为完成。
     * 用于解锁凭证物品的 Shift+右键激活。
     */
    public static void forceCompleteResearch(ServerPlayer player, String researchId) {
        Hk3ResearchNode node = Hk3ResearchNodes.get(researchId);
        if (node == null) return;
        if (isCompleted(player, researchId)) return;
        completeResearch(player, node, false);
        syncClientResearchState(player);
    }

    /** 将玩家的全部研究状态（含事件状态、选中目标、附近研究矩阵快照）通过网络包同步到客户端 */
    public static void syncClientResearchState(ServerPlayer player) {
        CompoundTag playerData = player.getPersistentData();
        CompoundTag syncTag = new CompoundTag();
        for (String key : playerData.getAllKeys()) {
            if (key.startsWith(TAG_PREFIX)
                    || key.startsWith("hk3gtl_evt_")
                    || key.startsWith("hk3gtl_nar_")
                    || "hk3gtl_gaze_level".equals(key)
                    || "hk3gtl_civ_level".equals(key)
                    || "hk3gtl_voltage_tier".equals(key)
                    || SELECTED_RESEARCH_TAG.equals(key)) {
                syncTag.put(key, playerData.get(key).copy());
            }
        }
        appendNearestMatrixSnapshot(player, syncTag);

        Hk3Network.CHANNEL.send(
                PacketDistributor.PLAYER.with(() -> player),
                new ResearchStateSyncS2CPacket(syncTag)
        );
    }

    private static void appendNearestMatrixSnapshot(ServerPlayer player, CompoundTag syncTag) {
        Hk3ResearchMatrixMachine matrix = Hk3ResearchMatrixMachine.findNearest(player);
        CompoundTag matrixTag = new CompoundTag();
        matrixTag.putBoolean("present", matrix != null);
        if (matrix != null) {
            matrixTag.putBoolean("busy", matrix.isBusy());
            Hk3ResearchMatrixMachine.Snapshot snapshot = matrix.snapshot();
            if (snapshot != null) {
                matrixTag.putString("research", snapshot.researchId());
                matrixTag.putInt("progress", snapshot.progress());
                matrixTag.putInt("total", snapshot.totalTicks());
                matrixTag.putLong("extra", snapshot.extraEutPerTick());
                matrixTag.putDouble("speedFactor", snapshot.speedFactor());
                matrixTag.putLong("gameTime", player.serverLevel().getGameTime());
            }
        }
        syncTag.put("hk3gtl_research_matrix", matrixTag);
    }
}
