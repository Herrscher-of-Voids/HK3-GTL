package com.sirin.hk3gtl.common.gaze;

import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.research.Hk3ResearchTeams;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;








@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class Hk3GazeEvents {
    private Hk3GazeEvents() {}
    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || event.getServer().getTickCount() % 20 != 0) return;
        for (var player : event.getServer().getPlayerList().getPlayers()) Hk3GazeManager.syncToClient(player);
    }
    @SubscribeEvent public static void commands(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("hk3gaze")
                .then(Commands.literal("status").executes(ctx -> {
                    var player = ctx.getSource().getPlayerOrException();
                    int team = (int) Hk3ResearchTeams.gaze(player.server, Hk3ResearchTeams.scope(player.server, player.getUUID()));
                    player.sendSystemMessage(Component.literal("注视度：个人 " + Hk3GazeManager.getGaze(player)
                            + "，有效 " + Hk3GazeManager.getEffectiveGaze(player) + "，在线团队最高 " + team
                            + "，缓冲" + (Hk3GazeManager.isBufferActive(player) ? "生效" : "未生效")
                            + "。S01免压；其他研究所按本机有效锚计算。"));
                    return 1;
                }))
                .then(Commands.literal("sources").executes(ctx -> {
                    var player = ctx.getSource().getPlayerOrException();
                    var list = Hk3GazeJournal.recent(player.getPersistentData());
                    if (list.isEmpty()) player.sendSystemMessage(Component.literal("暂无来源记录；旧档已有注视保留，不倒推或补扣历史。"));
                    for (int i = Math.max(0, list.size() - 10); i < list.size(); i++) {
                        var row = list.getCompound(i);
                        player.sendSystemMessage(Component.literal(row.getString("Source") + "：" + row.getInt("Before")
                                + " → " + row.getInt("After") + "（世界刻 " + row.getLong("Tick") + "）"));
                    }
                    return 1;
                })));
    }
}
