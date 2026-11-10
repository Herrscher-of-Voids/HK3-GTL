package com.sirin.hk3gtl.test.industry;

/**
 * 【文件职责】验证主材料电压身份、实体形态和目录不可变边界，并可导出待审批美术用物品清单。
 * 【变更记录 #1】2026-10-17 16:25:47（第 1 次备注 · 修订165）
 * - 删除：无，既有检查保留。
 * - 新增：十六电压、五十五工序、二百三十一物品的唯一身份和非法形态拒绝检查。
 * - 修改：检查直接调用纯目录，导出清单取同一运行数据，不复制注册表或从源码猜测身份。
 * - 用途：防止材料错阶及工序遗漏进入配方；不依赖游戏，不把此检查当作实际加工验收。
 */

import com.sirin.hk3gtl.common.material.main.Hk3MainMaterialCatalog;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.OffsetDateTime;
import java.time.ZoneId;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public final class MainMaterialCatalogTest {
    private MainMaterialCatalogTest() {}

    public static void main(String[] args) throws Exception {
        List<String> voltages = List.of("HBV", "HCV", "HRV", "HDV", "QSV", "QCV", "QEV", "QAV",
                "IMV", "ICV", "IRV", "IWV", "WFV", "WSV", "CIV", "CEV");
        Set<String> itemIds = new HashSet<>();
        int stageCount = 0;
        require(Hk3MainMaterialCatalog.entries().size() == 16, "主材料必须覆盖完整十六阶");
        for (int tier = 15; tier <= 30; tier++) {
            Hk3MainMaterialCatalog.Entry entry = Hk3MainMaterialCatalog.entry(tier);
            require(entry.tier() == tier && entry.index() == tier, "电压索引漂移");
            require(entry.voltage().equals(voltages.get(tier - 15)), "电压名映射漂移");
            int stages = tier == 21 ? 4 : tier == 26 || tier >= 29 ? 5 : 3;
            require(entry.stages().size() == stages, "独立支线或有限服役阶段遗漏：" + entry.voltage());
            stageCount += stages;
            require(entry.forms().size() == 11 + stages, "形态清单不完整");
            for (Hk3MainMaterialCatalog.Form form : entry.forms()) {
                String path = Hk3MainMaterialCatalog.itemPath(tier, form.key());
                require(itemIds.add(path), "重复材料实体：" + path);
                require(!path.equals(entry.key()), "不能注册没有实体形态的抽象基础材料");
            }
            int checkedTier = tier;
            reject(() -> Hk3MainMaterialCatalog.itemPath(checkedTier, "stage_0"));
            reject(() -> Hk3MainMaterialCatalog.itemPath(checkedTier, "stage_01"));
            reject(() -> Hk3MainMaterialCatalog.itemPath(checkedTier, "stage_" + (stages + 1)));
            reject(() -> Hk3MainMaterialCatalog.itemPath(checkedTier, "block"));
            reject(() -> Hk3MainMaterialCatalog.itemPath(checkedTier, null));
        }
        require(stageCount == 55 && itemIds.size() == 231, "整族物品总量漂移");
        reject(() -> Hk3MainMaterialCatalog.entry(14));
        reject(() -> Hk3MainMaterialCatalog.entry(31));
        rejectMutation(() -> Hk3MainMaterialCatalog.entries().clear());
        rejectMutation(() -> Hk3MainMaterialCatalog.entry(15).stages().clear());
        rejectMutation(() -> Hk3MainMaterialCatalog.forms(15).clear());
        List<String> sourceStages = new ArrayList<>(List.of("实体前驱"));
        Hk3MainMaterialCatalog.Entry copied = new Hk3MainMaterialCatalog.Entry(15, "HBV", "test_material",
                "测试材料", "Test Material", sourceStages, "测试支线");
        sourceStages.clear();
        require(copied.stages().size() == 1, "外部可变列表污染了目录");
        if (args.length == 1) {
            Path output = Path.of(args[0]);
            if (output.getParent() != null) Files.createDirectories(output.getParent());
            Files.writeString(output, manifest(), StandardCharsets.UTF_8);
        }
        System.out.println("主材料目录检查通过：16阶、55工序中间件、231实体物品；非法身份与可变列表均被拒绝。");
    }

    private static String manifest() {
        StringBuilder json = new StringBuilder("{\n  \"schema\":1,\n  \"created_at\":");
        json.append(quoted(OffsetDateTime.now(ZoneId.of("Asia/Hong_Kong")).toString()));
        json.append(",\n  \"revision\":165,\n  \"scope\":\"主材料实体身份、双语显示及待审批美术清单；不是配方或游戏验收\",")
                .append("\n  \"art_status\":\"pending_approval_not_installed\",\n  \"material_count\":16,\n  \"item_count\":231,\n  \"items\":[\n");
        boolean first = true;
        for (Hk3MainMaterialCatalog.Entry entry : Hk3MainMaterialCatalog.entries()) {
            for (Hk3MainMaterialCatalog.Form form : entry.forms()) {
                if (!first) json.append(",\n");
                first = false;
                String path = Hk3MainMaterialCatalog.itemPath(entry.tier(), form.key());
                String nameZh = form.key().startsWith("stage_")
                        ? entry.nameZh() + "·" + form.nameZh() : entry.nameZh() + form.nameZh();
                json.append("    {\"id\":").append(quoted("hk3gtl:" + path))
                        .append(",\"translation_key\":").append(quoted("item.hk3gtl." + path))
                        .append(",\"tier\":").append(entry.tier())
                        .append(",\"voltage\":").append(quoted(entry.voltage()))
                        .append(",\"material_key\":").append(quoted(entry.key()))
                        .append(",\"material_name_zh\":").append(quoted(entry.nameZh()))
                        .append(",\"material_name_en\":").append(quoted(entry.nameEn()))
                        .append(",\"form\":").append(quoted(form.key()))
                        .append(",\"name_zh\":").append(quoted(nameZh))
                        .append(",\"name_en\":").append(quoted(entry.nameEn() + " " + form.nameEn()))
                        .append(",\"description\":").append(quoted(form.description()))
                        .append(",\"industrial_lines\":").append(quoted(entry.lines()))
                        .append(",\"process_description\":").append(quoted(entry.processDescription()))
                        .append("}");
            }
        }
        return json.append("\n  ]\n}\n").toString();
    }

    private static String quoted(String value) {
        return "\"" + value.replace("\\", "\\\\").replace("\"", "\\\"")
                .replace("\n", "\\n").replace("\r", "\\r") + "\"";
    }

    private static void require(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }

    private static void reject(Runnable operation) {
        try {
            operation.run();
            throw new AssertionError("非法主材料参数未被拒绝");
        } catch (IllegalArgumentException expected) {
            require(expected.getMessage() != null, "非法参数缺少明确说明");
        }
    }

    private static void rejectMutation(Runnable operation) {
        try {
            operation.run();
            throw new AssertionError("主材料目录仍可被外部修改");
        } catch (UnsupportedOperationException expected) {
            // 不可变目录应当拒绝外部修改。
        }
    }
}
