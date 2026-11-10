package com.sirin.hk3gtl.common.machine.w02;

import com.gregtechceu.gtceu.api.data.RotationState;
import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.sirin.hk3gtl.Hk3Gtl;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Blocks;

/** A2静态船坞使用真实GT控制器，正式工艺尚待冻结。 */
public final class Hk3W02Machines {
    public static MultiblockMachineDefinition MATRIX;
    private Hk3W02Machines(){}
    public static void init(){
        MATRIX=Hk3Gtl.REGISTRATE.multiblock("omnia_autonomous_industrial_matrix",Hk3W02Machine::new)
            .tier(Hk3Tiers.WSV).rotationState(RotationState.NON_Y_AXIS).allowFlip(false).allowExtendedFacing(false)
            .appearanceBlock(()->Blocks.LIGHT_BLUE_CONCRETE).pattern(Hk3W02Pattern::new).multiblockPreviewRenderer(false,true)
            .workableCasingRenderer(new ResourceLocation("hk3gtl","block/casings/industrial_controller_shell"),new ResourceLocation("hk3gtl","block/overlay/w01_hall"))
            .tooltips(Component.literal("W02 · 19C构造船坞A2 · 全静态 · 649×493×368"),
                Component.literal("真实实体检查及创造启停调试；正式生产、研究和毕业链另验")).register();
    }
}
