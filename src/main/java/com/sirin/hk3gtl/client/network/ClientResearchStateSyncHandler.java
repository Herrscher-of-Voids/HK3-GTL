package com.sirin.hk3gtl.client.network;



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
