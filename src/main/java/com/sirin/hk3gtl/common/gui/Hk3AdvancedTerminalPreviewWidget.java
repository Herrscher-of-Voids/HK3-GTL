package com.sirin.hk3gtl.common.gui;

import com.gregtechceu.gtceu.api.gui.GuiTextures;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import com.gregtechceu.gtceu.api.pattern.MultiblockState;
import com.gregtechceu.gtceu.api.pattern.error.PatternError;
import com.lowdragmc.lowdraglib.gui.factory.HeldItemUIFactory.HeldItemHolder;
import com.lowdragmc.lowdraglib.gui.modular.ModularUIContainer;
import com.lowdragmc.lowdraglib.gui.texture.GuiTextureGroup;
import com.lowdragmc.lowdraglib.gui.texture.TextTexture;
import com.lowdragmc.lowdraglib.gui.widget.ButtonWidget;
import com.lowdragmc.lowdraglib.gui.widget.LabelWidget;
import com.lowdragmc.lowdraglib.gui.widget.ImageWidget;
import com.lowdragmc.lowdraglib.gui.widget.WidgetGroup;
import com.sirin.hk3gtl.common.easter.Hk3EggVanilla;
import net.minecraft.core.BlockPos;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;

public final class Hk3AdvancedTerminalPreviewWidget extends WidgetGroup {
    public static final String ARMED="hk3gtlPreviewArmed", TARGET="hk3gtlPreviewTarget", DIMENSION="hk3gtlPreviewDimension";
    private final HeldItemHolder holder;
    private final Player player;
    private final WidgetGroup preview=new WidgetGroup(194,3,160,160);
    private MultiblockControllerMachine target;
    private boolean requested,viewed;
    private Component inspection=Component.empty();
    private final ImageWidget resultLine;

    public Hk3AdvancedTerminalPreviewWidget(HeldItemHolder holder,Player player){
        super(0,0,358,166);this.holder=holder;this.player=player;
        preview.setClientSideWidget();preview.setBackground(GuiTextures.BACKGROUND_INVERSE);
        preview.addWidget(new LabelWidget(8,68,"hk3gtl.terminal.preview.choose"));addWidget(preview);
        addWidget(new ButtonWidget(8,132,80,20,new GuiTextureGroup(GuiTextures.BUTTON,new TextTexture("hk3gtl.terminal.preview.select")),click->{
            if(!click.isRemote&&player instanceof ServerPlayer p&&valid(p)){
                var tag=holder.getHeld().getOrCreateTag();tag.putBoolean(ARMED,true);tag.remove(TARGET);
                p.closeContainer();p.inventoryMenu.broadcastChanges();
                p.displayClientMessage(Component.translatable("hk3gtl.terminal.preview.armed"),true);
            }
        }));
        addWidget(new ButtonWidget(92,132,80,20,new GuiTextureGroup(GuiTextures.BUTTON,new TextTexture("hk3gtl.terminal.preview.check")),click->{
            if(!click.isRemote&&player instanceof ServerPlayer p&&selected(p)){
                var result=inspect(p);writeUpdateInfo(52,buf->buf.writeComponent(result));
            }
        }));
        resultLine=new ImageWidget(8,154,176,10,new TextTexture(()->inspection.getString()).setWidth(176).setType(TextTexture.TextType.ROLL));
        addWidget(resultLine);
    }

    private boolean valid(ServerPlayer p){
        return p.containerMenu instanceof ModularUIContainer ui&&ui.getModularUI().holder==holder&&ui.stillValid(p)
                &&net.minecraft.core.registries.BuiltInRegistries.ITEM.getKey(holder.getHeld().getItem()).toString().equals("gtmthings:advanced_terminal");
    }

    private boolean selected(ServerPlayer p){
        return target!=null&&valid(p)&&p.level()==target.getLevel()&&p.level().hasChunkAt(target.getPos())
                &&MetaMachine.getMachine(p.level(),target.getPos())==target;
    }

    private Component inspect(ServerPlayer p){
        var lock=target.getPatternLock();if(!lock.tryLock())return Component.translatable("hk3gtl.terminal.preview.checking");
        try{
            var state=target.getMultiblockState();var error=state.error;
            if(target.isFormed()&&!state.hasError())return Component.translatable("hk3gtl.terminal.preview.formed");
            if(error==null||error==MultiblockState.UNINIT_ERROR||error==MultiblockState.UNLOAD_ERROR)return Component.translatable("hk3gtl.terminal.preview.waiting");
            boolean missing=error.getClass()==PatternError.class&&state.predicate!=null&&error.getWorld()==p.level()
                    &&p.level().hasChunkAt(error.getPos())&&p.level().getBlockState(error.getPos()).isAir()
                    &&error.getCandidates().stream().flatMap(java.util.Collection::stream)
                    .anyMatch(stack->!stack.isEmpty()&&stack.getItem() instanceof net.minecraft.world.item.BlockItem);
            if(missing&&viewed)Hk3EggVanilla.caseEvent(p,466);
            return Component.translatable("hk3gtl.terminal.preview."+(missing?"missing":"error"),error.getErrorInfo());
        }finally{lock.unlock();}
    }

    @Override public void detectAndSendChanges(){
        super.detectAndSendChanges();
        if(requested||!(player instanceof ServerPlayer p))return;requested=true;
        var tag=holder.getHeld().getOrCreateTag();
        if(!tag.contains(TARGET)||!tag.getString(DIMENSION).equals(p.level().dimension().location().toString()))return;
        var pos=BlockPos.of(tag.getLong(TARGET));
        if(!valid(p)||!p.level().hasChunkAt(pos)||!(MetaMachine.getMachine(p.level(),pos) instanceof MultiblockControllerMachine controller))return;
        target=controller;writeUpdateInfo(51,buf->buf.writeResourceLocation(controller.getDefinition().getId()));
    }

    @Override public void readUpdateInfo(int id,FriendlyByteBuf buf){
        if(id==51){var machine=buf.readResourceLocation();DistExecutor.unsafeRunWhenOn(Dist.CLIENT,()->()->
                com.sirin.hk3gtl.client.preview.Hk3AdvancedTerminalPreviewClient.show(preview,machine,()->writeClientAction(51,ignored->{})));}
        else if(id==52){inspection=buf.readComponent();resultLine.setHoverTooltips(inspection);}
        else super.readUpdateInfo(id,buf);
    }

    @Override public void handleClientAction(int id,FriendlyByteBuf buf){
        if(id==51){
            if(player instanceof ServerPlayer p&&selected(p)){viewed=true;Hk3EggVanilla.caseEvent(p,275);}
        }else super.handleClientAction(id,buf);
    }
}
