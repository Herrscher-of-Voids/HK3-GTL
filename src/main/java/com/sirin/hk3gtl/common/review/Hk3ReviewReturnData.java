package com.sirin.hk3gtl.common.review;

import net.minecraft.nbt.*;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.saveddata.SavedData;
import java.util.*;

/** 【变更记录 #1】2026-10-01 18:42:57（修订140）：删除无；新增一审召入前返程账本；修改先留原位置再传送、成功返回才删除；用途：断线、重启、死亡或传送失败不丢返程位置，损坏记录拒绝空建覆盖。 */
public final class Hk3ReviewReturnData extends SavedData {
    public record ReturnPoint(UUID meeting,String dimension,double x,double y,double z,float yaw,float pitch){}
    private final Map<UUID,ReturnPoint> points=new LinkedHashMap<>();
    private long nextRoom;
    public static Hk3ReviewReturnData get(MinecraftServer server){return com.sirin.hk3gtl.common.util.Hk3SavedDataGuard.get(server,"hk3gtl_review_returns_v140",Hk3ReviewReturnData::load,Hk3ReviewReturnData::new);}
    public ReturnPoint point(UUID player){return points.get(player);}
    public long room(){if(nextRoom>=1_000_000)throw new IllegalStateException("审查场景编号已用尽");setDirty();return nextRoom++;}
    public void remember(ServerPlayer p,UUID meeting){
        if(points.containsKey(p.getUUID()))throw new IllegalStateException("必须先完成旧会面的返程");
        points.put(p.getUUID(),new ReturnPoint(meeting,p.level().dimension().location().toString(),p.getX(),p.getY(),p.getZ(),p.getYRot(),p.getXRot()));setDirty();
    }
    public void returned(UUID player){if(points.remove(player)!=null)setDirty();}
    @Override public CompoundTag save(CompoundTag n){
        n.putInt("Schema",1);n.putLong("Room",nextRoom);var list=new ListTag();points.forEach((p,r)->{
            var row=new CompoundTag();row.putUUID("Player",p);row.putUUID("Meeting",r.meeting);row.putString("Dimension",r.dimension);row.putDouble("X",r.x);row.putDouble("Y",r.y);row.putDouble("Z",r.z);row.putFloat("Yaw",r.yaw);row.putFloat("Pitch",r.pitch);list.add(row);
        });n.put("Returns",list);return n;
    }
    public static Hk3ReviewReturnData load(CompoundTag n){
        if(n.getInt("Schema")!=1||!n.contains("Room",Tag.TAG_LONG)||!n.contains("Returns",Tag.TAG_LIST))throw new IllegalArgumentException("返程账本结构损坏");
        var d=new Hk3ReviewReturnData();d.nextRoom=n.getLong("Room");if(d.nextRoom<0||d.nextRoom>1_000_000)throw new IllegalArgumentException("场景编号损坏");
        var list=n.getList("Returns",Tag.TAG_COMPOUND);if(list.size()!=((ListTag)n.get("Returns")).size())throw new IllegalArgumentException("返程记录类型错误");
        for(Tag raw:list){var r=(CompoundTag)raw;
            for(String k:List.of("X","Y","Z"))if(!r.contains(k,Tag.TAG_DOUBLE)||!Double.isFinite(r.getDouble(k)))throw new IllegalArgumentException("返程坐标损坏");
            for(String k:List.of("Yaw","Pitch"))if(!r.contains(k,Tag.TAG_FLOAT)||!Float.isFinite(r.getFloat(k)))throw new IllegalArgumentException("返程朝向损坏");
            if(net.minecraft.resources.ResourceLocation.tryParse(r.getString("Dimension"))==null)throw new IllegalArgumentException("返程维度损坏");
            var point=new ReturnPoint(r.getUUID("Meeting"),r.getString("Dimension"),r.getDouble("X"),r.getDouble("Y"),r.getDouble("Z"),r.getFloat("Yaw"),r.getFloat("Pitch"));
            if(d.points.putIfAbsent(r.getUUID("Player"),point)!=null)throw new IllegalArgumentException("重复返程记录");
        }return d;
    }
}
