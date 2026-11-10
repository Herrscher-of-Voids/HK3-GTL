package com.sirin.hk3gtl.common.research;

import com.gregtechceu.gtceu.api.machine.MetaMachine;
import net.minecraft.server.level.ServerPlayer;

/**
 * 【变更记录 #1】2026-09-28 00:04:14（内测5修订91）
 * 删除：无。新增：两种执行器共用的不扣费环境推进判定。
 * 修改：搬移既有无锚隔tick与注视度分段公式，保持64格最近玩家归属及时间相位。
 * 用途：增强版实际执行tick前仍应用原有环境限制；无缓存、无存档写入、无资源扣款。
 */
/**
 * 【变更记录 #2】2026-10-17 14:44:46（第2次备注 · 内测5修订162）
 * 删除：仅约束九个退役类型的旧锚邻域扫描与隔tick限速入口。
 * 新增：无。修改：保留注视度环境规则；现行锚定工艺、研究与事实条件不变。
 * 用途：已删除设备不再约束现役执行器，原文件完整备份于退役清理目录。
 */
/**
 * 【变更记录 #3】2026-11-04 21:00:03（第3次备注 · 内测5修订200）
 * 删除：工业守卫只读取最近玩家个人有效值的绕过路径。
 * 新增：调用现行在线团队最高有效值接口及独立工业分段调度函数。
 * 修改：保留64格最近玩家归属、既有工业分段和100刻位置相位，不套用研究减速公式。
 * 用途：同队低注视玩家靠近机器不能规避在线高注视队员；本入口不扣能源、不改并行和工时。
 */
public final class Hk3RecipeEnvironment {
    private Hk3RecipeEnvironment() {}
    public static boolean throttlesByGaze(MetaMachine machine) {
        var level = machine.getLevel(); var pos = machine.getPos();
        if (level == null || level.isClientSide() || pos == null) return false;
        var nearest = level.getNearestPlayer(pos.getX() + 0.5, pos.getY() + 0.5, pos.getZ() + 0.5, 64, false);
        if (!(nearest instanceof ServerPlayer player)) return false;
        double gaze = Hk3ResearchTeams.gaze(player.server,
                Hk3ResearchTeams.scope(player.server, player.getUUID()));
        return Hk3IndustrialGazeSchedule.throttles(gaze, level.getGameTime(), pos.asLong());
    }
}
