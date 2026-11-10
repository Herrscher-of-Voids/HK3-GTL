package com.sirin.hk3gtl.common.multiblock.build;

import appeng.api.config.Actionable;
import appeng.api.networking.IGrid;
import appeng.api.networking.IGridNode;
import appeng.api.networking.security.IActionSource;
import appeng.api.stacks.AEItemKey;
import appeng.api.storage.MEStorage;
import com.gregtechceu.gtceu.api.block.MetaMachineBlock;
import com.lowdragmc.lowdraglib.utils.BlockInfo;
import com.mojang.logging.LogUtils;
import net.minecraft.core.BlockPos;
import net.minecraft.core.GlobalPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.BedBlock;
import net.minecraft.world.level.block.DoorBlock;
import net.minecraft.world.level.block.DoublePlantBlock;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.LightBlock;
import net.minecraft.world.level.block.SlabBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.SlabType;
import net.minecraftforge.items.IItemHandler;
import net.minecraftforge.items.ItemHandlerHelper;
import net.minecraftforge.common.capabilities.ForgeCapabilities;
import org.gtlcore.gtlcore.api.pattern.AdvancedBlockPattern;
import org.gtlcore.gtlcore.common.item.UltimateTerminalBehavior.AutoBuildSetting;
import org.gtlcore.gtlcore.integration.ae2.WirelessTerminalGridResolver;
import org.slf4j.Logger;
import oshi.util.tuples.Triplet;

import java.util.ArrayList;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

/**
 * 【文件职责】为逐格建造提供可回退的物品与AE材料预留，所有操作限服务器线程。
 * 【变更记录 #1】2026-10-30 01:31:17（第1次备注 · 内测5修订184）
 * - 新增：生存材料预扣、提交与取消返还；AE提取失败不丢失已扣物品。
 * - 用途：让建造器在放置前确认材料，放置成功后提交，失败则回滚材料。
 * 【变更记录 #2】2026-10-30 01:36:10（第2次备注 · 内测5修订184）
 * - 新增：向统一入口暴露当前AutoBuildSetting兼容性。
 * - 用途：不支持的替换、翻转、重复层及拆除选项在开工前明确拒绝。
 * 【变更记录 #3】2026-10-30 02:11:18（第3次备注 · 内测5修订184）
 * - 修复：AE来源认证、精确扣料、部分退款及异常后盲目补发；双层台阶支持跨槽扣料。
 * - 新增：GT空机器默认NBT比对；禁止载入蓝图库存、能量、流体或其他非默认数据。
 * 【变更记录 #4】2026-10-30（修订184）：LightBlock的level是亮度，保留精确物品扣料且每格扣一块，不按储存资源拒绝。
 */
public final class Hk3BuildMaterials {
    private static final Logger LOGGER = LogUtils.getLogger();
    private static final Set<String> POSITION_ONLY_TAGS = Set.of("id", "x", "y", "z");
    private static final Set<String> STACKED_PROPERTIES = Set.of("candles", "pickles", "eggs", "layers", "flower_amount");
    private static final Set<String> RESOURCE_PROPERTIES = Set.of("charges", "honey_level", "level", "age", "stage");

    private final ServerPlayer player;
    private final ServerLevel level;
    private final AutoBuildSetting setting;
    private final Map<BlockState, CompoundTag> defaultTags = new IdentityHashMap<>();

    public Hk3BuildMaterials(ServerPlayer player, AutoBuildSetting setting) {
        this.player = Objects.requireNonNull(player);
        this.level = player.serverLevel();
        this.setting = Objects.requireNonNull(setting);
    }

    public boolean isSupported() {
        return setting.getRepeatCount() == 0 && !setting.isDismantleMode() && !setting.isReplaceMode()
                && !setting.isFlipped() && setting.isNoHatchMode() && setting.getBlocks().isEmpty();
    }

