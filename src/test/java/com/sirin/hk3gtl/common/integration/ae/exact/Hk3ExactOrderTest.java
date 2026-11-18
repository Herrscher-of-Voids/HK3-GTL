package com.sirin.hk3gtl.common.integration.ae.exact;

import java.math.BigInteger;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicInteger;

/** 父订单回执与恢复边界的纯状态测试，不代表真实CPU产出。 */
public final class Hk3ExactOrderTest {
    private static int checks;

    public static void main(String[] args) throws Exception {
        decimalParsing();
        batchesAndReceipts();
        partialProduction();
        pauseAndCancel();
        restoreAndValidation();
        concurrentReceipt();
        System.out.println("大数父订单离线核验通过：" + checks + "项；未进行真实CPU或游戏测试。");
    }

    private static void decimalParsing() {
        check(Hk3ExactOrder.parsePositiveDecimal("00012").equals(n(12)), "正十进制允许前导零");
        check(Hk3ExactOrder.parsePositiveDecimal("9".repeat(256)).toString().length() == 256, "256位边界");
        for (String invalid : new String[]{"", "0", "000", "-1", "+1", "1e9", "1.0", " 1", "1 ", "１", "9".repeat(257)}) {
            invalid(() -> Hk3ExactOrder.parsePositiveDecimal(invalid));
        }
    }

    private static void batchesAndReceipts() {
        BigInteger total = BigInteger.ONE.shiftLeft(100);
        var order = fresh(total);
        UUID first = order.beginBatch(Long.MAX_VALUE);
        check(order.snapshot().state() == Hk3ExactOrder.State.RUNNING, "开始批次进入运行状态");
        check(order.remaining().equals(total), "在途任务不提前计入完成量");
        check(!order.finish(UUID.randomUUID(), true), "错误令牌不计数");
        check(order.finish(first, true), "真实成功回执可消费");
        check(order.snapshot().completed().equals(n(Long.MAX_VALUE)), "超过long父总量保留精确完成量");
        check(order.remaining().equals(total.subtract(n(Long.MAX_VALUE))), "大数剩余量精确");
        check(!order.finish(first, true), "重复成功回执拒绝");
        check(order.snapshot().state() == Hk3ExactOrder.State.READY && order.snapshot().activeToken() == null, "成功后可开始新批且清在途");
        UUID second = order.beginBatch(1);
        check(!first.equals(second) && !order.finish(first, false), "旧批次不能干扰新批次");
        check(order.finish(second, false), "失败回执被消费一次");
        check(order.snapshot().state() == Hk3ExactOrder.State.PAUSED && order.snapshot().completed().equals(n(Long.MAX_VALUE)), "失败不计产出也不自动重发");
        illegalState(() -> order.beginBatch(1));
        check(order.resume(), "无在途暂停任务可恢复");

        var small = fresh(n(2));
        invalid(() -> small.beginBatch(0));
        invalid(() -> small.beginBatch(-1));
        invalid(() -> small.beginBatch(3));
        UUID finalToken = small.beginBatch(2);
        illegalState(() -> small.beginBatch(1));
        check(small.finish(finalToken, true) && small.remaining().signum() == 0, "最后一批成功完成父订单");
        check(small.snapshot().state() == Hk3ExactOrder.State.COMPLETE && !small.resume() && !small.pause() && !small.cancel(), "完成态不可复活或倒退");
    }

