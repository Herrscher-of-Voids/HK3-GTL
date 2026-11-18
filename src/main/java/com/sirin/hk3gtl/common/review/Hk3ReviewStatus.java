package com.sirin.hk3gtl.common.review;
import com.sirin.hk3gtl.common.research.Hk3ResearchTeams;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid="hk3gtl")
public final class Hk3ReviewStatus {
    private Hk3ReviewStatus(){}
    @SubscribeEvent public static void commands(RegisterCommandsEvent e){e.getDispatcher().register(Commands.literal("hk3review").executes(c->{
        var p=c.getSource().getPlayerOrException();var data=Hk3ReviewData.get(p.server);var scope=Hk3ResearchTeams.scope(p.server,p.getUUID());
        var snapshot=data.snapshot();
        for(var kind:Hk3ReviewLedger.Kind.values()){
            p.sendSystemMessage(Component.literal((kind==Hk3ReviewLedger.Kind.FIRST?"一审":"二审")+"：本队许可="+(data.settled(scope,kind)?"已取得":"未取得")+"，本人完整会面="+(data.experienced(p.getUUID(),kind)?"已完成":"未完成")));
            if(snapshot.qualified(scope,kind))p.sendSystemMessage(Component.literal("准入成果已核验并保存；不因停机失效。"));
            else for(String missing:Hk3ReviewQualification.inspect(p.server,scope,kind).missing())p.sendSystemMessage(Component.literal("尚缺："+missing));
        }
        p.sendSystemMessage(Component.translatable("hk3gtl.review.commands"));return 1;
    }).then(Commands.literal("first").executes(c->Hk3ReviewSessions.begin(c.getSource().getPlayerOrException(),Hk3ReviewLedger.Kind.FIRST)))
      .then(Commands.literal("second").executes(c->Hk3ReviewSessions.begin(c.getSource().getPlayerOrException(),Hk3ReviewLedger.Kind.SECOND)))
      .then(Commands.literal("watch").executes(c->Hk3ReviewSessions.watch(c.getSource().getPlayerOrException())))
      .then(Commands.literal("return").executes(c->Hk3ReviewSessions.returnNow(c.getSource().getPlayerOrException()))));}
}
