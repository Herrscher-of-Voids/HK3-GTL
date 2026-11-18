package com.sirin.hk3gtl.common.event;

import com.sirin.hk3gtl.common.bootstrap.Hk3ModHealthReport;
import com.sirin.hk3gtl.common.bootstrap.Hk3WelcomeState;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.network.Hk3Network;
import com.sirin.hk3gtl.common.network.ModWelcomeS2CPacket;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.network.PacketDistributor;

/**
 * 
 * - 玩家首次进入世界或模组版本变更时，下发欢迎/加载状态弹窗。
 *
 */
@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class Hk3ModWelcomeHandler {

    private static final java.util.Map<java.util.UUID, String> OFFERED = new java.util.concurrent.ConcurrentHashMap<>();

    private Hk3ModWelcomeHandler() {}

    @SubscribeEvent
    public static void onPlayerLoggedIn(PlayerEvent.PlayerLoggedInEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) {
            return;
        }
        // 登录即同步一次注视度，保证 HUD 在进世界时立刻显示正确初值。
        com.sirin.hk3gtl.common.gaze.Hk3GazeManager.syncToClient(player);

        String current = ModList.get().getModContainerById(Hk3Constants.MOD_ID)
                .map(c -> c.getModInfo().getVersion().toString())
                .orElse("0.0.0");

        CompoundTag data = player.getPersistentData();
        if (!Hk3WelcomeState.unread(data, current)) {
            return;
        }
        send(player, current, false);
    }

    private static void send(ServerPlayer player,String current,boolean manual) {
        java.util.List<String> lines=new java.util.ArrayList<>(Hk3ModHealthReport.toStatusLines(current));
        lines.add(Hk3WelcomeState.first(player.getPersistentData()) ? "welcome:first" : "welcome:return");
        lines.add(manual ? "open:manual" : "open:login");
        lines.add("content:" + Hk3WelcomeState.contentId(current));
        OFFERED.put(player.getUUID(), Hk3WelcomeState.contentId(current));
        Hk3Network.CHANNEL.send(
                PacketDistributor.PLAYER.with(() -> player),
                new ModWelcomeS2CPacket(current, lines));
    }

    /** 说明页可随时重开；只有明确确认阅读才写入已读版本。 */
    @SubscribeEvent public static void register(net.minecraftforge.event.RegisterCommandsEvent event) {
        event.getDispatcher().register(net.minecraft.commands.Commands.literal("hk3updates")
                .executes(c->{
                    ServerPlayer p=c.getSource().getPlayerOrException();
                    String v=ModList.get().getModContainerById(Hk3Constants.MOD_ID).orElseThrow().getModInfo().getVersion().toString();
                    send(p,v,true);com.sirin.hk3gtl.common.phone.Hk3PhoneAppHints.opened(p,"updates");return 1;
                }).then(net.minecraft.commands.Commands.literal("acknowledge")
                .then(net.minecraft.commands.Commands.argument("content", com.mojang.brigadier.arguments.StringArgumentType.greedyString()).executes(c->{
                    ServerPlayer p=c.getSource().getPlayerOrException();
                    String v=ModList.get().getModContainerById(Hk3Constants.MOD_ID).orElseThrow().getModInfo().getVersion().toString();
                    String displayed=com.mojang.brigadier.arguments.StringArgumentType.getString(c,"content");
                    boolean accepted=Hk3WelcomeState.acknowledge(p.getPersistentData(),v,displayed,OFFERED.get(p.getUUID()));
                    if(accepted) OFFERED.remove(p.getUUID());
                    else c.getSource().sendFailure(net.minecraft.network.chat.Component.translatable("hk3gtl.welcome.ack_stale"));
                    return accepted?1:0;
                }))));
    }

    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent event) { OFFERED.remove(event.getEntity().getUUID()); }
    @SubscribeEvent public static void stop(net.minecraftforge.event.server.ServerStoppedEvent event) { OFFERED.clear(); }
}
