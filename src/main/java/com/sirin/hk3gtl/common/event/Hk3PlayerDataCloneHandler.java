package com.sirin.hk3gtl.common.event;

import com.sirin.hk3gtl.common.constants.Hk3Constants;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;


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
