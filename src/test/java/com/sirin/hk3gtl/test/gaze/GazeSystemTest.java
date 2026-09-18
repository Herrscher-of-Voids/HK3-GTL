package com.sirin.hk3gtl.test.gaze;

import java.util.ArrayList;
import java.util.List;

/**
 * 终焉注视度系统核心公式回归测试（纯逻辑，不依赖 Minecraft 运行时）。
 *
 * <p>注视度的读写依赖 ServerPlayer.persistentData 与设施扫描，纯 JVM 无法构造；
 * 但系统的<b>核心数值规则</b>是纯函数，可独立固化，防止设计公式被误改。本测试镜像
 * 生产代码中的公式并断言其与设计文档（06 注视度与研究速度公式设计 / 07 终焉注视事件阈值表）一致。</p>
 *
 * <h3>覆盖</h3>
 * <ul>
 *   <li>G-101 研究速度衰减系数 = max(floor, 1 - gaze/2000)，含缓冲阵地板提升</li>
 *   <li>G-102 机器效率分级（RecipeLogicMixin 同款分段）</li>
 *   <li>G-103 增长修正：抑制 -30%、缓冲 -50%、负值原样、正值下限 1</li>
 *   <li>G-104 阈值跨越判定：仅在上穿且未触发过时命中</li>
 *   <li>G-105 HUD 占比与颜色分级边界</li>
 * </ul>
 */
public class GazeSystemTest {

    private static final double DECAY_DIVISOR = 2000.0;
    private static final double FLOOR = 0.3;
    private static final int GAZE_MAX = 1000;
    private static final int[] THRESHOLDS = {50, 100, 200, 300, 500, 700, 800, 900, 1000};

    // ── 镜像公式（与生产代码保持一致）────────────────────────────────

    private static double researchSpeedFactor(int gaze, boolean hasBufferArray) {
        double floor = hasBufferArray ? Math.max(FLOOR, 0.4) : FLOOR;
        double base = 1.0 - gaze / DECAY_DIVISOR;
        return Math.max(floor, base);
    }

    private static double machineFactor(int gaze) {
        if (gaze < 200) return 1.0;
        if (gaze < 500) return 0.95;
        if (gaze < 800) return 0.75;
        if (gaze < 1000) return 0.60;
        return 0.50;
    }

    private static int adjustGrowth(int amount, boolean suppression, boolean buffer) {
        if (amount <= 0) return amount;
        double adjusted = amount;
        if (suppression) adjusted *= 0.7;
        if (buffer) adjusted *= 0.5;
        return Math.max(1, (int) Math.round(adjusted));
    }

    private static boolean crossesThreshold(int oldV, int newV, int threshold, boolean alreadyTriggered) {
        if (newV <= oldV) return false;
        if (oldV >= threshold || newV < threshold) return false;
        return !alreadyTriggered;
    }

    // PLACEHOLDER_TESTS

    private static boolean approx(double a, double b) {
        return Math.abs(a - b) < 1e-6;
    }

    /** G-101 衰减系数：对齐设计 7.4 示例表 + 缓冲阵地板提升。 */
    private static boolean testG101() {
        boolean ok = true;
        ok &= approx(researchSpeedFactor(0, false), 1.00);
        ok &= approx(researchSpeedFactor(200, false), 0.90);
        ok &= approx(researchSpeedFactor(500, false), 0.75);
        ok &= approx(researchSpeedFactor(800, false), 0.60);
        ok &= approx(researchSpeedFactor(1000, false), 0.50);
        // 地板：无缓冲阵极大注视降到 0.3 下限
        ok &= approx(researchSpeedFactor(2000, false), 0.30);
        ok &= approx(researchSpeedFactor(5000, false), 0.30);
        // 缓冲阵把地板提升到 0.4
        ok &= approx(researchSpeedFactor(2000, true), 0.40);
        if (!ok) System.err.println("[G-101] 衰减系数与设计表不符");
        return ok;
    }

