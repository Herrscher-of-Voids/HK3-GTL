package com.sirin.hk3gtl.common.overview;

import com.sirin.hk3gtl.common.overview.Hk3MachineOverviewData.*;

import java.util.HashSet;
import java.util.UUID;

/**
 * 【文件职责】直接验证生产过载策略与已有账本轮转恢复条件，不构造或扫描真实世界。
 * 【变更记录 #1】2026-10-19 02:25:53（第1次备注 · 修订171）
 * 删除：无。新增：4097条既有记录的过载保留、轮转可达、未知条目拒建、非加载过载撤销及迁队反例。
 * 修改：由MachineOverviewTest调用；用途为生产策略回归，不代替Forge回滚、同BE身份或多人实机验收。
 */
/**
 * 【变更记录 #2】2026-10-19 02:29:04（第2次备注 · 修订171）
 * 删除：无。新增：原未加载记录遇元数据异常仍保留快照、实时记录故障降级与重复告警抑制的生产策略负例。
 * 修改：无；用途：验证读取异常不绕过后继身份核验，也不伪装最后可信记录的时间。
 */
public final class Hk3MachineOverviewLoadRecoveryTest {
    private static int checks;
    private Hk3MachineOverviewLoadRecoveryTest() {}
    public static int run() {
        checks = 0;
        UUID oldTeam = new UUID(31, 1), nextTeam = new UUID(31, 2);
        String dimension = "minecraft:overworld";
        var descriptor = new Descriptor("hk3gtl:load_test", "加载测试", "多方块控制器", true);
        var last = new Observation(State.RUNNING, "过载前最后可信快照");
        var data = new Hk3MachineOverviewData();
        for (long pos = 0; pos < 4097; pos++) data.register(oldTeam, dimension, pos, descriptor, last, 40, true);
        long delayed = 4096;
        UUID id = Hk3MachineOverviewData.identity(dimension, delayed);
        check(!Hk3MachineOverviewHooks.needsLoadVerification(data.visible(oldTeam, id), true), "已实时条目不重复排恢复");
        Hk3MachineOverviewHooks.overflow(data, dimension, delayed, true);
        var saved = data.visible(oldTeam, id);
        check(saved != null && saved.state() == State.UNLOADED, "加载过载保留有效索引而非删除");
        check(saved.team().equals(oldTeam) && saved.descriptor().equals(descriptor), "过载不改变团队或注册身份");
        check(saved.observation().equals(last) && saved.observedAt() == 40, "过载不改写最后可信状态和时间");
        check(data.visible(nextTeam, id) == null, "延迟快照没有授权其他队");
        check(Hk3MachineOverviewHooks.needsLoadVerification(saved, true), "持久归属HK必须重新提交同BE复核");
        check(!Hk3MachineOverviewHooks.needsLoadVerification(saved, false), "不能把第三方历史记录当HK持久归属");
        check(!Hk3MachineOverviewHooks.needsLoadVerification(null, true), "未知机器不因恢复策略自动认领");
        check(!Hk3MachineOverviewService.recordObservationFailure(data, saved, true, 70), "未核验的已加载位置异常不发布实时故障");
        check(data.visible(oldTeam, id).equals(saved), "元数据异常保留原未加载快照与时间");
        check(Hk3MachineOverviewHooks.needsLoadVerification(data.visible(oldTeam, id), true), "异常后仍需后继持久归属核验");
        for (int repeat = 0; repeat < 10; repeat++) Hk3MachineOverviewHooks.overflow(data, dimension, delayed, true);
        check(data.visible(oldTeam, id).equals(saved), "反复饱和仍保持同一未加载快照");
        var visited = new HashSet<UUID>();
        boolean reachedRecovery = false;
        for (int turn = 0; turn < 65; turn++) {
            var batch = data.refreshBatch(64);
            check(batch.size() <= 64, "恢复候选仍由既有64项预算轮转");
            for (var entry : batch) {
                visited.add(entry.id());
                if (entry.id().equals(id)) reachedRecovery |= Hk3MachineOverviewHooks.needsLoadVerification(entry, true);
            }
        }
        check(visited.size() == 4097 && reachedRecovery, "过载条目仍能从原账本到达后继复核入口");
        check(data.page(oldTeam, 0, 4, "all").total() == 4097, "延迟恢复不增加重复目录行");
        check(data.visible(oldTeam, id).state() == State.UNLOADED, "仅轮转不会越过后继身份复核伪装已加载");
        data.register(nextTeam, dimension, delayed, descriptor, new Observation(State.UNKNOWN, "后继复核恢复"), 80, true);
        check(data.visible(oldTeam, id) == null && data.visible(nextTeam, id).loaded(), "可信恢复可更新归属且立即撤旧队");
        check(!Hk3MachineOverviewHooks.needsLoadVerification(data.visible(nextTeam, id), true), "可信恢复后停止重排候选");
        check(Hk3MachineOverviewService.recordObservationFailure(data, data.visible(nextTeam, id), true, 90), "原可信实时记录首次故障可以告警");
        var failed = data.visible(nextTeam, id);
        check(failed.loaded() && failed.state() == State.UNKNOWN && failed.observedAt() == 90, "可信实时记录故障准确降为未知");
        check(!Hk3MachineOverviewService.recordObservationFailure(data, failed, true, 91), "连续同故障不重复告警");
        check(Hk3MachineOverviewService.recordObservationFailure(data, data.visible(nextTeam, id), false, 92), "加载检查失败撤销可信实时状态");
        check(data.visible(nextTeam, id).state() == State.UNLOADED && data.visible(nextTeam, id).observedAt() == 91, "加载失败保留上次记录时间");
        Hk3MachineOverviewHooks.overflow(data, dimension, delayed, false);
        check(data.visible(nextTeam, id) == null, "非加载替换过载仍撤销不确定索引");
        Hk3MachineOverviewHooks.overflow(data, dimension, 999999, true);
        check(data.entry(dimension, 999999) == null, "未登记加载超额仍不凭空新增归属");
        return checks;
    }
    private static void check(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
        checks++;
    }
}
