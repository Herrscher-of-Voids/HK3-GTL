package com.sirin.hk3gtl.common.recipe;



import com.gregtechceu.gtceu.api.recipe.GTRecipeType;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.capability.recipe.ItemRecipeCapability;
import com.gregtechceu.gtceu.api.capability.recipe.FluidRecipeCapability;
import org.gtlcore.gtlcore.common.data.GTLRecipeTypes;
import com.sirin.hk3gtl.common.worldbubble.Hk3WorldRuntimeCatalog;
import net.minecraft.network.chat.Component;
import java.util.*;
public final class Hk3ResearchProcessTypes {
    private static final Map<String,GTRecipeType> TYPES=load();
    private Hk3ResearchProcessTypes() {}
    private static Map<String,GTRecipeType> load() {
        Map<String,GTRecipeType> map=new LinkedHashMap<>();
        map.put("GT_ASSEMBLER",GTRecipeTypes.ASSEMBLER_RECIPES);map.put("GT_MIXER",GTRecipeTypes.MIXER_RECIPES);
        map.put("GT_CHEMICAL",GTRecipeTypes.CHEMICAL_RECIPES);
        map.put("GT_LARGE_CHEMICAL",GTRecipeTypes.LARGE_CHEMICAL_RECIPES);
        map.put("GT_CHEMICAL_BATH",GTRecipeTypes.CHEMICAL_BATH_RECIPES);
        map.put("GT_LASER_ENGRAVER",GTRecipeTypes.LASER_ENGRAVER_RECIPES);
        map.put("GT_CUTTER",GTRecipeTypes.CUTTER_RECIPES);
        map.put("GT_FORMING_PRESS",GTRecipeTypes.FORMING_PRESS_RECIPES);
        map.put("GT_CANNER",GTRecipeTypes.CANNER_RECIPES);
        map.put("GT_FLUID_SOLIDIFIER",GTRecipeTypes.FLUID_SOLIDFICATION_RECIPES);
        map.put("GT_PACKER",GTRecipeTypes.PACKER_RECIPES);
        map.put("GT_VACUUM",GTRecipeTypes.VACUUM_RECIPES);
        map.put("GT_COMPRESSOR",GTRecipeTypes.COMPRESSOR_RECIPES);
        map.put("GT_CENTRIFUGE",GTRecipeTypes.CENTRIFUGE_RECIPES);
        map.put("GT_BENDER",GTRecipeTypes.BENDER_RECIPES);
        map.put("GT_BLAST",GTRecipeTypes.BLAST_RECIPES);
        map.put("GTL_SUPRACHRONAL_ASSEMBLY_LINE",GTLRecipeTypes.SUPRACHRONAL_ASSEMBLY_LINE_RECIPES);
        map.put("GTL_PRECISION_ASSEMBLER",GTLRecipeTypes.PRECISION_ASSEMBLER_RECIPES);
        map.put("GTL_CIRCUIT_ASSEMBLY_LINE",GTLRecipeTypes.CIRCUIT_ASSEMBLY_LINE_RECIPES);
        map.put("GTL_SPS",GTLRecipeTypes.SPS_CRAFTING_RECIPES);
        map.put("NETWORK_INJECTION",Hk3IndustrialRecipeTypes.NETWORK_INJECTION);
        map.put("I01-1",Hk3IndustrialRecipeTypes.COLLECTION);map.put("I02",Hk3IndustrialRecipeTypes.SPECTRUM_ANALYSIS);
        map.put("I03",Hk3IndustrialRecipeTypes.LIQUID_REFINING);map.put("I04",Hk3IndustrialRecipeTypes.STABILIZATION);
        map.put("I05",Hk3IndustrialRecipeTypes.REGENERATION);map.put("I06",Hk3IndustrialRecipeTypes.FUEL_BLENDING);
        map.put("I07",Hk3IndustrialRecipeTypes.CALIBRATION);map.put("I17",Hk3IndustrialRecipeTypes.CONCENTRATION);
        List<String> roles=new ArrayList<>(List.of("I01-2","I01-3","I01-4"));
        for(int i=8;i<=45;i++)if(i!=17)roles.add(String.format(Locale.ROOT,"I%02d",i));
        for(int i=1;i<=15;i++)roles.add(String.format(Locale.ROOT,"W%02d",i));
        roles.add("H01");
        for(String role:roles) {
            var ports=Hk3ResearchProcessPorts.get(role);
            map.put(role,GTRecipeTypes.register("industrial_process_"+role.toLowerCase(Locale.ROOT).replace('-','_'),"multiblock")
                    .setMaxIOSize(ports.itemsIn(),ports.itemsOut(),ports.fluidsIn(),ports.fluidsOut()).setEUIO(isGenerator(role)?IO.OUT:IO.IN));
        }
        map.forEach((role,type)->{
            var ports=Hk3ResearchProcessPorts.get(role);
            type.setMaxIOSize(Math.max(type.getMaxInputs(ItemRecipeCapability.CAP),ports.itemsIn()),
                    Math.max(type.getMaxOutputs(ItemRecipeCapability.CAP),ports.itemsOut()),
                    Math.max(type.getMaxInputs(FluidRecipeCapability.CAP),ports.fluidsIn()),
                    Math.max(type.getMaxOutputs(FluidRecipeCapability.CAP),ports.fluidsOut()));
        });
        var mining = map.get("I26");
        mining.setRecipeUI(new Hk3WorldMiningRecipeUI(mining));
        mining.setMaxTooltips(6)
                .addDataInfo(data -> Component.translatable("hk3gtl.recipe.world_mining.package",
                        Hk3WorldRuntimeCatalog.SAMPLING.itemKinds(), Hk3WorldRuntimeCatalog.SAMPLING.fluidKinds()).getString())
                .addDataInfo(data -> Component.translatable("hk3gtl.recipe.world_mining.route").getString())
                .addDataInfo(data -> Component.translatable("hk3gtl.recipe.world_mining.archive").getString());
        return Collections.unmodifiableMap(map);
    }
    public static GTRecipeType of(Hk3ResearchProcessPlans.Plan plan) {
        return get(plan.role());
    }
    public static GTRecipeType[] machineTypes(String role) {
        return new GTRecipeType[]{get(role)};
    }
    public static GTRecipeType get(String role) {
        var type=TYPES.get(role);if(type==null)throw new IllegalArgumentException("Unknown process role "+role);return type;
    }
    public static void init() {}
    public static boolean isGenerator(String role){return Hk3ResearchProcessEnergy.isGenerator(role);}
}