    /** G-102 机器效率分级：分段边界必须与 RecipeLogicMixin 完全一致。 */
    private static boolean testG102() {
        boolean ok = true;
        ok &= approx(machineFactor(0), 1.0);
        ok &= approx(machineFactor(199), 1.0);
        ok &= approx(machineFactor(200), 0.95);   // 边界：设计"200 机器效率开始下降"
        ok &= approx(machineFactor(499), 0.95);
        ok &= approx(machineFactor(500), 0.75);
        ok &= approx(machineFactor(799), 0.75);
        ok &= approx(machineFactor(800), 0.60);
        ok &= approx(machineFactor(999), 0.60);
        ok &= approx(machineFactor(1000), 0.50);  // 设计"1000 半速"
        if (!ok) System.err.println("[G-102] 机器效率分级边界不符");
        return ok;
    }

    /** G-103 增长修正：抑制/缓冲乘数、负值原样、正值下限 1。 */
    private static boolean testG103() {
        boolean ok = true;
        ok &= adjustGrowth(30, false, false) == 30;
        ok &= adjustGrowth(30, true, false) == 21;    // 30*0.7=21
        ok &= adjustGrowth(30, false, true) == 15;     // 30*0.5=15
        ok &= adjustGrowth(30, true, true) == 11;      // 30*0.35=10.5→round 11
        ok &= adjustGrowth(-50, true, true) == -50;    // 负值（缓冲单元立即降）原样
        ok &= adjustGrowth(1, true, true) == 1;        // 正值下限保护，避免抑制到 0
        if (!ok) System.err.println("[G-103] 增长修正逻辑不符");
        return ok;
    }

    /** G-104 阈值跨越：仅在上穿且未触发过时命中。 */
    private static boolean testG104() {
        boolean ok = true;
        ok &= crossesThreshold(90, 110, 100, false);        // 正常上穿
        ok &= !crossesThreshold(90, 110, 100, true);        // 已触发过不重复
        ok &= !crossesThreshold(110, 90, 100, false);       // 下降不触发
        ok &= !crossesThreshold(100, 150, 100, false);      // 起点已达阈值不重复
        ok &= !crossesThreshold(50, 90, 100, false);        // 未达阈值
        ok &= crossesThreshold(0, 1000, 500, false);        // 一次跨多阈值中的某个
        // 校验设计阈值集合完整（50~1000 共 9 档）
        ok &= THRESHOLDS.length == 9 && THRESHOLDS[0] == 50 && THRESHOLDS[8] == GAZE_MAX;
        if (!ok) System.err.println("[G-104] 阈值跨越判定不符");
        return ok;
    }

    /** G-105 HUD 占比与颜色分级边界。 */
    private static boolean testG105() {
        boolean ok = true;
        ok &= approx(ratio(0, 1000), 0.0);
        ok &= approx(ratio(500, 1000), 0.5);
        ok &= approx(ratio(1000, 1000), 1.0);
        ok &= approx(ratio(1200, 1000), 1.0);   // 超上限钳到 1.0
        // 颜色分级：青<0.3 / 黄<0.6 / 橙<0.85 / 红>=0.85
        ok &= colorTier(0.29f) == 0 && colorTier(0.3f) == 1;
        ok &= colorTier(0.59f) == 1 && colorTier(0.6f) == 2;
        ok &= colorTier(0.84f) == 2 && colorTier(0.85f) == 3;
        if (!ok) System.err.println("[G-105] HUD 占比/颜色分级不符");
        return ok;
    }

    private static float ratio(int gaze, int max) {
        return Math.min(1.0f, (float) gaze / (float) Math.max(1, max));
    }

    private static int colorTier(float r) {
        if (r < 0.3f) return 0;
        if (r < 0.6f) return 1;
        if (r < 0.85f) return 2;
        return 3;
    }

    public static void main(String[] args) {
        List<boolean[]> results = new ArrayList<>();
        results.add(new boolean[]{testG101()});
        results.add(new boolean[]{testG102()});
        results.add(new boolean[]{testG103()});
        results.add(new boolean[]{testG104()});
        results.add(new boolean[]{testG105()});

        String[] ids = {"G-101", "G-102", "G-103", "G-104", "G-105"};
        int passed = 0;
        for (int i = 0; i < results.size(); i++) {
            boolean ok = results.get(i)[0];
            System.out.println((ok ? "[PASS] " : "[FAIL] ") + ids[i]);
            if (ok) passed++;
        }
        System.out.println("\n=============================================");
        System.out.println("  HK3GTL Gaze System Test: " + passed + " / " + results.size());
        System.out.println("=============================================");
        System.exit(passed == results.size() ? 0 : 1);
    }
}
