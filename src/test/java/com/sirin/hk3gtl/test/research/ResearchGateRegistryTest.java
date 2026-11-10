package com.sirin.hk3gtl.test.research;

import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import com.sirin.hk3gtl.common.research.Hk3ResearchCatalog;
import com.sirin.hk3gtl.common.research.Hk3RecipeAccess;
import com.sirin.hk3gtl.common.research.Hk3ResearchRequirementPolicy;
import com.sirin.hk3gtl.common.machine.Hk3RecipeCalculationHelper;
import com.sirin.hk3gtl.common.machine.ParallelData;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.resources.ResourceLocation;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

/** 【变更记录 #1】2026-10-17 15:07:20（修订163）：新增真实门槛注册表的退役拒绝、派生权限白名单与非法批次原子性回归，不操作游戏存档。 */
/** 【变更记录 #2】2026-11-04 00:12:20（第2次备注 · 内测5修订193）：删除无；新增真实GT配方合并的多前置去重、次方撤权、单方改ID、NBT续存及非法元数据拒绝回归；修改原任务覆盖共享规划器，不启动游戏或改存档。 */
/** 【变更记录 #3】2026-11-04 00:17:21（第3次备注 · 内测5修订193）：删除无；新增旧合并NBT缺权限拒绝、新空列表放行及既有完整液态列表兼容断言；修改同一回归任务验证暂停不改在途数据，不授予研究。 */
public final class ResearchGateRegistryTest {
    private static void check(boolean value, String message) {
        if (!value) throw new AssertionError(message);
    }

    public static void main(String[] args) throws java.io.IOException {
        net.minecraft.SharedConstants.tryDetectVersion();
        for (String id : Hk3ResearchCatalog.bundled().topics().keySet())
            check(Hk3RecipeResearchGate.isCurrentResearchId(id), "现行目录课题必须可绑定：" + id);
        for (String tier : List.of("ulv", "lv", "mv", "hv", "ev", "iv", "luv", "zpm", "uv", "uhv", "uev", "uiv", "uxv", "opv", "max"))
            check(Hk3RecipeResearchGate.isCurrentResearchId("RN-RCA/circuit/" + tier), "合法理之核心分支：" + tier);
        check(!Hk3RecipeResearchGate.isCurrentResearchId(null), "空课题不是合法权限");
        String type = "research_gate_registry_test";
        String name = "atomic_rejection";
        var key = new ResourceLocation("gtceu", type + "/" + name);
        Hk3RecipeResearchGate.bindAll(type, name, List.of("RN-CQS", "RN-WCP"));
        var before = Hk3RecipeResearchGate.snapshot();
        for (String invalid : List.of("R-AB-011", "R-IM-021", "R-FN-020", "RN-NOTREGISTERED", "RN-RCA/circuit/hbv", "RN-RCA/circuit/MAX", " ")) {
            try {
                Hk3RecipeResearchGate.bindAll(type, name, List.of("RN-HED", invalid));
                throw new AssertionError("非法门槛必须在注册期拒绝：" + invalid);
            } catch (IllegalArgumentException expected) {
                check(Hk3RecipeResearchGate.snapshot().equals(before), "失败不能写入任一命名空间：" + invalid);
            }
            try {
                Hk3RecipeResearchGate.bind(key, invalid);
                throw new AssertionError("单项入口不能恢复旧课题：" + invalid);
            } catch (IllegalArgumentException expected) {
                check(Hk3RecipeResearchGate.snapshot().equals(before), "单项拒绝不修改原绑定");
            }
        }
        Hk3RecipeResearchGate.bind(type, name, "RN-IAA");
        check(before.get(key).equals(List.of("RN-CQS", "RN-WCP")), "导出的旧快照不随注册变化");
        check(Hk3RecipeResearchGate.getAllRequiredResearch(key).equals(List.of("RN-CQS", "RN-WCP", "RN-IAA")), "所有前置必须保留");
        try {
            before.clear();
            throw new AssertionError("外部不能修改权限快照");
        } catch (UnsupportedOperationException expected) { }
        mergedRequirements();
        System.out.println("研究门槛注册回归通过：100课题、15个受限电路分支、旧节点拒绝、失败原子性及真实配方合并权限。");
    }

