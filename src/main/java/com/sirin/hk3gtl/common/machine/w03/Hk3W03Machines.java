package com.sirin.hk3gtl.common.machine.w03;

import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.data.RotationState;
import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.sirin.hk3gtl.Hk3Gtl;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.network.chat.Component;

/** 已批准C9的真实GT主控，生产与毕业链路尚未开放。 */
public final class Hk3W03Machines {
    public static MultiblockMachineDefinition VOID_ANCHOR;
    private Hk3W03Machines(){}
    public static void init(){
        VOID_ANCHOR=Hk3Gtl.REGISTRATE.multiblock("void_anchor_ring",Hk3W03Machine::new)
            .tier(GTValues.MAX).rotationState(RotationState.NON_Y_AXIS).allowFlip(false).allowExtendedFacing(false)
            .appearanceBlock(()->Blocks.QUARTZ_BLOCK).pattern(Hk3W03Pattern::new).multiblockPreviewRenderer(false,true)
            .workableCasingRenderer(new ResourceLocation("hk3gtl","block/casings/industrial_controller_shell"),new ResourceLocation("hk3gtl","block/overlay/w01_hall"))
            .tooltips(Component.translatable("hk3gtl.w03.size"),Component.translatable("hk3gtl.w03.commission")).register();
    }
}
