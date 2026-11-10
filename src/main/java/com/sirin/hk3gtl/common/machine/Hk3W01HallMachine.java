package com.sirin.hk3gtl.common.machine;

import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import net.minecraft.server.level.ServerLevel;

/** Azu礼堂完整原形；分批实读核验后允许启停创造调试。 */
public final class Hk3W01HallMachine extends Hk3CommissionMachine {
    private boolean terminalBuilding;
    public Hk3W01HallMachine(IMachineBlockEntity holder){super(holder);}
    @Override protected String commissionTitle(){return "W01 · 始源·群星协奏庭";}
    public boolean isTerminalBuilding(){return terminalBuilding;}
    public void setTerminalBuilding(boolean building){terminalBuilding=building;onStructureInvalid();}
    /** 远端区块卸载不代表实体拆除；控制器卸载仍撤销证据。 */
    public static void onBuildingChunkUnload(ServerLevel level,long chunk){}
}
