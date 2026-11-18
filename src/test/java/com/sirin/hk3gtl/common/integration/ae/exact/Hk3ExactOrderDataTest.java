package com.sirin.hk3gtl.common.integration.ae.exact;

import com.sirin.hk3gtl.common.research.Hk3ResearchPaymentJournal;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtIo;
import net.minecraft.nbt.StringTag;
import net.minecraft.nbt.Tag;

import java.math.BigInteger;
import java.nio.file.Files;
import java.util.UUID;

/** 实际压缩NBT往返、损坏拒绝与在途恢复，不启动游戏或写活动存档。 */
public final class Hk3ExactOrderDataTest {
    private static int checks;

    public static void main(String[] args) throws Exception {
        var target = Hk3AeExactPlanAdapterTest.key("persisted_target");
        UUID owner = UUID.randomUUID(), id = UUID.randomUUID();
        var order = new Hk3ExactOrder(id, owner, BigInteger.TEN.pow(80));
        UUID first = order.beginBatch(100);
        order.finish(first, true);
        UUID active = order.beginBatch(Long.MAX_VALUE);
        var data = new Hk3ExactOrderData();
        data.entries.put(id, new Hk3ExactOrderData.Entry(order, target, BigInteger.TEN.pow(90), "测试"));
        CompoundTag original = data.save(new CompoundTag());
        var directory = Files.createTempDirectory("hk3-ae-exact-nbt-");
        try {
            var file = directory.resolve("orders.dat");
            Hk3ResearchPaymentJournal.write(file, original);
            CompoundTag disk = NbtIo.readCompressed(file.toFile());
            check(disk.equals(original), "压缩NBT逐字节数值往返");
            var restored = Hk3ExactOrderData.load(disk, ignored -> target);
            var state = restored.entries.get(id).order.snapshot();
            check(state.total().equals(BigInteger.TEN.pow(80)) && state.completed().intValueExact() == 100, "超long总量和已完成量不截断");
            check(state.activeToken().equals(active) && state.activeAmount().equals(BigInteger.valueOf(Long.MAX_VALUE)), "在途令牌与批次数量保留");
            check(state.state() == Hk3ExactOrder.State.PAUSED && !restored.entries.get(id).order.resume(), "恢复后不得重发未知批次");
            check(restored.entries.get(id).plannedBytes.equals(BigInteger.TEN.pow(90)), "大数字节存档不饱和");
            check(restored.entries.get(id).order.finish(active, true), "恢复后仍可接原CPU真实回执");
            check(!restored.entries.get(id).order.finish(active, true), "已消费回执不会重复计数");
        } finally {
            Files.deleteIfExists(directory.resolve("orders.dat"));
            Files.delete(directory);
        }
        reject(new CompoundTag(), target);
        CompoundTag wrongType = original.copy();
        ListTag strings = new ListTag(); strings.add(StringTag.valueOf("broken")); wrongType.put("Orders", strings);
        reject(wrongType, target);
        for (String key : new String[]{"Total", "Completed", "ActiveAmount", "Bytes", "Owner", "Target", "State"}) {
            CompoundTag broken = original.copy(); row(broken).remove(key); reject(broken, target);
        }
        CompoundTag negative = original.copy(); row(negative).putByteArray("Completed", BigInteger.ONE.negate().toByteArray()); reject(negative, target);
        CompoundTag impossible = original.copy(); row(impossible).putByteArray("Completed", BigInteger.TEN.pow(100).toByteArray()); reject(impossible, target);
        CompoundTag tokenless = original.copy(); row(tokenless).remove("ActiveToken"); reject(tokenless, target);
        CompoundTag badToken = original.copy(); row(badToken).putString("ActiveToken", "broken"); reject(badToken, target);
        CompoundTag duplicate = original.copy(); duplicate.getList("Orders", Tag.TAG_COMPOUND).add(row(duplicate).copy()); reject(duplicate, target);
        CompoundTag badKey = original.copy();
        try { Hk3ExactOrderData.load(badKey, ignored -> null); throw new AssertionError("无效资源必须拒绝"); }
        catch (IllegalArgumentException expected) { checks++; }
        check(Hk3ExactOrderData.load(new Hk3ExactOrderData().save(new CompoundTag()), ignored -> target).entries.isEmpty(), "合法空账本可读");
        System.out.println("大数订单压缩NBT及损坏保护核验通过：" + checks + "项；未读写活动存档。");
    }

    private static CompoundTag row(CompoundTag tag) { return tag.getList("Orders", Tag.TAG_COMPOUND).getCompound(0); }
    private static void reject(CompoundTag tag, appeng.api.stacks.AEKey key) {
        try { Hk3ExactOrderData.load(tag, ignored -> key); throw new AssertionError("损坏账本必须拒绝"); }
        catch (IllegalArgumentException expected) { checks++; }
    }
    private static void check(boolean value, String message) { if (!value) throw new AssertionError(message); checks++; }
}
