package com.sirin.hk3gtl.client.dialogue;
import com.sirin.hk3gtl.common.easter.*;
import com.sirin.hk3gtl.common.network.Hk3Network;
/** 【变更记录 #1】2026-10-01 04:34:32（修订128）：删除无；新增逐句完整显示回报；修改无；用途：只有本段按序显示完的句子才累计，快速跳段和旧令牌无法补出全文。 */
public final class Hk3EggDialogueClient {
    private static Hk3EggDialoguePacket current;private static int next,offset;
    private Hk3EggDialogueClient(){}
    public static void begin(Hk3EggDialoguePacket packet){current=packet;next=0;offset=0;}
    public static void revealed(String dialogue,String segment,int index,String text){
        if(current==null||!current.dialogue().equals(dialogue)||!current.segment().equals(segment)||index!=next)return;
        String piece=Hk3EggReadingCursor.normalize(text);if(piece.isEmpty()||piece.length()>4096)return;
        Hk3Network.CHANNEL.sendToServer(new Hk3EggReadPacket(current.token(),offset,piece));next++;offset+=piece.length();
    }
    public static void clear(){current=null;next=0;offset=0;}
}
