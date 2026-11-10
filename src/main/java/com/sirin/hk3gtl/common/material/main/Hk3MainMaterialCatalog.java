package com.sirin.hk3gtl.common.material.main;

/**
 * 【文件职责】维护十六阶主材料身份、工业线及实体工序形态；不依赖游戏注册表，不自动生成加工旁路。
 * 【变更记录 #1】2026-10-17 16:25:14（第 1 次备注 · 修订165）
 * - 删除：无；原魂钢八步主线及既有注册身份保留。
 * - 新增：HBV至CEV材料目录、专属阶段形态、稳定物品路径和严格参数检查。
 * - 修改：材料身份与物品注册、加工配方分层；目录只描述实体身份，不把工序说明当作执行证据。
 * - 用途：由主材料物品、生产和消费者共享同一目录；配对及有限服役通过明确阶段区分，不引入无限批次状态。
 */

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

public final class Hk3MainMaterialCatalog {
    private static final List<Form> STANDARD_FORMS = List.of(
            new Form("billet", "标准坯", "Billet", "经本级工艺及质检后取得的实体标准坯，不自动附加熔炼配方"),
            new Form("plate", "板", "Plate", "完成本级专属成板工序的机械机壳及部件用板材"),
            new Form("rod", "棒", "Rod", "经本级独立成形工序加工的承力棒材"),
            new Form("fine_wire", "复合细线", "Composite Fine Wire", "由本级基材与导电前驱经拉制及功能处理制成的复合导体"),
            new Form("ring", "环", "Ring", "经本级成形及界面处理的密封或承力环件"),
            new Form("foil", "箔", "Foil", "经本级展薄及功能涂覆制成的薄层材料"),
            new Form("frame", "框架组件", "Frame Component", "机器部件使用的实体框架组件；普通物品，不是新增方块"),
            new Form("rejected_batch", "拒收批", "Rejected Batch", "未通过本级复核的实体批料，必须经有损分选回收"),
            new Form("classified_scrap", "分类废料", "Classified Scrap", "按本级来源分类的废料，不直接返还完整板材或部件"),
            new Form("recovered_fraction", "回收组分", "Recovered Fraction", "有损分离后的可用组分，须补充新料并重新制备"),
            new Form("unrecoverable_tailings", "不可回收尾料", "Unrecoverable Tailings", "工序及拆解损失的不可逆尾料，不提供逆向合成完整主材的入口"));

    private static final List<Entry> ENTRIES = List.of(
            new Entry(15, "HBV", "abyss_impregnated_soulium", "海渊浸渍魂钢", "Abyss Impregnated Soulium",
                    List.of("MAX初混坯", "MAX浸渍坯", "崩坏能量产浸渍坯"), "N01/N07/N08/N12"),
            new Entry(16, "HCV", "constraint_gradient_composite", "约束梯度复合材", "Constraint Gradient Composite",
                    List.of("陶瓷浸渍浆", "耐蚀界面层坯", "梯度压力复合坯"), "N11/N15/N12"),
            new Entry(17, "HRV", "resonance_oriented_lattice", "谐振取向晶格材", "Resonance Oriented Lattice",
                    List.of("功能纳米分散前体", "定向晶种生长坯", "取向整形晶格坯"), "N08/N18/N12"),
            new Entry(18, "HDV", "ultradense_loadbearing_soulium", "超致密承压魂钢", "Ultradense Loadbearing Soulium",
                    List.of("热等静压预制坯", "均匀化退火坯", "应力释放承压坯"), "N06/N12/N25"),
            new Entry(19, "QSV", "superposed_laminate_matrix", "叠态层压母材", "Superposed Laminate Matrix",
                    List.of("导体箔网层", "绝缘介质层", "层序压合坯"), "N14/N15/N18"),
            new Entry(20, "QCV", "coherent_interconnect_grid", "相干互连栅格材", "Coherent Interconnect Grid",
                    List.of("相干导体微栅", "低温介质涂覆坯", "隔离封装栅格坯"), "N14/N17/N18"),
            new Entry(21, "QEV", "paired_entangled_lattice", "纠缠配对晶格材", "Paired Entangled Lattice",
                    List.of("独立A晶种坯", "独立B晶种坯", "同步配对坯", "整对时效坯"), "N18/双晶制备"),
            new Entry(22, "QAV", "anchored_superlattice_structure", "锚定超晶格承力材", "Anchored Superlattice Structure",
                    List.of("定向约束涂层坯", "三轴锚定承力坯", "锚场固化坯"), "N15/N18/精密定位"),
            new Entry(23, "IMV", "imaginary_phase_transfer_ceramic", "虚数相转移陶瓷母材", "Imaginary Phase Transfer Ceramic",
                    List.of("陶瓷前驱浆", "受控相转移坯", "淬火除杂陶瓷坯"), "N15/相转移前体"),
            new Entry(24, "ICV", "imaginary_coupled_energy_band", "虚数耦合导能带", "Imaginary Coupled Energy Band",
                    List.of("高导基带", "多界面陶瓷浸渍带", "低温隔离封装带"), "N14/N17/低温介质"),
            new Entry(25, "IRV", "imaginary_reconstructed_alloy", "虚数重构母合金", "Imaginary Reconstructed Alloy",
                    List.of("分类重构前料", "补料调成合金坯", "重构熔合退火坯"), "N25/N26/新料补给"),
            new Entry(26, "IWV", "worldweave_multiaxial_composite", "织界多轴复合材", "Worldweave Multiaxial Composite",
                    List.of("陶瓷增强层", "导体增强层", "承力增强层", "修复增强层", "四层多轴共固化坯"), "N12/N13/N14/N15"),
            new Entry(27, "WFV", "worldforming_gradient_fiber", "构界梯度纤维材", "Worldforming Gradient Fiber",
                    List.of("实体增强纤维", "实测梯度处理纤维", "构型铺设坯"), "N22/N32/构型分解"),
            new Entry(28, "WSV", "worldstabilizing_confinement_shell", "稳界约束壳材", "Worldstabilizing Confinement Shell",
                    List.of("约束封隔前体", "纤维封隔多层坯", "疲劳老化复核坯"), "N06/N15/N30"),
            new Entry(29, "CIV", "civilization_quadrisystem_matrix", "文明四系统统合母材", "Civilization Quadrisystem Matrix",
                    List.of("独立导能系模块", "独立约束系模块", "独立重构系模块", "独立认知系模块", "四系共固化坯"), "N31四系独立支线"),
            new Entry(30, "CEV", "perennial_service_composite", "恒续服役复合母材", "Perennial Service Composite",
                    List.of("可维修功能层", "维修层复合坯", "人工老化服役件", "可修复拆解态", "补料修复复核态"), "N13/N25/N26"));

