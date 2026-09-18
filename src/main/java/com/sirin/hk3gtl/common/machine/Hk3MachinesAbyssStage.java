package com.sirin.hk3gtl.common.machine;



import com.gregtechceu.gtceu.api.data.RotationState;
import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.registry.registrate.GTRegistrate;
import com.mojang.logging.LogUtils;
import com.sirin.hk3gtl.Hk3Gtl;
import com.sirin.hk3gtl.common.block.CasingBlocks;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3P1Patterns;
import com.sirin.hk3gtl.common.recipe.Hk3RecipeTypes;
import net.minecraft.resources.ResourceLocation;
import org.slf4j.Logger;

/**
 * 海渊阶段（v0.3）仅保留 4 台聚合机器。
 */
public class Hk3MachinesAbyssStage {

    private static final Logger LOGGER = LogUtils.getLogger();
    private static final ResourceLocation OVERLAY = new ResourceLocation(Hk3Constants.MOD_ID, "block/overlay/default_set");

    public static MultiblockMachineDefinition LARGE_HONKAI_REACTOR;
    public static MultiblockMachineDefinition ABYSS_DEEP_SMELTERY;
    public static MultiblockMachineDefinition ABYSS_PRECISION_WORKSHOP;
    public static MultiblockMachineDefinition ABYSS_PARTICLE_RESEARCH_RING;

    private static GTRegistrate reg() {
        return Hk3Gtl.REGISTRATE;
    }

    private static ResourceLocation tex(String name) {
        return new ResourceLocation(Hk3Constants.MOD_ID, "block/casings/" + name);
    }

    public static void init() {
        LARGE_HONKAI_REACTOR = reg()
                .multiblock("large_honkai_reactor", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypes.LARGE_HONKAI_REACTION_RECIPES)
                .appearanceBlock(CasingBlocks.CASING_ABYSS_ENERGY)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_ABYSS_ENERGY))
                .workableCasingRenderer(tex("casing_abyss_energy"), OVERLAY)
                .register();

        // 合并化学反应、合金精炼、真空熔炼、裂解等深熔链
        ABYSS_DEEP_SMELTERY = reg()
                .multiblock("abyss_deep_smeltery", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypes.ABYSS_VACUUM_SMELTING_RECIPES)
                .appearanceBlock(CasingBlocks.CASING_REINFORCED_SOULIUM)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_REINFORCED_SOULIUM))
                .workableCasingRenderer(tex("casing_reinforced_soulium"), OVERLAY)
                .register();

        // 合并精密装配、纳米加工与材料压缩链
        ABYSS_PRECISION_WORKSHOP = reg()
                .multiblock("abyss_precision_workshop", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypes.ABYSS_PRECISION_ASSEMBLY_RECIPES)
                .appearanceBlock(CasingBlocks.CASING_ABYSS_MECHANICAL)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_ABYSS_MECHANICAL))
                .workableCasingRenderer(tex("casing_abyss_mechanical"), OVERLAY)
                .register();

        // 合并粒子加速、生物计算、频谱分析科研链
        ABYSS_PARTICLE_RESEARCH_RING = reg()
                .multiblock("abyss_particle_research_ring", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypes.ABYSS_PARTICLE_ACCELERATION_RECIPES)
                .appearanceBlock(CasingBlocks.CASING_ABYSS_RESEARCH)
                .pattern(def -> Hk3P1Patterns.createGenericMedium(def, CasingBlocks.CASING_ABYSS_RESEARCH))
                .workableCasingRenderer(tex("casing_abyss_research"), OVERLAY)
                .register();

        LOGGER.info("[HK3GTL] Abyss阶段多方块初始化完成（4台）。");
    }
}
