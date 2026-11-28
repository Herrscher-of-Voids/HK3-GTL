package com.sirin.hk3gtl.common.civ;

import com.sirin.hk3gtl.common.machine.wonder.Hk3WonderProductionMachine;
import com.sirin.hk3gtl.common.research.Hk3ResearchBatchProofs;
import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import java.util.regex.Pattern;
import net.minecraft.server.MinecraftServer;

import java.util.UUID;

public final class Hk3EngineeringFacts {
    private static final Pattern FACILITY = Pattern.compile("([^@]+)@(?:BlockPos|Vec3i)\\{x=(-?\\d+), y=(-?\\d+), z=(-?\\d+)\\}");
    private Hk3EngineeringFacts() {}

    public static CompoundTag accepted(MinecraftServer server, Hk3ResearchData research, UUID team, String role) {
        var proof = research.processFactReceipt(team, fact(role));
        if (!Hk3ResearchBatchProofs.valid(proof)) return new CompoundTag();
        var location = FACILITY.matcher(proof.getString("Facility"));
        if (location.matches()) {
            var level = server.getLevel(ResourceKey.create(Registries.DIMENSION, new ResourceLocation(location.group(1))));
            if (level == null) return new CompoundTag();
            int x = Integer.parseInt(location.group(2)), z = Integer.parseInt(location.group(4));
            if (level.getChunkSource().getChunkNow(x >> 4, z >> 4) == null) return proof;
        }
        return current(server, team, role, proof) ? proof : new CompoundTag();
    }

    private static String fact(String role) {
        return role.equals("H01") ? "hyperion_engineering" : role.equals("application") ? "wonder_application" : "wonder_" + role;
    }
    public static CompoundTag receipt(MinecraftServer server, Hk3ResearchData research, UUID team, String role) {
        var receipt = research.processFactReceipt(team, fact(role));
        return Hk3ResearchBatchProofs.valid(receipt) && current(server, team, role, receipt)
                ? receipt : new CompoundTag();
    }

    private static boolean current(MinecraftServer server, UUID team, String role, CompoundTag receipt) {
        String machineRole = role.equals("application") ? "W15" : role;
        return Hk3WonderProductionMachine.formed(server, team, machineRole, receipt.getString("Facility"));
    }
}
