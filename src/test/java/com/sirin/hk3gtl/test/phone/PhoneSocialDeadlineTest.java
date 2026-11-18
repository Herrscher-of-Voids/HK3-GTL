package com.sirin.hk3gtl.test.phone;

import com.sirin.hk3gtl.client.phone.Hk3SocialAiClient;
import com.sirin.hk3gtl.common.phone.Hk3SocialCatalog;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

/** 使用真实45秒期限及本机假凭据，验证完整正文期限、忙碌释放和HTTP传输取消。 */
public final class PhoneSocialDeadlineTest {
    private static final String KEY = "deadline-test-only-fake-key";
    private static final String TEXT = "研究失败的那一步，可以慢慢说。";
    private static final byte[] REPLY = ("{\"choices\":[{\"message\":{\"content\":\"" + TEXT + "\"}}]}")
            .getBytes(StandardCharsets.UTF_8);
    private static int checks;

    public static void main(String[] args) throws Exception {
        Hk3SocialAiClient.reset();
        try (var fixture = new Fixture()) {
            deadlines(fixture);
            explicitCancellation(fixture);
            check(fixture.failure.get() == null, "本机HTTP处理器无隐藏失败");
        } finally {
            Hk3SocialAiClient.reset();
        }
        System.out.println("社交AI响应期限：" + checks + "项检查通过");
    }

    private static void deadlines(Fixture fixture) throws Exception {
        var contact = Hk3SocialCatalog.get("V01");
        check(Hk3SocialAiClient.configure(fixture.base("stall"), "local-deadline-test", KEY).isEmpty(), "本机假凭据配置");
        long start = System.nanoTime();
        var stall = Hk3SocialAiClient.send(contact, "你好", List.of());
        var stallDone = new AtomicLong();
        var stallObserved = stall.whenComplete((value, error) -> stallDone.set(System.nanoTime()));
        var drip = Hk3SocialAiClient.request(URI.create(fixture.base("drip") + "/chat/completions"), KEY,
                Hk3SocialAiClient.payload("local-deadline-test", contact, "你好", List.of()));
        var dripDone = new AtomicLong();
        var dripObserved = drip.whenComplete((value, error) -> dripDone.set(System.nanoTime()));
        check(fixture.stall.headers.await(5, TimeUnit.SECONDS) && fixture.drip.headers.await(5, TimeUnit.SECONDS),
                "两路真实送出200及首字节，不只记录服务端准备状态");
        check(Hk3SocialAiClient.busy(), "send在响应体未完成时保持忙碌");
        check(!Hk3SocialAiClient.send(contact, "你好", List.of()).get(1, TimeUnit.SECONDS).ok(), "在途请求禁止重复发送");
        CompletableFuture.allOf(stallObserved, dripObserved).get(60, TimeUnit.SECONDS);
        var stalled = stall.get();
        var dripped = drip.get();
        check(!stalled.ok() && !dripped.ok(), "停滞与持续慢滴正文均按总期限失败");
        double stallSeconds = (stallDone.get() - start) / 1_000_000_000.0;
        double dripSeconds = (dripDone.get() - start) / 1_000_000_000.0;
        check(stallSeconds >= 44 && stallSeconds <= 60, "停滞请求使用真实45秒而非缩短测试参数");
        check(dripSeconds >= 44 && dripSeconds <= 60, "慢滴流量不能重置完整响应期限");
        check(fixture.drip.bytes.get() > 10 && fixture.drip.bytes.get() < 131072, "慢滴已实际持续且未触发128KiB上限");
        check(!Hk3SocialAiClient.busy() && Hk3SocialAiClient.configured(), "期限到达释放忙碌并保留配置");
        var next = Hk3SocialAiClient.send(contact, "你好", List.of()).get(5, TimeUnit.SECONDS);
        check(next.ok() && next.text().equals(contact.finish(TEXT)), "无需重配或手动取消即可再次发送成功");
        check(!Hk3SocialAiClient.busy(), "后续正常请求完成后释放忙碌");
        fixture.stall.release.countDown();
        fixture.drip.release.countDown();
        awaitClosed(fixture.stall, "停滞响应超时传递到真实HTTP传输");
        awaitClosed(fixture.drip, "慢滴响应超时传递到真实HTTP传输");
        check(!stall.get().ok() && !drip.get().ok(), "服务端迟到有效正文不能改成成功回复");
        check(fixture.stall.calls.get() == 2 && fixture.drip.calls.get() == 1, "仅原请求与显式后续请求，没有自动重试");
        System.out.printf(java.util.Locale.ROOT,
                "响应壁钟：停滞%.3fs，慢滴%.3fs；慢滴发送%d字节；仅本机假凭据%n",
                stallSeconds, dripSeconds, fixture.drip.bytes.get());
    }

