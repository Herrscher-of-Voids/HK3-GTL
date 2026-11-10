package com.sirin.hk3gtl.mixin.height;

import com.mojang.datafixers.DataFixer;
import com.mojang.serialization.Dynamic;
import com.mojang.serialization.Lifecycle;
import com.sirin.hk3gtl.common.dimension.height.*;
import net.minecraft.core.RegistryAccess;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.NbtOps;
import net.minecraft.world.level.LevelSettings;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.storage.LevelVersion;
import net.minecraft.world.level.storage.PrimaryLevelData;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.Map;
import java.util.UUID;

/**
 * 【文件职责】区别新建公开构造与旧档parse路径，在世界数据实例保存高度合同。
 * 【变更记录 #1】2026-10-17 21:19:41（第1次备注 · 修订166）
 * - 删除：无。新增：新世界身份、原生NBT合同写入/严格读取及瞬态应用标记。
 * - 修改：无合同旧档保持空合同，不依据level.dat存在或initialized猜测新世界。
 * - 用途：新建、重启、客户端新世界流程与专服共用持久身份，损坏合同拒绝加载而非降高。
 * 【变更记录 #2】2026-10-17 21:43:13（第2次备注 · 修订166）
 * - 删除：无，保留全部历史和无合同旧档分支。
 * - 新增：createTag写入前冻结原始注册表快照。
 * - 修改：兼容Minecraft在启动集成服务器前先保存新世界的实际调用顺序，禁止保存启用但无边界的合同。
 * - 用途：首次保存后中断再重开仍能核验原始高度；只读取注册表，不在保存路径修改维度高度。
 * 【变更记录 #3】2026-10-17 21:46:43（第3次备注 · 修订166）
 * - 删除：无。新增：保存封存入口传入本实例的应用标记。
 * - 修改：明确区分启动前原边界与运行后新边界，不由数值相同猜测世界状态。
 * - 用途：在原生世界数据写盘前拒绝维度资源漂移，避免写入不兼容设置。
 */
@Mixin(PrimaryLevelData.class)
public abstract class Hk3PrimaryLevelHeightMixin implements Hk3HeightWorldData {
    @Unique private static final String HK3GTL_HEIGHT_TAG = Hk3HeightWorldState.TAG_KEY;
    @Unique private Hk3HeightWorldState hk3gtl$heightState;
    @Unique private boolean hk3gtl$heightApplied;

    @Inject(method="<init>(Lnet/minecraft/world/level/LevelSettings;Lnet/minecraft/world/level/levelgen/WorldOptions;Lnet/minecraft/world/level/storage/PrimaryLevelData$SpecialWorldProperty;Lcom/mojang/serialization/Lifecycle;)V", at=@At("RETURN"))
    private void hk3gtl$newWorld(LevelSettings settings, WorldOptions options, PrimaryLevelData.SpecialWorldProperty property,
                                  Lifecycle lifecycle, CallbackInfo ci) {
        if (Hk3HeightConfig.shouldEnable(settings, property)) {
            int top = Hk3HeightConfig.TOP_EXCLUSIVE.get();
            Hk3HeightPolicy.requireTopExclusive(top);
            hk3gtl$heightState = new Hk3HeightWorldState(UUID.randomUUID(), Hk3HeightWorldState.CURRENT_VERSION, top, true, Map.of());
        }
    }

    @Inject(method="parse", at=@At("RETURN"))
    private static <T> void hk3gtl$readContract(Dynamic<T> source, DataFixer fixer, int version, CompoundTag player,
            LevelSettings settings, LevelVersion levelVersion, PrimaryLevelData.SpecialWorldProperty property,
            WorldOptions options, Lifecycle lifecycle, CallbackInfoReturnable<PrimaryLevelData> cir) {
        var saved = source.get(HK3GTL_HEIGHT_TAG).result();
        if (saved.isEmpty()) return;
        var tag = saved.get().convert(NbtOps.INSTANCE).getValue();
        if (!(tag instanceof CompoundTag contract)) throw new IllegalArgumentException("高度合同必须为完整NBT对象，拒绝忽略后降高。");
        ((Hk3HeightWorldData)cir.getReturnValue()).hk3gtl$setHeightState(Hk3HeightWorldState.fromNbt(contract));
    }

    @Inject(method="createTag", at=@At("RETURN"))
    private void hk3gtl$writeContract(RegistryAccess registry, CompoundTag player, CallbackInfoReturnable<CompoundTag> cir) {
        if (hk3gtl$heightState != null) {
            hk3gtl$heightState = Hk3HeightService.freezeBeforeSave(registry, hk3gtl$heightState, hk3gtl$heightApplied);
            cir.getReturnValue().put(HK3GTL_HEIGHT_TAG, hk3gtl$heightState.toNbt());
        }
    }
    @Override public Hk3HeightWorldState hk3gtl$getHeightState() { return hk3gtl$heightState; }
    @Override public void hk3gtl$setHeightState(Hk3HeightWorldState state) { hk3gtl$heightState = state; }
    @Override public boolean hk3gtl$isHeightApplied() { return hk3gtl$heightApplied; }
    @Override public void hk3gtl$markHeightApplied() { hk3gtl$heightApplied = true; }
}
