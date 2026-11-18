package com.sirin.hk3gtl.common.command;

import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.context.CommandContext;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import com.sirin.hk3gtl.common.machine.research.Hk3ResearchInstituteMachine;
import com.sirin.hk3gtl.common.research.Hk3W13ResearchData;
import com.sirin.hk3gtl.common.research.Hk3W13ResearchService;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.coordinates.BlockPosArgument;
import net.minecraft.network.chat.Component;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** 双方本人在各自主控旁确认；管理员权限和团队管理身份不代替私人供能许可。 */
@Mod.EventBusSubscriber(modid = "hk3gtl", bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class Hk3W13ResearchCommands {
    @SubscribeEvent public static void register(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("hk3w13")
                .then(Commands.argument("mother", BlockPosArgument.blockPos())
                .then(Commands.argument("lab", BlockPosArgument.blockPos())
                .then(Commands.literal("approve").executes(context -> execute(context, "approve")))
                .then(Commands.literal("revoke").executes(context -> execute(context, "revoke")))
                .then(Commands.literal("status").executes(context -> execute(context, "status")))
                .then(Commands.literal("priority").then(Commands.argument("value", IntegerArgumentType.integer())
                        .executes(context -> execute(context, "priority")))))));
    }
    private static int execute(CommandContext<CommandSourceStack> context, String action)
            throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        var player = context.getSource().getPlayerOrException();
        var motherPos = BlockPosArgument.getLoadedBlockPos(context, "mother");
        var labPos = BlockPosArgument.getLoadedBlockPos(context, "lab");
        var machine = MetaMachine.getMachine(player.level(), motherPos);
        var target = MetaMachine.getMachine(player.level(), labPos);
        if (!(machine instanceof Hk3WorkableMultiblockMachine mother)
                || !(target instanceof Hk3ResearchInstituteMachine lab)
                || Hk3W13ResearchService.mother(mother) == null || lab.getOwnerUUID() == null) {
            player.sendSystemMessage(Component.literal("需要已登记的真实W13主控和真实研究所；此命令不能创建母机。"));
            return 0;
        }
        var source = Hk3W13ResearchService.mother(mother);
        var receiver = lab.researchEndpoint();
        var actor = player.getUUID();
        boolean supplier = actor.equals(source.owner());
        boolean recipient = actor.equals(receiver.owner());
        if (!supplier && !recipient) {
            player.sendSystemMessage(Component.literal("只有双方机器的绑定人可以操作这条服务连接。"));
            return 0;
        }
        var data = Hk3W13ResearchData.get(player.server);
        if (!action.equals("status")) {
            var ownPos = supplier ? motherPos : labPos;
            if (player.distanceToSqr(ownPos.getX() + 0.5, ownPos.getY() + 0.5, ownPos.getZ() + 0.5) > 64) {
                player.sendSystemMessage(Component.literal("请靠近自己绑定的主控；优先级由W13付款人调整。"));
                return 0;
            }
            boolean changed = switch (action) {
                case "approve" -> data.approve(player.server, source, receiver, actor);
                case "revoke" -> data.revoke(source.id(), receiver.id(), actor);
                case "priority" -> data.priority(source.id(), receiver.id(), actor, IntegerArgumentType.getInteger(context, "value"));
                default -> false;
            };
            if (!changed) {
                player.sendSystemMessage(Component.literal("连接不存在或当前绑定人无权执行此操作。"));
                return 0;
            }
        }
        var link = data.link(source.id(), receiver.id());
        String status = link == null ? "尚未建立连接" : "供能同意=" + link.supply() + "；接入同意=" + link.receive()
                + "；授权有效=" + link.authorized(player.server) + "；研究所优先级=" + link.priority();
        int count = Hk3W13ResearchService.served(player.server, source.id());
        player.sendSystemMessage(Component.literal(status + "；当前服务=" + count + "/16；附加费用=" + count
                + "A(" + Hk3Values.getVN(Hk3W13ResearchService.RUNTIME_TIER) + ")/t＋" + (count * 256) + " HW/t；HW付款人=" + source.owner()));
        return 1;
    }
}
