package com.sirin.hk3gtl.test.civ;
import com.sirin.hk3gtl.common.civ.*;
import com.sirin.hk3gtl.common.research.*;
import com.sirin.hk3gtl.common.review.*;
import net.minecraft.nbt.*;
import java.util.*;

/** 【变更记录 #1】2026-09-30 23:46:03（修订120）：删除无；新增累计条件、真实来源过滤、200团队隔离与损坏记录测试；修改无；用途：断言不等于C7工程或主线已能游玩。 */
/** 【变更记录 #2】2026-11-04（修订197）：删除无；新增回信授权、查询只读、换队回队重启、当前缺项及损坏UUID回归；修改有效回信夹具携带团队授权；用途：核验账本边界，不代替工程运行验收。 */
public final class CivilizationTest {
    private static int checks;
    private static void check(boolean ok,String message){if(!ok)throw new AssertionError(message);checks++;}
    public static void main(String[] args){
        check(Hk3CivilizationRules.LEVELS.size()==8,"八级");var facts=new HashSet<String>();
        for(int level=0;level<8;level++){
            for(var r:Hk3CivilizationRules.LEVELS.get(level).requirements())facts.add(r.key());
            check(Hk3CivilizationRules.achieved(facts::contains)==level,"逐级累计"+level);
            check(Hk3CivilizationRules.missingThrough(level,facts::contains).isEmpty(),"已满足条件无缺项");
            for(var r:Hk3CivilizationRules.LEVELS.get(level).requirements()){
                facts.remove(r.key());check(Hk3CivilizationRules.achieved(facts::contains)<level,"任何必需成果缺失都不能升级");facts.add(r.key());
            }
        }
        var peak=new Hk3CivilizationData();UUID a=UUID.randomUUID(),b=UUID.randomUUID();
        check(peak.observe(a,facts::contains)==7,"合成完整条件仅用于测试最高级");
        check(peak.observe(a,k->false)==7&&peak.highest(b)==0,"本队不降级，换队不继承");
        peak=Hk3CivilizationData.load(peak.save(new CompoundTag()));check(peak.highest(a)==7&&peak.highest(b)==0,"重启保留归属");
        var snapshot=peak.save(new CompoundTag());snapshot.getCompound("Teams").putInt(a.toString(),0);check(peak.highest(a)==7,"存盘副本无写穿");
        for(int i=0;i<200;i++){UUID team=new UUID(2,i);int level=i%8;var partial=new HashSet<String>();for(int l=0;l<=level;l++)for(var r:Hk3CivilizationRules.LEVELS.get(l).requirements())partial.add(r.key());check(peak.observe(team,partial::contains)==level,"200团队历史独立");}
        peak=Hk3CivilizationData.load(peak.save(new CompoundTag()));for(int i=0;i<200;i++)check(peak.highest(new UUID(2,i))==i%8,"200团队重启隔离");
        var malformed=peak.save(new CompoundTag());malformed.getCompound("Teams").putInt(a.toString(),8);expectFailure(()->Hk3CivilizationData.load(malformed));
        expectFailure(()->Hk3CivilizationData.load(new CompoundTag()));
        var badId=new CompoundTag();badId.putInt("Version",1);var badTeams=new CompoundTag();badTeams.putInt("1-1-1-1-1",1);badId.put("Teams",badTeams);
        expectFailure(()->Hk3CivilizationData.load(badId));
        badTeams.remove("1-1-1-1-1");badTeams.putInt("invalid",1);expectFailure(()->Hk3CivilizationData.load(badId));
        var research=new Hk3ResearchData();var review=new Hk3ReviewData();
        check(Hk3CivilizationRules.achieved(Hk3CivilizationService.facts(research,review,a)::contains)==0,"新队C0");
        var communication=Hk3CommunicationResearchProof.receipt(UUID.randomUUID(),a,false,1);
        research.recordProcessFact(a,"formal_communication",communication);
        check(!Hk3CivilizationService.facts(research,review,a).contains("contact"),"旧个人回信缺团队授权不能提升文明");
        // 合法团队回信由首信账本携带授权字段；不修改首信迁移与结算行为。
        var authorized=communication.copy();authorized.putString("Authority","team_owner_or_explicit_delegate");
        research=new Hk3ResearchData();check(research.recordFormalCommunication(a,authorized),"正式团队回信可正常入账");
        research.recordExperiment(a,"RN-HED","test-real-sampling");research.recordExperiment(a,"RN-HSA","test-real-spectrum");
        check(Hk3CivilizationRules.achieved(Hk3CivilizationService.facts(research,review,a)::contains)==0,"真实证据不代替付款研究");
        research.recordCompletion(a,"RN-HED",1);
        check(Hk3CivilizationRules.achieved(Hk3CivilizationService.facts(research,review,a)::contains)==1,"拒绝合作的有效回信同样可达C1");
        var history=new Hk3CivilizationData();var before=history.save(new CompoundTag());
        var status=Hk3CivilizationService.status(research,review,history,a);
        check(status.highest()==0&&status.currentlyVerified()==1&&history.save(new CompoundTag()).equals(before),"查询只读，不提升历史");
        history.observe(a,status.facts()::contains);
        research.reconcileTeams(Map.of(a,b),Set.of(b));
        status=Hk3CivilizationService.status(research,review,history,research.scope(a));
        check(status.team().equals(b)&&status.highest()==0&&status.currentlyVerified()==0&&!status.facts().contains("contact"),"换队继承知识但不带旧队文明或外交");
        check(status.nextTarget()==1&&status.missing().stream().anyMatch(r->r.key().equals("contact")),"新队按当前事实报告C1缺项");
        research.reconcileTeams(Map.of(a,a),Set.of());
        research=Hk3ResearchData.load(research.save(new CompoundTag()));history=Hk3CivilizationData.load(history.save(new CompoundTag()));
        status=Hk3CivilizationService.status(research,review,history,research.scope(a));
        check(status.highest()==1&&status.currentlyVerified()==1,"离线重启后回原队保留原队归属");
        var regressed=Hk3CivilizationService.status(new Hk3ResearchData(),review,history,a);
        check(regressed.highest()==1&&regressed.currentlyVerified()==0&&regressed.nextTarget()==1&&!regressed.missing().isEmpty(),"历史最高不替代当前资格或缺项目标");
        check(Hk3CivilizationService.pendingSource("engineering:any_wonder").contains("功能运行")
                &&Hk3CivilizationService.pendingSource("engineering:15_wonders").contains("待批准")
                &&Hk3CivilizationService.pendingSource("engineering:hyperion").contains("待批准")
                &&Hk3CivilizationService.pendingSource("contact").isEmpty(),"工程来源未接入明确报告，常规缺项不冒充阻塞");
        research.processFactReceipt(a,"formal_communication").putString("TimeBasis","tampered");check(Hk3CivilizationService.facts(research,review,a).contains("contact"),"来源副本不可改写");
        research.recordProcessFact(b,"formal_communication",authorized);check(!Hk3CivilizationService.facts(research,review,b).contains("contact"),"不同团队的交流回执不算本队");
        UUID c=UUID.randomUUID();var old=Hk3CommunicationResearchProof.receipt(UUID.randomUUID(),c,true,2);old.putString("Authority","team_owner_or_explicit_delegate");old.putString("TimeBasis","verification_time_original_reply_time_unavailable");research.recordProcessFact(c,"formal_communication",old);
        check(!Hk3CivilizationService.facts(research,review,c).contains("contact"),"换队历史投影不伪造本队交流");
        // 合成100题有效祖先集合用于检查读侧边界，绝不写入实例或提供玩家授予命令。
        var saved=research.save(new CompoundTag());var completed=new ListTag();for(String id:Hk3ResearchExecutionContracts.all().keySet())completed.add(StringTag.valueOf(id));saved.getCompound("Accounts").getCompound(a.toString()).put("Completed",completed);
        research=Hk3ResearchData.load(saved);var observed=Hk3CivilizationService.facts(research,review,a);
        check(observed.contains("all_research"),"100题全祖先有效才能报告完成");
        check(!observed.contains("engineering:any_wonder")&&!observed.contains("engineering:15_wonders")&&!observed.contains("engineering:hyperion"),"全部研究不冒充工程验收");
        check(!observed.contains("review:1")&&!observed.contains("review:2"),"研究不授予审查通过");
        check(Hk3CivilizationRules.achieved(observed::contains)==1,"研究全满但工业/审查缺失不能跳级");
        System.out.println("Civilization: "+checks+" checks passed; live engineering providers and game acceptance remain pending");
    }
    private static void expectFailure(Runnable action){try{action.run();throw new AssertionError("损坏记录被接受");}catch(IllegalStateException expected){checks++;}}
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
