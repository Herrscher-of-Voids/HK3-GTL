package com.sirin.hk3gtl.mixin;


import com.mojang.blaze3d.platform.GlDebug;
import org.lwjgl.opengl.GLDebugMessageCallback;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import java.util.concurrent.atomic.AtomicLong;

/**
 * 抑制 Re-Avaritia 宇宙着色器每帧触发的 GL_INVALID_OPERATION(id=1282) 调试刷屏。
 *
 * <p><b>目标类</b>：{@code com.mojang.blaze3d.platform.GlDebug}（Mojang 原版类，需 {@code remap = true}，
 * 否则生产环境 SRG 名解析失败导致 Mixin APPLY 崩溃）。
 *
 * <p><b>行为</b>：仅拦截一条特定重复消息——首条照常打印，后续去重，并每 10s 汇总一次抑制次数；
 * 其它 GL 调试消息全部放行。
 */
@Mixin(GlDebug.class)
public class GlDebugMixin {

    private static final Logger HK3GTL$LOGGER = LoggerFactory.getLogger("hk3gtl-gldebug");

    /** Re-Avaritia 宇宙着色器每帧产生的无害 GL 错误文本（id=1282）。 */
    private static final String HK3GTL$COSMIC_MSG =
            "GL_INVALID_OPERATION error generated. Wrong component type or count.";
    private static final long HK3GTL$SUMMARY_INTERVAL_MS = 10_000L;

    private static final AtomicLong hk3gtl$suppressed = new AtomicLong();
    private static volatile boolean hk3gtl$loggedOnce = false;
    private static volatile long hk3gtl$lastSummaryAt = 0L;

    /**
     * Hook：{@code GlDebug#printDebugLog}（GL 调试回调，渲染线程高频调用）。
     * 边界：仅当 id=1282 且文本完全匹配时介入，其余立即返回放行。
     * 安全点：渲染线程单线程触发，计数用 AtomicLong/volatile 兜底跨帧可见性。
     */
    @Inject(method = "printDebugLog", at = @At("HEAD"), cancellable = true)
    private static void hk3gtl$throttleCosmicSpam(int source, int type, int id, int severity,
                                                  int length, long message, long userParam,
                                                  CallbackInfo ci) {
        if (id != 1282) {
            return;
        }
        String decodedMessage = GLDebugMessageCallback.getMessage(length, message);
        if (!HK3GTL$COSMIC_MSG.equals(decodedMessage)) {
            return;
        }
        if (!hk3gtl$loggedOnce) {
            hk3gtl$loggedOnce = true;
            hk3gtl$lastSummaryAt = System.currentTimeMillis();
            return; // 首条放行，保留来源线索
        }
        long count = hk3gtl$suppressed.incrementAndGet();
        long now = System.currentTimeMillis();
        if (now - hk3gtl$lastSummaryAt >= HK3GTL$SUMMARY_INTERVAL_MS) {
            hk3gtl$lastSummaryAt = now;
            HK3GTL$LOGGER.info("[HK3GTL] 已抑制 Re-Avaritia 宇宙着色器重复 GL 警告 {} 次", count);
        }
        ci.cancel();
    }
}
