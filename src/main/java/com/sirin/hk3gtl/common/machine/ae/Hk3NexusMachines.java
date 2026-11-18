package com.sirin.hk3gtl.common.machine.ae;

import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.data.RotationState;
import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.client.renderer.machine.MachineRenderer;
import com.sirin.hk3gtl.Hk3Gtl;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Blocks;

public final class Hk3NexusMachines {
    public static MultiblockMachineDefinition NEXUS;

    private Hk3NexusMachines() {}

    public static void init() {
        NEXUS = Hk3Gtl.REGISTRATE.multiblock("ae_nexus", Hk3NexusMachine::new)
                .tier(GTValues.MAX).rotationState(RotationState.NON_Y_AXIS)
                .allowFlip(false).allowExtendedFacing(false)
                .appearanceBlock(() -> Blocks.SMOOTH_QUARTZ)
                .pattern(Hk3NexusStructure::pattern)
                .shapeInfo(Hk3NexusStructure::shape)
                .renderer(() -> new MachineRenderer(new ResourceLocation("hk3gtl", "block/ae_nexus_controller_r13")))
                .tooltips(Component.translatable("hk3gtl.nexus.tooltip"),
                        Component.translatable("hk3gtl.nexus.tooltip.owner"),
                        Component.translatable("hk3gtl.nexus.tooltip.management"),
                        Component.translatable("hk3gtl.nexus.structure"))
                .register();
    }
}
