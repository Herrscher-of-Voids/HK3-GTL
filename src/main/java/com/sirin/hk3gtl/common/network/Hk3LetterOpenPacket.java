package com.sirin.hk3gtl.common.network;

/** 【变更记录 #2】2026-09-30 23:58:50（修订121）：删除旧个人答复自动代表新队的生产路径；新增/修改：首信包附当前权限、预览令牌和补谈步骤，不接受客户端自报状态；用途：团队外交、阅读与个人经历分账，不发研究或物品奖励。 */

/**
 * 【变更记录 #1】2026-09-29 17:51:46（内测5修订93）
 * - 删除：旧正文活动引用被审核原文替代；保留历史资源和存档。
 * - 新增／修改：阅读范围扩展到六份首信相关文档，后续来信仍由服务端核验状态。
 * - 用途：接通审核正文；其他系统触发及归属不据此宣称完成。
 */
import com.sirin.hk3gtl.client.communication.Hk3LetterScreen;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;
import java.util.function.Supplier;

/** 中文说明：该处说明已按当前代码行为整理。*/
public record Hk3LetterOpenPacket(int document, String state, net.minecraft.nbt.CompoundTag context) {
    /** 文档号0..2，状态名最多16字符；超界直接拒绝，防止任意资源访问。 / Bound document IDs to 0..2 and state names to 16 chars. */
    public Hk3LetterOpenPacket {
        context=context.copy();
        if (document < 0 || document > 5 || state.length() > 16) throw new IllegalArgumentException("Invalid letter packet");
    }
    /** 中文说明：该处说明已按当前代码行为整理。*/
    public static void encode(Hk3LetterOpenPacket packet, FriendlyByteBuf buffer) {
        buffer.writeVarInt(packet.document); buffer.writeUtf(packet.state, 16); buffer.writeNbt(packet.context);
    }
    /** 解码同一协议边界，构造器再次校验。 / Decode using identical bounds and constructor validation. */
    public static Hk3LetterOpenPacket decode(FriendlyByteBuf buffer) {
        return new Hk3LetterOpenPacket(buffer.readVarInt(), buffer.readUtf(16), java.util.Objects.requireNonNull(buffer.readNbt()));
    }
    /** 中文说明：该处说明已按当前代码行为整理。*/
    public static void handle(Hk3LetterOpenPacket packet, Supplier<NetworkEvent.Context> supplier) {
        NetworkEvent.Context context = supplier.get();
        context.enqueueWork(() -> DistExecutor.unsafeRunWhenOn(Dist.CLIENT,
                () -> () -> Hk3LetterScreen.open(packet.document, packet.state, packet.context)));
        context.setPacketHandled(true);
    }
}
