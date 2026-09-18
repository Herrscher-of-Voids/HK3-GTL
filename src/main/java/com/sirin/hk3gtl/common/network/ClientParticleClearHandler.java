package com.sirin.hk3gtl.common.network;

import net.minecraft.client.Minecraft;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

/**
 * 客户端粒子清除执行器：调用引擎的 clearParticles 强制回收所有存活粒子。
 * 单独成类，隔离客户端专用调用，避免服务端触碰 Minecraft 客户端实例。
 */
@OnlyIn(Dist.CLIENT)
final class ClientParticleClearHandler {

    private ClientParticleClearHandler() {}

    static void clear() {
        Minecraft mc = Minecraft.getInstance();
        if (mc.particleEngine != null && mc.level != null) {
            // ParticleEngine.clearParticles() 为 private，无法直接调用；
            // 公开的 setLevel(level) 内部会清空全部粒子池（trackedParticles / particles），
            // 传入当前 level 即可安全地一次性回收所有存活粒子，且不影响后续粒子渲染。
            mc.particleEngine.setLevel(mc.level);
        }
    }
}