    /** 预扣一个目标方块的物品；不支持或材料不足时返回null，来源异常则中止任务。 */
    public Reservation reserve(BlockState expected, CompoundTag templateTag) {
        requireServerThread(player);
        if (!isSupported() || expected == null || expected.isAir() || !supportedState(expected)
                || !supportedTag(expected, templateTag)) return null;

        BlockInfo info = new BlockInfo(expected);
        ItemStack wanted = info.getItemStackForm();
        // 两个相同候选用于显式识别终端的隐含电压替换，不能把替代材料扣成正式蓝图。
        List<ItemStack> candidates = setting.apply(new BlockInfo[]{info, info});
        if (wanted.isEmpty() || !(wanted.getItem() instanceof BlockItem) || candidates.size() != 2
                || candidates.stream().anyMatch(candidate -> !ItemStack.isSameItemSameTags(wanted, candidate))) return null;
        if (player.isCreative()) return new Reservation(player);

        int count = materialCount(expected);
        if (count < 1) return null;
        wanted.setCount(1);
        if (setting.isAeMode()) {
            Reservation reservation = reserveFromAe(wanted, count);
            if (reservation != null) return reservation;
        }
        return reserveFromInventory(wanted, count);
    }

    /** 创造原稿测试允许活塞头、双格门及历史实体数据，不改变生存材料策略。 */
    Reservation reserveCreativeBlueprint() {
        requireServerThread(player);
        return player.isCreative() && isSupported() ? new Reservation(player) : null;
    }

    private Reservation reserveFromInventory(ItemStack wanted, int count) {
        Reservation reservation = new Reservation(player);
        boolean complete = false;
        try {
            while (count > 0) {
                Triplet<ItemStack, IItemHandler, Integer> found = AdvancedBlockPattern.foundItem(
                        player, List.of(wanted), item -> item instanceof BlockItem);
                if (found == null || found.getA() == null || found.getB() == null || found.getC() == null
                        || found.getA().isEmpty() || !ItemStack.isSameItemSameTags(wanted, found.getA())) return null;
                IItemHandler handler = found.getB();
                int slot = found.getC();
                if (slot < 0 || slot >= handler.getSlots()) return null;
                int taking = Math.min(count, found.getA().getCount());
                ItemStack simulated = handler.extractItem(slot, taking, true);
                if (!exact(simulated, wanted, taking)) return null;
                ItemStack extracted = handler.extractItem(slot, taking, false);
                if (extracted == null || !extracted.isEmpty()
                        && (!ItemStack.isSameItemSameTags(extracted, wanted) || extracted.getCount() > taking))
                    throw invalidProvider("背包提取返回了错误物品或数量");
                if (!extracted.isEmpty()) reservation.debits.add(new Debit(extracted.copy(), handler, slot, null, null));
                if (!exact(extracted, wanted, taking)) return null;
                count -= taking;
            }
            complete = true;
            return reservation;
        } finally {
            if (!complete) reservation.close();
        }
    }

    private Reservation reserveFromAe(ItemStack wanted, int count) {
        MEStorage storage = findAeStorage();
        AEItemKey key = AEItemKey.of(wanted);
        if (storage == null || key == null) return null;
        IActionSource source = IActionSource.ofPlayer(player);
        long simulated = checkedAmount(storage.extract(key, count, Actionable.SIMULATE, source), count);
        if (simulated != count) return null;
        long extracted = checkedAmount(storage.extract(key, count, Actionable.MODULATE, source), count);
        Reservation reservation = new Reservation(player);
        if (extracted > 0) reservation.debits.add(new Debit(key.toStack((int) extracted), null, -1, storage, key));
        if (extracted == count) return reservation;
        reservation.close();
        return null;
    }

