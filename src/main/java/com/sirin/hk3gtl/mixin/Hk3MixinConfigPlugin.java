package com.sirin.hk3gtl.mixin;

import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ProbabilitySupport;
import net.minecraftforge.fml.loading.LoadingModList;
import net.minecraftforge.forgespi.language.MavenVersionAdapter;
import org.apache.maven.artifact.versioning.VersionRange;
import org.objectweb.asm.ClassReader;
import org.objectweb.asm.tree.ClassNode;
import org.objectweb.asm.tree.MethodInsnNode;
import org.objectweb.asm.tree.LdcInsnNode;

import java.io.IOException;
import java.nio.file.Files;
import java.util.HashSet;
import org.spongepowered.asm.mixin.extensibility.IMixinConfigPlugin;
import org.spongepowered.asm.mixin.extensibility.IMixinInfo;

import java.util.List;
import java.util.Set;

public final class Hk3MixinConfigPlugin implements IMixinConfigPlugin {

    private static final String WMP_MIXIN_PACKAGE = "com.sirin.hk3gtl.mixin.wmp.";
    private static final VersionRange CAMPUS_CORE_VERSIONS = MavenVersionAdapter.createFromVersionSpec("[5.1.1,6.0.0)");
    private static boolean campusVersionReported;
    private static Boolean completeTransfer;
    private static Set<String> conflictingRecipeTypes;
    private static final String REGISTER = "(Ljava/lang/String;Ljava/lang/String;[Lnet/minecraft/world/item/crafting/RecipeType;)Lcom/gregtechceu/gtceu/api/recipe/GTRecipeType;";
    private static final String RECIPE_TYPES = "com/gregtechceu/gtceu/common/data/GTRecipeTypes";
    private static final Set<String> LEGACY_COLLISIONS = Set.of("holographic_data_storage", "floating_point_computation");

    @Override
    public void onLoad(String mixinPackage) {}

    @Override
    public String getRefMapperConfig() {
        return null;
    }

