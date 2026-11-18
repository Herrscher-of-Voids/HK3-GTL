package com.sirin.hk3gtl.common.event;

import com.sirin.hk3gtl.common.constants.Hk3Constants;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * 
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
 */
@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
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
