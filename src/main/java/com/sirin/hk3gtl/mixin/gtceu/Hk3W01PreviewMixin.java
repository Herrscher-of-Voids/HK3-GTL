package com.sirin.hk3gtl.mixin.gtceu;

import com.gregtechceu.gtceu.api.gui.widget.PatternPreviewWidget;
import com.mojang.blaze3d.systems.RenderSystem;
import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.pattern.MultiblockShapeInfo;
import com.lowdragmc.lowdraglib.gui.widget.SceneWidget;
import com.lowdragmc.lowdraglib.gui.widget.WidgetGroup;
import com.sirin.hk3gtl.client.preview.Hk3SparsePreviewWidget;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.Redirect;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.HashSet;
import java.util.List;

/**
 * 【文件职责】在GT原生分类内接入本模组自家完整预览，按需解码稀疏实体，不接管其他模组。
 * 【变更记录 #1】2026-10-29 23:12:35（第1次备注 · 本轮高度与预览修复）
 * 删除：无；新增：W01专用场景分支；修改：跳过基类单控制器形状，改为真实完整布局。
 * 用途：其他多方块维持原GT预览，W01不展开约两亿空气格、不隐藏原生预览入口。
 */
/** 【变更记录 #2】2026-10-29 23:18:13（第2次备注 · 本轮高度与预览修复）：删除无；新增原组件VBO释放的渲染线程守卫；修改私有身份函数标记Unique；用途为离屏注册时在原排队申请后释放被替换场景，不遗留GPU缓存。 */
@Mixin(value = PatternPreviewWidget.class, remap = false)
public abstract class Hk3W01PreviewMixin {
    @Shadow @Final public MultiblockMachineDefinition controllerDefinition;
    @Shadow @Final private SceneWidget sceneWidget;

    @Unique private boolean hk3gtl$isSparse() {
        return "hk3gtl".equals(controllerDefinition.getId().getNamespace());
    }

    /** 本模组全部使用自家预览；其他模组保留原入口，世界投影与成型不受影响。 */
    @Redirect(method = "lambda$new$2", at = @At(value = "INVOKE", target =
            "Lcom/gregtechceu/gtceu/api/machine/MultiblockMachineDefinition;getMatchingShapes()Ljava/util/List;"))
    private List<MultiblockShapeInfo> hk3gtl$skipPrototypeDenseShapes(MultiblockMachineDefinition definition) {
        return "hk3gtl".equals(definition.getId().getNamespace()) ? List.of() : definition.getMatchingShapes();
    }

    @Inject(method = "initializePattern", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$skipDensePreview(MultiblockShapeInfo shape, HashSet<?> drops, CallbackInfoReturnable<Object> callback) {
        if (hk3gtl$isSparse()) callback.setReturnValue(null);
    }

    @Inject(method = "<init>", at = @At("RETURN"))
    private void hk3gtl$attachFullPreview(MultiblockMachineDefinition definition, CallbackInfo callback) {
        if (!hk3gtl$isSparse()) return;
        if (RenderSystem.isOnRenderThread()) sceneWidget.releaseCacheBuffer();
        else RenderSystem.recordRenderCall(sceneWidget::releaseCacheBuffer);
        WidgetGroup widget = (WidgetGroup) (Object) this;
        widget.clearAllWidgets();
        widget.addWidget(new Hk3SparsePreviewWidget(definition));
    }
}
