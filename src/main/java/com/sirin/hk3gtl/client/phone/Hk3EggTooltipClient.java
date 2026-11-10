package com.sirin.hk3gtl.client.phone;
import net.minecraft.client.Minecraft;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraftforge.client.event.RenderTooltipEvent;
import net.minecraftforge.client.event.ScreenEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.api.distmarker.Dist;
import com.sirin.hk3gtl.common.network.Hk3Network;
import com.sirin.hk3gtl.common.easter.Hk3EggUiPacket;
@Mod.EventBusSubscriber(modid="hk3gtl",value=Dist.CLIENT)
/** 【变更记录 #1】2026-10-01 12:13:33（修订128）：删除：无；新增/修改：实际工具提示停留一秒与已打开GTLAdd指南页回执，服务端核对取得和当前持物；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public final class Hk3EggTooltipClient {
    private static String seen="";private static long start=-1,last=-1;
    private Hk3EggTooltipClient(){}
    @SubscribeEvent public static void tooltip(RenderTooltipEvent.Color e){
        var mc=Minecraft.getInstance();if(mc.level==null||mc.player==null||e.getItemStack().isEmpty())return;String id=BuiltInRegistries.ITEM.getKey(e.getItemStack().getItem()).toString();if(!id.equals("gtladditions:barnarda_data")&&!id.equals("gtladditions:create_data"))return;
        long now=mc.level.getGameTime();if(!seen.equals(id)||now<last||now-last>2){seen=id;start=now;}last=now;if(start>=0&&now-start>=20){Hk3Network.CHANNEL.sendToServer(new Hk3EggUiPacket("egg_tooltip",id));start=-1;}
    }
    @SubscribeEvent public static void screen(ScreenEvent.Render.Post e){
        var mc=Minecraft.getInstance();if(mc.level==null||mc.player==null||mc.level.getGameTime()%20!=0||!e.getScreen().getClass().getName().equals("guideme.internal.screen.GuideScreen"))return;
        try{Object page=e.getScreen().getClass().getMethod("getCurrentPageId").invoke(e.getScreen());if(page instanceof net.minecraft.resources.ResourceLocation id&&id.getNamespace().equals("gtladditions"))Hk3Network.CHANNEL.sendToServer(new Hk3EggUiPacket("egg_guide",id.toString()));}catch(ReflectiveOperationException ignored){/* 无兼容页面回执时不授收藏。 */}
    }
}
