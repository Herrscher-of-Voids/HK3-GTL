import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;

/**
 * 【变更记录 #1】2026-09-30 02:20:26（第1次备注 · 内测5修订107）
 * 删除：本文件可执行代码中的旧电压键及常量引用，不保留旧键注册别名。
 * 新增：16档正式缩写作为唯一电压标识；逐文件映射见logs/voltage-keys-r107。
 * 修改：注册、配方、查询或标签引用按原tier序号一一迁移；数值、层级与资源内容保持原义。
 * 用途：避免显示名与实际注册键不一致；历史备注保留，旧存档不自动改写。
 */
/**
 * 【变更记录 #2】2026-10-23 23:41:24（内测5名称统一维护）：删除旧项目名引用；新增本条维护记录；修改项目路径、启动标识或纹理目录为 HK3GTL 对应名称；用途为统一工具与构建引用，保留原有业务逻辑。
 */
public class GenerateTextures {

    static final String ITEM_DIR = "src/main/resources/assets/hk3gtl/textures/item/";
    static final String BLOCK_DIR = "src/main/resources/assets/hk3gtl/textures/block/";

    public static void main(String[] args) throws IOException {
        new File(ITEM_DIR).mkdirs();
        new File(BLOCK_DIR).mkdirs();

        generateCircuits();
        generateComponents();
        generateCasings();
        generateControllerFronts();

        System.out.println("All textures generated!");
    }

    // 仿 GT 组件风格色板
    static final int C0 = 0x00000000; // 透明
    static final int C1 = 0xFF0A1A5E; // 深海蓝（主体）
    static final int C2 = 0xFF060E32; // 极暗蓝（阴影）
    static final int C3 = 0xFFC0C8D0; // 银蓝（金属板/轴）
    static final int C4 = 0xFF00CCFF; // 青色（能量/高光）
    static final int C5 = 0xFF7B2FBE; // 紫色（线圈/能量线）
    static final int C6 = 0xFF162878; // 中蓝（高光边）
    static final int C7 = 0xFF808890; // 暗银
    static final int C8 = 0xFF66DDFF; // 亮青
    static final int C9 = 0xFF3A1A80; // 暗紫

