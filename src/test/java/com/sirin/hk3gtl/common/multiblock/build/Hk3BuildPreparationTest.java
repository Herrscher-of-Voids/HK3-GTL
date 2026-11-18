package com.sirin.hk3gtl.common.multiblock.build;

import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

/** 验证后台交接、取消中输入不被抢关、异常传播及清理次数；不写游戏世界。 */
public final class Hk3BuildPreparationTest {
    public static void main(String[] args) throws Exception {
        Thread caller=Thread.currentThread();
        AtomicInteger decoded=new AtomicInteger(),closed=new AtomicInteger();
        var job=new Hk3BuildPreparation(() -> {
            check(Thread.currentThread()!=caller,"解码必须在后台线程");
            return decoded.incrementAndGet()==100_000;
        },() -> {
            check(Thread.currentThread()!=caller,"排序必须在后台线程");
            return new Hk3BuildOrder(4,2,0,i -> i%2,i -> 0);
        },closed::incrementAndGet);
        await(job);
        var order=job.finish();
        check(order.index(0)==0&&order.index(1)==2&&order.index(2)==1&&order.index(3)==3,"交接必须给出完整稳定索引");
        check(decoded.get()==100_000&&closed.get()==1,"交接前完成全部解码并关闭输入");
        job.close();check(closed.get()==1,"完成后取消不得二次清理");

        CountDownLatch entered=new CountDownLatch(1),resume=new CountDownLatch(1);
        AtomicInteger cancelClosed=new AtomicInteger();
        var cancelled=new Hk3BuildPreparation(() -> {
            entered.countDown();
            try {check(resume.await(5,TimeUnit.SECONDS),"测试释放超时");}
            catch(InterruptedException failure){throw new RuntimeException(failure);}
            check(cancelClosed.get()==0,"取消不能抢先关闭后台正在读取的输入");
            return false;
        },() -> {throw new AssertionError("取消后不得排序");},cancelClosed::incrementAndGet);
        check(entered.await(5,TimeUnit.SECONDS),"后台任务未启动");
        cancelled.close();
        check(cancelClosed.get()==0&&!cancelled.done(),"取消必须立即返回并由后台收尾");
        resume.countDown();await(cancelled);
        try {cancelled.finish();throw new AssertionError("取消必须传播");}
        catch(CancellationException expected) { }
        check(cancelClosed.get()==1,"取消只清理一次");

        AtomicInteger failedClosed=new AtomicInteger();
        var failed=new Hk3BuildPreparation(() -> {throw new IllegalArgumentException("损坏蓝图");},
                () -> {throw new AssertionError("失败后不得排序");},failedClosed::incrementAndGet);
        await(failed);
        try {failed.finish();throw new AssertionError("解码异常必须传播");}
        catch(CompletionException expected){check(expected.getCause() instanceof IllegalArgumentException,"保留原异常");}
        check(failedClosed.get()==1,"失败只清理一次");
        System.out.println("后台蓝图准备、排序交接、取消与失败清理通过；未执行客户端搭建测试。");
    }
    private static void await(Hk3BuildPreparation task) throws Exception {
        long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(10);
        while(!task.done()&&System.nanoTime()<deadline)Thread.sleep(1);
        check(task.done(),"后台任务超时");
    }
    private static void check(boolean ok,String message){if(!ok)throw new AssertionError(message);}
}
