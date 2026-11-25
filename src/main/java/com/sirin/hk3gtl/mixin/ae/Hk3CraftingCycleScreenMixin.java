package com.sirin.hk3gtl.mixin.ae;

import appeng.api.stacks.AEKey;
import appeng.client.gui.AEBaseScreen;
import appeng.client.gui.Icon;
import appeng.client.gui.me.crafting.CraftConfirmScreen;
import appeng.client.gui.style.ScreenStyle;
import appeng.menu.me.crafting.CraftConfirmMenu;
import com.sirin.hk3gtl.common.integration.ae.Hk3AeAmountFormatter;
import com.sirin.hk3gtl.common.integration.ae.Hk3CraftingCycleFlag;
import com.sirin.hk3gtl.common.integration.ae.nexus.crafting.Hk3NexusPlanSummary;
import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.ComponentRenderUtils;
import net.minecraft.network.chat.Component;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.world.entity.player.Inventory;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.List;

@Mixin(value = CraftConfirmScreen.class, remap = false)
public abstract class Hk3CraftingCycleScreenMixin extends AEBaseScreen<CraftConfirmMenu> {
    @Unique private Hk3NexusPlanSummary.Cycle hk3gtl$cycle;
    @Unique private List<FormattedCharSequence> hk3gtl$cycleLines = List.of();
    @Unique private int hk3gtl$cycleOffset;

    protected Hk3CraftingCycleScreenMixin(CraftConfirmMenu menu, Inventory inventory,
                                        Component title, ScreenStyle style) {
        super(menu, inventory, title, style);
    }

    @Inject(method = "drawFG", at = @At("TAIL"))
    private void hk3gtl$drawCycle(GuiGraphics graphics, int offsetX, int offsetY,
                                 int mouseX, int mouseY, CallbackInfo ci) {
        var plan = getMenu().getPlan();
        var cycle = plan instanceof Hk3NexusPlanSummary summary ? summary.cycle : null;
        if (cycle == null && (plan == null || !((Hk3CraftingCycleFlag) plan).hk3gtl$hasCycles())) return;
        var label = Component.translatable(cycle == null ? "hk3gtl.ae.cycle.present" : "hk3gtl.ae.cycle.details");
        int x = imageWidth - font.width(label) - 24;
        Icon.SCHEDULING_ROUND_ROBIN.getBlitter().dest(x, 2).blit(graphics);
        graphics.drawString(font, label, x + 18, 6, cycle == null ? 0x404040 : 0x795400, false);
        if (!hk3gtl$overCycle(mouseX - offsetX, mouseY - offsetY, x)) return;

        graphics.pose().pushPose();
        graphics.pose().translate(-offsetX, -offsetY, 0);
        if (cycle == null) {
            drawTooltipWithHeader(graphics, mouseX, mouseY, List.of(label,
                    Component.translatable("hk3gtl.ae.cycle.description")));
        } else {
            if (cycle != hk3gtl$cycle) hk3gtl$setCycle(cycle);
            int maxOffset = hk3gtl$maxOffset();
            hk3gtl$cycleOffset = Math.min(hk3gtl$cycleOffset, maxOffset);
            int end = Math.min(hk3gtl$cycleLines.size(), hk3gtl$cycleOffset + hk3gtl$visibleLines());
            var lines = new ArrayList<FormattedCharSequence>();
            lines.add(label.withStyle(ChatFormatting.YELLOW).getVisualOrderText());
            lines.addAll(hk3gtl$cycleLines.subList(hk3gtl$cycleOffset, end));
            if (maxOffset > 0) lines.add(Component.translatable("hk3gtl.ae.cycle.scroll",
                    hk3gtl$cycleOffset + 1, end, hk3gtl$cycleLines.size()).getVisualOrderText());
            graphics.renderTooltip(font, lines, mouseX, mouseY);
        }
        graphics.pose().popPose();
    }

    @Override
    public boolean mouseScrolled(double mouseX, double mouseY, double delta) {
        if (getMenu().getPlan() instanceof Hk3NexusPlanSummary summary && summary.cycle != null
                && hk3gtl$overCycle(mouseX - leftPos, mouseY - topPos,
                        imageWidth - font.width(Component.translatable("hk3gtl.ae.cycle.details")) - 24)) {
            if (summary.cycle != hk3gtl$cycle) hk3gtl$setCycle(summary.cycle);
            hk3gtl$cycleOffset = Math.max(0, Math.min(hk3gtl$maxOffset(), hk3gtl$cycleOffset + (delta > 0 ? -3 : 3)));
            return true;
        }
        return super.mouseScrolled(mouseX, mouseY, delta);
    }

    @Unique private boolean hk3gtl$overCycle(double x, double y, int left) {
        return x >= left && x < imageWidth - 6 && y >= 2 && y < 18;
    }

    @Unique private int hk3gtl$visibleLines() { return Math.max(1, (height - 48) / 10); }

    @Unique private int hk3gtl$maxOffset() { return Math.max(0, hk3gtl$cycleLines.size() - hk3gtl$visibleLines()); }

    @Unique private void hk3gtl$setCycle(Hk3NexusPlanSummary.Cycle cycle) {
        hk3gtl$cycle = cycle;
        hk3gtl$cycleOffset = 0;
        var lines = new ArrayList<Component>();
        if (!cycle.reason().isEmpty()) lines.add(Component.literal(cycle.reason()));
        cycle.missing().forEach((key, amount) -> lines.add(Component.translatable("hk3gtl.ae.cycle.missing",
                key.getDisplayName(), hk3gtl$amount(key, amount)).withStyle(ChatFormatting.RED)));
        int index = 1;
        for (var step : cycle.steps()) {
            lines.add((step.batches().signum() > 0
                    ? Component.translatable("hk3gtl.ae.cycle.batches", index, Hk3AeAmountFormatter.compact(step.batches()))
                    : Component.translatable("hk3gtl.ae.cycle.step", index)).withStyle(ChatFormatting.GOLD));
            index++;
            step.inputs().forEach((key, amount) -> lines.add(hk3gtl$material("hk3gtl.ae.cycle.input", key, amount, step.batches())));
            step.outputs().forEach((key, amount) -> lines.add(hk3gtl$material("hk3gtl.ae.cycle.output", key, amount, step.batches())));
        }
        hk3gtl$cycleLines = lines.stream().flatMap(line -> ComponentRenderUtils.wrapComponents(
                line, Math.max(100, width / 2 - 40), font).stream()).toList();
    }

    @Unique private static Component hk3gtl$material(String label, AEKey key, BigInteger amount, BigInteger batches) {
        var line = Component.translatable(label, key.getDisplayName(), hk3gtl$amount(key, amount));
        if (batches.compareTo(BigInteger.ONE) > 0) line.append(Component.translatable(
                "hk3gtl.ae.cycle.total", hk3gtl$amount(key, amount.multiply(batches))));
        return line;
    }

    @Unique private static String hk3gtl$amount(AEKey key, BigInteger amount) {
        var quantity = new BigDecimal(amount).divide(BigDecimal.valueOf(key.getAmountPerUnit()));
        String number = quantity.abs().compareTo(BigDecimal.valueOf(1000)) < 0
                ? quantity.stripTrailingZeros().toPlainString() : Hk3AeAmountFormatter.compact(quantity);
        String symbol = key.getUnitSymbol();
        return symbol == null ? number : number + " " + symbol;
    }
}
