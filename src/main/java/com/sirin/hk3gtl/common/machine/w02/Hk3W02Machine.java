package com.sirin.hk3gtl.common.machine.w02;

import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.sirin.hk3gtl.common.machine.Hk3CommissionMachine;

/** 普通理之律者19C A2实体船坞，保持全静态。 */
public final class Hk3W02Machine extends Hk3CommissionMachine {
    public Hk3W02Machine(IMachineBlockEntity holder){super(holder);}
    @Override protected String commissionTitle(){return "W02 · 万象·自律工业矩阵";}
    @Override public com.lowdragmc.lowdraglib.gui.modular.ModularUI createUI(net.minecraft.world.entity.player.Player player) {
        return super.createUI(player).widget(new com.lowdragmc.lowdraglib.gui.widget.ButtonWidget(8,157,64,20,
            new com.lowdragmc.lowdraglib.gui.texture.GuiTextureGroup(com.gregtechceu.gtceu.api.gui.GuiTextures.BUTTON,
                new com.lowdragmc.lowdraglib.gui.texture.TextTexture("hk3gtl.w02.move_ports")),click->{
                if(!click.isRemote && player instanceof net.minecraft.server.level.ServerPlayer owner)
                    owner.sendSystemMessage(net.minecraft.network.chat.Component.literal(Hk3W02PortMigration.apply(this,owner)));
            }));
    }
}
