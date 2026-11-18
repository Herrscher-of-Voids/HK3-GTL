package com.sirin.hk3gtl.client.phone;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import java.util.UUID;

 
final class Hk3PhoneAppHintClient {
    private UUID token;
    private String hover="";
    private long start,lastRead;
    void accept(CompoundTag view){token=view.hasUUID("AppHintToken")?view.getUUID("AppHintToken"):null;hover="";}
    private void send(String action,String app){if(token!=null)Hk3EggUiClient.send(action,token+","+app);}
    void tooltip(GuiGraphics g,String app,int mx,int my){
        long now=System.nanoTime()/1_000_000L;
        if(!app.equals(hover)){hover=app;start=lastRead=now;send("app_hint_hover",app);}
        if(app.isEmpty())return;
        var font=Minecraft.getInstance().font;
        g.renderTooltip(font,font.split(Component.translatable("hk3gtl.phone.app."+app+".hint"),196),mx,my);
        if(now-start>=1200&&now-lastRead>=1000){send("app_hint_read",app);lastRead=now;}
    }
    void launch(String app){send("app_hint_launch",app);}
    void removed(){send("app_hint_cancel","");hover="";token=null;}
}
