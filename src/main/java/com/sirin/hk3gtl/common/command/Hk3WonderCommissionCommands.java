package com.sirin.hk3gtl.common.command;

import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.sirin.hk3gtl.common.machine.Hk3CommissionMachine;
import com.sirin.hk3gtl.common.machine.w03.Hk3W03Machine;
import com.sirin.hk3gtl.common.multiblock.build.Hk3UniversalTerminalBuilder;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.coordinates.BlockPosArgument;
import net.minecraft.network.chat.Component;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** 创造验收入口复用主控按钮，不跳过搭建、完整实读或GT成型检查。 */
@Mod.EventBusSubscriber(modid="hk3gtl",bus=Mod.EventBusSubscriber.Bus.FORGE)
public final class Hk3WonderCommissionCommands {
    @SubscribeEvent public static void register(RegisterCommandsEvent event){
        event.getDispatcher().register(Commands.literal("hk3wonder").requires(s->s.hasPermission(2))
            .then(Commands.argument("controller",BlockPosArgument.blockPos())
            .then(Commands.argument("action",StringArgumentType.word())
            .suggests((c,b)->{for(String s:new String[]{"status","build","check","toggle"})b.suggest(s);return b.buildFuture();})
            .executes(c->{
                var source=c.getSource();var player=source.getPlayerOrException();
                if(!player.isCreative()){source.sendFailure(Component.literal("仅创造验收使用"));return 0;}
                var pos=BlockPosArgument.getLoadedBlockPos(c,"controller");
                var machine=MetaMachine.getMachine(source.getLevel(),pos);
                if(!(machine instanceof Hk3CommissionMachine)&&!(machine instanceof Hk3W03Machine)){
                    source.sendFailure(Component.literal("此处不是W01–W03真实主控"));return 0;
                }
                var control=(com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine)machine;
                String action=StringArgumentType.getString(c,"action");
                switch(action){
                    case "status" -> {}
                    case "build" -> Hk3UniversalTerminalBuilder.use(player,control.getMultiblockState(),null);
                    case "check" -> {if(machine instanceof Hk3CommissionMachine m)m.requestIntegrityCheck();else ((Hk3W03Machine)machine).requestIntegrityCheck();}
                    case "toggle" -> {if(machine instanceof Hk3CommissionMachine m)m.toggleCommission(player);else ((Hk3W03Machine)machine).toggleField(player);}
                    default -> {source.sendFailure(Component.literal("操作：status、build、check、toggle"));return 0;}
                }
                String state=machine instanceof Hk3CommissionMachine m?m.commissionStatus()+"；运行="+m.commissioning()+"；tick="+m.commissionTicks():((Hk3W03Machine)machine).commissionStatus();
                String message="奇观验收 "+pos.toShortString()+"；formed="+control.isFormed()+"；"+state+"；"+Hk3UniversalTerminalBuilder.progress(control);
                source.sendSuccess(()->Component.literal(message),false);
                com.mojang.logging.LogUtils.getLogger().info(message);return 1;
            }))));
    }
}
