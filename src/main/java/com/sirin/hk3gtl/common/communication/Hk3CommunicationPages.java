package com.sirin.hk3gtl.common.communication;

import com.mojang.brigadier.arguments.*;
import com.sirin.hk3gtl.common.research.*;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import java.util.*;

/** 【变更记录 #1】2026-10-01 00:56:35（修订124）：删除无；新增手机内的历史、个人目录与队长显式授权管理；修改操作使用当前团队及目标成员复核；用途：完整交流无需手打管理指令，每页不超过八个操作。 */
/** 【变更记录 #2】2026-10-01 01:01:52（修订124）：删除无；新增只读成员权限状态标签；修改不向普通成员显示可授权措辞；用途：界面与真实权限一致。 */
public final class Hk3CommunicationPages {
    private static final String ROOT="hk3letter diplomacy records";
    private Hk3CommunicationPages() {}
    private static UUID team(ServerPlayer p){return Hk3ResearchTeams.scope(p.server,p.getUUID());}
    public static int home(ServerPlayer p){
        if(!Hk3DiplomacyService.allowed(p))return 0;Hk3DiplomacyService.refresh(p);Hk3DiplomacyService.clearPreview(p.getUUID());
        var view=Hk3DiplomacyService.view("diplomacy");view.putString("Title","联络记录与授权");
        view.putString("Body","历史回看不改变立场；补谈写入本人经历。只有当前队长能授予或撤销团队答复权限。");
        Hk3DiplomacyService.button(view,"回看本队全部往来",ROOT+" history 0");
        Hk3DiplomacyService.button(view,"查看本人正式经历","hk3phone apps experience");
        Hk3DiplomacyService.button(view,"团队答复权限",ROOT+" permissions 0");
        Hk3DiplomacyService.button(view,"返回五方联络","hk3letter diplomacy");Hk3DiplomacyService.send(p,view);return 1;
    }
    public static int history(ServerPlayer p,int page){
        if(!Hk3DiplomacyService.allowed(p))return 0;Hk3DiplomacyService.refresh(p);Hk3DiplomacyService.clearPreview(p.getUUID());
        var docs=Hk3DiplomacyData.get(p.server).documents(team(p));int last=Math.max(0,(docs.size()-1)/5);page=Math.max(0,Math.min(last,page));
        var view=Hk3DiplomacyService.view("diplomacy");view.putString("Title","本队往来 · 第 "+(page+1)+" / "+(last+1)+" 页");
        view.putString("Body","回看已发生的正文和提交时保存的摘要。原队历史仍在个人收件箱，只能查看你已收到的信件。");
        for(String id:docs.stream().skip(page*5L).limit(5).toList())Hk3DiplomacyService.button(view,Hk3DiplomacyService.title(id),"hk3letter diplomacy read "+id);
        if(page>0)Hk3DiplomacyService.button(view,"上一页",ROOT+" history "+(page-1));
        if(page<last)Hk3DiplomacyService.button(view,"下一页",ROOT+" history "+(page+1));
        Hk3DiplomacyService.button(view,"返回联络记录",ROOT);Hk3DiplomacyService.send(p,view);return 1;
    }
    public static int permissions(ServerPlayer p,int page){
        if(!Hk3DiplomacyService.allowed(p))return 0;Hk3DiplomacyService.refresh(p);UUID team=team(p),owner=Hk3ResearchTeams.owner(p.server,team);
        var data=Hk3TeamContactData.get(p.server);var members=Hk3ResearchData.get(p).members(team).stream().filter(id->!id.equals(owner)).sorted().toList();
        int last=Math.max(0,(members.size()-1)/4);page=Math.max(0,Math.min(last,page));
        var view=Hk3DiplomacyService.view("diplomacy");view.putString("Title","答复权限 · 第 "+(page+1)+" / "+(last+1)+" 页");
        view.putString("Body",p.getUUID().equals(owner)?"你是本队队长。点击成员授予或撤销答复权限；职务不会自动授予此权限。离队或换队长后须重新授权。":"你可阅读权限；只有队长可以更改。本人补谈不需要团队答复授权。");
        for(UUID member:members.stream().skip(page*4L).limit(4).toList()){
            var online=p.server.getPlayerList().getPlayer(member);String name=online==null?"离线成员 "+member.toString().substring(0,8):online.getGameProfile().getName();
            boolean granted=data.canDecide(team,member,owner,true);
            String prefix=p.getUUID().equals(owner)?(granted?"撤销授权：":"授予授权："):(granted?"已授权：":"未授权：");
            Hk3DiplomacyService.button(view,prefix+name,p.getUUID().equals(owner)?ROOT+" grant "+team+" "+member+" "+!granted+" "+page:ROOT+" permissions "+page);
        }
        if(page>0)Hk3DiplomacyService.button(view,"上一页",ROOT+" permissions "+(page-1));
        if(page<last)Hk3DiplomacyService.button(view,"下一页",ROOT+" permissions "+(page+1));
        Hk3DiplomacyService.button(view,"返回联络记录",ROOT);Hk3DiplomacyService.send(p,view);return 1;
    }
    private static int grant(ServerPlayer p,String expectedTeam,String target,boolean grant,int page){
        if(!Hk3DiplomacyService.allowed(p))return 0;Hk3DiplomacyService.refresh(p);UUID team=team(p),member,expected;
        try{member=UUID.fromString(target);expected=UUID.fromString(expectedTeam);}catch(IllegalArgumentException bad){return 0;}
        if(!team.equals(expected)){p.sendSystemMessage(Component.literal("团队已变化，旧权限页面已失效。"));return home(p);}
        boolean ok=Hk3TeamContactData.get(p.server).delegate(team,p.getUUID(),Hk3ResearchTeams.owner(p.server,team),member,Hk3ResearchData.get(p).isMember(member,team),grant);
        if(ok){Hk3TeamContactService.clearPreview(member);Hk3DiplomacyService.clearPreview(member);}
        p.sendSystemMessage(Component.literal(ok?(grant?"已授权该成员代表本队答复。":"已撤销该成员答复权限，旧预览失效。"):"权限未改变：仅当前队长可操作本队成员，或已处于该状态。"));
        return permissions(p,page);
    }
    public static com.mojang.brigadier.builder.LiteralArgumentBuilder<net.minecraft.commands.CommandSourceStack> commands(){
        return Commands.literal("records").executes(c->home(c.getSource().getPlayerOrException()))
            .then(Commands.literal("history").then(Commands.argument("page",IntegerArgumentType.integer(0)).executes(c->history(c.getSource().getPlayerOrException(),IntegerArgumentType.getInteger(c,"page")))))
            .then(Commands.literal("permissions").then(Commands.argument("page",IntegerArgumentType.integer(0)).executes(c->permissions(c.getSource().getPlayerOrException(),IntegerArgumentType.getInteger(c,"page")))))
            .then(Commands.literal("grant").then(Commands.argument("team",StringArgumentType.word()).then(Commands.argument("target",StringArgumentType.word())
                .then(Commands.argument("grant",BoolArgumentType.bool()).then(Commands.argument("page",IntegerArgumentType.integer(0)).executes(c->grant(c.getSource().getPlayerOrException(),StringArgumentType.getString(c,"team"),StringArgumentType.getString(c,"target"),BoolArgumentType.getBool(c,"grant"),IntegerArgumentType.getInteger(c,"page"))))))));
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
