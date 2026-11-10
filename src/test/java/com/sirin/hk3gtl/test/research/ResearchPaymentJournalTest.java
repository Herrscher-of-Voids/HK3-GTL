package com.sirin.hk3gtl.test.research;

import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import com.sirin.hk3gtl.common.research.Hk3ResearchPaymentJournal;
import net.minecraft.SharedConstants;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtIo;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.UUID;

/**
 * 【文件职责】验证生产支付日志在各文件落盘边界的重放、幂等和损坏拒绝，不替代Forge真实库存验收。
 * 【变更记录 #1】2026-11-04 01:23:43（第1次备注 · 内测5修订194）
 * - 删除：无；新增：提交前文件保全、日志后恢复、玩家先落盘、账本先落盘、重复恢复和IO失败保留日志测试。
 * - 修改：无；用途：用真实NBT文件验证持久层，附属模组另验真实材料、工具、退款与JVM强停。
 */
/**
 * 【变更记录 #2】2026-11-04 02:53:59（第2次备注 · 内测5修订194）
 * - 删除：recover自动删除日志的断言；新增：重放后日志保留、显式完成后删除的校验。
 * - 修改：独立文件测试显式finish模拟内存恢复成功；用途：覆盖恢复后异常仍有重放决定的边界。
 */
public final class ResearchPaymentJournalTest {
    private static final UUID PAYER = UUID.fromString("11111111-2222-3333-4444-555555555555");
    public static void main(String[] args) throws Exception {
        SharedConstants.tryDetectVersion();
        for (int boundary = 0; boundary < 4; boundary++) recovery(boundary);
        corruption(); ioFailure(); memoryFailure();
        System.out.println("研究支付日志：提交前保全、四边界恢复、单人内嵌库存、重复恢复、损坏与IO拒绝通过");
    }

    private static CompoundTag player(int count) {
        CompoundTag player = new CompoundTag(), item = new CompoundTag();
        player.putUUID("UUID", PAYER);
        item.putByte("Slot", (byte) 0); item.putString("id", "minecraft:paper"); item.putByte("Count", (byte) count);
        CompoundTag exact = new CompoundTag(); exact.putString("支付测试", "原始NBT"); item.put("tag", exact);
        ListTag inventory = new ListTag(); inventory.add(item); player.put("Inventory", inventory);
        return player;
    }

    private static CompoundTag ledger(String marker) {
        CompoundTag value = new Hk3ResearchData().save(new CompoundTag());
        value.putString("TestMarker", marker);
        return value;
    }

    private static void recovery(int boundary) throws Exception {
        Path root = Files.createTempDirectory("hk3-payment-");
        Path playerFile = root.resolve("playerdata").resolve(PAYER + ".dat");
        Path ledgerFile = root.resolve("data").resolve(Hk3ResearchPaymentJournal.LEDGER + ".dat");
        CompoundTag before = player(9), after = player(5), ledger = ledger("已真实付款");
        Hk3ResearchPaymentJournal.write(playerFile, before);
        CompoundTag envelope = new CompoundTag(); envelope.put("data", ledger("未付款"));
        Hk3ResearchPaymentJournal.write(ledgerFile, envelope);
        CompoundTag level = new CompoundTag(), data = new CompoundTag();
        data.put("Player", before.copy()); data.putString("保留世界信息", "不能回退"); level.put("Data", data);
        Hk3ResearchPaymentJournal.write(root.resolve("level.dat"), level);
        check(Hk3ResearchPaymentJournal.recover(root) == null, "无日志不得生成事务");
        Hk3ResearchPaymentJournal.prepare(root, PAYER, ledger, after);
        check(NbtIo.readCompressed(playerFile.toFile()).equals(before), "日志阶段不得提前修改玩家");
        expectFailure(() -> Hk3ResearchPaymentJournal.prepare(root, PAYER, ledger, after));
        if (boundary >= 1) Hk3ResearchPaymentJournal.write(playerFile, after);
        if (boundary >= 2) {
            envelope.put("data", ledger.copy()); Hk3ResearchPaymentJournal.write(ledgerFile, envelope);
        }
        if (boundary >= 3) Hk3ResearchPaymentJournal.write(playerFile, before);
        CompoundTag record = Hk3ResearchPaymentJournal.recover(root);
        check(record != null, "事务必须重放");
        check(Files.exists(Hk3ResearchPaymentJournal.journal(root)), "内存恢复前不得移除决定");
        check(NbtIo.readCompressed(playerFile.toFile()).equals(after), "库存必须为准确后像");
        check(NbtIo.readCompressed(ledgerFile.toFile()).getCompound("data").equals(ledger), "账本必须为准确后像");
        CompoundTag restoredLevel = NbtIo.readCompressed(root.resolve("level.dat").toFile()).getCompound("Data");
        check(restoredLevel.getCompound("Player").equals(after), "单人服主内嵌库存必须同步");
        check(restoredLevel.getString("保留世界信息").equals("不能回退"), "不得覆盖无关世界数据");
        Hk3ResearchPaymentJournal.finish(root);
        check(Hk3ResearchPaymentJournal.recover(root) == null, "已完成事务不得重复执行");
        // 模拟删除日志前强停后的再次重放，结果只能仍为同一后像。
        Hk3ResearchPaymentJournal.write(Hk3ResearchPaymentJournal.journal(root), record);
        Hk3ResearchPaymentJournal.recover(root);
        check(NbtIo.readCompressed(playerFile.toFile()).equals(after), "重复重放不能重复扣料或发放");
        Hk3ResearchPaymentJournal.finish(root);
    }

