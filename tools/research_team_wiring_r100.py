from pathlib import Path
import shutil
R=Path(__file__).resolve().parents[1]
B=R/'logs/research-mainline-r100/before'
def edit(path,changes):
 p=R/path;t=p.read_text(encoding='utf-8-sig');b=B/path
 if not b.exists():b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,b)
 for a,z in changes:
  assert a in t,(path,a[:100]);t=t.replace(a,z)
 pos=t.index('\n',t.index('package '))+1
 t=t[:pos]+'\n/** 修订100 · 2026-09-29：接通团队研究归属、个人付款及真实实验来源。 */\n'+t[pos:]
 p.write_text(t,encoding='utf-8')
base='src/main/java/com/sirin/hk3gtl/'
edit(base+'common/machine/Hk3WorkableMultiblockMachine.java',[
 ('private UUID ownerUUID;','private UUID ownerUUID;\n    @Persisted @Nullable private UUID researchTeamUUID;'),
 ('    /** 双能源结算归属：','''    /** 研究归属首次绑定后固定；电网归属仍使用放置者。 */
    @Nullable public UUID getResearchTeamUUID() {
        if (researchTeamUUID==null && ownerUUID!=null && getLevel()!=null && !isRemote() && getLevel().getServer()!=null) {
            researchTeamUUID=com.sirin.hk3gtl.common.research.Hk3ResearchTeams.scope(getLevel().getServer(),ownerUUID);
            getHolder().markDirty();
        }
        return researchTeamUUID;
    }
    /** 双能源结算归属：'''),
 ('this.ownerUUID = player.getUUID();','this.ownerUUID = player.getUUID();\n            if (!isRemote()) getResearchTeamUUID();')])
edit(base+'common/communication/Hk3CommunicationData.java',[
 ('return player.server.overworld().getDataStorage().computeIfAbsent(', 'return get(player.server);\n    }\n    public static Hk3CommunicationData get(net.minecraft.server.MinecraftServer server) {\n        return server.overworld().getDataStorage().computeIfAbsent(')])
edit(base+'common/research/Hk3ResearchStartService.java',[
 ('        if (!available) return Result.UNAVAILABLE;','''        return start(player, Hk3ResearchTeams.scope(player.server,player.getUUID()), facility, lab, available, topicId, points, gaze);
    }
    public static Result start(ServerPlayer player, java.util.UUID owner, String facility, int lab, boolean available,
                               String topicId, boolean points, double gaze) {
        if (!available || !Hk3ResearchData.get(player).isMember(player.getUUID(),owner)) return Result.UNAVAILABLE;'''),
 ('        var owner = player.getUUID();',''),
 ('data.points(owner)','data.points(player.getUUID())'),
 ('data.startResearchWithPoints(owner,','data.startResearchWithPoints(owner, player.getUUID(),'),
 ('new Hk3ResearchWorkQueue.Quote(topicId, facility, lab, plan.ticks(), eut, "materials", payment.receipt()),','Hk3ResearchData.withPayer(new Hk3ResearchWorkQueue.Quote(topicId, facility, lab, plan.ticks(), eut, "materials", payment.receipt()), player.getUUID()),')])
edit(base+'common/research/Hk3ResearchManager.java',[
 ('Hk3ResearchData.get(player).permits(player.getUUID(), researchId)','Hk3ResearchData.get(player).permits(Hk3ResearchData.get(player).scope(player.getUUID()), researchId)'),
 ('research.completed(player.getUUID(), id)','research.completed(research.scope(player.getUUID()), id)'),
 ('research.canReconstruct(player.getUUID(), tier)','research.canReconstruct(research.scope(player.getUUID()), tier)')])
edit(base+'common/research/Hk3RecipeAccess.java',[
 ('            player = level.getServer().getPlayerList().getPlayer(owned.getOwnerUUID());','''            if (research.startsWith("RN-")) {
                var scope=owned.getResearchTeamUUID();
                return scope==null || !Hk3ResearchData.get(level.getServer()).permits(scope,research);
            }
            player = level.getServer().getPlayerList().getPlayer(owned.getOwnerUUID());''')])