    private MEStorage findAeStorage() {
        IGrid grid = null;
        GlobalPos bound = setting.getBoundAE();
        if (bound != null && bound.dimension().equals(level.dimension()) && level.hasChunkAt(bound.pos())) {
            var blockEntity = level.getBlockEntity(bound.pos());
            IGridNode node = blockEntity == null ? null : AdvancedBlockPattern.getGridNode(blockEntity);
            // AE2 15的NetworkStorage不做玩家鉴权，坐标绑定不能作为共享网络的提取凭据。
            if (node != null && node.isActive() && player.getUUID().equals(node.getOwningPlayerProfileId())
                    && level.mayInteract(player, bound.pos())) grid = node.getGrid();
        }
        // 共享网络须持有已绑定、有电且通过真实无线距离检查的终端，不能仅凭存储API的ActionSource。
        if (grid == null) grid = WirelessTerminalGridResolver.find(player, level);
        return grid == null ? null : grid.getStorageService().getInventory();
    }

    /** 每份掉落只交付一次；外部提供方抛错后不重试未知份额，未触碰的掉落仍投放给玩家。 */
    void deliver(List<ItemStack> drops) {
        requireServerThread(player);
        int claimed = 0;
        try {
            MEStorage storage = setting.isAeMode() ? findAeStorage() : null;
            for (; claimed < drops.size();) {
                ItemStack remainder = drops.get(claimed++).copy();
                if (remainder.isEmpty()) continue;
                AEItemKey key = AEItemKey.of(remainder);
                if (storage != null && key != null) {
                    long inserted = checkedAmount(storage.insert(key,remainder.getCount(),Actionable.MODULATE,
                            IActionSource.ofPlayer(player)),remainder.getCount());
                    remainder.shrink((int)inserted);
                }
                if (!remainder.isEmpty()) {
                    var visited = java.util.Collections.newSetFromMap(new IdentityHashMap<IItemHandler, Boolean>());
                    var handler = player.getCapability(ForgeCapabilities.ITEM_HANDLER).resolve().orElse(null);
                    remainder = insertNested(handler,remainder,visited,0);
                }
                if (!remainder.isEmpty()) player.getInventory().add(remainder);
                if (!remainder.isEmpty() && player.drop(remainder,false) == null)
                    throw invalidProvider("拆除余量无法投放");
            }
        } catch (RuntimeException failure) {
            LOGGER.error("拆除掉落交付结果未知，当前份额不重试；未处理掉落继续投放",failure);
            for (; claimed < drops.size(); claimed++) {
                try { if (!drops.get(claimed).isEmpty()) player.drop(drops.get(claimed).copy(),false); }
                catch (RuntimeException fallback) { failure.addSuppressed(fallback); }
            }
            throw failure;
        }
    }

    private static ItemStack insertNested(IItemHandler handler, ItemStack stack, Set<IItemHandler> visited, int depth) {
        if (handler == null || depth >= 16 || !visited.add(handler)) return stack;
        for (int slot=0; slot<handler.getSlots() && !stack.isEmpty(); slot++) {
            var nested = handler.getStackInSlot(slot).getCapability(ForgeCapabilities.ITEM_HANDLER).resolve().orElse(null);
            stack = insertNested(nested,stack,visited,depth+1);
        }
        return stack.isEmpty() ? stack : ItemHandlerHelper.insertItemStacked(handler,stack,false);
    }

    private boolean supportedTag(BlockState state, CompoundTag tag) {
        if (tag == null || tag.isEmpty()) return true;
        CompoundTag defaults = defaultTags.computeIfAbsent(state, key -> {
            if (!(key.getBlock() instanceof EntityBlock entityBlock)) return new CompoundTag();
            var entity = entityBlock.newBlockEntity(BlockPos.ZERO, key);
            return entity == null ? new CompoundTag() : entity.saveWithFullMetadata();
        });
        if (defaults.isEmpty() || tag.contains("id") && !Objects.equals(tag.get("id"), defaults.get("id"))) return false;
        for (String key : tag.getAllKeys()) {
            if (POSITION_ONLY_TAGS.contains(key)) continue;
            // 建造器只setBlock，不加载蓝图NBT；仅接受新建空GT机器原生默认值，不能免费重建容器内容。
            if (!(state.getBlock() instanceof MetaMachineBlock) || !Objects.equals(tag.get(key), defaults.get(key))) return false;
        }
        return true;
    }

