package com.sirin.hk3gtl.common.machine.multiblock.part;



import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.gregtechceu.gtceu.api.machine.multiblock.part.TieredIOPartMachine;
import com.sirin.hk3gtl.common.block.energy.HonkaiHatchType;
import com.sirin.hk3gtl.common.capability.HonkaiEnergyStorage;
import com.sirin.hk3gtl.common.capability.HonkaiWirelessNetwork;
import com.sirin.hk3gtl.common.capability.IHonkaiEnergyContainer;

import net.minecraft.nbt.CompoundTag;

import javax.annotation.Nullable;
import java.util.UUID;

public class HonkaiEnergyHatchPartMachine extends TieredIOPartMachine {

    private final HonkaiHatchType type;
    private final HonkaiEnergyStorage localStorage;

    @Nullable
    private UUID ownerId;

    public HonkaiEnergyHatchPartMachine(IMachineBlockEntity holder, HonkaiHatchType type, Object... args) {
        // We pass tier 0 and IO based on hatch type.
        super(holder, 0, type.canInsertFromOutside ? IO.IN : IO.OUT);
        this.type = type;

        if (type.creative) {
            this.localStorage = HonkaiEnergyStorage.creative();
        } else if (type.wireless) {
            this.localStorage = new HonkaiEnergyStorage(0, false, false, false);
        } else {
            this.localStorage = new HonkaiEnergyStorage(
                    type.localCapacity,
                    type.canInsertFromOutside,
                    type.canExtractFromOutside,
                    false);
        }
    }

    public HonkaiHatchType getHatchType() {
        return type;
    }

    @Nullable
    public UUID getOwnerId() {
        return ownerId;
    }

    public boolean ensureOwner(UUID playerId) {
        if (!type.wireless) return false;
        if (this.ownerId != null) return false;
        this.ownerId = playerId;
        return true;
    }

    public IHonkaiEnergyContainer getContainer() {
        if (type.wireless) {
            return new WirelessView();
        }
        return localStorage;
    }

    @Override
    public void saveCustomPersistedData(CompoundTag tag, boolean isItem) {
        super.saveCustomPersistedData(tag, isItem);
        tag.putString("type", type.id);
        if (ownerId != null) tag.putUUID("owner", ownerId);
        if (!type.wireless && !type.creative) {
            localStorage.saveNBT(tag);
        }
    }

    @Override
    public void loadCustomPersistedData(CompoundTag tag) {
        super.loadCustomPersistedData(tag);
        if (tag.hasUUID("owner")) this.ownerId = tag.getUUID("owner");
        if (!type.wireless && !type.creative) {
            localStorage.loadNBT(tag);
        }
    }

    private final class WirelessView implements IHonkaiEnergyContainer {
        @Override
        public long getAmount() {
            if (ownerId == null) return 0L;
            var stored = HonkaiWirelessNetwork.getStoredAmount(ownerId);
            return stored.bitLength() > 63 ? Long.MAX_VALUE : stored.longValue();
        }
        @Override
        public long getCapacity() {
            return Long.MAX_VALUE;
        }
        @Override
        public boolean canInsert() {
            return type == HonkaiHatchType.WIRELESS_INPUT;
        }
        @Override
        public boolean canExtract() {
            return type == HonkaiHatchType.WIRELESS_OUTPUT;
        }
        @Override
        public long insert(long request, boolean simulate) {
            if (ownerId == null || type != HonkaiHatchType.WIRELESS_INPUT) return 0;
            return HonkaiWirelessNetwork.insert(ownerId, request, simulate);
        }
        @Override
        public long extract(long request, boolean simulate) {
            if (ownerId == null || type != HonkaiHatchType.WIRELESS_OUTPUT) return 0;
            return HonkaiWirelessNetwork.extract(ownerId, request, simulate);
        }
    }
}
