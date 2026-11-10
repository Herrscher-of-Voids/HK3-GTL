package com.sirin.hk3gtl.common.research;

import net.minecraft.SharedConstants;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.storage.LevelResource;
import net.minecraftforge.event.server.ServerStartingEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.function.BooleanSupplier;

/**
 * 【文件职责】将研究开题、实验托管与退款领取的真实内存变更提交为可重放的跨文件事务。
 * 【变更记录 #1】2026-11-04 01:23:43（第1次备注 · 内测5修订194）
 * - 删除：无。
 * - 新增：服务端主线程、全局重入守卫、提交前回滚和启动前恢复；持久日志失败时阻断并停止服务器。
 * - 修改：付款与退款入口在成功后立即持久化；恢复同时更新既有账本对象和在线玩家库存，防旧缓存覆盖。
 * - 用途：服务入口→本事务→Hk3ResearchPaymentJournal；不更改研究费用、证据或完成条件。
 */
@Mod.EventBusSubscriber(modid = "hk3gtl")
/**
 * 【变更记录 #2】2026-11-04 02:53:59（第2次备注 · 内测5修订194）
 * - 删除：全JVM共享布尔守卫和内存恢复前删除日志的顺序；新增：按服务器线程隔离的事务守卫及完成点。
 * - 修改：文件、同对象账本及玩家缓存均恢复后才移除日志，异常停服仍保留决定；finally移除线程状态。
 * - 用途：避免多服务器互相跳过恢复及同步异常后的旧缓存覆写；不改变费用和扣料规则。
 */
public final class Hk3ResearchPayment {
    private Hk3ResearchPayment() {}
    private static final ThreadLocal<Boolean> ACTIVE = ThreadLocal.withInitial(() -> false);

    @SubscribeEvent(priority = EventPriority.HIGHEST)
    public static void starting(ServerStartingEvent event) { Hk3ResearchData.get(event.getServer()); }

    static CompoundTag recover(MinecraftServer server) {
        if (!server.isSameThread()) throw new IllegalStateException("研究支付必须运行在服务器主线程");
        if (ACTIVE.get()) return null;
        try { return Hk3ResearchPaymentJournal.recover(server.getWorldPath(LevelResource.ROOT)); }
        catch (IOException | RuntimeException failure) {
            server.halt(false);
            throw new IllegalStateException("研究支付日志恢复失败，已阻断服务器运行并保留原日志", failure);
        }
    }

    static void recovered(MinecraftServer server, Hk3ResearchData data, CompoundTag record) {
        ACTIVE.set(true);
        try {
            data.restore(record.getCompound("Ledger"));
            restorePlayer(server, record);
            Hk3ResearchPaymentJournal.finish(server.getWorldPath(LevelResource.ROOT));
        } catch (IOException | RuntimeException failure) {
            server.halt(false);
            throw new IllegalStateException("研究支付缓存恢复失败，保留日志等待重启", failure);
        } finally { ACTIVE.remove(); }
    }

    static void restorePlayer(MinecraftServer server, CompoundTag record) {
        CompoundTag embedded = server.getWorldData().getLoadedPlayerTag();
        if (embedded != null && embedded.hasUUID("UUID") && record.getUUID("Payer").equals(embedded.getUUID("UUID"))) {
            for (String key : java.util.Set.copyOf(embedded.getAllKeys())) embedded.remove(key);
            CompoundTag snapshot = record.getCompound("Player");
            for (String key : snapshot.getAllKeys()) embedded.put(key, snapshot.get(key).copy());
        }
        ServerPlayer player = server.getPlayerList().getPlayer(record.getUUID("Payer"));
        if (player != null) {
            player.getInventory().load(record.getCompound("Player").getList("Inventory", Tag.TAG_COMPOUND));
            player.inventoryMenu.broadcastChanges();
        }
    }

    /** 回调只允许修改本账本和此玩家库存；真实扣料仍由原分配器完成，返回失败时恢复双方前像。 */
    public static boolean commit(ServerPlayer player, Hk3ResearchData data, BooleanSupplier operation) {
        MinecraftServer server = player.server;
        if (!server.isSameThread() || ACTIVE.get()) throw new IllegalStateException("研究支付线程错误或事务重入");
        if (Hk3ResearchData.get(server) != data) throw new IllegalArgumentException("研究支付账本不属于当前服务器");
        Path root = server.getWorldPath(LevelResource.ROOT);
        CompoundTag beforeLedger = data.save(new CompoundTag());
        CompoundTag beforePlayer = player.saveWithoutId(new CompoundTag());
        ACTIVE.set(true);
        boolean decided = false;
        try {
            if (!operation.getAsBoolean()) {
                rollback(player, data, beforeLedger, beforePlayer);
                return false;
            }
            CompoundTag afterPlayer = player.saveWithoutId(new CompoundTag());
            afterPlayer.putInt("DataVersion", SharedConstants.getCurrentVersion().getDataVersion().getVersion());
            Hk3ResearchPaymentJournal.prepare(root, player.getUUID(), data.save(new CompoundTag()), afterPlayer);
            decided = true;
            restorePlayer(server, Hk3ResearchPaymentJournal.recover(root));
            Hk3ResearchPaymentJournal.finish(root);
            player.inventoryMenu.broadcastChanges();
            return true;
        } catch (IOException | RuntimeException failure) {
            // 原子移动成功后也可能由文件系统报告失败；以日志实际存在作为不可回滚的依据。
            if (!decided && Files.notExists(Hk3ResearchPaymentJournal.journal(root))) {
                rollback(player, data, beforeLedger, beforePlayer);
            } else {
                server.halt(false);
            }
            throw new IllegalStateException("研究支付提交失败；已提交日志保留供重启恢复", failure);
        } finally { ACTIVE.remove(); }
    }

    private static void rollback(ServerPlayer player, Hk3ResearchData data, CompoundTag ledger, CompoundTag snapshot) {
        data.restore(ledger);
        player.getInventory().load(snapshot.getList("Inventory", Tag.TAG_COMPOUND));
        player.inventoryMenu.broadcastChanges();
    }

    public static int claimRefunds(ServerPlayer player) {
        Hk3ResearchData data = Hk3ResearchData.get(player);
        int[] moved = {0};
        commit(player, data, () -> (moved[0] = data.claimRefunds(player.getUUID(), player.getInventory())) > 0);
        return moved[0];
    }
}
