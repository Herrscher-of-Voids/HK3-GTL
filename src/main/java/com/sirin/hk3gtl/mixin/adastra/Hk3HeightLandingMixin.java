package com.sirin.hk3gtl.mixin.adastra;

/** 【变更记录 #1】2026-10-31 00:46:39（第1次备注 · 修订187）：删除无；新增合同扩高维度的49柱高度图避障；修改降落前的玩家及着陆器共同入口；用途：不扫描整片建筑，不把着陆点放进高层结构。 */

import com.sirin.hk3gtl.common.dimension.height.Hk3HeightLandingPolicy;
import com.sirin.hk3gtl.common.dimension.height.Hk3HeightService;
import earth.terrarium.adastra.common.utils.ModUtils;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

/** Ad Astra 原入口可能位于扩高建筑内部；落地前按原生高度图抬高入口，不拆建筑。 */
@Mixin(value = ModUtils.class, remap = false)
public abstract class Hk3HeightLandingMixin {
    @ModifyVariable(method = "land", at = @At("HEAD"), argsOnly = true)
    private static Vec3 hk3gtl$safeArrival(Vec3 requested, ServerPlayer player, ServerLevel target, Vec3 original) {
        var state = Hk3HeightService.state(target.getServer()).orElse(null);
        if (state == null || !state.enabled()) return requested;
        var bounds = state.dimensions().get(target.dimensionTypeId().location().toString());
        if (bounds == null || bounds.newHeight() == bounds.originalHeight()) return requested;
        var center = BlockPos.containing(requested);
        int firstFree = target.getMinBuildHeight();
        for (int x = center.getX() - 3; x <= center.getX() + 3; x++) {
            for (int z = center.getZ() - 3; z <= center.getZ() + 3; z++) {
                firstFree = Math.max(firstFree, target.getHeight(Heightmap.Types.MOTION_BLOCKING, x, z));
            }
        }
        return new Vec3(requested.x, Hk3HeightLandingPolicy.arrivalY(requested.y, firstFree), requested.z);
    }
}