    @Override
    public boolean shouldApplyMixin(String targetClassName, String mixinClassName) {
        if (mixinClassName.endsWith(".Hk3CompleteGtPatternTransferMixin")
                || mixinClassName.endsWith(".Hk3EncodingHelperAccess"))
            return supportsCompleteTransfer();
        if (mixinClassName.endsWith(".Hk3ConflictingRecipeTypesMixin")) {
            return !conflictingRecipeTypes().isEmpty();
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
        if (mixinClassName.endsWith(".Hk3WormholeTravelMixin")) {
            var wormhole = bytecode("sgjourney", targetClassName);
            return wormhole != null && wormhole.methods.stream().anyMatch(method -> method.name.equals("wormholeEntity"));
        }
        if (mixinClassName.startsWith("com.sirin.hk3gtl.mixin.stargate."))
            return LoadingModList.get().getModFileById("sgjourney") != null;
        if (mixinClassName.startsWith("com.sirin.hk3gtl.mixin.gtceu.")) {
            return LoadingModList.get().getModFileById("gtceu") != null;
        }
        if(mixinClassName.startsWith("com.sirin.hk3gtl.mixin.adastra."))return LoadingModList.get().getModFileById("ad_astra")!=null;
        if(mixinClassName.startsWith("com.sirin.hk3gtl.mixin.gtmthings."))return LoadingModList.get().getModFileById("gtmthings")!=null;
        if(mixinClassName.startsWith("com.sirin.hk3gtl.mixin.ae."))return LoadingModList.get().getModFileById("ae2")!=null;
        if (mixinClassName.startsWith("com.sirin.hk3gtl.mixin.gtladd.")) {
            var logic = bytecode("gtladditions", targetClassName);
            boolean compatible = mutableRecipeLogic(logic);
            if (!compatible && LoadingModList.get().getModFileById("gtladditions") != null)
                com.mojang.logging.LogUtils.getLogger().warn("[HK3GTL] GTLAdditions 缺少匹配的多配方动力接口，跳过该联动：{}", targetClassName);
            return compatible;
        }
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

    private static ClassNode bytecode(String modId, String className) {
        var file = LoadingModList.get().getModFileById(modId);
        if (file == null) return null;
        var path = file.getFile().findResource(className.replace('.', '/') + ".class");
        if (!Files.isRegularFile(path)) return null;
        try (var in = Files.newInputStream(path)) {
            var node = new ClassNode();
            new ClassReader(in).accept(node, ClassReader.SKIP_DEBUG | ClassReader.SKIP_FRAMES);
            return node;
        } catch (IOException failure) {
            com.mojang.logging.LogUtils.getLogger().warn("[HK3GTL] 无法读取兼容接口 {}:{}", modId, className, failure);
            return null;
        }
    }

    private static boolean supportsCompleteTransfer() {
        if (completeTransfer != null) return completeTransfer;
        if (LoadingModList.get().getModFileById("jei") == null) return completeTransfer = false;
        var handler = bytecode("ae2", "appeng.integration.modules.jei.transfer.EncodePatternTransferHandler");
        var encoding = bytecode("ae2", "appeng.integration.modules.jeirei.EncodingHelper");
        String menu = "Lappeng/menu/me/items/PatternEncodingTermMenu;";
        String view = "Lmezz/jei/api/gui/ingredient/IRecipeSlotsView;";
        String helper = "appeng/integration/modules/jei/GenericEntryStackHelper";
        var transfer = handler == null ? null : handler.methods.stream().filter(m -> m.name.equals("transferRecipe")
                && m.desc.equals("(" + menu + "Ljava/lang/Object;" + view + "Lnet/minecraft/world/entity/player/Player;ZZ)Lmezz/jei/api/recipe/transfer/IRecipeTransferError;")).findFirst().orElse(null);
        completeTransfer = transfer != null && handler.fields.stream().anyMatch(f -> f.name.equals("helper")
                && f.desc.equals("Lmezz/jei/api/recipe/transfer/IRecipeTransferHandlerHelper;"))
                && calls(transfer, helper, "ofInputs", "(" + view + ")Ljava/util/List;")
                && calls(transfer, helper, "ofOutputs", "(" + view + ")Ljava/util/List;")
                && calls(transfer, "appeng/integration/modules/jeirei/EncodingHelper", "encodeProcessingRecipe",
                    "(" + menu + "Ljava/util/List;Ljava/util/List;)V")
                && encoding != null && encoding.fields.stream().anyMatch(f -> f.name.equals("ENTRY_COMPARATOR")
                    && f.desc.equals("Ljava/util/Comparator;"))
                && hasMethod(encoding, "findBestIngredient", "(Ljava/util/Map;Ljava/util/List;)Lappeng/api/stacks/GenericStack;")
                && hasMethod(encoding, "addOrMerge", "(Ljava/util/List;Lappeng/api/stacks/GenericStack;)V");
        if (!completeTransfer) com.mojang.logging.LogUtils.getLogger().warn(
                "[HK3GTL] AE2 的 JEI 样板转移接口未匹配，完整配方转移未启用。增强版 3.9.2/3.9.3 使用 AE2 15.4.10。");
        return completeTransfer;
    }

    private static boolean calls(org.objectweb.asm.tree.MethodNode method, String owner, String name, String descriptor) {
        for (var node : method.instructions)
            if (node instanceof MethodInsnNode call && call.owner.equals(owner) && call.name.equals(name) && call.desc.equals(descriptor)) return true;
        return false;
    }

    private static boolean hasMethod(ClassNode type, String name, String descriptor) {
        return type.methods.stream().anyMatch(m -> m.name.equals(name) && m.desc.equals(descriptor));
    }

    private static boolean mutableRecipeLogic(ClassNode logic) {
        return logic != null && logic.superName.equals("com/gregtechceu/gtceu/api/machine/trait/RecipeLogic")
                && logic.interfaces.contains("org/gtlcore/gtlcore/api/machine/trait/ILockRecipe")
                && logic.fields.stream().anyMatch(f -> f.name.equals("recipeCheck") && f.desc.equals("Ljava/util/function/BiPredicate;"))
                && hasMethod(logic, "handleRecipeWorking", "()V") && hasMethod(logic, "onRecipeFinish", "()V")
                && hasMethod(logic, "isMultipleRecipeMode", "()Z") && hasMethod(logic, "findAndHandleRecipe", "()V")
                && hasMethod(logic, "getRecipe", "()Lcom/gregtechceu/gtceu/api/recipe/GTRecipe;")
                && hasMethod(logic, "checkRecipe", "(Lcom/gregtechceu/gtceu/api/recipe/GTRecipe;)Z");
    }

    public static Set<String> conflictingRecipeTypes() {
        if (conflictingRecipeTypes != null) return conflictingRecipeTypes;
        if (LoadingModList.get().getModFileById("gtlultimate") == null || LoadingModList.get().getModFileById("gtlsupb") == null)
            return conflictingRecipeTypes = Set.of();
        var shared = registrations(bytecode("gtlsupb", "com.gtlsupb.gtlsupb.common.recipe.GTLSupbRecipeTypes"));
        shared.retainAll(registrations(bytecode("gtlultimate", "org.gtlultimate.gtlultimate.common.data.GTLUltimateRecipeTypes")));
        if (hasVersion("gtlultimate", "1.5.9") && hasVersion("gtlsupb", "4.8.1")) shared.addAll(LEGACY_COLLISIONS);
        conflictingRecipeTypes = Set.copyOf(shared);
        if (shared.isEmpty()) com.mojang.logging.LogUtils.getLogger().info("[HK3GTL] 未在已知注册入口发现 GTL Ultimate / GTL-Supb 重名配方类型。");
        return conflictingRecipeTypes;
    }

    private static Set<String> registrations(ClassNode type) {
        Set<String> result = new HashSet<>();
        if (type == null) return result;
        for (var method : type.methods) {
            if (!method.name.equals("<clinit>")) continue;
            var literals = new java.util.ArrayList<String>();
            for (var node : method.instructions) {
                if (node instanceof LdcInsnNode literal && literal.cst instanceof String text) literals.add(text);
                if (node instanceof MethodInsnNode call) {
                    if (call.owner.equals(RECIPE_TYPES) && call.name.equals("register") && call.desc.equals(REGISTER)
                            && literals.size() == 2) result.add(literals.get(0));
                    literals.clear();
                }
            }
        }
        return result;
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
