package com.sirin.hk3gtl.common.narrative;

import com.google.gson.JsonParser;
import com.sirin.hk3gtl.common.communication.Hk3TeamContactData;
import com.sirin.hk3gtl.common.communication.Hk3DiplomacyData;
import com.sirin.hk3gtl.common.communication.Hk3PersonalCommunicationData;
import com.sirin.hk3gtl.common.finale.Hk3FinaleRequirements.Fact;
import com.sirin.hk3gtl.common.research.Hk3ResearchPlans;
import com.sirin.hk3gtl.common.research.Hk3ResearchExecutionContracts;
import com.sirin.hk3gtl.common.review.Hk3ReviewLedger;
import net.minecraft.nbt.CompoundTag;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.function.Predicate;

/**
 * 【变更记录 #1】2026-11-04 05:57:01（第1次备注 · 内测5修订196）
 * 删除：无；新增：64旧正式事件逐项处置目录及本人首信的严格同义适配。
 * 修改：候选来源仅供审核，生产只接受OT001已批准首信映射，其余逐项等待。
 * 用途：正式档案保留原要求与具体缺口；查询只读原账本，不改旧收藏、正文或许可。
 */
/**
 * 【变更记录 #2】2026-11-04 06:12:15（第2次备注 · 内测5修订196）
 * 删除：63事件未采用候选的等待分支；新增：负责人授权的64逐项新正文与准确研究/通信/审查来源。
 * 修改：研究型读取本人新版全文回执，交流审查型投影精确本人经历；未接执行器仍显示等待。
 * 用途：规则和正文指纹绑定，不让旧收藏、泛研究或错误来源授资格；不推断实体设施与上游可玩性。
 */
public final class Hk3LegacyArchiveMigration {
    public enum SourceKind { RESEARCH, COMMUNICATION, REVIEW }
    public record Rule(String eventId, String previousTrigger, SourceKind kind, String source,
                       String title, String body, String fingerprint) {}
    private static final Map<String, Rule> ALL = load();
    private Hk3LegacyArchiveMigration() {}
    public static Map<String, Rule> all() { return ALL; }

    /** 核验完整目录、准确来源类型与正文；历史和候选字段绝不用于授权。 */
    private static Map<String, Rule> load() {
        try (var stream = Hk3LegacyArchiveMigration.class.getResourceAsStream(
                "/data/hk3gtl/narrative/legacy_archive_migration.json")) {
            if (stream == null) throw new IllegalStateException("旧正式事件迁移目录缺失");
            var root = JsonParser.parseReader(new InputStreamReader(stream, StandardCharsets.UTF_8)).getAsJsonObject();
            if (root.get("schema").getAsInt() != 2) throw new IllegalArgumentException("迁移目录版本不符");
            var result = new TreeMap<String, Rule>();
            for (var element : root.getAsJsonArray("events")) {
                var item = element.getAsJsonObject();
                var active = item.getAsJsonObject("approved_rule");
                String id=item.get("event_id").getAsString(), source=active.get("source").getAsString();
                var kind=SourceKind.valueOf(active.get("kind").getAsString());
                var parts=new ArrayList<String>();
                for(var part:item.getAsJsonArray("approved_body")) {
                    if(!part.isJsonPrimitive()||!part.getAsJsonPrimitive().isString())throw new IllegalArgumentException("正文段落不是字符串："+id);
                    String line=part.getAsString();if(line.isBlank())throw new IllegalArgumentException("正文空段："+id);parts.add(line);
                }
                String title=item.get("approved_title").getAsString(),body=String.join("\n\n",parts);
                var rule = new Rule(id,item.get("old_trigger").getAsString(),kind,source,title,body,
                    digest(id+"\n"+kind+"\n"+source+"\n"+title+"\n"+body));
                boolean validSource=switch(kind) {
                    case RESEARCH -> Hk3ResearchPlans.get(source)!=null&&Hk3ResearchExecutionContracts.get(source)!=null;
                    case COMMUNICATION -> source.equals("first_contact")||Hk3DiplomacyData.topic(source)!=null;
                    case REVIEW -> Arrays.stream(Hk3ReviewLedger.Kind.values()).anyMatch(k->k.name().equals(source));
                };
                if (rule.previousTrigger().isBlank() || title.isBlank() || title.length()>128 || parts.size()<2
                        || body.length()>12000 || !validSource || result.putIfAbsent(rule.eventId(), rule) != null)
                    throw new IllegalArgumentException("未经批准或重复的迁移来源：" + rule.eventId());
            }
            var expected = new TreeSet<String>();
            for (var node : Hk3NarrativeNodes.all())
                if (Hk3CollectionCatalog.kind(node.id()) == Hk3CollectionCatalog.Kind.FORMAL
                        && !node.unlockEventId().equals("E-HQ-005")) expected.add(node.unlockEventId());
            if (result.size() != 64 || !result.keySet().equals(expected))
                throw new IllegalArgumentException("64旧正式事件迁移目录遗漏或越界");
            return Collections.unmodifiableMap(result);
        } catch (Exception exception) {
            throw new IllegalStateException("旧正式事件迁移目录无效", exception);
        }
    }

