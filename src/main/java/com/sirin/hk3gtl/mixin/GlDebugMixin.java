package com.sirin.hk3gtl.mixin;

/**
 * 【文件职责】
 * - 抑制 Re-Avaritia 宇宙着色器每帧触发的 GL_INVALID_OPERATION(id=1282) 调试刷屏。
 * - 关键调用链：OpenGL 驱动调试回调 -> GlDebug.printDebugLog -> 本 Mixin 拦截特定重复消息。
 *
 * 【变更记录 #1】2026-05-31 20:24:00（第 1 次备注 · 内测二第 9 次更新）
 * - 删除：
 *   1) 无。本文件为新增。
 * - 新增：
 *   1) 新增 GlDebugMixin，对 GlDebug.printDebugLog 注入 HEAD 拦截。
 *   2) 仅针对 id=1282 且文本为 "GL_INVALID_OPERATION error generated. Wrong component type or count."
 *      的这一条 Re-Avaritia 宇宙着色器重复消息：首条放行保留来源线索，之后去重，每 10s 汇总一次抑制次数。
 *   3) 其它任何 GL 调试消息一律放行，不影响真实问题排查。
 * - 修改：
 *   1) 无。
 * - 用途：
 *   1) 作为「方案 B（保留星空特效、仅去日志噪声）」的实现。
 *   2) 关键风险点：printDebugLog 在渲染线程被高频调用，逻辑必须极轻量；
 *      计数用 AtomicLong、标志位用 volatile，避免跨帧竞态。
 *
 * 【变更记录 #2】2026-05-31 21:28:00（第 2 次备注 · 内测二第 10 次更新）
 * - 修改：
 *   1) 正式启用本 Mixin：已加入 hk3gtl.mixins.json 的 client 列表（采用方案 B）。
 *   2) 同步保留 AvaritiaShaderMixin / CosmicBakeModelMixin 源码（方案 A 备用，未注册），便于随时回切。
 * - 用途：
 *   1) 方案 B = 维持 AvaritiaCCShaderInstanceMixin 星空修复（不引入无尽护甲 NPE）+ 本 Mixin 抑制 dev 端 GL 刷屏。
 *   2) 注意：本 Mixin 仅作用于开发环境的 GlDebug 回调；生产环境默认不开 GL 调试，testers 日志本无此刷屏。
 *
 * 【变更记录 #3】2026-05-31 23:05:00（第 3 次备注 · 内测三第 3 次更新，崩溃热修）
 * - 删除：
 *   1) @Mixin 上的 remap = false。
 *   2) 原因：GlDebug 是 Mojang 原版类，printDebugLog 在生产(SRG 混淆)环境会被改名；remap=false 导致运行时按字面名
 *      查找失败 → "could not find any targets matching 'printDebugLog'" → Mixin APPLY 崩溃，整个客户端无法启动。
 *   3) 影响：仅本 Mixin 的目标解析方式；行为逻辑不变。
 * - 修改：
 *   1) @Mixin(value = GlDebug.class, remap = false) → @Mixin(GlDebug.class)（remap 取默认 true）。
 *   2) 效果：构建时 Mixin AP 将 printDebugLog 写入 refmap → SRG 名，开发与生产环境均可正确解析、不再崩溃。
 * - 用途：
 *   1) 修复内测三生产环境(Prism 启动)因本 Mixin 注入失败导致的致命崩溃。
 *   2) 说明：项目「全部 remap=false」规则仅针对 GT/联动模组(无 Mojang 映射)；Mojang 原版类必须 remap=true，本类属此例外。
 *
 * 【段内说明】
 * - hk3gtl$throttleCosmicSpam：先按 id 与文本双重匹配过滤，命中后首条放行、其余 cancel。
 *
 * 【变更记录 #4】2026-07-19 21:49:23（第 4 次备注 · revision 35）
 * - 删除：
 *   1) 删除本地 HTTP 调试上报的 URI、HttpClient、HttpRequest、HttpResponse 字段与导入。
 *   2) 删除首条 GL 错误上报 JSON、sendAsync 调用及 debug-point E 区块；不再向 127.0.0.1:7777 发送生产运行数据。
 * - 新增：
 *   1) 无新增生产功能；保留既有 GL 日志抑制与每 10 秒汇总日志。
 * - 修改：
 *   1) 首次命中逻辑由“上报后放行”改为直接放行，后续仍按原条件计数、汇总并取消重复消息。
 *   2) 修改范围仅限调试上报副作用，GL_INVALID_OPERATION 过滤条件和线程安全计数逻辑不变。
 * - 用途：
 *   1) 移除生产代码中的本地网络调试通道，避免渲染线程产生外部 HTTP 请求。
 *   2) 保持 GlDebug.printDebugLog 的无害重复消息抑制能力，不影响其他 GL 日志。
 */
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

    /** 中文说明：该处说明已按当前代码行为整理。*/
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
