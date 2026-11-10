package com.sirin.hk3gtl.common.event;

import com.sirin.hk3gtl.common.util.Hk3SavedDataGuard;
import net.minecraft.nbt.*;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;
import java.util.*;
import java.util.function.IntPredicate;

/**
 * 【变更记录 #1】2026-10-01 01:36:39（修订126）
 * 删除：无；新增：Herrscher_Void三件首次入世礼物及UUID逐件发放账本。
 * 修改：独立于旧xiguamao彩蛋；只在确认物品已插入后记录，不把缺模组/背包满算已领取。
 * 用途：世界级SavedData避免死亡重生丢失标记；逐件恢复、不自动安装手机、不写研究或终局资格。
 */
public final class Hk3VoidGiftData extends SavedData {
    public static final String TARGET="Herrscher_Void";
    public record Gift(String item,long charge) {
        public CompoundTag tag(){var n=new CompoundTag();if(charge>0)n.putLong("Charge",charge);return n;}
    }
    public static final List<Gift> GIFTS=List.of(new Gift("hk3gtl:personal_phone",128000L),
            new Gift("sov:spear_of_void",0),new Gift("sov:spear_of_void_5x",0));
    private static final int ALL=(1<<GIFTS.size())-1;
    private final Map<UUID,Integer> players=new HashMap<>();
    private boolean delivering;
    public static Hk3VoidGiftData get(MinecraftServer server){
        return Hk3SavedDataGuard.get(server,"hk3gtl_herrscher_void_gift_v1",Hk3VoidGiftData::load,Hk3VoidGiftData::new);
    }
    public static boolean matches(String name){return TARGET.equalsIgnoreCase(name);}
    public boolean enrolled(UUID player){return players.containsKey(player);}
    public boolean pending(UUID player){return enrolled(player)&&players.get(player)!=ALL;}
    public boolean enroll(UUID player,String name){
        if(delivering)throw new IllegalStateException("礼物发放不能重入");
        if(player==null||!matches(name)||enrolled(player))return false;
        players.put(player,0);setDirty();return true;
    }
    /** 插入与记账同在服务端主线程；回调拒绝时保留该项，已成功项不因后续失败回滚重发。 */
    public int deliver(UUID player,IntPredicate insert){
        if(delivering)throw new IllegalStateException("礼物发放不能重入");
        if(!pending(player))return 0;
        delivering=true;int granted=0;
        try{
            for(int i=0;i<GIFTS.size();i++)if((players.get(player)&(1<<i))==0&&insert.test(i)){
                players.put(player,players.get(player)|(1<<i));setDirty();granted++;
            }
            return granted;
        }finally{delivering=false;}
    }
    @Override public CompoundTag save(CompoundTag n){
        n.putInt("Schema",1);var rows=new CompoundTag();players.forEach((id,mask)->rows.putInt(id.toString(),mask));n.put("Players",rows);return n;
    }
    public static Hk3VoidGiftData load(CompoundTag n){
        if(!n.contains("Schema",Tag.TAG_INT)||n.getInt("Schema")!=1||!n.contains("Players",Tag.TAG_COMPOUND))throw new IllegalArgumentException("礼物账本格式错误，拒绝重置");
        var data=new Hk3VoidGiftData();var rows=n.getCompound("Players");
        for(String key:rows.getAllKeys()){
            if(!rows.contains(key,Tag.TAG_INT)||rows.getInt(key)<0||rows.getInt(key)>ALL)throw new IllegalArgumentException("礼物发放记录损坏，拒绝重发");
            if(data.players.putIfAbsent(UUID.fromString(key),rows.getInt(key))!=null)throw new IllegalArgumentException("重复玩家礼物记录");
        }
        return data;
    }
}