    static void generateComponents() throws IOException {
        genComponent("electric_motor_hbv", new int[][] {
            {C0,C0,C0,C0,C0,C2,C2,C2,C2,C2,C2,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C2,C5,C5,C5,C5,C5,C5,C2,C0,C0,C0,C0},
            {C0,C0,C0,C2,C5,C1,C1,C1,C1,C1,C1,C5,C2,C0,C0,C0},
            {C0,C0,C0,C2,C4,C1,C6,C6,C6,C6,C1,C4,C2,C0,C0,C0},
            {C0,C0,C2,C5,C1,C6,C3,C3,C3,C3,C6,C1,C5,C2,C0,C0},
            {C3,C3,C7,C5,C1,C6,C3,C4,C4,C3,C6,C1,C5,C7,C3,C3},
            {C7,C7,C3,C5,C1,C6,C3,C8,C8,C3,C6,C1,C5,C3,C7,C7},
            {C3,C3,C3,C9,C1,C6,C3,C4,C4,C3,C6,C1,C9,C3,C3,C3},
            {C7,C7,C3,C5,C1,C6,C3,C8,C8,C3,C6,C1,C5,C3,C7,C7},
            {C3,C3,C7,C5,C1,C6,C3,C4,C4,C3,C6,C1,C5,C7,C3,C3},
            {C0,C0,C2,C5,C1,C6,C3,C3,C3,C3,C6,C1,C5,C2,C0,C0},
            {C0,C0,C0,C2,C4,C1,C6,C6,C6,C6,C1,C4,C2,C0,C0,C0},
            {C0,C0,C0,C2,C5,C1,C1,C1,C1,C1,C1,C5,C2,C0,C0,C0},
            {C0,C0,C0,C0,C2,C5,C5,C5,C5,C5,C5,C2,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C2,C2,C2,C2,C2,C2,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0},
        });

        genComponent("electric_piston_hbv", new int[][] {
            {C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C2,C2,C2,C2,C2,C2,C2,C2,C0,C0,C0,C0},
            {C0,C0,C0,C2,C1,C1,C6,C6,C6,C6,C1,C1,C2,C0,C0,C0},
            {C0,C0,C2,C1,C1,C6,C3,C3,C3,C3,C6,C1,C1,C2,C0,C0},
            {C0,C0,C2,C1,C6,C3,C3,C7,C7,C3,C3,C6,C1,C2,C0,C0},
            {C0,C0,C2,C1,C6,C3,C7,C4,C4,C7,C3,C6,C1,C2,C0,C0},
            {C0,C0,C2,C1,C6,C3,C3,C7,C7,C3,C3,C6,C1,C2,C0,C0},
            {C0,C0,C2,C1,C1,C6,C3,C3,C3,C3,C6,C1,C1,C2,C0,C0},
            {C0,C0,C0,C2,C1,C1,C6,C6,C6,C6,C1,C1,C2,C0,C0,C0},
            {C0,C0,C0,C0,C2,C2,C2,C3,C3,C2,C2,C2,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C0,C0,C3,C3,C0,C0,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C0,C0,C3,C3,C0,C0,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C0,C7,C3,C3,C7,C0,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C7,C3,C4,C4,C3,C7,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C7,C3,C3,C3,C3,C7,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C0,C7,C7,C7,C7,C0,C0,C0,C0,C0,C0},
        });

        genComponent("electric_pump_hbv", new int[][] {
            {C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C2,C2,C2,C2,C2,C2,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C2,C1,C1,C6,C6,C1,C1,C2,C0,C0,C0,C0},
            {C0,C0,C0,C2,C1,C6,C3,C3,C3,C3,C6,C1,C2,C0,C0,C0},
            {C0,C7,C3,C2,C1,C3,C4,C8,C8,C4,C3,C1,C2,C3,C7,C0},
            {C7,C3,C3,C2,C6,C3,C8,C4,C4,C8,C3,C6,C2,C3,C3,C7},
            {C0,C7,C3,C2,C1,C3,C4,C8,C8,C4,C3,C1,C2,C3,C7,C0},
            {C0,C0,C0,C2,C1,C6,C3,C3,C3,C3,C6,C1,C2,C0,C0,C0},
            {C0,C0,C0,C0,C2,C1,C1,C6,C6,C1,C1,C2,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C2,C2,C5,C5,C2,C2,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C0,C0,C5,C5,C0,C0,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C0,C5,C9,C9,C5,C0,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C5,C9,C5,C5,C9,C5,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C5,C5,C5,C5,C5,C5,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C0,C5,C5,C5,C5,C0,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0},
        });

        genComponent("conveyor_module_hbv", new int[][] {
            {C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0},
            {C0,C0,C2,C2,C2,C2,C2,C2,C2,C2,C2,C2,C2,C2,C0,C0},
            {C0,C2,C1,C1,C6,C1,C1,C6,C1,C1,C6,C1,C1,C1,C2,C0},
            {C2,C1,C6,C6,C3,C6,C6,C3,C6,C6,C3,C6,C6,C6,C1,C2},
            {C2,C5,C3,C3,C3,C3,C3,C3,C3,C3,C3,C3,C3,C3,C5,C2},
            {C2,C9,C5,C5,C5,C5,C5,C5,C5,C5,C5,C5,C5,C5,C9,C2},
            {C2,C1,C4,C4,C4,C4,C4,C4,C4,C4,C4,C4,C4,C4,C1,C2},
            {C2,C1,C4,C8,C4,C4,C4,C8,C4,C4,C4,C8,C4,C4,C1,C2},
            {C2,C9,C5,C5,C5,C5,C5,C5,C5,C5,C5,C5,C5,C5,C9,C2},
            {C2,C5,C3,C3,C3,C3,C3,C3,C3,C3,C3,C3,C3,C3,C5,C2},
            {C2,C1,C6,C6,C3,C6,C6,C3,C6,C6,C3,C6,C6,C6,C1,C2},
            {C0,C2,C1,C1,C6,C1,C1,C6,C1,C1,C6,C1,C1,C1,C2,C0},
            {C0,C0,C2,C2,C2,C2,C2,C2,C2,C2,C2,C2,C2,C2,C0,C0},
            {C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0},
        });

        genComponent("robot_arm_hbv", new int[][] {
            {C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C0,C0,C4,C4,C0,C0,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C0,C4,C3,C3,C4,C0,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C0,C4,C3,C3,C4,C0,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C0,C2,C7,C7,C2,C0,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C2,C1,C3,C3,C1,C2,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C2,C6,C5,C3,C3,C5,C6,C2,C0,C0,C0,C0},
            {C0,C0,C0,C2,C1,C5,C9,C7,C7,C9,C5,C1,C2,C0,C0,C0},
            {C0,C0,C2,C1,C6,C1,C5,C3,C3,C5,C1,C6,C1,C2,C0,C0},
            {C0,C2,C1,C6,C3,C6,C1,C3,C3,C1,C6,C3,C6,C1,C2,C0},
            {C2,C1,C6,C3,C3,C3,C6,C1,C1,C6,C3,C3,C3,C6,C1,C2},
            {C2,C6,C3,C7,C7,C7,C3,C6,C6,C3,C7,C7,C7,C3,C6,C2},
            {C0,C2,C1,C6,C6,C6,C1,C2,C2,C1,C6,C6,C6,C1,C2,C0},
            {C0,C0,C2,C2,C5,C2,C2,C0,C0,C2,C2,C5,C2,C2,C0,C0},
            {C0,C0,C0,C0,C4,C0,C0,C0,C0,C0,C0,C4,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0},
        });

        genComponent("field_generator_hbv", new int[][] {
            {C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0},
            {C0,C2,C2,C2,C2,C2,C2,C2,C2,C2,C2,C2,C2,C2,C2,C0},
            {C0,C2,C1,C1,C6,C6,C6,C6,C6,C6,C6,C6,C1,C1,C2,C0},
            {C0,C2,C1,C6,C2,C2,C2,C2,C2,C2,C2,C2,C6,C1,C2,C0},
            {C0,C2,C6,C2,C0,C0,C5,C5,C5,C5,C0,C0,C2,C6,C2,C0},
            {C0,C2,C6,C2,C0,C5,C4,C4,C4,C4,C5,C0,C2,C6,C2,C0},
            {C0,C2,C6,C2,C5,C4,C8,C8,C8,C8,C4,C5,C2,C6,C2,C0},
            {C0,C2,C6,C2,C5,C4,C8,C4,C4,C8,C4,C5,C2,C6,C2,C0},
            {C0,C2,C6,C2,C5,C4,C8,C4,C4,C8,C4,C5,C2,C6,C2,C0},
            {C0,C2,C6,C2,C5,C4,C8,C8,C8,C8,C4,C5,C2,C6,C2,C0},
            {C0,C2,C6,C2,C0,C5,C4,C4,C4,C4,C5,C0,C2,C6,C2,C0},
            {C0,C2,C6,C2,C0,C0,C5,C5,C5,C5,C0,C0,C2,C6,C2,C0},
            {C0,C2,C1,C6,C2,C2,C2,C2,C2,C2,C2,C2,C6,C1,C2,C0},
            {C0,C2,C1,C1,C6,C6,C6,C6,C6,C6,C6,C6,C1,C1,C2,C0},
            {C0,C2,C2,C2,C2,C2,C2,C2,C2,C2,C2,C2,C2,C2,C2,C0},
            {C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0},
        });

        genComponent("emitter_hbv", new int[][] {
            {C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C0,C0,C2,C2,C0,C0,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C0,C2,C1,C1,C2,C0,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C2,C1,C6,C6,C1,C2,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C2,C1,C6,C3,C3,C6,C1,C2,C0,C0,C0,C0},
            {C0,C0,C0,C2,C1,C6,C3,C4,C4,C3,C6,C1,C2,C0,C0,C0},
            {C0,C0,C2,C1,C6,C3,C4,C8,C8,C4,C3,C6,C1,C2,C0,C0},
            {C0,C2,C1,C6,C3,C4,C8,C8,C8,C8,C4,C3,C6,C1,C2,C4},
            {C0,C2,C1,C6,C3,C4,C8,C8,C8,C8,C4,C3,C6,C1,C2,C4},
            {C0,C0,C2,C1,C6,C3,C4,C8,C8,C4,C3,C6,C1,C2,C0,C0},
            {C0,C0,C0,C2,C1,C6,C3,C4,C4,C3,C6,C1,C2,C0,C0,C0},
            {C0,C0,C0,C0,C2,C1,C6,C3,C3,C6,C1,C2,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C2,C1,C6,C6,C1,C2,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C0,C2,C1,C1,C2,C0,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C0,C0,C2,C2,C0,C0,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0},
        });

        genComponent("sensor_hbv", new int[][] {
            {C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C2,C2,C2,C2,C2,C2,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C2,C1,C1,C6,C6,C1,C1,C2,C0,C0,C0,C0},
            {C0,C0,C0,C2,C1,C6,C5,C5,C5,C5,C6,C1,C2,C0,C0,C0},
            {C0,C0,C2,C1,C6,C5,C4,C4,C4,C4,C5,C6,C1,C2,C0,C0},
            {C0,C0,C2,C1,C5,C4,C8,C8,C8,C8,C4,C5,C1,C2,C0,C0},
            {C0,C0,C2,C6,C5,C4,C8,C4,C4,C8,C4,C5,C6,C2,C0,C0},
            {C0,C0,C2,C6,C5,C4,C8,C4,C4,C8,C4,C5,C6,C2,C0,C0},
            {C0,C0,C2,C1,C5,C4,C8,C8,C8,C8,C4,C5,C1,C2,C0,C0},
            {C0,C0,C2,C1,C6,C5,C4,C4,C4,C4,C5,C6,C1,C2,C0,C0},
            {C0,C0,C0,C2,C1,C6,C5,C5,C5,C5,C6,C1,C2,C0,C0,C0},
            {C0,C0,C0,C0,C2,C1,C1,C3,C3,C1,C1,C2,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C2,C2,C3,C3,C2,C2,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C0,C0,C3,C3,C0,C0,C0,C0,C0,C0,C0},
            {C0,C0,C0,C0,C0,C0,C0,C7,C7,C0,C0,C0,C0,C0,C0,C0},
        });
    }

