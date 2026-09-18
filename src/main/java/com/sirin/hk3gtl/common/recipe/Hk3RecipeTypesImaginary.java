package com.sirin.hk3gtl.common.recipe;



import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.gui.GuiTextures;
import com.gregtechceu.gtceu.api.recipe.GTRecipeType;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.gregtechceu.gtceu.common.data.GTSoundEntries;

import static com.lowdragmc.lowdraglib.gui.texture.ProgressTexture.FillDirection.LEFT_TO_RIGHT;

/**
 * 虚数阶段配方类型（v0.3 精简版）。
 */
public class Hk3RecipeTypesImaginary {

    public static final GTRecipeType IMAGINARY_TREE_OBSERVATION = reg("imaginary_tree_observation", 4, 4, 1, 1, IO.IN, GTSoundEntries.ELECTROLYZER);
    public static final GTRecipeType IMAGINARY_ANCHORING = reg("imaginary_anchoring", 4, 2, 1, 1, IO.IN, GTSoundEntries.ARC);
    public static final GTRecipeType IMAGINARY_CIRCUIT_COMPUTATION = reg("imaginary_circuit_computation", 6, 4, 1, 0, IO.IN, GTSoundEntries.ASSEMBLER);
    public static final GTRecipeType SOULIUM_SUPERSTRUCTURE_FORGING = reg("soulium_superstructure_forging", 6, 4, 2, 1, IO.IN, GTSoundEntries.FURNACE);
    public static final GTRecipeType CIVILIZATION_EXCHANGE = reg("civilization_exchange", 4, 4, 0, 0, IO.IN, GTSoundEntries.ELECTROLYZER);
    public static final GTRecipeType PRECIVILIZATION_DATABASE_DECODING = reg("precivilization_database_decoding", 4, 4, 0, 0, IO.IN, GTSoundEntries.ELECTROLYZER);
    public static final GTRecipeType HONKAI_PHASE_PURIFICATION = reg("honkai_phase_purification", 4, 4, 2, 1, IO.IN, GTSoundEntries.COOLING);
    public static final GTRecipeType IMAGINARY_MATTER_WEAVING = reg("imaginary_matter_weaving", 4, 2, 1, 1, IO.IN, GTSoundEntries.ASSEMBLER);
    public static final GTRecipeType DUAL_ENERGY_STABLE_SUPPLY = reg("dual_energy_stable_supply", 2, 2, 1, 1, IO.BOTH, GTSoundEntries.ARC);
    public static final GTRecipeType IMAGINARY_DREAM_MELTING = reg("imaginary_dream_melting", 4, 2, 1, 0, IO.IN, GTSoundEntries.FURNACE);

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
