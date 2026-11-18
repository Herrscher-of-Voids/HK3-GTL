package com.sirin.hk3gtl.client.phone;


import com.sirin.hk3gtl.common.easter.*;
import com.sirin.hk3gtl.common.network.Hk3Network;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.util.FormattedCharSequence;
import java.util.*;
public final class Hk3EggReadClient {
    private UUID token;private int observed=-1,nextOffset;private int[] dwell=new int[0];private boolean confirmed;private final Set<Integer> sent=new HashSet<>();
    public void tick(CompoundTag view,List<FormattedCharSequence> lines,int page,int size,int firstVisible,int lastVisible){
        if(!view.hasUUID("ReadToken")){close();return;}
        UUID next=view.getUUID("ReadToken");if(!next.equals(token)){close();token=next;}
        if(observed!=page){observed=page;dwell=new int[Math.min(size,lines.size()-page*size)];}
        if(sent.contains(page))return;
        for(int i=firstVisible;i<lastVisible;i++)dwell[i]++;
        for(int ticks:dwell)if(ticks<20)return;
        var before=new StringBuilder();var current=new StringBuilder();
        for(int i=0;i<Math.min(lines.size(),(page+1)*size);i++){
            var output=i<page*size?before:current;lines.get(i).accept((index,style,cp)->{output.appendCodePoint(cp);return true;});
        }
        String piece=Hk3EggReadingCursor.normalize(current.toString());if(piece.isEmpty()||piece.length()>4096)return;
        int start=Hk3EggReadingCursor.normalize(before.toString()).length();if(start!=nextOffset)return;
        Hk3Network.CHANNEL.sendToServer(new Hk3EggReadPacket(token,start,piece));sent.add(page);nextOffset+=piece.length();
    }
    public void confirm(UUID readToken){if(readToken.equals(token))confirmed=true;}
    public boolean complete(CompoundTag view){return confirmed&&token!=null&&view.hasUUID("ReadToken")&&token.equals(view.getUUID("ReadToken"))
        &&nextOffset==Hk3EggReadingCursor.normalize(view.getString("Body")).length();}
    public void leaveInstruction(CompoundTag view){if(view.getBoolean("InstructionPage")&&view.hasUUID("ReadToken"))Hk3Network.CHANNEL.sendToServer(new Hk3EggReadPacket(view.getUUID("ReadToken"),-2,""));close();}
    public void close(){if(token!=null)Hk3Network.CHANNEL.sendToServer(new Hk3EggReadPacket(token,-1,""));token=null;observed=-1;dwell=new int[0];nextOffset=0;confirmed=false;sent.clear();}
}
