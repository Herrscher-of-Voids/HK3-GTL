package com.sirin.hk3gtl.common.communication;

import java.util.*;

/** 【变更记录 #1】2026-10-01 00:55:45（修订124）：删除无；新增正式通信六组目录只读核验；修改手机与卷轴使用同一缺项结果；用途：互斥路线择一、本人回执有效，通信目录完成不等于全卷轴或终审资格。 */
public final class Hk3CommunicationCompletion {
    public record Status(int completed,List<String> missing) {
        public Status { missing=List.copyOf(missing); }
        public boolean complete(){return completed==6&&missing.isEmpty();}
    }
    private Hk3CommunicationCompletion() {}
    public static Status status(Hk3TeamContactData contacts,Hk3PersonalCommunicationData personal,UUID actor){
        var missing=new ArrayList<String>();
        if(!contacts.experienced(actor))missing.add("奥托首信、答复与观察资料附件");
        for(var t:Hk3DiplomacyData.TOPICS)if(!personal.experienced(actor,t.id()))missing.add(t.name()+"正式交流");
        return new Status(6-missing.size(),missing);
    }
}