    static void genComponent(String name, int[][] pixels) throws IOException {
        BufferedImage img = new BufferedImage(16, 16, BufferedImage.TYPE_INT_ARGB);
        for (int y = 0; y < 16; y++)
            for (int x = 0; x < 16; x++)
                img.setRGB(x, y, pixels[y][x]);
        ImageIO.write(img, "png", new File(ITEM_DIR + name + ".png"));
        System.out.println("Generated: " + name);
    }

    // ═══ 4 级海渊电路板 16×16 ═══
    static void generateCircuits() throws IOException {
        // 量子之海配色：深蓝底 + 青色/紫色电路走线
        int[][] boardColors = {
            {0xFF0A1A5E, 0xFF00CCFF, 0xFF0055AA}, // Abyss I: 深蓝底, 青走线, 暗青芯片
            {0xFF0C2278, 0xFF00AADD, 0xFF0066BB}, // Abyss II
            {0xFF1A0A5E, 0xFF7B2FBE, 0xFF5522AA}, // Abyss III: 紫色系
            {0xFF050520, 0xFFAAEEFF, 0xFF4488CC}, // Abyss IV: 极暗底, 亮青走线
        };
        String[] names = {"circuit_hbv", "circuit_hcv", "circuit_hrv", "circuit_hdv"};

        for (int i = 0; i < 4; i++) {
            BufferedImage img = new BufferedImage(16, 16, BufferedImage.TYPE_INT_ARGB);
            int bg = boardColors[i][0];
            int trace = boardColors[i][1];
            int chip = boardColors[i][2];

            // 板体 (3,3)-(12,12)
            for (int y = 3; y <= 12; y++)
                for (int x = 3; x <= 12; x++)
                    img.setRGB(x, y, bg);

            // 边框（亮一度）
            int border = brighten(bg, 30);
            for (int x = 3; x <= 12; x++) { img.setRGB(x, 3, border); img.setRGB(x, 12, border); }
            for (int y = 3; y <= 12; y++) { img.setRGB(3, y, border); img.setRGB(12, y, border); }

            // 走线横
            for (int x = 5; x <= 10; x++) { img.setRGB(x, 6, trace); img.setRGB(x, 9, trace); }
            // 走线纵
            for (int y = 5; y <= 10; y++) { img.setRGB(6, y, trace); img.setRGB(9, y, trace); }

            // 芯片 (7,7)-(8,8)
            img.setRGB(7, 7, chip); img.setRGB(8, 7, chip);
            img.setRGB(7, 8, chip); img.setRGB(8, 8, chip);

            // 角上小焊点
            img.setRGB(4, 4, trace); img.setRGB(11, 4, trace);
            img.setRGB(4, 11, trace); img.setRGB(11, 11, trace);

            // 额外细节随级别递增
            if (i >= 1) { img.setRGB(5, 5, chip); img.setRGB(10, 10, chip); }
            if (i >= 2) { img.setRGB(10, 5, chip); img.setRGB(5, 10, chip); }
            if (i >= 3) {
                // Abyss IV 发光核心
                int glow = 0xFFCCEEFF;
                img.setRGB(7, 7, glow); img.setRGB(8, 8, glow);
            }

            ImageIO.write(img, "png", new File(ITEM_DIR + names[i] + ".png"));
            System.out.println("Generated: " + names[i]);
        }
    }