    private static void corruption() throws Exception {
        Path root = Files.createTempDirectory("hk3-payment-corrupt-");
        Files.createDirectories(root.resolve("data"));
        Files.writeString(Hk3ResearchPaymentJournal.journal(root), "损坏日志");
        expectFailure(() -> Hk3ResearchPaymentJournal.recover(root));
        check(Files.exists(Hk3ResearchPaymentJournal.journal(root)), "损坏日志必须保留");
        check(!Files.exists(root.resolve("playerdata")), "损坏日志不得写玩家");
        CompoundTag wrong = player(1); wrong.putUUID("UUID", UUID.randomUUID());
        Path other = Files.createTempDirectory("hk3-payment-identity-");
        expectFailure(() -> Hk3ResearchPaymentJournal.prepare(other, PAYER, ledger("x"), wrong));
        check(!Files.exists(Hk3ResearchPaymentJournal.journal(other)), "身份错误不得生成决定");
    }

    private static void ioFailure() throws Exception {
        Path root = Files.createTempDirectory("hk3-payment-io-");
        Hk3ResearchPaymentJournal.prepare(root, PAYER, ledger("x"), player(1));
        Files.writeString(root.resolve("playerdata"), "阻断目录创建");
        expectFailure(() -> Hk3ResearchPaymentJournal.recover(root));
        check(Files.exists(Hk3ResearchPaymentJournal.journal(root)), "写失败必须留日志");
        Files.delete(root.resolve("playerdata"));
        check(Hk3ResearchPaymentJournal.recover(root) != null, "IO恢复后必须能够完成同一事务");
        Hk3ResearchPaymentJournal.finish(root);
    }

    private static void memoryFailure() throws Exception {
        Path root = Files.createTempDirectory("hk3-payment-memory-");
        Hk3ResearchPaymentJournal.prepare(root, PAYER, ledger("已付款"), player(1));
        try {
            Hk3ResearchPaymentJournal.recover(root);
            throw new IllegalStateException("模拟玩家缓存或界面同步失败");
        } catch (IllegalStateException expected) {
            check(Files.exists(Hk3ResearchPaymentJournal.journal(root)), "内存恢复失败必须保留决定");
        }
        // 模拟异常后的正常停服用旧缓存重写文件，下一次重放仍必须恢复后像。
        Hk3ResearchPaymentJournal.write(root.resolve("playerdata").resolve(PAYER + ".dat"), player(9));
        check(Hk3ResearchPaymentJournal.recover(root) != null, "停服旧缓存覆写后必须重放");
        check(NbtIo.readCompressed(root.resolve("playerdata").resolve(PAYER + ".dat").toFile()).equals(player(1)),
                "内存同步失败不能导致原材料复活");
        Hk3ResearchPaymentJournal.finish(root);
    }

    private static void check(boolean condition, String message) { if (!condition) throw new AssertionError(message); }
    private interface IoAction { void run() throws IOException; }
    private static void expectFailure(IoAction operation) throws IOException {
        try { operation.run(); } catch (IOException expected) { return; }
        throw new AssertionError("本应拒绝的事务却被接受");
    }
}
