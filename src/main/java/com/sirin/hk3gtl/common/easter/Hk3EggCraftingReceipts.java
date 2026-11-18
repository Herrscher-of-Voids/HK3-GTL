package com.sirin.hk3gtl.common.easter;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import java.util.UUID;
public final class Hk3EggCraftingReceipts {
    public record TransformInput(net.minecraft.world.entity.item.ItemEntity entity,int count,UUID owner){}
    private Hk3EggCraftingReceipts(){}
    public static void started(ServerPlayer p,UUID token,BlockPos pos,String dim){
        var state=Hk3EggRuntime.state(p);var jobs=state.getCompound("eggAeTasks");
        if(jobs.size()>=64){String oldest=null;long tick=Long.MAX_VALUE;for(String id:jobs.getAllKeys())if(jobs.getCompound(id).getLong("start")<tick){oldest=id;tick=jobs.getCompound(id).getLong("start");}if(oldest!=null)jobs.remove(oldest);}var j=new CompoundTag();j.putLong("start",p.server.overworld().getGameTime());j.putString("dim",dim);j.putLong("pos",pos.asLong());jobs.put(token.toString(),j);state.put("eggAeTasks",jobs);
    }
    public static void readLetter(ServerPlayer p){var jobs=Hk3EggRuntime.state(p).getCompound("eggAeTasks");for(String id:jobs.getAllKeys()){var j=jobs.getCompound(id);if(j.getString("dim").equals(p.level().dimension().location().toString())&&p.position().distanceToSqr(net.minecraft.world.phys.Vec3.atCenterOf(BlockPos.of(j.getLong("pos"))))<=256)j.putBoolean("letterRead",true);}}
    public static void finished(ServerPlayer p,UUID token,boolean success){if(token==null)return;var jobs=Hk3EggRuntime.state(p).getCompound("eggAeTasks");var j=jobs.getCompound(token.toString());if(success&&j.getBoolean("letterRead"))Hk3EggVanilla.caseEvent(p,484);jobs.remove(token.toString());}
}
