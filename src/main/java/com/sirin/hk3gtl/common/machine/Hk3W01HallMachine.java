package com.sirin.hk3gtl.common.machine;

import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;

public final class Hk3W01HallMachine extends Hk3CommissionMachine {
    private boolean terminalBuilding;
    public Hk3W01HallMachine(IMachineBlockEntity holder){super(holder,"W01");}
    @Override protected String commissionTitle(){return "W01 · 始源·群星协奏庭";}
    public boolean isTerminalBuilding(){return terminalBuilding;}
    public void setTerminalBuilding(boolean building){terminalBuilding=building;if(building)onStructureInvalid();}
}
