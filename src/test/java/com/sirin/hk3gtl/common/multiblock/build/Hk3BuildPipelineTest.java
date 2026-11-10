package com.sirin.hk3gtl.common.multiblock.build;

import java.util.*;
import java.util.concurrent.*;

/** 并行任务保序、有界缓存、异常与取消；进度跨阈值只通知十次。 */
public final class Hk3BuildPipelineTest {
    public static void main(String[] args)throws Exception {
        ExecutorService pool=Executors.newFixedThreadPool(3);
        try {
            CountDownLatch active=new CountDownLatch(3),release=new CountDownLatch(1);
            Set<String> threads=ConcurrentHashMap.newKeySet();String caller=Thread.currentThread().getName();
            try(var queue=new Hk3BuildPipeline<>(9000,i->{
                threads.add(Thread.currentThread().getName());
                if(i%Hk3BuildPipeline.BATCH_SIZE==0 && i<6144) {
                    active.countDown();
                    try {if(!release.await(5,TimeUnit.SECONDS))throw new AssertionError("并行测试释放超时");}
                    catch(InterruptedException failure){throw new CancellationException();}
                }
                return i;
            },pool,4)) {
                check(queue.peek()==null,"服务器不能等待准备中的批次");
                check(active.await(5,TimeUnit.SECONDS),"至少三个批次实际并发");release.countDown();
                check(threads.size()==3&&!threads.contains(caller),"只能由后台线程读取蓝图");
                check(queue.bufferedLimit()==5*2048,"缓存与建筑总大小无关");
                long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(10);
                int next=0;
                while(next<9000 && System.nanoTime()<deadline) {
                    Integer value=queue.peek();
                    if(value==null){Thread.sleep(1);continue;}
                    check(value==next++&&queue.peek().equals(value),"并行完成顺序不能改变提交顺序");queue.advance();
                }
                check(next==9000&&queue.peek()==null,"末尾不足一批仍完整交付");
            }
            try(var failed=new Hk3BuildPipeline<Integer>(1,i->{throw new IllegalArgumentException("坏蓝图");},pool,1)) {
                boolean caught=false;
                for(int i=0;i<1000&&!caught;i++)try {failed.peek();Thread.sleep(1);}
                catch(CompletionException expected){caught=expected.getCause() instanceof IllegalArgumentException;}
                check(caught,"后台错误必须交还主线程处理");
            }
            CountDownLatch entered=new CountDownLatch(1),interrupted=new CountDownLatch(1);
            var cancelled=new Hk3BuildPipeline<Integer>(1,i->{
                entered.countDown();
                try{new CountDownLatch(1).await();}catch(InterruptedException expected){interrupted.countDown();}
                return i;
            },pool,1);
            cancelled.peek();check(entered.await(5,TimeUnit.SECONDS),"取消测试启动失败");cancelled.close();
            check(interrupted.await(5,TimeUnit.SECONDS)&&cancelled.peek()==null,"取消必须中断工作并丢弃结果");
        }finally {pool.shutdownNow();}
        var progress=new Hk3BuildProgress();List<Integer> sent=new ArrayList<>();
        for(int i:new int[]{0,1,9,10,10,35,35,99,100,100})progress.report(i,100,sent::add);
        check(sent.equals(List.of(10,20,30,40,50,60,70,80,90,100)),"进度恰好十次且不重复");
        check(Hk3BuildProgress.percent(Integer.MAX_VALUE,Integer.MAX_VALUE)==100,"大蓝图百分比不得溢出");
        check(Hk3W01BuildBudget.nanos(2,8)==12_000_000L,"空闲时不再固定限速四毫秒");
        check(Hk3W01BuildBudget.nanos(49,50)==1_000_000L,"低帧及服务器繁忙必须降速");
        check(Hk3W01BuildBudget.placementLimit(8)>Hk3W01BuildBudget.placementLimit(50),"客户端压力必须降低提交上限");
        System.out.println("并行保序、有界缓存、取消、异常、十次百分比与自适应预算通过；未测游戏实际速度。");
    }
    private static void check(boolean ok,String message){if(!ok)throw new AssertionError(message);}
}
