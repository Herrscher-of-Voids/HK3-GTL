/**
 * 崩坏能吸收塔 21x21x48 结构生成器
 * 巴黎铁塔风格：底部四腿宽大，中部收窄，顶部塔尖+水晶核心
 *
 * 坐标系：GTCEu pattern = aisle(Z轴方向)，每个aisle字符串=X轴(21字符)，字符串数=Y轴(48层)
 * 控制器 S 在 Z=10, Y=1, X=10 (底部正面中心)
 *
 * 字符映射：
 * B = black_concrete (主体)
 * W = white_concrete (装饰线)
 * P = purple_concrete (紫色装饰)
 * G = purple_stained_glass (紫色玻璃)
 * g = purple_stained_glass_pane (紫色玻璃板)
 * U = blue_concrete (蓝色结构)
 * C = gtlcore:create_casing (机械壳)
 * I = iron_bars (铁栏杆)
 * E = kubejs:eternity_coil_block (永恒线圈)
 * O = command_block (核心)
 * c = chain (锁链)
 * Q = smooth_quartz_stairs (楼梯装饰)
 * H = 仓室位置 (控制器周围)
 * F = fishbig (装饰，控制器上方)
 * S = 控制器
 * ' ' = any (空气/忽略)
 */
public class TowerPatternGenerator {

    static final int W = 21; // X 宽度
    static final int H = 48; // Y 高度 (每个aisle的字符串数)
    static final int D = 21; // Z 深度 (aisle数)

