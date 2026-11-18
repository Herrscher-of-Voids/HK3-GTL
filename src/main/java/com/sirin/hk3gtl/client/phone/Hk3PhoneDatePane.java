package com.sirin.hk3gtl.client.phone;

import com.sirin.hk3gtl.common.phone.Hk3PhoneDate;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;

 



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
