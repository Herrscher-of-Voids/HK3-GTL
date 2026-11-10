package com.sirin.hk3gtl.common.multiblock.build;

import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import net.minecraft.core.Direction;

/** 分批实读与具体机器的成型状态分离，不以建造计数授予成型。 */
public interface Hk3IntegrityHost {
    MultiblockControllerMachine integrityController();
    void integrityFailed(String reason);
    void integrityPassed(Direction facing);
    default void acceptVerifiedPlan(Hk3BuildPlan plan) {}
    default boolean captureFarView() { return true; }
}
