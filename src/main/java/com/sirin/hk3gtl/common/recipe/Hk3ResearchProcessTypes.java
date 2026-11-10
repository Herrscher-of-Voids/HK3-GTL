package com.sirin.hk3gtl.common.recipe;



import com.gregtechceu.gtceu.api.recipe.GTRecipeType;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.gregtechceu.gtceu.api.capability.recipe.IO;
import java.util.*;

/**
 * 【变更记录 #1】2026-09-29 · 修订101。
 * 删除：无。新增：独立工艺类型；修改：八台合并设备回到已批准职责。
 * 用途：可先实现配方，不注册未经审批的控制器、结构、占地或建筑。
 */
/**
 * 【变更记录 #2】2026-09-29 23:37:35（内测5修订101）
 * 删除：本轮被替代的单前置或旧提示分支；其余历史保留。
 * 新增／修改：注册待接设备的配方类型，保留合并工艺职责，不创建未经审批的机器。
 * 用途：补足研究接线并如实保留未接物理执行器及结构审批边界。
 * 追溯：logs/research-mainline-r101；R101_FINAL_RECORD。
 */
public final class Hk3ResearchProcessTypes {
    private static final Map<String,GTRecipeType> TYPES=load();
    private Hk3ResearchProcessTypes() {}
    private static Map<String,GTRecipeType> load() {
        Map<String,GTRecipeType> map=new LinkedHashMap<>();
        map.put("GT_ASSEMBLER",GTRecipeTypes.ASSEMBLER_RECIPES);map.put("GT_MIXER",GTRecipeTypes.MIXER_RECIPES);
        map.put("GT_CHEMICAL",GTRecipeTypes.CHEMICAL_RECIPES);
        map.put("I01-1",Hk3IndustrialRecipeTypes.COLLECTION);map.put("I02",Hk3IndustrialRecipeTypes.SPECTRUM_ANALYSIS);
        map.put("I03",Hk3IndustrialRecipeTypes.LIQUID_REFINING);map.put("I04",Hk3IndustrialRecipeTypes.STABILIZATION);
        map.put("I05",Hk3IndustrialRecipeTypes.REGENERATION);map.put("I06",Hk3IndustrialRecipeTypes.FUEL_BLENDING);
        map.put("I07",Hk3IndustrialRecipeTypes.CALIBRATION);map.put("I17",Hk3IndustrialRecipeTypes.CONCENTRATION);
        List<String> roles=new ArrayList<>(List.of("I01-2","I01-3","I01-4"));
        for(int i=8;i<=45;i++)if(i!=17)roles.add(String.format(Locale.ROOT,"I%02d",i));
        for(String role:roles) {
            var ports=Hk3ResearchProcessPorts.get(role);
            map.put(role,GTRecipeTypes.register("industrial_process_"+role.toLowerCase(Locale.ROOT).replace('-','_'),"multiblock")
                    .setMaxIOSize(ports.itemsIn(),ports.itemsOut(),ports.fluidsIn(),ports.fluidsOut()).setEUIO(isGenerator(role)?IO.OUT:IO.IN));
        }
        return Collections.unmodifiableMap(map);
    }
    public static GTRecipeType get(String role) {
        var type=TYPES.get(role);if(type==null)throw new IllegalArgumentException("Unknown process role "+role);return type;
    }
    public static void init() {}
    public static boolean isGenerator(String role){return Hk3ResearchProcessEnergy.isGenerator(role);}
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
