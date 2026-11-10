package com.sirin.hk3gtl.common.research;

/**
 * 【文件职责／本轮边界】加载100题实际EU/t及材料敏感度，校验数值，不以目录存在代替执行接线。
 * 【变更记录 #1】2026-09-29 21:06:40（第 1 次编号备注 · 内测5修订100）
 * 删除：取消已被批准规则替代的研究个人独占、旧数值或在线限定分支；历史备注与其他系统保留。
 * 新增／修改：加载100题实际EU/t及材料敏感度，校验数值，不以目录存在代替执行接线。
 * 用途：接通实际证据→付款→研究完成与权限检查；不授予缺真实证据的课题。
 * 边界：编译和账本测试不代表游戏验收；S02至S05正式结构及未接线课题仍未完成。
 * 追溯：logs/research-mainline-r100；R100_FINAL_RECORD。
 */

/** 【变更记录 · 内测5修订100】2026-09-29：落实已批准研究费用、三公式及离线账户规则。 */

import com.google.gson.JsonParser;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** 中文说明：该处说明已按当前代码行为整理。*/
public final class Hk3ResearchPlans {
    /** 中文说明：该处说明已按当前代码行为整理。*/
    public record Material(String tag, long count, double sensitivity) {
        public Material(String tag, long count) { this(tag, count, 1.0); }
        public Material {
            if (!Double.isFinite(sensitivity) || sensitivity < 0 || sensitivity > 1) throw new IllegalArgumentException("Invalid sensitivity");
            if (tag == null || !tag.matches("[a-z0-9_.-]+:[a-z0-9_/.-]+") || count < 1)
                throw new IllegalArgumentException("Invalid material cost");
        }
    }
    /** 点数为整数、时间为基础tick；英文/中文课题名由lang键展示。 / Integer points and base ticks; topic names use language keys. */
    public record Plan(String id, long points, long ticks, String evidence, String result, List<Material> materials, long eut) {
        public Plan {
            if (points < 1 || ticks < 1 || eut < 1 || materials.isEmpty()) throw new IllegalArgumentException("Invalid plan");
            materials = List.copyOf(materials);
        }
        public String nameKey() { return "hk3gtl.research.topic." + id.toLowerCase(Locale.ROOT); }
    }
    private Hk3ResearchPlans() {}
    /** 顺序与已确认目录一致，返回不可变映射。 / Immutable plans in accepted catalog order. */
    public static Map<String, Plan> all() { return Holder.PLANS; }
    public static Plan get(String id) { return all().get(id); }
    private static final class Holder { private static final Map<String, Plan> PLANS = load(); }
    private static Map<String, Plan> load() {
        try (var in = Hk3ResearchPlans.class.getResourceAsStream("/data/hk3gtl/research/research_costs.json")) {
            if (in == null) throw new IllegalStateException("Missing research costs");
            var root = JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject();
            if (root.get("schema").getAsInt() != 1) throw new IllegalArgumentException("Unsupported costs version");
            Map<String, Plan> result = new LinkedHashMap<>();
            for (var element : root.getAsJsonArray("topics")) {
                var object = element.getAsJsonObject(); String id = object.get("id").getAsString();
                List<Material> materials = new ArrayList<>();
                for (var raw : object.getAsJsonArray("materials")) {
                    var material = raw.getAsJsonObject();
                    materials.add(new Material(material.get("tag").getAsString(), material.get("count").getAsLong(), material.get("sensitivity").getAsDouble()));
                }
                Plan plan = new Plan(id, object.get("points").getAsLong(), object.get("ticks").getAsLong(),
                        object.get("evidence").getAsString(), object.get("result").getAsString(), materials, object.get("eut").getAsLong());
                if (Hk3ResearchCatalog.bundled().get(id) == null || result.putIfAbsent(id, plan) != null)
                    throw new IllegalArgumentException("Unknown/duplicate research cost: " + id);
            }
            if (!result.keySet().equals(Hk3ResearchCatalog.bundled().topics().keySet()))
                throw new IllegalArgumentException("Incomplete research costs");
            return Collections.unmodifiableMap(result);
        } catch (Exception e) { throw new IllegalStateException("Cannot load research costs", e); }
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
