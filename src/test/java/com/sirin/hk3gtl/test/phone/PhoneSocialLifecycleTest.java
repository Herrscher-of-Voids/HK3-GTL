package com.sirin.hk3gtl.test.phone;

import com.sirin.hk3gtl.client.phone.Hk3SocialAiClient;
import com.sirin.hk3gtl.common.phone.Hk3SocialCatalog;
import com.sun.net.httpserver.HttpServer;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * 【变更记录 #1】2026-10-01 22:07:52（第1次备注 · 内测5修订154）
 * 删除：无。新增：接口切换、配置拒绝原子性、请求取消及迟到回复隔离回归。
 * 修改：使用本机服务和显式假Key，不访问真实服务。用途：核验整段客户端通信生命周期。
 */
public final class PhoneSocialLifecycleTest {
    private static int checks;
    private static void check(boolean value,String why) {
        if(!value)throw new AssertionError(why);checks++;
    }
    public static void run() throws Exception {
        Hk3SocialAiClient.reset();
        check(Hk3SocialAiClient.configure("https://example.com/v1","model-a","fake-key-a").isEmpty(),"初次配置");
        check(Hk3SocialAiClient.configure("https://example.com/v1/","model-b","").isEmpty(),"同接口规范化后保留Key");
        String original=Hk3SocialAiClient.endpoint();int epoch=Hk3SocialAiClient.epoch();
        for(String address:List.of("https://another.example/v1","https://example.com:8443/v1","https://example.com/v2")) {
            check(!Hk3SocialAiClient.configure(address,"model-c","").isEmpty(),"换接口禁止复用旧Key");
            check(Hk3SocialAiClient.endpoint().equals(original)&&Hk3SocialAiClient.model().equals("model-b")
                    &&Hk3SocialAiClient.epoch()==epoch,"拒绝配置不部分覆盖也不取消现有会话");
        }
        check(Hk3SocialAiClient.configure("https://another.example/v1","model-c","fake-key-c").isEmpty(),"显式新Key允许更换接口");
        Hk3SocialAiClient.reset();
        check(!Hk3SocialAiClient.configured()&&Hk3SocialAiClient.endpoint().isEmpty()&&Hk3SocialAiClient.model().isEmpty(),"退出清空所有配置");
        check(!Hk3SocialAiClient.configure("https://another.example/v1","model-c","").isEmpty(),"退出后不能复用Key");

        var entered=new CountDownLatch(1);var release=new CountDownLatch(1);var finished=new CountDownLatch(1);
        var calls=new AtomicInteger();var executor=Executors.newCachedThreadPool();
        var server=HttpServer.create(new InetSocketAddress("127.0.0.1",0),0);server.setExecutor(executor);
        server.createContext("/slow/chat/completions",exchange->{
            calls.incrementAndGet();exchange.getRequestBody().readAllBytes();entered.countDown();
            try {
                release.await(10,TimeUnit.SECONDS);
                byte[] response="{\"choices\":[{\"message\":{\"content\":\"迟到的回复\"}}]}".getBytes(StandardCharsets.UTF_8);
                exchange.sendResponseHeaders(200,response.length);exchange.getResponseBody().write(response);
            } catch(InterruptedException ex) {Thread.currentThread().interrupt();}
              catch(java.io.IOException ignored) { /* 取消请求后连接已关闭，属于预期行为。 */ }
            finally {exchange.close();finished.countDown();}
        });
        server.start();
        try {
            String base="http://127.0.0.1:"+server.getAddress().getPort()+"/slow";
            check(Hk3SocialAiClient.configure(base,"local-test","fake-key-local").isEmpty(),"本机配置");
            int requestEpoch=Hk3SocialAiClient.epoch();
            var pending=Hk3SocialAiClient.send(Hk3SocialCatalog.get("V01"),"你好",List.of());
            check(entered.await(5,TimeUnit.SECONDS)&&Hk3SocialAiClient.busy(),"请求实际到达且忙碌");
            check(!Hk3SocialAiClient.send(Hk3SocialCatalog.get("V02"),"你好",List.of()).get().ok(),"其他角色不能重复发送在途请求");
            Hk3SocialAiClient.reset();
            check(Hk3SocialAiClient.epoch()!=requestEpoch&&!Hk3SocialAiClient.busy()&&!Hk3SocialAiClient.configured(),"取消后旧epoch失效且释放请求");
            release.countDown();
            boolean cancelled=false;
            // HTTP取消也可能被错误处理层转成失败Result；两种路径都不得产生成功回复。
            try {cancelled=!pending.get(5,TimeUnit.SECONDS).ok();} catch(CancellationException|ExecutionException expected) {cancelled=true;}
            check(cancelled,"迟到回复不能返回正常角色消息");
            check(finished.await(5,TimeUnit.SECONDS)&&calls.get()==1,"取消不自动重试也不重复收费请求");
        } finally {
            release.countDown();Hk3SocialAiClient.reset();server.stop(0);executor.shutdownNow();
        }
        System.out.println("Phone social lifecycle: "+checks+" checks passed; local mock only");
    }
}