    private static void partialProduction() {
        var order = fresh(n(100));
        UUID token = order.beginBatch(100);
        invalid(() -> order.finish(token, false, n(-1)));
        invalid(() -> order.finish(token, false, n(101)));
        invalid(() -> order.finish(token, true, n(40)));
        invalid(() -> order.finish(token, false, null));
        check(order.snapshot().state() == Hk3ExactOrder.State.RUNNING
                && order.snapshot().activeToken().equals(token) && order.snapshot().completed().signum() == 0,
                "非法回执不消费令牌或改动完成量");
        check(order.finish(token, false, n(40)) && order.snapshot().completed().equals(n(40))
                && order.remaining().equals(n(60)), "失败仍核销真实部分产出40件");
        check(order.snapshot().state() == Hk3ExactOrder.State.PAUSED && order.resume(), "部分失败后可明确恢复真实余量");
        check(!order.finish(token, false, n(40)), "重复部分回执不再次计数");
        invalid(() -> order.beginBatch(100));
        UUID remaining = order.beginBatch(60);
        check(order.finish(remaining, true, n(60)) && order.snapshot().completed().equals(n(100))
                && order.snapshot().state() == Hk3ExactOrder.State.COMPLETE, "恢复只生产余下60件，累计不超100件");

        var cancelled = fresh(n(100));
        UUID cancelledToken = cancelled.beginBatch(100);
        cancelled.cancel();
        check(cancelled.finish(cancelledToken, false, n(40)) && cancelled.snapshot().completed().equals(n(40))
                && cancelled.snapshot().state() == Hk3ExactOrder.State.CANCELLED, "取消的部分回执记40件且不复活");
        check(!cancelled.resume() && !cancelled.finish(cancelledToken, false, n(40)), "取消部分回执不重启或重复计数");

        var fullyProduced = fresh(n(10));
        UUID fullToken = fullyProduced.beginBatch(10);
        check(fullyProduced.finish(fullToken, false, n(10))
                && fullyProduced.snapshot().state() == Hk3ExactOrder.State.COMPLETE,
                "失败回执确认全量已产出时不再重发已满足的订单");
    }

    private static void pauseAndCancel() {
        var paused = fresh(n(10));
        UUID token = paused.beginBatch(4);
        check(paused.pause() && paused.snapshot().activeToken().equals(token), "暂停保留真实在途令牌");
        check(!paused.resume(), "在途未知时不得恢复发新批");
        check(paused.finish(token, true) && paused.snapshot().completed().equals(n(4)), "暂停期间真实成功仍计数");
        check(paused.snapshot().state() == Hk3ExactOrder.State.PAUSED && paused.resume(), "回执后仍保持暂停意图");
        check(paused.pause() && !paused.pause() && paused.snapshot().state() == Hk3ExactOrder.State.PAUSED, "重复暂停不破坏状态");

        var cancelled = fresh(n(10));
        UUID running = cancelled.beginBatch(4);
        check(cancelled.cancel() && cancelled.snapshot().activeToken().equals(running), "取消保留令牌供外层取消CPU");
        check(!cancelled.resume() && !cancelled.pause() && !cancelled.cancel(), "取消状态不能自动复活");
        check(cancelled.finish(running, true) && cancelled.snapshot().completed().equals(n(4)), "取消竞态下真实成功必须计数");
        check(cancelled.snapshot().state() == Hk3ExactOrder.State.CANCELLED && cancelled.snapshot().activeToken() == null, "成功回执不复活已取消订单");
        check(!cancelled.finish(running, true), "取消后的重复回执仍拒绝");

        var failed = fresh(n(3));
        UUID failedToken = failed.beginBatch(3);
        failed.cancel();
        check(failed.finish(failedToken, false) && failed.snapshot().state() == Hk3ExactOrder.State.CANCELLED
                && failed.snapshot().completed().signum() == 0, "取消失败回执不倒退到可恢复状态");
    }

