package com.sirin.hk3gtl.mixin;

/** 【变更记录 #10】2026-10-31 00:46:39（第10次备注 · 修订187）：删除无；新增ad_astra可选依赖守卫；修改仅加载对应兼容Mixin；用途：缺少该模组仍可启动。 */

import net.minecraftforge.fml.loading.LoadingModList;
import org.objectweb.asm.tree.ClassNode;
import org.spongepowered.asm.mixin.extensibility.IMixinConfigPlugin;
import org.spongepowered.asm.mixin.extensibility.IMixinInfo;

import java.util.List;
import java.util.Set;

/**
 * 【文件职责】
 * - 控制外部模组 Mixin 的条件加载，避免可选依赖缺失时解析目标类。
 *
 * 【变更记录 #1】2026-07-19 20:14:25（第 1 次备注 · 内测四第 33 次更新）
 * - 删除：无。
 * - 新增：仅当 Forge LoadingModList 检测到 modId=wmp 时应用 mixin.wmp 包下的联动 Mixin。
 * - 修改：核心 hk3gtl Mixin 始终加载，不改变现有 required/defaultRequire 策略。
 * - 用途：让 WMP 联动保持可选，未安装 WMP 的服务端和客户端仍能正常启动。
 */
/**
 * 【变更记录 #2】2026-09-27 23:52:00（内测5修订91）
 * 删除：无，保留旧兼容代码。新增：增强版条件守卫只在增强版存在时加载。
 * 修改：增强版存在时禁用旧SkyTears初始化取消补丁，让定制依赖正常注册内容。
 * 用途：同一HK3包支持两套底包，不替换增强版依赖或取消其性能补丁。
 */
/**
 * 【变更记录 #3】2026-09-30 01:28:26（第3次备注 · 内测5修订105）
 * - 删除：无。新增：JEI复制保护仅在JEI与jei_copy_recipe_json均存在时加载。
 * - 修改：可选客户端兼容条件独立于增强版判断。
 * - 用途：原版缺少复制附属时跳过目标解析，专用服务端不加载客户端Mixin。
 */
/**
 * 【变更记录 #4】2026-09-30 17:52:49（内测5修订111）
 * 删除：无。新增：Avaritia能力集合补丁的可选模组加载守卫。
 * 修改：仅在avaritia存在时启用目标Mixin；用途：缺少可选依赖时不解析其类。
 */
/** 【变更记录 #5】2026-10-01 04:45:29（修订128）：删除：旧固定上限或被替代的分支；新增/修改：AE专用检测Mixin仅在AE2存在时解析，缺联动不加载目标类；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #6】2026-10-01 05:20:36（修订128）：删除：旧固定上限或被替代的分支；新增/修改：GTLCore和GTLSupb专用彩蛋Mixin按实际模组存在守卫；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #7】2026-10-01 06:15:25（修订128）：删除：无；新增/修改：无线覆盖板旁注Mixin随实际GTMThings可选依赖启用；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #8】2026-10-01 12:13:33（修订128）：删除：无；新增/修改：JEI彩蛋客户端钩子按依赖存在加载，专服不解析界面类；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/**
 * 【变更记录 #9】2026-10-17 16:27:36（第9次备注 · 修订165）
 * 删除：公共GT配方条件守卫仅在增强版启用的限制。
 * 新增：无；修改：EnhancedRecipeConditionsMixin只依赖GT，所有目标底包均加载，tick兼容仍按增强版存在选择。
 * 用途：高阶工况匹配/模拟/实际推进共用同一只读校验，不新增第三方私有类依赖。
 */
/**
 * 【变更记录 #11】2026-11-04 21:03:18（第11次备注 · 内测5修订200）
 * 删除：无。新增：IV工业独立执行器降效兼容按增强核心存在条件加载。
 * 修改：与既有增强版tick守卫共用模组检测；用途：普通底包不解析可选IV目标类。
 */
public final class Hk3MixinConfigPlugin implements IMixinConfigPlugin {

    private static final String WMP_MIXIN_PACKAGE = "com.sirin.hk3gtl.mixin.wmp.";

    @Override
    public void onLoad(String mixinPackage) {}

    @Override
    public String getRefMapperConfig() {
        return null;
    }

    @Override
    public boolean shouldApplyMixin(String targetClassName, String mixinClassName) {
        if(mixinClassName.contains(".Hk3W03Embeddium"))return LoadingModList.get().getModFileById("embeddium")!=null;
        if (mixinClassName.endsWith(".AvaritiaAbilityHandlerMixin")) {
            return LoadingModList.get().getModFileById("avaritia") != null;
        }
        if (mixinClassName.endsWith(".JeiCopyItemHandlerMixin")) {
            return LoadingModList.get().getModFileById("jei") != null
                    && LoadingModList.get().getModFileById("jei_copy_recipe_json") != null;
        }
        if (mixinClassName.startsWith("com.sirin.hk3gtl.mixin.gtceu.")) {
            return LoadingModList.get().getModFileById("gtceu") != null;
        }
        if(mixinClassName.startsWith("com.sirin.hk3gtl.mixin.adastra."))return LoadingModList.get().getModFileById("ad_astra")!=null;
        if(mixinClassName.startsWith("com.sirin.hk3gtl.mixin.gtmthings."))return LoadingModList.get().getModFileById("gtmthings")!=null;
        if(mixinClassName.startsWith("com.sirin.hk3gtl.mixin.ae."))return LoadingModList.get().getModFileById("ae2")!=null;
        if(mixinClassName.startsWith("com.sirin.hk3gtl.mixin.gtlcore."))return LoadingModList.get().getModFileById("gtlcore")!=null;
        if(mixinClassName.startsWith("com.sirin.hk3gtl.mixin.gtlsupb."))return LoadingModList.get().getModFileById("gtlsupb")!=null;
        if(mixinClassName.startsWith("com.sirin.hk3gtl.mixin.jei."))return LoadingModList.get().getModFileById("jei")!=null;
        boolean enhanced = LoadingModList.get().getModFileById("gtl_enhancedcore") != null;
        if (mixinClassName.endsWith(".EnhancedRecipeTickMixin")
                || mixinClassName.endsWith(".EnhancedIndustrialGazeMixin")) return enhanced;
        if (mixinClassName.endsWith(".SkyTearsAndGregHeartMixin") && enhanced) return false;
        return !mixinClassName.startsWith(WMP_MIXIN_PACKAGE)
                || LoadingModList.get().getModFileById("wmp") != null;
    }

    @Override
    public void acceptTargets(Set<String> myTargets, Set<String> otherTargets) {}

    @Override
    public List<String> getMixins() {
        return null;
    }

    @Override
    public void preApply(String targetClassName, ClassNode targetClass, String mixinClassName, IMixinInfo mixinInfo) {}

    @Override
    public void postApply(String targetClassName, ClassNode targetClass, String mixinClassName, IMixinInfo mixinInfo) {}
}
