package com.sirin.hk3gtl.common.easter;

import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.gregtechceu.gtceu.api.machine.trait.NotifiableEnergyContainer;
import com.sirin.hk3gtl.common.campus.Hk3CampusCatalog;
import com.sirin.hk3gtl.common.narrative.Hk3NarrativeLog;
import com.sirin.hk3gtl.common.research.Hk3ResearchBatchProofs;
import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;

import java.util.Collections;
import java.util.IdentityHashMap;
import java.util.UUID;

public final class Hk3EggEngineering {
    public static final String PREFIX = "context:formed:";

    private Hk3EggEngineering() {}

    public static void formed(MetaMachine machine, UUID owner) {
        if (owner == null || !(machine.getLevel() instanceof ServerLevel level)) return;
        var data = Hk3EggProductionData.get(level.getServer());
        String key = PREFIX + machine.getDefinition().getId();
        if (data.count(owner, key) == 0) data.produced(owner, key, 1);
    }

    public static void poll(ServerPlayer player) {
        var data = Hk3EggProductionData.get(player.server);
        var counts = data.counts(player.getUUID());
        if (!Hk3NarrativeLog.isUnlocked(player, "E-EG-045") && Hk3CampusCatalog.entries().stream()
                .allMatch(entry -> counts.getOrDefault(PREFIX + entry.machineId(), 0L) > 0))
            Hk3EggVanilla.caseEvent(player, 45);
        if (!Hk3NarrativeLog.isUnlocked(player, "E-EG-044")) {
            var research = Hk3ResearchData.get(player.server);
            var team = research.scope(player.getUUID());
            if (java.util.stream.IntStream.rangeClosed(1, 15).allMatch(index -> Hk3ResearchBatchProofs.valid(
                    research.processFactReceipt(team, index == 15 ? "wonder_application"
                            : String.format(java.util.Locale.ROOT, "wonder_W%02d", index)))))
                Hk3EggVanilla.caseEvent(player, 44);
        }
        if (!Hk3NarrativeLog.isUnlocked(player, "E-EG-035")) reserve(player);
    }

    private static void reserve(ServerPlayer player) {
        var source = player.serverLevel().getChunkSource();
        var center = player.chunkPosition();
        var seen = Collections.newSetFromMap(new IdentityHashMap<NotifiableEnergyContainer, Boolean>());
        long total = 0;
        for (int x = center.x - 4; x <= center.x + 4; x++) for (int z = center.z - 4; z <= center.z + 4; z++) {
            var chunk = source.getChunkNow(x, z);
            if (chunk == null) continue;
            for (var block : chunk.getBlockEntities().values()) {
                if (block.isRemoved() || block.getBlockPos().distToCenterSqr(player.position()) > 4096
                        || !(block instanceof IMachineBlockEntity holder)) continue;
                var machine = holder.getMetaMachine();
                if (machine.isInValid() || machine.getDefinition().getId().getPath().contains("creative")) continue;
                for (var trait : machine.getTraits()) if (trait instanceof NotifiableEnergyContainer energy && seen.add(energy)) {
                    total += Math.min(1_000_000 - total, energy.getEnergyStored());
                    if (total >= 1_000_000) {
                        Hk3EggVanilla.caseEvent(player, 35);
                        return;
                    }
                }
            }
        }
    }
}
