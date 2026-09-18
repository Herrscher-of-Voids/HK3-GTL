package com.sirin.hk3gtl.common.recipe;



import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.gui.GuiTextures;
import com.gregtechceu.gtceu.api.recipe.GTRecipeType;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.gregtechceu.gtceu.common.data.GTSoundEntries;

import static com.lowdragmc.lowdraglib.gui.texture.ProgressTexture.FillDirection.LEFT_TO_RIGHT;

/**
 * 量子阶段配方类型（v0.3，12台对应）。
 */
public class Hk3RecipeTypesQuantum {

    public static final GTRecipeType QUANTUM_ENTANGLEMENT_COMPUTING = reg("quantum_entanglement_computing", 6, 4, 1, 1, IO.IN, GTSoundEntries.ELECTROLYZER);
    public static final GTRecipeType THOUSAND_REALMS_TRANSIT = reg("thousand_realms_transit", 6, 6, 2, 2, IO.IN, GTSoundEntries.MOTOR);
    public static final GTRecipeType WORLD_BUBBLE_MELTDOWN = reg("world_bubble_meltdown", 4, 4, 2, 2, IO.IN, GTSoundEntries.FURNACE);
    public static final GTRecipeType QUANTUM_SUPERCONDUCTOR_LATTICE = reg("quantum_superconductor_lattice", 6, 4, 1, 1, IO.IN, GTSoundEntries.ASSEMBLER);
    public static final GTRecipeType HONKAI_WIRELESS_TRANSIT = reg("honkai_wireless_transit", 2, 2, 1, 1, IO.IN, GTSoundEntries.ARC);
    public static final GTRecipeType QUANTUM_THOUGHT_FORGING = reg("quantum_thought_forging", 6, 2, 1, 0, IO.IN, GTSoundEntries.ASSEMBLER);
    public static final GTRecipeType DIVINE_KEY_DISPLAY = reg("divine_key_display", 4, 4, 0, 0, IO.IN, GTSoundEntries.ELECTROLYZER);
    public static final GTRecipeType QUANTUM_CIVILIZATION_TRADE = reg("quantum_civilization_trade", 6, 6, 1, 1, IO.IN, GTSoundEntries.MOTOR);
    public static final GTRecipeType QUANTUM_HONKAI_FUSION = reg("quantum_honkai_fusion", 4, 4, 2, 2, IO.OUT, GTSoundEntries.FURNACE);
    public static final GTRecipeType FINALITY_PRESSURE_BUFFERING = reg("finality_pressure_buffering", 4, 4, 2, 2, IO.IN, GTSoundEntries.COOLING);
    public static final GTRecipeType WONDER_CONSTRUCTION_SIMULATION = reg("wonder_construction_simulation", 4, 4, 1, 1, IO.IN, GTSoundEntries.ASSEMBLER);
    /** 量子级精密装配：独立 RecipeType，不复用任何 shipboard/休伯利安相关能力。 */
    public static final GTRecipeType QUANTUM_PRECISION_ASSEMBLY = reg("quantum_precision_assembly", 6, 4, 1, 1, IO.IN, GTSoundEntries.ASSEMBLER);

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
