package com.sirin.hk3gtl.mixin.gtceu;

import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import com.gregtechceu.gtceu.api.pattern.MultiblockWorldSavedData;
import com.gregtechceu.gtceu.api.pattern.MultiblockState;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.sirin.hk3gtl.common.multiblock.build.Hk3UniversalTerminalBuilder;
import com.mojang.logging.LogUtils;
import net.minecraft.server.level.ServerLevel;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * 【文件职责】分批建造期间跳过周期性全结构扫描，任务结束后恢复原GT检查。
 * 【变更记录 #1】2026-10-30 01:36:10（修订184）：新增建造期多方块检查节流入口。
 * 【变更记录 #2】2026-10-30（修订184）：HK异步结果在主线程锁内复检，防止开工前排队结果误报成型。
 * 【变更记录 #3】2026-10-30 02:29:19（修订184）：异步入口只排队，主线程锁内完成唯一真实检查；去重排队并清理卸载任务。
 */
@Mixin(value = MultiblockControllerMachine.class, remap = false)
public abstract class Hk3UniversalBuildCheckMixin {
    @Unique private final AtomicBoolean hk3gtl$checkQueued = new AtomicBoolean();

    @Inject(method = "asyncCheckPattern", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$skipRepeatedBuildScan(long periodID, CallbackInfo callback) {
        MultiblockControllerMachine controller = (MultiblockControllerMachine) (Object) this;
        if (!"hk3gtl".equals(controller.self().getDefinition().getId().getNamespace())) return;
        callback.cancel();
        if (Hk3UniversalTerminalBuilder.isBuilding(controller) || controller.isInValid()
                || controller.isFormed() && !controller.getMultiblockState().hasError()
                || (controller.getHolder().getOffset() + periodID) % 4L != 0L
                || !(controller.getLevel() instanceof ServerLevel level)
                || !hk3gtl$checkQueued.compareAndSet(false,true)) return;
        try {
            level.getServer().execute(() -> {
                try {
                    if (Hk3UniversalTerminalBuilder.isBuilding(controller) || controller.isInValid()
                            || controller.getLevel() != level
                            || level.getChunkSource().getChunkNow(controller.getPos().getX() >> 4,controller.getPos().getZ() >> 4) == null
                            || MetaMachine.getMachine(level,controller.getPos()) != controller
                            || !controller.getPatternLock().tryLock()) return;
                    try {
                        if (Hk3UniversalTerminalBuilder.isBuilding(controller) || controller.isInValid()
                                || controller.isFormed() && !controller.getMultiblockState().hasError()
                                || !controller.checkPattern()) return;
                        controller.setFlipped(controller.getMultiblockState().isNeededFlip());
                        controller.onStructureFormed();
                        var saved = MultiblockWorldSavedData.getOrCreate(level);
                        saved.addMapping(controller.getMultiblockState());
                        saved.removeAsyncLogic(controller);
                    } catch (RuntimeException failure) {
                        try {
                            controller.onStructureInvalid();
                            controller.getMultiblockState().setError(MultiblockState.UNINIT_ERROR);
                            MultiblockWorldSavedData.getOrCreate(level).removeMapping(controller.getMultiblockState());
                        } catch (RuntimeException cleanup) { failure.addSuppressed(cleanup); }
                        throw failure;
                    } finally { controller.getPatternLock().unlock(); }
                } catch (RuntimeException failure) {
                    LogUtils.getLogger().error("HK3GTL主线程真实结构检查失败：{}",controller.self().getDefinition().getId(),failure);
                } finally { hk3gtl$checkQueued.set(false); }
            });
        } catch (RuntimeException failure) {
            hk3gtl$checkQueued.set(false);
            throw failure;
        }
    }

    @Inject(method = "onUnload", at = @At("HEAD"))
    private void hk3gtl$releaseBuildOnUnload(CallbackInfo callback) {
        Hk3UniversalTerminalBuilder.controllerUnloaded((MultiblockControllerMachine)(Object)this);
    }

    @Inject(method = "onStructureFormed", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$rejectStaleFormation(CallbackInfo callback) {
        if (Hk3UniversalTerminalBuilder.isBuilding((MultiblockControllerMachine)(Object)this)) callback.cancel();
    }
}
