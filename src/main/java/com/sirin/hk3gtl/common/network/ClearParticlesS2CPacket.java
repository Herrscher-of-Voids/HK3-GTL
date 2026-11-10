package com.sirin.hk3gtl.common.network;

import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/**
 * 【文件职责】
 * - 服务端 -> 客户端 强制清除粒子包：通知客户端立即回收全部存活粒子。
 *
 * 【背景】2026-07-03（内测四·特效残留修复）
 * - 香草 Minecraft 中，服务端 sendParticles 生成的粒子生命周期完全由客户端管理，
 *   服务端无法逐个销毁。西琳出场动画高密度、长寿命的 PORTAL/REVERSE_PORTAL 粒子会
 *   在落位后残留成拖影。唯一能保证“转场前 100% 清除”的手段，是让客户端主动调用
 *   {@code ParticleEngine.clearParticles()} 强制回收。
 *
 * 【用途】西琳出场动作完成、进入对话转场前，服务端向观演玩家下发本包，清干净残留粒子。
 */
public record ClearParticlesS2CPacket() {

    public static void encode(ClearParticlesS2CPacket pkt, FriendlyByteBuf buf) {
        // 无字段：本包仅作为“立即清除粒子”的信号
    }

    public static ClearParticlesS2CPacket decode(FriendlyByteBuf buf) {
        return new ClearParticlesS2CPacket();
    }

    public static void handle(ClearParticlesS2CPacket pkt, Supplier<NetworkEvent.Context> ctxSupplier) {
        NetworkEvent.Context ctx = ctxSupplier.get();
        // 仅客户端物理端执行，服务端不加载客户端类，避免 ClassNotFound。
        ctx.enqueueWork(() -> DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> ClientParticleClearHandler::clear));
        ctx.setPacketHandled(true);
    }
}