    static {
        Set<String> keys = new LinkedHashSet<>();
        for (int i = 0; i < ENTRIES.size(); i++) {
            Entry entry = ENTRIES.get(i);
            if (entry.tier() != i + 15 || !keys.add(entry.key())) {
                throw new IllegalStateException("主材料目录电压顺序或身份重复：" + entry.key());
            }
        }
    }

    private Hk3MainMaterialCatalog() {}

    public static List<Entry> entries() {
        return ENTRIES;
    }

    public static Entry entry(int tier) {
        if (tier < 15 || tier > 30) throw new IllegalArgumentException("未知主材料电压：" + tier);
        return ENTRIES.get(tier - 15);
    }

    public static List<Form> standardForms() {
        return STANDARD_FORMS;
    }

    public static List<Form> forms(int tier) {
        return entry(tier).forms();
    }

    public static String itemPath(int tier, String form) {
        Entry entry = entry(tier);
        return entry.key() + "_" + entry.form(form).key();
    }

    public record Entry(int tier, String voltage, String key, String nameZh, String nameEn,
                        List<String> stages, String lines) {
        public Entry {
            if (tier < 15 || tier > 30) throw new IllegalArgumentException("未知主材料电压：" + tier);
            requireText(voltage, "电压名");
            requireText(key, "主材料身份");
            if (!key.matches("[a-z][a-z0-9]*(?:_[a-z0-9]+)*")) {
                throw new IllegalArgumentException("非法主材料身份：" + key);
            }
            requireText(nameZh, "中文名");
            requireText(nameEn, "英文名");
            requireText(lines, "工业线");
            if (stages == null || stages.isEmpty() || stages.size() > 8) {
                throw new IllegalArgumentException("主材料工序数量无效：" + key);
            }
            stages.forEach(stage -> requireText(stage, "工序形态"));
            stages = List.copyOf(stages);
        }

        public int index() {
            return tier;
        }

        public List<Form> forms() {
            List<Form> forms = new ArrayList<>(STANDARD_FORMS);
            for (int i = 0; i < stages.size(); i++) {
                forms.add(new Form("stage_" + (i + 1), stages.get(i), "Process Intermediate " + (i + 1),
                        "本级实体工序形态：" + stages.get(i) + "；加工和复核由对应配方执行"));
            }
            return List.copyOf(forms);
        }

        public Form form(String key) {
            if (key == null) throw new IllegalArgumentException("主材料形态不得为空");
            return forms().stream().filter(form -> form.key().equals(key)).findFirst()
                    .orElseThrow(() -> new IllegalArgumentException("未知主材料形态：" + voltage + "/" + key));
        }

        public String processDescription() {
            return String.join(" → ", stages) + " → 本级质检及专属成板";
        }
    }

    public record Form(String key, String nameZh, String nameEn, String description) {
        public Form {
            requireText(key, "形态身份");
            requireText(nameZh, "形态中文名");
            requireText(nameEn, "形态英文名");
            requireText(description, "形态说明");
        }
    }

    private static void requireText(String value, String field) {
        if (value == null || value.isBlank()) throw new IllegalArgumentException(field + "不得为空");
    }
}
