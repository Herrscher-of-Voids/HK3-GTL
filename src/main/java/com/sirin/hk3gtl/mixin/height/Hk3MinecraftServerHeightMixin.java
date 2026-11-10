package com.sirin.hk3gtl.mixin.height;

import com.sirin.hk3gtl.common.dimension.height.Hk3HeightService;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.progress.ChunkProgressListener;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * 【文件职责】在服务器首个Level构造、Radium缓存与区段分配之前应用世界合同。
 * 【变更记录 #1】2026-10-17 21:19:41（第1次备注 · 修订166）
 * - 删除：无。新增：createLevels入口；修改：不在全局DimensionType构造时改高。
 * - 用途：同时覆盖原版全部维度与后续AE2动态ServerLevel，不写已有玩家世界。
 */
@Mixin(MinecraftServer.class)
public abstract class Hk3MinecraftServerHeightMixin {
    @Inject(method="createLevels", at=@At("HEAD"))
    private void hk3gtl$applyHeight(ChunkProgressListener listener, CallbackInfo ci) {
        Hk3HeightService.applyBeforeLevels((MinecraftServer)(Object)this);
    }
}
