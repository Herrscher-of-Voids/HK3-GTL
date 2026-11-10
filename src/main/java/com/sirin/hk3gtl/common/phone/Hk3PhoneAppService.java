package com.sirin.hk3gtl.common.phone;
import com.sirin.hk3gtl.common.narrative.*;
import com.sirin.hk3gtl.common.research.*;
import net.minecraft.commands.Commands;
import net.minecraft.nbt.*;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import com.mojang.brigadier.arguments.*;
/**
 * 【变更记录 #1】2026-09-30 19:02:06（内测5修订114）
 * 删除：无；新增：私人笔记与文明档案手机入口；修改：无。
 * 用途：服务端校验手机、本人记录和版本；文明总览只读真实研究/卷轴，不改变进度，交易未接入。
 */
/** 【变更记录 #2】2026-09-30 23:43:42（修订120）：删除无；新增/修改：文明总览读取本队历史等级，八页里程碑逐项显示真实满足状态，服务器校验手机权限；用途：按真实团队事实展示文明进度，不给机器/配方增加等级锁。 */
/** 【变更记录 #3】2026-10-01 00:44:06（修订123）：删除无；新增/修改：手机读取统一的本人正式经历摘要，旧档案数量不当满级资格；用途：个人交流、团队决定及额外收藏分开，保留真实记录。 */
/** 【变更记录 #4】2026-10-01 01:54:14（修订127）：删除：被替代的旧分支；新增/修改：收藏按全部/可选/剧情/里程碑分页，同一本人记录与完整条件正文；用途：个人收藏与正式资格分离，保留历史记录。 */
/** 【变更记录 #5】2026-10-01 03:55:10（修订128）：删除：旧固定上限或被替代的分支；新增/修改：仅在笔记事务成功且不是删除操作之后提交彩蛋事实，拒绝失败请求解锁；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #6】2026-10-01 04:12:10（修订128）：删除：旧固定上限或被替代的分支；新增/修改：保存成功后统计正文指纹，重新打开只观察服务器保存的本人笔记；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #7】2026-10-01 04:27:55（修订128）：删除：旧固定上限或被替代的分支；新增/修改：笔记与文明总览真实打开回调，缺电拒绝请求不会计入；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #8】2026-10-01 04:30:25（修订128）：删除：旧固定上限或被替代的分支；新增/修改：已拥有收藏回看附正文身份，重复阅读按同一ID去重；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #9】2026-10-01 16:30:04（修订134）：删除无；新增经过安装/电量校验的真实日期页；修改即死年从本人已存笔记重检三项准备，不再等待缺失入口；用途：保持审核条件，只读存档时间且不产生死亡或时间变化。 */
/** 【变更记录 #10】2026-10-19 02:05:22（第10次备注 · 修订171）：删除无；新增机器总览分页、筛选和服务端详情；修改无；用途：读取当前团队索引，保持手机供电门槛，不同步他队位置、私人能源或库存，不提供远程机器控制。 */
/** 【变更记录 #11】2026-10-31 21:56:17（第11次备注 · 内测5修订191）：删除无；新增仅按发送人本人记录判断的版本冲突与记录存在标记；修改保存失败回包区分校验失败及旧版本，仍不返回他人正文；用途：让客户端保留草稿后明确选择重载或另存，不绕过供电、配额与CAS。 */
/** 【变更记录 #12】2026-11-04 06:12:50（第12次备注 · 内测5修订196）：删除64正式收藏手机目录的旧标题投影；新增共用新版标题和仅回看说明；修改普通收藏仍不创建正式阅读会话；用途：正文同源且旧标记不能授予本人正式资格。 */
/** 【变更记录 #13】2026-11-04（修订197）：删除无；新增文明里程碑当前核验等级及工程来源说明；修改仍只投影本队事实；用途：区分历史称号、当前资格和待接入来源。 */
/** 【变更记录 #14】2026-11-05 01:51:41（第14次备注 · 内测5修订204）：删除无；新增收藏搜索、保存版本只读笔记、第五百页说明和主动收藏命令；修改目录同步说明入口资格；用途：复用手机权限和阅读通道，搜索只包含本人已拥有条目。 */
public final class Hk3PhoneAppService {
    /** 【变更记录 #16】2026-11-05（修订207）：总览与阅读全文共用本队只读快照，全文阅读沿用原令牌及供电校验。 */
    /** 【变更记录 #15】2026-11-05（修订205）：新增颜色标签及个人待办命令；仅成功保存提交新事实，复用本人手机供电与CAS。 */
    private Hk3PhoneAppService(){}
    public static com.mojang.brigadier.builder.LiteralArgumentBuilder<net.minecraft.commands.CommandSourceStack> commands(){
        return Commands.literal("apps")
            .then(Commands.literal("gallery").executes(c->Hk3PhoneGallery.open(c.getSource().getPlayerOrException())))
            .then(Commands.literal("todos").executes(c->Hk3PhoneTodoService.open(c.getSource().getPlayerOrException(),0))
                .then(Commands.argument("page",IntegerArgumentType.integer(0)).executes(c->Hk3PhoneTodoService.open(c.getSource().getPlayerOrException(),IntegerArgumentType.getInteger(c,"page")))))
            .then(Commands.literal("checknote").then(Commands.argument("id",StringArgumentType.word()).then(Commands.argument("version",IntegerArgumentType.integer(1)).then(Commands.argument("done",BoolArgumentType.bool())
                .executes(c->Hk3PhoneTodoService.check(c.getSource().getPlayerOrException(),StringArgumentType.getString(c,"id"),IntegerArgumentType.getInteger(c,"version"),BoolArgumentType.getBool(c,"done")))))))
            .then(Commands.literal("collectionsearch").then(Commands.argument("page",IntegerArgumentType.integer(0)).then(Commands.argument("query",StringArgumentType.greedyString()).executes(c->Hk3PhoneCollectionService.search(c.getSource().getPlayerOrException(),IntegerArgumentType.getInteger(c,"page"),StringArgumentType.getString(c,"query"))))))
            .then(Commands.literal("readnote").then(Commands.argument("id",StringArgumentType.word()).executes(c->Hk3PhoneCollectionService.readNote(c.getSource().getPlayerOrException(),StringArgumentType.getString(c,"id")))))
            .then(Commands.literal("notenext").then(Commands.argument("token",StringArgumentType.word()).executes(c->Hk3PhoneCollectionService.nextNote(c.getSource().getPlayerOrException(),StringArgumentType.getString(c,"token")))))
            .then(Commands.literal("collectionexplanation").executes(c->Hk3PhoneCollectionService.explanation(c.getSource().getPlayerOrException())))
            .then(Commands.literal("collect").then(Commands.argument("token",StringArgumentType.word()).executes(c->Hk3PhoneCollectionService.collect(c.getSource().getPlayerOrException(),StringArgumentType.getString(c,"token")))))
            .then(Commands.literal("date").executes(c->date(c.getSource().getPlayerOrException())))
            .then(Commands.literal("notes").executes(c->notes(c.getSource().getPlayerOrException(),0))
                .then(Commands.argument("page",IntegerArgumentType.integer(0)).executes(c->notes(c.getSource().getPlayerOrException(),IntegerArgumentType.getInteger(c,"page")))))
            .then(Commands.literal("note").then(Commands.argument("id",StringArgumentType.word()).executes(c->note(c.getSource().getPlayerOrException(),StringArgumentType.getString(c,"id")))))
            .then(Commands.literal("experience").executes(c->experience(c.getSource().getPlayerOrException())))
            .then(Commands.literal("civilization").executes(c->civilization(c.getSource().getPlayerOrException())))
            .then(Commands.literal("civilizationread").executes(c->civilizationRead(c.getSource().getPlayerOrException())))
            .then(Commands.literal("machines").executes(c->machines(c.getSource().getPlayerOrException(),0,"all"))
                .then(Commands.literal("bind").executes(c->bindMachine(c.getSource().getPlayerOrException())))
                .then(Commands.argument("page",IntegerArgumentType.integer(0)).executes(c->machines(c.getSource().getPlayerOrException(),IntegerArgumentType.getInteger(c,"page"),"all"))
                    .then(Commands.argument("filter",StringArgumentType.word()).executes(c->machines(c.getSource().getPlayerOrException(),IntegerArgumentType.getInteger(c,"page"),StringArgumentType.getString(c,"filter"))))))
            .then(Commands.literal("machine").then(Commands.argument("id",StringArgumentType.word())
                .executes(c->machine(c.getSource().getPlayerOrException(),StringArgumentType.getString(c,"id"),0,"all"))
                .then(Commands.argument("page",IntegerArgumentType.integer(0)).executes(c->machine(c.getSource().getPlayerOrException(),StringArgumentType.getString(c,"id"),IntegerArgumentType.getInteger(c,"page"),"all"))
                    .then(Commands.argument("filter",StringArgumentType.word()).executes(c->machine(c.getSource().getPlayerOrException(),StringArgumentType.getString(c,"id"),IntegerArgumentType.getInteger(c,"page"),StringArgumentType.getString(c,"filter")))))))
            .then(Commands.literal("milestones").executes(c->milestones(c.getSource().getPlayerOrException(),0))
                .then(Commands.argument("page",IntegerArgumentType.integer(0)).executes(c->milestones(c.getSource().getPlayerOrException(),IntegerArgumentType.getInteger(c,"page")))))
            .then(Commands.literal("archive").executes(c->archive(c.getSource().getPlayerOrException(),0,"all"))
                .then(Commands.argument("page",IntegerArgumentType.integer(0)).executes(c->archive(c.getSource().getPlayerOrException(),IntegerArgumentType.getInteger(c,"page"),"all"))
                    .then(Commands.argument("filter",StringArgumentType.word()).executes(c->archive(c.getSource().getPlayerOrException(),IntegerArgumentType.getInteger(c,"page"),StringArgumentType.getString(c,"filter"))))))
            .then(Commands.literal("entry").then(Commands.argument("id",StringArgumentType.word()).executes(c->entry(c.getSource().getPlayerOrException(),StringArgumentType.getString(c,"id")))));
    }
    private static boolean allowed(ServerPlayer p){return Hk3PhoneData.get(p).installed(p.getUUID())&&Hk3PhoneRuntime.requirePower(p);}
    private static CompoundTag view(String mode){var v=new CompoundTag();v.putString("Mode",mode);return v;}
    static CompoundTag row(Hk3PhoneNotes.Note n){
        var r=new CompoundTag();r.putString("Id",n.id());r.putString("Title",n.title());r.putString("Body",n.body());r.putInt("Version",n.version());r.putLong("Time",n.time());
        r.putInt("Colors",n.colors());r.putBoolean("Task",n.task());r.putBoolean("Done",n.done());return r;
    }
    public static int notes(ServerPlayer p,int page){
        if(!allowed(p))return 0;var all=Hk3PhoneNotes.get(p).list(p.getUUID());var v=view("notes");
        com.sirin.hk3gtl.common.easter.Hk3EggPhone.opened(p,"notes");
        page=Math.min(Math.max(0,page),Math.max(0,(all.size()-1)/6));
        var rows=new ListTag();all.stream().skip(page*6L).limit(6).forEach(n->{var r=row(n);r.putString("Body",n.body().substring(0,Math.min(180,n.body().length())));rows.add(r);});
        v.putInt("Page",page);v.putInt("Total",all.size());v.put("Rows",rows);Hk3PhoneService.send(p,v);return 1;
    }
    private static int note(ServerPlayer p,String id){
        if(!allowed(p))return 0;var n=Hk3PhoneNotes.get(p).find(p.getUUID(),id);if(n==null)return 0;
        var v=row(n);v.putString("Mode","note");Hk3PhoneService.send(p,v);
        com.sirin.hk3gtl.common.easter.Hk3EggNotes.opened(p,n.title(),n.body());return 1;
    }
    public static void writeNote(ServerPlayer p,Hk3PhoneNotePacket request){
        if(!allowed(p)){error(p,"手机不可用，草稿仍保留；充电后再保存。");return;}
        var data=Hk3PhoneNotes.get(p);
        var saved=request.delete()?null:data.saveNote(p.getUUID(),request.id(),request.version(),request.title(),request.body(),p.server.overworld().getGameTime(),request.colors(),request.task());
        boolean ok=request.delete()?data.delete(p.getUUID(),request.id(),request.version()):saved!=null;
        if(!ok){
            var current=data.find(p.getUUID(),request.id());
            boolean conflict=!request.id().isEmpty()&&(current==null||current.version()!=request.version());
            var failure=view("app_error");
            failure.putString("Error",conflict?"笔记已变更或删除，草稿仍保留；可另存，或放弃草稿并重载。":"未保存：检查标题或笔记上限。草稿仍保留。");
            failure.putBoolean("NoteConflict",conflict);failure.putBoolean("NoteExists",current!=null);
            Hk3PhoneService.send(p,failure);return;
        }
        if(saved!=null){com.sirin.hk3gtl.common.easter.Hk3EggNotes.saved(p,saved.title(),saved.body());Hk3PhoneTodoService.saved(p,saved);}
        var ack=view("note_saved");Hk3PhoneService.send(p,ack);notes(p,0);
    }
    private static void error(ServerPlayer p,String message){var v=view("app_error");v.putString("Error",message);Hk3PhoneService.send(p,v);}
    private static int date(ServerPlayer p){
        if(!allowed(p))return 0;
        com.sirin.hk3gtl.common.easter.Hk3EggPhone.opened(p,"date");
        Hk3PhoneService.send(p,view("date"));
        if(com.sirin.hk3gtl.common.easter.Hk3EggScpFacts.hasEmergencyNote(Hk3PhoneNotes.get(p).list(p.getUUID())))
            com.sirin.hk3gtl.common.easter.Hk3EggVanilla.caseEvent(p,417);
        return 1;
    }
    private static int experience(ServerPlayer p){
        if(!allowed(p))return 0;var v=view("archive_detail");v.putString("Title","本人正式经历与待补项");
        v.putString("Body",Hk3PersonalArchive.summary(p));Hk3PhoneService.send(p,v);return 1;
    }
    private static int civilization(ServerPlayer p){
        if(!allowed(p))return 0;
        com.sirin.hk3gtl.common.easter.Hk3EggPhone.opened(p,"civilization");
        Hk3PhoneService.send(p,civilizationView(p));return 1;
    }
    private static int civilizationRead(ServerPlayer p){
        if(!allowed(p))return 0;return Hk3PhoneCivilizationReading.open(p,civilizationView(p));
    }
    private static CompoundTag civilizationView(ServerPlayer p){
        var data=Hk3ResearchData.get(p);var scope=Hk3ResearchTeams.scope(p.server,p.getUUID());var v=view("civilization");
        int done=0;for(String id:Hk3ResearchPlans.all().keySet())if(data.completed(scope,id))done++;
        v.putInt("ResearchDone",done);v.putInt("ResearchTotal",Hk3ResearchPlans.all().size());
        v.putInt("Archives",unlocked(p).size());v.putInt("ArchiveTotal",Hk3NarrativeNodes.totalCount());
        v.putInt("Members",data.members(scope).size());
        var status=com.sirin.hk3gtl.common.civ.Hk3CivilizationService.status(p);
        v.putString("CivilizationTitle",com.sirin.hk3gtl.common.civ.Hk3CivilizationRules.title(status.highest()));
        v.putInt("CivilizationVerified",status.currentlyVerified());
        return v;
    }
    private static int milestones(ServerPlayer p,int page){
        if(!allowed(p))return 0;
        var status=com.sirin.hk3gtl.common.civ.Hk3CivilizationService.status(p);
        page=Math.max(0,Math.min(7,page));var level=com.sirin.hk3gtl.common.civ.Hk3CivilizationRules.LEVELS.get(page);
        var v=view("civilization_milestones");v.putInt("Page",page);v.putInt("Total",8);
        v.putString("Title",com.sirin.hk3gtl.common.civ.Hk3CivilizationRules.title(page));
        v.putString("Highest",com.sirin.hk3gtl.common.civ.Hk3CivilizationRules.title(status.highest()));
        v.putInt("Current",status.currentlyVerified());
        var rows=new ListTag();for(var requirement:level.requirements()){
            var r=new CompoundTag();r.putString("Title",requirement.label());r.putBoolean("Done",status.facts().contains(requirement.key()));
            r.putString("Pending",com.sirin.hk3gtl.common.civ.Hk3CivilizationService.pendingSource(requirement.key()));rows.add(r);
        }v.put("Rows",rows);v.putBoolean("LowerReady",com.sirin.hk3gtl.common.civ.Hk3CivilizationRules.missingThrough(Math.max(0,page-1),status.facts()::contains).isEmpty());
        Hk3PhoneService.send(p,v);return 1;
    }
    private static int machines(ServerPlayer p,int page,String filter){
        if(!allowed(p)){error(p,"手机不可用；恢复供电后重新查询机器目录。");return 0;}
        if(!com.sirin.hk3gtl.common.overview.Hk3MachineOverviewData.validFilter(filter)){error(p,"机器目录筛选条件无效。");return 0;}
        var result=com.sirin.hk3gtl.common.overview.Hk3MachineOverviewService.page(p,page,filter);
        var v=view("machines");v.putInt("Page",result.page());v.putInt("PageSize",4);v.putInt("Total",result.total());v.putString("Filter",filter);
        var sources=new ListTag();for(var source:com.sirin.hk3gtl.common.overview.Hk3MachineOverviewService.sources(p))sources.add(net.minecraft.nbt.StringTag.valueOf(source));v.put("Sources",sources);
        var rows=new ListTag();for(var entry:result.rows())rows.add(machineRow(entry));v.put("Rows",rows);
        Hk3PhoneService.send(p,v);return 1;
    }
    private static int machine(ServerPlayer p,String rawId,int page,String filter){
        if(!allowed(p)){error(p,"手机不可用；恢复供电后重新查询机器详情。");return 0;}
        if(!com.sirin.hk3gtl.common.overview.Hk3MachineOverviewData.validFilter(filter)){error(p,"机器目录筛选条件无效。");return 0;}
        java.util.UUID id;try{id=java.util.UUID.fromString(rawId);}catch(IllegalArgumentException invalid){error(p,"机器记录标识无效，请重新打开目录。");return 0;}
        var entry=com.sirin.hk3gtl.common.overview.Hk3MachineOverviewService.detail(p,id);
        if(entry==null){error(p,"这台机器已移除，或不属于当前团队。");return 0;}
        var v=machineRow(entry);v.putString("Mode","machine_detail");v.putInt("Page",page);v.putString("Filter",filter);
        Hk3PhoneService.send(p,v);return 1;
    }
    private static int bindMachine(ServerPlayer p){
        if(!allowed(p)){error(p,"手机不可用；恢复供电后再登记机器。");return 0;}
        var hit=p.pick(8,0,false);
        if(!(hit instanceof net.minecraft.world.phys.BlockHitResult block)||!p.serverLevel().hasChunkAt(block.getBlockPos())
                ||!(p.serverLevel().getBlockEntity(block.getBlockPos()) instanceof com.gregtechceu.gtceu.api.machine.IMachineBlockEntity holder)
                ||!com.sirin.hk3gtl.common.overview.Hk3MachineOverviewService.bind(p,holder.getMetaMachine())){
            error(p,"未登记：请在八格内指向拥有访问权限的机器。已有团队归属不能覆盖。");return 0;
        }
        return machines(p,0,"all");
    }
    private static CompoundTag machineRow(com.sirin.hk3gtl.common.overview.Hk3MachineOverviewData.Entry entry){
        var v=new CompoundTag();var at=net.minecraft.core.BlockPos.of(entry.position());
        v.putString("Id",entry.id().toString());v.putString("Title",entry.descriptor().displayName());
        v.putString("Registry",entry.descriptor().registryId());v.putString("Module",entry.descriptor().module());
        v.putString("ControllerType",entry.descriptor().controllerType());v.putString("Dimension",entry.dimension());
        v.putInt("X",at.getX());v.putInt("Y",at.getY());v.putInt("Z",at.getZ());
        v.putString("State",entry.state().key());v.putString("StateLabel",entry.state().label());
        v.putString("Detail",entry.observation().detail());v.putLong("LastObserved",entry.observedAt());v.putBoolean("Loaded",entry.loaded());return v;
    }
    private static java.util.List<Hk3NarrativeNode> unlocked(ServerPlayer p){
        return Hk3CollectionRecords.unlocked(p.getPersistentData(),"all");
    }
    private static int archive(ServerPlayer p,int page,String filter){
        if(!allowed(p)||!Hk3CollectionCatalog.validFilter(filter))return 0;var all=Hk3CollectionRecords.unlocked(p.getPersistentData(),filter);page=Math.min(Math.max(0,page),Math.max(0,(all.size()-1)/8));
        var v=view("archive");v.putString("Filter",filter);v.putInt("Available",(int)Hk3CollectionRecords.total(filter));var rows=new ListTag();all.stream().skip(page*8L).limit(8).forEach(n->{var r=new CompoundTag();r.putString("Id",n.id());r.putString("Title",Hk3CollectionRecords.title(n,k->Component.translatable(k).getString()));rows.add(r);});
        v.put("Rows",rows);v.putInt("Page",page);v.putInt("Total",all.size());v.putBoolean("CollectionExplanation",Hk3PhoneCollectionService.discovered(p.getPersistentData()));Hk3PhoneService.send(p,v);return 1;
    }
    private static int entry(ServerPlayer p,String id){
        if(!allowed(p)||!Hk3NarrativeLog.isUnlocked(p,id))return 0;var n=Hk3NarrativeNodes.byId(id);if(n==null)return 0;
        var v=view("archive_detail");v.putString("Id","narrative_"+id);v.putString("Title",Hk3CollectionRecords.title(n,k->Component.translatable(k).getString()));
        String body=Hk3CollectionRecords.body(n,k->Component.translatable(k).getString());
        if(Hk3LegacyArchiveMigration.all().containsKey(n.unlockEventId()))body="仅回看；本次阅读不取得正式资格。正式全文请从手机通知进入。\n\n"+body;
        v.putString("Body",body);Hk3PhoneService.send(p,v);return 1;
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
