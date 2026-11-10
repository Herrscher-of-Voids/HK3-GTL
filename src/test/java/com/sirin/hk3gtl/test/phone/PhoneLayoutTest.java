package com.sirin.hk3gtl.test.phone;

import com.sirin.hk3gtl.common.phone.*;
import java.util.HashSet;
import java.util.UUID;

/**
 * 【变更记录 #1】2026-09-30 18:18:05（内测5修订112）
 * 删除：无；新增：整页无遗漏、屏幕边界与拖动坐标回算、纯消息夹具回归。
 * 修改：验证实际生产计算；用途：防止末页重叠漏字、分辨率变化越界、测试污染玩法。
 */
public final class PhoneLayoutTest {
    private static int checks;
    private static void check(boolean ok,String message){if(!ok)throw new AssertionError(message);checks++;}
    public static void main(String[] args){
        for(int lines=0;lines<=500;lines++){
            int count=Hk3PhoneLayout.pages(lines,16),seen=0;
            check(count>=1,"空文档也有一页");
            check(Hk3PhoneLayout.page(-1,lines,16)==0,"首页不能向前");
            check(Hk3PhoneLayout.page(Integer.MAX_VALUE,lines,16)==count-1,"末页截断");
            for(int p=0;p<count;p++)for(int i=p*16;i<Math.min(lines,(p+1)*16);i++){check(i==seen,"翻页不重复不遗漏");seen++;}
            check(seen==lines,"所有正文都能到达");
        }
        check(Hk3PhoneLayout.pages(Integer.MAX_VALUE,16)==134217728,"计数不溢出");
        for(int sw:new int[]{240,320,600,854,1920})
        for(int sh:new int[]{120,240,480,1080})
        for(double scale:new double[]{.6,1,1.5})
        for(double px:new double[]{0,.25,.75,1})
        for(double py:new double[]{0,.25,.75,1}){
            int count=sw<600||sh<240?1:2;
            var p=Hk3PhoneLayout.toast(sw,sh,count,scale,px,py,true,12,24);
            check(p.x()>=0&&p.y()>=0&&p.x()+p.width()<=sw&&p.y()+p.stackHeight()<=sh,"预览与实绘在视野内");
            if(sw>p.width())check(Math.abs((double)p.x()/(sw-p.width())-px)<=1.0/(sw-p.width()),"拖动横向比例回算");
            if(sh>p.stackHeight())check(Math.abs((double)p.y()/(sh-p.stackHeight())-py)<=1.0/(sh-p.stackHeight()),"拖动纵向比例回算");
        }
        var old=Hk3PhoneLayout.toast(800,480,2,1,-1,-1,true,12,24);
        check(old.x()==570&&old.y()==24,"旧位置兼容");
        check(Hk3PhoneLayout.unit(Double.NaN)==0&&Hk3PhoneLayout.unit(-2)==0&&Hk3PhoneLayout.unit(3)==1,"越界坐标约束");
        var ids=new HashSet<String>();var user=UUID.randomUUID();var data=new Hk3PhoneData();
        for(String name:new String[]{"research_pair","burst","history_more"}){
            var batch=Hk3PhoneTestMessages.batch(name);
            check(batch.size()==(name.equals("research_pair")?2:name.equals("burst")?100:40),"批次数量");
            for(var m:batch){
                check(ids.add(m.id()),"批次互不覆盖");
                check(data.add(user,m.id(),m.title(),m.body(),1,m.kind(),"",false),"符合真实账本限制");
                if(name.equals("history_more"))check(m.body().endsWith("【全文结束】")&&m.body().contains("\n"),"长文含换页材料与末尾标记");
            }
            for(var m:Hk3PhoneTestMessages.batch(name))check(!data.add(user,m.id(),m.title(),m.body(),2),"重复测试不重复入账");
        }
        check(data.count(user)==142&&!data.installed(user),"测试夹具不授予手机资格");
        check(Hk3PhoneTestMessages.batch("unknown").isEmpty(),"未知测试批次拒绝");
        System.out.println("Phone layout: "+checks+" checks passed; live UI acceptance pending");
    }
}
