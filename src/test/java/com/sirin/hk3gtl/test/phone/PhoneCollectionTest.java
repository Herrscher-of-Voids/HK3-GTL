package com.sirin.hk3gtl.test.phone;

import com.sirin.hk3gtl.common.phone.*;
import com.sirin.hk3gtl.common.easter.*;
import com.sirin.hk3gtl.common.narrative.*;
import net.minecraft.nbt.CompoundTag;
import java.util.*;

/** 【变更记录 #1】2026-11-05 01:51:41（第1次备注 · 内测5修订204）：删除无；新增本人收藏隔离、精确七段版本与服务端阅读动作的回归；修改无；用途：核验生产筛选和令牌规则，不替代客户端界面与真实网络验收。 */
public final class PhoneCollectionTest {
    private static int checks;
    private static void check(boolean value,String why){checks++;if(!value)throw new AssertionError(why);}
    public static void main(String[] args){
        var owner=new CompoundTag();var stranger=new CompoundTag();
        check(!Hk3PhoneCollectionService.discovered(owner),"未发现不能打开第五百页说明");
        Hk3NarrativeLog.unlock(owner,"E-EG-001");
        check(Hk3PhoneCollectionService.discovered(owner)&&!Hk3PhoneCollectionService.discovered(stranger),"发现资格只来自本人本批彩蛋");
        check(Hk3PhoneCollectionService.searchOwned(owner,"404",s->s).isEmpty(),"未拥有404不能搜索出全目录条目");
        Hk3NarrativeLog.unlock(owner,"E-EG-404");
        var found=Hk3PhoneCollectionService.searchOwned(owner,"404",s->s);
        check(found.size()==1&&found.get(0).id().equals("E-EG-404"),"只匹配本人已拥有ID");
        check(Hk3PhoneCollectionService.searchOwned(stranger,"404",s->s).isEmpty(),"他人收藏不泄露");
        check(Hk3PhoneCollectionService.matches("404","其他","正文404")&&Hk3PhoneCollectionService.matches("abc","ABC",""),"标题正文搜索及大小写");
        String seven="一\n\n二\n三\n四\n五\n六\n七";
        var data=new Hk3PhoneNotes();UUID actor=UUID.randomUUID();
        check(data.saveNote(actor,"",0,"2747",seven,1),"保存原文");var opened=data.list(actor).get(0);
        check(Hk3PhoneCollectionService.sevenParagraphs(opened)&&Hk3PhoneCollectionService.notePages(seven).size()==7,"空白行不冒充段落");
        check(Hk3PhoneCollectionService.sameNote(opened,data.find(actor,opened.id())),"保存版本匹配");
        for(String body:List.of("一\n二\n三\n四\n五\n六",seven+"\n八"))
            check(!Hk3PhoneCollectionService.sevenParagraphs(new Hk3PhoneNotes.Note("id","2747",body,1,1)),"精确七段拒绝六段和八段");
        check(!Hk3PhoneCollectionService.sevenParagraphs(new Hk3PhoneNotes.Note("id"," 2747",seven,1,1)),"标题必须精确");
        check(data.saveNote(actor,opened.id(),1,"2747",seven,2)&&!Hk3PhoneCollectionService.sameNote(opened,data.find(actor,opened.id())),"即使同正文重新保存也使旧版本失效");
        check(!Hk3PhoneCollectionService.sameNote(opened,null),"删除版本不能完成阅读");
        var sessions=new Hk3ReadingSessions();var s=sessions.open(actor,"collection_explanation_500","首段末段","action",false,0);
        check(sessions.accept(UUID.randomUUID(),s.token(),0,"首段末段",1)==null,"跨玩家令牌拒绝");
        check(sessions.accept(actor,UUID.randomUUID(),0,"首段末段",1)==null,"伪造令牌拒绝");
        check(!sessions.consumeAction(actor,"action",1),"未读不能主动收藏或翻段");
        check(sessions.accept(actor,s.token(),2,"末段",1)==null,"跳末段拒绝");
        check(sessions.accept(actor,s.token(),0,"首段",2)==null&&!sessions.consumeAction(actor,"action",2),"半读不授动作");
        check(sessions.accept(actor,s.token(),2,"末段",3)!=null,"连续全文完成");
        check(sessions.accept(actor,s.token(),0,"首段末段",4)==null,"重放回执不重复完成");
        check(!sessions.consumeAction(actor,"wrong",4)&&sessions.consumeAction(actor,"action",4)&&!sessions.consumeAction(actor,"action",4),"动作身份及单次消费");
        s=sessions.open(actor,"note_read_id","完整","next",false,0);sessions.accept(actor,s.token(),0,"完整",1);
        check(!sessions.consumeAction(actor,"next",36000),"到期不能翻段或收藏");
        s=sessions.open(actor,"note_read_id","完整","next",false,0);sessions.clear(actor);
        check(sessions.accept(actor,s.token(),0,"完整",1)==null,"关闭失效");
        for(String id:List.of("E-EG-324","E-EG-385","E-EG-500")){
            var rule=Hk3EggRules.all().stream().filter(r->r.id().equals(id)).findFirst().orElseThrow();
            var facts=new HashMap<String,String>();for(var c:rule.checks())facts.put(c.field(),c.value());
            check(rule.matches(rule.event(),facts),"规则满足"+id);
            for(var c:rule.checks()){var missing=new HashMap<>(facts);missing.remove(c.field());check(!rule.matches(rule.event(),missing),"缺事实拒绝"+id);}
        }
        System.out.println("Phone collection: "+checks+" checks passed");
    }
}
