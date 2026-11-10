package com.sirin.hk3gtl.test.gaze;

import com.sirin.hk3gtl.common.gaze.Hk3GazeJournal;
import com.sirin.hk3gtl.common.gaze.Hk3GazeRules;
import com.sirin.hk3gtl.common.gaze.Hk3SuppressionSourceRegistry;
import com.sirin.hk3gtl.common.research.Hk3ResearchMath;
import com.sirin.hk3gtl.common.research.Hk3ResearchPlans;
import com.sirin.hk3gtl.common.research.Hk3ResearchStartService;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.NbtIo;

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
/**
 * 【变更记录 #1】2026-09-30 15:52:28（内测5修订109）
 * 删除：测试中镜像旧线性研究公式的实现；上方历史说明留存，仅作追溯。
 * 新增：直接调用生产公式、材料报价、来源去重与NBT序列化测试。
 * 修改：验证S01免压、锚球形边界、日志裁剪不解锁来源、溢出钳制。
 * 用途：防止测试通过而实际研究使用另一套公式；不代表实机验收。
 */
/**
 * 【变更记录 #2】2026-11-04 21:09:06（内测5修订200）
 * 删除：无。新增：生产稳定源登记的实例替换、迟到注销、注销幂等与快照隔离回归；集成生产工业分段测试。
 * 修改：直接调用生产注册表；用途：验证按实例而非坐标或equals授予资格，不冒充正式I36实机验收。
 */
public class GazeSystemTest {
    private static int checks;
    private static void check(boolean result, String label) {
        if (!result) throw new AssertionError(label);
        checks++;
    }
    private static void near(double value, double expected, String label) {
        check(Math.abs(value - expected) < 1e-9, label);
    }
    private static void sourceIdentity() {
        var registry = new Hk3SuppressionSourceRegistry<String, String>();
        var oldSource = new String("相同内容的不同实例");
        var newSource = new String("相同内容的不同实例");
        check(registry.snapshot().isEmpty(), "未登记实例无资格");
        registry.register("位置A", oldSource);
        check(registry.snapshot().get("位置A") == oldSource, "登记保留具体实例");
        registry.unregister("位置A", newSource);
        check(registry.snapshot().get("位置A") == oldSource, "equals相同的另一实例不能注销");
        registry.register("位置A", newSource);
        check(registry.snapshot().get("位置A") == newSource, "同位置新登记替换旧实例");
        registry.unregister("位置A", oldSource);
        check(registry.snapshot().get("位置A") == newSource, "旧实例迟到卸载不删除新登记");
        registry.snapshot().clear();
        check(registry.snapshot().get("位置A") == newSource, "查询快照不修改实际登记");
        registry.register("位置B", oldSource);
        registry.unregister("位置A", newSource);
        registry.unregister("位置A", newSource);
        check(!registry.snapshot().containsKey("位置A"), "拆除注销立即生效且重复安全");
        check(registry.snapshot().get("位置B") == oldSource, "注销不影响其他坐标");
        registry.unregister("位置B", oldSource);
        check(registry.snapshot().isEmpty(), "全部注销后不残留资格");
    }