    private static void restoreAndValidation() {
        var original = fresh(n(10));
        UUID active = original.beginBatch(3);
        var restored = Hk3ExactOrder.restore(original.snapshot());
        check(restored.snapshot().state() == Hk3ExactOrder.State.PAUSED, "恢复运行任务强制暂停");
        check(restored.snapshot().activeToken().equals(active) && !restored.resume(), "恢复后保留未知在途且禁止重发");
        check(restored.finish(active, true) && restored.snapshot().completed().equals(n(3)), "真实恢复回执可核销原批次");
        check(restored.snapshot().state() == Hk3ExactOrder.State.PAUSED && restored.resume(), "恢复回执后仍需明确恢复");
        var ready = Hk3ExactOrder.restore(fresh(n(1)).snapshot());
        check(ready.snapshot().state() == Hk3ExactOrder.State.PAUSED && ready.resume(), "保存的就绪状态也先暂停");
        var complete = fresh(n(1));
        complete.finish(complete.beginBatch(1), true);
        check(Hk3ExactOrder.restore(complete.snapshot()).snapshot().state() == Hk3ExactOrder.State.COMPLETE, "完成态恢复保持");
        var cancelled = fresh(n(2));
        UUID cancellationToken = cancelled.beginBatch(1);
        cancelled.cancel();
        var cancelledRestore = Hk3ExactOrder.restore(cancelled.snapshot());
        check(cancelledRestore.snapshot().state() == Hk3ExactOrder.State.CANCELLED
                && cancelledRestore.snapshot().activeToken().equals(cancellationToken), "取消态及其在途恢复保持");

        invalid(() -> fresh(BigInteger.ZERO));
        invalid(() -> fresh(BigInteger.TEN.pow(256)));
        UUID id = UUID.randomUUID(), owner = UUID.randomUUID(), token = UUID.randomUUID();
        invalidRestore(id, owner, n(10), n(-1), n(0), null, Hk3ExactOrder.State.PAUSED);
        invalidRestore(id, owner, n(10), n(11), n(0), null, Hk3ExactOrder.State.PAUSED);
        invalidRestore(id, owner, n(10), n(8), n(3), token, Hk3ExactOrder.State.PAUSED);
        invalidRestore(id, owner, n(10), n(0), n(1), null, Hk3ExactOrder.State.PAUSED);
        invalidRestore(id, owner, n(10), n(0), n(0), token, Hk3ExactOrder.State.PAUSED);
        invalidRestore(id, owner, n(10), n(0), n(1), token, Hk3ExactOrder.State.READY);
        invalidRestore(id, owner, n(10), n(0), n(0), null, Hk3ExactOrder.State.RUNNING);
        invalidRestore(id, owner, n(10), n(9), n(0), null, Hk3ExactOrder.State.COMPLETE);
        invalidRestore(id, owner, n(10), n(10), n(0), null, Hk3ExactOrder.State.PAUSED);
        check(restored.snapshot().orderId().equals(original.snapshot().orderId())
                && restored.snapshot().owner().equals(original.snapshot().owner()), "恢复保留订单及归属身份");
    }

    private static void concurrentReceipt() throws Exception {
        var order = fresh(n(10));
        UUID token = order.beginBatch(7);
        AtomicInteger accepted = new AtomicInteger();
        CountDownLatch start = new CountDownLatch(1);
        Runnable receipt = () -> {
            try { start.await(); if (order.finish(token, true)) accepted.incrementAndGet(); }
            catch (InterruptedException e) { Thread.currentThread().interrupt(); }
        };
        Thread first = new Thread(receipt), second = new Thread(receipt);
        first.start(); second.start(); start.countDown();
        first.join(5000); second.join(5000);
        check(!first.isAlive() && !second.isAlive(), "并发回执不死锁");
        check(accepted.get() == 1 && order.snapshot().completed().equals(n(7)), "并发重复回执只计数一次");
    }

    private static void invalidRestore(UUID id, UUID owner, BigInteger total, BigInteger completed,
                                       BigInteger active, UUID token, Hk3ExactOrder.State state) {
        invalid(() -> Hk3ExactOrder.restore(new Hk3ExactOrder.Snapshot(id, owner, total, completed, active, token, state)));
    }
    private static Hk3ExactOrder fresh(BigInteger total) { return new Hk3ExactOrder(UUID.randomUUID(), UUID.randomUUID(), total); }
    private static BigInteger n(long value) { return BigInteger.valueOf(value); }
    private static void invalid(Runnable action) {
        try { action.run(); throw new AssertionError("应拒绝无效数量或状态"); }
        catch (IllegalArgumentException expected) { checks++; }
    }
    private static void illegalState(Runnable action) {
        try { action.run(); throw new AssertionError("应拒绝当前状态操作"); }
        catch (IllegalStateException expected) { checks++; }
    }
    private static void check(boolean ok, String reason) {
        if (!ok) throw new AssertionError(reason);
        checks++;
    }
}
