package com.sirin.hk3gtl.client.phone;


import com.mojang.blaze3d.platform.InputConstants;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RegisterKeyMappingsEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.lwjgl.glfw.GLFW;







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
