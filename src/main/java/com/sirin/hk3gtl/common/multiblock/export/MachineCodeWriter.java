package com.sirin.hk3gtl.common.multiblock.export;


/**
 * 【文件职责】
 * - 维护 MachineCodeWriter 的核心功能实现。
 * - 关键调用链：由上层系统入口调用 -> 本文件核心方法 -> 下游模块。
 *
 * 【变更记录】2026-05-19
 * - 删除：
 *   1) 初始归档备注：自 v0.3 基线梳理，无本次 diff。
 * - 新增：
 *   1) 新增统一变更备注块，便于后续维护与审计追踪。
 * - 修改：
 *   1) 未改动业务逻辑，仅补充文件级职责与维护注释模板。
 * - 用途：
 *   1) 帮助维护者快速理解文件职责、变更背景与风险点。
 *
 * 【段内说明】
 * - 复杂方法补充“干什么 / 边界 / 线程侧”精简中文注释。
 */
/**
 * 【变更记录 #3】2026-10-31 17:42:29（第 3 次备注 · 内测5修订189）
 * - 删除：依赖服务器默认区域设置的大小写转换。
 * - 新增：Locale.ROOT固定大小写规则。
 * - 修改：所有生成标识符均使用固定区域设置，避免土耳其语环境产生非法注册字段。
 * - 用途：保持不同服务器生成的Java草稿一致；未确定的工艺仍保留原有人工确认占位。
 */
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import java.util.Locale;
import net.minecraft.resources.ResourceLocation;

import java.util.Map;

/** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
/** 中文说明：该处说明已按当前代码行为整理。*/
/**
 * 变更记录 #1 · 2026-09-24 16:45:00 · 内测5修订66。
 * 删除：稳定、再生、浓缩被推断为通用精炼。新增：正式工艺类型映射。
 * 修改：按注册ID顺序匹配；用途：防止后续手动结构导出重新引入错误配方关联。
 *
 * 变更记录 #2 · 2026-09-24 19:40:00 · 内测5修订68。
 * 修改：生成的控制器渲染路径统一指向新版 default_set overlay，避免新旧贴图风格回退。
 */
public final class MachineCodeWriter {

    private MachineCodeWriter() {}

    public static String render(ExportContext ctx) {
        String machineId = sanitizeMachineId(ctx.exportName);
        String constant = machineId.toUpperCase(Locale.ROOT);
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
        sb.append("        .recipeType(").append(recipeType).append(")\n");
        sb.append("        .appearanceBlock(").append(appearance).append(")\n");
        sb.append("        .pattern(").append(patternClass).append("::createPattern)\n");
        sb.append("        .workableCasingRenderer(\n");
        sb.append("                new ResourceLocation(Hk3Constants.MOD_ID, \"block/casings/")
                .append(extractCasingPath(ctx.legend)).append("\"),\n");
        sb.append("                new ResourceLocation(Hk3Constants.MOD_ID, \"block/overlay/default_set\"))\n");
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

    /** 按机器 ID 推断完整配方类型引用；未命中时保留待人工确认的占位符。 */
    private static String guessRecipeType(String machineId) {
        if (machineId.contains("absorption") || machineId.contains("collection")) {
            return "com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes.COLLECTION";
        }
        if (machineId.contains("regeneration")) return "com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes.REGENERATION";
        if (machineId.contains("stabilization")) return "com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes.STABILIZATION";
        if (machineId.contains("fuel_blending")) return "com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes.FUEL_BLENDING";
        if (machineId.contains("calibration")) return "com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes.CALIBRATION";
        if (machineId.contains("concentration")) return "com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes.CONCENTRATION";
        if (machineId.contains("fractionation")) {
            return "com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes.LIQUID_REFINING";
        }
        if (machineId.contains("spectrum") || machineId.contains("analysis")) {
            return "com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes.SPECTRUM_ANALYSIS";
        }
        if (machineId.contains("network") || machineId.contains("injector")) {
            return "com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes.NETWORK_INJECTION";
        }
        if (machineId.contains("research") && machineId.contains("matrix")) {
            return "Hk3RecipeTypes.ABYSS_RESEARCH_ANALYSIS_RECIPES";
        }
        return "/* TODO_RECIPE_TYPE */";
    }

    /** 从图例中挑选 X（机壳）的方块引用作为 appearanceBlock 入参 */
    private static String resolveAppearance(Map<Character, ResourceLocation> legend) {
        ResourceLocation casing = legend.get('X');
        if (casing == null) {
            return "/* TODO_APPEARANCE_BLOCK */";
        }
        if (Hk3Constants.MOD_ID.equals(casing.getNamespace()) && casing.getPath().startsWith("casing_")) {
            return "CasingBlocks." + casing.getPath().toUpperCase(Locale.ROOT) + ".get()";
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
        String id = raw.toLowerCase(Locale.ROOT)
                .replaceAll("[^a-z0-9_]+", "_")
                .replaceAll("_+", "_")
                .replaceAll("^_+|_+$", "");
        if (id.isEmpty()) return "generated_machine";
        if (!Character.isLetter(id.charAt(0))) return "generated_" + id;
        return id;
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。

// 【变更记录 · 修订162】2026-10-17 14:40:05：删除导出器对旧魂钢冶炼类型的自动推断，未确定工艺继续留人工待确认占位。
