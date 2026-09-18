package com.sirin.hk3gtl.common.multiblock.export;



import com.sirin.hk3gtl.common.constants.Hk3Constants;
import net.minecraft.resources.ResourceLocation;

import java.util.Map;

/**
 * 生成 Hk3MachinesXxxStage 中用得到的"字段声明 + init() 注册片段"代码文本。
 *
 * <h3>输出结构</h3>
 * 两段代码：
 * <ol>
 *   <li>常量声明：{@code public static MultiblockMachineDefinition XXX;}</li>
 *   <li>init 片段：{@code XXX = registrate().multiblock(...) ... .register();}</li>
 * </ol>
 * 生成到单个 {@code .txt} 文件中，玩家复制到对应 Stage 类即可。
 *
 * <h3>推断规则</h3>
 * <ul>
 *   <li>机器 id：沿用导出名（小写下划线规范化）</li>
 *   <li>recipeType：尝试按 id 关键字匹配已知 RecipeType，否则留 {@code TODO_RECIPE_TYPE}</li>
 *   <li>appearanceBlock：优先挑选 X（机壳）对应的方块 id，否则 {@code TODO_APPEARANCE_BLOCK}</li>
 *   <li>rotationState：沿用扫描到的朝向；水平 → NON_Y_AXIS</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>扩展 {@link #guessRecipeType} 以支持更多机器 id → RecipeType 映射</li>
 *   <li>若机壳命名惯例变更：同步修改 {@link #resolveAppearance}</li>
 * </ul>
 */
public final class MachineCodeWriter {

    private MachineCodeWriter() {}

    public static String render(ExportContext ctx) {
        String machineId = sanitizeMachineId(ctx.exportName);
        String constant = machineId.toUpperCase();
        String patternClass = PatternCodeWriter.className(ctx.exportName);
        String recipeType = guessRecipeType(machineId);
        String appearance = resolveAppearance(ctx.legend);
        String rotationState = ctx.controllerFacing.getAxis().isHorizontal() ? "NON_Y_AXIS" : "ALL";

        StringBuilder sb = new StringBuilder(1024);
        sb.append("// ========== Hk3Machines<Stage>Impl.java 草稿 ==========\n");
        sb.append("// 来源：/hk3export ").append(ctx.exportName).append('\n');
        sb.append("// controller: ").append(ctx.controllerId).append('\n');
        sb.append("// 尺寸: ").append(ctx.width).append('x').append(ctx.height).append('x').append(ctx.depth).append('\n');
        sb.append("// 请把以下字段声明与 init() 片段复制到对应阶段的 Machines 类中\n\n");

        sb.append("// ── 字段声明 ──\n");
        sb.append("/** ").append(ctx.exportName).append(" 控制器 */\n");
        sb.append("public static MultiblockMachineDefinition ").append(constant).append(";\n\n");

        sb.append("// ── init() 片段 ──\n");
        sb.append(constant).append(" = registrate()\n");
        sb.append("        .multiblock(\"").append(machineId).append("\", Hk3WorkableMultiblockMachine::new)\n");
        sb.append("        .rotationState(RotationState.").append(rotationState).append(")\n");
        sb.append("        .recipeType(Hk3RecipeTypes.").append(recipeType).append(")\n");
        sb.append("        .appearanceBlock(").append(appearance).append(")\n");
        sb.append("        .pattern(").append(patternClass).append("::createPattern)\n");
        sb.append("        .workableCasingRenderer(\n");
        sb.append("                new ResourceLocation(Hk3Constants.MOD_ID, \"block/casings/")
                .append(extractCasingPath(ctx.legend)).append("\"),\n");
        sb.append("                new ResourceLocation(Hk3Constants.MOD_ID, \"block/overlay/default\"))\n");
        sb.append("        .tooltips(\n");
        sb.append("                Component.translatable(\"hk3gtl.machine.")
                .append(machineId).append(".tooltip.0\"),\n");
        sb.append("                Component.translatable(\"hk3gtl.machine.")
                .append(machineId).append(".tooltip.1\"))\n");
        sb.append("        .register();\n\n");

        sb.append("// ── 需要同步的语言键 ──\n");
        sb.append("// \"block.hk3gtl.").append(machineId).append("\": \"<中文名>\",\n");
        sb.append("// \"hk3gtl.machine.").append(machineId).append(".tooltip.0\": \"<说明>\",\n");
        sb.append("// \"hk3gtl.machine.").append(machineId).append(".tooltip.1\": \"<更多说明>\",\n");

        if (!ctx.rejectedBlocks.isEmpty()) {
            sb.append('\n');
            sb.append("// ── FIXME：选区内存在以下被拒方块（未写入 Pattern）──\n");
            for (ResourceLocation id : ctx.rejectedBlocks) {
                sb.append("//   - ").append(id).append('\n');
            }
        }

        return sb.toString();
    }

    /** 按机器 id 关键字推断 RecipeType；未命中时返回 TODO 占位 */
    private static String guessRecipeType(String machineId) {
        if (machineId.contains("absorption")) return "HONKAI_ABSORPTION_RECIPES";
        if (machineId.contains("condenser")) return "HONKAI_CONDENSATION_RECIPES";
        if (machineId.contains("smeltery")) return "SOULIUM_SMELTING_RECIPES";
        if (machineId.contains("research") && machineId.contains("matrix")) return "ABYSS_RESEARCH_ANALYSIS_RECIPES";
        return "/* TODO_RECIPE_TYPE */";
    }

    /** 从图例中挑选 X（机壳）的方块引用作为 appearanceBlock 入参 */
    private static String resolveAppearance(Map<Character, ResourceLocation> legend) {
        ResourceLocation casing = legend.get('X');
        if (casing == null) {
            return "/* TODO_APPEARANCE_BLOCK */";
        }
        if (Hk3Constants.MOD_ID.equals(casing.getNamespace()) && casing.getPath().startsWith("casing_")) {
            return "CasingBlocks." + casing.getPath().toUpperCase() + ".get()";
        }
        return "() -> BuiltInRegistries.BLOCK.get(new ResourceLocation(\""
                + casing.getNamespace() + "\", \"" + casing.getPath() + "\"))";
    }

    /** 提取机壳名（用于 workableCasingRenderer 贴图路径） */
    private static String extractCasingPath(Map<Character, ResourceLocation> legend) {
        ResourceLocation casing = legend.get('X');
        if (casing == null) return "TODO_CASING";
        if (Hk3Constants.MOD_ID.equals(casing.getNamespace()) && casing.getPath().startsWith("casing_")) {
            return casing.getPath();
        }
        return "TODO_CASING";
    }

    private static String sanitizeMachineId(String raw) {
        String id = raw.toLowerCase()
                .replaceAll("[^a-z0-9_]+", "_")
                .replaceAll("_+", "_")
                .replaceAll("^_+|_+$", "");
        if (id.isEmpty()) return "generated_machine";
        if (!Character.isLetter(id.charAt(0))) return "generated_" + id;
        return id;
    }
}
