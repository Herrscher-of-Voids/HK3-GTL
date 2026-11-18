package com.sirin.hk3gtl.mixin.ae;

import appeng.api.stacks.AEKey;
import appeng.api.stacks.KeyCounter;
import appeng.api.storage.MEStorage;
import appeng.menu.me.common.MEStorageMenu;
import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.sirin.hk3gtl.common.integration.ae.Hk3InfiniteSourceMenu;
import com.sirin.hk3gtl.common.integration.ae.Hk3InfiniteSources;
import com.sirin.hk3gtl.common.network.Hk3InfiniteSourcesPacket;
import com.sirin.hk3gtl.common.network.Hk3Network;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.PacketDistributor;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;

import java.util.HashSet;
import java.util.Set;

@Mixin(value = MEStorageMenu.class, remap = false)
public abstract class Hk3InfiniteSourceMenuMixin implements Hk3InfiniteSourceMenu {
    @Unique private Set<AEKey> hk3gtl$infiniteSources = Set.of();
    @Unique private boolean hk3gtl$sentInfiniteSources;

    @Override
    public Set<AEKey> hk3gtl$infiniteSources() {
        return hk3gtl$infiniteSources;
    }

    @Override
    public void hk3gtl$setInfiniteSources(Set<AEKey> keys) {
        hk3gtl$infiniteSources = keys;
    }

    @WrapOperation(method = "broadcastChanges", remap = true, at = @At(value = "INVOKE", remap = false,
            target = "Lappeng/api/storage/MEStorage;getAvailableStacks()Lappeng/api/stacks/KeyCounter;"))
    private KeyCounter hk3gtl$syncInfiniteSources(MEStorage storage, Operation<KeyCounter> original) {
        var available = original.call(storage);
        var menu = (MEStorageMenu) (Object) this;
        var keys = new HashSet<>(Hk3InfiniteSources.collect(storage, menu.getActionSource()));
        keys.removeIf(key -> !menu.isKeyVisible(key));
        if (!hk3gtl$sentInfiniteSources || !keys.equals(hk3gtl$infiniteSources)) {
            hk3gtl$infiniteSources = Set.copyOf(keys);
            hk3gtl$sentInfiniteSources = true;
            Hk3Network.CHANNEL.send(PacketDistributor.PLAYER.with(() -> (ServerPlayer) menu.getPlayer()),
                    new Hk3InfiniteSourcesPacket(menu.containerId, hk3gtl$infiniteSources));
        }
        return available;
    }
}