    public static void main(String[] args) {
        // 生成 21 个 aisle，每个 aisle 有 48 层（字符串）
        String[][] tower = new String[D][H];

        // 初始化为空气
        for (int z = 0; z < D; z++)
            for (int y = 0; y < H; y++)
                tower[z][y] = " ".repeat(W);

        // ═══ 底座平台 Y=0 ═══
        fillLayer(tower, 0, 'B', 0, 20, 0, 20);

        // ═══ 四腿基座 Y=1~12 ═══
        for (int y = 1; y <= 12; y++) {
            int shrink = y / 3; // 每3层收缩1格
            int lo = shrink;
            int hi = 20 - shrink;

            // 四条腿 (角落 5x5 区域)
            fillRect(tower, y, 'B', lo, lo + 4, lo, lo + 4);
            fillRect(tower, y, 'B', hi - 4, hi, lo, lo + 4);
            fillRect(tower, y, 'B', lo, lo + 4, hi - 4, hi);
            fillRect(tower, y, 'B', hi - 4, hi, hi - 4, hi);

            // 四腿之间的横梁（每4层加一道）
            if (y % 4 == 0) {
                int mid = 10;
                // X方向横梁
                for (int x = lo + 5; x <= hi - 5; x++) {
                    setChar(tower, y, x, lo + 2, 'W');
                    setChar(tower, y, x, hi - 2, 'W');
                }
                // Z方向横梁
                for (int z = lo + 5; z <= hi - 5; z++) {
                    setChar(tower, y, lo + 2, z, 'W');
                    setChar(tower, y, hi - 2, z, 'W');
                }
            }

            // 斜撑 (X形铁栏杆)
            if (y >= 3 && y <= 10) {
                int offset = y - 2;
                if (offset >= 5 && offset <= 15) {
                    setChar(tower, y, offset, offset, 'I');
                    setChar(tower, y, 20 - offset, offset, 'I');
                    setChar(tower, y, offset, 20 - offset, 'I');
                    setChar(tower, y, 20 - offset, 20 - offset, 'I');
                }
            }
        }

        // ═══ 第一平台 Y=13~15（拱门层）═══
        for (int y = 13; y <= 15; y++) {
            fillRect(tower, y, 'B', 3, 17, 3, 17);
            // 中空
            fillRect(tower, y, ' ', 5, 15, 5, 15);
            // 紫色玻璃装饰边
            for (int x = 4; x <= 16; x++) {
                setChar(tower, y, x, 4, 'P');
                setChar(tower, y, x, 16, 'P');
            }
            for (int z = 4; z <= 16; z++) {
                setChar(tower, y, 4, z, 'P');
                setChar(tower, y, 16, z, 'P');
            }
        }

        // ═══ 中段塔身 Y=16~32 ═══
        for (int y = 16; y <= 32; y++) {
            int shrink2 = 5 + (y - 16) / 4;
            int lo = shrink2;
            int hi = 20 - shrink2;
            if (lo > 8) lo = 8;
            if (hi < 12) hi = 12;

            // 外壁
            for (int x = lo; x <= hi; x++) {
                setChar(tower, y, x, lo, 'B');
                setChar(tower, y, x, hi, 'B');
            }
            for (int z = lo; z <= hi; z++) {
                setChar(tower, y, lo, z, 'B');
                setChar(tower, y, hi, z, 'B');
            }
            // 白色角装饰
            setChar(tower, y, lo, lo, 'W');
            setChar(tower, y, hi, lo, 'W');
            setChar(tower, y, lo, hi, 'W');
            setChar(tower, y, hi, hi, 'W');
        }

        // ═══ 第二平台 Y=33~35 ═══
        for (int y = 33; y <= 35; y++) {
            fillRect(tower, y, 'B', 7, 13, 7, 13);
            fillRect(tower, y, ' ', 8, 12, 8, 12);
            // 紫色装饰
            for (int x = 7; x <= 13; x++) {
                setChar(tower, y, x, 7, 'P');
                setChar(tower, y, x, 13, 'P');
            }
            for (int z = 7; z <= 13; z++) {
                setChar(tower, y, 7, z, 'P');
                setChar(tower, y, 13, z, 'P');
            }
        }

        // ═══ 上段塔尖 Y=36~41 ═══
        for (int y = 36; y <= 41; y++) {
            // 3x3 中心柱
            fillRect(tower, y, 'B', 9, 11, 9, 11);
            setChar(tower, y, 10, 10, 'C'); // 中心机械壳
        }

        // ═══ 水晶核心 Y=42~46 ═══
        // Y=42: 底座
        fillRect(tower, 42, 'U', 9, 11, 9, 11);
        setChar(tower, 42, 10, 10, 'E');

        // Y=43: 外壳
        fillRect(tower, 43, 'g', 8, 12, 8, 12);
        fillRect(tower, 43, ' ', 9, 11, 9, 11);
        setChar(tower, 43, 10, 10, 'E');
        setChar(tower, 43, 9, 10, 'G'); setChar(tower, 43, 11, 10, 'G');
        setChar(tower, 43, 10, 9, 'G'); setChar(tower, 43, 10, 11, 'G');

        // Y=44: 核心层 (命令方块)
        fillRect(tower, 44, 'G', 8, 12, 8, 12);
        fillRect(tower, 44, ' ', 9, 11, 9, 11);
        setChar(tower, 44, 10, 10, 'O'); // 命令方块核心
        setChar(tower, 44, 9, 10, 'E'); setChar(tower, 44, 11, 10, 'E');
        setChar(tower, 44, 10, 9, 'E'); setChar(tower, 44, 10, 11, 'E');

        // Y=45: 上壳
        fillRect(tower, 45, 'g', 8, 12, 8, 12);
        fillRect(tower, 45, ' ', 9, 11, 9, 11);
        setChar(tower, 45, 10, 10, 'E');
        setChar(tower, 45, 9, 10, 'G'); setChar(tower, 45, 11, 10, 'G');
        setChar(tower, 45, 10, 9, 'G'); setChar(tower, 45, 10, 11, 'G');

        // Y=46: 顶部
        fillRect(tower, 46, 'U', 9, 11, 9, 11);
        setChar(tower, 46, 10, 10, 'E');

        // Y=47: 塔尖
        setChar(tower, 47, 10, 10, 'E');

        // ═══ 控制器区域 Z=10 ═══
        // Y=1: 控制器 S 在 (X=10, Z=10)
        setChar(tower, 1, 10, 10, 'S');

        // Y=2: 鱼大 F 在控制器上方
        setChar(tower, 2, 10, 10, 'F');

        // 控制器周围一圈 H (Y=0,1,2 的 8 个相邻位置在 Z=9,10,11)
        // Y=0 底层
        setChar(tower, 0, 9, 9, 'H'); setChar(tower, 0, 10, 9, 'H'); setChar(tower, 0, 11, 9, 'H');
        setChar(tower, 0, 9, 10, 'H'); setChar(tower, 0, 11, 10, 'H');
        setChar(tower, 0, 9, 11, 'H'); setChar(tower, 0, 10, 11, 'H'); setChar(tower, 0, 11, 11, 'H');
        // Y=1 控制器层旁边
        setChar(tower, 1, 9, 9, 'H'); setChar(tower, 1, 11, 9, 'H');
        setChar(tower, 1, 9, 11, 'H'); setChar(tower, 1, 11, 11, 'H');
        setChar(tower, 1, 9, 10, 'H'); setChar(tower, 1, 11, 10, 'H');
        setChar(tower, 1, 10, 9, 'H'); setChar(tower, 1, 10, 11, 'H');
        // Y=2
        setChar(tower, 2, 9, 9, 'H'); setChar(tower, 2, 10, 9, 'H'); setChar(tower, 2, 11, 9, 'H');
        setChar(tower, 2, 9, 10, 'H'); setChar(tower, 2, 11, 10, 'H');
        setChar(tower, 2, 9, 11, 'H'); setChar(tower, 2, 10, 11, 'H'); setChar(tower, 2, 11, 11, 'H');

        // ═══ 输出 Java 代码 ═══
        System.out.println("// Generated tower pattern: 21x21x48");
        System.out.println("// Each .aisle() = one Z slice, containing 48 strings (Y layers), each 21 chars (X)");
        for (int z = 0; z < D; z++) {
            System.out.println(".aisle(  // Z=" + z);
            for (int y = 0; y < H; y++) {
                String line = tower[z][y];
                String comma = (y < H - 1) ? "," : "";
                System.out.println("    \"" + line + "\"" + comma);
            }
            System.out.println(")");
        }
    }

    static void setChar(String[][] tower, int y, int x, int z, char ch) {
        if (x < 0 || x >= W || y < 0 || y >= H || z < 0 || z >= D) return;
        char[] arr = tower[z][y].toCharArray();
        arr[x] = ch;
        tower[z][y] = new String(arr);
    }

    static void fillLayer(String[][] tower, int y, char ch, int xMin, int xMax, int zMin, int zMax) {
        for (int z = zMin; z <= zMax; z++) {
            char[] arr = tower[z][y].toCharArray();
            for (int x = xMin; x <= xMax; x++) arr[x] = ch;
            tower[z][y] = new String(arr);
        }
    }

    static void fillRect(String[][] tower, int y, char ch, int xMin, int xMax, int zMin, int zMax) {
        fillLayer(tower, y, ch, xMin, xMax, zMin, zMax);
    }

    static char getChar(String[][] tower, int y, int x, int z) {
        if (x < 0 || x >= W || y < 0 || y >= H || z < 0 || z >= D) return ' ';
        return tower[z][y].charAt(x);
    }
}
