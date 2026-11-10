package com.sirin.hk3gtl.common.phone;

import com.sirin.hk3gtl.common.narrative.Hk3CollectionRecords;
import com.sirin.hk3gtl.common.narrative.Hk3NarrativeNodes;
import java.util.function.Function;
import java.util.regex.Pattern;

/** 仅投影系统消息的当前正文，不写回账本，也不处理玩家笔记或微讯息聊天。 */
/** 【变更记录 #1】2026-10-01 22:50:14（第1次备注 · 内测5修订155）：删除玩家展示中的旧电压及开发说明；新增现行正文投影或对应回归；修改仅限呈现与检索，不改变进度、回执、触发条件或权限；用途：统一发布版玩家文案，历史备注保留。 */
/** 【变更记录 #2】2026-11-04 06:08:10（第2次备注 · 内测5修订196）：删除旧正式通知被当前正文静默替换的呈现；新增旧版历史标识与当前正式正文同源投影；修改历史正文原字保留且不参与资格；用途：保存旧叙事并明确当前迁移边界。 */
public final class Hk3PhonePresentation {
    private static final String[] GROUPS={"海渊","虚数","量子","终焉"};
    private static final String[] NAMES={"崩能压","约束压","谐振压","致密压","叠态压","相干压","纠缠压","锚定压","虚数压","耦合压","重构压","织界压","构界压","稳界压","统合压","恒续压"};
    private static final Pattern OLD=Pattern.compile("(海渊|虚数|量子|终焉)\\s*(III|IV|II|I|[ⅠⅡⅢⅣ一二三四1-4])(?!领域|种|类|次)(?:\\s*(?:级电压|电压|级))?");
    private static final Pattern ENGLISH=Pattern.compile("\\b(Abyss|Imaginary|Quantum|Finality)[ -]+(III|IV|II|I|stage|tier)\\b",Pattern.CASE_INSENSITIVE);
    private static final java.util.List<String> ENGLISH_GROUPS=java.util.List.of("abyss","imaginary","quantum","finality");
    private static final String[] KEYS={"HBV","HCV","HRV","HDV","QSV","QCV","QEV","QAV","IMV","ICV","IRV","IWV","WFV","WSV","CIV","CEV"};
    private Hk3PhonePresentation(){}
    public static String voltage(String text){
        var matcher=OLD.matcher(text);var result=new StringBuffer();
        while(matcher.find()){
            int group=java.util.List.of(GROUPS).indexOf(matcher.group(1));
            int index=switch(matcher.group(2)){case "I","Ⅰ","一","1"->0;case "II","Ⅱ","二","2"->1;case "III","Ⅲ","三","3"->2;default->3;};
            matcher.appendReplacement(result,NAMES[group*4+index]);
        }
        matcher.appendTail(result);String value=result.toString();
        for(int i=0;i<4;i++){
            String span=NAMES[i*4]+"至"+NAMES[i*4+3];
            value=value.replace(GROUPS[i]+"阶段",span+"阶段").replace(GROUPS[i]+"时代",span+"阶段")
                .replace(GROUPS[i]+"电压",span).replace(GROUPS[i]+"级",span+"级");
        }
        var english=ENGLISH.matcher(value);var translated=new StringBuffer();
        while(english.find()){
            int g=ENGLISH_GROUPS.indexOf(english.group(1).toLowerCase(java.util.Locale.ROOT));
            int n=java.util.List.of("I","II","III","IV").indexOf(english.group(2).toUpperCase(java.util.Locale.ROOT));
            english.appendReplacement(translated,n>=0?KEYS[g*4+n]:KEYS[g*4]+"–"+KEYS[g*4+3]+" "+english.group(2));
        }
        return english.appendTail(translated).toString();
    }
    public static Hk3PhoneData.Entry current(Hk3PhoneData.Entry entry,Function<String,String> tr){
        if(entry==null)return null;
        // 仅收件箱内模组生成的系统类型；未知类型原样保留，避免重写用户内容。
        if(!java.util.Set.of("narrative","chatter","research","experiment","letter","diplomacy","notice").contains(entry.kind()))return entry;
        String title=entry.title(),body=entry.body();
        String legacyEvent=entry.id().startsWith("event_E-")?entry.id().substring(6):"";
        var legacyNode=Hk3NarrativeNodes.byId(entry.target().isEmpty()&&entry.id().startsWith("narrative_")?entry.id().substring(10):entry.target());
        if(legacyNode!=null)legacyEvent=legacyNode.unlockEventId();
        var migrated=com.sirin.hk3gtl.common.narrative.Hk3LegacyArchiveMigration.all().get(legacyEvent);
        if(migrated!=null&&!body.equals(migrated.body()))
            return new Hk3PhoneData.Entry(entry.id(),"旧版历史｜"+title,body,entry.time(),entry.read(),entry.kind(),entry.target(),false);
        if(entry.id().startsWith("hint_hk3gtl.")){
            String key=entry.id().substring(5),current=tr.apply(key);
            if(!current.equals(key))body=current;
        }
        if(entry.id().startsWith("event_E-")){
            String event=entry.id().substring(6);
            var nodes=Hk3NarrativeNodes.byEventIdAll(event);
            if(!nodes.isEmpty()){var node=nodes.get(0);title=Hk3CollectionRecords.title(node,tr);body=Hk3CollectionRecords.body(node,tr);}
            else {
                String key="hk3gtl.event."+event.substring(2).replace("-","").toLowerCase(java.util.Locale.ROOT),current=tr.apply(key);
                if(!current.equals(key))body=current;
            }
        }
        if(entry.kind().equals("research")){
            var plan=com.sirin.hk3gtl.common.research.Hk3ResearchPlans.get(entry.target());
            if(plan!=null){title="研究完成｜"+tr.apply(plan.nameKey());body="已开放："+plan.result()+"\n\n"+com.sirin.hk3gtl.common.research.Hk3ResearchStory.get(entry.target());}
        }
        if(entry.kind().equals("experiment"))body=title.startsWith("对照基线")?
            "普通演算基线已保存。继续完成辅助运行，取得完整实验凭据。":
            "实验成果已记入团队档案。请带上实验凭据与所需材料，继续完成对应课题。";
        if(entry.kind().equals("narrative")||entry.kind().equals("chatter")){
            String target=entry.target();
            if(target.isEmpty()&&entry.id().startsWith("narrative_"))target=entry.id().substring(10);
            var node=Hk3NarrativeNodes.byId(target);
            if(node!=null){title=Hk3CollectionRecords.title(node,tr);body=Hk3CollectionRecords.body(node,tr);}
            else {
                title=title.replaceFirst("^档案解锁[｜|：: ]*","");
                body=body.replace("额外收藏 · 不阻断终审\n","")
                    .replace("额外收藏：不会替代研究、工程与正式会面。","")
                    .replace("额外收藏不阻断终审","");
            }
        }
        return new Hk3PhoneData.Entry(entry.id(),voltage(title),voltage(body).strip(),entry.time(),entry.read(),entry.kind(),entry.target(),entry.pending());
    }
}
