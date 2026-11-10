package com.sirin.hk3gtl.mixin.gtlsupb;
import com.gtlsupb.gtlsupb.api.dimension.PrivateDimensionManager;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.Level;
import net.minecraft.core.BlockPos;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(value=PrivateDimensionManager.class,remap=false)
/** 【变更记录 #1】2026-10-01 13:26:03（修订128）：删除：无；新增/修改：真实传送结束验证目的维度和位置，调用来源必须是现有维度传送器，其他命令传送不冒充；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public abstract class Hk3EggPrivateTeleportMixin {
    @Inject(method="teleportPlayer",at=@At("HEAD"))private static void hk3gtl$before(ServerPlayer p,ResourceKey<Level> target,BlockPos pos,CallbackInfo ci){var s=com.sirin.hk3gtl.common.easter.Hk3EggRuntime.state(p);s.remove("dimensionalAttempt");boolean tool=StackWalker.getInstance().walk(frames->frames.anyMatch(f->f.getClassName().equals("com.gtlsupb.gtlsupb.common.item.DimensionalTeleporter")));if(tool&&!p.level().dimension().equals(target))s.putBoolean("dimensionalAttempt",true);}
    @Inject(method="teleportPlayer",at=@At("RETURN"))private static void hk3gtl$after(ServerPlayer p,ResourceKey<Level> target,BlockPos pos,CallbackInfo ci){var s=com.sirin.hk3gtl.common.easter.Hk3EggRuntime.state(p);if(s.getBoolean("dimensionalAttempt")&&p.level().dimension().equals(target)&&p.blockPosition().distSqr(pos)<4){s.putLong("dimensionalTeleported",p.server.overworld().getGameTime());s.putString("dimensionalTeleportedDim",target.location().toString());}s.remove("dimensionalAttempt");}
}
