package com.sirin.hk3gtl.common.communication;

import com.sirin.hk3gtl.common.phone.Hk3PhoneData;
import java.util.*;
import java.util.function.Consumer;

public final class Hk3CommunicationDelivery {
    public record Notice(UUID recipient,String id,String title,String body,String kind,boolean pending) {}
    private Hk3CommunicationDelivery() {}
    private static void deliver(Hk3PhoneData inbox,UUID recipient,String id,String title,String body,String kind,
                                String target,boolean pending,long time,Consumer<Notice> newlyDelivered){
        if(inbox.add(recipient,id,title,body,time,kind,target,pending))newlyDelivered.accept(new Notice(recipient,id,title,body,kind,pending));
        inbox.pending(recipient,id,pending);
    }
    public static void first(Hk3TeamContactData contacts,Hk3PhoneData inbox,UUID team,Collection<UUID> members,
                             long time,Consumer<Notice> newlyDelivered){
        if(!contacts.available(team))return;
        for(UUID actor:members){
            inbox.resolveForeignDiplomacy(actor,team);
            deliver(inbox,actor,"contact_"+team,"奥托的首信","团队往来：由队长或明确授权成员答复；其他成员可阅读。",
                    "letter","0",!contacts.settled(team),time,newlyDelivered);
            if(contacts.settled(team)){
                inbox.resolve(actor,"first_contact_letter");
                deliver(inbox,actor,"contact_reply_"+team,"奥托的后续来信","本队已答复。个人补谈包括首信、对应答复、后续来信与观察资料附件。",
                        "letter",contacts.state(team).equals("ACCEPTED")?"4":"5",false,time,newlyDelivered);
            }
        }
    }
    public static void diplomacy(Hk3DiplomacyData diplomacy,Hk3PhoneData inbox,UUID team,Collection<UUID> members,
                                 long time,Consumer<Notice> newlyDelivered){
        diplomacy(diplomacy,inbox,team,members,time,newlyDelivered,true);
    }
    public static void diplomacy(Hk3DiplomacyData diplomacy,Hk3PhoneData inbox,UUID team,Collection<UUID> members,
                                 long time,Consumer<Notice> newlyDelivered,boolean schicksalActive){
        var schicksal=Hk3DiplomacyData.topic("schicksal");
        var oldSchicksal=Set.of(schicksal.first(),schicksal.yes(),schicksal.no(),schicksal.refused(),schicksal.submit(),schicksal.feedback(),schicksal.retry(),schicksal.resumed(),"A06");
        for(UUID actor:members){
            inbox.resolveForeignDiplomacy(actor,team);
            for(String id:diplomacy.documents(team))deliver(inbox,actor,"diplomacy_"+team+"_"+id,
                    Hk3DiplomacyService.title(id),"收到一封团队来信，请打开正文查看并答复。","diplomacy",team+"/"+id,
                    (schicksalActive||!oldSchicksal.contains(id))&&diplomacy.pendingDocument(team,id),time,newlyDelivered);
        }
    }
}
