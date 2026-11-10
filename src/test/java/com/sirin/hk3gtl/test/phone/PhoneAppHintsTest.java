package com.sirin.hk3gtl.test.phone;

import com.sirin.hk3gtl.common.phone.*;
import com.sirin.hk3gtl.common.easter.Hk3EggRules;
import java.util.*;

/** 【变更记录 #1】2026-11-05（修订208）：验证真实说明会话的停留时间、本人身份、去重、顺序与清理；原生入口另行验收。 */
public final class PhoneAppHintsTest {
    private static int checks;
    private static void check(boolean ok,String label){checks++;if(!ok)throw new AssertionError(label);}
    public static void main(String[] args){
        var s=new Hk3PhoneAppHintSessions();var a=UUID.randomUUID();var b=UUID.randomUUID();var token=s.open(a,100);
        check(!s.read(a,token,"notes",100),"没有开始悬停不能读完");
        check(!s.hover(b,token,"notes",100),"他人令牌无效");
        check(s.hover(a,token,"notes",100)&&!s.read(a,token,"notes",119),"不足停留时间不计入");
        check(s.read(a,token,"notes",120)&&!s.read(a,token,"notes",121),"有效停留仅计同App一次");
        check(!s.launch(a,token,"notes",122),"一项不能冒充三项");
        check(s.hover(a,token,"civilization",123)&&s.hover(a,token,"social",124)&&!s.read(a,token,"civilization",150),"移开后中断原计时");
        check(!s.hover(a,token,"E-EG-490",151)&&!s.hover(a,token,"quiet",152),"白名单和非App操作边界");
        long tick=160;for(String app:List.of("civilization","social")){s.hover(a,token,app,tick);s.read(a,token,app,tick+=20);}
        check(!s.launch(a,token,"settings",201),"只能打开已读项");
        check(s.launch(a,token,"notes",201)&&!s.opened(a,"social",202),"实际打开项必须对应");
        check(!s.opened(a,"notes",203),"错误打开后不保留候选");
        token=prepare(s,a,200);check(s.launch(a,token,"notes",260)&&s.opened(a,"notes",261),"三项连续会话加正确打开");
        check(!s.opened(a,"notes",262),"成功回执不可重放");
        token=prepare(s,a,300);var old=token;token=s.open(a,370);check(!s.launch(a,old,"notes",371),"新桌面废弃旧令牌");
        token=prepare(s,a,400);s.cancel(a,UUID.randomUUID(),460);check(s.launch(a,token,"notes",460),"伪造取消不影响本人会话");
        s.cancel(a,token,461);check(!s.opened(a,"notes",462),"真实关闭废弃会话");
        token=prepare(s,a,500);s.validate(a,560,false);check(!s.launch(a,token,"notes",561),"失电或失去桌面资格清理");
        token=prepare(s,a,600);check(!s.launch(a,token,"notes",599),"时钟回退清理");
        token=prepare(s,a,700);check(!s.launch(a,token,"notes",6701),"过期清理");
        token=prepare(s,a,800);s.launch(a,token,"notes",860);check(!s.opened(a,"notes",901),"实际打开不能无限延后");
        token=prepare(s,a,1000);s.clear(a);check(!s.launch(a,token,"notes",1060),"登出清理");
        token=prepare(s,a,1100);s.clear();check(!s.launch(a,token,"notes",1160),"停服清理");
        var rule=Hk3EggRules.all().stream().filter(r->r.id().equals("E-EG-490")).findFirst().orElseThrow();
        check(rule.matches("phone_app_hints_open",Map.of("three_read","true"))&&!rule.matches("phone_open",Map.of("three_read","true")),"审核绑定只接收正确打开事实");
        System.out.println("Phone App hints: "+checks+" checks passed");
    }
    private static UUID prepare(Hk3PhoneAppHintSessions s,UUID owner,long now){
        var token=s.open(owner,now);for(String app:List.of("notes","civilization","social")){s.hover(owner,token,app,now);s.read(owner,token,app,now+=20);}return token;
    }
}
