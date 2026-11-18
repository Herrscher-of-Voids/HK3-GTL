package com.sirin.hk3gtl.common.network;

 

 





import com.sirin.hk3gtl.client.communication.Hk3LetterScreen;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;
import java.util.function.Supplier;

public record Hk3LetterOpenPacket(int document, String state, net.minecraft.nbt.CompoundTag context) {
    /** 文档号0..2，状态名最多16字符；超界直接拒绝，防止任意资源访问。 / Bound document IDs to 0..2 and state names to 16 chars. */
    public Hk3LetterOpenPacket {
        context=context.copy();
        if (document < 0 || document > 5 || state.length() > 16) throw new IllegalArgumentException("Invalid letter packet");
    }
    public static void encode(Hk3LetterOpenPacket packet, FriendlyByteBuf buffer) {
        buffer.writeVarInt(packet.document); buffer.writeUtf(packet.state, 16); buffer.writeNbt(packet.context);
    }
    /** 解码同一协议边界，构造器再次校验。 / Decode using identical bounds and constructor validation. */
    public static Hk3LetterOpenPacket decode(FriendlyByteBuf buffer) {
        return new Hk3LetterOpenPacket(buffer.readVarInt(), buffer.readUtf(16), java.util.Objects.requireNonNull(buffer.readNbt()));
    }
    public static void handle(Hk3LetterOpenPacket packet, Supplier<NetworkEvent.Context> supplier) {
        NetworkEvent.Context context = supplier.get();
        context.enqueueWork(() -> DistExecutor.unsafeRunWhenOn(Dist.CLIENT,
                () -> () -> Hk3LetterScreen.open(packet.document, packet.state, packet.context)));
        context.setPacketHandled(true);
    }
}
