package com.sirin.hk3gtl.common.communication;

import java.util.*;

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
