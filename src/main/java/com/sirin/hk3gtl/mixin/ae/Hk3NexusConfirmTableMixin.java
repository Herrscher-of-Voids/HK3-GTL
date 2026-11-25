package com.sirin.hk3gtl.mixin.ae;

import appeng.api.stacks.AEKey;
import appeng.client.gui.me.crafting.CraftConfirmTableRenderer;
import appeng.core.localization.GuiText;
import appeng.menu.me.crafting.CraftingPlanSummaryEntry;
import com.sirin.hk3gtl.common.integration.ae.nexus.crafting.Hk3NexusPlanSummary;
import com.sirin.hk3gtl.common.integration.ae.Hk3AeAmountFormatter;
import com.sirin.hk3gtl.common.util.Hk3HonkaiEnergyFormatter;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.contents.TranslatableContents;
import org.gtlcore.gtlcore.integration.ae2.crafting.ICraftingPlanSummaryEntry;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.List;

@Mixin(value = CraftConfirmTableRenderer.class, priority = 900, remap = false)
public abstract class Hk3NexusConfirmTableMixin {
    @Inject(method = "getEntryOverlayColor(Lappeng/menu/me/crafting/CraftingPlanSummaryEntry;)I",
            at = @At("RETURN"), cancellable = true)
    private void hk3gtl$markCycle(CraftingPlanSummaryEntry entry, CallbackInfoReturnable<Integer> cir) {
        if (entry instanceof Hk3NexusPlanSummary.Entry exact && exact.cycle && exact.missing.signum() == 0)
            cir.setReturnValue(0x36FFD54F);
    }

    // 桥接方法在 GTL 可取消回调之后返回，保留其状态说明。
    @Inject(method = "getEntryDescription(Ljava/lang/Object;)Ljava/util/List;",
            at = @At("RETURN"), cancellable = true)
    private void hk3gtl$describeExact(Object value, CallbackInfoReturnable<List<Component>> cir) {
        var entry = (CraftingPlanSummaryEntry) value;
        var lines = hk3gtl$quantities(entry, true);
        cir.getReturnValue().stream().filter(line -> !hk3gtl$isQuantity(line)).forEach(lines::add);
        if (lines.isEmpty() && entry instanceof Hk3NexusPlanSummary.Entry exact && exact.cycle)
            lines.add(Component.translatable("hk3gtl.ae.cycle.entry"));
        cir.setReturnValue(lines);
    }

    @Inject(method = "getEntryTooltip(Ljava/lang/Object;)Ljava/util/List;",
            at = @At("RETURN"), cancellable = true)
    private void hk3gtl$tooltipExact(Object value, CallbackInfoReturnable<List<Component>> cir) {
        var entry = (CraftingPlanSummaryEntry) value;
        var lines = new ArrayList<>(cir.getReturnValue());
        lines.removeIf(Hk3NexusConfirmTableMixin::hk3gtl$isQuantity);
        lines.addAll(hk3gtl$quantities(entry, false));
        if (entry instanceof Hk3NexusPlanSummary.Entry exact && exact.cycle)
            lines.add(Component.translatable("hk3gtl.ae.cycle.entry").withStyle(ChatFormatting.GOLD));
        cir.setReturnValue(lines);
    }

    @Unique
    private static List<Component> hk3gtl$quantities(CraftingPlanSummaryEntry entry, boolean compact) {
        if (entry instanceof Hk3NexusPlanSummary.Entry exact)
            return hk3gtl$quantities(entry.getWhat(), exact.stored, exact.missing, exact.crafting, exact.operations, compact);
        return hk3gtl$quantities(entry.getWhat(), BigInteger.valueOf(entry.getStoredAmount()),
                BigInteger.valueOf(entry.getMissingAmount()), BigInteger.valueOf(entry.getCraftAmount()),
                BigInteger.valueOf(((ICraftingPlanSummaryEntry) entry).gtlcore$getCraftTimes()), compact);
    }

    @Unique
    private static List<Component> hk3gtl$quantities(AEKey key, BigInteger stored, BigInteger missing,
            BigInteger crafting, BigInteger operations, boolean compact) {
        var lines = new ArrayList<Component>();
        if (stored.signum() > 0) lines.add(GuiText.FromStorage.text(hk3gtl$amount(key, stored, compact)));
        if (missing.signum() > 0) lines.add(GuiText.Missing.text(hk3gtl$amount(key, missing, compact)));
        if (crafting.signum() > 0) lines.add(GuiText.ToCraft.text(hk3gtl$amount(key, crafting, compact)));
        if (operations.signum() > 0) {
            var color = operations.compareTo(BigInteger.valueOf(500)) < 0 ? ChatFormatting.DARK_GREEN
                    : operations.compareTo(BigInteger.valueOf(2000)) < 0 ? ChatFormatting.GOLD
                    : operations.compareTo(BigInteger.valueOf(6000)) < 0 ? ChatFormatting.RED : ChatFormatting.DARK_RED;
            lines.add(Component.translatable("gui.hk3gtl.nexus.craft_times", Component.literal(compact
                    ? Hk3AeAmountFormatter.compact(operations)
                    : Hk3HonkaiEnergyFormatter.formatFullGrouped(operations)).withStyle(color)));
        }
        return lines;
    }

    @Unique
    private static String hk3gtl$amount(AEKey key, BigInteger amount, boolean compact) {
        BigInteger unit = BigInteger.valueOf(key.getAmountPerUnit());
        String number = compact && amount.compareTo(unit.multiply(BigInteger.valueOf(1000))) >= 0
                ? Hk3AeAmountFormatter.compact(new BigDecimal(amount).divide(new BigDecimal(unit)))
                : new BigDecimal(amount).divide(new BigDecimal(unit)).stripTrailingZeros().toPlainString();
        return !compact && key.getUnitSymbol() != null ? number + " " + key.getUnitSymbol() : number;
    }

    @Unique
    private static boolean hk3gtl$isQuantity(Component line) {
        if (!(line.getContents() instanceof TranslatableContents text)) return false;
        String key = text.getKey();
        return key.equals(GuiText.FromStorage.getTranslationKey()) || key.equals(GuiText.Missing.getTranslationKey())
                || key.equals(GuiText.ToCraft.getTranslationKey()) || key.equals("gtlcore.ae.craft.create_times");
    }
}
