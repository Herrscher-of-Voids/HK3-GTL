package com.sirin.hk3gtl.common.integration;

import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import com.sirin.hk3gtl.common.review.*;
import com.sirin.hk3gtl.common.dimension.Hk3GraduationData;

/** 原版进度与FTB研究读取相同账本；个人审查和终审只读本人回执，旧事件不能授予新进度。 */


public final class Hk3GuideAdvancements {
    private Hk3GuideAdvancements(){}
    public static void sync(ServerPlayer p,Hk3QuestCatalog.Facts f){
        var review=Hk3ReviewData.get(p.server);
        if(!f.research().isEmpty()||com.sirin.hk3gtl.common.communication.Hk3CommunicationData.get(p).state(p.getUUID()).hasObservationData())grant(p,"guide/root");
        for(var entry:Hk3QuestCatalog.all()){
            if(entry.kind().equals("research")&&Hk3QuestCatalog.satisfied(entry,f))grant(p,"guide/research/"+entry.value().toLowerCase(java.util.Locale.ROOT));
        }
        for(int level=1;level<=f.civilization();level++)grant(p,"guide/civilization/c"+level);
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
