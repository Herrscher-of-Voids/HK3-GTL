package com.sirin.hk3gtl.test.research;

import com.google.gson.*;
import com.sirin.hk3gtl.common.research.Hk3ResearchRuntimeComparison;

/**
 * 【文件职责】验证实际配方审计会拒绝失去研究门槛、模板或耗能的配置。
 * 【变更记录 #1】2026-09-30 00:57:59（第1次备注 · 内测5修订103）
 * 删除：无。新增：运行时配方缺失、空标签、能耗和非消耗模板差异回归。
 * 修改：纳入check；用途：检查审计失败语义，不冒充Minecraft真实加载测试。
 */
/**
 * 【变更记录 #2】2026-09-30 01:42:00（第2次备注 · 内测5修订106）
 * - 删除：无。新增：0.2倍率预期、二次缩时、零耗时和发电豁免比较检查。
 * - 修改：继续严格比较定义；用途：防止以适配倍率为由跳过耗时核验。
 */
public final class ResearchRuntimeComparisonTest {
    private static int checks;
    public static void main(String[] args) {
        JsonObject expected=JsonParser.parseString("""
            {"id":"hk3gtl:analysis/copy","type":"fixture:type",
             "definition":{"duration":1200,"eu":536870912,"catalyst":{"item":"fixture:blueprint","chance":0}},
             "gates":["RN-HBD"],"resolved_inputs":{"items":["fixture:substrate"],"fluids":["fixture:reagent"]},
             "resolved_outputs":{"items":["fixture:copy"],"fluids":["fixture:spent"]},"empty_ingredients":[]}
            """).getAsJsonObject();
        check(Hk3ResearchRuntimeComparison.compare(expected,expected.deepCopy()).isEmpty(),"unchanged snapshot");
        check(Hk3ResearchRuntimeComparison.compare(expected,null).contains("missing_recipe"),"removed recipe");
        var bad=expected.deepCopy();bad.add("gates",new JsonArray());
        check(Hk3ResearchRuntimeComparison.compare(expected,bad).contains("mismatch:gates"),"cannot erase research gate");
        bad=expected.deepCopy();bad.getAsJsonObject("definition").addProperty("eu",0);
        check(Hk3ResearchRuntimeComparison.compare(expected,bad).contains("mismatch:definition"),"cannot make energy free");
        bad=expected.deepCopy();bad.getAsJsonObject("definition").getAsJsonObject("catalyst").addProperty("chance",10000);
        check(Hk3ResearchRuntimeComparison.compare(expected,bad).contains("mismatch:definition"),"cannot consume blueprint template");
        bad=expected.deepCopy();bad.getAsJsonArray("empty_ingredients").add("input:fluid:0");
        check(Hk3ResearchRuntimeComparison.compare(expected,bad).contains("empty_ingredients"),"empty tag is not a usable input");
        check(Hk3ResearchRuntimeComparison.compare(bad,bad.deepCopy()).contains("empty_ingredients"),"two equally broken tags cannot pass");
        bad=expected.deepCopy();bad.getAsJsonObject("resolved_outputs").addProperty("items","unexpected");
        check(Hk3ResearchRuntimeComparison.compare(expected,bad).contains("mismatch:resolved_outputs"),"changed resolved items");
        for(String key:new String[]{"id","type","definition","gates","resolved_inputs","resolved_outputs","empty_ingredients"}) {
            bad=expected.deepCopy();bad.remove(key);
            check(!Hk3ResearchRuntimeComparison.compare(expected,bad).isEmpty(),"missing field "+key);
        }
        var scaled=expected.deepCopy();
        scaled.getAsJsonObject("definition").addProperty("duration",240);
        check(Hk3ResearchRuntimeComparison.compare(scaled,scaled.deepCopy()).isEmpty(),"serialized 0.2 multiplier matches");
        check(Hk3ResearchRuntimeComparison.compare(scaled,expected).contains("mismatch:definition"),"raw duration cannot silently pass");
        bad=scaled.deepCopy();bad.getAsJsonObject("definition").addProperty("duration",48);
        check(Hk3ResearchRuntimeComparison.compare(scaled,bad).contains("mismatch:definition"),"double scaling rejected");
        bad=scaled.deepCopy();bad.getAsJsonObject("definition").addProperty("duration",0);
        check(Hk3ResearchRuntimeComparison.compare(scaled,bad).contains("mismatch:definition"),"zero duration rejected");
        check(Hk3ResearchRuntimeComparison.compare(expected,scaled).contains("mismatch:definition"),"exempt generator cannot be scaled");
        check(expected.getAsJsonObject("definition").get("duration").getAsInt()==1200,"source duration retained");
        check(expected.getAsJsonArray("gates").size()==1,"comparison preserves source");
        System.out.println("ResearchRuntimeComparisonTest: "+checks+" checks passed; not a live game acceptance");
    }
    private static void check(boolean ok,String message){checks++;if(!ok)throw new AssertionError(message);}
}