    // ═══ 5 种机壳 16×16 ═══
    static void generateCasings() throws IOException {
        String[] names = {"casing_soulium", "casing_reinforced_soulium",
                "casing_abyss_mechanical", "casing_abyss_research", "casing_abyss_energy"};
        int[][] colors = {
            {0xFFC0C8D0, 0xFFA0A8B0, 0xFF808890}, // 魂钢: 银蓝
            {0xFF8888A0, 0xFF707088, 0xFF585870}, // 强化魂钢: 暗钢蓝
            {0xFF0A1A5E, 0xFF081448, 0xFF060E32}, // 海渊机械: 深海蓝
            {0xFF1A1050, 0xFF140C3C, 0xFF0E082A}, // 海渊科研: 蓝紫
            {0xFF050530, 0xFF040420, 0xFF030315}, // 海渊能源: 极暗蓝
        };
        int[][] accents = {
            {0xFFD8E0E8, 0}, // 魂钢亮边
            {0xFF9898B0, 0}, // 强化魂钢铆钉色
            {0xFF1A3A8E, 0}, // 海渊机械亮边
            {0xFF00AACC, 0}, // 海渊科研青色数据线
            {0xFF7B2FBE, 0}, // 海渊能源紫色能量线
        };

        for (int i = 0; i < 5; i++) {
            BufferedImage img = new BufferedImage(16, 16, BufferedImage.TYPE_INT_ARGB);
            int base = colors[i][0];
            int mid = colors[i][1];
            int dark = colors[i][2];
            int accent = accents[i][0];

            // 填充底色
            fill(img, base);

            // 外边框（暗色）
            for (int x = 0; x < 16; x++) { img.setRGB(x, 0, dark); img.setRGB(x, 15, dark); }
            for (int y = 0; y < 16; y++) { img.setRGB(0, y, dark); img.setRGB(15, y, dark); }

            // 内边框（中间色）
            for (int x = 1; x < 15; x++) { img.setRGB(x, 1, mid); img.setRGB(x, 14, mid); }
            for (int y = 1; y < 15; y++) { img.setRGB(1, y, mid); img.setRGB(14, y, mid); }

            // 面板线（十字分割）
            for (int x = 0; x < 16; x++) img.setRGB(x, 7, mid);
            for (int y = 0; y < 16; y++) img.setRGB(7, y, mid);

            // 四角铆钉/高光
            img.setRGB(2, 2, accent); img.setRGB(13, 2, accent);
            img.setRGB(2, 13, accent); img.setRGB(13, 13, accent);

            // 特殊效果
            if (i == 3) {
                // 科研机壳: 青色数据线
                for (int x = 3; x <= 12; x++) img.setRGB(x, 5, accent);
                for (int x = 3; x <= 12; x++) img.setRGB(x, 10, accent);
            }
            if (i == 4) {
                // 能源机壳: 紫色能量线网格
                for (int x = 0; x < 16; x++) { img.setRGB(x, 4, accent); img.setRGB(x, 11, accent); }
                for (int y = 0; y < 16; y++) { img.setRGB(4, y, accent); img.setRGB(11, y, accent); }
            }

            ImageIO.write(img, "png", new File(BLOCK_DIR + names[i] + ".png"));
            System.out.println("Generated: " + names[i]);
        }
    }

