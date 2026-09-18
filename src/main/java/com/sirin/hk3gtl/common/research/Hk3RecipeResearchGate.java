package com.sirin.hk3gtl.common.research;



import net.minecraft.resources.ResourceLocation;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

import java.util.Collections;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 配方-研究节点映射注册表（配方研究门槛系统）。
 *
 * <h3>职责</h3>
 * 将 GT 配方与研究节点绑定，实现"未完成研究则无法执行/查看配方"的门槛机制。
 *
 * <h3>核心机制</h3>
 * <ul>
 *   <li>配方注册时调用 {@link #bind} 记录 recipeId → researchNodeId 的映射</li>
 *   <li>机器匹配配方时查询 {@link #getRequiredResearch}，未完成研究则跳过</li>
 *   <li>客户端 JEI 查询时同样检查此表，隐藏未解锁配方</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增配方门槛 → 在 {@code Hk3RecipeAdderImpl} 注册配方后调用 {@code Hk3RecipeResearchGate.bind("recipeType", "recipeId", "R-AB-xxx")}</li>
 *   <li>移除门槛 → 删除对应的 bind 调用</li>
 *   <li>当前已绑定: hk3gtl_circuit_abyss_2→R-AB-012, _3→R-AB-018, _4→R-AB-022</li>
 * </ul>
 *
 * <h3>线程安全</h3>
 * 使用 ConcurrentHashMap，因为配方注册（Mixin 线程）和查询（服务端/客户端线程）可能并发。
 */
public final class Hk3RecipeResearchGate {

    private static final Logger LOGGER = LogUtils.getLogger();

    /** 配方ID → 研究节点ID 的映射表。Key: gtceu:recipeType/recipeId, Value: R-AB-xxx */
    private static final Map<ResourceLocation, String> RECIPE_TO_RESEARCH = new ConcurrentHashMap<>();

    /** 130 台时代遗留节点到 v0.3 节点的重定向，避免被裁剪机器留下孤儿门槛。 */
    private static final Map<String, String> LEGACY_NODE_REDIRECT = Map.ofEntries(
            Map.entry("R-IM-021", "R-IM-014"),
            Map.entry("R-IM-022", "R-IM-014"),
            Map.entry("R-QT-015", "R-QT-011"),
            Map.entry("R-QT-016", "R-QT-012"),
            Map.entry("R-QT-017", "R-QT-010"),
            Map.entry("R-QT-018", "R-QT-009"),
            Map.entry("R-QT-019", "R-QT-009"),
            Map.entry("R-QT-020", "R-QT-010"),
            Map.entry("R-QT-021", "R-QT-012"),
            Map.entry("R-QT-022", "R-QT-012"),
            Map.entry("R-FN-013", "R-FN-010"),
            Map.entry("R-FN-014", "R-FN-011"),
            Map.entry("R-FN-015", "R-FN-007"),
            Map.entry("R-FN-016", "R-FN-012"),
            Map.entry("R-FN-017", "R-FN-012"),
            Map.entry("R-FN-018", "R-FN-012"),
            Map.entry("R-FN-019", "R-FN-006"),
            Map.entry("R-FN-020", "R-GR-001")
    );

    private Hk3RecipeResearchGate() {}

    /**
     * 注册配方与研究节点的绑定关系。
     * 在配方注册后立即调用。
     *
     * @param recipeId    GT 配方的 ResourceLocation（如 gtceu:assembler/hk3gtl_circuit_abyss_2）
     * @param researchId  研究节点 ID（如 R-AB-011）
     */
    public static void bind(ResourceLocation recipeId, String researchId) {
        RECIPE_TO_RESEARCH.put(recipeId, normalizeResearchId(researchId));
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
        if (Hk3ResearchNodes.get(researchId) != null) {
            return researchId;
        }
        String redirected = LEGACY_NODE_REDIRECT.get(researchId);
        if (redirected != null && Hk3ResearchNodes.get(redirected) != null) {
            LOGGER.warn("[HK3GTL] 研究门槛节点 {} 已弃用，已重定向到 {}", researchId, redirected);
            return redirected;
        }
        LOGGER.warn("[HK3GTL] 研究门槛节点 {} 未注册，回退到 R-AB-001", researchId);
        return "R-AB-001";
    }

    /**
     * 查询配方是否需要研究门槛。
     */
    public static boolean requiresResearch(ResourceLocation recipeId) {
        return RECIPE_TO_RESEARCH.containsKey(recipeId);
    }

    /**
     * 获取配方所需的研究节点 ID。
     * @return 研究节点 ID，或 null（无门槛）
     */
    public static String getRequiredResearch(ResourceLocation recipeId) {
        return RECIPE_TO_RESEARCH.get(recipeId);
    }

    /**
     * 获取所有已注册的门槛映射（只读视图）。
     */
    public static Set<Map.Entry<ResourceLocation, String>> entries() {
        return Collections.unmodifiableSet(RECIPE_TO_RESEARCH.entrySet());
    }

    /**
     * 获取所有被锁定的配方 ID 集合。
     */
    public static Set<ResourceLocation> allGatedRecipeIds() {
        return Collections.unmodifiableSet(RECIPE_TO_RESEARCH.keySet());
    }

    public static int size() {
        return RECIPE_TO_RESEARCH.size();
    }
}
