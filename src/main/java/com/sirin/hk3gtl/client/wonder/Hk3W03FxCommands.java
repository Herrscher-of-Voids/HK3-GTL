package com.sirin.hk3gtl.client.wonder;

import com.mojang.brigadier.arguments.DoubleArgumentType;
import net.minecraft.client.Minecraft;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RegisterClientCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** 明确的创造特效测试入口，不能提供配方、研究资格或成型状态。 */
@Mod.EventBusSubscriber(modid="hk3gtl",value=Dist.CLIENT)
public final class Hk3W03FxCommands {
    private Hk3W03FxCommands() {}
    @SubscribeEvent public static void commands(RegisterClientCommandsEvent event) {
        var root=Commands.literal("hk3w03fx").requires(s->Minecraft.getInstance().player!=null&&Minecraft.getInstance().player.isCreative());
        root.then(Commands.literal("show").then(Commands.argument("x",DoubleArgumentType.doubleArg(-29000000,29000000))
            .then(Commands.argument("y",DoubleArgumentType.doubleArg(-4096,4096))
            .then(Commands.argument("z",DoubleArgumentType.doubleArg(-29000000,29000000)).executes(c->{
                Hk3W03FxRenderer.show(new Vec3(DoubleArgumentType.getDouble(c,"x"),DoubleArgumentType.getDouble(c,"y"),DoubleArgumentType.getDouble(c,"z")));
                tell("W03 C9真实尺寸特效开始分帧上传；仅本客户端可见，未放置世界方块。" );return 1;
            })))));
        root.then(Commands.literal("hide").executes(c->{Hk3W03FxRenderer.hide();tell("C9特效已收起并释放GPU缓存。");return 1;}));
        root.then(Commands.literal("seek").then(Commands.argument("seconds",DoubleArgumentType.doubleArg(0,360)).executes(c->{Hk3W03FxRenderer.seek(DoubleArgumentType.getDouble(c,"seconds"));tell(Hk3W03FxRenderer.status());return 1;})));
        root.then(Commands.literal("play").executes(c->{Hk3W03FxRenderer.play();tell(Hk3W03FxRenderer.status());return 1;}));
        root.then(Commands.literal("status").executes(c->{tell(Hk3W03FxRenderer.status());return 1;}));
        event.getDispatcher().register(root);
    }
    private static void tell(String text){Minecraft.getInstance().player.displayClientMessage(Component.literal(text),false);}
}