    // ═══ 3 个控制器正面（机壳+荧幕）16×16 ═══
    static void generateControllerFronts() throws IOException {
        // 控制器正面 = 对应机壳底 + 中央6×6荧幕
        String[] names = {"honkai_absorption_tower", "honkai_crystal_condenser", "soulium_smeltery"};

        // 吸收塔: 能源机壳底 + 紫色荧幕
        generateControllerFront(names[0],
                0xFF050530, 0xFF040420, 0xFF030315, 0xFF7B2FBE,
                0xFF9933FF, 0xFF6622CC);

        // 凝结厂: 魂钢机壳底 + 青蓝荧幕
        generateControllerFront(names[1],
                0xFFC0C8D0, 0xFFA0A8B0, 0xFF808890, 0xFFD8E0E8,
                0xFF00CCFF, 0xFF0088AA);

        // 冶铸中心: 强化魂钢底 + 橙红荧幕
        generateControllerFront(names[2],
                0xFF8888A0, 0xFF707088, 0xFF585870, 0xFF9898B0,
                0xFFFF6633, 0xFFCC4422);
    }

    static void generateControllerFront(String name, int base, int mid, int dark, int accent,
                                         int screenMain, int screenDark) throws IOException {
        BufferedImage img = new BufferedImage(16, 16, BufferedImage.TYPE_INT_ARGB);

        // 底层机壳
        fill(img, base);
        for (int x = 0; x < 16; x++) { img.setRGB(x, 0, dark); img.setRGB(x, 15, dark); }
        for (int y = 0; y < 16; y++) { img.setRGB(0, y, dark); img.setRGB(15, y, dark); }
        for (int x = 1; x < 15; x++) { img.setRGB(x, 1, mid); img.setRGB(x, 14, mid); }
        for (int y = 1; y < 15; y++) { img.setRGB(1, y, mid); img.setRGB(14, y, mid); }
        img.setRGB(2, 2, accent); img.setRGB(13, 2, accent);
        img.setRGB(2, 13, accent); img.setRGB(13, 13, accent);

        // 荧幕区域 (5,5)-(10,10)
        int border = 0xFF111111;
        for (int x = 4; x <= 11; x++) { img.setRGB(x, 4, border); img.setRGB(x, 11, border); }
        for (int y = 4; y <= 11; y++) { img.setRGB(4, y, border); img.setRGB(11, y, border); }

        // 荧幕内部
        for (int y = 5; y <= 10; y++)
            for (int x = 5; x <= 10; x++)
                img.setRGB(x, y, screenDark);

        // 荧幕图案（十字高光）
        for (int x = 6; x <= 9; x++) img.setRGB(x, 7, screenMain);
        for (int x = 6; x <= 9; x++) img.setRGB(x, 8, screenMain);
        for (int y = 6; y <= 9; y++) img.setRGB(7, y, screenMain);
        for (int y = 6; y <= 9; y++) img.setRGB(8, y, screenMain);

        // 中心最亮点
        int bright = brighten(screenMain, 60);
        img.setRGB(7, 7, bright); img.setRGB(8, 8, bright);

        ImageIO.write(img, "png", new File(BLOCK_DIR + name + ".png"));
        System.out.println("Generated controller: " + name);
    }

    // ═══ 工具方法 ═══

    static void fill(BufferedImage img, int color) {
        for (int y = 0; y < 16; y++)
            for (int x = 0; x < 16; x++)
                img.setRGB(x, y, color);
    }

    static int brighten(int argb, int amount) {
        int a = (argb >> 24) & 0xFF;
        int r = Math.min(255, ((argb >> 16) & 0xFF) + amount);
        int g = Math.min(255, ((argb >> 8) & 0xFF) + amount);
        int b = Math.min(255, (argb & 0xFF) + amount);
        return (a << 24) | (r << 16) | (g << 8) | b;
    }
}
