package com.sirin.hk3gtl.common.command;

import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import com.sirin.hk3gtl.common.machine.research.Hk3ResearchInstituteMachine;
import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import com.mojang.brigadier.arguments.StringArgumentType;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.coordinates.BlockPosArgument;
import net.minecraft.network.chat.Component;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.loading.FMLLoader;

@Mod.EventBusSubscriber(modid="hk3gtl", bus=Mod.EventBusSubscriber.Bus.FORGE)
public final class Hk3ResearchVerificationCommands {
    private Hk3ResearchVerificationCommands() {}
    @SubscribeEvent public static void register(RegisterCommandsEvent event) {
        if (FMLLoader.isProduction()) return;
        event.getDispatcher().register(Commands.literal("hk3researchverify")
            .requires(s -> s.hasPermission(2) && s.getEntity() instanceof net.minecraft.server.level.ServerPlayer p && p.isCreative())
            .then(Commands.literal("fixture").executes(c -> Hk3ResearchRuntimeCheck.begin(c.getSource().getPlayerOrException())))
            .then(Commands.literal("status").executes(c -> {
                var p=c.getSource().getPlayerOrException(); var d=Hk3ResearchData.get(p);
                c.getSource().sendSuccess(() -> Component.literal("RESEARCH points="+d.points(p.getUUID())+" evidence="+d.hasExperiment(p.getUUID(),"RN-HED")+" completed="+d.completed(p.getUUID(),"RN-HED")+" job="+d.researchJob(p.getUUID(),"RN-HED")),false); return 1;
            }))
            .then(Commands.literal("build").then(Commands.argument("pos",BlockPosArgument.blockPos()).executes(c -> {
                var p=c.getSource().getPlayerOrException(); var pos=BlockPosArgument.getLoadedBlockPos(c,"pos");
                var machine=MetaMachine.getMachine(p.level(),pos);
                if (!(machine instanceof MultiblockControllerMachine multiblock)) return 0;
                // 玩家明确指定控制器，沿用其注册Pattern，不创建替代占位建筑。
                multiblock.getPattern().autoBuild(p,multiblock.getMultiblockState());
                c.getSource().sendSuccess(() -> Component.literal("Pattern built; wait for actual formation check."),false);return 1;
            })))
            .then(Commands.literal("start").then(Commands.argument("pos",BlockPosArgument.blockPos())
                .then(Commands.argument("topic",StringArgumentType.word()).then(Commands.argument("payment",StringArgumentType.word()).executes(c -> {
                    var p=c.getSource().getPlayerOrException(); var machine=MetaMachine.getMachine(p.level(),BlockPosArgument.getLoadedBlockPos(c,"pos"));
                    if (!(machine instanceof Hk3ResearchInstituteMachine institute)) return 0;
                    var mode=StringArgumentType.getString(c,"payment"); if (!mode.equals("points") && !mode.equals("materials")) return 0;
                    var result=institute.requestResearch(p,StringArgumentType.getString(c,"topic"),mode.equals("points"));
                    c.getSource().sendSuccess(() -> Component.literal("RESEARCH_START="+result),false);return 1;
                }))))));
    }
}


