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

/**
 * 【变更记录 #1】2026-09-26 01:52:49（第 1 次备注 · 内测5修订74）
 * 删除：无。新增：正式电路的独立电压提示类。
 * 修改：参照整包GTL高阶电路的独立等级提示，使用安全long电压体系的显示接口。
 * 用途：注册ID与标签负责配方兼容，名称表达技术形态；客户端提示只读，不改变服务端等级。
 */
/**
 * 【变更记录 #2】2026-09-26 22:00:00（第 2 次备注 · 内测5修订75）
 * 删除：等级提示只使用固定电压颜色的显示方式。
 * 新增：负责人选择的系列主题色流动，使用逐字RGB色彩与连续时间变化。
 * 修改：只改变等级提示行，不附加电压到物品名称，不修改等级和标签。
 * 用途：颜色在系列主题附近流动；直接生成文字样式，避免混入GTL七彩代码。
 */
/**
 * 【变更记录 #3】2026-09-26 22:06:33（第 3 次备注 · 内测5修订75）
 * 删除：无。新增：六系列主题色。
 * 修改：13系列均使用负责人选择的主题色流动等级提示，保留正式电压名称。
 * 用途：新物品自动显示实际等级；普通机器标签兼容不受提示动画影响。
 */
/**
 * 【变更记录 #4】2026-09-30 03:22:49（内测5修订108）
 * 删除：13系列固定主题色。新增：按实际tier读取批准配色。
 * 修改：高阶提示保留轻微亮度流动；原版tier提示不变。
 * 用途：52种正式电路与电压色统一，等级和标签不变。
 */
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
