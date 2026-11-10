package com.sirin.hk3gtl.common.research;




/** 中文说明：该处说明已按当前代码行为整理。*/
import net.minecraft.resources.ResourceLocation;
import com.sirin.hk3gtl.common.constants.Hk3Constants;

import java.util.List;
import java.util.LinkedHashSet;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 配方-研究节点映射注册表（配方研究门槛系统）。
 *
 * <h3>职责</h3>
 * 将 GT 配方与现行团队课题绑定；未完成研究不能执行，JEI保留配方和门槛提示。
 *
 * <h3>核心机制</h3>
 * <ul>
 *   <li>配方注册时调用 {@link #bind} 记录 recipeId → researchNodeId 的映射</li>
 *   <li>机器匹配和运行时查询全部前置，未完成研究则拒绝执行</li>
 *   <li>客户端 JEI 同样读取全部前置，显示各项研究状态</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增配方门槛 → 注册配方后调用 {@code bindAll}，显式列出现行课题</li>
 *   <li>移除门槛 → 删除对应的 bind 调用</li>
 *   <li>只接受当前课题目录和理之核心的有效电路解析分支</li>
 * </ul>
 *
 * <h3>线程安全</h3>
 * 使用 ConcurrentHashMap，因为配方注册（Mixin 线程）和查询（服务端/客户端线程）可能并发。
 */
/**
 * 【变更记录 #1】2026-09-29 23:37:35（内测5修订101）
 * 删除：本轮被替代的单前置或旧提示分支；其余历史保留。
 * 新增／修改：增加多前置绑定，保留旧单前置接口兼容。
 * 用途：补足研究接线并如实保留未接物理执行器及结构审批边界。
 * 追溯：logs/research-mainline-r101；R101_FINAL_RECORD。
 */
/** 【变更记录 #2】2026-10-01 21:11:08（修订150）：删除可互相失步的单项副表；新增每配方原子去重合并及不可变查询快照；修改后续bind不再覆盖bindAll的其他前置；用途：防止注册顺序或并发丢失研究条件，不映射旧研究也不授予完成。 */
/** 【变更记录 #3】2026-10-17 15:03:23（修订163）：删除旧研究节点及兼容重定向的配方入口；新增现行课题白名单与完整只读快照；修改非法门槛在注册时整体拒绝；用途：防止退役研究再次锁住现行配方，执行与显示共同读取全部前置。 */
public final class Hk3RecipeResearchGate {

    /** 配方ID到全部现行研究前置；每次发布的列表不可变。 */
    private static final Map<ResourceLocation, java.util.List<String>> ALL_REQUIREMENTS = new ConcurrentHashMap<>();

    private Hk3RecipeResearchGate() {}

    /**
     * 注册配方与研究节点的绑定关系。
     * 在配方注册后立即调用。
     *
     * @param recipeId    GT 配方的 ResourceLocation（如 gtceu:assembler/hk3gtl_circuit_abyss_2）
     * @param researchId  现行研究节点ID
     */
    public static void bind(ResourceLocation recipeId, String researchId) {
        merge(recipeId, List.of(normalizeResearchId(researchId)));
    }
    /** 修订101：同一配方的全部工艺前置，不允许后一次bind覆盖其他必要条件。 */
    public static void bindAll(String type, String id, java.util.List<String> requirements) {
        if (requirements.isEmpty()) return;
        var normalized = requirements.stream().map(Hk3RecipeResearchGate::normalizeResearchId).distinct().toList();
        for (String namespace : java.util.List.of("gtceu", Hk3Constants.MOD_ID)) {
            var key = new ResourceLocation(namespace,type+"/"+id);
            merge(key, normalized);
        }
    }
    /** 每个配方原子合并并发布不可变列表；并发或重复注册不能撤销已有条件。 */
    private static void merge(ResourceLocation id, List<String> additions) {
        ALL_REQUIREMENTS.compute(id, (key, previous) -> {
            var merged = new LinkedHashSet<String>();
            if (previous != null) merged.addAll(previous);
            merged.addAll(additions);
            return List.copyOf(merged);
        });
    }
    public static java.util.List<String> getAllRequiredResearch(ResourceLocation id) {
        return ALL_REQUIREMENTS.getOrDefault(id,java.util.List.of());
    }

    /**
     * 通过字符串 ID 注册绑定（配方注册阶段用，此时 ResourceLocation 通常是 gtceu:recipeType/recipeId）。
     */
    public static void bind(String recipeType, String recipeId, String researchId) {
        String path = recipeType + "/" + recipeId;
        String normalized = normalizeResearchId(researchId);
        bind(new ResourceLocation("gtceu", path), normalized);
        bind(new ResourceLocation(Hk3Constants.MOD_ID, path), normalized);
    }

    private static String normalizeResearchId(String researchId) {
        if (!isCurrentResearchId(researchId)) throw new IllegalArgumentException("配方引用非现行研究：" + researchId);
        return researchId;
    }

    /** 不信任旧完成标记或仅有RN前缀的未知课题。 */
    public static boolean isCurrentResearchId(String researchId) {
        return researchId != null && (Hk3ResearchCatalog.bundled().get(researchId) != null
                || researchId.startsWith(Hk3ResearchData.CIRCUIT_PREFIX)
                && Hk3ResearchData.CIRCUIT_TIERS.contains(researchId.substring(Hk3ResearchData.CIRCUIT_PREFIX.length())));
    }

    /** 导出全部条件，禁止核验或客户端只取第一项。 */
    public static Map<ResourceLocation, List<String>> snapshot() {
        return Map.copyOf(ALL_REQUIREMENTS);
    }

    /**
     * 查询配方是否需要研究门槛。
     */
    public static boolean requiresResearch(ResourceLocation recipeId) {
        return ALL_REQUIREMENTS.containsKey(recipeId);
    }

    /**
     * 获取所有被锁定的配方 ID 集合。
     */
    public static Set<ResourceLocation> allGatedRecipeIds() {
        return Set.copyOf(ALL_REQUIREMENTS.keySet());
    }

    public static int size() {
        return ALL_REQUIREMENTS.size();
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
