package com.sirin.hk3gtl.common.multiblock.pattern;



import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.pattern.BlockPattern;
import net.minecraft.world.level.block.Block;
import net.minecraftforge.registries.RegistryObject;

/**
 * P1 核心三台多方块 + 通用中型结构的 Pattern 门面类。
 *
 * @see Hk3P1PatternsImpl
 */
public class Hk3P1Patterns {

    private Hk3P1Patterns() {}

    public static BlockPattern createAbsorptionTower(MultiblockMachineDefinition definition) {
        return Hk3P1PatternsImpl.createAbsorptionTower(definition);
    }

    public static BlockPattern createCrystalCondenser(MultiblockMachineDefinition definition) {
        return Hk3P1PatternsImpl.createCrystalCondenser(definition);
    }

    public static BlockPattern createSouliumSmeltery(MultiblockMachineDefinition definition) {
        return Hk3P1PatternsImpl.createSouliumSmeltery(definition);
    }

    public static BlockPattern createGenericMedium(MultiblockMachineDefinition definition,
                                                   RegistryObject<Block> casing) {
        return Hk3P1PatternsImpl.createGenericMedium(definition, casing);
    }
}
