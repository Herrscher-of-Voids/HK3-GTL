package com.sirin.hk3gtl.mixin.ae;

import appeng.api.storage.MEStorage;
import appeng.me.storage.NetworkStorage;
import com.sirin.hk3gtl.common.integration.ae.nexus.network.Hk3NexusStock;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

import java.util.List;
import java.util.NavigableMap;

@Mixin(value = NetworkStorage.class, remap = false)
public interface Hk3NexusStorageAccess extends Hk3NexusStock.Mounts {
    @Override @Accessor("priorityInventory")
    NavigableMap<Integer, List<MEStorage>> hk3gtl$mountedInventories();
}
