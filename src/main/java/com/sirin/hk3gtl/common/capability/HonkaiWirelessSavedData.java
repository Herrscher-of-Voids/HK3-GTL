package com.sirin.hk3gtl.common.capability;

/**
 * 【文件职责】
 * - 持久化每个玩家的任意精度无线崩坏能余额。
 * - 关键调用链：HonkaiWirelessNetwork 写入 -> SavedData dirty -> 世界保存/启动镜像。
 *
 * 【变更记录】2026-05-19
 * - 删除：
 *   1) 初始归档备注：自 v0.3 基线梳理，无本次 diff。
 * - 新增：
 *   1) 新增统一变更备注块，便于后续维护与审计追踪。
 * - 修改：
 *   1) 未改动业务逻辑，仅补充文件级职责与维护注释模板。
 * - 用途：
 *   1) 帮助维护者快速理解文件职责、变更背景与风险点。
 *
 * 【变更记录 #2】2026-07-19 19:16:14（第 2 次备注 · 内测四第 31 次更新）
 * - 删除：
 *   1) 删除 Map<UUID, Long> 与 NBT Long 的 64 位存储上限。
 * - 新增：
 *   1) 新增十进制字符串 BigInteger 序列化；损坏、空值或负数记录加载时安全跳过。
 * - 修改：
 *   1) getAmount/setAmount/mirrorToMemory 全部升级为 BigInteger，零值继续删除记录以控制 NBT 体积。
 * - 用途：
 *   1) 确保超 Long.MAX_VALUE 的崩坏能余额跨服务器重启后精确恢复，不发生截断或回绕。
 */

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.nbt.NbtIo;
import net.minecraft.nbt.NbtUtils;
import com.sirin.hk3gtl.common.util.Hk3LedgerValidation;
import com.sirin.hk3gtl.common.util.Hk3SavedDataGuard;
import com.mojang.logging.LogUtils;
import org.slf4j.Logger;

import javax.annotation.Nullable;
import java.math.BigInteger;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.HashSet;
import java.io.File;
import java.io.IOException;
import java.nio.channels.FileChannel;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.nio.file.StandardOpenOption;

/**
 * 【变更记录 #3】2026-10-01 17:17:43（修订137）
 * 删除：静默跳过坏记录、重复余额及启动时向第二份静态余额复制的分支。
 * 新增：严格整账读取、防覆盖加载、原子充值/扣款和同步临时文件落盘。
 * 修改：本账本成为唯一余额来源；保存成功才清待保存标记，失败保留原文件并等待重试。
 * 用途：保护个人HW充值、机器耗能及重启恢复；保留UUID隔离、任意精度和既有费用。
 */
/**
 * 【变更记录 #4】2026-10-01 17:45:00（修订139）
 * 删除：无；新增：本账本一次工作HW预留，精确退款仍写回相同实例和UUID。
 * 修改：实际预留与反向记录共用方法供生产与隔离回归调用。
 * 用途：验证失败全退、成功只扣一次及并发账户守恒，不创建第二份静态余额。
 */
public final class HonkaiWirelessSavedData extends SavedData {

    private static final Logger LOGGER = LogUtils.getLogger();
    public static final String DATA_NAME = "hk3gtl_wireless_pool";
    private static final String POOLS_KEY = "pools";
    private static final String ID_KEY = "id";
    private static final String AMOUNT_KEY = "amt";

    private final Map<UUID, BigInteger> pools = new ConcurrentHashMap<>();

    public HonkaiWirelessSavedData() {}

    public static HonkaiWirelessSavedData load(CompoundTag tag) {
        HonkaiWirelessSavedData data = new HonkaiWirelessSavedData();
        ListTag list = Hk3LedgerValidation.list(tag, POOLS_KEY, Tag.TAG_COMPOUND);
        var seen = new HashSet<UUID>();
        for (int index = 0; index < list.size(); index++) {
            CompoundTag entry = list.getCompound(index);
            Hk3LedgerValidation.require(entry.hasUUID(ID_KEY), ID_KEY);
            Hk3LedgerValidation.type(entry, AMOUNT_KEY, Tag.TAG_STRING);
            UUID id = entry.getUUID(ID_KEY);
            Hk3LedgerValidation.require(seen.add(id), "重复HW账户");
            String raw = entry.getString(AMOUNT_KEY);
            Hk3LedgerValidation.require(raw.matches("[0-9]+"), "HW余额");
            BigInteger amount = new BigInteger(raw);
            if (amount.signum() > 0) data.pools.put(id, amount);
        }
        return data;
    }

