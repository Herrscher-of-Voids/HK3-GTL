package com.sirin.hk3gtl.common.easter;

import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.sirin.hk3gtl.common.item.main.Hk3MainMaterialItems;
import com.sirin.hk3gtl.common.recipe.main.Hk3MainMaterialAccess;
import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;

import java.util.UUID;

public final class Hk3EggVoltageProgress {
    public static final String PREFIX = "industrial_voltage:";

    private Hk3EggVoltageProgress() {}

    public static void produced(MinecraftServer server, UUID owner, GTRecipe recipe, ItemStack output) {
        if (!recipe.id.getNamespace().equals("hk3gtl") || !recipe.id.getPath().startsWith("main_material/")) return;
        int tier = recipe.data.getInt("hk3_material_product_tier");
        if (!output.is(Hk3MainMaterialItems.stack(tier, "billet", 1).getItem())) return;
        var research = Hk3ResearchData.get(server);
        var scope = research.scope(owner);
        if (Hk3MainMaterialAccess.requirements(tier, tier).stream().allMatch(id -> research.completed(scope, id)))
            Hk3EggProductionData.get(server).produced(owner, PREFIX + tier, 1);
    }

    public static boolean unlocked(ServerPlayer player, int tier) {
        return Hk3EggProductionData.get(player.server).count(player.getUUID(), PREFIX + tier) > 0;
    }

    public static void poll(ServerPlayer player) {
        var counts = Hk3EggProductionData.get(player.server).counts(player.getUUID());
        if (counts.getOrDefault(PREFIX + 19, 0L) > 0) Hk3EggVanilla.caseEvent(player, 11);
        for (int group = 0; group < 4; group++) {
            int first = 15 + group * 4;
            if (java.util.stream.IntStream.range(first, first + 4).allMatch(tier -> counts.getOrDefault(PREFIX + tier, 0L) > 0))
                Hk3EggVanilla.caseEvent(player, 40 + group);
        }
        if (java.util.stream.IntStream.rangeClosed(15, 30).allMatch(tier -> counts.getOrDefault(PREFIX + tier, 0L) > 0))
            Hk3EggVanilla.caseEvent(player, 28);
    }
}
