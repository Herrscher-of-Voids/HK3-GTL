package com.sirin.hk3gtl.client.dialogue;
import com.sirin.hk3gtl.common.easter.*;
import com.sirin.hk3gtl.common.network.Hk3Network;
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
