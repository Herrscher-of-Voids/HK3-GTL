import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;

/**
 * 生成崩坏能吸收塔的 Java pattern 源文件。
 *
 * 目标结构：
 * - 21 x 21 x 48
 * - 控制器位于 Z=0, Y=1, X=10
 * - 仅前脸 3x3 区域允许放仓室，鱼大固定在控制器上方
 * - 整体为黑白紫配色的“巴黎铁塔顶着崩坏能水晶”
 */
public class GenerateAbsorptionTower {

    private static final int WIDTH = 21;
    private static final int HEIGHT = 48;
    private static final int DEPTH = 21;
    private static final int CENTER = 10;
    private static final int CONTROLLER_Z = 0;
    private static final int CONTROLLER_Y = 1;
    private static final int CONTROLLER_X = 10;

    private static final char[][][] GRID = new char[DEPTH][HEIGHT][WIDTH];

    public static void main(String[] args) throws IOException {
        fill(' ');

        buildFoundation();
        buildFrontFacade();
        buildLowerLegs();
        buildPrimaryDeck();
        buildMainTower();
        buildUpperTower();
        buildCrystalSeat();
        buildCrystalCore();
        placeControllerCluster();

        writePatternSource();
        verify();
    }

    private static void fill(char value) {
        for (char[][] slice : GRID) {
            for (char[] row : slice) {
                Arrays.fill(row, value);
            }
        }
    }

    private static void buildFoundation() {
        for (int z = 0; z < DEPTH; z++) {
            for (int x = 0; x < WIDTH; x++) {
                set(z, 0, x, 'B');
            }
        }

        // 基座边框与导能线
        for (int i = 0; i < WIDTH; i++) {
            set(0, 0, i, 'W');
            set(DEPTH - 1, 0, i, 'W');
            set(i, 0, 0, 'W');
            set(i, 0, WIDTH - 1, 'W');
        }
        for (int z = 2; z <= 18; z++) {
            set(z, 0, 5, 'P');
            set(z, 0, 15, 'P');
        }
        for (int x = 5; x <= 15; x++) {
            set(5, 0, x, 'P');
            set(15, 0, x, 'P');
        }
    }

    private static void buildFrontFacade() {
        // 前脸控制区周围的主装饰框
        for (int x = 6; x <= 14; x++) {
            set(0, 1, x, 'B');
            set(0, 2, x, 'B');
            set(0, 3, x, 'W');
            set(0, 4, x, 'Q');
        }
        for (int y = 1; y <= 6; y++) {
            set(0, y, 6, 'B');
            set(0, y, 14, 'B');
        }
        for (int x = 7; x <= 13; x++) {
            set(0, 5, x, 'P');
        }
        set(0, 6, 8, 'W');
        set(0, 6, 12, 'W');
        set(0, 6, 9, 'P');
        set(0, 6, 10, 'P');
        set(0, 6, 11, 'P');

        // 侧向延伸的门框，避免控制器显得贴在空气上
        for (int z = 1; z <= 3; z++) {
            set(z, 1, 7, 'B');
            set(z, 1, 13, 'B');
            set(z, 2, 7, 'W');
            set(z, 2, 13, 'W');
            set(z, 3, 8, 'P');
            set(z, 3, 12, 'P');
        }
    }

    private static void buildLowerLegs() {
        for (int y = 1; y <= 14; y++) {
            currentYValue = y;
            double t = (double) (y - 1) / 13.0;
            int front = lerp(2, 6, t);
            int back = 20 - front;
            int half = y <= 6 ? 2 : 1;

            placeLeg(front, front, half);
            placeLeg(20 - front, front, half);
            placeLeg(front, back, half);
            placeLeg(20 - front, back, half);

            if (y % 4 == 0) {
                for (int x = front + half + 1; x <= 20 - front - half - 1; x++) {
                    set(front + 1, y, x, 'W');
                    set(back - 1, y, x, 'W');
                }
                for (int z = front + half + 1; z <= back - half - 1; z++) {
                    set(z, y, front + 1, 'W');
                    set(z, y, 20 - front - 1, 'W');
                }
            }

            if (y == 6 || y == 10 || y == 14) {
                for (int x = front + 2; x <= 20 - front - 2; x++) {
                    set(front + 2, y, x, 'P');
                    set(back - 2, y, x, 'P');
                }
            }

            // 前后斜撑
            if (y >= 3 && y <= 12) {
                int braceStart = Math.max(3, front + 1);
                int braceEnd = Math.min(17, back - 1);
                int left = Math.min(9, braceStart + (y - 3) / 2);
                int right = Math.max(11, braceEnd - (y - 3) / 2);
                set(braceStart, y, left, 'I');
                set(braceStart, y, right, 'I');
                set(braceEnd, y, left, 'I');
                set(braceEnd, y, right, 'I');
            }
        }
    }

