package com.sirin.hk3gtl.common.easter;
import com.sirin.hk3gtl.common.util.Hk3SavedDataGuard;
import net.minecraft.server.MinecraftServer;
import net.minecraft.nbt.*;
import net.minecraft.world.level.saveddata.SavedData;
import java.util.*;
/** 【变更记录 #1】2026-10-01 04:24:23（修订128）：删除无；新增个人真实产物账本；修改无；用途：离线生产记录归放置者，逐存档保存，只追踪已注册规则目标，饱和计数防溢出。 */
/** 【变更记录 #2】2026-10-01 05:50:31（修订128）：删除：无；新增/修改：工业彩蛋账本损坏只停可选记录，不让已成功的配方因为收藏记录失败而中断；不重置旧账本；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #3】2026-10-01 13:40:41（修订128）：删除：无；新增/修改：增加只读单项计数入口，避免发电每tick复制整个个人产量表；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public final class Hk3EggProductionData extends SavedData {
    private final Map<UUID,Map<String,Long>> counts=new HashMap<>();
    private boolean disabled;
    private static final Map<MinecraftServer,Hk3EggProductionData> FAILED=Collections.synchronizedMap(new WeakHashMap<>());
    public static Hk3EggProductionData get(MinecraftServer server){
        var failed=FAILED.get(server);if(failed!=null)return failed;
        try{return Hk3SavedDataGuard.get(server,"hk3gtl_egg_production",Hk3EggProductionData::load,Hk3EggProductionData::new);}
        catch(RuntimeException error){var offline=new Hk3EggProductionData();offline.disabled=true;FAILED.put(server,offline);com.mojang.logging.LogUtils.getLogger().error("[HK3GTL] 工业彩蛋账本不可读，本次运行关闭相关检测；保留原文件，不影响实际生产",error);return offline;}
    }
    public static long plus(long a,long b){if(a<0||b<0)throw new IllegalArgumentException("产量不能为负");return a>Long.MAX_VALUE-b?Long.MAX_VALUE:a+b;}
    public void produced(UUID user,String item,long amount){if(disabled||amount<=0||!Hk3EggProduction.watches(item))return;var own=counts.computeIfAbsent(user,k->new HashMap<>());own.put(item,plus(own.getOrDefault(item,0L),amount));setDirty();}
    public long count(UUID user,String item){return counts.getOrDefault(user,Map.of()).getOrDefault(item,0L);}
    public Map<String,Long> counts(UUID user){return Map.copyOf(counts.getOrDefault(user,Map.of()));}
    public static Hk3EggProductionData load(CompoundTag n){
        if(!n.contains("Users",10))throw new IllegalArgumentException("生产收藏账本缺少用户表");
        var out=new Hk3EggProductionData();var users=n.getCompound("Users");
        for(String key:users.getAllKeys()){
            UUID id=UUID.fromString(key);var values=users.getCompound(key);var map=new HashMap<String,Long>();
            for(String item:values.getAllKeys()){if(!values.contains(item,4)||values.getLong(item)<0)throw new IllegalArgumentException("生产收藏账本数值无效");map.put(item,values.getLong(item));}
            out.counts.put(id,map);
        }return out;
    }
    @Override public CompoundTag save(CompoundTag n){var users=new CompoundTag();counts.forEach((id,values)->{var v=new CompoundTag();values.forEach(v::putLong);users.put(id.toString(),v);});n.put("Users",users);return n;}
}
