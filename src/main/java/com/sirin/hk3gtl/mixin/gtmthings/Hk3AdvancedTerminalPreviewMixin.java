package com.sirin.hk3gtl.mixin.gtmthings;

import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import com.hepdd.gtmthings.common.item.AdvancedTerminalBehavior;
import com.lowdragmc.lowdraglib.gui.factory.HeldItemUIFactory.HeldItemHolder;
import com.lowdragmc.lowdraglib.gui.modular.ModularUI;
import com.lowdragmc.lowdraglib.gui.widget.Widget;
import com.sirin.hk3gtl.common.gui.Hk3AdvancedTerminalPreviewWidget;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3SparsePreviewData;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.UseOnContext;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.Redirect;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;



@Mixin(value=AdvancedTerminalBehavior.class,remap=false)
public abstract class Hk3AdvancedTerminalPreviewMixin {
    private static AdvancedTerminalBehavior.AutoBuildSetting hk3gtl$settings(ItemStack stack){
        var settings=new AdvancedTerminalBehavior.AutoBuildSetting();var tag=stack.getOrCreateTag();
        settings.setCoilTier(tag.getInt("CoilTier"));settings.setRepeatCount(tag.getInt("RepeatCount"));
        settings.setNoHatchMode(tag.getInt("NoHatchMode"));return settings;
    }

    @Redirect(method="createUI",at=@At(value="INVOKE",target="Lcom/hepdd/gtmthings/common/item/AdvancedTerminalBehavior;createWidget()Lcom/lowdragmc/lowdraglib/gui/widget/Widget;"))
    private Widget hk3gtl$localSettings(AdvancedTerminalBehavior behavior,HeldItemHolder holder,Player player){
        var local=(Hk3AdvancedTerminalSettingsAccess)new AdvancedTerminalBehavior();
        local.hk3gtl$setItemStack(holder.getHeld());local.hk3gtl$setAutoBuildSetting(hk3gtl$settings(holder.getHeld()));
        return local.hk3gtl$createWidget();
    }

    @Redirect(method="useOn",at=@At(value="FIELD",target="Lcom/hepdd/gtmthings/common/item/AdvancedTerminalBehavior;autoBuildSetting:Lcom/hepdd/gtmthings/common/item/AdvancedTerminalBehavior$AutoBuildSetting;"))
    private AdvancedTerminalBehavior.AutoBuildSetting hk3gtl$buildSettings(AdvancedTerminalBehavior behavior,UseOnContext context){
        return hk3gtl$settings(context.getItemInHand());
    }

    @Inject(method="createUI",at=@At("RETURN"))
    private void hk3gtl$previewEntry(HeldItemHolder holder,Player player,CallbackInfoReturnable<ModularUI> callback){
        var ui=callback.getReturnValue();ui.setSize(358,166);ui.widget(new Hk3AdvancedTerminalPreviewWidget(holder,player));
    }

    @Inject(method="useOn",at=@At("HEAD"),cancellable=true)
    private void hk3gtl$previewTarget(UseOnContext context,CallbackInfoReturnable<InteractionResult> callback){
        if(!(context.getPlayer() instanceof ServerPlayer player)||!player.isShiftKeyDown())return;
        var stack=context.getItemInHand();var tag=stack.getOrCreateTag();
        if(!tag.getBoolean(Hk3AdvancedTerminalPreviewWidget.ARMED)
                ||!(MetaMachine.getMachine(context.getLevel(),context.getClickedPos()) instanceof MultiblockControllerMachine controller))return;
        var definition=controller.getDefinition();
        if(!Hk3SparsePreviewData.supported(definition.getId().toString())&&definition.getMatchingShapes().isEmpty()){
            player.displayClientMessage(net.minecraft.network.chat.Component.translatable("hk3gtl.terminal.preview.unavailable"),true);
            callback.setReturnValue(InteractionResult.SUCCESS);return;
        }
        tag.remove(Hk3AdvancedTerminalPreviewWidget.ARMED);tag.putLong(Hk3AdvancedTerminalPreviewWidget.TARGET,context.getClickedPos().asLong());
        tag.putString(Hk3AdvancedTerminalPreviewWidget.DIMENSION,context.getLevel().dimension().location().toString());
        player.inventoryMenu.broadcastChanges();
        ((AdvancedTerminalBehavior)(Object)this).use(stack.getItem(),context.getLevel(),player,context.getHand());
        callback.setReturnValue(InteractionResult.SUCCESS);
    }
}
