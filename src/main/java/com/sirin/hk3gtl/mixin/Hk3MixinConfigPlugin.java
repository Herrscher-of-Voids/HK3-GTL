package com.sirin.hk3gtl.mixin;

import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ProbabilitySupport;
import net.minecraftforge.fml.loading.LoadingModList;
import net.minecraftforge.forgespi.language.MavenVersionAdapter;
import org.apache.maven.artifact.versioning.VersionRange;
import org.objectweb.asm.tree.ClassNode;
import org.spongepowered.asm.mixin.extensibility.IMixinConfigPlugin;
import org.spongepowered.asm.mixin.extensibility.IMixinInfo;

import java.util.List;
import java.util.Set;

public final class Hk3MixinConfigPlugin implements IMixinConfigPlugin {

    private static final String WMP_MIXIN_PACKAGE = "com.sirin.hk3gtl.mixin.wmp.";
    private static final VersionRange CAMPUS_CORE_VERSIONS = MavenVersionAdapter.createFromVersionSpec("[5.1.1,6.0.0)");
    private static boolean campusVersionReported;

    @Override
    public void onLoad(String mixinPackage) {}

    @Override
    public String getRefMapperConfig() {
        return null;
    }

    @Override
    public boolean shouldApplyMixin(String targetClassName, String mixinClassName) {
        if (mixinClassName.endsWith(".Hk3ConflictingRecipeTypesMixin")) {
            return hasVersion("gtlultimate", "1.5.9") && hasVersion("gtlsupb", "4.8.1");
        }
        if (mixinClassName.startsWith("com.sirin.hk3gtl.mixin.enhanced.")) {
            var file = LoadingModList.get().getModFileById("gtl_enhancedcore");
            if (file == null) return false;
            boolean compatible = file.getMods().stream().anyMatch(mod -> mod.getModId().equals("gtl_enhancedcore")
                    && CAMPUS_CORE_VERSIONS.containsVersion(mod.getVersion()));
            if (!compatible && !campusVersionReported) {
                campusVersionReported = true;
                com.mojang.logging.LogUtils.getLogger().warn("HK3GTL园区扩展支持增强核心[5.1.1,6.0.0)，当前版本跳过该兼容");
            }
            return compatible;
        }
        if (mixinClassName.endsWith(".Hk3ProbabilityAssemblyMixin") || mixinClassName.endsWith(".Hk3ProbabilityOutputMixin")
                || mixinClassName.endsWith(".Hk3RecipeRunnerInvoker") || mixinClassName.endsWith(".Hk3ProbabilitySlotAccess")
                || mixinClassName.endsWith(".Hk3ProbabilityPushMixin"))
            return Hk3ProbabilitySupport.AVAILABLE;
        if(mixinClassName.endsWith(".Hk3FarNativeRenderMixin"))return LoadingModList.get().getModFileById("embeddium")==null;
        if(mixinClassName.contains(".Hk3W03Embeddium")||mixinClassName.contains(".Hk3FarEmbeddium"))return LoadingModList.get().getModFileById("embeddium")!=null;
        if (mixinClassName.endsWith(".AvaritiaAbilityHandlerMixin")) {
            return LoadingModList.get().getModFileById("avaritia") != null;
        }
        if (mixinClassName.endsWith(".JeiCopyItemHandlerMixin")) {
            return LoadingModList.get().getModFileById("jei") != null
                    && LoadingModList.get().getModFileById("jei_copy_recipe_json") != null;
        }
        if (mixinClassName.startsWith("com.sirin.hk3gtl.mixin.stargate."))
            return LoadingModList.get().getModFileById("sgjourney") != null;
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

    private static boolean hasVersion(String id, String version) {
        var file = LoadingModList.get().getModFileById(id);
        return file != null && file.getMods().stream().anyMatch(mod ->
                mod.getModId().equals(id) && mod.getVersion().toString().equals(version));
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
