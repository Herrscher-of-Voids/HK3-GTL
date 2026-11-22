package com.sirin.hk3gtl.mixin;

import net.minecraft.world.level.storage.DimensionDataStorage;
import java.io.File;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;

@Mixin(DimensionDataStorage.class)
public interface Hk3DimensionDataStorageAccess {
    @Invoker("getDataFile") File hk3gtl$getDataFile(String name);
}
