package com.sirin.hk3gtl.test.phone;

import com.sirin.hk3gtl.common.phone.Hk3PhoneCivilizationReading;
import com.sirin.hk3gtl.common.easter.*;
import net.minecraft.nbt.CompoundTag;
import java.util.*;

/** 【变更记录 #1】2026-11-05（修订207）：核对空白及非空总览快照、完整正文和审核绑定；真实玩家权限另由隔离专服验证。 */
public final class PhoneCivilizationReadTest {
    private static int checks;
    private static void check(boolean ok,String label){checks++;if(!ok)throw new AssertionError(label);}
    public static void main(String[] args){
        var empty=new CompoundTag();String body=Hk3PhoneCivilizationReading.body(empty);
        check(body.contains("已完成 0 / 0 项研究")&&body.contains("本人现有 0 / 0 条"),"空白快照可以阅读");
        check(body.contains("阅读本身不解锁配方")&&body.contains("收藏数量不是正式资格"),"阅读和正式资格分离");
        var snapshot=new CompoundTag();snapshot.putString("CivilizationTitle","测试称号");snapshot.putInt("CivilizationVerified",3);
        snapshot.putInt("ResearchDone",17);snapshot.putInt("ResearchTotal",471);snapshot.putInt("Archives",29);snapshot.putInt("ArchiveTotal",644);snapshot.putInt("Members",2);
        var original=snapshot.copy();body=Hk3PhoneCivilizationReading.body(snapshot);
        check(original.equals(snapshot),"正文生成不改快照");
        for(String text:List.of("测试称号","当前核验等级：C3","已完成 17 / 471 项研究","本人现有 29 / 644 条","成员数为 2","阅读到这里"))check(body.contains(text),"真实字段："+text);
        check(!Hk3PhoneCivilizationReading.managed("formal_civilization")&&Hk3PhoneCivilizationReading.managed(Hk3PhoneCivilizationReading.ID),"阅读身份不混同正式档案");
        var sessions=new Hk3ReadingSessions();var owner=UUID.randomUUID();var s=sessions.open(owner,Hk3PhoneCivilizationReading.ID,body,"",false,10);
        String normalized=Hk3EggReadingCursor.normalize(body);int cut=normalized.length()/2;
        check(sessions.accept(owner,s.token(),cut,normalized.substring(cut),11)==null&&!s.cursor().done(),"只读末段不算全读");
        check(sessions.accept(owner,s.token(),0,normalized.substring(0,cut),12)==null&&!s.cursor().done(),"前半段不提前完成");
        check(sessions.accept(owner,s.token(),cut,normalized.substring(cut),13)==s&&s.cursor().done(),"连续读完整份快照才完成");
        check(sessions.accept(owner,s.token(),0,normalized,14)==null,"完成重放不再返回回执");
        var rule=Hk3EggRules.all().stream().filter(r->r.id().equals("E-EG-175")).findFirst().orElseThrow();
        check(rule.matches("civilization_overview_read",Map.of("complete","true")),"原审核完整阅读绑定");
        check(!rule.matches("civilization_overview_read",Map.of("complete","false"))&&!rule.matches("phone_open",Map.of("complete","true")),"打开或未读完不能授奖");
        System.out.println("Civilization overview reading: "+checks+" checks passed");
    }
}
