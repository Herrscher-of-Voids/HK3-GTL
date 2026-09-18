package com.sirin.hk3gtl.mixin;



import com.mojang.logging.LogUtils;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * GTLAdditions SkyTearsAndGregHeart 初始化跳过 Mixin（dev 环境兼容）。
 *
 * <p><b>目标类</b>：{@code com.gtladd.gtladditions.common.modify.SkyTearsAndGregHeart}
 * （GTLAdditions 附属模组的初始化类，负责在运行时给部分 GTCEu 对象注入"天泪"与"GT 之心"
 * 相关的自定义数据）。
 *
 * <p><b>注入目的</b>：该类的 {@code init()} 在运行期会遍历一些"外部模组必定存在"的数据，
 * 在开发环境（dev/部分模组未完整加载）下这些依赖可能缺失，导致
 * {@link ArrayIndexOutOfBoundsException}，整个客户端启动终止。
 * 因项目本身并不依赖 GTLAdditions 的这个特性，直接跳过其 init 最省事。
 *
 * <p><b>失效后影响</b>：
 * <ul>
 *   <li>dev 环境游戏启动阶段 AIOOBE，客户端无法进入游戏。</li>
 *   <li>生产环境若 GTLAdditions 存在但数据不完整，同样会崩。</li>
 * </ul>
 *
 * <p><b>修改指南</b>：
 * <ul>
 *   <li>{@link Pseudo} + {@code require = 0}：保证 GTLAdditions 未加载时本 Mixin
 *       静默失效，不会反向影响游戏。</li>
 *   <li>如果后续需要启用 GTLAdditions 的该功能：
 *       <ol>
 *         <li>确认运行环境中依赖数据完整；</li>
 *         <li>删除本 Mixin（连同 mixins.json 的引用）；</li>
 *         <li>dev 环境回归测试。</li>
 *       </ol></li>
 *   <li>不要改成"条件跳过"（比如判断某模组是否加载），该类抛的是数组越界，判断条件
 *       成本高且难维护。整体跳过对本项目无副作用。</li>
 *   <li>{@code remap = false}（第三方模组类）。</li>
 * </ul>
 */
@Pseudo
@Mixin(targets = "com.gtladd.gtladditions.common.modify.SkyTearsAndGregHeart", remap = false)
public class SkyTearsAndGregHeartMixin {

    /**
     * Hook 位置：{@code SkyTearsAndGregHeart#init}（实例方法，由 GTLAdditions 在启动期调用）。
     * <br>Hook 时机：{@code @At("HEAD")} + {@code cancellable = true} —— 入口处立即取消，
     * 彻底跳过原 init 内部的危险数组操作。
     * <br>日志：打印 warn 级别的提示，方便玩家/开发者在日志里确认 Mixin 生效。
     */
    @Inject(method = "init", at = @At("HEAD"), cancellable = true, require = 0)
    private void hk3gtl$skipInit(CallbackInfo ci) {
        LogUtils.getLogger().warn("[HK3GTL] 跳过 SkyTearsAndGregHeart.init()（dev 环境兼容）");
        ci.cancel();
    }
}
