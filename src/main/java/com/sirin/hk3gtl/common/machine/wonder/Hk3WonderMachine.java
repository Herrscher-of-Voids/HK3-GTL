package com.sirin.hk3gtl.common.machine.wonder;

import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.lowdragmc.lowdraglib.syncdata.annotation.Persisted;
import com.lowdragmc.lowdraglib.syncdata.field.ManagedFieldHolder;
import com.sirin.hk3gtl.common.machine.Hk3CommissionMachine;
import com.sirin.hk3gtl.common.research.Hk3W13ResearchService;
import java.util.UUID;

public class Hk3WonderMachine extends Hk3CommissionMachine implements Hk3W13ResearchService.Source {
    protected static final ManagedFieldHolder FIELDS = new ManagedFieldHolder(Hk3WonderMachine.class, HK3_MANAGED_FIELD_HOLDER);
    @Persisted private UUID serviceId = UUID.randomUUID();
    public Hk3WonderMachine(IMachineBlockEntity holder, String role) { super(holder, role); }
    @Override public ManagedFieldHolder getFieldHolder() { return FIELDS; }
    @Override protected String commissionTitle() { return researchRole() + " · " + Hk3WonderCatalog.get(researchRole()).title(); }
    @Override public UUID researchServiceId() { return serviceId; }
    @Override public boolean researchServiceRunning() { return verified() && isFormed() && getRecipeLogic().isActive(); }
    @Override public void onLoad() {
        super.onLoad();
        if (!isRemote() && researchRole().equals("W13")) Hk3W13ResearchService.loaded(this);
    }
    @Override public void onUnload() {
        if (!isRemote() && researchRole().equals("W13")) Hk3W13ResearchService.unloaded(this);
        super.onUnload();
    }
}
