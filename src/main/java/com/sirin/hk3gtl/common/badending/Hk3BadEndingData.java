package com.sirin.hk3gtl.common.badending;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

/**
 * 坏结局持久化：当前按UUID记录会面、个人阶段和历史；旧世界字段仅归档。
 *
 * <h3>阶段流转</h3>
 * <ul>
 *   <li>{@link #STAGE_NONE}：未触发，正常终局流程可用</li>
 *   <li>{@link #STAGE_ERASED}：Boss 战已触发（攻击满 10 次），世界被"抹除"，等待玩家重进虚数维度</li>
 *   <li>{@link #STAGE_COMPLETED}：坏结局终局文本播放完毕，存档已毕业</li>
 * </ul>
 *
 * <p>与 Hk3GraduationData 一样存储在主世界 data 目录（hk3gtl_bad_ending.dat）。</p>
 */
/** 【变更记录 #1】2026-09-30 23:34:26（修订119）：删除：世界级结果对所有玩家的隐式授权；新增/修改：个人会面UUID、坏结局次数、回城和九句收尾进度；读取旧世界阶段不波及新玩家；用途：个人结算不覆盖其他玩家，未完成的资格采集仍单独接入。 */
/** 【变更记录 #2】2026-10-01 16:49:18（修订135）：删除无；新增经完整资格校验的新会面/坏结局重试；修改重试保留累计坏结局历史并更换会面身份；用途：正常申请不能用调试清档替代重新核验，不改变改名或强制登出。 */
/** 【变更记录 #3】2026-10-01 17:04:49（修订136）：删除加载异常时空建坏结局账本；新增根类型/个人UUID/布尔合法性检查；修改使用防覆盖读取；用途：异常不能清掉攻击后果、收尾检查点及重试历史，保留旧世界字段。 */
public class Hk3BadEndingData extends SavedData {

    private static final Logger LOGGER = LogUtils.getLogger();
    private static final String DATA_NAME = "hk3gtl_bad_ending";

    public static final int STAGE_NONE = 0;
    public static final int STAGE_ERASED = 1;
    public static final int STAGE_COMPLETED = 2;

    /** 玩家对西琳的累计左键攻击次数（跨玩家全局累计）。 */
    private int attackCount = 0;
    /** 坏结局阶段，见 STAGE_* 常量。 */
    private int stage = STAGE_NONE;

    /** 旧世界计数/阶段保留归档，当前流程仅读写个人状态。 */
    private final java.util.Map<java.util.UUID, Personal> people = new java.util.HashMap<>();
    private record Personal(java.util.UUID meeting,int stage,boolean returned,int badCount,int line) {}
    public int getStage(java.util.UUID player) { var p=people.get(player);return p==null?STAGE_NONE:p.stage; }
    public java.util.UUID meeting(java.util.UUID player) { var p=people.get(player);return p==null?null:p.meeting; }
    public java.util.UUID beginEncounter(java.util.UUID player) {
        if (getStage(player)!=STAGE_NONE) return null;
        var p=people.get(player);if(p!=null)return p.meeting;
        var id=java.util.UUID.randomUUID();people.put(player,new Personal(id,STAGE_NONE,false,0,0));setDirty();return id;
    }
    public boolean erase(java.util.UUID player,java.util.UUID meeting) {
        var p=people.get(player);if(p==null||p.stage!=STAGE_NONE||!p.meeting.equals(meeting))return false;
        people.put(player,new Personal(meeting,STAGE_ERASED,false,Math.min(Integer.MAX_VALUE-1,p.badCount)+1,0));setDirty();return true;
    }
    public boolean returned(java.util.UUID player) {var p=people.get(player);return p!=null&&p.returned;}
    public void markReturned(java.util.UUID player) {
        var p=people.get(player);if(p==null||p.stage!=STAGE_ERASED||p.returned)return;
        people.put(player,new Personal(p.meeting,p.stage,true,p.badCount,p.line));setDirty();
    }
    public int line(java.util.UUID player) {var p=people.get(player);return p==null?0:p.line;}
    public void advanceLine(java.util.UUID player,int line) {
        var p=people.get(player);if(p==null||p.stage!=STAGE_ERASED||line!=p.line+1||line>9)return;
        people.put(player,new Personal(p.meeting,p.stage,p.returned,p.badCount,line));setDirty();
    }
    public boolean complete(java.util.UUID player) {
        var p=people.get(player);if(p==null||p.stage!=STAGE_ERASED||p.line!=9)return false;
        people.put(player,new Personal(p.meeting,STAGE_COMPLETED,p.returned,p.badCount,p.line));setDirty();return true;
    }
    public int badCount(java.util.UUID player) {var p=people.get(player);return p==null?0:p.badCount;}
    /** 仅在新申请已完整核验后建立新身份，未读完坏结局收尾不能跳过。 */
    public java.util.UUID beginQualifiedEncounter(java.util.UUID player,com.sirin.hk3gtl.common.finale.Hk3FinaleRequirements.Evaluation qualification) {
        if(!qualification.ready()||!com.sirin.hk3gtl.common.finale.Hk3FinaleRequirements.validSnapshot(qualification.sources(),player)
                ||getStage(player)==STAGE_ERASED)return null;
        var id=java.util.UUID.randomUUID();int history=badCount(player);
        people.put(player,new Personal(id,STAGE_NONE,false,history,0));setDirty();return id;
    }
    /** 仅显式管理员调试调用；资格复核后的新申请入口须另接，不能用重连清除历史。 */
    public void resetForDebug(java.util.UUID player) { if(people.remove(player)!=null)setDirty(); }
    public Hk3BadEndingData() {}

