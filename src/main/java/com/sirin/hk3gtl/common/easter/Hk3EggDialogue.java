package com.sirin.hk3gtl.common.easter;
import com.sirin.hk3gtl.common.dialogue.*;
import com.sirin.hk3gtl.common.dialogue.definition.*;
import com.sirin.hk3gtl.common.network.Hk3Network;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.network.chat.Component;
import net.minecraft.nbt.CompoundTag;
import net.minecraftforge.network.PacketDistributor;

public final class Hk3EggDialogue {
    private Hk3EggDialogue(){}
    public static void opened(ServerPlayer p,String dialogue,String segment){
        Hk3EggReading.clear(p.getUUID());int index=-1;boolean free=dialogue.equals(Hk3IfArchiveDialogue.ID);
        if(free&&segment.matches("if_[0-9]{1,2}"))index=Integer.parseInt(segment.substring(3));
        else if(dialogue.equals(SirinDialogueDefinitions.DIALOGUE_ID))index=Hk3ApprovedDialogues.ifIndex(segment);
        if(index<0||index>=26)return;
        if(!free&&(Hk3FinaleIfData.get(p).selectedMask(p.getUUID())&(1<<index))==0)return;
        var def=DialogueRegistry.getDialogue(dialogue);if(def==null||!def.segments().containsKey(segment))return;
        var body=new StringBuilder();for(var line:def.segments().get(segment))body.append(Component.translatable(line.textKey()).getString());
        var v=new CompoundTag();v.putString("Mode","archive_detail");v.putString("Id",(free?"egg_if_free_":"egg_if_normal_")+index);v.putString("Body",body.toString());
        Hk3EggReading.attach(p,v);if(v.hasUUID("ReadToken"))Hk3Network.CHANNEL.send(PacketDistributor.PLAYER.with(()->p),new Hk3EggDialoguePacket(dialogue,segment,v.getUUID("ReadToken")));
    }
}
