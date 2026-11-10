package com.sirin.hk3gtl.common.command;

import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.dialogue.DialogueSessionManager;
import com.sirin.hk3gtl.common.dialogue.definition.Hk3IfArchiveDialogue;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** 普通玩家可用的IF只读入口，不检查或扣除终审五次名额。 */
@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class Hk3IfArchiveCommand {
    private Hk3IfArchiveCommand() {}

    @SubscribeEvent
    public static void register(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("hk3if")
                .requires(source -> source.getEntity() instanceof ServerPlayer)
                .executes(context -> {
                    ServerPlayer player = context.getSource().getPlayerOrException();
                    if (DialogueSessionManager.startDialogue(player, Hk3IfArchiveDialogue.ID)) return 1;
                    context.getSource().sendFailure(Component.translatable("hk3gtl.dialogue.if_archive.busy"));
                    return 0;
                }));
    }
}