    public static Hk3BadEndingData load(CompoundTag tag) {
        com.sirin.hk3gtl.common.util.Hk3LedgerValidation.require(tag.contains("Personal")||(tag.contains("AttackCount")&&tag.contains("Stage")),"坏结局根字段");
        com.sirin.hk3gtl.common.util.Hk3LedgerValidation.optionalType(tag,"AttackCount",net.minecraft.nbt.Tag.TAG_INT);
        com.sirin.hk3gtl.common.util.Hk3LedgerValidation.optionalType(tag,"Stage",net.minecraft.nbt.Tag.TAG_INT);
        com.sirin.hk3gtl.common.util.Hk3LedgerValidation.require(tag.getInt("AttackCount")>=0&&tag.getInt("Stage")>=0&&tag.getInt("Stage")<=2,"旧坏结局字段");
        Hk3BadEndingData data = new Hk3BadEndingData();
        data.attackCount = tag.getInt("AttackCount");
        data.stage = tag.getInt("Stage");
        if(tag.contains("Personal")) {
            if(!tag.contains("Personal",net.minecraft.nbt.Tag.TAG_COMPOUND))throw new IllegalStateException("个人坏结局记录损坏");
            var entries=tag.getCompound("Personal");
            for(String id:entries.getAllKeys()) {
                if(!entries.contains(id,net.minecraft.nbt.Tag.TAG_COMPOUND))throw new IllegalStateException("个人坏结局条目无效");
                var n=entries.getCompound(id);int stage=n.getInt("Stage"),count=n.getInt("BadCount"),line=n.getInt("Line");
                if(!n.hasUUID("Meeting")||!n.contains("Stage",3)||!n.contains("BadCount",3)||!n.contains("Line",3)||!n.contains("Returned",1)
                    ||stage<0||stage>2||count<0||line<0||line>9||stage==STAGE_COMPLETED&&line!=9||stage!=STAGE_NONE&&count==0)
                    throw new IllegalStateException("个人坏结局字段无效");
                com.sirin.hk3gtl.common.util.Hk3LedgerValidation.flag(n,"Returned",true);
                data.people.put(com.sirin.hk3gtl.common.util.Hk3LedgerValidation.uuid(id),new Personal(n.getUUID("Meeting"),stage,n.getBoolean("Returned"),count,line));
            }
        }
        return data;
    }

    @Override
    public CompoundTag save(CompoundTag tag) {
        tag.putInt("AttackCount", attackCount);
        tag.putInt("Stage", stage);
        var entries=new CompoundTag();people.forEach((id,p)->{
            var n=new CompoundTag();n.putUUID("Meeting",p.meeting);n.putInt("Stage",p.stage);n.putBoolean("Returned",p.returned);n.putInt("BadCount",p.badCount);n.putInt("Line",p.line);entries.put(id.toString(),n);
        });tag.put("Personal",entries);
        return tag;
    }

    public int getAttackCount() {
        return attackCount;
    }

    /** 累计一次攻击并返回累计值（自动 setDirty）。 */
    public int incrementAttackCount() {
        attackCount++;
        setDirty();
        return attackCount;
    }

    public int getStage() {
        return stage;
    }

    public void setStage(int newStage) {
        if (this.stage != newStage) {
            this.stage = newStage;
            setDirty();
            LOGGER.info("[HK3GTL] 坏结局阶段变更 -> {}", newStage);
        }
    }

    /** 调试用：完全重置坏结局进度。 */
    public void resetForDebug() {
        attackCount = 0;
        stage = STAGE_NONE;
        setDirty();
        LOGGER.info("[HK3GTL] [DEBUG] 坏结局数据已重置。");
    }

    /** 从主世界获取坏结局数据（任意维度的 ServerLevel 均可传入）。 */
    public static Hk3BadEndingData get(ServerLevel level) {
        return com.sirin.hk3gtl.common.util.Hk3SavedDataGuard.get(level.getServer(),DATA_NAME,Hk3BadEndingData::load,Hk3BadEndingData::new);
    }
}
