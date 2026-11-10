package com.sirin.hk3gtl.mixin;

import com.mojang.datafixers.DataFixer;
import com.mojang.serialization.Dynamic;
import com.mojang.serialization.Lifecycle;
import com.sirin.hk3gtl.common.easter.*;
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
import java.time.Instant;

/**
 * 【文件职责】在新建世界公开构造入口捕获创建时刻，通过原生level.dat持久保存。
 * 【变更记录 #1】2026-11-05 19:08:32（修订210）
 * 删除：无。新增：新建捕获、旧档严格读取、原生保存；修改：无高度合同和旧档创建时间。
 * 用途：旧档parse路径不补当前时间，生日元数据缺失保持未知，不读取文件修改时间或LastPlayed。
 */
@Mixin(PrimaryLevelData.class)
public abstract class Hk3WorldOriginMixin implements Hk3WorldOriginData {
    @Unique private Hk3WorldOrigin hk3gtl$worldOrigin;

    @Inject(method="<init>(Lnet/minecraft/world/level/LevelSettings;Lnet/minecraft/world/level/levelgen/WorldOptions;Lnet/minecraft/world/level/storage/PrimaryLevelData$SpecialWorldProperty;Lcom/mojang/serialization/Lifecycle;)V", at=@At("RETURN"))
    private void hk3gtl$captureCreation(LevelSettings settings, WorldOptions options, PrimaryLevelData.SpecialWorldProperty property,
            Lifecycle lifecycle, CallbackInfo ci) {
        hk3gtl$worldOrigin = new Hk3WorldOrigin(Instant.now());
    }

    @Inject(method="parse", at=@At("RETURN"))
    private static <T> void hk3gtl$readOrigin(Dynamic<T> source, DataFixer fixer, int version, CompoundTag player,
            LevelSettings settings, LevelVersion levelVersion, PrimaryLevelData.SpecialWorldProperty property,
            WorldOptions options, Lifecycle lifecycle, CallbackInfoReturnable<PrimaryLevelData> cir) {
        var saved = source.get(Hk3WorldOrigin.TAG).result();
        if (saved.isEmpty()) return;
        var tag = saved.get().convert(NbtOps.INSTANCE).getValue();
        if (tag instanceof CompoundTag compound) ((Hk3WorldOriginMixin)(Object)cir.getReturnValue()).hk3gtl$worldOrigin = Hk3WorldOrigin.read(compound).orElse(null);
    }

    @Inject(method="createTag", at=@At("RETURN"))
    private void hk3gtl$writeOrigin(RegistryAccess registry, CompoundTag player, CallbackInfoReturnable<CompoundTag> cir) {
        if (hk3gtl$worldOrigin != null) cir.getReturnValue().put(Hk3WorldOrigin.TAG, hk3gtl$worldOrigin.save());
    }
    @Override public Hk3WorldOrigin hk3gtl$getWorldOrigin() { return hk3gtl$worldOrigin; }
}
