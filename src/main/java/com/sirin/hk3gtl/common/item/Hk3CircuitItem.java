package com.sirin.hk3gtl.common.item;

import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.constants.Hk3VoltagePalette;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import java.util.List;
import javax.annotation.Nullable;


























public final class Hk3CircuitItem extends Item {
    private final int tier;

    public Hk3CircuitItem(int tier) {
        super(new Item.Properties());
        this.tier = tier;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        super.appendHoverText(stack, level, tooltip, flag);
        // 未列入正式目录的历史占位物不推断等级；正式电路按稳定目录显示。
        if (tier >= 0) {
            String label=Component.translatable("hk3gtl.tooltip.circuit_voltage", Hk3Values.getVN(tier)).getString();
            tooltip.add(tier >= 15 ? paletteFlow(label, Hk3VoltagePalette.text(tier))
                    : themeFlow(label, 0x55CFE2));
        }
    }
    // 保留逐字亮度流动，只在主题色与少量白色之间呼吸，不再跨色相。
    private static Component paletteFlow(String text, int rgb) {
        double phase=(System.currentTimeMillis()%4800L)/4800.0*Math.PI*2;
        var line=Component.empty();
        int[] points=text.codePoints().toArray();
        for(int i=0;i<points.length;i++) {
            double light=.06*(1+Math.sin(i*.45-phase));
            int color=0;
            for(int shift:new int[]{16,8,0}) {
                int channel=(rgb>>shift)&255;
                color |= ((int)Math.round(channel+(255-channel)*light))<<shift;
            }
            final int rgbColor=color;
            line.append(Component.literal(new String(Character.toChars(points[i])))
                    .withStyle(style->style.withColor(rgbColor)));
        }
        return line;
    }
    private static Component themeFlow(String text,int rgb) {
        float[] hsv=java.awt.Color.RGBtoHSB((rgb>>16)&255,(rgb>>8)&255,rgb&255,null);
        double phase=(System.currentTimeMillis()%4800L)/4800.0*Math.PI*2;
        var line=Component.empty();
        int[] points=text.codePoints().toArray();
        for(int i=0;i<points.length;i++) {
            double wave=Math.sin(i*.45-phase);
            float hue=(float)((hsv[0]+.07*wave+1)%1);
            int color=java.awt.Color.HSBtoRGB(hue,.65F,(float)(.8+.2*wave*wave))&0xFFFFFF;
            line.append(Component.literal(new String(Character.toChars(points[i])))
                    .withStyle(style->style.withColor(color)));
        }
        return line;
    }
}