    private static String digest(String text) {
        try{return HexFormat.of().formatHex(java.security.MessageDigest.getInstance("SHA-256").digest(text.getBytes(StandardCharsets.UTF_8)));}
        catch(java.security.NoSuchAlgorithmException impossible){throw new IllegalStateException(impossible);}
    }
    /** 仅准确来源算前置成立；研究合同存在不等于课题完成，个人答复和会面均读取本人账本。 */
    public static Fact prerequisite(Rule rule, Predicate<String> research, Hk3TeamContactData contacts,
            Hk3PersonalCommunicationData personal,Hk3ReviewLedger reviews,UUID actor) {
        if(rule==null||!rule.equals(ALL.get(rule.eventId())))return Fact.waiting("该事件没有获准的正式迁移来源");
        Objects.requireNonNull(actor);
        boolean complete=switch(rule.kind()) {
            case RESEARCH -> research.test(rule.source());
            case COMMUNICATION -> rule.source().equals("first_contact")?contacts.experienced(actor):personal.experienced(actor,rule.source());
            case REVIEW -> reviews.experienced(actor,Hk3ReviewLedger.Kind.valueOf(rule.source()));
        };
        if(!complete) {
            if(rule.kind()==SourceKind.RESEARCH&&!Hk3ResearchExecutionContracts.get(rule.source()).existing())
                return Fact.waiting("课题 "+rule.source()+" 的执行来源尚未全部接入；已有真实完成记录才可阅读本条");
            return Fact.missing(switch(rule.kind()) {
                case RESEARCH -> "本队尚未完成准确课题："+rule.source();
                case COMMUNICATION -> "本人尚未完成该组正式交流："+rule.source();
                case REVIEW -> "本人尚未完成"+(rule.source().equals("FIRST")?"一审":"二审")+"真实会面";
            });
        }
        var proof = new CompoundTag();
        proof.putInt("MigrationVersion", 2); proof.putString("Event", rule.eventId());
        proof.putString("Source", rule.source());proof.putString("Kind",rule.kind().name());
        proof.putString("RuleHash",rule.fingerprint());proof.putUUID("Actor", actor);
        return Fact.complete(proof);
    }

    /** 已完成的研究型本人阅读历史跨队保留；没有该历史时必须先满足当前队课题再本人全文补读。 */
    public static Fact evaluate(String eventId,Predicate<String> research,Hk3TeamContactData contacts,
            Hk3PersonalCommunicationData personal,Hk3ReviewLedger reviews,Hk3LegacyArchiveData readings,UUID actor) {
        var rule=ALL.get(eventId);
        if(rule!=null&&rule.kind()==SourceKind.RESEARCH&&readings.experienced(actor,rule))return Fact.complete(readings.receipt(actor,rule));
        var source=prerequisite(rule,research,contacts,personal,reviews,actor);
        if(rule==null||source.state()!=com.sirin.hk3gtl.common.finale.Hk3FinaleRequirements.State.COMPLETE)return source;
        return rule.kind()==SourceKind.RESEARCH?Fact.missing("本队课题已完成；手机通知 → "+rule.title()+" → 本人逐页读完全文"):source;
    }
}
