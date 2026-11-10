package com.sirin.hk3gtl.client.phone;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import java.util.UUID;

/** 【变更记录 #1】2026-11-05（修订209）：复用原版全景作为相册页；仅真实渲染时发送可见回执，手动关闭与被动移除分开处理。 */
final class Hk3PhoneGalleryPane {
    private static final java.util.List<ResourceLocation> TEXTURES=java.util.stream.IntStream.range(0,4).mapToObj(i->new ResourceLocation("minecraft","textures/gui/title/background/panorama_"+i+".png")).toList();
    private UUID token;
    private long lastPulse;
    private int page;
    void accept(CompoundTag view){
        UUID next=view.getString("Mode").equals("gallery")&&view.hasUUID("GalleryToken")?view.getUUID("GalleryToken"):null;
        if(!java.util.Objects.equals(next,token)){cancel();token=next;page=0;lastPulse=Long.MIN_VALUE;}
    }
    private void send(String action){if(token!=null)Hk3EggUiClient.send(action,token.toString());}
    void init(Hk3PhoneScreen host,int x,int y){
        host.button("‹",x,y+475,70,()->page=Math.floorMod(page-1,4));
        host.button("›",x+242,y+475,70,()->page=(page+1)%4);
    }
    void render(GuiGraphics g,int x,int y){
        var font=Minecraft.getInstance().font;
        g.fill(x+12,y+124,x+300,y+412,0xFFE1DED5);
        g.blit(TEXTURES.get(page),x+16,y+128,280,280,0,0,1024,1024,1024,1024);
        g.drawCenteredString(font,Component.translatable("hk3gtl.phone.gallery.caption",page+1),x+156,y+428,Hk3PhoneStyle.INK);
        g.drawWordWrap(font,Component.translatable("hk3gtl.phone.gallery.note"),x+12,y+450,288,Hk3PhoneStyle.MUTED);
        long now=System.nanoTime()/1_000_000L;
        if(token!=null&&(lastPulse==Long.MIN_VALUE||now-lastPulse>=1000)){send("gallery_pulse");lastPulse=now;}
    }
    void close(){send("gallery_close");token=null;}
    void cancel(){send("gallery_cancel");token=null;}
}