edit(base+'common/machine/research/Hk3ResearchInstituteMachine.java',[
 ('''        ServerPlayer owner=getLevel().getServer().getPlayerList().getPlayer(getOwnerUUID());
        if (owner==null) return;
        var data=Hk3ResearchData.get(owner);
        double speed=Hk3ResearchMath.speed(lab, Math.max(0, Hk3GazeManager.getEffectiveGaze(owner)), 0, false, false);''','''        var server=getLevel().getServer(); var scope=getResearchTeamUUID();
        var online=Hk3ResearchTeams.online(server,scope);
        if (online.isEmpty()) return;
        var data=Hk3ResearchData.get(server);
        double speed=Hk3ResearchMath.speed(lab,Hk3ResearchTeams.gaze(server,scope),0,false,false);'''),
 ('data.activeResearch(owner.getUUID(), facility())','data.activeResearch(scope, facility())'),
 ('data.advanceResearch(owner.getUUID(), job.quote().topic(), facility(), owner.server.overworld().getGameTime(),','data.advanceResearch(scope, job.quote().topic(), facility(), server.overworld().getGameTime(),'),
 ('''                Hk3ResearchManager.syncClientResearchState(owner);
                com.sirin.hk3gtl.common.phone.Hk3PhoneService.notify(owner,
                        "research_"+job.quote().topic(),"研究完成",job.quote().topic());''','''                for (var member:online) {
                    Hk3ResearchManager.syncClientResearchState(member);
                    com.sirin.hk3gtl.common.phone.Hk3PhoneService.notify(member,
                            "research_"+job.quote().topic(),"研究完成",job.quote().topic());
                }'''),
 ('getOwnerUUID().equals(player.getUUID())','player instanceof ServerPlayer sp && Hk3ResearchData.get(sp).isMember(player.getUUID(),getResearchTeamUUID())'),
 ('var owner = server.getUUID();','var owner = getResearchTeamUUID();'),
 ('data.points(owner).toString()','data.points(server.getUUID()).toString()'),
 ('            view.putBoolean("running", job != null);','''            view.putBoolean("running", job != null);
            view.putBoolean("canCancel", job!=null && Hk3ResearchData.payer(owner,job.quote()).equals(server.getUUID()));
            view.putInt("refunds",data.refundItems(server.getUUID()).size());'''),
 ('            if ("toggle".equals(action))','''            if ("cancel".equals(action)) {
                Hk3ResearchData.get(server).cancelResearch(getResearchTeamUUID(),server.getUUID(),selected); return;
            }
            if ("claim".equals(action)) {
                Hk3ResearchData.get(server).claimRefunds(server.getUUID(),server.getInventory());
                server.inventoryMenu.broadcastChanges(); return;
            }
            if ("toggle".equals(action))'''),
 ('var id=server.getUUID();','var id=getResearchTeamUUID();'),
 ('Hk3ResearchStartService.start(player, facility(),','Hk3ResearchStartService.start(player, getResearchTeamUUID(), facility(),'),
 ('Math.max(0, Hk3GazeManager.getEffectiveGaze(player))','Hk3ResearchTeams.gaze(player.server,getResearchTeamUUID())'),
 ('Math.max(0,Hk3GazeManager.getEffectiveGaze(player))','Hk3ResearchTeams.gaze(player.server,getResearchTeamUUID())')])
edit(base+'common/machine/research/Hk3LiquidProcessMachine.java',[
 ('    /** 检查批次全部原配方权限','''    protected boolean hasObservationData() {
        return !isRemote() && getLevel()!=null && getLevel().getServer()!=null && getOwnerUUID()!=null
                && Hk3CommunicationData.get(getLevel().getServer()).state(getOwnerUUID()).hasObservationData();
    }
    private boolean researchAllowed(String id) {
        if (id.startsWith("RN-")) return getResearchTeamUUID()!=null
                && Hk3ResearchData.get(getLevel().getServer()).permits(getResearchTeamUUID(),id);
        var player=informedOwner(); return player!=null && Hk3ResearchManager.isCompleted(player,id);
    }
    /** 检查批次全部原配方权限'''),
 ('var owner=informedOwner();if(owner==null||recipe==null)return false;','if(!hasObservationData()||recipe==null)return false;'),
 ('Hk3ResearchManager.isCompleted(owner,id.getAsString())','researchAllowed(id.getAsString())'),
 ('Hk3ResearchManager.isCompleted(owner,gate)','researchAllowed(gate)'),
 ('var owner=informedOwner();if(owner==null||!isFormed())return;','if(!hasObservationData()||!isFormed()||getResearchTeamUUID()==null)return;\n        var owner=informedOwner();'),
 ('var data=Hk3ResearchData.get(owner);','var data=Hk3ResearchData.get(getLevel().getServer());'),
 ('if(data.recordExperiment(owner.getUUID(),topic))','if(data.recordExperiment(getResearchTeamUUID(),topic,getLevel().dimension().location()+"@"+getPos()+"/"+recipe.id) && owner!=null)')])
edit(base+'common/machine/research/Hk3HonkaiAbsorptionMachine.java',[
 ('    public void onSamplingOutputSettled(GTRecipe recipe) {','''    private boolean hasObservationData() {
        return getLevel()!=null && !isRemote() && getLevel().getServer()!=null && getOwnerUUID()!=null
                && Hk3CommunicationData.get(getLevel().getServer()).state(getOwnerUUID()).hasObservationData();
    }
    public void onSamplingOutputSettled(GTRecipe recipe) {'''),
 ('if (owner != null && Hk3ResearchData.get(owner).recordExperiment(owner.getUUID(), "RN-HED")) {','if (hasObservationData() && getResearchTeamUUID()!=null && Hk3ResearchData.get(getLevel().getServer()).recordExperiment(getResearchTeamUUID(), "RN-HED",getLevel().dimension().location()+"@"+getPos()+"/"+recipe.id) && owner!=null) {'),
 ('informedOwner() != null','hasObservationData()'),('informedOwner() == null','!hasObservationData()')])
edit(base+'common/machine/research/Hk3SpectrumAnalysisMachine.java',[
 ('if (player != null && Hk3ResearchData.get(player).recordExperiment(player.getUUID(), "RN-HSA")) {','if (hasObservationData() && getResearchTeamUUID()!=null && Hk3ResearchData.get(getLevel().getServer()).recordExperiment(getResearchTeamUUID(), "RN-HSA",getLevel().dimension().location()+"@"+getPos()+"/"+recipe.id) && player!=null) {'),
 ('informedOwner() != null','hasObservationData()'),('informedOwner() == null','!hasObservationData()')])

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
