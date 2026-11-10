package com.sirin.hk3gtl.test.worldbubble;

import com.sirin.hk3gtl.common.worldbubble.Hk3WorldBubbleData;
import com.sirin.hk3gtl.common.worldbubble.Hk3WorldBubbleLedger;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;

import java.util.UUID;
import static com.sirin.hk3gtl.common.worldbubble.Hk3WorldBubbleLedger.*;

/**
 * 【变更记录 #1】2026-09-27 04:18:00（第 1 次备注 · 内测5修订90）
 * 删除：无。新增：真实/模拟生命周期、十次上限、并发预留、恢复与防重复交付收据测试。
 * 修改：不读取玩家存档、不调用外部库存；用途：验证公共账本，不代表L6–L8游戏工序已完成。
 */
/**
 * 【变更记录 #2】2026-09-27 04:26:03（第 2 次备注 · 内测5修订90）
 * 删除：无。新增：十次上限的恢复校验、不同操作者共享计数、十次后合法捕获与终止。
 * 修改：不自行规定终止产量扣减；用途：确保技术上限与未裁定的资源预算保持分离。
 */
public final class WorldBubbleLedgerTest {
    private static final UUID ACTOR = new UUID(1, 1), OTHER = new UUID(2, 2);
    private static int checks;
    public static void main(String[] args) {
        miningAndRecovery(); terminalLifecycle(); simulationIsolation(); corruptData(); dirtyPersistence();
        System.out.println("World bubble ledger: " + checks + " checks passed; no game or inventory delivery tested");
    }
    private static CompoundTag receipt(int n) {
        CompoundTag tag = new CompoundTag(); tag.putInt("VerifiedProcess", n); return tag;
    }
    private static void miningAndRecovery() {
        var ledger = new Hk3WorldBubbleLedger();
        UUID target = ledger.discover("test:sea/coordinate-1");
        check(target.equals(ledger.discover("test:sea/coordinate-1")), "rediscovery stable ID");
        UUID cancelled = new UUID(3, 0);
        ledger.begin(cancelled, ACTOR, Domain.REAL, target, Action.MINE);
        ledger.cancel(cancelled, ACTOR); ledger.cancel(cancelled, ACTOR);
        check(ledger.begin(cancelled, ACTOR, Domain.REAL, target, Action.MINE).phase() == Phase.CANCELLED,
                "cancelled request never restarts");
        reject(() -> ledger.settle(cancelled, ACTOR, receipt(0)));
        check(ledger.real(target).miningCount() == 0, "cancel does not consume mining budget");
        for (int i = 0; i < 10; i++) {
            UUID op = new UUID(4, i);
            ledger.begin(op, ACTOR, Domain.REAL, target, Action.MINE);
            check(ledger.real(target).miningCount() == i, "reservation not counted");
            var restored = Hk3WorldBubbleLedger.load(ledger.save());
            check(restored.begin(op, ACTOR, Domain.REAL, target, Action.MINE).phase() == Phase.RESERVED,
                    "reserved operation restored");
            reject(() -> restored.begin(UUID.randomUUID(), ACTOR, Domain.REAL, target, Action.CAPTURE));
            reject(() -> restored.begin(op, OTHER, Domain.REAL, target, Action.MINE));
            reject(() -> restored.settle(op, OTHER, receipt(1)));
            reject(() -> restored.settle(op, ACTOR, new CompoundTag()));
            CompoundTag fixed = receipt(i);
            restored.settle(op, ACTOR, fixed); fixed.putInt("VerifiedProcess", 100);
            var tx = restored.settle(op, ACTOR, receipt(i));
            tx.receipt().putString("Injected", "no");
            check(!restored.transaction(op).receipt().contains("Injected"), "immutable receipt");
            reject(() -> restored.settle(op, ACTOR, receipt(100)));
            check(restored.real(target).miningCount() == i + 1, "one completed mining per operation");
            var roundTrip = Hk3WorldBubbleLedger.load(restored.save());
            roundTrip.settle(op, ACTOR, receipt(i));
            check(roundTrip.real(target).miningCount() == i + 1, "restart retry not recounted");
            check(roundTrip.acknowledge(op, ACTOR), "first delivery acknowledgement");
            check(!roundTrip.acknowledge(op, ACTOR), "second delivery acknowledgement rejected");
            var finalTrip = Hk3WorldBubbleLedger.load(roundTrip.save());
            check(!finalTrip.acknowledge(op, ACTOR), "delivery acknowledgement persists");
            // 保持主账本对象以便闭包引用，每次用新目标对象继续验证已确认收据。
            ledger.settle(op, ACTOR, receipt(i)); ledger.acknowledge(op, ACTOR);
        }
        reject(() -> ledger.begin(UUID.randomUUID(), ACTOR, Domain.REAL, target, Action.MINE));
        check(ledger.pendingDeliveries(ACTOR).isEmpty(), "acknowledged receipts not redelivered");
        check(ledger.real(target).miningCount() == 10, "global cap is ten");
        var restoredLimit = Hk3WorldBubbleLedger.load(ledger.save());
        reject(() -> restoredLimit.begin(UUID.randomUUID(), OTHER, Domain.REAL, target, Action.MINE));
        UUID capture = UUID.randomUUID();
        restoredLimit.begin(capture, OTHER, Domain.REAL, target, Action.CAPTURE);
        restoredLimit.settle(capture, OTHER, receipt(50));
        UUID terminal = UUID.randomUUID();
        restoredLimit.begin(terminal, OTHER, Domain.REAL, target, Action.TERMINATE_REAL);
        restoredLimit.settle(terminal, OTHER, receipt(51));
        check(restoredLimit.real(target).miningCount() == 10, "capture and termination do not change mining count");
        check(Hk3WorldBubbleLedger.load(restoredLimit.save()).real(target).state() == RealState.TERMINATED,
                "ten mines followed by termination persist");
        UUID newTarget = ledger.discover("test:sea/coordinate-2");
        check(ledger.real(newTarget).miningCount() == 0, "different target independent budget");
        reject(() -> ledger.begin(new UUID(4, 0), ACTOR, Domain.REAL, newTarget, Action.MINE));
    }
    private static void terminalLifecycle() {
        var ledger = new Hk3WorldBubbleLedger(); UUID target = ledger.discover("test:terminal");
        reject(() -> ledger.begin(UUID.randomUUID(), ACTOR, Domain.REAL, target, Action.TERMINATE_REAL));
        UUID capture = UUID.randomUUID();
        ledger.begin(capture, ACTOR, Domain.REAL, target, Action.CAPTURE);
        reject(() -> ledger.acknowledge(capture, ACTOR));
        ledger.settle(capture, ACTOR, receipt(11));
        check(ledger.real(target).state() == RealState.CAPTURED, "capture state");
        reject(() -> ledger.begin(UUID.randomUUID(), ACTOR, Domain.REAL, target, Action.MINE));
        reject(() -> ledger.begin(UUID.randomUUID(), ACTOR, Domain.REAL, target, Action.CAPTURE));
        UUID terminal = UUID.randomUUID(); ledger.begin(terminal, ACTOR, Domain.REAL, target, Action.TERMINATE_REAL);
        ledger.settle(terminal, ACTOR, receipt(12));
        var loaded = Hk3WorldBubbleLedger.load(ledger.save());
        loaded.settle(terminal, ACTOR, receipt(12));
        check(loaded.real(target).state() == RealState.TERMINATED, "terminal state survives restart");
        check(loaded.discover("test:terminal").equals(target), "rediscovery cannot reset terminal target");
        reject(() -> loaded.begin(UUID.randomUUID(), ACTOR, Domain.REAL, target, Action.TERMINATE_REAL));
        reject(() -> loaded.begin(UUID.randomUUID(), ACTOR, Domain.REAL, target, Action.CAPTURE));
        reject(() -> loaded.cancel(terminal, ACTOR));
        check(loaded.pendingDeliveries(ACTOR).size() == 2, "one capture and one terminal receipt");
        check(loaded.pendingDeliveries(OTHER).isEmpty(), "pending records isolated by actor");
    }
    private static void simulationIsolation() {
        var ledger = new Hk3WorldBubbleLedger(); UUID batch = UUID.randomUUID();
        ledger.createSimulation(batch, ACTOR, "test:builder/first");
        reject(() -> ledger.begin(UUID.randomUUID(), ACTOR, Domain.REAL, batch, Action.MINE));
        reject(() -> ledger.begin(UUID.randomUUID(), ACTOR, Domain.SIMULATED, batch, Action.MINE));
        reject(() -> ledger.begin(UUID.randomUUID(), ACTOR, Domain.SIMULATED, batch, Action.TERMINATE_SIMULATION));
        UUID stable = UUID.randomUUID(); ledger.begin(stable, ACTOR, Domain.SIMULATED, batch, Action.STABILIZE_SIMULATION);
        ledger.settle(stable, ACTOR, receipt(21));
        UUID end = UUID.randomUUID(); ledger.begin(end, ACTOR, Domain.SIMULATED, batch, Action.TERMINATE_SIMULATION);
        ledger.settle(end, ACTOR, receipt(22));
        var loaded = Hk3WorldBubbleLedger.load(ledger.save());
        loaded.createSimulation(batch, ACTOR, "test:builder/first");
        check(loaded.simulation(batch).state() == SimulationState.TERMINATED, "batch identity never recycled");
        check(loaded.real(batch) == null, "simulation is never a real target");
        reject(() -> loaded.createSimulation(batch, OTHER, "test:builder/first"));
        reject(() -> loaded.createSimulation(batch, ACTOR, "test:builder/second"));
        reject(() -> loaded.begin(UUID.randomUUID(), ACTOR, Domain.SIMULATED, batch, Action.TERMINATE_SIMULATION));
        UUID next = UUID.randomUUID(); loaded.createSimulation(next, ACTOR, "test:builder/first");
        check(loaded.simulation(next).state() == SimulationState.CREATED, "next independent simulation");
    }
    private static void corruptData() {
        var ledger = new Hk3WorldBubbleLedger(); UUID target = ledger.discover("test:corrupt");
        UUID operation = UUID.randomUUID(); ledger.begin(operation, ACTOR, Domain.REAL, target, Action.CAPTURE);
        ledger.settle(operation, ACTOR, receipt(30)); CompoundTag original = ledger.save();
        CompoundTag future = original.copy(); future.putInt("Version", 2); reject(() -> Hk3WorldBubbleLedger.load(future));
        CompoundTag duplicate = original.copy(); var ops = duplicate.getList("Operations", Tag.TAG_COMPOUND);
        ops.add(ops.getCompound(0).copy()); reject(() -> Hk3WorldBubbleLedger.load(duplicate));
        CompoundTag empty = original.copy(); empty.getList("Operations", Tag.TAG_COMPOUND).getCompound(0).put("Receipt", new CompoundTag());
        reject(() -> Hk3WorldBubbleLedger.load(empty));
        CompoundTag badTarget = original.copy(); badTarget.getList("Real", Tag.TAG_COMPOUND).getCompound(0).putUUID("Id", UUID.randomUUID());
        reject(() -> Hk3WorldBubbleLedger.load(badTarget));
        CompoundTag delivered = original.copy(); var first = delivered.getList("Operations", Tag.TAG_COMPOUND).getCompound(0);
        first.putString("Phase", "RESERVED"); first.putBoolean("Delivered", true); reject(() -> Hk3WorldBubbleLedger.load(delivered));
        CompoundTag badAction = original.copy(); badAction.getList("Operations", Tag.TAG_COMPOUND).getCompound(0).putString("Action", "TERMINATE_REAL");
        reject(() -> Hk3WorldBubbleLedger.load(badAction));
        CompoundTag missing = original.copy(); missing.remove("Simulations"); reject(() -> Hk3WorldBubbleLedger.load(missing));
        check(Hk3WorldBubbleLedger.load(original).save().equals(original), "deterministic NBT roundtrip");
    }
    private static void dirtyPersistence() {
        var data = new Hk3WorldBubbleData(); UUID target = data.ledger().discover("test:saved-data");
        check(data.isDirty(), "discovery marks SavedData dirty"); data.setDirty(false);
        data.ledger().discover("test:saved-data"); check(!data.isDirty(), "duplicate discovery unchanged");
        UUID op = UUID.randomUUID(); data.ledger().begin(op, ACTOR, Domain.REAL, target, Action.MINE);
        check(data.isDirty(), "reservation marks SavedData dirty");
        var loaded = Hk3WorldBubbleData.load(data.save(new CompoundTag()));
        check(!loaded.isDirty(), "load does not simulate new mutations");
        loaded.ledger().settle(op, ACTOR, receipt(41)); check(loaded.isDirty(), "restored listener marks dirty");
        var saved = loaded.save(new CompoundTag()); saved.getCompound("Ledger").remove("Real");
        check(loaded.ledger().real(target).miningCount() == 1, "save output cannot mutate ledger");
    }
    private static void check(boolean value, String message) { checks++; if (!value) throw new AssertionError(message); }
    private static void reject(Runnable operation) {
        checks++; try { operation.run(); } catch (IllegalArgumentException expected) { return; }
        throw new AssertionError("Invalid world bubble operation accepted");
    }
}
