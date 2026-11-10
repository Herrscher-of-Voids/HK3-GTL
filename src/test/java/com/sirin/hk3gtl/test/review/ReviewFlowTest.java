package com.sirin.hk3gtl.test.review;

import com.sirin.hk3gtl.common.review.*;
import com.sirin.hk3gtl.common.dialogue.*;
import com.sirin.hk3gtl.common.dialogue.definition.Hk3ApprovedDialogues;
import com.sirin.hk3gtl.common.narrative.Hk3ApprovedProse;
import net.minecraft.nbt.*;
import java.util.*;
import java.nio.file.*;
import org.objectweb.asm.*;

/** 【变更记录 #1】2026-10-01 18:48:33（修订140）：删除无；新增336种三问题序、81条二审选择、补行/重启/退出/页面令牌与返程账本检查；修改调用生产账本及阅读屏障；用途：代码流程回归，不冒充多人、世界传送及投影实际运行。 */
/** 【变更记录 #3】2026-11-04 18:48:13（修订199）：删除：无；新增：代表收束后离线及重启不代签的回归；修改：沿用生产账本完成与离场接口；用途：防止团队结算误记个人亲历，不冒充实机传送验证。 */
public final class ReviewFlowTest {
    // 变更记录 #2 · 2026-10-01 18:54:07：新增组播/ESC交错、跨队/跨会面拒绝及页面窗口上限回归，删除无。
    private static int checks;
    private static void check(boolean ok,String why){if(!ok)throw new AssertionError(why);checks++;}
    private static CompoundTag proof(){var p=new CompoundTag();p.putString("source","isolated_test_only");return p;}
    private static Hk3ReviewLedger fresh(UUID team){var l=new Hk3ReviewLedger();check(l.qualify(team,Hk3ReviewLedger.Kind.FIRST,proof()),"夹具一审资格");return l;}
    private static Hk3ReviewLedger first(Hk3ReviewLedger l,UUID team,List<UUID> members,int[] questions){
        var m=l.beginFirst(team,members,new Random(1));check(m!=null,"正式一审开始");var id=m.id();var rep=m.representative();
        var b=new Hk3ReviewReadingBarrier();
        for(UUID p:members){check(b.confirm(p,m.participants()),"本人阅读确认");check(!b.confirm(p,m.participants()),"重复阅读不叠加");}
        check(b.ready(m.participants()),"全部在场者确认后推进");check(l.openingRead(id,rep),"开场推进");
        for(int q:questions){
            var before=l.meeting(id);int choice=Hk3ReviewDialogues.remaining(Hk3ReviewDialogues.mask(before)).indexOf(q);check(choice>=0,"菜单过滤保留合法选题");
            check(l.choose(id,rep,q),"代表选择");check(!l.choose(id,rep,q),"重复选题拒绝");
            check(l.finishFirst(id,rep)==null,"回答期间不能结算");
            b.reset();check(!b.ready(m.participants()),"每段重新确认");
            for(UUID p:members)b.confirm(p,m.participants());check(b.ready(m.participants()),"回答全员确认");check(l.answerRead(id,rep,q),"回答确认推进");
            l=Hk3ReviewLedger.load(l.save());
        }
        check(l.meeting(id).phase()==Hk3ReviewLedger.Phase.CLOSING,"三问进入收束");
        int grants=0;for(UUID p:members){var r=l.finishFirst(id,p);check(r!=null&&r.personalCompleted(),"本人收束记经历");if(r.firstTeamSettlement())grants++;check(l.finishFirst(id,p)==null,"重复完成拒绝");}
        check(grants==(m.supplement()?0:1),"团队仅发一次许可");return Hk3ReviewLedger.load(l.save());
    }
    private static void allFirst(){
        UUID team=UUID.randomUUID(),a=UUID.randomUUID(),b=UUID.randomUUID();
        for(int x=1;x<=8;x++)for(int y=1;y<=8;y++)for(int z=1;z<=8;z++)if(x!=y&&x!=z&&y!=z){
            var l=first(fresh(team),team,List.of(a,b),new int[]{x,y,z});check(l.experienced(a,Hk3ReviewLedger.Kind.FIRST)&&l.experienced(b,Hk3ReviewLedger.Kind.FIRST),"两人各自完成");
        }
        var l=fresh(team);var m=l.beginFirst(team,List.of(a,b),new Random(1));var rep=m.representative();var other=rep.equals(a)?b:a;
        check(!l.openingRead(m.id(),other),"非代表不能推进团队");l.openingRead(m.id(),rep);l.choose(m.id(),rep,7);l.answerRead(m.id(),rep,7);l.choose(m.id(),rep,3);
        l.depart(rep);check(l.meeting(m.id()).phase()==Hk3ReviewLedger.Phase.PAUSED,"代表退出暂停全场");
        l=Hk3ReviewLedger.load(l.save());l.suspendAll();m=l.restartFirst(m.id(),other,List.of(other),new Random(2));
        check(m.questions().equals(List.of(7,3)),"重开保持题序");l.openingRead(m.id(),other);
        check(l.meeting(m.id()).questions().size()==2,"重播不新增问题");check(l.answerRead(m.id(),other,7)&&l.answerRead(m.id(),other,3),"原答案按序重播");
        l.choose(m.id(),other,8);l.answerRead(m.id(),other,8);check(l.finishFirst(m.id(),other)!=null,"替补代表完成");check(!l.experienced(rep,Hk3ReviewLedger.Kind.FIRST),"退出者不代签");
        first(l,team,List.of(rep),new int[]{1,2,3});
        var barrier=new Hk3ReviewReadingBarrier();barrier.confirm(a,Set.of(a,b));check(!barrier.ready(Set.of(a,b)),"未读队员仍须确认");check(barrier.ready(Set.of(a)),"队员退出不阻塞");check(!barrier.confirm(UUID.randomUUID(),Set.of(a)),"陌生人不能确认");
    }
    private static void closingLifecycle(){
        UUID team=UUID.randomUUID(),a=UUID.randomUUID(),b=UUID.randomUUID();
        var l=fresh(team);var m=l.beginFirst(team,List.of(a,b),new Random(4));
        UUID rep=m.representative(),other=rep.equals(a)?b:a;
        l.openingRead(m.id(),rep);
        for(int q:new int[]{2,5,8}){l.choose(m.id(),rep,q);l.answerRead(m.id(),rep,q);}
        check(l.finishFirst(m.id(),rep).firstTeamSettlement(),"代表收束仅授一次团队许可");
        l.depart(rep);
        check(l.meeting(m.id()).phase()==Hk3ReviewLedger.Phase.CLOSING,"已完成代表离线不重开他人收束");
        check(!l.experienced(other,Hk3ReviewLedger.Kind.FIRST),"团队结算不替未收束者填写亲历");
        var restarted=Hk3ReviewLedger.load(l.save());restarted.suspendAll();
        check(restarted.meeting(m.id()).phase()==Hk3ReviewLedger.Phase.PAUSED,"重启时未收束会面暂停");
        check(!restarted.experienced(other,Hk3ReviewLedger.Kind.FIRST),"重启不补写个人亲历");
        check(l.finishFirst(m.id(),other)!=null&&l.meeting(m.id()).phase()==Hk3ReviewLedger.Phase.COMPLETE,"已完成代表离线后其余成员可独立收束");
    }
    private static Hk3ReviewLedger second(Hk3ReviewLedger l,UUID team,UUID player,int[] branches,boolean supplement){
        var m=l.beginSecond(team,player);check(m!=null&&m.supplement()==supplement,"二审首次/补行区分");var id=m.id();int safety=0;
        while(!l.meeting(id).checkpoint().equals("S209")){
            String at=l.meeting(id).checkpoint();check(l.finishSecond(id,player)==null,"二审中途不结算");
            var entry=Hk3ApprovedProse.get(at);int index=switch(at){case "S203"->branches[0];case "S204"->branches[1];case "S205"->branches[2];case "S206"->branches[3];default->0;};
            check(!l.advanceSecond(id,UUID.randomUUID(),at,index),"拒绝他人操作");check(!l.advanceSecond(id,player,"S209",0),"拒绝跳段");
            check(l.advanceSecond(id,player,at,index),"批准分支可推进："+at);check(!l.advanceSecond(id,player,at,index),"旧段重复包拒绝");
            if(++safety==3){l.depart(player);String checkpoint=l.meeting(id).checkpoint();l=Hk3ReviewLedger.load(l.save());check(l.resumeSecond(id,player)!=null&&l.meeting(id).checkpoint().equals(checkpoint),"断线存盘保留检查点");}
            check(safety<30,"所有分支有界可到结尾");
        }
        var r=l.finishSecond(id,player);check(r!=null&&r.firstTeamSettlement()!=supplement,"二审仅首次团队许可");check(l.finishSecond(id,player)==null,"二审结算幂等");return Hk3ReviewLedger.load(l.save());
    }
    private static void allSecond(){
        UUID team=UUID.randomUUID(),a=UUID.randomUUID(),b=UUID.randomUUID();
        var seed=first(fresh(team),team,List.of(a,b),new int[]{1,4,8});check(seed.qualify(team,Hk3ReviewLedger.Kind.SECOND,proof()),"夹具二审资格");
        for(int i=0;i<3;i++)for(int j=0;j<3;j++)for(int k=0;k<3;k++)for(int n=0;n<3;n++){
            var l=second(Hk3ReviewLedger.load(seed.save()),team,a,new int[]{i,j,k,n},false);
            second(l,team,b,new int[]{i,j,k,n},true);
        }
        var l=Hk3ReviewLedger.load(seed.save());var m=l.beginSecond(team,a);l.leaveTeam(a);
        check(l.meeting(m.id()).phase()==Hk3ReviewLedger.Phase.ABANDONED&&l.resumeSecond(m.id(),a)==null,"换队旧会面不可继续");check(l.beginSecond(UUID.randomUUID(),a)==null,"换队不继承资格");
    }
    private static void graphAndPackets()throws Exception{
        Hk3ApprovedDialogues.register();
        var lang=new com.google.gson.Gson().fromJson(Files.readString(Path.of("src/main/resources/assets/hk3gtl/lang/zh_cn.json")),com.google.gson.JsonObject.class);
        for(String id:List.of(Hk3ReviewDialogues.FIRST,Hk3ReviewDialogues.SECOND,Hk3ReviewDialogues.NOTICE)){
            var def=DialogueRegistry.getDialogue(id);check(def.endHandlerKey()==null,"通用关闭不授予审查许可");
            for(var segment:def.segments().values())for(var line:segment){check(lang.has(line.textKey()),"正文/控件键存在："+line.textKey());if(line.choices()!=null)for(var choice:line.choices()){check(lang.has(choice.labelKey()),"选项翻译存在");check(def.segments().containsKey(choice.targetSegmentId()),"图内目标存在");}}
        }
        UUID m=UUID.randomUUID(),scope=UUID.randomUUID();var frame=Hk3ReviewFrame.issue(m,scope,Hk3ReviewDialogues.FIRST,"menu.0");
        check(frame.accepts(scope,frame.dialogue(),frame.segment(),frame.nonce()),"当前令牌可用");
        check(!frame.accepts(UUID.randomUUID(),frame.dialogue(),frame.segment(),frame.nonce()),"换队令牌拒绝");
        check(!frame.accepts(scope,Hk3ReviewDialogues.SECOND,frame.segment(),frame.nonce()),"跨系统令牌拒绝");
        check(!frame.accepts(scope,frame.dialogue(),"first_review.closing",frame.nonce()),"跳段拒绝");
        check(!frame.accepts(scope,frame.dialogue(),frame.segment(),frame.nonce()^1),"错误令牌拒绝");
        var pages=new Hk3ReviewPageWindow();pages.sent(frame);var next=Hk3ReviewFrame.issue(m,scope,frame.dialogue(),"first_review.question.1");pages.sent(next);
        check(pages.mayPause(scope,frame.dialogue(),frame.segment(),frame.nonce()),"组播推进后上一页仍可暂停同一会面");
        check(!next.accepts(scope,frame.dialogue(),frame.segment(),frame.nonce()),"旧页面只能暂停不能选择");
        check(!pages.mayPause(UUID.randomUUID(),frame.dialogue(),frame.segment(),frame.nonce()),"换队旧关闭请求无效");
        for(int i=0;i<100;i++)pages.sent(Hk3ReviewFrame.issue(m,scope,frame.dialogue(),"wait"));check(pages.size()==32,"页面窗口有界");
        check(!pages.mayPause(scope,frame.dialogue(),frame.segment(),frame.nonce()),"历史过旧窗口失效");
        pages.sent(next);pages.sent(Hk3ReviewFrame.issue(UUID.randomUUID(),scope,frame.dialogue(),"first_review.open"));
        check(!pages.mayPause(scope,next.dialogue(),next.segment(),next.nonce()),"新会面拒绝旧关闭包");
        for(String file:List.of("common/review/Hk3ReviewActionPacket","client/dialogue/Hk3DialogueScreen","common/review/Hk3ReviewSessions","common/network/Hk3Network")){
            final Set<String> calls=new HashSet<>();new ClassReader(Files.readAllBytes(Path.of("build/classes/java/main/com/sirin/hk3gtl/"+file+".class"))).accept(new ClassVisitor(Opcodes.ASM9){@Override public MethodVisitor visitMethod(int a,String n,String d,String s,String[] e){return new MethodVisitor(Opcodes.ASM9){@Override public void visitMethodInsn(int o,String owner,String name,String desc,boolean itf){calls.add(owner+"."+name);}};}},ClassReader.SKIP_DEBUG|ClassReader.SKIP_FRAMES);
            String required=file.endsWith("Hk3ReviewActionPacket")?"Hk3ReviewSessions.action":file.endsWith("Hk3DialogueScreen")?"Hk3ReviewActionPacket.<init>":file.endsWith("Hk3ReviewSessions")?"Hk3ReviewQualification.refresh":"SimpleChannel.registerMessage";
            check(calls.stream().anyMatch(c->c.endsWith(required)),"真实生产入口接线："+required);
        }
    }
    private static void returns(){
        var d=new Hk3ReviewReturnData();check(d.room()==0&&d.room()==1,"场景编号互不复用");
        var n=d.save(new CompoundTag());var rows=n.getList("Returns",Tag.TAG_COMPOUND);UUID p=UUID.randomUUID(),m=UUID.randomUUID();var r=new CompoundTag();r.putUUID("Player",p);r.putUUID("Meeting",m);r.putString("Dimension","minecraft:overworld");r.putDouble("X",2);r.putDouble("Y",90);r.putDouble("Z",4);r.putFloat("Yaw",45);r.putFloat("Pitch",10);rows.add(r);
        d=Hk3ReviewReturnData.load(n);check(d.point(p).meeting().equals(m)&&d.point(p).y()==90,"返程完整保存");check(d.room()==2,"重启不重用场景编号");
        var corrupt=n.copy();corrupt.getList("Returns",Tag.TAG_COMPOUND).getCompound(0).putDouble("X",Double.NaN);boolean rejected=false;try{Hk3ReviewReturnData.load(corrupt);}catch(IllegalArgumentException e){rejected=true;}check(rejected,"坏返程坐标不当作0");
        rows.add(r.copy());rejected=false;try{Hk3ReviewReturnData.load(n);}catch(IllegalArgumentException e){rejected=true;}check(rejected,"重复返程记录拒绝");d.returned(p);check(d.point(p)==null,"返回成功清票据");
    }
    public static void main(String[] args)throws Exception{allFirst();closingLifecycle();allSecond();graphAndPackets();returns();System.out.println("Review flow: "+checks+" checks passed; production ledgers/graphs/packet wiring, no live teleport or rendering test");}
}
