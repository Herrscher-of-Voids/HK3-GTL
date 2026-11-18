package com.sirin.hk3gtl.mixin;

import net.minecraft.world.level.LevelSettings;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Mutable;
import org.spongepowered.asm.mixin.gen.Accessor;

/**
 * LevelSettings 访问器 —— levelName 为 final 字段，通过 @Mutable 解除后写入，
 * 用于坏结局将世界名改为「xxxx：已被抹除」。
 */
@Mixin(LevelSettings.class)
public interface LevelSettingsAccessor {

    @Mutable
    @Accessor("levelName")
    void hk3gtl$setLevelName(String name);
}
