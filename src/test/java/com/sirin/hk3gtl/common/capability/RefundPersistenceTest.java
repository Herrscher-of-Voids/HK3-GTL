package com.sirin.hk3gtl.common.capability;

import com.sirin.hk3gtl.common.recipe.power.Hk3PortPayment;
import net.minecraft.nbt.*;
import org.objectweb.asm.ClassReader;
import org.objectweb.asm.tree.*;

import java.io.*;
import java.math.BigInteger;
import java.util.*;
import java.util.concurrent.atomic.*;

/** 真实退款栈、原账本与NBT往返的离线回归；不冒充实际区块卸载或客户端验收。 */
public final class RefundPersistenceTest {
    private static int checks;
    private static final UUID OWNER = new UUID(0, 1), OTHER = new UUID(0, 2);
    private static final BigInteger TOTAL = BigInteger.TEN.pow(40);
    private static void check(boolean value, String reason) { checks++; if (!value) throw new AssertionError(reason); }
    private static void reject(Runnable work) {
        try { work.run(); throw new AssertionError("损坏退款被接受"); }
        catch (IllegalStateException | IllegalArgumentException expected) { checks++; }
    }
    private static CompoundTag address(long position) {
        var tag = new CompoundTag(); tag.putString("Dimension", "minecraft:overworld");
        tag.putLong("Position", position); tag.putString("Definition", "gtceu:test_machine");
        tag.putUUID("Instance", new UUID(0, position + 10)); return tag;
    }
    private static String key(CompoundTag address) { return address.getString("Dimension") + "/" + address.getLong("Position"); }
    private static CompoundTag trait(long pos) {
        var tag = address(pos); tag.putInt("Trait", 2); tag.putString("TraitClass", "test.StandardTrait"); return tag;
    }
    private static HonkaiWirelessSavedData roundtrip(HonkaiWirelessSavedData data) {
        try {
            var bytes = new ByteArrayOutputStream(); NbtIo.writeCompressed(data.save(new CompoundTag()), bytes);
            return HonkaiWirelessSavedData.load(NbtIo.readCompressed(new ByteArrayInputStream(bytes.toByteArray())));
        } catch (IOException problem) { throw new AssertionError(problem); }
    }
    private static final class Port implements Hk3PortPayment.Port {
        BigInteger balance = BigInteger.valueOf(100), limit = BigInteger.valueOf(100);
        BigInteger maximumRefund = BigInteger.valueOf(100);
        boolean failAfterChange, reverse;
        final CompoundTag address = trait(12);
        @Override public BigInteger available() { return balance; }
        @Override public BigInteger power() { return BigInteger.valueOf(100); }
        @Override public CompoundTag refundTarget() { return address.copy(); }
        @Override public BigInteger change(BigInteger delta) {
            BigInteger actual = delta;
            if (delta.signum() > 0) {
                actual = delta.min(maximumRefund).min(limit.subtract(balance));
                if (reverse) actual = BigInteger.valueOf(-2);
            }
            balance = balance.add(actual);
            if (failAfterChange) { failAfterChange = false; throw new Hk3PortPayment.ChangeFailure(actual,
                    new IllegalStateException("受控：余额已改、通知抛错")); }
            return actual;
        }
    }
    public static void main(String[] args) throws Exception {
        net.minecraft.SharedConstants.tryDetectVersion();
        energyRestart(); diskRestart(); sameAccountTwoMachines(); partialPorts(); checkpointFailures(); damagedJournal();
        targetIdentity(); dirtyFailures();
        if (Arrays.asList(args).contains("--registry")) materialCodec();
        wiring();
        System.out.println("Refund persistence: " + checks + " checks passed; offline helpers/NBT/wiring only; live restart acceptance pending");
    }
    private static Runnable decode(HonkaiWirelessSavedData hw, Map<UUID, BigInteger> eu, AtomicBoolean available,
                                    Port port, CompoundTag row) {
        return switch (row.getString("Kind")) {
            case "hw" -> Hk3RefundActions.hw(hw, row.getUUID("Account"), new BigInteger(row.getString("Amount")));
            case "grid" -> Hk3RefundActions.action(row, () -> {
                if (!available.get()) throw new IllegalStateException("受控：原账户暂不可用");
                Hk3GridEnergyRefund.reverse(eu, row.getUUID("Account"), new BigInteger(row.getString("Amount")), () -> {});
            });
            case "port" -> Hk3PortPayment.refund(port, new BigInteger(row.getString("Left")));
            default -> Hk3RefundActions.action(row, () -> { throw new IllegalStateException("未知回调仍阻断"); });
        };
    }
    private static CompoundTag money(String kind, UUID account, BigInteger amount) {
        var row = new CompoundTag(); row.putString("Kind", kind); row.putUUID("Account", account);
        row.putString("Amount", amount.toString()); return row;
    }
    private static void energyRestart() {
        var hw = new HonkaiWirelessSavedData(); hw.setAmount(OWNER, TOTAL); hw.setAmount(OTHER, TOTAL);
        var eu = new HashMap<UUID, BigInteger>(); eu.put(OWNER, TOTAL.subtract(BigInteger.valueOf(37))); eu.put(OTHER, TOTAL);
        var identity = address(1); var ready = new AtomicBoolean(false);
        var tick = new Hk3EnergyTick(Hk3RefundJournal.checkpoint(hw, key(identity), identity));
        check(hw.reserve(OWNER, BigInteger.valueOf(19), tick), "原玩家HW预留");
        var delta = BigInteger.valueOf(-37);
        tick.undoWith(Hk3RefundActions.action(money("grid", OWNER, delta), () -> { throw new IllegalStateException("等待原EU账本"); }));
        check(!tick.finish(false), "退款失败留下两项");
        var restarted = roundtrip(hw);
        var resumed = Hk3RefundJournal.restore(restarted, key(identity), row -> decode(restarted, eu, ready, null, row));
        reject(() -> resumed.onCommit(() -> {}));
        reject(() -> resumed.finish(true));
        check(!resumed.finish(false) && restarted.getAmount(OWNER).equals(TOTAL.subtract(BigInteger.valueOf(19))),
                "未退EU时不越序发HW");
        ready.set(true);
        check(resumed.finish(false) && resumed.finish(false), "恢复后重复收尾幂等");
        check(restarted.getAmount(OWNER).equals(TOTAL) && eu.get(OWNER).equals(TOTAL), "正常保存重启双能源守恒");
        check(restarted.getAmount(OTHER).equals(TOTAL) && eu.get(OTHER).equals(TOTAL), "当前owner换成他人也不改原退款UUID");
        check(roundtrip(restarted).pendingRefund(key(identity)) == null, "成功退款再保存重启无剩余记录");
        var dataCopy = restarted.save(new CompoundTag());
        check(dataCopy.getList("PendingRefunds", Tag.TAG_COMPOUND).isEmpty(), "结算日志清账");
    }
    private static void diskRestart() throws IOException {
        var directory = java.nio.file.Files.createTempDirectory("hk3-pending-refund-");
        try {
            var file = directory.resolve("hk3gtl_wireless_pool.dat").toFile();
            var data = new HonkaiWirelessSavedData(); data.setAmount(OWNER, TOTAL);
            var controller = address(10);
            var tick = new Hk3EnergyTick(Hk3RefundJournal.checkpoint(data, key(controller), controller));
            check(data.reserve(OWNER, BigInteger.valueOf(17), tick), "文件重启夹具预留");
            tick.undoWith(Hk3RefundActions.action(money("grid", OWNER, BigInteger.valueOf(-29)),
                    () -> { throw new IllegalStateException("受控原账户不可用"); }));
            check(!tick.finish(false), "保留退款记录后正常保存"); data.save(file);
            check(file.isFile() && !data.isDirty(), "原子SavedData文件写入完成");
            var loaded = HonkaiWirelessSavedData.load(NbtIo.readCompressed(file).getCompound("data"));
            var eu = new HashMap<UUID, BigInteger>(); eu.put(OWNER, TOTAL.subtract(BigInteger.valueOf(29)));
            var retry = Hk3RefundJournal.restore(loaded, key(controller), row -> decode(loaded, eu, new AtomicBoolean(true), null, row));
            check(retry.finish(false) && loaded.getAmount(OWNER).equals(TOTAL) && eu.get(OWNER).equals(TOTAL),
                    "真实SavedData文件重读后恢复原账户");
            loaded.save(file);
            var twice = HonkaiWirelessSavedData.load(NbtIo.readCompressed(file).getCompound("data"));
            check(twice.pendingRefund(key(controller)) == null && twice.getAmount(OWNER).equals(TOTAL),
                    "完成后再落盘读取不会重复退款");
        } finally {
            try (var files = java.nio.file.Files.list(directory)) {
                for (var file : files.toList()) java.nio.file.Files.delete(file);
            }
            java.nio.file.Files.delete(directory);
        }
    }
    private static void sameAccountTwoMachines() {
        var hw = new HonkaiWirelessSavedData(); hw.setAmount(OWNER, TOTAL);
        for (int i = 20; i < 22; i++) {
            var controller = address(i);
            var tick = new Hk3EnergyTick(Hk3RefundJournal.checkpoint(hw, key(controller), controller));
            check(hw.reserve(OWNER, BigInteger.valueOf(i), tick), "双机同账户预留独立");
            tick.undoWith(() -> { throw new IllegalStateException("不可序列化回调"); });
            check(!tick.finish(false), "双机各自保留日志");
        }
        var restarted = roundtrip(hw);
        check(restarted.getAmount(OWNER).equals(TOTAL.subtract(BigInteger.valueOf(41))), "重启未自动越过未知退款");
        check(restarted.save(new CompoundTag()).getList("PendingRefunds", Tag.TAG_COMPOUND).size() == 2, "两台机日志未互相覆盖");
        for (int i = 20; i < 22; i++) {
            var tick = Hk3RefundJournal.restore(restarted, key(address(i)), row -> decode(restarted, Map.of(), new AtomicBoolean(true), null, row));
            check(!tick.finish(false) && !tick.settled(), "未知回调跨重启仍阻断");
        }
        var original = restarted.pendingRefund(key(address(20)));
        var altered = original.copy(); altered.getCompound("Controller").putString("Definition", "gtceu:other_machine");
        check(!Hk3RefundTarget.sameIdentity(original.getCompound("Controller"), altered.getCompound("Controller")), "旧日志实例不能转移到其他机器");
    }
    private static void partialPorts() {
        for (int mode = 0; mode < 3; mode++) {
            var hw = new HonkaiWirelessSavedData(); hw.setAmount(OWNER, TOTAL);
            var controller = address(30 + mode); var port = new Port();
            var tick = new Hk3EnergyTick(Hk3RefundJournal.checkpoint(hw, key(controller), controller));
            check(hw.reserve(OWNER, BigInteger.valueOf(5), tick), "端口夹具HW预留");
            check(Hk3PortPayment.pay(List.of(port), BigInteger.valueOf(13), tick), "真实端口付款13");
            port.maximumRefund = BigInteger.valueOf(3); port.failAfterChange = mode == 1; port.reverse = mode == 2;
            check(!tick.finish(false), "部分/通知异常/反向退款保持暂停");
            BigInteger remaining = BigInteger.valueOf(100).subtract(port.balance);
            var saved = hw.pendingRefund(key(controller));
            check(new BigInteger(saved.getList("Actions", Tag.TAG_COMPOUND).getCompound(0).getString("Left")).equals(remaining),
                    "持久化真实剩余差额而非原总额");
            var restart = roundtrip(hw); port.maximumRefund = BigInteger.valueOf(100); port.reverse = false;
            var retry = Hk3RefundJournal.restore(restart, key(controller), row -> decode(restart, Map.of(), new AtomicBoolean(true), port, row));
            check(retry.finish(false) && retry.finish(false), "部分退款正常保存重启继续");
            check(port.balance.equals(BigInteger.valueOf(100)) && restart.getAmount(OWNER).equals(TOTAL), "不重复退已到账部分");
            check(roundtrip(restart).pendingRefund(key(controller)) == null, "端口退款清账后再启无动作");
        }
    }
    private static void checkpointFailures() {
        for (boolean committed : List.of(false, true)) {
            var first = new AtomicBoolean(true); var undo = new AtomicInteger(); var receipts = new AtomicInteger();
            var saves = new AtomicInteger(); var tick = new Hk3EnergyTick(pending -> {
                saves.incrementAndGet(); if (first.getAndSet(false)) throw new IllegalStateException("受控日志写失败");
            });
            tick.undoWith(undo::incrementAndGet); tick.onCommit(receipts::incrementAndGet);
            check(!tick.finish(committed) && !tick.settled(), "日志失败不能丢活票据");
            check(tick.finish(false) && tick.settled() && saves.get() == 2, "只重试日志");
            check(undo.get() == (committed ? 0 : 1) && receipts.get() == (committed ? 1 : 0), "补存不重跑退款或成功回执");
        }
    }
    private static void damagedJournal() {
        var hw = new HonkaiWirelessSavedData(); var controller = address(70);
        var tick = new Hk3EnergyTick(Hk3RefundJournal.checkpoint(hw, key(controller), controller));
        tick.undoWith(() -> { throw new IllegalStateException("未知"); }); tick.finish(false);
        var baseline = hw.save(new CompoundTag());
        var badVersion = baseline.copy(); badVersion.getList("PendingRefunds", Tag.TAG_COMPOUND).getCompound(0).putInt("Version", 2);
        reject(() -> HonkaiWirelessSavedData.load(badVersion));
        var duplicate = baseline.copy(); duplicate.getList("PendingRefunds", Tag.TAG_COMPOUND).add(
                duplicate.getList("PendingRefunds", Tag.TAG_COMPOUND).getCompound(0).copy());
        reject(() -> HonkaiWirelessSavedData.load(duplicate));
        var wrongKey = baseline.copy(); wrongKey.getList("PendingRefunds", Tag.TAG_COMPOUND).getCompound(0).putString("Key", "other");
        reject(() -> HonkaiWirelessSavedData.load(wrongKey));
        var badAction = baseline.copy(); badAction.getList("PendingRefunds", Tag.TAG_COMPOUND).getCompound(0)
                .getList("Actions", Tag.TAG_COMPOUND).getCompound(0).putString("Kind", "unrecognized");
        reject(() -> HonkaiWirelessSavedData.load(badAction));
        var badAmount = money("hw", OWNER, BigInteger.ONE.negate()); reject(() -> Hk3RefundActions.validate(badAmount));
        var missingAccount = money("grid", OWNER, BigInteger.ONE); missingAccount.remove("Account");
        reject(() -> Hk3RefundActions.validate(missingAccount));
        var legacy = baseline.copy(); legacy.remove("PendingRefunds");
        check(HonkaiWirelessSavedData.load(legacy).save(new CompoundTag()).getList("PendingRefunds", Tag.TAG_COMPOUND).isEmpty(), "旧账本无退款字段兼容");
        var exposed = hw.pendingRefund(key(controller)); exposed.getCompound("Controller").putString("Definition", "gtceu:mutated");
        check(hw.pendingRefund(key(controller)).getCompound("Controller").getString("Definition").equals("gtceu:test_machine"),
                "读取副本不能改写原日志");
        var replacement = controller.copy(); replacement.putUUID("Instance", OTHER);
        reject(() -> Hk3RefundJournal.checkpoint(hw, key(controller), replacement).accept(List.of()));
        check(hw.pendingRefund(key(controller)) != null, "替换控制器不能清掉原退款");
    }
    private static void targetIdentity() {
        var original = address(90);
        check(Hk3RefundTarget.sameIdentity(original, original.copy()), "原机器身份匹配");
        var replacement = original.copy(); replacement.putUUID("Instance", OTHER);
        check(!Hk3RefundTarget.sameIdentity(original, replacement), "同坐标同型替换机拒绝");
        var dimension = original.copy(); dimension.putString("Dimension", "minecraft:the_nether");
        check(!Hk3RefundTarget.sameIdentity(original, dimension), "相同坐标跨维度拒绝");
        var moved = original.copy(); moved.putLong("Position", 91);
        check(!Hk3RefundTarget.sameIdentity(original, moved), "同UUID坐标变化拒绝");
        var missing = original.copy(); missing.remove("Instance"); reject(() -> Hk3RefundTarget.validate(missing, false));
    }
    private static void dirtyFailures() throws Exception {
        var observed = com.sirin.hk3gtl.common.recipe.power.Hk3PowerPorts.class.getDeclaredMethod("changeObserved",
                com.gregtechceu.gtceu.api.capability.IEnergyContainer.class, BigInteger.class, Runnable.class);
        observed.setAccessible(true);
        for (boolean failureOnPayment : List.of(true, false)) {
            var balance = new AtomicLong(100); var failDirty = new AtomicBoolean(failureOnPayment);
            var energy = (com.gregtechceu.gtceu.api.capability.IEnergyContainer) java.lang.reflect.Proxy.newProxyInstance(
                    RefundPersistenceTest.class.getClassLoader(), new Class<?>[]{com.gregtechceu.gtceu.api.capability.IEnergyContainer.class},
                    (proxy, method, args) -> {
                        if (method.getName().equals("getEnergyStored")) return balance.get();
                        if (method.getName().equals("changeEnergy")) { balance.addAndGet((long) args[0]); return args[0]; }
                        throw new AssertionError(method.getName());
                    });
            var port = new Hk3PortPayment.Port() {
                @Override public BigInteger available() { return BigInteger.valueOf(balance.get()); }
                @Override public BigInteger power() { return BigInteger.valueOf(100); }
                @Override public CompoundTag refundTarget() { return trait(110); }
                @Override public BigInteger change(BigInteger delta) {
                    try { return (BigInteger) observed.invoke(null, energy, delta, (Runnable) () -> {
                        if (failDirty.getAndSet(false)) throw new IllegalStateException("受控：余额已改、标脏失败");
                    }); }
                    catch (java.lang.reflect.InvocationTargetException failure) { throw (RuntimeException) failure.getCause(); }
                    catch (ReflectiveOperationException failure) { throw new AssertionError(failure); }
                }
            };
            var hw = new HonkaiWirelessSavedData(); var controller = address(failureOnPayment ? 111 : 112);
            var tick = new Hk3EnergyTick(Hk3RefundJournal.checkpoint(hw, key(controller), controller));
            check(Hk3PortPayment.pay(List.of(port), BigInteger.valueOf(13), tick) != failureOnPayment,
                    "标脏异常付款返回失败且登记真实差量");
            if (!failureOnPayment) failDirty.set(true);
            check(tick.finish(false) == failureOnPayment && balance.get() == 100, "标脏异常后实际退款改量已记录");
            check(tick.finish(false) && balance.get() == 100, "标脏失败再结算不重复返款");
        }
    }
    private static Object invoke(String method, Class<?> type, Object argument) throws Exception {
        var action = Hk3MaterialTick.class.getDeclaredMethod(method, type); action.setAccessible(true);
        try { return action.invoke(null, argument); }
        catch (java.lang.reflect.InvocationTargetException failure) {
            if (failure.getCause() instanceof RuntimeException runtime) throw runtime;
            throw failure;
        }
    }
    private static void materialCodec() throws Exception {
        try { net.minecraft.server.Bootstrap.bootStrap(); }
        catch (ExceptionInInitializerError offlineForge) {
            // 普通Java进程没有Forge事件转换器；只接受其注册表完成后的已知网络事件构造器缺口。
            Throwable cause = offlineForge;
            while (cause.getCause() != null) cause = cause.getCause();
            if (!(cause instanceof NoSuchMethodException)
                    || !cause.getMessage().equals("net.minecraftforge.network.NetworkEvent.<init>()")) throw offlineForge;
            check(net.minecraft.core.registries.BuiltInRegistries.ITEM.containsKey(
                    net.minecraft.resources.ResourceLocation.tryParse("minecraft:iron_ingot")), "离线原生物品注册表已就绪");
        }
        var item = new net.minecraft.world.item.ItemStack(net.minecraft.world.item.Items.IRON_INGOT, 100_000);
        item.getOrCreateTag().putString("Marker", "原始");
        var before = (CompoundTag) invoke("itemTag", net.minecraft.world.item.ItemStack.class, item);
        item.getOrCreateTag().putString("Marker", "已改写");
        var restored = (net.minecraft.world.item.ItemStack) invoke("itemStack", CompoundTag.class, before);
        check(restored.getCount() == 100_000 && restored.getTag().getString("Marker").equals("原始"), "大物品数量与NBT深拷贝");
        var badItem = before.copy(); badItem.putString("id", "hk3gtl:unknown_item");
        reject(() -> { try { invoke("itemStack", CompoundTag.class, badItem); } catch (RuntimeException e) { throw e; } catch (Exception e) { throw new AssertionError(e); } });
        var fluid = new CompoundTag(); fluid.putString("FluidName", "minecraft:water"); fluid.putLong("Amount", Long.MAX_VALUE - 5);
        var custom = new CompoundTag(); custom.putString("Marker", "原始"); fluid.put("Tag", custom);
        var fluidStack = (com.lowdragmc.lowdraglib.side.fluid.FluidStack) invoke("fluidStack", CompoundTag.class, fluid);
        custom.putString("Marker", "已改写");
        check(fluidStack.getAmount() == Long.MAX_VALUE - 5 && fluidStack.saveToTag(new CompoundTag())
                .getCompound("Tag").getString("Marker").equals("原始"), "流体long数量与NBT深拷贝");
        var badFluid = fluid.copy(); badFluid.putString("FluidName", "hk3gtl:unknown_fluid");
        reject(() -> { try { invoke("fluidStack", CompoundTag.class, badFluid); } catch (RuntimeException e) { throw e; } catch (Exception e) { throw new AssertionError(e); } });
        var material = new CompoundTag(); material.putString("Kind", "item"); material.put("Target", trait(100));
        material.putInt("Slot", 1); material.putBoolean("Sealed", true); material.putBoolean("RestorePending", true);
        material.put("Before", before); material.put("After", before.copy()); Hk3RefundActions.validate(material); checks++;
        material.putInt("Slot", -1); reject(() -> Hk3RefundActions.validate(material));
    }
    private static ClassNode node(String name) throws IOException {
        try (var stream = RefundPersistenceTest.class.getResourceAsStream("/com/sirin/hk3gtl/" + name + ".class")) {
            var node = new ClassNode(); new ClassReader(Objects.requireNonNull(stream)).accept(node, 0); return node;
        }
    }
    private static boolean calls(ClassNode node, String owner, String method) {
        for (var m : node.methods) for (var instruction : m.instructions)
            if (instruction instanceof MethodInsnNode call && call.owner.endsWith(owner) && call.name.equals(method)) return true;
        return false;
    }
    private static void wiring() throws Exception {
        var own = node("common/machine/Hk3RecipeLogic"); var foreign = node("mixin/Hk3PowerLogicMixin");
        check(calls(own, "/Hk3RefundJournal", "open") && calls(own, "/Hk3RefundJournal", "resume"), "HK真实入口创建与恢复日志票据");
        check(calls(foreign, "/Hk3RefundJournal", "open") && calls(foreign, "/Hk3RefundJournal", "resume")
                && calls(foreign, "/Hk3RecipeLogic", "retryPendingRefund"), "GT serverTick含自家退款恢复及空配方重试");
        var target = node("common/capability/Hk3RefundTarget");
        check(calls(target, "/ServerLevel", "hasChunkAt") && calls(target, "/MetaMachine", "getMachine"), "目标解析先守已加载区块");
        var actions = node("common/capability/Hk3RefundActions");
        check(calls(actions, "/Hk3GridEnergyRefund", "forAccount") && !calls(actions, "/TeamUtil", "getTeamUUID"), "重启恢复原团队UUID不再次映射");
    }
}
