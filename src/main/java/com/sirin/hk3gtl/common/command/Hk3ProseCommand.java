package com.sirin.hk3gtl.common.command;

import com.mojang.brigadier.arguments.StringArgumentType;
import com.sirin.hk3gtl.common.dialogue.DialogueSessionManager;
import com.sirin.hk3gtl.common.dialogue.definition.Hk3ApprovedDialogues;
import com.sirin.hk3gtl.common.narrative.Hk3ApprovedProse;
import net.minecraft.commands.Commands;
import net.minecraft.commands.SharedSuggestionProvider;
import net.minecraft.network.chat.Component;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * 管理员在游戏内校对全部已审核正文；没有解锁、贸易交付或审查结算副作用。
 * 【变更记录 #1】2026-09-29 17:51:46（内测5修订93）
 * 删除：无。新增：分页全文与两场会面预览命令。修改：无。用途：验证实际字体及分支。
 */
@Mod.EventBusSubscriber(modid="hk3gtl",bus=Mod.EventBusSubscriber.Bus.FORGE)
public final class Hk3ProseCommand {
    private Hk3ProseCommand() {}
    @SubscribeEvent public static void register(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("hk3text").requires(s->s.hasPermission(2))
            .executes(c->open(c.getSource().getPlayerOrException(),Hk3ApprovedDialogues.LIBRARY,"library"))
            .then(Commands.literal("second_review").executes(c->open(c.getSource().getPlayerOrException(),Hk3ApprovedDialogues.REVIEW_PREVIEW,"S201")))
            .then(Commands.literal("finale").executes(c->open(c.getSource().getPlayerOrException(),Hk3ApprovedDialogues.FINALE_PREVIEW,"F01")))
            .then(Commands.literal("read").then(Commands.argument("id",StringArgumentType.word())
                .suggests((c,b)->SharedSuggestionProvider.suggest(Hk3ApprovedProse.all().stream().map(Hk3ApprovedProse.Entry::id),b))
                .executes(c->{String id=StringArgumentType.getString(c,"id");
                    if(Hk3ApprovedProse.get(id)==null)return 0;
                    return open(c.getSource().getPlayerOrException(),Hk3ApprovedDialogues.LIBRARY,id);}))));
    }
    private static int open(net.minecraft.server.level.ServerPlayer player,String dialogue,String segment) {
        if(DialogueSessionManager.startAt(player,dialogue,segment,0))return 1;
        player.sendSystemMessage(Component.translatable("hk3gtl.dialogue.if_archive.busy"));return 0;
    }
}
