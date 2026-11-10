package com.sirin.hk3gtl.common.phone;
import java.util.ArrayList;
import java.util.List;
/**
 * 【变更记录 #1】2026-09-30 18:18:05（内测5修订112）
 * 删除：无；新增：只生成消息数据的三组验收夹具。
 * 修改：不调用研究/事件完成入口；用途：验证队列、分页、防重与长文，避免改剧情。
 */
public final class Hk3PhoneTestMessages {
    private Hk3PhoneTestMessages(){}
    public record Message(String id,String title,String body,String kind){}
    public static List<Message> batch(String name){
        int count=switch(name){case "research_pair"->2;case "burst"->100;case "history_more"->40;default->0;};
        var result=new ArrayList<Message>();
        for(int i=0;i<count;i++){
            String kind=name.equals("research_pair")?"research":"notice";
            String body="这是一条界面验收消息，不代表真实研究完成，也不会解锁机器或剧情。";
            if(name.equals("history_more"))body+=("\n\n长文分页校验：每页有固定的正文区域。请使用上一页和下一页，末页应显示结束标记。").repeat(35)+"\n\n【全文结束】";
            result.add(new Message("ui_test_112_"+name+"_"+i,"[界面测试] "+(kind.equals("research")?"研究成果":"通知")+" "+(i+1),body,kind));
        }
        return List.copyOf(result);
    }
}
