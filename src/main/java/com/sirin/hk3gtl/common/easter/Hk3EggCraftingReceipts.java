package com.sirin.hk3gtl.common.easter;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import java.util.UUID;
/** 【变更记录 #1】2026-10-01 06:27:59（修订128）：删除无；新增AE实际提交、完成与转化回执；修改无；用途：失败、取消、模拟及创造拿取不当生产，归属写入CPU存档。 */
/** 【变更记录 #2】2026-10-01 06:35:47（修订128）：删除：无；新增/修改：任务旁注有界淘汰旧证据而非永久拒绝新任务；转化快照移到普通公共record，不依赖Mixin嵌套访问；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
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
