package com.sirin.hk3gtl.mixin.gtceu;

import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.integration.jei.multipage.MultiblockInfoWrapper;
import com.lowdragmc.lowdraglib.gui.widget.Widget;
import com.lowdragmc.lowdraglib.jei.ModularWrapper;
import com.sirin.hk3gtl.client.preview.Hk3SparsePreviewWidget;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** 在包装器构造完成后接管自家场景，避免GTL的参数替换再次覆盖。 */
@Mixin(value=MultiblockInfoWrapper.class,remap=false)
public abstract class Hk3JeiPreviewWidgetMixin extends ModularWrapper<Widget> {
    protected Hk3JeiPreviewWidgetMixin(Widget widget) { super(widget); }

    @Inject(method="<init>",at=@At("RETURN"))
    private void hk3gtl$preview(MultiblockMachineDefinition definition,CallbackInfo ci) {
        if(!"hk3gtl".equals(definition.getId().getNamespace()))return;
        var preview=new Hk3SparsePreviewWidget(definition);
        modularUI.mainGroup.clearAllWidgets();
        modularUI.mainGroup.setSize(preview.getSize());
        modularUI.widget(preview);
        this.widget=preview;
    }
}
