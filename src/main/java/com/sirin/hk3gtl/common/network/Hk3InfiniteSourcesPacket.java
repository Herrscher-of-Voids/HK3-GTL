package com.sirin.hk3gtl.common.network;

import appeng.api.stacks.AEKey;
import appeng.client.gui.me.common.Repo;
import appeng.menu.me.common.MEStorageMenu;
import com.sirin.hk3gtl.common.integration.ae.Hk3InfiniteSourceMenu;
import net.minecraft.client.Minecraft;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;

import java.util.HashSet;
import java.util.Set;
import java.util.function.Supplier;

public record Hk3InfiniteSourcesPacket(int menuId, Set<AEKey> keys) {
    public static void encode(Hk3InfiniteSourcesPacket packet, FriendlyByteBuf buffer) {
        buffer.writeVarInt(packet.menuId);
        buffer.writeCollection(packet.keys, AEKey::writeKey);
    }

    public static Hk3InfiniteSourcesPacket decode(FriendlyByteBuf buffer) {
        return new Hk3InfiniteSourcesPacket(buffer.readVarInt(),
                Set.copyOf(buffer.readCollection(HashSet::new, AEKey::readKey)));
    }

    public static void handle(Hk3InfiniteSourcesPacket packet, Supplier<NetworkEvent.Context> supplier) {
        var context = supplier.get();
        context.enqueueWork(() -> DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () -> receive(packet)));
        context.setPacketHandled(true);
    }

    private static void receive(Hk3InfiniteSourcesPacket packet) {
        var player = Minecraft.getInstance().player;
        if (player != null && player.containerMenu.containerId == packet.menuId
                && player.containerMenu instanceof MEStorageMenu menu) {
            ((Hk3InfiniteSourceMenu) menu).hk3gtl$setInfiniteSources(packet.keys);
            if (menu.getClientRepo() instanceof Repo repo) repo.updateView();
        }
    }
}
