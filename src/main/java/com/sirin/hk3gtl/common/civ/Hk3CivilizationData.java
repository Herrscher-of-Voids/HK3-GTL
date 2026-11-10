package com.sirin.hk3gtl.common.civ;
import net.minecraft.nbt.*;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.server.MinecraftServer;
import java.util.*;
import java.util.function.Predicate;

/** 【变更记录 #1】2026-09-30 23:43:42（修订120）：删除无；新增/修改：以研究团队UUID持久化文明历史最高级，换队读取新队、拆机不降级、损坏文件明确报错；用途：按真实团队事实展示文明进度，不给机器/配方增加等级锁。 */
/** 【变更记录 #2】2026-11-04（修订197）：删除无；新增规范团队UUID校验及中文损坏异常；修改拒绝别名键覆盖同队历史；用途：损坏存档明确拒绝，保留原始文件。 */
public final class Hk3CivilizationData extends SavedData {
    private final Map<UUID,Integer> highest=new HashMap<>();
    public static Hk3CivilizationData get(MinecraftServer server){return com.sirin.hk3gtl.common.util.Hk3SavedDataGuard.get(server,"hk3gtl_civilization_v5",Hk3CivilizationData::load,Hk3CivilizationData::new);}
    public int highest(UUID team){return highest.getOrDefault(team,0);}
    public int observe(UUID team,Predicate<String> facts){
        Objects.requireNonNull(team);int level=Math.max(highest(team),Hk3CivilizationRules.achieved(facts));
        if(level>highest(team)){highest.put(team,level);setDirty();}return level;
    }
    @Override public CompoundTag save(CompoundTag n){n.putInt("Version",1);var teams=new CompoundTag();highest.forEach((id,level)->teams.putInt(id.toString(),level));n.put("Teams",teams);return n;}
    public static Hk3CivilizationData load(CompoundTag n){
        if(!n.contains("Version",Tag.TAG_INT)||n.getInt("Version")!=1||!n.contains("Teams",Tag.TAG_COMPOUND))throw new IllegalStateException("文明等级记录格式损坏");
        var data=new Hk3CivilizationData();var teams=n.getCompound("Teams");
        for(String id:teams.getAllKeys()){
            if(!teams.contains(id,Tag.TAG_INT)||teams.getInt(id)<0||teams.getInt(id)>7)throw new IllegalStateException("文明等级记录越界");
            UUID team;
            try{team=UUID.fromString(id);}catch(IllegalArgumentException ex){throw new IllegalStateException("文明团队标识损坏："+id,ex);}
            if(!team.toString().equals(id))throw new IllegalStateException("文明团队标识格式损坏："+id);
            data.highest.put(team,teams.getInt(id));
        }return data;
    }
}
