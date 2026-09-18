package com.sirin.hk3gtl.common.recipe;



import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.gui.GuiTextures;
import com.gregtechceu.gtceu.api.recipe.GTRecipeType;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.gregtechceu.gtceu.common.data.GTSoundEntries;

import static com.lowdragmc.lowdraglib.gui.texture.ProgressTexture.FillDirection.LEFT_TO_RIGHT;

/**
 * 终焉阶段配方类型（v0.3）。
 */
public class Hk3RecipeTypesFinality {

    public static final GTRecipeType HYPERION_FLAGSHIP_PROCESSING = reg("hyperion_flagship_processing", 6, 6, 4, 4, IO.IN, GTSoundEntries.ASSEMBLER);
    public static final GTRecipeType SHIPBOARD_FINALITY_OBSERVATION = reg("shipboard_finality_observation", 4, 4, 1, 1, IO.IN, GTSoundEntries.ELECTROLYZER);
    public static final GTRecipeType SHIPBOARD_DUAL_ENERGY_REACTOR = reg("shipboard_dual_energy_reactor", 4, 4, 2, 2, IO.BOTH, GTSoundEntries.ARC);
    public static final GTRecipeType SHIPBOARD_ENDGAME_COORDINATION = reg("shipboard_endgame_coordination", 4, 4, 1, 1, IO.IN, GTSoundEntries.ELECTROLYZER);
    public static final GTRecipeType SHIPBOARD_DIVINE_KEY = reg("shipboard_divine_key", 4, 4, 0, 0, IO.IN, GTSoundEntries.ELECTROLYZER);
    public static final GTRecipeType FINALITY_CIVILIZATION_CONSTRUCTION = reg("finality_civilization_construction", 6, 4, 2, 2, IO.IN, GTSoundEntries.ASSEMBLER);
    public static final GTRecipeType CIVILIZATION_VALIDATION = reg("civilization_validation", 6, 4, 2, 2, IO.IN, GTSoundEntries.ARC);
    public static final GTRecipeType FINALITY_ENERGY_DISTRIBUTION = reg("finality_energy_distribution", 4, 4, 2, 2, IO.BOTH, GTSoundEntries.ARC);
    public static final GTRecipeType FINALITY_ULTIMATE_MATERIAL_FORGE = reg("finality_ultimate_material_forge", 6, 4, 2, 1, IO.IN, GTSoundEntries.FURNACE);
    public static final GTRecipeType FINALITY_HONKAI_ANNIHILATION = reg("finality_honkai_annihilation", 4, 4, 2, 2, IO.OUT, GTSoundEntries.FURNACE);
    public static final GTRecipeType GRADUATION_PERMISSION_VERIFICATION = reg("graduation_permission_verification", 4, 2, 1, 1, IO.IN, GTSoundEntries.ARC);
    public static final GTRecipeType CIVILIZATION_WONDER_SANCTUM = reg("civilization_wonder_sanctum", 6, 6, 2, 2, IO.IN, GTSoundEntries.ASSEMBLER);
    public static final GTRecipeType IMAGINARY_DIMENSION_GATEWAY_PROC = reg("imaginary_dimension_gateway", 4, 4, 2, 2, IO.IN, GTSoundEntries.ARC);

    private static GTRecipeType reg(String id, int iIn, int iOut, int fIn, int fOut, IO euIO,
                                    com.gregtechceu.gtceu.api.sound.SoundEntry sound) {
        return GTRecipeTypes.register(id, "multiblock")
                .setMaxIOSize(iIn, iOut, fIn, fOut)
                .setEUIO(euIO)
                .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
                .setSound(sound);
    }

    public static void init() {
    }
}
