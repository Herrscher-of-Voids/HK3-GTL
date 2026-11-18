package com.sirin.hk3gtl.common.worldbubble;

import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.capability.recipe.ItemRecipeCapability;
import com.gregtechceu.gtceu.api.capability.recipe.FluidRecipeCapability;
import com.gregtechceu.gtceu.api.machine.trait.NotifiableItemStackHandler;
import com.gregtechceu.gtceu.api.machine.trait.NotifiableFluidTank;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.recipe.ingredient.FluidIngredient;
import com.lowdragmc.lowdraglib.side.fluid.FluidStack;
import com.sirin.hk3gtl.common.machine.research.Hk3ResearchProcessMachine;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Ingredient;
import org.gtlcore.gtlcore.common.machine.multiblock.part.ae.NotifiableMERecipeHandlerTrait;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Stream;

public record Hk3WorldOutputPorts(List<NotifiableItemStackHandler> items, List<NotifiableFluidTank> fluids,
        List<NotifiableMERecipeHandlerTrait<Ingredient, ItemStack>> aeItems,
        List<NotifiableMERecipeHandlerTrait<FluidIngredient, FluidStack>> aeFluids) {
    @SuppressWarnings("unchecked")
    public static Hk3WorldOutputPorts of(Hk3ResearchProcessMachine machine) {
        var ports = new Hk3WorldOutputPorts(new ArrayList<>(), new ArrayList<>(), new ArrayList<>(), new ArrayList<>());
        Stream.of(IO.OUT, IO.BOTH).flatMap(io -> machine.getCapabilitiesProxy().row(io).values().stream())
                .flatMap(List::stream).distinct().forEach(handler -> {
                    if (handler.getCapability() == ItemRecipeCapability.CAP) {
                        if (handler instanceof NotifiableItemStackHandler item) ports.items.add(item);
                    } else if (handler.getCapability() == FluidRecipeCapability.CAP) {
                        if (handler instanceof NotifiableFluidTank fluid) ports.fluids.add(fluid);
                    }
                });
        for (var part : machine.getParts()) {
            if (!(part instanceof MetaMachine meta)) continue;
            for (var trait : meta.getTraits()) {
                if (!(trait instanceof NotifiableMERecipeHandlerTrait<?, ?> handler)
                        || handler.getIo() != IO.OUT && handler.getIo() != IO.BOTH) continue;
                if (handler.getCapability() == ItemRecipeCapability.CAP)
                    ports.aeItems.add((NotifiableMERecipeHandlerTrait<Ingredient, ItemStack>) handler);
                else if (handler.getCapability() == FluidRecipeCapability.CAP)
                    ports.aeFluids.add((NotifiableMERecipeHandlerTrait<FluidIngredient, FluidStack>) handler);
            }
        }
        return ports;
    }
}
