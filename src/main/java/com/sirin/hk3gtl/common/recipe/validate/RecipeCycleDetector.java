package com.sirin.hk3gtl.common.recipe.validate;



import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.resources.ResourceLocation;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.Consumer;

/**
 * 配方可达性 / 死链检测器 —— 开发期保护栏。
 *
 * <h3>用途</h3>
 * 用 {@link #wrap(Consumer)} 包装 GT 配方 provider，记录每条配方的「产物 ← 其 hk3gtl 输入集」。
 * 全部配方注册完成后调用 {@link #scanAndLog()}，做可达性不动点分析，报告「无法从基础材料造出」的产物（真死链）。
 *
 * <h3>为什么不是图论找环</h3>
 * 工业链里「替代配方 / 回收配方 / 高产物消耗低产物」会让产物依赖图天然含环，但只要存在一条可引导路径就不是问题。
 * 因此判据应为「可造性」：某产物可达 ⇔ 存在至少一条配方其全部 hk3gtl 输入都可达。只有任何配方都无法引导的产物才是真死链。
 *
 * <h3>使用</h3>
 * <pre>{@code
 * RecipeCycleDetector.reset();
 * provider = RecipeCycleDetector.wrap(provider);
 * // ... 各 layer 注册 ...
 * RecipeCycleDetector.scanAndLog();
 * }</pre>
 */
public final class RecipeCycleDetector {

    private static final Logger LOGGER = LogUtils.getLogger();

    /** 产物 → 它的「每条配方输入集」列表（每个 Set 为一条配方的全部 hk3gtl 输入；多条配方之间是 OR 关系）。 */
    private static final Map<ResourceLocation, List<Set<ResourceLocation>>> OUTPUT_TO_RECIPES = new HashMap<>();

    /** 仅分析以此命名空间为目标的产物。 */
    private static final String NAMESPACE = Hk3Constants.MOD_ID;

    private RecipeCycleDetector() {}

    /** 清空累积的图（多次调用 addRecipes 时调用）。 */
    public static void reset() {
        OUTPUT_TO_RECIPES.clear();
    }

    /** 包装 provider，每次写入配方时静默记录。 */
    public static Consumer<FinishedRecipe> wrap(Consumer<FinishedRecipe> upstream) {
        return recipe -> {
            try {
                record(recipe);
            } catch (Throwable t) {
                // 容错：检测器问题绝不阻碍正常注册流程
                LOGGER.debug("[HK3GTL] cycle-detector record skipped for {}: {}",
                        recipe == null ? "?" : recipe.getId(), t.getMessage());
            }
            upstream.accept(recipe);
        };
    }

    /**
     * 可达性不动点扫描：报告无法从基础材料造出的 hk3gtl 产物（真死链）。
     *
     * @return 不可达（死链）产物列表，按字典序
     */
    public static List<ResourceLocation> scanAndLog() {
        Set<ResourceLocation> reachable = computeReachable();

        List<ResourceLocation> deadlocked = new ArrayList<>();
        for (ResourceLocation out : OUTPUT_TO_RECIPES.keySet()) {
            if (!reachable.contains(out)) {
                deadlocked.add(out);
            }
        }
        deadlocked.sort((a, b) -> a.toString().compareTo(b.toString()));

        if (deadlocked.isEmpty()) {
            LOGGER.info("[HK3GTL] 配方可达性检测：{} 个 hk3gtl 产物全部可从基础材料造出，无死链 ✓",
                    OUTPUT_TO_RECIPES.size());
        } else {
            LOGGER.warn("[HK3GTL] ⚠ 配方可达性检测：发现 {} 个无法造出的产物（真死链）", deadlocked.size());
            for (ResourceLocation out : deadlocked) {
                LOGGER.warn("[HK3GTL]   死链产物: {} —— 缺失输入: {}", out, missingInputsHint(out, reachable));
            }
            LOGGER.warn("[HK3GTL] 请为上述产物补一条「输入全部可达」的配方，或让现有配方的某个输入改走可达材料。");
        }
        return deadlocked;
    }

    // ════════════════════════════════════════════════════════
    //  内部实现
    // ════════════════════════════════════════════════════════

    /** 计算可达集：基础物(无配方产出的 hk3gtl 输入)为种子，迭代加入「存在一条全输入可达的配方」的产物。 */
    private static Set<ResourceLocation> computeReachable() {
        Set<ResourceLocation> outputs = OUTPUT_TO_RECIPES.keySet();
        Set<ResourceLocation> reachable = new HashSet<>();

        // 种子：作为输入出现、但没有任何配方产出的 hk3gtl 物 = 世界可直接获得的基础物（如原始崩坏粒子、矿物等）。
        for (List<Set<ResourceLocation>> recipes : OUTPUT_TO_RECIPES.values()) {
            for (Set<ResourceLocation> in : recipes) {
                for (ResourceLocation id : in) {
                    if (!outputs.contains(id)) {
                        reachable.add(id);
                    }
                }
            }
        }

        boolean changed = true;
        while (changed) {
            changed = false;
            for (Map.Entry<ResourceLocation, List<Set<ResourceLocation>>> e : OUTPUT_TO_RECIPES.entrySet()) {
                ResourceLocation out = e.getKey();
                if (reachable.contains(out)) {
                    continue;
                }
                for (Set<ResourceLocation> recipeInputs : e.getValue()) {
                    if (reachable.containsAll(recipeInputs)) { // 空集亦满足：无 hk3gtl 输入 = 基础配方，可直接引导
                        reachable.add(out);
                        changed = true;
                        break;
                    }
                }
            }
        }
        return reachable;
    }

