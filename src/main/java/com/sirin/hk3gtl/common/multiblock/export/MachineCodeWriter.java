package com.sirin.hk3gtl.common.multiblock.export;

import com.sirin.hk3gtl.common.constants.Hk3Constants;
import java.util.Locale;
import net.minecraft.resources.ResourceLocation;

import java.util.Map;

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


