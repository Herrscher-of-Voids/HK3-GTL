package com.sirin.hk3gtl.common.easter;


 

 
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.nbt.CompoundTag;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;
 
@Mod.EventBusSubscriber(modid="hk3gtl")
 
 
 
 
 
 
 
public final class Hk3EggReading {
     
     
 
    private static boolean guarded(String id){return com.sirin.hk3gtl.common.phone.Hk3PhoneVoltagePages.managed(id)||com.sirin.hk3gtl.common.phone.Hk3SocialBuiltinTopics.managed(id)||com.sirin.hk3gtl.common.phone.Hk3PhoneCollectionService.managed(id)||com.sirin.hk3gtl.common.phone.Hk3PhoneCivilizationReading.managed(id)||com.sirin.hk3gtl.common.phone.Hk3PhoneInstructionPages.managed(id);}
    private static boolean authorized(ServerPlayer p,String id){if(com.sirin.hk3gtl.common.phone.Hk3PhoneVoltagePages.managed(id))return com.sirin.hk3gtl.common.phone.Hk3PhoneVoltagePages.authorize(p,id);if(com.sirin.hk3gtl.common.phone.Hk3SocialBuiltinTopics.managed(id))return com.sirin.hk3gtl.common.phone.Hk3SocialBuiltinTopics.authorize(p,id);if(com.sirin.hk3gtl.common.phone.Hk3PhoneCivilizationReading.managed(id))return com.sirin.hk3gtl.common.phone.Hk3PhoneCivilizationReading.authorize(p);if(com.sirin.hk3gtl.common.phone.Hk3PhoneInstructionPages.managed(id))return com.sirin.hk3gtl.common.phone.Hk3PhoneInstructionPages.authorize(p,id);return com.sirin.hk3gtl.common.phone.Hk3PhoneCollectionService.authorize(p,id);}
    private static final Hk3ReadingSessions READING = new Hk3ReadingSessions();
    private static final class Open { final UUID token;final String id;final long expires;long previous;boolean crossed;Open(UUID token,String id,long time,long expires){this.token=token;this.id=id;this.previous=time;this.expires=expires;} }
    private static final Map<UUID,Open> OPEN=new java.util.concurrent.ConcurrentHashMap<>();
    private Hk3EggReading(){}
    @SubscribeEvent public static void tick(net.minecraftforge.event.TickEvent.PlayerTickEvent e){if(e.phase==net.minecraftforge.event.TickEvent.Phase.END&&e.player instanceof ServerPlayer p){var open=OPEN.get(p.getUUID());if(open!=null){long now=p.server.overworld().getGameTime();if(guarded(open.id)&&(now>=open.expires||now<open.expires-36000||!authorized(p,open.id))){clear(p.getUUID());return;}long time=p.server.overworld().getDayTime();if(time==open.previous+1&&Math.floorMod(time,24000)==17000)open.crossed=true;open.previous=time;}}}
    public static void clear(UUID player){READING.clear(player);OPEN.remove(player);com.sirin.hk3gtl.common.phone.Hk3SocialBuiltinTopics.clear(player);com.sirin.hk3gtl.common.phone.Hk3PhoneCollectionService.clear(player);com.sirin.hk3gtl.common.narrative.Hk3LegacyArchiveService.clear(player);}
    public static void attach(ServerPlayer p,CompoundTag view){
         
        com.sirin.hk3gtl.common.phone.Hk3PhoneGallery.view(p,view);
        String mode=view.getString("Mode"),id=view.getString("Id");
        if(mode.equals("status")||mode.equals("toast"))return;
        com.sirin.hk3gtl.common.phone.Hk3PhoneCollectionService.viewChanged(p,view);
        com.sirin.hk3gtl.common.phone.Hk3SocialBuiltinTopics.viewChanged(p,view);
        READING.clear(p.getUUID());OPEN.remove(p.getUUID());
        String action=view.getString("Token");
        if(id.isEmpty()&&!action.isEmpty())id="preview_"+action;
        if(!Set.of("letter","detail","diplomacy_read","archive_detail","instruction_read").contains(mode)||id.isEmpty()||view.getString("Body").isBlank())return;
        var session=READING.open(p.getUUID(),id,view.getString("Body"),action,mode.equals("letter")||mode.equals("diplomacy_read"),p.server.overworld().getGameTime());
        var token=session.token();
        OPEN.put(p.getUUID(),new Open(token,id,p.server.overworld().getDayTime(),session.expires()));
        view.putUUID("ReadToken",token);
    }
    public static void accept(ServerPlayer p,UUID token,int start,String piece){
        if(start<0){var open=OPEN.get(p.getUUID());if(open!=null&&open.token.equals(token)){long now=p.server.overworld().getGameTime();if(start==-2&&com.sirin.hk3gtl.common.phone.Hk3PhoneInstructionPages.managed(open.id)&&now<open.expires&&now>=open.expires-36000&&authorized(p,open.id))com.sirin.hk3gtl.common.phone.Hk3PhoneInstructionPages.closed(p,open.id);else if(open.crossed&&!guarded(open.id))Hk3EggVanilla.caseEvent(p,303);clear(p.getUUID());}return;}
        var open=OPEN.get(p.getUUID());
        if(open!=null&&guarded(open.id)&&!authorized(p,open.id)){clear(p.getUUID());return;}
        var s=READING.accept(p.getUUID(),token,start,piece,p.server.overworld().getGameTime());
        if(s==null)return;
        if(guarded(s.id())){
            if(com.sirin.hk3gtl.common.phone.Hk3PhoneVoltagePages.managed(s.id()))com.sirin.hk3gtl.common.phone.Hk3PhoneVoltagePages.completed(p,s);
            else if(com.sirin.hk3gtl.common.phone.Hk3SocialBuiltinTopics.managed(s.id()))com.sirin.hk3gtl.common.phone.Hk3SocialBuiltinTopics.completed(p,s);
            else if(com.sirin.hk3gtl.common.phone.Hk3PhoneCivilizationReading.managed(s.id()))com.sirin.hk3gtl.common.phone.Hk3PhoneCivilizationReading.completed(p,s);
            else if(com.sirin.hk3gtl.common.phone.Hk3PhoneInstructionPages.managed(s.id()))com.sirin.hk3gtl.common.phone.Hk3PhoneInstructionPages.completed(p,s);
            else com.sirin.hk3gtl.common.phone.Hk3PhoneCollectionService.readCompleted(p,s);
            var ack=new CompoundTag();ack.putString("Mode","read_complete");ack.putUUID("ReadToken",token);
            com.sirin.hk3gtl.common.network.Hk3Network.CHANNEL.send(net.minecraftforge.network.PacketDistributor.PLAYER.with(()->p),new com.sirin.hk3gtl.common.phone.Hk3PhonePacket(ack));return;
        }
        if(s.id().startsWith("formal_"))com.sirin.hk3gtl.common.narrative.Hk3LegacyArchiveService.readCompleted(p,s);
        var acknowledgement=new CompoundTag();acknowledgement.putString("Mode","read_complete");acknowledgement.putUUID("ReadToken",token);
        com.sirin.hk3gtl.common.network.Hk3Network.CHANNEL.send(net.minecraftforge.network.PacketDistributor.PLAYER.with(()->p),new com.sirin.hk3gtl.common.phone.Hk3PhonePacket(acknowledgement));
        com.sirin.hk3gtl.common.communication.Hk3TeamContactService.readCompleted(p,s.id());
        if(s.id().startsWith("formal_"))return;
        var state=Hk3EggRuntime.state(p);
        if(s.id().startsWith("egg_if_")){
            boolean free=s.id().startsWith("egg_if_free_");int index=Integer.parseInt(s.id().substring(s.id().lastIndexOf('_')+1));
            if(!free)state.putInt("readNormalIf",state.getInt("readNormalIf")|(1<<index));
            Hk3EggRuntime.observe(p,"if_read",Hk3EggRuntime.fields("free",Boolean.toString(free),"complete","true","normal_count",Integer.toString(Integer.bitCount(state.getInt("readNormalIf")))));return;
        }
        var read=state.getCompound("fullyRead");if(read.size()<101&&com.sirin.hk3gtl.common.phone.Hk3PhoneData.get(p).entry(p.getUUID(),s.id())!=null)read.putBoolean(Hk3EggNotes.digest(s.id()),true);state.put("fullyRead",read);
        var first=state.getCompound("firstLetters");
        if(s.id().startsWith("contact_")&&!s.id().startsWith("contact_reply_"))first.putBoolean("158",true);
        for(var pair:Map.of("_A08","159","_A09","160","_SF01","161","_ER01","162").entrySet())if(s.id().startsWith("diplomacy_")&&s.id().endsWith(pair.getKey()))first.putBoolean(pair.getValue(),true);
        state.put("firstLetters",first);
        var facts=new LinkedHashMap<>(Hk3EggCalendar.facts(Hk3EggCalendar.now(),p.server.overworld().getDayTime()));
        facts.put("id",s.id());facts.put("letter",Boolean.toString(s.letter()));facts.put("pages",Integer.toString(s.cursor().pages()));facts.put("read_count",Integer.toString(read.size()));facts.put("first_letters",Integer.toString(first.size()));
        if(state.getBoolean("awayThreeDays")&&com.sirin.hk3gtl.common.phone.Hk3PhoneData.get(p).entry(p.getUUID(),s.id())!=null){Hk3EggVanilla.caseEvent(p,494);state.remove("awayThreeDays");}
        if(s.letter()&&com.sirin.hk3gtl.common.phone.Hk3PhoneData.get(p).entry(p.getUUID(),s.id())!=null)Hk3EggCraftingReceipts.readLetter(p);
        Hk3EggRuntime.observe(p,"reading_complete",facts);
        for(String number:first.getAllKeys())Hk3EggRuntime.observe(p,"first_letter_read",Map.of("case",number));
    }
    public static boolean consumeAction(ServerPlayer player,String token){
        return READING.consumeAction(player.getUUID(),token,player.server.overworld().getGameTime());
    }
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e){clear(e.getEntity().getUUID());}
    @SubscribeEvent public static void stop(ServerStoppedEvent e){READING.clear();OPEN.clear();com.sirin.hk3gtl.common.phone.Hk3PhoneCollectionService.clear();}
}
