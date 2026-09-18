package com.sirin.hk3gtl.common.recipe;



import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.gui.GuiTextures;
import com.gregtechceu.gtceu.api.recipe.GTRecipeType;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.gregtechceu.gtceu.common.data.GTSoundEntries;

import static com.lowdragmc.lowdraglib.gui.texture.ProgressTexture.FillDirection.LEFT_TO_RIGHT;

/**
 * 奇观阶段配方类型（v0.3，12台）。
 */
public class Hk3RecipeTypesWonder {

    public static final GTRecipeType HONKAI_ULTIMATE_FUSION = reg("honkai_ultimate_fusion", 4, 4, 4, 4, IO.OUT, GTSoundEntries.FURNACE);
    public static final GTRecipeType DIVINE_KEY_GRAND_CATHEDRAL = reg("divine_key_grand_cathedral", 6, 6, 2, 2, IO.IN, GTSoundEntries.ASSEMBLER);
    public static final GTRecipeType CIVILIZATION_JUDGMENT = reg("civilization_judgment", 4, 4, 1, 1, IO.IN, GTSoundEntries.ARC);
    public static final GTRecipeType CIVILIZATION_MEMORY_ETERNAL = reg("civilization_memory_eternal", 4, 4, 0, 0, IO.IN, GTSoundEntries.ELECTROLYZER);
    public static final GTRecipeType MYRIAD_REALMS_COMMUNICATION = reg("myriad_realms_communication", 4, 2, 1, 1, IO.IN, GTSoundEntries.ELECTROLYZER);
    public static final GTRecipeType DESTINY_WEAVING = reg("destiny_weaving", 6, 4, 1, 0, IO.IN, GTSoundEntries.ASSEMBLER);
    public static final GTRecipeType CIVILIZATION_EYE_OBSERVATION = reg("civilization_eye_observation", 4, 4, 1, 1, IO.IN, GTSoundEntries.ELECTROLYZER);
    public static final GTRecipeType CYCLE_NARRATION = reg("cycle_narration", 4, 2, 0, 0, IO.IN, GTSoundEntries.ELECTROLYZER);
    public static final GTRecipeType CIVILIZATION_STARSHIP_EXHIBITION = reg("civilization_starship_exhibition", 4, 4, 0, 0, IO.IN, GTSoundEntries.ELECTROLYZER);
    public static final GTRecipeType PROOF_OF_EXISTENCE = reg("proof_of_existence", 4, 2, 1, 1, IO.IN, GTSoundEntries.ARC);
    public static final GTRecipeType ULTIMATE_MEDITATION = reg("ultimate_meditation", 2, 2, 1, 1, IO.IN, GTSoundEntries.COOLING);
    public static final GTRecipeType GRAND_CONVERGENCE = reg("grand_convergence", 6, 4, 2, 1, IO.IN, GTSoundEntries.ASSEMBLER);

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
