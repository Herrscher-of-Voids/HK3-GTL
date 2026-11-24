package com.sirin.hk3gtl.mixin.ae;

import appeng.client.gui.NumberEntryType;
import appeng.client.gui.widgets.ConfirmableTextField;
import appeng.client.gui.widgets.NumberEntryWidget;
import appeng.client.gui.widgets.ValidationIcon;
import appeng.core.localization.GuiText;
import com.sirin.hk3gtl.client.ae.Hk3NexusNumberEntry;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactOrder;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.math.RoundingMode;
import java.util.ArrayList;
import java.util.Optional;
import java.util.OptionalInt;
import java.util.OptionalLong;
import java.util.regex.Pattern;

@Mixin(value = NumberEntryWidget.class, priority = 900, remap = false)
public abstract class Hk3NexusNumberEntryMixin implements Hk3NexusNumberEntry {
    @Unique private static final Pattern HK3GTL$EXACT_LITERAL = Pattern.compile(
            "([+]?(?:[0-9]+(?:\\.[0-9]*)?|\\.[0-9]+))(?:e([+-]?[0-9]{1,3}))?([KMBTPEZYRQ]?)", Pattern.CASE_INSENSITIVE);
    @Shadow @Final private ConfirmableTextField textField;
    @Shadow @Final private int errorTextColor;
    @Shadow @Final private int normalTextColor;
    @Shadow private NumberEntryType type;
    @Shadow private long minValue;
    @Shadow private ValidationIcon validationIcon;
    @Shadow private Optional<BigDecimal> getValueInternal() { return Optional.empty(); }
    @Unique private boolean hk3gtl$exact;

    @Override
    public void hk3gtl$enableExact() {
        if (hk3gtl$exact) return;
        hk3gtl$exact = true;
        textField.setMaxLength(Hk3ExactOrder.MAX_DECIMAL_DIGITS);
        textField.setValue(textField.getValue());
    }

    @Override
    public Optional<BigInteger> hk3gtl$exactValue() {
        return getValueInternal().map(value -> value.multiply(BigDecimal.valueOf(type.amountPerUnit()))
                .stripTrailingZeros()).filter(value -> value.scale() <= 0
                && value.compareTo(BigDecimal.valueOf(minValue)) >= 0
                && value.precision() - value.scale() <= Hk3ExactOrder.MAX_DECIMAL_DIGITS)
                .map(BigDecimal::toBigInteger);
    }

    @Override
    public void hk3gtl$setExactValue(BigInteger amount) {
        textField.setValue(new BigDecimal(amount).divide(BigDecimal.valueOf(type.amountPerUnit()))
                .stripTrailingZeros().toPlainString());
    }

    @Inject(method = "getValueInternal", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$parseExactLiteral(CallbackInfoReturnable<Optional<BigDecimal>> cir) {
        if (!hk3gtl$exact) return;
        String value = textField.getValue().trim();
        if (value.startsWith("=")) value = value.substring(1);
        var literal = HK3GTL$EXACT_LITERAL.matcher(value.trim());
        if (!literal.matches()) return;
        int exponent = literal.group(2) == null ? 0 : Integer.parseInt(literal.group(2));
        String suffix = literal.group(3);
        if (!suffix.isEmpty()) exponent += 3 * ("KMBTPEZYRQ".indexOf(Character.toUpperCase(suffix.charAt(0))) + 1);
        cir.setReturnValue(Optional.of(new BigDecimal(literal.group(1)).scaleByPowerOfTen(exponent)));
    }

    @Inject(method = "getLongValue", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$projectLong(CallbackInfoReturnable<OptionalLong> cir) {
        if (hk3gtl$exact) cir.setReturnValue(hk3gtl$exactValue()
                .map(value -> OptionalLong.of(value.min(BigInteger.valueOf(Long.MAX_VALUE)).longValue()))
                .orElseGet(OptionalLong::empty));
    }

    @Inject(method = "getIntValue", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$projectInt(CallbackInfoReturnable<OptionalInt> cir) {
        if (hk3gtl$exact) cir.setReturnValue(hk3gtl$exactValue()
                .map(value -> OptionalInt.of(value.min(BigInteger.valueOf(Integer.MAX_VALUE)).intValue()))
                .orElseGet(OptionalInt::empty));
    }

    @Inject(method = "setLongValue", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$setExactLong(long amount, CallbackInfo ci) {
        if (!hk3gtl$exact) return;
        hk3gtl$setExactValue(BigInteger.valueOf(Math.max(minValue, amount)));
        ci.cancel();
    }

    @Inject(method = "addQty", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$addExact(long delta, CallbackInfo ci) {
        if (!hk3gtl$exact) return;
        if (Screen.hasShiftDown()) {
            BigInteger value = hk3gtl$exactValue().orElse(BigInteger.ZERO);
            BigInteger changed = switch ((int) delta) {
                case 1 -> value.multiply(BigInteger.TWO);
                case 10 -> value.multiply(BigInteger.valueOf(5));
                case 100 -> value.add(BigInteger.valueOf(Integer.MAX_VALUE));
                case 1000 -> BigInteger.valueOf(Long.MAX_VALUE);
                case -1 -> value.divide(BigInteger.TWO);
                case -10 -> value.divide(BigInteger.valueOf(5));
                case -100 -> value.subtract(BigInteger.valueOf(Integer.MAX_VALUE));
                default -> BigInteger.ZERO;
            };
            hk3gtl$setExactValue(changed.max(BigInteger.ZERO));
        } else {
            BigDecimal current = getValueInternal().orElse(BigDecimal.ZERO);
            BigDecimal changed = current.add(BigDecimal.valueOf(delta));
            BigDecimal minimum = BigDecimal.valueOf(minValue).divide(BigDecimal.valueOf(type.amountPerUnit()))
                    .setScale(0, RoundingMode.CEILING);
            if (changed.compareTo(minimum) < 0) changed = minimum;
            else if (current.compareTo(BigDecimal.ONE) == 0 && delta > 0 && delta % 10 == 0)
                changed = changed.subtract(BigDecimal.ONE);
            textField.setValue(changed.stripTrailingZeros().toPlainString());
        }
        ci.cancel();
    }

    @Inject(method = "validate", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$validateExact(CallbackInfo ci) {
        if (!hk3gtl$exact) return;
        var errors = new ArrayList<Component>();
        var value = getValueInternal().map(amount -> amount.multiply(BigDecimal.valueOf(type.amountPerUnit()))
                .stripTrailingZeros());
        if (value.isEmpty()) errors.add(GuiText.InvalidNumber.text());
        else if (value.get().scale() > 0) errors.add(GuiText.NumberNonInteger.text());
        else if (value.get().compareTo(BigDecimal.valueOf(minValue)) < 0)
            errors.add(GuiText.NumberLessThanMinValue.text(minValue));
        else if (value.get().precision() - value.get().scale() > Hk3ExactOrder.MAX_DECIMAL_DIGITS)
            errors.add(Component.literal("数量最多 " + Hk3ExactOrder.MAX_DECIMAL_DIGITS + " 位"));
        boolean valid = errors.isEmpty();
        textField.setTextColor(valid ? normalTextColor : errorTextColor);
        textField.setTooltipMessage(errors);
        if (validationIcon != null) {
            validationIcon.setValid(valid);
            validationIcon.setTooltip(errors);
        }
        ci.cancel();
    }
}
