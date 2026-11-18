package com.sirin.hk3gtl.mixin;

import net.minecraft.world.level.LevelSettings;
import net.minecraft.world.level.storage.PrimaryLevelData;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/**
 * PrimaryLevelData 访问器 —— 暴露内部 LevelSettings，供坏结局改写世界名称
 * （level.dat 的 Data.LevelName 由 settings.levelName() 序列化）。
 */
@Mixin(PrimaryLevelData.class)
public interface PrimaryLevelDataAccessor {

    @Accessor("settings")
    LevelSettings hk3gtl$getSettings();
}
