package com.sirin.hk3gtl.common.multiblock.pattern;

/** 2026-10-30（修订182）：I40–I45进入原位接口与完整严格Pattern白名单；数据、权限和旅行能力不由仓室或结构批准授予。 */

import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.machine.multiblock.PartAbility;
import com.gregtechceu.gtceu.api.pattern.BlockPattern;
import com.gregtechceu.gtceu.api.pattern.TraceabilityPredicate;
import com.sirin.hk3gtl.common.recipe.Hk3ResearchProcessPlans;

import java.util.HashSet;
import java.util.Locale;
import java.util.Set;



 






public final class Hk3LateIndustrialPatterns {
     
 






    public static final Set<String> IDS = Set.of("i19", "i20", "i21", "i22", "i23", "i24", "i25", "i26", "i27", "i28", "i29", "i30", "i31", "i32", "i33",
            "i34", "i35", "i36", "i37", "i38", "i39", "i40", "i41", "i42", "i43", "i44", "i45");

    private Hk3LateIndustrialPatterns() {}

    public static BlockPattern create(MultiblockMachineDefinition definition, String id) {
        if (!IDS.contains(id)) throw new IllegalArgumentException("未批准高阶工业结构：" + id);
        var data = Hk3ApprovedArchitecture.get(id);
        var required = requiredGroups(id.toUpperCase(Locale.ROOT));
        var itemIn = ability(PartAbility.IMPORT_ITEMS, required.contains("item_input"));
        var itemOut = ability(PartAbility.EXPORT_ITEMS, required.contains("item_output"));
        var fluidIn = ability(PartAbility.IMPORT_FLUIDS, required.contains("fluid_input"));
        var fluidOut = ability(PartAbility.EXPORT_FLUIDS, required.contains("fluid_output"));
        var universal = Hk3InterfacePredicates.interfaces(itemIn.or(itemOut).or(fluidIn).or(fluidOut));
        return new Hk3LargeStructurePattern(definition, data, universal);
    }

    private static TraceabilityPredicate ability(PartAbility ability, boolean required) {
        var result = Hk3InterfacePredicates.abilities(ability).setPreviewCount(required ? 1 : 0);
        return required ? result.setMinGlobalLimited(1) : result;
    }

    private static Set<String> requiredGroups(String role) {
        Set<String> groups = new HashSet<>();
        for (var plan : Hk3ResearchProcessPlans.all()) {
            if (!plan.role().equals(role)) continue;
            if (!plan.inputs().isEmpty() || !plan.catalysts().isEmpty()) groups.add("item_input");
            if (!plan.outputs().isEmpty()) groups.add("item_output");
            if (!plan.fluidInputs().isEmpty()) groups.add("fluid_input");
            if (!plan.fluidOutputs().isEmpty()) groups.add("fluid_output");
        }
        return groups;
    }
}