    private static void placeLeg(int xCenter, int zCenter, int half) {
        for (int dz = -half; dz <= half; dz++) {
            for (int dx = -half; dx <= half; dx++) {
                int z = zCenter + dz;
                int x = xCenter + dx;
                char block = (Math.abs(dx) == half || Math.abs(dz) == half) ? 'B' : 'W';
                set(z, currentY(), x, block);
            }
        }
    }

    private static int currentYValue;

    private static int currentY() {
        return currentYValue;
    }

    private static void buildPrimaryDeck() {
        for (int y = 15; y <= 18; y++) {
            currentYValue = y;
            for (int z = 3; z <= 17; z++) {
                for (int x = 3; x <= 17; x++) {
                    boolean edge = z == 3 || z == 17 || x == 3 || x == 17;
                    boolean innerEdge = z == 4 || z == 16 || x == 4 || x == 16;
                    if (edge) {
                        set(z, y, x, y == 16 ? 'Q' : 'B');
                    } else if (innerEdge) {
                        set(z, y, x, 'P');
                    } else if (y == 15 || y == 18) {
                        set(z, y, x, 'B');
                    } else if (z >= 6 && z <= 14 && x >= 6 && x <= 14) {
                        set(z, y, x, ((x + z + y) & 1) == 0 ? 'C' : 'E');
                    }
                }
            }
        }
    }

    private static void buildMainTower() {
        for (int y = 19; y <= 34; y++) {
            int half = y <= 28 ? 5 : 4;
            for (int z = CENTER - half; z <= CENTER + half; z++) {
                for (int x = CENTER - half; x <= CENTER + half; x++) {
                    boolean edge = z == CENTER - half || z == CENTER + half || x == CENTER - half || x == CENTER + half;
                    boolean corner = (z == CENTER - half || z == CENTER + half) && (x == CENTER - half || x == CENTER + half);
                    if (corner) {
                        set(z, y, x, 'U');
                    } else if (edge) {
                        set(z, y, x, (y % 3 == 0) ? 'P' : 'B');
                    } else if (x == CENTER || z == CENTER) {
                        set(z, y, x, (y % 4 == 0) ? 'E' : 'C');
                    } else if ((x == CENTER - 2 || x == CENTER + 2) && (z == CENTER - 2 || z == CENTER + 2) && y % 5 == 0) {
                        set(z, y, x, 'I');
                    }
                }
            }

            if (y % 4 == 1) {
                for (int x = CENTER - half; x <= CENTER + half; x++) {
                    set(CENTER - half, y, x, 'W');
                    set(CENTER + half, y, x, 'W');
                }
            }
        }
    }

    private static void buildUpperTower() {
        int[] halfSizes = {3, 3, 3, 2, 2, 2, 1};
        for (int i = 0; i < halfSizes.length; i++) {
            int y = 35 + i;
            int half = halfSizes[i];

            for (int z = CENTER - half; z <= CENTER + half; z++) {
                for (int x = CENTER - half; x <= CENTER + half; x++) {
                    boolean edge = z == CENTER - half || z == CENTER + half || x == CENTER - half || x == CENTER + half;
                    if (edge) {
                        set(z, y, x, (i % 2 == 0) ? 'B' : 'I');
                    } else if (x == CENTER && z == CENTER) {
                        set(z, y, x, 'E');
                    }
                }
            }

            if (half >= 2) {
                set(CENTER - half - 1, y, CENTER, 'c');
                set(CENTER + half + 1, y, CENTER, 'c');
                set(CENTER, y, CENTER - half - 1, 'c');
                set(CENTER, y, CENTER + half + 1, 'c');
            }

            if (y == 35) {
                for (int z = CENTER - 4; z <= CENTER + 4; z++) {
                    set(z, y, CENTER - 4, 'Q');
                    set(z, y, CENTER + 4, 'Q');
                }
                for (int x = CENTER - 4; x <= CENTER + 4; x++) {
                    set(CENTER - 4, y, x, 'Q');
                    set(CENTER + 4, y, x, 'Q');
                }
            }
        }
    }

