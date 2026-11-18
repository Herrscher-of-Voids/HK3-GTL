package com.sirin.hk3gtl.common.multiblock.export;

import com.sirin.hk3gtl.common.constants.Hk3Constants;
import java.util.Locale;
import net.minecraft.resources.ResourceLocation;

import java.util.LinkedHashSet;
import java.util.Map;
import java.util.Set;

public final class PatternCodeWriter {

    public static final String PATTERN_PACKAGE = "com.sirin.hk3gtl.common.multiblock.pattern";

    private PatternCodeWriter() {}

    /** 生成 {@code Hk3XxxPatternImpl.java} 正文 */
    public static String renderImpl(ExportContext ctx) {
        String implName = impleClassName(ctx.exportName);
        Set<String> extraImports = new LinkedHashSet<>();

        StringBuilder where = new StringBuilder();
        appendWhereClauses(ctx, where, extraImports);

        StringBuilder sb = new StringBuilder(4096);
        sb.append("package ").append(PATTERN_PACKAGE).append(";\n\n");

        sb.append("import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;\n");
        sb.append("import com.gregtechceu.gtceu.api.machine.multiblock.PartAbility;\n");
        sb.append("import com.gregtechceu.gtceu.api.pattern.BlockPattern;\n");
        sb.append("import com.gregtechceu.gtceu.api.pattern.FactoryBlockPattern;\n");
        sb.append("import com.gregtechceu.gtceu.api.pattern.Predicates;\n");
        for (String imp : extraImports) {
            sb.append("import ").append(imp).append(";\n");
        }
        sb.append('\n');

        sb.append("/**\n");
        sb.append(" * ").append(ctx.exportName).append(" 多方块 Pattern 实现（由 /hk3export 自动生成）。\n");
        sb.append(" *\n");
        sb.append(" * <p>源 controller: ").append(ctx.controllerId)
                .append(" @ ").append(ctx.controllerWorldPos.toShortString())
                .append("，朝向 ").append(ctx.controllerFacing).append("</p>\n");
        sb.append(" * <p>尺寸 W×H×D = ").append(ctx.width).append('x').append(ctx.height)
                .append('x').append(ctx.depth).append("；\n");
        sb.append(" * aisle[0] 为背面，aisle[depth-1] 为控制器前脸（与 Hk3AbsorptionTowerPattern 惯例一致）。</p>\n");
        if (!ctx.warnings.isEmpty()) {
            sb.append(" *\n * <h3>导出时产生的警告（需人工核对）</h3>\n");
            sb.append(" * <ul>\n");
            for (String w : ctx.warnings) {
                sb.append(" *   <li>").append(escapeJavadoc(w)).append("</li>\n");
            }
            sb.append(" * </ul>\n");
        }
        sb.append(" */\n");

        sb.append("public class ").append(implName).append(" {\n\n");
        sb.append("    public static BlockPattern createPattern(MultiblockMachineDefinition definition) {\n");
        appendAutoAbilities(sb, ctx.abilitySummary);
        sb.append("        return FactoryBlockPattern.start()\n");

        for (int z = 0; z < ctx.depth; z++) {
            sb.append("                .aisle(\n");
            for (int y = ctx.height - 1; y >= 0; y--) {
                String row = new String(ctx.grid[z][y]);
                sb.append("                        \"").append(row).append('"');
                if (y != 0) sb.append(',');
                sb.append('\n');
            }
            sb.append("                )\n");
        }

        sb.append("                .where('").append(SymbolAllocator.CONTROLLER_SYMBOL)
                .append("', Predicates.controller(Predicates.blocks(definition.getBlock())))\n");
        sb.append(where);
        sb.append("                .where('").append(SymbolAllocator.AIR_SYMBOL)
                .append("', Hk3InterfacePredicates.clearance())\n");
        sb.append("                .build();\n");
        sb.append("    }\n");
        sb.append("}\n");
        return sb.toString();
    }

    /** 生成 {@code Hk3XxxPattern.java} 门面类，直接继承 Impl */
    public static String renderFacade(ExportContext ctx) {
        String facade = className(ctx.exportName);
        String impl = impleClassName(ctx.exportName);
        return "package " + PATTERN_PACKAGE + ";\n\n"
                + "/**\n"
                + " * " + ctx.exportName + " 多方块 Pattern 门面类。\n"
                + " *\n"
                + " * <p>实际逻辑见 {@link " + impl + "}。</p>\n"
                + " */\n"
                + "public class " + facade + " extends " + impl + " {\n"
                + "}\n";
    }

    private static void appendWhereClauses(ExportContext ctx, StringBuilder sb, Set<String> extraImports) {
        for (Map.Entry<Character, ResourceLocation> e : ctx.legend.entrySet()) {
            char symbol = e.getKey();
            ResourceLocation id = e.getValue();
            HatchAbilityMap.Ability ab = ctx.abilityBySymbol.get(symbol);

            if (symbol == SymbolAllocator.HATCH_SYMBOL) {
                sb.append("                .where('").append(symbol).append("', interfaces)\n");
                continue;
            }

            if (ab != null) {
                sb.append("                .where('").append(symbol)
                        .append("', interfaces)\n");
                continue;
            }

            sb.append("                .where('").append(symbol)
                    .append("', Predicates.blocks(")
                    .append(formatBlockRef(id, extraImports))
                    .append(").or(interfaces))\n");
        }
    }

    private static void appendAutoAbilities(StringBuilder sb, HatchAbilityMap.Summary s) {
        sb.append("        var interfaces = Hk3InterfacePredicates.interfaces()");
        for (String ability : s.explicitAbilities().keySet()) {
            if (ability.equals("PARALLEL_HATCH") || ability.equals("MAINTENANCE")) continue;
            sb.append("\n                .or(Predicates.abilities(PartAbility.").append(ability).append("))");
        }
        sb.append(";\n");
    }

    /** 把方块注册名转为 Java 代码片段，必要时补充 import */
    private static String formatBlockRef(ResourceLocation id, Set<String> extraImports) {
        String ns = id.getNamespace();
        String path = id.getPath();

        if (Hk3Constants.MOD_ID.equals(ns) && path.startsWith("casing_")) {
            extraImports.add("com.sirin.hk3gtl.common.block.CasingBlocks");
            return "CasingBlocks." + path.toUpperCase(Locale.ROOT) + ".get()";
        }
        if ("minecraft".equals(ns)) {
            extraImports.add("net.minecraft.world.level.block.Blocks");
            return "Blocks." + path.toUpperCase(Locale.ROOT);
        }
        extraImports.add("net.minecraft.core.registries.BuiltInRegistries");
        extraImports.add("net.minecraft.resources.ResourceLocation");
        return "BuiltInRegistries.BLOCK.get(new ResourceLocation(\"" + ns + "\", \"" + path + "\"))";
    }

    public static String className(String exportName) {
        return "Hk3" + pascal(exportName) + "Pattern";
    }

    public static String impleClassName(String exportName) {
        return className(exportName) + "Impl";
    }

    private static String pascal(String raw) {
        String safe = raw.toLowerCase(Locale.ROOT).replaceAll("[^a-z0-9_]+", "_").replaceAll("_+", "_");
        StringBuilder out = new StringBuilder();
        for (String part : safe.split("_")) {
            if (part.isEmpty()) continue;
            out.append(Character.toUpperCase(part.charAt(0))).append(part.substring(1));
        }
        return out.length() == 0 ? "Generated" : out.toString();
    }

    private static String escapeJavadoc(String s) {
        return s.replace("*/", "* /");
    }
}
