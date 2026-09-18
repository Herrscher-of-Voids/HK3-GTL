package com.sirin.hk3gtl.common.badending;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

/**
 * 坏结局世界级持久化数据 —— 记录玩家对西琳的累计左键攻击次数与坏结局阶段。
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

    public Hk3BadEndingData() {}

    public static Hk3BadEndingData load(CompoundTag tag) {
        Hk3BadEndingData data = new Hk3BadEndingData();
        data.attackCount = tag.getInt("AttackCount");
        data.stage = tag.getInt("Stage");
        return data;
    }

    @Override
    public CompoundTag save(CompoundTag tag) {
        tag.putInt("AttackCount", attackCount);
        tag.putInt("Stage", stage);
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
        ServerLevel overworld = level.getServer().overworld();
        return overworld.getDataStorage()
                .computeIfAbsent(Hk3BadEndingData::load, Hk3BadEndingData::new, DATA_NAME);
    }
}
