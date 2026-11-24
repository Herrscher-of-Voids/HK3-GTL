package com.sirin.hk3gtl.common.integration.ae.nexus.crafting;

import appeng.api.networking.crafting.CalculationStrategy;
import appeng.api.stacks.AEKey;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.contents.TranslatableContents;

import java.math.BigInteger;

public final class Hk3NexusNativeMenus {
    public static final String CPU_NAME = "gui.hk3gtl.nexus.cpu";

    private Hk3NexusNativeMenus() {}

    public static boolean isNexusCpu(Component name) {
        return name != null && name.getContents() instanceof TranslatableContents text
                && text.getKey().equals(CPU_NAME);
    }

    public interface Amount {
        String hk3gtl$initialAmount();
        void hk3gtl$initialAmount(String amount);
        void hk3gtl$confirmAmount(BigInteger amount, boolean missing, boolean immediate);
    }

    public interface Confirm {
        void hk3gtl$planAmount(AEKey target, BigInteger amount, CalculationStrategy strategy);
        String hk3gtl$probabilityHint();
        void hk3gtl$startProbability(String attempts);
    }
}
