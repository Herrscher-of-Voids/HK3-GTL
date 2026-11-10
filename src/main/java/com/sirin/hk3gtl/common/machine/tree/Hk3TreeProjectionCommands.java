package com.sirin.hk3gtl.common.machine.tree;

import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.coordinates.BlockPosArgument;
import net.minecraft.network.chat.Component;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** 创造调试仍要求已成型的正式I34；仅选择光效，不授予工作成果。 */
@Mod.EventBusSubscriber(modid="hk3gtl")
public final class Hk3TreeProjectionCommands {
    private Hk3TreeProjectionCommands(){}
    @SubscribeEvent public static void register(RegisterCommandsEvent event){
        var at=Commands.argument("pos",BlockPosArgument.blockPos());
        for(var name:new String[]{"auto","idle","run","off","pause","resume"})at.then(Commands.literal(name).executes(c->{
            var player=c.getSource().getPlayerOrException();if(!player.isCreative()){c.getSource().sendFailure(Component.literal("树影工况调试仅供创造模式使用。"));return 0;}
            var pos=BlockPosArgument.getLoadedBlockPos(c,"pos");var block=c.getSource().getLevel().getBlockEntity(pos);
            if(!(block instanceof IMachineBlockEntity holder)||!(holder.getMetaMachine() instanceof Hk3TreeObservationMachine machine)||!machine.projectionFormed()){
                c.getSource().sendFailure(Component.literal("必须指定已通过真实GT检查的I34控制器；未更改成型、配方或研究。"));return 0;
            }
            switch(name){case "pause"->machine.pauseProjection(true);case "resume"->machine.pauseProjection(false);default->machine.setProjectionMode(switch(name){case "idle"->1;case "run"->2;case "off"->3;default->0;});}
            c.getSource().sendSuccess(()->Component.literal("I34树影调试："+name+"；实际GT成型有效，不计生产或研究成果。"),false);return 1;
        }));
        event.getDispatcher().register(Commands.literal("hk3treefx").requires(s->s.hasPermission(2)).then(at));
    }
}
