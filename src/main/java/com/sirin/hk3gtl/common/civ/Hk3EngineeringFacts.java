package com.sirin.hk3gtl.common.civ;

import com.sirin.hk3gtl.common.machine.wonder.Hk3WonderProductionMachine;
import com.sirin.hk3gtl.common.research.Hk3ResearchBatchProofs;
import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.MinecraftServer;

import java.util.UUID;

public final class Hk3EngineeringFacts {
    private Hk3EngineeringFacts() {}
    public static CompoundTag receipt(MinecraftServer server, Hk3ResearchData research, UUID team, String role) {
        String fact = role.equals("H01") ? "hyperion_engineering" : role.equals("application") ? "wonder_application" : "wonder_" + role;
        var receipt = research.processFactReceipt(team, fact);
        String machineRole = role.equals("application") ? "W15" : role;
        return Hk3ResearchBatchProofs.valid(receipt)
                && Hk3WonderProductionMachine.formed(server, team, machineRole, receipt.getString("Facility"))
                ? receipt : new CompoundTag();
    }
}
