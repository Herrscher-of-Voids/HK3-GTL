package com.sirin.hk3gtl.client.phone;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.network.chat.Component;
/**
 * 【变更记录 #1】2026-09-30 19:03:21（内测5修订114）
 * 删除：无；新增：讯息/笔记分层卡片按钮；修改：无；用途：完整命中区域和键盘焦点，不复制参考图私人内容。
 */
final class Hk3PhoneAppCard extends Button {
    private final String subtitle,badge;private final int accent;
    Hk3PhoneAppCard(String title,String subtitle,String badge,int x,int y,int w,int h,int accent,Runnable action){
        super(x,y,w,h,Component.literal(title),b->action.run(),DEFAULT_NARRATION);this.subtitle=subtitle;this.badge=badge;this.accent=accent;
    }
    @Override public void renderWidget(GuiGraphics g,int mx,int my,float delta){
        var font=Minecraft.getInstance().font;int x=getX(),y=getY(),w=getWidth(),h=getHeight();
        g.fill(x+3,y,x+w-3,y+h,isHoveredOrFocused()?0xFF354054:0xFF242A34);
        g.fill(x,y+3,x+w,y+h-3,isHoveredOrFocused()?0xFF354054:0xFF242A34);
        g.fill(x+8,y+10,x+11,y+h-10,accent);
        g.drawString(font,font.plainSubstrByWidth(getMessage().getString(),w-28),x+18,y+(h<45?5:10),0xFFF1EFF6,false);
        int line=0,max=Math.max(1,(h-46)/12);
        for(var part:font.split(Component.literal(subtitle),w-30)){if(line>=max)break;g.drawString(font,part,x+18,y+(h<45?21:26)+line++*12,0xFFAEB6C6,false);}
        if(!badge.isEmpty())g.drawString(font,font.plainSubstrByWidth(badge,w-28),x+18,y+h-15,accent,false);
    }
}
