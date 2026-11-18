package com.sirin.hk3gtl.common.research;

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
        mergeOne(id, additions);
        copiesOf(id).forEach(copy -> mergeOne(copy, additions));
    }
    public static List<ResourceLocation> copiesOf(ResourceLocation id) {
        String prefix = "chemical_reactor/";
        return id.getPath().startsWith(prefix)
                ? List.of(new ResourceLocation(id.getNamespace(), "large_chemical_reactor/" + id.getPath().substring(prefix.length())))
                : List.of();
    }
    private static void mergeOne(ResourceLocation id, List<String> additions) {
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