    @Override
    public synchronized CompoundTag save(CompoundTag tag) {
        ListTag list = new ListTag();
        for (Map.Entry<UUID, BigInteger> entryValue : pools.entrySet()) {
            BigInteger amount = entryValue.getValue();
            if (amount == null || amount.signum() <= 0) continue;
            CompoundTag entry = new CompoundTag();
            entry.putUUID(ID_KEY, entryValue.getKey());
            entry.putString(AMOUNT_KEY, amount.toString());
            list.add(entry);
        }
        tag.put(POOLS_KEY, list);
        return tag;
    }

    public static HonkaiWirelessSavedData get(MinecraftServer server) {
        if (server == null) return null;
        return Hk3SavedDataGuard.get(server, DATA_NAME, HonkaiWirelessSavedData::load, HonkaiWirelessSavedData::new);
    }

    public synchronized BigInteger getAmount(UUID playerId) {
        return playerId == null ? BigInteger.ZERO : pools.getOrDefault(playerId, BigInteger.ZERO);
    }

    public synchronized boolean reserve(UUID playerId, BigInteger amount, Hk3EnergyTick tick) {
        tick.requireOpen();
        if (amount == null || amount.signum() < 0) throw new IllegalArgumentException("无效HW费用");
        if (amount.signum() == 0) return true;
        if (playerId == null || !tryExtractExact(playerId, amount)) return false;
        tick.undoWith(() -> insert(playerId, amount, false));
        return true;
    }

    public synchronized void setAmount(UUID playerId, BigInteger amount) {
        if (playerId == null) return;
        BigInteger normalized = normalize(amount);
        if (normalized.signum() == 0) {
            if (pools.remove(playerId) != null) setDirty();
            return;
        }
        BigInteger previous = pools.put(playerId, normalized);
        if (!normalized.equals(previous)) setDirty();
    }

    public synchronized BigInteger insert(UUID playerId, BigInteger amount, boolean simulate) {
        BigInteger requested = normalize(amount);
        if (playerId == null || requested.signum() == 0) return BigInteger.ZERO;
        if (!simulate) setAmount(playerId, getAmount(playerId).add(requested));
        return requested;
    }

    public synchronized BigInteger extract(UUID playerId, BigInteger amount, boolean simulate) {
        BigInteger drawn = getAmount(playerId).min(normalize(amount));
        if (!simulate && drawn.signum() > 0) setAmount(playerId, getAmount(playerId).subtract(drawn));
        return drawn;
    }

    /** 同一把锁完成检查和扣款，余额不足不会部分付款。 */
    public synchronized boolean tryExtractExact(UUID playerId, BigInteger amount) {
        BigInteger requested = normalize(amount);
        if (requested.signum() == 0) return true;
        if (playerId == null || getAmount(playerId).compareTo(requested) < 0) return false;
        setAmount(playerId, getAmount(playerId).subtract(requested));
        return true;
    }

    public synchronized boolean hasPool(@Nullable UUID playerId) {
        return playerId != null && pools.containsKey(playerId);
    }

    private static BigInteger normalize(BigInteger amount) {
        return amount == null || amount.signum() <= 0 ? BigInteger.ZERO : amount;
    }

    @Override
    public synchronized boolean isDirty() { return super.isDirty(); }

    @Override
    public synchronized void setDirty(boolean dirty) { super.setDirty(dirty); }

    /** 写完整压缩NBT后原子替换；序列化至清标记全程持锁，不丢并发更新。 */
    @Override
    public synchronized void save(File file) {
        if (!isDirty()) return;
        Path temporary = null;
        try {
            // 原版StringTag遇超长字符串会写空值而非向外抛错，必须在替换原件前拒绝。
            for (BigInteger amount : pools.values()) {
                if (amount.toString().length() > 65535)
                    throw new IOException("HW余额超出NBT字符串编码长度，拒绝保存空余额");
            }
            CompoundTag root = new CompoundTag();
            root.put("data", save(new CompoundTag()));
            NbtUtils.addCurrentDataVersion(root);
            Path target = file.toPath().toAbsolutePath();
            temporary = Files.createTempFile(target.getParent(), DATA_NAME + "-", ".tmp");
            try (var stream = Files.newOutputStream(temporary)) { NbtIo.writeCompressed(root, stream); }
            try (var channel = FileChannel.open(temporary, StandardOpenOption.WRITE)) { channel.force(true); }
            Files.move(temporary, target, StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING);
            setDirty(false);
        } catch (IOException failure) {
            LOGGER.error("[HK3GTL] 无线HW账本保存失败，保留原文件及待保存状态：{}", file, failure);
        } finally {
            if (temporary != null) {
                try { Files.deleteIfExists(temporary); }
                catch (IOException failure) { LOGGER.warn("[HK3GTL] 无线HW临时文件清理失败：{}", temporary, failure); }
            }
        }
    }
}
