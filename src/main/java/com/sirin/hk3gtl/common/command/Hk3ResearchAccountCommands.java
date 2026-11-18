package com.sirin.hk3gtl.common.command;











import com.mojang.brigadier.arguments.StringArgumentType;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import com.sirin.hk3gtl.common.research.Hk3ResearchTeams;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.UuidArgument;
import net.minecraft.network.chat.Component;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** 修订100 · 2026-09-29：离队后仍能取消本人付款任务、领取原样退款，不要求管理员权限。 */
@Mod.EventBusSubscriber(modid=Hk3Constants.MOD_ID)






public final class Hk3ResearchAccountCommands {
    @SubscribeEvent public static void register(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("hk3research")
            .then(Commands.literal("bind").then(Commands.argument("pos",net.minecraft.commands.arguments.coordinates.BlockPosArgument.blockPos())
                .then(Commands.argument("member",net.minecraft.commands.arguments.EntityArgument.player()).executes(c -> {
                    var p=c.getSource().getPlayerOrException();
                    var target=net.minecraft.commands.arguments.EntityArgument.getPlayer(c,"member");
                    var pos=net.minecraft.commands.arguments.coordinates.BlockPosArgument.getLoadedBlockPos(c,"pos");
                    var machine=com.gregtechceu.gtceu.api.machine.MetaMachine.getMachine(p.level(),pos);
                    boolean ok=machine instanceof com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine owned
                            && owned.rebindResearchTeam(p,Hk3ResearchTeams.scope(p.server,target.getUUID()));
                    p.sendSystemMessage(Component.literal(ok?"机器研究归属已重新绑定；电网与个人账户归属不变。":"无法重绑：需要原队管理权限、靠近控制器且机器没有在研或运行批次。"));return ok?1:0;
                }))))
            .then(Commands.literal("account").executes(c -> {
                var p=c.getSource().getPlayerOrException(); Hk3ResearchTeams.refresh(p.server);
                var data=Hk3ResearchData.get(p);
                p.sendSystemMessage(Component.literal("个人研究点："+data.points(p.getUUID())+"；待领取物品组："+data.refundItems(p.getUUID()).size()));
                for (var entry:data.paidResearch(p.getUUID())) p.sendSystemMessage(Component.literal(
                        entry.snapshot().quote().topic()+" / "+entry.scope()+" / "+entry.snapshot().quote().facility()));
                return 1;
            }))
            .then(Commands.literal("claim").executes(c -> {
                var p=c.getSource().getPlayerOrException();
                int moved=com.sirin.hk3gtl.common.research.Hk3ResearchPayment.claimRefunds(p);
                p.inventoryMenu.broadcastChanges();
                p.sendSystemMessage(Component.literal("已领取 "+moved+" 件退款物品，放不下的仍保存在个人账本。")); return moved;
            }))
            .then(Commands.literal("cancel").then(Commands.argument("scope",UuidArgument.uuid())
                .then(Commands.argument("topic",StringArgumentType.word()).executes(c -> {
                    var p=c.getSource().getPlayerOrException();
                    boolean ok=Hk3ResearchData.get(p).cancelResearch(UuidArgument.getUuid(c,"scope"),p.getUUID(),StringArgumentType.getString(c,"topic"));
                    p.sendSystemMessage(Component.literal(ok?"研究已取消；点数退回个人账户，材料记入待领取账本。":"无法取消：任务不存在或你不是原付款人。"));
                    return ok?1:0;
                })))));
    }
}


