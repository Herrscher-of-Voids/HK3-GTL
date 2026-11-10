package com.sirin.hk3gtl.test.dialogue;

/** 【变更记录 #2】2026-09-29 19:50:20（内测5修订99）：删除：92条贸易正文的活动计数要求，改为验证无贸易分类；新增：无；修改：按负责人决定撤下五方贸易；用途：保留其他系统独立运行。 */
import com.google.gson.*;
import com.sirin.hk3gtl.common.dialogue.*;
import com.sirin.hk3gtl.common.dialogue.definition.*;
import com.sirin.hk3gtl.common.narrative.Hk3ApprovedProse;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.*;

/**
 * 已审核正文回归：完整覆盖、语言键、终审分支可达性与只读边界。
 * 【变更记录 #1】2026-09-29 17:51:46（内测5修订93）
 * 删除：无。新增：审核来源与运行定义一致性检查。修改：无。用途：不启动游戏验证接线。
 */
public final class ApprovedProseTest {
    public static void main(String[] args) throws Exception {
        check(Hk3ApprovedProse.all().size()==644,"正文总数");
        check(Hk3ApprovedProse.system("npc").size()==480,"访客480条");
        check(Hk3ApprovedProse.system("trade").isEmpty(),"贸易正文已从运行目录移除");
        for (String locale:List.of("zh_cn","en_us")) {
            try (var stream=ApprovedProseTest.class.getResourceAsStream("/assets/hk3gtl/lang/"+locale+".json")) {
                check(stream!=null,"语言资源缺失");
                JsonObject lang=JsonParser.parseReader(new InputStreamReader(stream,StandardCharsets.UTF_8)).getAsJsonObject();
                for(var e:Hk3ApprovedProse.all()) {
                    check(lang.has(e.key()+".title") && lang.has(e.key()+".speaker"),e.id());
                    for(int i=0;i<e.lineCount();i++)check(lang.has(e.key()+".line."+i),e.id()+"正文缺行");
                }
                check(lang.get("hk3gtl.approved.update.U29.line.1").getAsString().contains("758974004")
                        || lang.toString().contains("758974004"),"反馈群号");
                check(lang.toString().contains("3929461640"),"作者QQ");
            }
        }
        Hk3ApprovedDialogues.register();
        SirinDialogueDefinitions.register();
        Hk3IfArchiveDialogue.register();
        for(String id:List.of(Hk3ApprovedDialogues.LIBRARY,Hk3ApprovedDialogues.REVIEW_PREVIEW,
                Hk3ApprovedDialogues.FINALE_PREVIEW,Hk3IfArchiveDialogue.ID)) {
            var d=DialogueRegistry.getDialogue(id);
            check(d!=null && d.endHandlerKey()==null,"只读入口不能结算："+id);
            checkGraph(d);
        }
        var finale=DialogueRegistry.getDialogue(SirinDialogueDefinitions.DIALOGUE_ID);
        check(finale.startSegmentId().equals("F01") && !finale.segments().containsKey("intro"),"正式终审不能继续读取旧开场");
        checkGraph(finale);
        Set<String> visited=new HashSet<>();
        visit(finale,"F01",visited);
        check(visited.containsAll(List.of("FU01","FP01","F09")),"通过、暂缓与现实生活收束均可达");
        check(!visited.contains("FP03") && !visited.contains("FU02"),"正常选项不能触发攻击坏结局");
        for(int i=1;i<=26;i++) {
            String id=String.format(Locale.ROOT,"IF-%02d",i);
            check(visited.contains(id),"终审IF不可达："+id);
            check(finale.segments().get(id).size()==10,"IF必须为十条独立播放行："+id);
            check(Hk3ApprovedDialogues.ifIndex(id)==i-1,"IF账本索引一致");
        }
        check(Hk3ApprovedDialogues.ifIndex("IF_MENU_1")==-1,"翻页不得扣名额");
        check(Hk3ApprovedDialogues.ifIndex("IF-00")==-1 && Hk3ApprovedDialogues.ifIndex("IF-27")==-1,"无效IF拒绝");
        System.out.println("已审核正文检查通过：644条、480访客对白、26条IF逐句、全分支与只读边界");
    }
    private static void checkGraph(DialogueDefinition d) {
        check(d.segments().containsKey(d.startSegmentId()),"入口段落不存在");
        for(var lines:d.segments().values())for(var line:lines) {
            check(DialogueRegistry.getSpeaker(line.speakerId())!=null || line.speakerId().equals("system") || line.speakerId().equals("sirin"),"发言者缺失");
            if(line.choices()!=null)for(var c:line.choices())check(d.segments().containsKey(c.targetSegmentId()),"目标缺失："+c.targetSegmentId());
        }
    }
    private static void visit(DialogueDefinition d,String id,Set<String> seen) {
        if(!seen.add(id))return;
        for(var line:d.segments().get(id))if(line.choices()!=null)for(var c:line.choices())visit(d,c.targetSegmentId(),seen);
    }
    private static void check(boolean value,String message) { if(!value)throw new AssertionError(message); }
}
