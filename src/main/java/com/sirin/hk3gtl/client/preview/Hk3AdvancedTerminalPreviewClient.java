package com.sirin.hk3gtl.client.preview;

import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.registry.GTRegistries;
import com.lowdragmc.lowdraglib.gui.widget.WidgetGroup;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public final class Hk3AdvancedTerminalPreviewClient {
    private Hk3AdvancedTerminalPreviewClient(){}
    public static void show(WidgetGroup host,ResourceLocation id,Runnable shown){
        host.clearAllWidgets();host.addWidget(new Hk3SparsePreviewWidget((MultiblockMachineDefinition)GTRegistries.MACHINES.get(id),shown));
    }
}
