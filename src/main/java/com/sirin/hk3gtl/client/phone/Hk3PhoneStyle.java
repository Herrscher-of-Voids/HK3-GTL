package com.sirin.hk3gtl.client.phone;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.network.chat.Component;

/**
 * 【变更记录 #1】2026-09-30 18:18:05（内测5修订112）
 * 删除：无；新增：金属深色、紫金强调的统一通讯终端控件。
 * 修改：原版灰按钮改为自绘按钮；用途：主页、收件箱、信件与设置视觉一致。
 */
public final class Hk3PhoneStyle {
    public static final int INK=0xFFF0EBFA,MUTED=0xFFAEA5C2,GOLD=0xFFE1BE78,PURPLE=0xFFA687E8;
    private Hk3PhoneStyle(){}
    public static Button button(String text,int x,int y,int w,int h,Runnable action){
        return new Button(x,y,w,h,Component.literal(text),b->action.run(),supplier->supplier.get()){
            @Override public void renderWidget(GuiGraphics g,int mx,int my,float partial){
                boolean hover=isHoveredOrFocused();
                g.fill(getX(),getY(),getX()+getWidth(),getY()+getHeight(),active?(hover?0xFF39304F:0xFF242436):0xFF1B1C27);
                g.fill(getX(),getY(),getX()+2,getY()+getHeight(),active?(hover?GOLD:PURPLE):0xFF484350);
                if(hover&&active)g.fill(getX(),getY()+getHeight()-1,getX()+getWidth(),getY()+getHeight(),GOLD);
                var font=Minecraft.getInstance().font;
                g.drawString(font,font.plainSubstrByWidth(getMessage().getString(),getWidth()-16),getX()+9,getY()+(getHeight()-8)/2,active?INK:MUTED,false);
            }
        };
    }
    public static void card(GuiGraphics g,String title,String body,String footer){
        var font=Minecraft.getInstance().font;
        g.fill(0,0,218,64,0xF2181927);g.fill(0,0,3,64,PURPLE);
        g.fill(3,0,218,1,0xFF76618E);g.fill(8,8,12,12,GOLD);
        g.drawString(font,font.plainSubstrByWidth(title,190),17,7,GOLD,false);
        int line=0;
        for(var part:font.split(Component.literal(body),198)){
            if(line>=2)break;g.drawString(font,part,9,23+line++*10,INK,false);
        }
        g.drawString(font,font.plainSubstrByWidth(footer,198),9,50,MUTED,false);
    }
}
