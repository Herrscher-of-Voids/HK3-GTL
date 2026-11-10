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
/** 【变更记录 #1】2026-10-01 05:04:18（修订128）：删除无；新增已打开背包/实际第一人称地图渲染提示；用途：只发动作名，服务器读取本人真实物品；不传分数、文件或完成编号。 */
@Mod.EventBusSubscriber(modid="hk3gtl",value=Dist.CLIENT)
/** 【变更记录 #2】2026-10-01 13:26:03（修订128）：删除：无；新增/修改：从实际画面渲染发送AE预览和非精简F3坐标回执，服务端仍校验菜单及真实传送记录；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
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
