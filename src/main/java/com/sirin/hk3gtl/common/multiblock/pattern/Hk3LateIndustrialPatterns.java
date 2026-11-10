package com.sirin.hk3gtl.common.multiblock.pattern;

/** 2026-10-30（修订182）：I40–I45进入原位接口与完整严格Pattern白名单；数据、权限和旅行能力不由仓室或结构批准授予。 */

import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.machine.multiblock.PartAbility;
import com.gregtechceu.gtceu.api.pattern.BlockPattern;
import com.gregtechceu.gtceu.api.pattern.Predicates;
import com.gregtechceu.gtceu.api.pattern.TraceabilityPredicate;
import com.sirin.hk3gtl.common.machine.multiblock.part.Hk3PartAbility;
import com.sirin.hk3gtl.common.recipe.Hk3ResearchProcessPlans;

import java.util.HashSet;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;



/**
 * 【文件职责】把十五台批准大结构的原位接口映射为真实能力，不改动建筑或添设接口。
 * 【变更记录 #1】2026-10-26 19:57:03（修订177）
 * 删除：无。新增：按工艺需求共享输入输出能力计数，维护、研究和服务接口可选。
 * 修改：EU由控制器玩家电网结算，能源标记保留填充壳，避免可选低阶仓分流高阶发电。
 * 用途：严格成型与真实IO接线；研究仓不授研究权限，暂定工况仍由执行策略关闭。
 */
public final class Hk3LateIndustrialPatterns {
    // 【变更记录 #2】2026-10-27（修订180）：I29–I33沿批准原位接口接入，复用既有严格成型。
/**
 * 【变更记录 #3】2026-10-27 22:31:22（第3次备注 · 内测5修订181）
 * - 删除：无，已有15台真实端口与严格成型行为保留。
 * - 新增：batch09五台批准建筑进入同一端口能力映射入口，I37继续排除。
 * - 修改：新增端口沿批准资源组别校验真实物品、流体、崩坏能与维护能力。
 * - 用途：只扩展批准结构身份，不增造接口，不因建筑批准开放暂定工艺。
 */
    public static final Set<String> IDS = Set.of("i19", "i20", "i21", "i22", "i23", "i24", "i25", "i26", "i27", "i28", "i29", "i30", "i31", "i32", "i33",
            "i34", "i35", "i36", "i38", "i39", "i40", "i41", "i42", "i43", "i44", "i45");

    private Hk3LateIndustrialPatterns() {}

    public static BlockPattern create(MultiblockMachineDefinition definition, String id) {
        if (!IDS.contains(id)) throw new IllegalArgumentException("未批准高阶工业结构：" + id);
        var data = Hk3ApprovedArchitecture.get(id);
        var required = requiredGroups(id.toUpperCase(Locale.ROOT));
        var itemIn = ability(PartAbility.IMPORT_ITEMS, required.contains("item_input"));
        var itemOut = ability(PartAbility.EXPORT_ITEMS, required.contains("item_output"));
        var fluidIn = ability(PartAbility.IMPORT_FLUIDS, required.contains("fluid_input"));
        var fluidOut = ability(PartAbility.EXPORT_FLUIDS, required.contains("fluid_output"));
        var filler = Predicates.blocks(Hk3StructureBlocks.require("hk3gtl:industrial_port_casing"));
        var research = Predicates.abilities(PartAbility.DATA_ACCESS, PartAbility.COMPUTATION_DATA_RECEPTION).setPreviewCount(0);
        var maintenance = Predicates.abilities(PartAbility.MAINTENANCE).setMaxGlobalLimited(1).setPreviewCount(0);
        var parallel = Predicates.abilities(PartAbility.PARALLEL_HATCH).setMaxGlobalLimited(1).setPreviewCount(0);
        // 修订214：物品、流体四种仓在全部接口共享；专用能力保留原入口与结算边界。
        var universal = itemIn.or(itemOut).or(fluidIn).or(fluidOut).or(filler);
        Map<String, TraceabilityPredicate> ports = new ConcurrentHashMap<>();
        Set<String> available = new HashSet<>();
        for (var port : data.ports()) {
            TraceabilityPredicate allowed = switch (port.group()) {
                case "item_input" -> itemIn;
                case "item_output" -> itemOut;
                case "fluid_input" -> fluidIn;
                case "fluid_output" -> fluidOut;
                case "item" -> itemIn.or(itemOut);
                case "fluid" -> fluidIn.or(fluidOut);
                case "input" -> itemIn.or(fluidIn);
                case "output" -> itemOut.or(fluidOut);
                case "research" -> research;
                case "maintenance" -> maintenance;
                case "service" -> parallel.or(maintenance);
                case "honkai_input" -> Predicates.abilities(Hk3PartAbility.HONKAI_ENERGY_INPUT).setPreviewCount(0);
                case "honkai_output" -> Predicates.abilities(Hk3PartAbility.HONKAI_ENERGY_OUTPUT).setPreviewCount(0);
                case "energy_input", "energy_output", "energy" -> filler;
                default -> throw new IllegalStateException("未定义高阶接口组：" + id + "/" + port.group());
            };
            if (ports.putIfAbsent(port.id(), allowed.or(universal)) != null)
                throw new IllegalStateException("高阶接口编号重复：" + id + "/" + port.id());
            switch (port.group()) {
                case "item" -> available.addAll(Set.of("item_input", "item_output"));
                case "fluid" -> available.addAll(Set.of("fluid_input", "fluid_output"));
                case "input" -> available.addAll(Set.of("item_input", "fluid_input"));
                case "output" -> available.addAll(Set.of("item_output", "fluid_output"));
                default -> available.add(port.group());
            }
        }
        if (!available.containsAll(required)) {
            required.removeAll(available);
            throw new IllegalStateException("批准结构缺少工艺所需接口，不得新增孤面板：" + id + "/" + required);
        }
        return new Hk3LargeStructurePattern(definition, data, ports);
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