    private static void buildCrystalSeat() {
        for (int z = CENTER - 2; z <= CENTER + 2; z++) {
            for (int x = CENTER - 2; x <= CENTER + 2; x++) {
                boolean edge = z == CENTER - 2 || z == CENTER + 2 || x == CENTER - 2 || x == CENTER + 2;
                boolean corner = (z == CENTER - 2 || z == CENTER + 2) && (x == CENTER - 2 || x == CENTER + 2);

                set(z, 42, x, edge ? 'Q' : 'U');
                set(z, 43, x, corner ? 'U' : edge ? 'g' : 'G');
            }
        }
        set(CENTER, 42, CENTER, 'E');
    }

    private static void buildCrystalCore() {
        for (int z = CENTER - 1; z <= CENTER + 1; z++) {
            for (int x = CENTER - 1; x <= CENTER + 1; x++) {
                set(z, 44, x, 'G');
                set(z, 45, x, 'G');
            }
        }

        set(CENTER, 44, CENTER, 'O');
        set(CENTER - 1, 44, CENTER, 'E');
        set(CENTER + 1, 44, CENTER, 'E');
        set(CENTER, 44, CENTER - 1, 'E');
        set(CENTER, 44, CENTER + 1, 'E');

        set(CENTER, 45, CENTER, 'E');
        set(CENTER, 46, CENTER, 'G');
        set(CENTER, 47, CENTER, 'P');
    }

    private static void placeControllerCluster() {
        // 固定前脸控制器与鱼大
        set(CONTROLLER_Z, CONTROLLER_Y, CONTROLLER_X, 'S');
        set(CONTROLLER_Z, CONTROLLER_Y + 1, CONTROLLER_X, 'F');

        // 仅允许这 7 个前脸位置替换为仓室
        set(CONTROLLER_Z, 0, 9, 'H');
        set(CONTROLLER_Z, 0, 10, 'H');
        set(CONTROLLER_Z, 0, 11, 'H');
        set(CONTROLLER_Z, 1, 9, 'H');
        set(CONTROLLER_Z, 1, 11, 'H');
        set(CONTROLLER_Z, 2, 9, 'H');
        set(CONTROLLER_Z, 2, 11, 'H');

        // 保证鱼大左右仍有结构/仓位支撑
        set(CONTROLLER_Z, 2, 8, 'B');
        set(CONTROLLER_Z, 2, 12, 'B');
    }

    private static void set(int z, int y, int x, char value) {
        if (z < 0 || z >= DEPTH || y < 0 || y >= HEIGHT || x < 0 || x >= WIDTH) {
            return;
        }
        GRID[z][y][x] = value;
    }

    private static int lerp(int start, int end, double t) {
        return (int) Math.round(start + (end - start) * t);
    }

    private static void verify() {
        for (int z = 0; z < DEPTH; z++) {
            for (int y = 0; y < HEIGHT; y++) {
                if (GRID[z][y].length != WIDTH) {
                    throw new IllegalStateException("Invalid row width at z=" + z + ", y=" + y);
                }
            }
        }
        System.out.println("Verified absorption tower grid: 21x21x48");
    }

