package com.sirin.hk3gtl.client.phone;

import com.sirin.hk3gtl.common.phone.Hk3PhoneDate;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;

/**
 * 复用手机外框显示服务器存档日历，不增加材质或修改应用排序。
 * 【变更记录 #1】2026-10-01 16:30:04（修订134）：删除无；新增首页日期入口对应的完整只读页面；修改无；用途：承接即死年原条件，说明游戏日历与现实日期的区别。
 */
final class Hk3PhoneDatePane {
    private Hk3PhoneDatePane() {}
    static void render(GuiGraphics gui, CompoundTag runtime, int x, int y) {
        var font=Minecraft.getInstance().font;
        var date=Hk3PhoneDate.from(runtime.getLong("SaveDayTime"));
        Component[] rows={Component.translatable("hk3gtl.phone.date.day",date.day()),
                Component.translatable("hk3gtl.phone.date.clock",date.clock()),
                Component.translatable("hk3gtl.phone.date.tick",date.tick()),
                Component.translatable("hk3gtl.phone.date.source"),
                Component.translatable("hk3gtl.phone.date.readonly")};
        int top=y+123;
        for(int i=0;i<rows.length;i++){
            for(var line:font.split(rows[i],288)){gui.drawString(font,line,x+12,top,i<3?Hk3PhoneStyle.GOLD:Hk3PhoneStyle.INK,false);top+=15;}
            top+=22;
        }
    }
}
