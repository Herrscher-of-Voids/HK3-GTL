package com.sirin.hk3gtl.client.phone;

/** 【变更记录 #1】2026-09-29 18:57:18（内测5修订95）：默认P键打开手机；按键可在控制设置修改，FCL可绑定屏幕按键。 */
import com.mojang.blaze3d.platform.InputConstants;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RegisterKeyMappingsEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.lwjgl.glfw.GLFW;

/**
 * 【变更记录 #2】2026-09-30 16:19:31（内测5修订110）
 * 删除：被新版通知读取流程替代的旧分支，历史备注保留。
 * 新增／修改：断开世界连接时清除客户端通知队列，防止跨服/跨存档泄漏旧消息。
 * 用途：通知与业务结果分离，服务端授权和个人持久化；不改结构、贴图和贸易。
 */
public final class Hk3PhoneKey {
    public static final KeyMapping OPEN=new KeyMapping("key.hk3gtl.phone",InputConstants.Type.KEYSYM,GLFW.GLFW_KEY_P,"key.categories.hk3gtl");
    @Mod.EventBusSubscriber(modid="hk3gtl",bus=Mod.EventBusSubscriber.Bus.MOD,value=Dist.CLIENT)
    public static final class Register {
        @SubscribeEvent public static void keys(RegisterKeyMappingsEvent e){e.register(OPEN);}
    }
    @Mod.EventBusSubscriber(modid="hk3gtl",value=Dist.CLIENT)
    public static final class Input {
        @SubscribeEvent public static void logout(net.minecraftforge.client.event.ClientPlayerNetworkEvent.LoggingOut e){Hk3PhoneScreen.reset();}
        @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){
            if(e.phase!=TickEvent.Phase.END)return;
            var mc=Minecraft.getInstance();
            while(OPEN.consumeClick())if(mc.player!=null&&mc.screen==null&&mc.getConnection()!=null)mc.getConnection().sendCommand("hk3phone");
        }
    }
}