    /** 给死链产物挑一条「缺失最少」的配方，列出其尚不可达的输入，便于定位。 */
    private static String missingInputsHint(ResourceLocation out, Set<ResourceLocation> reachable) {
        List<Set<ResourceLocation>> recipes = OUTPUT_TO_RECIPES.get(out);
        if (recipes == null || recipes.isEmpty()) {
            return "(无配方)";
        }
        Set<ResourceLocation> best = null;
        int bestMissing = Integer.MAX_VALUE;
        for (Set<ResourceLocation> in : recipes) {
            int missing = 0;
            for (ResourceLocation id : in) {
                if (!reachable.contains(id)) {
                    missing++;
                }
            }
            if (missing < bestMissing) {
                bestMissing = missing;
                best = in;
            }
        }
        List<String> missingList = new ArrayList<>();
        if (best != null) {
            for (ResourceLocation id : best) {
                if (!reachable.contains(id)) {
                    missingList.add(id.toString());
                }
            }
        }
        missingList.sort(String::compareTo);
        return missingList.toString();
    }

    /** 解析单条 FinishedRecipe，提取 hk3gtl:* 输入/输出，按「每条配方一个输入集」记录。 */
    private static void record(FinishedRecipe recipe) {
        if (recipe == null) return;
        JsonObject json = new JsonObject();
        recipe.serializeRecipeData(json);

        Set<ResourceLocation> inputs = new HashSet<>();
        Set<ResourceLocation> outputs = new HashSet<>();

        // 输入/输出各自只在自己的顶层子树内提取（GT 的输出项也用 ingredient:{item} 序列化，不能全树搜索）。
        extractScoped(json, "inputs", inputs);
        extractScoped(json, "tickInputs", inputs);
        extractScoped(json, "outputs", outputs);
        extractScoped(json, "tickOutputs", outputs);
        // 原版/其它配方风格：顶层 ingredients/ingredient/key → 输入；result/results → 输出
        extractScoped(json, "ingredients", inputs);
        extractScoped(json, "ingredient", inputs);
        extractScoped(json, "key", inputs);
        extractScoped(json, "result", outputs);
        extractScoped(json, "results", outputs);

        // 仅保留本模产物/原料，避免把 minecraft/gtceu/gtlcore 物当成需要被本模配方满足的节点
        inputs.removeIf(rl -> !NAMESPACE.equals(rl.getNamespace()));
        outputs.removeIf(rl -> !NAMESPACE.equals(rl.getNamespace()));

        if (outputs.isEmpty()) {
            return;
        }
        // 同一产物可能由多条配方产出；每条配方的输入集作为一个 OR 分支独立记录。
        for (ResourceLocation out : outputs) {
            // 产物自身不计入输入（防止「需要自己」的伪条件阻断可达，例如并行/保留型配方）。
            Set<ResourceLocation> recipeInputs = new HashSet<>(inputs);
            recipeInputs.remove(out);
            OUTPUT_TO_RECIPES.computeIfAbsent(out, k -> new ArrayList<>()).add(recipeInputs);
        }
    }

    /**
     * 仅在顶层字段 {@code field} 的子树内递归提取物品 id（不跨字段）。
     * 这样 inputs 子树只贡献输入、outputs 子树只贡献输出，杜绝输入/输出串用。
     */
    private static void extractScoped(JsonObject json, String field, Set<ResourceLocation> sink) {
        if (json.has(field)) {
            extractItemFromAny(json.get(field), sink);
        }
    }

    /** 从任意 JsonElement 提取所有 "item"/"id" 字符串作为物品 id。 */
    private static void extractItemFromAny(JsonElement element, Set<ResourceLocation> sink) {
        if (element == null || element.isJsonNull()) return;
        if (element.isJsonObject()) {
            JsonObject obj = element.getAsJsonObject();
            tryAddString(obj, "item", sink);
            tryAddString(obj, "id", sink);
            for (Map.Entry<String, JsonElement> e : obj.entrySet()) {
                if (e.getValue().isJsonObject() || e.getValue().isJsonArray()) {
                    extractItemFromAny(e.getValue(), sink);
                }
            }
        } else if (element.isJsonArray()) {
            for (JsonElement entry : element.getAsJsonArray()) {
                extractItemFromAny(entry, sink);
            }
        } else if (element.isJsonPrimitive() && element.getAsJsonPrimitive().isString()) {
            tryParse(element.getAsString(), sink);
        }
    }

    private static void tryAddString(JsonObject obj, String key, Set<ResourceLocation> sink) {
        if (obj.has(key) && obj.get(key).isJsonPrimitive() && obj.get(key).getAsJsonPrimitive().isString()) {
            tryParse(obj.get(key).getAsString(), sink);
        }
    }

    private static void tryParse(String raw, Set<ResourceLocation> sink) {
        if (raw == null || raw.isEmpty() || raw.indexOf(':') < 0) return;
        try {
            sink.add(new ResourceLocation(raw));
        } catch (Exception ignored) {
            // 非合法 RL 直接跳过
        }
    }

    /** 仅供测试与诊断用：返回当前累积的产物数量。 */
    public static int recordedNodeCount() {
        return OUTPUT_TO_RECIPES.size();
    }
}