    private static void explicitCancellation(Fixture fixture) throws Exception {
        check(Hk3SocialAiClient.configure(fixture.base("client-cancel"), "local-deadline-test", KEY).isEmpty(), "取消场景本机配置");
        int epoch = Hk3SocialAiClient.epoch();
        var send = Hk3SocialAiClient.send(Hk3SocialCatalog.get("V01"), "你好", List.of());
        check(fixture.clientCancel.headers.await(5, TimeUnit.SECONDS) && Hk3SocialAiClient.busy(), "显式取消前已收到响应首字节");
        Hk3SocialAiClient.cancel();
        check(Hk3SocialAiClient.epoch() != epoch && !Hk3SocialAiClient.busy(), "显式客户端取消释放忙碌及旧代次");
        check(failedOrCancelled(send), "客户端取消不得返回成功角色消息");
        fixture.clientCancel.release.countDown();
        awaitClosed(fixture.clientCancel, "客户端取消传至HTTP传输");

        var direct = Hk3SocialAiClient.request(URI.create(fixture.base("direct-cancel") + "/chat/completions"), KEY, "{}");
        check(fixture.directCancel.headers.await(5, TimeUnit.SECONDS), "直接取消前已收到响应首字节");
        check(!direct.isDone(), "直接取消前请求仍在途，不接受事先网络失败");
        boolean cancelled = direct.cancel(true);
        // JDK MinimalFuture先取消底层，exceptionally可能同步把终态转换为失败Result。
        check(cancelled && direct.isDone() && failedOrCancelled(direct), "直接返回future显式取消后仅允许失败或取消终态");
        System.out.printf("显式取消：future=%s，cancel=%s，isCancelled=%s，isDone=%s%n",
                direct.getClass().getName(), cancelled, direct.isCancelled(), direct.isDone());
        fixture.directCancel.release.countDown();
        awaitClosed(fixture.directCancel, "直接future取消传至HTTP传输");
        check(fixture.clientCancel.calls.get() == 1 && fixture.directCancel.calls.get() == 1, "取消不自动重试");
    }

    private static boolean failedOrCancelled(CompletableFuture<Hk3SocialAiClient.Result> future) throws Exception {
        try { return !future.get(5, TimeUnit.SECONDS).ok(); }
        catch (CancellationException | ExecutionException expected) { return true; }
    }

    private static void awaitClosed(Route route, String reason) throws InterruptedException {
        check(route.finished.await(5, TimeUnit.SECONDS), "本机挂起处理器及时释放");
        check(route.disconnected.get(), reason);
        check(route.bytes.get() < 131072, "关闭观察写入总量低于128KiB，排除体积限制取消假阳性");
    }

    private static final class Fixture implements AutoCloseable {
        private final AtomicReference<Throwable> failure = new AtomicReference<>();
        private final ExecutorService executor = Executors.newCachedThreadPool();
        private final HttpServer server;
        private final Route stall = new Route(this, false, true);
        private final Route drip = new Route(this, true, false);
        private final Route clientCancel = new Route(this, false, false);
        private final Route directCancel = new Route(this, false, false);

        private Fixture() throws IOException {
            server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
            server.setExecutor(executor);
            server.createContext("/stall/chat/completions", stall::handle);
            server.createContext("/drip/chat/completions", drip::handle);
            server.createContext("/client-cancel/chat/completions", clientCancel::handle);
            server.createContext("/direct-cancel/chat/completions", directCancel::handle);
            server.start();
        }

        private String base(String path) { return "http://127.0.0.1:" + server.getAddress().getPort() + "/" + path; }

        @Override public void close() throws InterruptedException {
            for (var route : List.of(stall, drip, clientCancel, directCancel)) route.release.countDown();
            Hk3SocialAiClient.reset();
            server.stop(0);
            executor.shutdownNow();
            check(executor.awaitTermination(5, TimeUnit.SECONDS), "HTTP夹具线程已清理");
        }
    }

    private static final class Route {
        private final Fixture fixture;
        private final boolean drip, followup;
        private final AtomicInteger calls = new AtomicInteger(), bytes = new AtomicInteger();
        private final CountDownLatch headers = new CountDownLatch(1), release = new CountDownLatch(1), finished = new CountDownLatch(1);
        private final AtomicBoolean disconnected = new AtomicBoolean();

        private Route(Fixture fixture, boolean drip, boolean followup) {
            this.fixture = fixture; this.drip = drip; this.followup = followup;
        }

        private void handle(HttpExchange exchange) {
            int call = calls.incrementAndGet();
            try {
                if (!("Bearer " + KEY).equals(exchange.getRequestHeaders().getFirst("Authorization")))
                    throw new AssertionError("只允许显式假Key");
                exchange.getRequestBody().readAllBytes();
                if (followup && call > 1) {
                    exchange.sendResponseHeaders(200, REPLY.length);
                    exchange.getResponseBody().write(REPLY);
                    return;
                }
                exchange.sendResponseHeaders(200, 0);
                var output = exchange.getResponseBody();
                output.write(' '); output.flush(); bytes.incrementAndGet(); headers.countDown();
                if (drip) {
                    while (!release.await(250, TimeUnit.MILLISECONDS)) {
                        output.write(' '); output.flush(); bytes.incrementAndGet();
                    }
                } else if (!release.await(70, TimeUnit.SECONDS)) {
                    throw new AssertionError("本机挂起响应未释放");
                }
                output.write(REPLY); output.flush(); bytes.addAndGet(REPLY.length);
                // 少量空白仍是有效JSON尾部；正常传输不会触发体积限制。
                var probe = new byte[64]; java.util.Arrays.fill(probe, (byte) ' ');
                for (int i = 0; i < 20; i++) {
                    output.write(probe); output.flush(); bytes.addAndGet(probe.length);
                    Thread.sleep(25);
                }
            } catch (IOException expectedCancellation) {
                disconnected.set(true);
            } catch (Throwable error) {
                fixture.failure.compareAndSet(null, error);
                if (error instanceof InterruptedException) Thread.currentThread().interrupt();
            } finally {
                exchange.close();
                if (!(followup && call > 1)) finished.countDown();
            }
        }
    }

    private static void check(boolean value, String reason) {
        checks++;
        if (!value) throw new AssertionError(reason);
    }
}