    private static void writePatternSource() throws IOException {
        StringBuilder source = new StringBuilder();
        source.append("package com.sirin.hk3gtl.common.data;\n\n");
        source.append("import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;\n");
        source.append("import com.gregtechceu.gtceu.api.machine.multiblock.PartAbility;\n");
        source.append("import com.gregtechceu.gtceu.api.pattern.BlockPattern;\n");
        source.append("import com.gregtechceu.gtceu.api.pattern.FactoryBlockPattern;\n");
        source.append("import com.gregtechceu.gtceu.api.pattern.Predicates;\n");
        source.append("import net.minecraft.core.registries.BuiltInRegistries;\n");
        source.append("import net.minecraft.resources.ResourceLocation;\n");
        source.append("import net.minecraft.world.level.block.Blocks;\n\n");
        source.append("/**\n");
        source.append(" * 崩坏能吸收塔 21x21x48 结构 pattern。\n");
        source.append(" * 由 tools/GenerateAbsorptionTower.java 自动生成。\n");
        source.append(" */\n");
        source.append("public class Hk3AbsorptionTowerPattern {\n\n");
        source.append("    public static BlockPattern createPattern(MultiblockMachineDefinition definition) {\n");
        source.append("        return FactoryBlockPattern.start()\n");

        for (int z = 0; z < DEPTH; z++) {
            source.append("                        .aisle(  // Z=").append(z).append("\n");
            for (int y = 0; y < HEIGHT; y++) {
                source.append("                                \"").append(new String(GRID[z][y])).append("\"");
                if (y < HEIGHT - 1) {
                    source.append(",");
                }
                source.append("\n");
            }
            source.append("                        )\n");
        }

        source.append("                .where('S', Predicates.controller(Predicates.blocks(definition.getBlock())))\n");
        source.append("                .where('H', Predicates.blocks(Blocks.BLACK_CONCRETE)\n");
        source.append("                        .or(Predicates.abilities(PartAbility.IMPORT_ITEMS).setMaxGlobalLimited(1))\n");
        source.append("                        .or(Predicates.abilities(PartAbility.EXPORT_ITEMS).setMaxGlobalLimited(1))\n");
        source.append("                        .or(Predicates.abilities(PartAbility.INPUT_ENERGY).setMaxGlobalLimited(2))\n");
        source.append("                        .or(Predicates.abilities(PartAbility.INPUT_LASER).setMaxGlobalLimited(1))\n");
        source.append("                        .or(Predicates.abilities(PartAbility.PARALLEL_HATCH).setMaxGlobalLimited(1)))\n");
        source.append("                .where('F', Predicates.blocks(BuiltInRegistries.BLOCK.get(new ResourceLocation(\"expatternprovider\", \"fishbig\"))))\n");
        source.append("                .where('B', Predicates.blocks(Blocks.BLACK_CONCRETE))\n");
        source.append("                .where('W', Predicates.blocks(Blocks.WHITE_CONCRETE))\n");
        source.append("                .where('P', Predicates.blocks(Blocks.PURPLE_CONCRETE))\n");
        source.append("                .where('G', Predicates.blocks(Blocks.PURPLE_STAINED_GLASS))\n");
        source.append("                .where('g', Predicates.blocks(Blocks.PURPLE_STAINED_GLASS_PANE))\n");
        source.append("                .where('U', Predicates.blocks(Blocks.BLUE_CONCRETE))\n");
        source.append("                .where('Q', Predicates.blocks(Blocks.SMOOTH_QUARTZ_STAIRS))\n");
        source.append("                .where('C', Predicates.blocks(BuiltInRegistries.BLOCK.get(new ResourceLocation(\"gtlcore\", \"create_casing\"))))\n");
        source.append("                .where('E', Predicates.blocks(BuiltInRegistries.BLOCK.get(new ResourceLocation(\"kubejs\", \"eternity_coil_block\"))))\n");
        source.append("                .where('O', Predicates.blocks(Blocks.COMMAND_BLOCK))\n");
        source.append("                .where('I', Predicates.blocks(Blocks.IRON_BARS))\n");
        source.append("                .where('c', Predicates.blocks(Blocks.CHAIN))\n");
        source.append("                .where(' ', Predicates.any())\n");
        source.append("                .build();\n");
        source.append("    }\n");
        source.append("}\n");

        Path sourcePath = Path.of("src/main/java/com/sirin/hk3gtl/common/data/Hk3AbsorptionTowerPattern.java");
        Files.writeString(sourcePath, source, StandardCharsets.UTF_8);
        System.out.println("Wrote " + sourcePath);
    }
}
