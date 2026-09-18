package com.sirin.hk3gtl.common.dimension;



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
 * 全服共享一个毕业标记，而非按玩家存储。
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
public class Hk3GraduationData extends SavedData {

    private static final Logger LOGGER = LogUtils.getLogger();
    /** SavedData 存储键名，对应磁盘文件 hk3gtl_graduation.dat */
    private static final String DATA_NAME = "hk3gtl_graduation";

    /** 毕业状态标记：true 表示终局对话已完成 */
    private boolean graduated = false;

    public Hk3GraduationData() {}

    /** 从 NBT 反序列化毕业数据 */
    public static Hk3GraduationData load(CompoundTag tag) {
        Hk3GraduationData data = new Hk3GraduationData();
        data.graduated = tag.getBoolean("Graduated");
        return data;
    }

    /** 序列化毕业数据到 NBT */
    @Override
    public CompoundTag save(CompoundTag tag) {
        tag.putBoolean("Graduated", graduated);
        return tag;
    }

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
        ServerLevel overworld = level.getServer().overworld();
        return overworld.getDataStorage()
                .computeIfAbsent(Hk3GraduationData::load, Hk3GraduationData::new, DATA_NAME);
    }
}
