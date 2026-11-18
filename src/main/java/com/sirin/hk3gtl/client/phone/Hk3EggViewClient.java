package com.sirin.hk3gtl.client.phone;
import com.sirin.hk3gtl.common.easter.Hk3EggUiPacket;
import com.sirin.hk3gtl.common.network.Hk3Network;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.inventory.InventoryScreen;
import net.minecraft.world.item.Items;
import net.minecraftforge.client.event.ScreenEvent;
import net.minecraftforge.client.event.RenderHandEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.api.distmarker.Dist;
 
@Mod.EventBusSubscriber(modid="hk3gtl",value=Dist.CLIENT)
 
public final class Hk3EggViewClient {
    private static long lastMap=-1,lastUi=-1,lastDebug=-1;
    @SubscribeEvent public static void preview(ScreenEvent.Render.Post e){var mc=Minecraft.getInstance();if(mc.player==null||mc.level==null||mc.getConnection()==null)return;long now=mc.level.getGameTime();if(now==lastUi)return;lastUi=now;if(now%20==0&&e.getScreen() instanceof net.minecraft.client.gui.screens.inventory.AbstractContainerScreen<?> screen&&screen.getMenu() instanceof appeng.menu.me.items.PatternEncodingTermMenu)Hk3Network.CHANNEL.sendToServer(new Hk3EggUiPacket("egg_ae_preview",""));}
    @SubscribeEvent public static void coordinates(net.minecraftforge.client.event.RenderGuiEvent.Post e){var mc=Minecraft.getInstance();if(mc.player==null||mc.level==null||mc.getConnection()==null||!mc.options.renderDebug||mc.player.isReducedDebugInfo()||mc.options.reducedDebugInfo().get())return;long now=mc.level.getGameTime();if(now>=lastDebug&&now-lastDebug<20)return;lastDebug=now;Hk3Network.CHANNEL.sendToServer(new Hk3EggUiPacket("egg_coordinates",""));}

    private Hk3EggViewClient(){}
    @SubscribeEvent public static void screen(ScreenEvent.Init.Post e){if(e.getScreen() instanceof InventoryScreen&&Minecraft.getInstance().getConnection()!=null)Hk3Network.CHANNEL.sendToServer(new Hk3EggUiPacket("inventory",""));}
    @SubscribeEvent public static void map(RenderHandEvent e){
        var mc=Minecraft.getInstance();if(mc.player==null||mc.level==null||mc.getConnection()==null||e.isCanceled()||!e.getItemStack().is(Items.FILLED_MAP))return;
        long now=mc.level.getGameTime();if(now>=lastMap&&now-lastMap<20)return;lastMap=now;
        Hk3Network.CHANNEL.sendToServer(new Hk3EggUiPacket("map_view",""));
    }
}
