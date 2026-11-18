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
