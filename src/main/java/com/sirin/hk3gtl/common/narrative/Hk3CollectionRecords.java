package com.sirin.hk3gtl.common.narrative;

import com.sirin.hk3gtl.common.phone.Hk3PhoneData;
import net.minecraft.nbt.CompoundTag;
import java.util.*;
import java.util.function.Function;

/** 【变更记录 #1】2026-10-01 01:54:14（修订127）：删除无；新增收藏记录、正文组装与持久投递共用服务；修改无；用途：手机、卷轴、通知同源，按本人状态判定且阅读不解锁、不发奖；无玩家实体依赖便于真实存档回归。 */
/** 【变更记录 #2】2026-10-01 22:50:14（第2次备注 · 内测5修订155）：删除玩家展示中的旧电压及开发说明；新增现行正文投影或对应回归；修改仅限呈现与检索，不改变进度、回执、触发条件或权限；用途：统一发布版玩家文案，历史备注保留。 */
/** 【变更记录 #3】2026-11-04 06:08:10（第3次备注 · 内测5修订196）：删除64正式收藏的旧正文投影；新增现行迁移标题与全文共享入口；修改只影响当前呈现，已投递历史原文不覆盖；用途：让手机与卷轴引用同一获准正文，不授予资格。 */
public final class Hk3CollectionRecords {
    public record Receipt(boolean unlocked,boolean delivered,String title,String body,String kind){}
    private Hk3CollectionRecords(){}
    public static List<Hk3NarrativeNode> unlocked(CompoundTag state,String filter){
        if(!Hk3CollectionCatalog.validFilter(filter))return List.of();
        return Hk3NarrativeNodes.all().stream().filter(n->Hk3NarrativeLog.isUnlocked(state,n.id()))
            .filter(n->Hk3CollectionCatalog.matches(n.id(),filter)).sorted(Comparator.comparing(Hk3NarrativeNode::id)).toList();
    }
    public static long total(String filter){return Hk3NarrativeNodes.all().stream().filter(n->Hk3CollectionCatalog.matches(n.id(),filter)).count();}
    public static String title(Hk3NarrativeNode node,Function<String,String> tr){
        var rule=Hk3LegacyArchiveMigration.all().get(node.unlockEventId());
        return rule==null?tr.apply(node.titleKey()):rule.title();
    }
    public static String body(Hk3NarrativeNode node,Function<String,String> tr){
        var rule=Hk3LegacyArchiveMigration.all().get(node.unlockEventId());
        if(rule!=null)return rule.body();
        StringBuilder b=new StringBuilder();
        if(node.hasAuthor())b.append(tr.apply(node.authorKey())).append("\n\n");
        for(String key:node.bodyKeys())b.append(tr.apply(key)).append("\n\n");
        return b.toString().stripTrailing();
    }
    /** 已解锁记录允许静默补回缺失收件箱；未解锁只由真实事件调用本方法。 */
    public static Receipt record(CompoundTag state,Hk3PhoneData inbox,UUID actor,Hk3NarrativeNode node,long time,Function<String,String> tr){
        if(node==null||Hk3NarrativeNodes.byId(node.id())!=node)throw new IllegalArgumentException("未知收藏条目");
        String title=title(node,tr);
        String text=body(node,tr),kind=Hk3CollectionCatalog.optional(node.id())?"chatter":"narrative";
        // 先确保存档消息有效，再写解锁；相同收件人/条目ID由信箱去重。
        boolean delivered=inbox.add(actor,"narrative_"+node.id(),title,text,time,kind,node.id(),false);
        boolean unlocked=Hk3NarrativeLog.unlock(state,node.id());
        return new Receipt(unlocked,delivered,title,text,kind);
    }
}