    public static void main(String[] args) throws Exception {
        IndustrialGazeScheduleTest.main(args);
        sourceIdentity();
        near(Hk3ResearchMath.pressure(2, 100, 0), .4125, "G100复合压力");
        near(Hk3ResearchMath.speed(1, 1000, 0, false, false), 1, "S01免压");
        near(Hk3ResearchMath.speed(5, 0, 0, true, true), 3, "加速统一上限");
        check(Hk3ResearchMath.speed(2, 1000, .5, false, false)
                > Hk3ResearchMath.speed(2, 1000, 0, false, false), "锚降低研究压力");
        check(Hk3ResearchMath.speed(2, 1000, .75, false, false)
                > Hk3ResearchMath.speed(2, 1000, .5, false, false), "强化锚进一步减压");
        for (int lab = 2; lab <= 5; lab++) {
            double previous = 1;
            for (int g = 0; g <= 1000; g++) {
                double speed = Hk3ResearchMath.speed(lab, g, 0, false, false);
                check(speed > 0 && speed <= previous, "压力升高速度单调下降且不归零"); previous = speed;
            }
        }
        var plan = new Hk3ResearchPlans.Plan("test", 100, 100, "", "", java.util.List.of(
                new Hk3ResearchPlans.Material("forge:plates/steel", 100, 1),
                new Hk3ResearchPlans.Material("forge:circuits/max", 100, .35)), 1);
        var quote = Hk3ResearchStartService.materials(plan, 2, 100, 0);
        check(quote.get(0).count() == 127 && quote.get(1).count() == 110, "板材/电路敏感度与额外向上取整");
        check(Hk3ResearchStartService.materials(plan, 1, 1000, 0).equals(plan.materials()), "S01材料免压");
        var suppressed = Hk3ResearchStartService.materials(plan, 2, 100, .75);
        check(suppressed.get(0).count() < quote.get(0).count() && plan.points() == 100, "锚影响材料不改点价");
        check(quote.get(0).count() == 127, "后续压力变化不改旧报价");
        near(Hk3GazeRules.suppression(true, true, false, 4096), .5, "64格边界包含");
        near(Hk3GazeRules.suppression(true, true, false, 4097), 0, "超64格无效");
        near(Hk3GazeRules.suppression(true, true, true, 16384), .75, "128格边界包含");
        near(Hk3GazeRules.suppression(true, true, true, 16385), 0, "超128格无效");
        near(Hk3GazeRules.suppression(false, true, true, 0), 0, "异队不共享");
        near(Hk3GazeRules.suppression(true, false, true, 0), 0, "未付电无效");
        near(Hk3GazeRules.suppression(true, true, true, Double.NaN), 0, "非法距离无效");
        check(Hk3GazeRules.add(999, Integer.MAX_VALUE, 1000) == 1000, "正溢出不反向降压");
        check(Hk3GazeRules.add(1, Integer.MIN_VALUE, 1000) == 0, "负溢出不变正");
        check(Hk3GazeRules.bufferActive(6000, 5999), "缓冲到期前一刻");
        check(!Hk3GazeRules.bufferActive(6000, 6000), "到期刻立即失效");
        check(Hk3GazeRules.effective(30, true) == 0 && Hk3GazeRules.effective(100, true) == 50, "有效值不负数");
        check(Hk3GazeRules.effective(100, false) == 100, "到期恢复原值");
        check(Hk3GazeRules.growth(30, true) == 15 && Hk3GazeRules.growth(30, false) == 30, "缓冲只修正正增长");
        check(Hk3GazeRules.growth(-50, true) == -50 && Hk3GazeRules.growth(1, true) == 1, "负增长不修正及正增长下限");
        var player = new CompoundTag();
        check(Hk3GazeJournal.claim(player, "event:first"), "首次来源");
        check(!Hk3GazeJournal.claim(player, "event:first"), "重复来源");
        for (int i = 0; i < 100; i++) Hk3GazeJournal.record(player, "test:" + i, i, i + 1, i);
        check(Hk3GazeJournal.recent(player).size() == 64, "仅保留64条详细记录");
        Hk3GazeJournal.record(player, "buffer-unit", 100, 50, 101);
        check(player.getCompound(Hk3GazeJournal.KEY).getInt("Peak") == 100, "降压不抹掉峰值");
        var bytes = new java.io.ByteArrayOutputStream(); NbtIo.writeCompressed(player, bytes);
        var restored = NbtIo.readCompressed(new java.io.ByteArrayInputStream(bytes.toByteArray()));
        check(!Hk3GazeJournal.claim(restored, "event:first"), "序列化和日志裁剪不重置去重");
        var clone = new CompoundTag(); clone.put(Hk3GazeJournal.KEY, restored.getCompound(Hk3GazeJournal.KEY).copy());
        check(!Hk3GazeJournal.claim(clone, "event:first"), "重生复制同键不重扣");
        var view = Hk3GazeJournal.recent(restored); view.clear();
        check(Hk3GazeJournal.recent(restored).size() == 64, "只读返回副本");
        System.out.println("注视与研究生产逻辑回归通过：" + checks + " 项断言");
    }
}
