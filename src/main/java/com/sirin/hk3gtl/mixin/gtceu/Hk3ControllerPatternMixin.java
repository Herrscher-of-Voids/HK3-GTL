package com.sirin.hk3gtl.mixin.gtceu;

import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import com.sirin.hk3gtl.common.multiblock.loading.Hk3MultiblockLoading;
import org.spongepowered.asm.mixin.Mixin;

/** 动态Pattern创建前先切换到分批核验会话。 */
@Mixin(value=MultiblockControllerMachine.class,remap=false,priority=1300)
public abstract class Hk3ControllerPatternMixin {
    public boolean checkPattern(){
        var controller=(MultiblockControllerMachine)(Object)this;
        if(Hk3MultiblockLoading.intercept(controller))return false;
        var pattern=controller.getPattern();
        return pattern!=null&&pattern.checkPatternAt(controller.getMultiblockState(),false);
    }
}
