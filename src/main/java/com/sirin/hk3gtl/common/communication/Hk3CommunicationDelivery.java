package com.sirin.hk3gtl.common.communication;

import com.sirin.hk3gtl.common.phone.Hk3PhoneData;
import java.util.*;
import java.util.function.Consumer;

/** 【变更记录 #1】2026-10-01 00:55:45（修订124）：删除无；新增首信和五方往来的共用投递投影；修改服务端与整链测试复用同一逻辑；用途：离线入箱、幂等通知、待处理和个人已读分别记账，不发业务奖励。 */
/** 【变更记录 #2】2026-10-01 22:50:14（第2次备注 · 内测5修订155）：删除玩家展示中的旧电压及开发说明；新增现行正文投影或对应回归；修改仅限呈现与检索，不改变进度、回执、触发条件或权限；用途：统一发布版玩家文案，历史备注保留。 */
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
        for(UUID actor:members){
            inbox.resolveForeignDiplomacy(actor,team);
            for(String id:diplomacy.documents(team))deliver(inbox,actor,"diplomacy_"+team+"_"+id,
                    Hk3DiplomacyService.title(id),"收到一封团队来信，请打开正文查看并答复。","diplomacy",team+"/"+id,
                    diplomacy.pendingDocument(team,id),time,newlyDelivered);
        }
    }
}
