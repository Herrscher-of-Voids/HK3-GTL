package com.sirin.hk3gtl.common.command;

import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactOrder;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ProbabilityOrderService;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ProbabilityTerminalService;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.UuidArgument;
import net.minecraft.commands.arguments.coordinates.BlockPosArgument;
import net.minecraft.network.chat.Component;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import static com.sirin.hk3gtl.common.integration.ae.exact.Hk3ProbabilitySupport.AVAILABLE;
import net.minecraftforge.fml.common.Mod;

import java.io.IOException;
import java.math.BigInteger;

@Mod.EventBusSubscriber(modid = "hk3gtl")
public final class Hk3ProbabilityCommands {
    @SubscribeEvent public static void register(RegisterCommandsEvent event) {
        if (!AVAILABLE) return;
        var root = Commands.literal("hk3probability");
        for (String action : new String[]{"preview", "start"}) root.then(Commands.literal(action)
                .then(Commands.argument("controller", BlockPosArgument.blockPos())
                .then(Commands.argument("assembly", BlockPosArgument.blockPos())
                .then(Commands.argument("slot", IntegerArgumentType.integer(0))
                .then(Commands.argument("target", StringArgumentType.word())
                .then(Commands.argument("attempts", StringArgumentType.word()).executes(context -> {
                    var player = context.getSource().getPlayerOrException();
                    var controller = BlockPosArgument.getLoadedBlockPos(context, "controller");
                    var assembly = BlockPosArgument.getLoadedBlockPos(context, "assembly");
                    int slot = IntegerArgumentType.getInteger(context, "slot");
                    return reply(context.getSource(), () -> {
                        BigInteger target = Hk3ExactOrder.parsePositiveDecimal(StringArgumentType.getString(context, "target"));
                        BigInteger attempts = Hk3ExactOrder.parsePositiveDecimal(StringArgumentType.getString(context, "attempts"));
                        return action.equals("preview")
                            ? Hk3ProbabilityOrderService.preview(player,
                                    new Hk3ProbabilityOrderService.Candidate(controller, assembly, slot, ""), null, target, attempts)
                            : "专属概率订单：" + Hk3ProbabilityOrderService.start(player, controller, assembly, slot, target, attempts);
                    });
                })))))));
        for (String action : new String[]{"status", "cancel", "claim", "resume", "forget"}) {
            root.then(Commands.literal(action).then(Commands.argument("order", UuidArgument.uuid()).executes(context -> {
                var player = context.getSource().getPlayerOrException();
                var id = UuidArgument.getUuid(context, "order");
                return reply(context.getSource(), () -> switch (action) {
                    case "status" -> Hk3ProbabilityOrderService.status(player, id);
                    case "cancel" -> { Hk3ProbabilityOrderService.cancel(player, id); yield Hk3ProbabilityOrderService.status(player, id); }
                    case "claim" -> "已按AE实际接收量领取：" + Hk3ProbabilityOrderService.claim(player, id);
                    case "resume" -> { Hk3ProbabilityOrderService.resume(player, id); yield Hk3ProbabilityOrderService.status(player, id); }
                    default -> { Hk3ProbabilityOrderService.forget(player, id); yield "已移除无在途及无托管余额的终态订单"; }
                });
            })));
        }
        event.getDispatcher().register(root);
    }

    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent event) {
        if (AVAILABLE) {
            Hk3ProbabilityOrderService.tick(event);
            Hk3ProbabilityTerminalService.tick(event);
        }
    }

    @SubscribeEvent public static void stopped(ServerStoppedEvent event) {
        if (AVAILABLE) Hk3ProbabilityTerminalService.stopped(event);
    }

    @SubscribeEvent public static void loggedOut(PlayerEvent.PlayerLoggedOutEvent event) {
        if (AVAILABLE && event.getEntity() instanceof net.minecraft.server.level.ServerPlayer player)
            Hk3ProbabilityTerminalService.loggedOut(player);
    }

    private interface ThrowingAction { String get() throws IOException; }

    private static int reply(CommandSourceStack source, ThrowingAction action) {
        try {
            var message = Component.literal(action.get());
            source.sendSuccess(() -> message, false);
            return 1;
        } catch (IllegalArgumentException | IOException rejected) {
            source.sendFailure(Component.literal(rejected.getMessage()));
            return 0;
        }
    }
}
