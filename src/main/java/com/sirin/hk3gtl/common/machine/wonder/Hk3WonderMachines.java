package com.sirin.hk3gtl.common.machine.wonder;

import com.gregtechceu.gtceu.api.data.RotationState;
import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.sirin.hk3gtl.Hk3Gtl;
import com.sirin.hk3gtl.common.capability.Hk3DualEnergyCosts;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.machine.Hk3W01Machines;
import com.sirin.hk3gtl.common.machine.w02.Hk3W02Machines;
import com.sirin.hk3gtl.common.machine.w03.Hk3W03Machines;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3PendingStructurePattern;
import com.sirin.hk3gtl.common.recipe.Hk3ResearchProcessTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Blocks;
import java.util.LinkedHashMap;
import java.util.Locale;
import java.util.Map;

public final class Hk3WonderMachines {
    private static final Map<String, MultiblockMachineDefinition> MACHINES = new LinkedHashMap<>();
    private Hk3WonderMachines() {}
    public static MultiblockMachineDefinition get(String role) { return MACHINES.get(role); }
    public static void init() {
        MACHINES.put("W01", Hk3W01Machines.HALL);
        MACHINES.put("W02", Hk3W02Machines.MATRIX);
        MACHINES.put("W03", Hk3W03Machines.VOID_ANCHOR);
        for (var entry : Hk3WonderCatalog.ALL) {
            Hk3DualEnergyCosts.bindMachine(entry.controller(), Hk3DualEnergyCosts.COST_WONDER);
            if (MACHINES.containsKey(entry.role())) continue;
            boolean blueprint = Hk3WonderCatalog.hasBlueprint(entry.role());
            var definition = Hk3Gtl.REGISTRATE.multiblock(entry.controller(), holder -> entry.role().equals("W13")
                            ? new Hk3W13ResearchMachine(holder) : entry.role().equals("W14")
                            ? new Hk3W14WorldMachine(holder) : entry.role().equals("W08")
                            ? new com.sirin.hk3gtl.common.machine.w08.Hk3W08Machine(holder) : entry.role().equals("W10")
                            ? new com.sirin.hk3gtl.common.machine.w10.Hk3W10Machine(holder) : entry.role().equals("W12")
                            ? new com.sirin.hk3gtl.common.machine.w12.Hk3W12Machine(holder) : entry.role().equals("W05")||entry.role().equals("W06")||entry.role().equals("W07")||entry.role().equals("W11")||entry.role().equals("W15")
                            ? new Hk3AnimatedWonderMachine(holder,entry.role()) : new Hk3WonderMachine(holder, entry.role()))
                    .tier(entry.runtimeTier()).rotationState(RotationState.NON_Y_AXIS).allowFlip(false).allowExtendedFacing(false)
                    .recipeType(Hk3ResearchProcessTypes.get(entry.role())).noRecipeModifier()
                    .appearanceBlock(() -> Blocks.POLISHED_BLACKSTONE_BRICKS)
                    .pattern(def -> blueprint ? new Hk3WonderPattern(entry.role(),def)
                            : new Hk3PendingStructurePattern(def, "结构尚未开放，暂时无法成型或运行"))
                    .multiblockPreviewRenderer(false, blueprint)
                    .workableCasingRenderer(new ResourceLocation("hk3gtl", "block/casings/industrial_controller_shell"),
                            new ResourceLocation("hk3gtl", entry.role().equals("W04")
                                    ? "block/overlay/w04_appearance_0002_r7" : entry.role().equals("W11")
                                    ? "block/overlay/w11_puppetry_f5" : "block/overlay/"
                                    + entry.role().toLowerCase(Locale.ROOT) + "_appearance_0002_r18"))
                    .tooltips(Component.translatable("hk3gtl.machine." + entry.controller() + ".tooltip.0"),
                            Component.translatable("hk3gtl.machine." + entry.controller() + ".tooltip.1"),
                            Component.translatable("hk3gtl.machine.controller.research_required"),
                            Component.translatable("hk3gtl.machine.controller.voltage", Hk3Values.getVN(entry.runtimeTier())),
                            Component.translatable(blueprint ? "hk3gtl.machine." + entry.controller() + ".tooltip.structure"
                                    : "hk3gtl.machine.controller.structure_unavailable"))
                    .register();
            MACHINES.put(entry.role(), definition);
        }
    }
}
