package com.sirin.hk3gtl.common.machine.w02;

import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.sirin.hk3gtl.common.machine.Hk3CommissionMachine;

/** 普通理之律者19C A2实体船坞，保持全静态。 */
public final class Hk3W02Machine extends Hk3CommissionMachine {
    public Hk3W02Machine(IMachineBlockEntity holder){super(holder,"W02");}
    @Override protected String commissionTitle(){return "W02 · 万象·自律工业矩阵";}
}