    private static void mergedRequirements() throws java.io.IOException {
        var first = recipe("first");
        var second = recipe("second");
        Hk3RecipeResearchGate.bind(first.id, "RN-CQS");
        Hk3RecipeResearchGate.bind(second.id, "RN-WCP");
        gates(first, "RN-IAA");
        gates(second, "RN-IAA", "RN-LES");
        var firstData = first.data.copy();
        var secondData = second.data.copy();
        var merged = merge(List.of(first, second), List.of(first.copy(), second.copy()));
        check(merged != null, "合法跨配方批次必须可以规划");
        var required = Hk3RecipeAccess.effectiveRequirements(merged);
        check(required.valid() && required.requirements().equals(List.of("RN-CQS", "RN-IAA", "RN-WCP", "RN-LES")),
                "注册表及全部批次前置必须去重保留");
        check(!Hk3ResearchRequirementPolicy.evaluate(required, id -> !id.equals("RN-WCP")).allowed(),
                "次方权限撤销必须阻止运行和续跑");
        check(Hk3ResearchRequirementPolicy.evaluate(required, id -> true).allowed(), "全部权限恢复才能续跑");
        check(first.data.equals(firstData) && second.data.equals(secondData), "合并不能修改注册原方元数据");
        var restored = recipe("restored");
        restored.data = reload(merged.data);
        check(Hk3RecipeAccess.effectiveRequirements(restored).equals(required), "NBT恢复后不能丢掉次方门槛");
        var transformed = first.copy();
        transformed.id = recipe("transformed").id;
        transformed.data = new CompoundTag();
        check(Hk3RecipeAccess.effectiveRequirements(merge(List.of(first), List.of(transformed)))
                .requirements().equals(List.of("RN-CQS", "RN-IAA")), "单方修改ID或数据后仍保留原方门槛");
        for (String invalid : List.of("RN-NOTREGISTERED", "R-AB-011")) {
            gates(second, invalid);
            check(merge(List.of(first, second), List.of(first.copy(), second.copy())) == null,
                    "后续配方非法权限不能变成无门槛：" + invalid);
        }
        second.data.putString(Hk3ResearchRequirementPolicy.METADATA_KEY, "RN-WCP");
        check(merge(List.of(first, second), List.of(first.copy(), second.copy())) == null, "错误NBT类型必须拒绝整批");

        var oldBatch = recipe("old_merged");
        oldBatch.data.putBoolean("hk3gtlMergedPlan", true);
        var saved = oldBatch.data.copy();
        var loaded = recipe("old_merged_loaded");
        loaded.data = reload(saved);
        check(!Hk3RecipeAccess.effectiveRequirements(loaded).valid() && Hk3RecipeAccess.blocks(loaded, null),
                "旧合并NBT读回缺权限列表时必须暂停，不能退回首配方");
        check(loaded.data.equals(saved), "拒绝旧批次不能清除或改写在途数据");
        var ordinary = recipe("no_gate");
        var noGate = merge(List.of(ordinary), List.of(ordinary.copy()));
        noGate.data.putBoolean("hk3gtlMergedPlan", true);
        check(Hk3RecipeAccess.effectiveRequirements(noGate).valid()
                        && !Hk3RecipeAccess.blocks(noGate, null), "新无门槛批次的显式空列表必须放行");
        gates(loaded, "RN-CQS", "RN-LES");
        check(Hk3RecipeAccess.effectiveRequirements(loaded).valid()
                        && Hk3RecipeAccess.effectiveRequirements(loaded).requirements().equals(List.of("RN-CQS", "RN-LES")),
                "旧液态批次已有完整权限列表时保持正常读取");
    }

    private static GTRecipe recipe(String name) {
        return new GTRecipe(null, new ResourceLocation("hk3gtl", "research_gate_registry_test/" + name),
                new HashMap<>(), new HashMap<>(), new HashMap<>(), new HashMap<>(),
                new HashMap<>(), new HashMap<>(), new HashMap<>(), new HashMap<>(),
                new ArrayList<>(), new ArrayList<>(), new CompoundTag(), 20, false);
    }
    private static CompoundTag reload(CompoundTag saved) throws java.io.IOException {
        var bytes = new java.io.ByteArrayOutputStream();
        net.minecraft.nbt.NbtIo.writeCompressed(saved, bytes);
        return net.minecraft.nbt.NbtIo.readCompressed(new java.io.ByteArrayInputStream(bytes.toByteArray()));
    }
    private static void gates(GTRecipe recipe, String... requirements) {
        var list = new ListTag();
        for (String id : requirements) list.add(StringTag.valueOf(id));
        recipe.data.put(Hk3ResearchRequirementPolicy.METADATA_KEY, list);
    }
    private static GTRecipe merge(List<GTRecipe> originals, List<GTRecipe> processed) {
        var parallels = new long[originals.size()];
        java.util.Arrays.fill(parallels, 1);
        return Hk3RecipeCalculationHelper.buildNormalRecipe(new ParallelData(originals, parallels, false, processed), null);
    }
}
