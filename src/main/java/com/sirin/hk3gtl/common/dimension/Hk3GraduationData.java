package com.sirin.hk3gtl.common.dimension;


/**
 * 【文件职责】
 * - 维护 Hk3GraduationData 的核心功能实现。
 * - 关键调用链：由上层系统入口调用 -> 本文件核心方法 -> 下游模块。
 *
 * 【变更记录】2026-05-19
 * - 删除：
 *   1) 初始归档备注：自 v0.3 基线梳理，无本次 diff。
 * - 新增：
 *   1) 新增统一变更备注块，便于后续维护与审计追踪。
 * - 修改：
 *   1) 未改动业务逻辑，仅补充文件级职责与维护注释模板。
 * - 用途：
 *   1) 帮助维护者快速理解文件职责、变更背景与风险点。
 *
 * 【段内说明】
 * - 复杂方法补充“干什么 / 边界 / 线程侧”精简中文注释。
 */
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

/**
 * 世界级持久化数据 —— 记录终局审判（毕业）是否已完成。
 *
 * <h3>职责</h3>
 * 使用 Minecraft WorldSavedData 机制，将毕业状态持久化到主世界存档中。
 * 当前以玩家UUID保存通过记录；旧全服标记只保留历史。
 *
 * <h3>存储位置</h3>
 * 主世界 data 目录下的 "hk3gtl_graduation.dat" 文件。
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增持久化字段：在 save/load 中添加 NBT 读写，并在类中添加对应字段</li>
 *   <li>查询毕业状态：通过 Hk3GraduationData.get(level).isGraduated()</li>
 *   <li>标记毕业：调用 markGraduated()，会自动 setDirty 触发存盘</li>
 *   <li>调试重置：调用 resetForDebug()（仅供 /hk3debug 使用）</li>
 * </ul>
 */
/** 【变更记录 #1】2026-09-30 23:34:26（修订119）：删除：世界级结果对所有玩家的隐式授权；新增/修改：UUID通过集合、幂等个人通过与个人调试重置，旧世界标记不自动迁移给全队；用途：个人结算不覆盖其他玩家，未完成的资格采集仍单独接入。 */
/** 【变更记录 #2】2026-10-01 17:04:49（修订136）：删除结局账本加载失败后创建空账本的入口；新增根标记与个人UUID严格校验；修改统一使用防覆盖读取，旧世界标记仍只保留历史；用途：避免损坏后正常通过历史被清空或奖励重复结算。 */
public class Hk3GraduationData extends SavedData {

    private static final Logger LOGGER = LogUtils.getLogger();
    /** SavedData 存储键名，对应磁盘文件 hk3gtl_graduation.dat */
    private static final String DATA_NAME = "hk3gtl_graduation";

    /** 毕业状态标记：true 表示终局对话已完成 */
    private boolean graduated = false;
    /** 旧世界标记仅保留历史，不再推断任意玩家已经通过；新结算以UUID为准。 */
    private final java.util.Set<java.util.UUID> passedPlayers = new java.util.HashSet<>();
    public boolean isGraduated(java.util.UUID player) { return passedPlayers.contains(player); }
    public boolean markGraduated(java.util.UUID player) {
        if (!passedPlayers.add(java.util.Objects.requireNonNull(player))) return false;
        setDirty(); return true;
    }
    public void resetForDebug(java.util.UUID player) { if (passedPlayers.remove(player)) setDirty(); }


    public Hk3GraduationData() {}

    /** 从 NBT 反序列化毕业数据 */
    public static Hk3GraduationData load(CompoundTag tag) {
        com.sirin.hk3gtl.common.util.Hk3LedgerValidation.require(tag.contains("Graduated")||tag.contains("PassedPlayers"),"结局根字段");
        com.sirin.hk3gtl.common.util.Hk3LedgerValidation.flag(tag,"Graduated",false);
        Hk3GraduationData data = new Hk3GraduationData();
        data.graduated = tag.getBoolean("Graduated");
        if (tag.contains("PassedPlayers")) {
            if (!tag.contains("PassedPlayers", net.minecraft.nbt.Tag.TAG_COMPOUND)) throw new IllegalStateException("个人终局记录损坏");
            var entries=tag.getCompound("PassedPlayers");
            for (String id:entries.getAllKeys()) {
                com.sirin.hk3gtl.common.util.Hk3LedgerValidation.flag(entries,id,true);
                if (!entries.getBoolean(id)) throw new IllegalStateException("个人终局结果无效");
                data.passedPlayers.add(com.sirin.hk3gtl.common.util.Hk3LedgerValidation.uuid(id));
            }
        }
        return data;
    }

    /** 序列化毕业数据到 NBT */
    @Override
    public CompoundTag save(CompoundTag tag) {
        tag.putBoolean("Graduated", graduated);
        var entries=new CompoundTag();
        passedPlayers.forEach(id->entries.putBoolean(id.toString(),true));
        tag.put("PassedPlayers",entries);
        return tag;
    }

    /** 仅供旧数据归档读取，生产流程必须使用UUID重载。 */
    @Deprecated
    public boolean isGraduated() {
        return graduated;
    }

    public void markGraduated() {
        if (!graduated) {
            graduated = true;
            setDirty();
            LOGGER.info("[HK3GTL] 文明审判已通过，世界标记毕业完成。");
        }
    }

    /** 调试用：清除毕业标记 */
    public void resetForDebug() {
        graduated = false;
        setDirty();
        LOGGER.info("[HK3GTL] [DEBUG] 毕业标记已重置。");
    }

    /** 从主世界获取毕业数据 */
    public static Hk3GraduationData get(ServerLevel level) {
        return com.sirin.hk3gtl.common.util.Hk3SavedDataGuard.get(level.getServer(),DATA_NAME,Hk3GraduationData::load,Hk3GraduationData::new);
    }
}