    private static int materialCount(BlockState state) {
        for (var property : state.getProperties()) {
            Comparable<?> value = state.getValue(property);
            if (value instanceof Integer number && (STACKED_PROPERTIES.contains(property.getName()) && number != 1
                    || RESOURCE_PROPERTIES.contains(property.getName()) && number != 0
                    && !(state.getBlock() instanceof LightBlock && "level".equals(property.getName())))
                    || "eye".equals(property.getName()) && Boolean.TRUE.equals(value)) return -1;
        }
        return state.getBlock() instanceof SlabBlock && state.getValue(SlabBlock.TYPE) == SlabType.DOUBLE ? 2 : 1;
    }

    private static boolean supportedState(BlockState state) {
        return state.getFluidState().isEmpty() && !(state.getBlock() instanceof DoublePlantBlock)
                && !(state.getBlock() instanceof DoorBlock) && !(state.getBlock() instanceof BedBlock);
    }

    private static boolean exact(ItemStack stack, ItemStack wanted, int count) {
        return stack != null && stack.getCount() == count && ItemStack.isSameItemSameTags(stack, wanted);
    }

    private static long checkedAmount(long amount, int requested) {
        if (amount < 0 || amount > requested) throw invalidProvider("AE返回数量超出请求范围");
        return amount;
    }

    private static IllegalStateException invalidProvider(String message) {
        LOGGER.error("HK3GTL材料来源违反事务约定：{}；结果未知时拒绝猜测补发", message);
        return new IllegalStateException(message);
    }

    private static void requireServerThread(ServerPlayer player) {
        if (!player.server.isSameThread()) throw new IllegalStateException("材料事务必须运行在服务器线程");
    }

    private static void refund(ServerPlayer player, Debit debit) {
        ItemStack remainder;
        if (debit.storage != null) {
            int count = debit.stack.getCount();
            long inserted = checkedAmount(debit.storage.insert(debit.key, count, Actionable.MODULATE,
                    IActionSource.ofPlayer(player)), count);
            remainder = debit.stack.copyWithCount(count - (int) inserted);
        } else if (debit.slot < 0 || debit.slot >= debit.handler.getSlots()) {
            remainder = debit.stack.copy();
        } else {
            remainder = debit.handler.insertItem(debit.slot, debit.stack.copy(), false);
            if (remainder == null || !remainder.isEmpty() && (!ItemStack.isSameItemSameTags(remainder, debit.stack)
                    || remainder.getCount() > debit.stack.getCount())) throw invalidProvider("背包退款返回了错误物品或数量");
        }
        if (remainder.isEmpty()) return;
        ItemStack refund = remainder.copy();
        player.getInventory().add(refund);
        if (!refund.isEmpty() && player.drop(refund, false) == null) throw invalidProvider("无法投放退款余量");
    }

    private record Debit(ItemStack stack, IItemHandler handler, int slot, MEStorage storage, AEItemKey key) {}

    /** 放置成功调用commit；未提交的预留在close时退回原来源。 */
    public static final class Reservation implements AutoCloseable {
        private final ServerPlayer player;
        private final List<Debit> debits = new ArrayList<>(2);
        private boolean settled;

        private Reservation(ServerPlayer player) { this.player = player; }

        public void commit() {
            requireServerThread(player);
            if (settled) throw new IllegalStateException("材料事务已结算");
            settled = true;
            debits.clear();
        }

        @Override
        public void close() {
            requireServerThread(player);
            if (settled) return;
            settled = true;
            RuntimeException failure = null;
            for (int i = debits.size() - 1; i >= 0; i--) {
                try {
                    refund(player, debits.get(i));
                } catch (RuntimeException exception) {
                    // 提供方可能已写入后抛错，未知结果不重试、不凭空补发；其余已知预扣仍逐项退还。
                    LOGGER.error("HK3GTL退款结果未知，材料事务中止；不自动重试以免复制物品", exception);
                    if (failure == null) failure = exception;
                    else failure.addSuppressed(exception);
                }
            }
            debits.clear();
            if (failure != null) throw failure;
        }
    }
}
