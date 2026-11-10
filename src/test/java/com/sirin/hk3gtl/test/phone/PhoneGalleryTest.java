package com.sirin.hk3gtl.test.phone;

import com.sirin.hk3gtl.common.phone.Hk3PhoneGallerySessions;
import com.sirin.hk3gtl.common.easter.Hk3EggRules;
import java.util.*;

/** 【变更记录 #1】2026-11-05（修订209）：核对30秒边界、本人令牌、连续可见、手动关闭和生命周期；原生测试另外真实等待。 */
public final class PhoneGalleryTest {
    private static int checks;
    private static void check(boolean ok,String label){checks++;if(!ok)throw new AssertionError(label);}
    private static UUID start(Hk3PhoneGallerySessions s,UUID owner,long now){var t=s.open(owner,now);s.pulse(owner,t,now);return t;}
    private static void pulses(Hk3PhoneGallerySessions s,UUID owner,UUID token,long start,long end){for(long n=start;n<=end;n+=1000)s.pulse(owner,token,n);}
    public static void main(String[] args){
        var s=new Hk3PhoneGallerySessions();var a=UUID.randomUUID();var b=UUID.randomUUID();var t=s.open(a,0);
        check(!s.close(a,t,0),"未显示相册不能完成");
        t=start(s,a,0);check(!s.pulse(b,t,1000)&&!s.close(b,t,30000),"拒绝他人令牌");
        pulses(s,a,t,1000,29000);check(!s.close(a,t,29999),"不足30秒不完成");
        t=start(s,a,0);pulses(s,a,t,1000,30000);check(s.close(a,t,30000),"满30秒亲自关闭");check(!s.close(a,t,30001),"成功回执不能重放");
        t=start(s,a,0);pulses(s,a,t,1000,30000);s.cancel(a,t);check(!s.close(a,t,30000),"被动移除不冒充手动关闭");
        t=start(s,a,0);s.pulse(a,t,5001);pulses(s,a,t,6000,40000);check(!s.close(a,t,40000),"可见回执中断不拼接计时");
        t=s.open(a,0);check(s.pulse(a,t,4000),"首次可见时才开始计时");pulses(s,a,t,5000,30000);check(!s.close(a,t,30000),"服务器发送到客户端显示的等待不计阅读");
        t=start(s,a,0);s.open(a,1000);check(!s.close(a,t,30000),"重开废弃旧会话");
        t=start(s,a,0);s.cancel(a,UUID.randomUUID());check(s.pulse(a,t,1000),"伪造取消不能删真实会话");
        s.validate(a,1001,false);check(!s.pulse(a,t,1002),"导航或失电清理");
        t=start(s,a,1000);check(!s.pulse(a,t,999)&&!s.contains(a),"单调时钟回退失效");
        t=start(s,a,0);s.validate(a,5001,true);check(!s.contains(a),"超时释放");
        t=start(s,a,0);s.clear(a);check(!s.pulse(a,t,1),"登出清理本人");
        t=start(s,a,0);s.clear();check(!s.pulse(a,t,1),"停服释放全部");
        var rule=Hk3EggRules.all().stream().filter(r->r.id().equals("E-EG-310")).findFirst().orElseThrow();
        check(rule.matches("phone_gallery_closed",Map.of("thirty_seconds","true"))&&!rule.matches("phone_open",Map.of("thirty_seconds","true")),"只接收相册关闭事实");
        System.out.println("Phone gallery: "+checks+" checks passed");
    }
}
