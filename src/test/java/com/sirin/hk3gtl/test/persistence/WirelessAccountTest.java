package com.sirin.hk3gtl.test.persistence;

import com.sirin.hk3gtl.common.capability.HonkaiWirelessNetwork;
import com.sirin.hk3gtl.common.capability.HonkaiWirelessSavedData;
import com.sirin.hk3gtl.common.util.Hk3SavedDataGuard;
import net.minecraft.nbt.*;
import net.minecraft.server.MinecraftServer;
import net.minecraftforge.event.server.ServerStoppingEvent;

import java.io.*;
import java.math.BigInteger;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Consumer;

/**
 * 【变更记录 #1】2026-10-01 17:17:43（修订137）
 * 删除：无；新增：真实账户并发扣款、模拟、压缩保存、损坏拒绝、保存失败重试及会话代理回归。
 * 修改：可选只读指定实例旧HW文件，测试不写回玩家档案；用途：验证完整账户流程，不替代游戏机器实测。
 */
public final class WirelessAccountTest {
    private static int checks;
    private static final UUID A = new UUID(0, 1), B = new UUID(0, 2);
    private static final BigInteger HUGE = BigInteger.TEN.pow(70).add(BigInteger.valueOf(321));
    private static void check(boolean ok, String reason) { checks++; if (!ok) throw new AssertionError(reason); }
    private static void reject(Runnable action) {
        try { action.run(); throw new AssertionError("非法账户被接受"); }
        catch (IllegalArgumentException | IllegalStateException expected) { checks++; }
    }
    private static CompoundTag disk(CompoundTag value) throws IOException {
        var out = new ByteArrayOutputStream(); NbtIo.writeCompressed(value, out);
        return NbtIo.readCompressed(new ByteArrayInputStream(out.toByteArray()));
    }
    private static void corrupt(CompoundTag source, Consumer<CompoundTag> mutation) {
        var broken = source.copy(); mutation.accept(broken); var before = broken.copy();
        reject(() -> HonkaiWirelessSavedData.load(broken));
        check(broken.equals(before), "失败读取保持输入原件");
    }
    public static void main(String[] args) throws Exception {
        net.minecraft.SharedConstants.tryDetectVersion();
        transactions(); validation(); concurrency(); persistence(); sessions();
        if (args.length > 0) auditExisting(Path.of(args[0]));
        System.out.println("Wireless accounts: " + checks + " checks passed; live machine acceptance pending");
    }
    private static void transactions() throws Exception {
        var d = new HonkaiWirelessSavedData();
        check(d.getAmount(A).signum() == 0 && !d.isDirty(), "新账户为空且未修改");
        check(d.insert(A, HUGE, true).equals(HUGE) && !d.isDirty(), "模拟充值不落账");
        check(d.getAmount(A).signum() == 0, "模拟无余额副作用");
        check(d.insert(A, HUGE, false).equals(HUGE) && d.isDirty(), "超long充值完整到账");
        d.setAmount(B, BigInteger.valueOf(123)); d.setDirty(false);
        check(!d.tryExtractExact(A, HUGE.add(BigInteger.ONE)) && !d.isDirty(), "不足全额零扣除");
        check(d.extract(A, HUGE, true).equals(HUGE) && !d.isDirty(), "模拟抽取不标脏");
        check(d.tryExtractExact(A, BigInteger.valueOf(300)), "实际全额扣款成功");
        check(d.getAmount(A).equals(HUGE.subtract(BigInteger.valueOf(300))), "真实余额准确");
        check(d.getAmount(B).equals(BigInteger.valueOf(123)), "不同玩家账户隔离");
        var restored = HonkaiWirelessSavedData.load(disk(d.save(new CompoundTag())));
        check(restored.getAmount(A).equals(d.getAmount(A)) && restored.getAmount(B).equals(d.getAmount(B)), "超long重启精确恢复");
        check(restored.extract(A, HUGE, false).equals(d.getAmount(A)) && !restored.hasPool(A), "部分抽取以实际余额为限并清零");
        check(restored.tryExtractExact(B, BigInteger.valueOf(123)) && !restored.hasPool(B), "恰好耗尽移除空账户");
        d.setDirty(false);
        check(d.insert(A, BigInteger.valueOf(-1), false).signum() == 0, "负充值不生效");
        check(d.extract(A, null, false).signum() == 0, "空请求不扣能");
        check(d.insert(null, HUGE, false).signum() == 0 && !d.tryExtractExact(null, HUGE), "未绑定不充值或消费");
        check(d.tryExtractExact(A, BigInteger.ZERO) && !d.isDirty(), "零费用不写盘");
        var exposed = d.save(new CompoundTag()); exposed.getList("pools", 10).clear();
        check(d.getAmount(A).signum() > 0, "序列化快照不暴露内部余额");
    }
    private static void validation() {
        var d = new HonkaiWirelessSavedData(); d.setAmount(A, HUGE);
        var n = d.save(new CompoundTag());
        corrupt(n, v -> v.remove("pools"));
        corrupt(n, v -> v.putString("pools", "错误类型"));
        corrupt(n, v -> { var l = new ListTag(); l.add(StringTag.valueOf("非账户")); v.put("pools", l); });
        corrupt(n, v -> v.getList("pools", 10).getCompound(0).remove("id"));
        corrupt(n, v -> v.getList("pools", 10).getCompound(0).putIntArray("id", new int[]{1, 2}));
        corrupt(n, v -> v.getList("pools", 10).getCompound(0).remove("amt"));
        corrupt(n, v -> v.getList("pools", 10).getCompound(0).putLong("amt", 10));
        for (String value : List.of("", "-1", "NaN", "1.5", " 12", "1e9"))
            corrupt(n, v -> v.getList("pools", 10).getCompound(0).putString("amt", value));
        corrupt(n, v -> v.getList("pools", 10).add(v.getList("pools", 10).getCompound(0).copy()));
        var zero = n.copy(); zero.getList("pools", 10).getCompound(0).putString("amt", "0");
        check(!HonkaiWirelessSavedData.load(zero).hasPool(A), "合法零值可读取");
        check(HonkaiWirelessSavedData.load(new HonkaiWirelessSavedData().save(new CompoundTag())).getAmount(A).signum() == 0, "合法空账本可重启");
        check(HonkaiWirelessSavedData.load(n).getAmount(A).equals(HUGE), "失败夹具未污染合法账本");
    }
    private static void concurrency() throws Exception {
        var d = new HonkaiWirelessSavedData(); var executor = Executors.newFixedThreadPool(8);
        try {
            var jobs = new ArrayList<Callable<Void>>();
            for (int worker = 0; worker < 8; worker++) jobs.add(() -> {
                for (int i = 0; i < 1000; i++) {
                    d.insert(A, BigInteger.valueOf(37), false);
                    if (!d.tryExtractExact(A, BigInteger.valueOf(17))) throw new AssertionError("并发扣款错误拒绝");
                    d.insert(B, BigInteger.ONE, false);
                    if (i % 100 == 0) HonkaiWirelessSavedData.load(d.save(new CompoundTag()));
                }
                return null;
            });
            for (var task : executor.invokeAll(jobs)) task.get(30, TimeUnit.SECONDS);
            check(d.getAmount(A).equals(BigInteger.valueOf(160000)), "8000次充值扣款无丢失");
            check(d.getAmount(B).equals(BigInteger.valueOf(8000)), "并发独立账户守恒");
            d.setAmount(A, BigInteger.valueOf(10000)); var paid = new AtomicInteger(); jobs.clear();
            for (int worker = 0; worker < 8; worker++) jobs.add(() -> {
                for (int i = 0; i < 2000; i++) if (d.tryExtractExact(A, BigInteger.valueOf(7))) paid.incrementAndGet();
                return null;
            });
            for (var task : executor.invokeAll(jobs)) task.get(30, TimeUnit.SECONDS);
            check(paid.get() == 1428 && d.getAmount(A).intValueExact() == 4, "竞争尾款不透支不重复结算");
            check(d.getAmount(B).intValueExact() == 8000, "竞争扣款不挪用其他玩家");
        } finally { executor.shutdownNow(); }
    }
    private static void persistence() throws Exception {
        Path directory = Files.createTempDirectory("hk3-wireless-r137-");
        Path file = directory.resolve(HonkaiWirelessSavedData.DATA_NAME + ".dat");
        try {
            var d = new HonkaiWirelessSavedData(); d.setAmount(A, HUGE); d.save(file.toFile());
            check(Files.exists(file) && !d.isDirty(), "完整文件保存后清待保存标记");
            var loaded = HonkaiWirelessSavedData.load(NbtIo.readCompressed(file.toFile()).getCompound("data"));
            check(loaded.getAmount(A).equals(HUGE), "实际磁盘压缩文件重载");
            byte[] original = Files.readAllBytes(file);
            // 超出NBT字符串编码上限，验证不会被原版StringTag静默写成空值。
            d.setAmount(A, BigInteger.TEN.pow(70000)); d.save(file.toFile());
            check(d.isDirty(), "写入失败保留待保存状态");
            check(Arrays.equals(original, Files.readAllBytes(file)), "序列化失败原余额文件字节不变");
            d.setAmount(A, BigInteger.valueOf(555)); d.save(file.toFile());
            check(!d.isDirty() && HonkaiWirelessSavedData.load(NbtIo.readCompressed(file.toFile()).getCompound("data")).getAmount(A).intValueExact() == 555, "故障解除后再次保存成功");
            d.setAmount(A, BigInteger.valueOf(666));
            d.save(directory.resolve("missing-parent").resolve("ledger.dat").toFile());
            check(d.isDirty(), "真实文件创建失败仍待保存");
            check(HonkaiWirelessSavedData.load(NbtIo.readCompressed(file.toFile()).getCompound("data")).getAmount(A).intValueExact() == 555, "文件创建失败不碰既有存盘");
            d.save(file.toFile());
            check(!d.isDirty() && HonkaiWirelessSavedData.load(NbtIo.readCompressed(file.toFile()).getCompound("data")).getAmount(A).intValueExact() == 666, "IO故障后重试保存新余额");
            var executor = Executors.newFixedThreadPool(2);
            try {
                var start = new CountDownLatch(1);
                var writer = executor.submit(() -> {
                    start.await();
                    for (int i = 0; i < 3000; i++) d.insert(B, BigInteger.ONE, false);
                    return null;
                });
                var saver = executor.submit(() -> {
                    start.await();
                    for (int i = 0; i < 30; i++) d.save(file.toFile());
                    return null;
                });
                start.countDown(); writer.get(30, TimeUnit.SECONDS); saver.get(30, TimeUnit.SECONDS);
                d.save(file.toFile());
                var concurrent = HonkaiWirelessSavedData.load(NbtIo.readCompressed(file.toFile()).getCompound("data"));
                check(concurrent.getAmount(B).intValueExact() == 3000 && !d.isDirty(), "并发写盘不丢最后更新及待保存标记");
                check(concurrent.getAmount(A).intValueExact() == 666, "并发保存不影响其他账户");
            } finally { executor.shutdownNow(); }
            try (var paths = Files.list(directory)) { check(paths.count() == 1, "保存及失败清理临时文件"); }
            reject(() -> Hk3SavedDataGuard.freshIfMissing(file, HonkaiWirelessSavedData::new));
            check(Hk3SavedDataGuard.freshIfMissing(directory.resolve("absent.dat"), HonkaiWirelessSavedData::new) != null, "确实不存在才可新建");
            Files.write(file, new byte[]{0, 1, 2});
            reject(() -> Hk3SavedDataGuard.freshIfMissing(file, HonkaiWirelessSavedData::new));
            check(Arrays.equals(Files.readAllBytes(file), new byte[]{0, 1, 2}), "坏文件防覆盖不改原件");
        } finally {
            try (var paths = Files.walk(directory)) {
                paths.sorted(Comparator.reverseOrder()).forEach(path -> { try { Files.deleteIfExists(path); } catch (IOException ignored) {} });
            }
        }
    }
    private static void sessions() throws Exception {
        // 反射绑定仅为隔离测试夹具，不启动游戏，不替代真实生命周期验收。
        var field = HonkaiWirelessNetwork.class.getDeclaredField("active"); field.setAccessible(true);
        var binding = Class.forName(HonkaiWirelessNetwork.class.getName() + "$Binding")
                .getDeclaredConstructor(MinecraftServer.class, HonkaiWirelessSavedData.class);
        binding.setAccessible(true); Object previous = field.get(null);
        try {
            field.set(null, null);
            check(HonkaiWirelessNetwork.insert(A, 10L, true) == 0, "未就绪模拟不承诺接收");
            reject(() -> HonkaiWirelessNetwork.insert(A, 10L, false));
            reject(() -> HonkaiWirelessNetwork.putStoredAmount(A, HUGE));
            check(!HonkaiWirelessNetwork.tryExtractExact(A, HUGE), "未就绪不能免费消费");
            var first = new HonkaiWirelessSavedData(); field.set(null, binding.newInstance(null, first));
            check(HonkaiWirelessNetwork.insert(A, HUGE, false).equals(HUGE), "代理充值使用同一权威账本");
            check(first.getAmount(A).equals(HUGE) && first.isDirty(), "真实充值直接标脏");
            check(HonkaiWirelessNetwork.extract(A, 10L, false) == 10L, "long适配正常扣款");
            HonkaiWirelessNetwork.putStoredAmountInternal(B, BigInteger.valueOf(9));
            check(first.getAmount(B).intValueExact() == 9, "旧写入入口也持久化");
            HonkaiWirelessNetwork.onServerStopping(new ServerStoppingEvent(null));
            check(HonkaiWirelessNetwork.getStoredAmount(A).signum() == 0, "停止后解除会话");
            reject(() -> HonkaiWirelessNetwork.insert(A, BigInteger.ONE, false));
            var second = new HonkaiWirelessSavedData(); field.set(null, binding.newInstance(null, second));
            check(HonkaiWirelessNetwork.getStoredAmount(A).signum() == 0, "下一存档不继承上一余额");
            HonkaiWirelessNetwork.insert(A, BigInteger.ONE, false);
            check(first.getAmount(A).equals(HUGE.subtract(BigInteger.TEN)), "下一存档操作不改前一存档");
            var restored = HonkaiWirelessSavedData.load(disk(first.save(new CompoundTag())));
            field.set(null, binding.newInstance(null, restored));
            check(HonkaiWirelessNetwork.getStoredAmount(A).equals(HUGE.subtract(BigInteger.TEN)), "返回原存档精确恢复");
        } finally { field.set(null, previous); }
    }
    private static void auditExisting(Path root) throws IOException {
        int count = 0;
        try (var paths = Files.walk(root)) {
            for (Path file : paths.filter(p -> p.getFileName().toString().equals(HonkaiWirelessSavedData.DATA_NAME + ".dat")).toList()) {
                byte[] before = Files.readAllBytes(file);
                var loaded = HonkaiWirelessSavedData.load(NbtIo.readCompressed(new ByteArrayInputStream(before)).getCompound("data"));
                check(HonkaiWirelessSavedData.load(disk(loaded.save(new CompoundTag()))) != null, "旧账户可只读重载");
                check(Arrays.equals(before, Files.readAllBytes(file)), "旧账户文件未写回"); count++;
            }
        }
        System.out.println("Existing wireless audit: " + count + " read-only files accepted");
    }
}
