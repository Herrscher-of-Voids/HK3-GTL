package com.sirin.hk3gtl.common.easter;
import net.minecraft.server.level.*;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.*;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.core.registries.BuiltInRegistries;
import java.util.*;
/** 【变更记录 #1】2026-10-01 05:41:36（修订128）：删除无；新增每维度最近32768处实际放置记录与持久归属，超界只丢历史证据不补授；修改无；用途：只读当前已加载建筑，不生成结构或授予工程验收。 */
/** 【变更记录 #2】2026-10-01 05:50:31（修订128）：删除：无；新增/修改：读取损坏账本时拒绝覆盖旧文件，当前维度相关彩蛋关闭并一次记录日志，不让放置或爆炸回调崩溃；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #3】2026-10-01 13:29:18（修订128）：删除：无；新增/修改：生成黑曜石与普通手放方块区分，任何替换都撤销生成标记，采掘前验证真实来源；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public final class Hk3EggBuildMemory extends SavedData {
    private record Cell(UUID owner,String block){}
    private static final int LIMIT=32768;
    private final LinkedHashMap<Long,Cell> cells=new LinkedHashMap<>();
    private boolean disabled;
    private final Set<Long> madeObsidian=new HashSet<>();
    private static final Map<ServerLevel,Hk3EggBuildMemory> FAILED=Collections.synchronizedMap(new WeakHashMap<>());
    public static Hk3EggBuildMemory get(ServerLevel level){
        var failed=FAILED.get(level);if(failed!=null)return failed;
        var file=net.minecraft.world.level.dimension.DimensionType.getStorageFolder(level.dimension(),level.getServer().getWorldPath(net.minecraft.world.level.storage.LevelResource.ROOT)).resolve("data/hk3gtl_egg_builds.dat");
        try{return level.getDataStorage().computeIfAbsent(Hk3EggBuildMemory::load,()->com.sirin.hk3gtl.common.util.Hk3SavedDataGuard.freshIfMissing(file,Hk3EggBuildMemory::new),"hk3gtl_egg_builds");}
        catch(RuntimeException error){var offline=new Hk3EggBuildMemory();offline.disabled=true;FAILED.put(level,offline);com.mojang.logging.LogUtils.getLogger().error("[HK3GTL] 建筑彩蛋记录不可读，本次运行关闭相关检测，保留原文件：{}",file,error);return offline;}
    }
    public void placed(ServerPlayer p,BlockPos pos){
        if(disabled)return;long key=pos.asLong();madeObsidian.remove(key);cells.remove(key);cells.put(key,new Cell(p.getUUID(),BuiltInRegistries.BLOCK.getKey(p.level().getBlockState(pos).getBlock()).toString()));
        if(cells.size()>LIMIT){long oldest=cells.keySet().iterator().next();cells.remove(oldest);madeObsidian.remove(oldest);}setDirty();
    }
    public void changed(BlockPos pos){madeObsidian.remove(pos.asLong());if(cells.remove(pos.asLong())!=null)setDirty();}
    public boolean madeObsidian(ServerPlayer p,BlockPos pos){return madeObsidian.contains(pos.asLong())&&owns(p,pos);}
    public void madeObsidian(ServerPlayer p,BlockPos pos,boolean produced){if(!produced||disabled)return;placed(p,pos);madeObsidian.add(pos.asLong());setDirty();}
    public UUID recordedOwner(BlockPos pos,String block){var c=cells.get(pos.asLong());return c!=null&&c.block.equals(block)?c.owner:null;}

    public boolean owns(ServerPlayer p,BlockPos pos){
        var cell=cells.get(pos.asLong());return cell!=null&&cell.owner.equals(p.getUUID())&&p.level().hasChunkAt(pos)&&cell.block.equals(BuiltInRegistries.BLOCK.getKey(p.level().getBlockState(pos).getBlock()).toString());
    }
    public List<BlockPos> near(ServerPlayer p,BlockPos origin,int radius){
        var out=new ArrayList<BlockPos>();for(var e:cells.entrySet())if(e.getValue().owner.equals(p.getUUID())){var at=BlockPos.of(e.getKey());if(Math.abs(at.getX()-origin.getX())<=radius&&Math.abs(at.getY()-origin.getY())<=radius&&Math.abs(at.getZ()-origin.getZ())<=radius&&owns(p,at))out.add(at);}return out;
    }
    public static Hk3EggBuildMemory load(CompoundTag root){
        if(root.getInt("Schema")!=1||!root.contains("Cells",9))throw new IllegalArgumentException("建筑彩蛋归属账本格式错误");
        var out=new Hk3EggBuildMemory();var rows=root.getList("Cells",10);if(rows.size()>LIMIT)throw new IllegalArgumentException("建筑彩蛋归属超出有界容量");
        for(var raw:rows){var n=(CompoundTag)raw;if(!n.hasUUID("Owner")||n.getString("Block").isBlank())throw new IllegalArgumentException("建筑彩蛋归属记录错误");out.cells.put(n.getLong("Pos"),new Cell(n.getUUID("Owner"),n.getString("Block")));}for(long packed:root.getLongArray("MadeObsidian"))if(out.cells.containsKey(packed))out.madeObsidian.add(packed);return out;
    }
    @Override public CompoundTag save(CompoundTag root){root.putInt("Schema",1);root.putLongArray("MadeObsidian",madeObsidian.stream().mapToLong(Long::longValue).toArray());var rows=new ListTag();cells.forEach((pos,cell)->{var n=new CompoundTag();n.putLong("Pos",pos);n.putUUID("Owner",cell.owner);n.putString("Block",cell.block);rows.add(n);});root.put("Cells",rows);return root;}
}
