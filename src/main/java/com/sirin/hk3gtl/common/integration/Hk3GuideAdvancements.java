package com.sirin.hk3gtl.common.integration;

import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import com.sirin.hk3gtl.common.review.*;
import com.sirin.hk3gtl.common.dimension.Hk3GraduationData;

/** 原版进度与FTB研究读取相同账本；个人审查和终审只读本人回执，旧事件不能授予新进度。 */
/** 【变更记录 #1】2026-10-01 14:10:35（修订129）：删除：无；新增/修改：新原版进度共用真实研究来源，个人审查和终审不读取团队代办或旧世界标记；用途：任务和进度只投影真实账本，不授研究、物品或审查资格。 */
public final class Hk3GuideAdvancements {
    private Hk3GuideAdvancements(){}
    public static void sync(ServerPlayer p,Hk3QuestCatalog.Facts f){
        var review=Hk3ReviewData.get(p.server);
        if(!f.research().isEmpty()||com.sirin.hk3gtl.common.communication.Hk3CommunicationData.get(p).state(p.getUUID()).hasObservationData())grant(p,"guide/root");
        for(String id:f.research())grant(p,"guide/research/"+id.toLowerCase(java.util.Locale.ROOT));
        for(int i=1;i<=f.civilization();i++)grant(p,"guide/civilization/c"+i);
        if(review.experienced(p.getUUID(),Hk3ReviewLedger.Kind.FIRST))grant(p,"guide/first_review");
        if(review.experienced(p.getUUID(),Hk3ReviewLedger.Kind.SECOND))grant(p,"guide/second_review");
        if(Hk3GraduationData.get(p.server.overworld()).isGraduated(p.getUUID()))grant(p,"guide/finale");
    }
    private static void grant(ServerPlayer p,String path){
        var advancement=p.server.getAdvancements().getAdvancement(new ResourceLocation("hk3gtl",path));if(advancement==null)return;
        var progress=p.getAdvancements().getOrStartProgress(advancement);if(progress.isDone())return;
        for(String criterion:java.util.List.copyOf(com.google.common.collect.Lists.newArrayList(progress.getRemainingCriteria())))p.getAdvancements().award(advancement,criterion);
    }
}
