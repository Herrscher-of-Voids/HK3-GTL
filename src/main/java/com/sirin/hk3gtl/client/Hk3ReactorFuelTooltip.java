package com.sirin.hk3gtl.client;

import com.sirin.hk3gtl.common.recipe.Hk3ResearchProcessPlans;
import com.sirin.hk3gtl.common.recipe.honkai.Hk3ReactorFuels;
import com.sirin.hk3gtl.common.recipe.honkai.Hk3FuelBundlePlans;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.entity.player.ItemTooltipEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.Comparator;
import java.util.Locale;
import java.math.BigDecimal;
import java.math.RoundingMode;

@Mod.EventBusSubscriber(modid = "hk3gtl", value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class Hk3ReactorFuelTooltip {
    private Hk3ReactorFuelTooltip() {}

    @SubscribeEvent
    public static void tooltip(ItemTooltipEvent event) {
        String id = BuiltInRegistries.ITEM.getKey(event.getItemStack().getItem()).toString();
        if (!Hk3ReactorFuels.FUEL_IDS.contains(id)) return;
        var rod = Hk3ReactorFuels.RODS.stream()
                .filter(fuel -> id.equals("hk3gtl:" + fuel.path()) || id.startsWith("hk3gtl:" + fuel.path() + "_"))
                .findFirst().get();
        event.getToolTip().add(Component.translatable("hk3gtl.tooltip.reactor_fuel.heat",
                rod.heatPerTick(), rod.heatPerTick() * Hk3ReactorFuels.bundleSize(id)));
        event.getToolTip().add(Component.translatable("hk3gtl.tooltip.reactor_fuel." + (rod.highGrade() ? "high" : "low")));
        for (var plan : Hk3ResearchProcessPlans.all().stream()
                .filter(value -> Hk3ReactorFuels.reactor(value.role()) && value.inputs().get(0).id().equals(id))
                .sorted(Comparator.comparing(Hk3ResearchProcessPlans.Plan::role)
                        .thenComparingLong(Hk3ResearchProcessPlans.Plan::outputEut)).toList()) {
            var operation = Hk3FuelBundlePlans.get(plan.id());
            var name = Component.translatable("gtceu.industrial_process_" + plan.role().toLowerCase(Locale.ROOT))
                    .append(plan.fluidInputs().isEmpty() ? "（基础）" : "（高能）");
            event.getToolTip().add(Component.translatable("hk3gtl.tooltip.reactor_fuel.hw",
                    name, BigDecimal.valueOf(plan.networkCredit()).divide(BigDecimal.valueOf(plan.ticks()),
                            8, RoundingMode.HALF_UP).stripTrailingZeros().toPlainString(),
                    plan.inputs().get(0).count(), plan.networkCredit()));
            event.getToolTip().add(Component.literal("  " + plan.outputEut() + " EU/t，堆芯产热 "
                    + operation.heatPerRodTick() * operation.bundleSize() * operation.rodsPerBatch()
                    * operation.activityMultiplier() + " H/t，工时 " + plan.ticks() + " tick"));
        }
        event.getToolTip().add(Component.translatable("hk3gtl.tooltip.reactor_fuel.settlement"));
    }
}
