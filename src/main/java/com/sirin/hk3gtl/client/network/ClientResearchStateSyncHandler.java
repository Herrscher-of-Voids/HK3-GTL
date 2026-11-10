package com.sirin.hk3gtl.client.network;

/**
 * 【文件职责】
 * - 在物理客户端应用服务端同步的研究、事件与叙事状态。
 * - 关键调用链：ResearchStateSyncS2CPacket.handle -> DistExecutor -> apply -> LocalPlayer.persistentData。
 *
 * 【变更记录 #1】2026-07-19 21:49:23（第 1 次备注 · revision 35）
 * - 删除：
 *   1) 无。本文件为客户端类引用隔离而新增。
 * - 新增：
 *   1) 新增客户端研究状态覆盖入口，清除旧 hk3gtl 研究/事件键后写入服务端权威 NBT。
 * - 修改：
 *   1) 将原 ResearchStateSyncS2CPacket 内的 Minecraft 与 LocalPlayer 调用迁移到 client.network 包。
 * - 用途：
 *   1) 避免 common 数据包直接导入客户端类，同时保持 S2C 同步行为不变。
 */

import com.sirin.hk3gtl.common.constants.Hk3Constants;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.nbt.CompoundTag;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public final class ClientResearchStateSyncHandler {

    private ClientResearchStateSyncHandler() {}

    public static void apply(CompoundTag syncedTag) {
        Minecraft minecraft = Minecraft.getInstance();
        minecraft.execute(() -> {
            LocalPlayer player = minecraft.player;
            if (player == null) return;

            CompoundTag playerData = player.getPersistentData();
            for (String key : java.util.List.copyOf(playerData.getAllKeys())) {
                if (isSynchronizedKey(key)) {
                    playerData.remove(key);
                }
            }

            for (String key : syncedTag.getAllKeys()) {
                if (syncedTag.get(key) != null) {
                    playerData.put(key, syncedTag.get(key).copy());
                }
            }
        });
    }

    private static boolean isSynchronizedKey(String key) {
        return key.startsWith(Hk3Constants.MOD_ID + "_res_")
                || key.startsWith(Hk3Constants.MOD_ID + "_evt_")
                || key.startsWith("hk3gtl_nar_")
                || "hk3gtl_research_matrix".equals(key)
                || "hk3gtl_res_selected".equals(key)
                || "hk3gtl_gaze_level".equals(key)
                || "hk3gtl_civ_level".equals(key)
                || "hk3gtl_voltage_tier".equals(key);
    }
}
