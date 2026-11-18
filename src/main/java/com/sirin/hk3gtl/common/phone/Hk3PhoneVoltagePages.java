package com.sirin.hk3gtl.common.phone;

import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.easter.Hk3EggPhone;
import com.sirin.hk3gtl.common.easter.Hk3EggRuntime;
import com.sirin.hk3gtl.common.easter.Hk3EggVanilla;
import com.sirin.hk3gtl.common.easter.Hk3EggVoltageProgress;
import com.sirin.hk3gtl.common.easter.Hk3ReadingSessions;
import com.sirin.hk3gtl.common.material.main.Hk3MainMaterialCatalog;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.server.level.ServerPlayer;

public final class Hk3PhoneVoltagePages {
    private static final String PREFIX = "voltage_page_";

    private Hk3PhoneVoltagePages() {}

    public static boolean managed(String id) { return id.startsWith(PREFIX); }

    public static boolean authorize(ServerPlayer player, String id) {
        var state = Hk3EggRuntime.state(player);
        return Hk3PhoneData.get(player).installed(player.getUUID()) && Hk3PhoneRuntime.powered(player)
                && state.getBoolean("phoneOpen") && state.getString("phoneMode").equals("voltage_read")
                && state.getString("voltagePage").equals(id)
                && Hk3EggVoltageProgress.unlocked(player, Integer.parseInt(id.substring(PREFIX.length())));
    }

    public static int index(ServerPlayer player) {
        if (!Hk3PhoneData.get(player).installed(player.getUUID()) || !Hk3PhoneRuntime.requirePower(player)) return 0;
        Hk3EggPhone.opened(player, "voltage_catalog");
        var view = new CompoundTag();
        view.putString("Mode", "voltage_catalog");
        var rows = new ListTag();
        for (int tier = 15; tier <= 30; tier++) {
            var row = new CompoundTag();
            row.putInt("Tier", tier);
            row.putString("Title", Hk3Values.getVN(tier) + " · " + (player.getLanguage().startsWith("zh")
                    ? Hk3Tiers.VOLTAGE_NAMES_ZH[tier - 15] : Hk3Tiers.VOLTAGE_NAMES_EN[tier - 15]));
            row.putBoolean("Unlocked", Hk3EggVoltageProgress.unlocked(player, tier));
            rows.add(row);
        }
        view.put("Rows", rows);
        Hk3PhoneService.send(player, view);
        return 1;
    }

    public static int open(ServerPlayer player, int tier) {
        if (!Hk3PhoneData.get(player).installed(player.getUUID()) || !Hk3PhoneRuntime.requirePower(player)
                || !Hk3EggVoltageProgress.unlocked(player, tier)) return 0;
        Hk3EggPhone.opened(player, "voltage_read");
        String id = PREFIX + tier;
        Hk3EggRuntime.state(player).putString("voltagePage", id);
        var material = Hk3MainMaterialCatalog.entry(tier);
        var view = new CompoundTag();
        view.putString("Mode", "instruction_read");
        view.putString("Id", id);
        view.putBoolean("VoltagePage", true);
        view.putString("Title", Hk3Values.getVN(tier) + " · " + (player.getLanguage().startsWith("zh")
                ? Hk3Tiers.VOLTAGE_NAMES_ZH[tier - 15] : Hk3Tiers.VOLTAGE_NAMES_EN[tier - 15]));
        view.putString("Body", Hk3PhoneInstructionPages.text(player, "voltage.body", Hk3Values.getVN(tier),
                Hk3Values.getVA(tier), player.getLanguage().startsWith("zh") ? material.nameZh() : material.nameEn()));
        Hk3PhoneService.send(player, view);
        return 1;
    }

    public static void completed(ServerPlayer player, Hk3ReadingSessions.Session session) {
        if (authorize(player, session.id()))
            Hk3EggVanilla.caseEvent(player, 141 + Integer.parseInt(session.id().substring(PREFIX.length())) - 15);
    }
}
