package com.sirin.hk3gtl.common.easter;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.NoteBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.entity.Entity;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;
/** 【变更记录 #1】2026-10-01 04:55:02（修订128）：删除无；新增手动音符请求与实际奏响结果配对；用途：取消声音、红石自动演奏、不足间隔不算本人手动20次，临时队列有界清理。 */
@Mod.EventBusSubscriber(modid="hk3gtl")
/** 【变更记录 #2】2026-10-01 05:59:33（修订128）：删除：无；新增/修改：现有成功交互串联本人装饰、存取与自然场景检测；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public final class Hk3EggMusic {
    private record Key(Level level,BlockPos pos){}
    private record Pending(UUID player,long tick,int note){}
    private static final Map<Key,Pending> PENDING=new java.util.concurrent.ConcurrentHashMap<>();
    private Hk3EggMusic(){}
    public static void queued(Entity actor,BlockState state,Level level,BlockPos pos){
        if(level.isClientSide)return;var key=new Key(level,pos.immutable());
        if(actor instanceof ServerPlayer p&&(state.getValue(NoteBlock.INSTRUMENT).worksAboveNoteBlock()||level.getBlockState(pos.above()).isAir())&&PENDING.size()<2048)PENDING.put(key,new Pending(p.getUUID(),level.getGameTime(),state.getValue(NoteBlock.NOTE)));else PENDING.remove(key);
    }
    private static net.minecraft.nbt.CompoundTag counter(ServerPlayer p,BlockPos pos){
        var s=Hk3EggRuntime.state(p);var notes=s.getCompound("noteBlocks");String key=Hk3EggVanilla.key(p,pos);
        if(!notes.contains(key)){if(notes.size()>=64)notes.remove(notes.getAllKeys().iterator().next());notes.put(key,new net.minecraft.nbt.CompoundTag());}
        s.put("noteBlocks",notes);return notes.getCompound(key);
    }
    public static void tuned(ServerPlayer p,BlockPos pos){var n=counter(p,pos);n.putInt("tunes",Math.min(8,n.getInt("tunes")+1));}
    public static void played(BlockState state,Level level,BlockPos pos,boolean success){
        if(!(level instanceof ServerLevel server))return;var pending=PENDING.remove(new Key(level,pos));
        if(!success||pending==null||level.getGameTime()-pending.tick<0||level.getGameTime()-pending.tick>2||pending.note!=state.getValue(NoteBlock.NOTE))return;
        var p=server.getServer().getPlayerList().getPlayer(pending.player);if(p==null||p.level()!=level)return;
        Hk3EggExtraScenes.played(p,pos);
        var n=counter(p,pos);if(n.getInt("tunes")>=8)Hk3EggVanilla.caseEvent(p,288);
        long now=level.getGameTime();if(!n.contains("lastPlayed")||now-n.getLong("lastPlayed")>=10){int count=Math.min(20,n.getInt("plays")+1);n.putInt("plays",count);n.putLong("lastPlayed",now);if(count>=20)Hk3EggVanilla.caseEvent(p,300);}
        if(pos.getY()<level.getSeaLevel()&&!level.canSeeSky(pos.above())){
            var instruments=n.getCompound("instruments");instruments.putBoolean(state.getValue(NoteBlock.INSTRUMENT).getSerializedName(),true);n.put("instruments",instruments);if(instruments.size()>=2)Hk3EggVanilla.caseEvent(p,413);
        }
    }
    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent e){if(e.phase==TickEvent.Phase.END)PENDING.entrySet().removeIf(v->v.getKey().level.getServer()==e.getServer()&&v.getKey().level.getGameTime()-v.getValue().tick>2);}
    @SubscribeEvent public static void stop(ServerStoppedEvent e){PENDING.entrySet().removeIf(v->v.getKey().level.getServer()==e.getServer());}
}
