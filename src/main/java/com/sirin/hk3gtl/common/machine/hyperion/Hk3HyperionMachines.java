package com.sirin.hk3gtl.common.machine.hyperion;

import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.data.RotationState;
import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.sirin.hk3gtl.Hk3Gtl;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Blocks;

/** 仅注册负责人要求的舰体搭建测试控制器，不恢复旧版502格结构。 */
public final class Hk3HyperionMachines {
    public static MultiblockMachineDefinition FLAGSHIP;
    private Hk3HyperionMachines() {}
    public static void init() {
        FLAGSHIP = Hk3Gtl.REGISTRATE.multiblock("hyperion_flagship", Hk3HyperionMachine::new)
                .tier(GTValues.MAX).rotationState(RotationState.NON_Y_AXIS)
                .allowFlip(false).allowExtendedFacing(false)
                .appearanceBlock(() -> Blocks.WHITE_CONCRETE)
                .pattern(Hk3HyperionConstructionPattern::new)
                .multiblockPreviewRenderer(false, true)
                .workableCasingRenderer(new ResourceLocation("hk3gtl", "block/casings/industrial_controller_shell"),
                        new ResourceLocation("hk3gtl", "block/overlay/w01_hall"))
                .tooltips(Component.translatable("hk3gtl.hyperion.size"), Component.translatable("hk3gtl.hyperion.creative"),
                        Component.translatable("hk3gtl.hyperion.height"))
                .register();
    }
}
