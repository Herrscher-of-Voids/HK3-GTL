package com.sirin.hk3gtl.common.event;

import com.sirin.hk3gtl.common.constants.Hk3Constants;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * 【文件职责】
 * - 在玩家实体被重建（死亡重生 / 末地返回）时，迁移本模组写在
 *   {@code Player#getPersistentData()} 根级的全部 {@code hk3gtl_} 状态键。
 * - 关键调用链：Forge FORGE 总线 {@link PlayerEvent.Clone} -> 本处理器 -> 复制旧实体 persistentData 到新实体。
 *
 * 【文件背景】
 * - 研究(hk3gtl_res_*)、事件(hk3gtl_evt_*)、叙事(hk3gtl_nar_*)、注视度(hk3gtl_gaze_level)、
 *   文明等级(hk3gtl_civ_level)、电压层(hk3gtl_voltage_tier)、对话完成(hk3gtl_dialogue_done)、
 *   坏结局回城(hk3gtl_be_respawned)、失败计数(hk3gtl_total_fails/unlucky_egg)、欢迎版本
 *   (hk3gtl_seen_welcome_version) 等均写在 persistentData 根级。
 * - Forge 只会在死亡/重生时自动复制 {@code PlayerPersisted} 子标签，根级自定义键不会自动带过去，
 *   因此不迁移就会导致玩家死亡后研究/事件/终局进度与一次性防重标记丢失，造成重复奖励或流程回退。
 *
 * 【变更记录 #1】2026-07-21 10:00:00（第 1 次备注 · 修复 V3 报告 R-02/P0-2）
 * - 删除：无。
 * - 新增：
 *   1) 订阅 {@link PlayerEvent.Clone}，把旧实体 persistentData 中所有以 {@code hk3gtl_} 开头的键
 *      深拷贝到新实体，覆盖死亡重生与末地返回两种重建场景。
 *   2) 前缀白名单迁移：只复制本模组命名空间键，不触碰其他模组或原版数据。
 * - 修改：无（新增独立处理器，不改动既有事件类）。
 * - 用途：
 *   1) 保证玩家死亡/末地返回后 hk3gtl_ 进度与一次性标记不丢失，堵住 persistentData 死亡迁移缺口。
 *   2) 关键风险点：必须在服务端主线程执行；只做 NBT 深拷贝，无跨线程共享。
 */
@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
/** 【变更记录 #2】2026-10-01 01:54:14（修订127）：删除：被替代的旧分支；新增/修改：保留命名空间深拷贝，抽出重生迁移方法供存档隔离回归；用途：个人收藏与正式资格分离，保留历史记录。 */
public final class Hk3PlayerDataCloneHandler {

    /** 需要跨实体重建迁移的本模组 persistentData 键前缀。 */
    private static final String HK3_PREFIX = "hk3gtl_";

    private Hk3PlayerDataCloneHandler() {}

    /**
     * 玩家实体重建时迁移本模组进度。
     * 边界：死亡重生与末地返回均会触发本事件；两种情况都需要保留 hk3gtl_ 进度。
     * 安全点：仅复制 hk3gtl_ 前缀键并深拷贝，避免与旧实体共享同一 NBT 引用。
     */
    @SubscribeEvent
    public static void onClone(PlayerEvent.Clone event) {
        CompoundTag oldData = event.getOriginal().getPersistentData();
        CompoundTag newData = event.getEntity().getPersistentData();

        copyPersistentState(oldData,newData);
    }

    public static void copyPersistentState(CompoundTag oldData,CompoundTag newData) {
        for (String key : oldData.getAllKeys()) {
            if (!key.startsWith(HK3_PREFIX)) {
                continue;
            }
            Tag value = oldData.get(key);
            if (value != null) {
                newData.put(key, value.copy());
            }
        }
    }
}
