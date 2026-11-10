package com.sirin.hk3gtl.test.research;

import com.sirin.hk3gtl.common.research.Hk3ResearchRequirementPolicy;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * 【变更记录 #1】2026-10-17 15:07:57（内测5修订163）
 * 新增：全部前置、合并批次、未知旧ID、错误元数据及只读快照的纯Java反绕过回归。
 * 边界：验证生产入口与JEI共用的判定策略，不冒充游戏归属、扣料和输出实测。
 */
public final class ResearchRequirementPolicyTest {
    private static int checks;
    private static final Set<String> CURRENT = Set.of("RN-LES", "RN-CQS", "RN-NSP", "RN-RCA/circuit/max");
    private ResearchRequirementPolicyTest() {}

    public static void main(String[] args) {
        allRequirements(); mergedBatches(); rejectLegacyAndMalformed(); snapshots();
        System.out.println("ResearchRequirementPolicyTest：" + checks + " 项通过；未执行游戏验收");
    }

    private static void allRequirements() {
        var requirements = read(List.of("RN-LES", "RN-CQS"), List.of(), false);
        var partial = Hk3ResearchRequirementPolicy.evaluate(requirements, "RN-LES"::equals);
        check(!partial.allowed(), "完成第一前置不能绕过第二前置");
        check(partial.completed() == 1 && partial.total() == 2, "摘要统计全部前置");
        check(partial.missing().equals(List.of("RN-CQS")), "悬停详情保留具体缺失项");
        check(Hk3ResearchRequirementPolicy.evaluate(requirements, id -> true).allowed(), "全部前置完成可通过知识检查");
        check(Hk3ResearchRequirementPolicy.evaluate(read(List.of(), List.of(), false), id -> false).allowed(),
                "真正无研究门槛的配方保持可执行");
    }

    private static void mergedBatches() {
        var requirements = read(List.of("RN-LES", "RN-CQS"), List.of("RN-CQS", "RN-NSP", "RN-RCA/circuit/max"), false);
        check(requirements.requirements().equals(List.of("RN-LES", "RN-CQS", "RN-NSP", "RN-RCA/circuit/max")),
                "合并批次与注册表做有序并集且去重");
        var state = Hk3ResearchRequirementPolicy.evaluate(requirements,
                id -> Set.of("RN-LES", "RN-CQS").contains(id));
        check(!state.allowed() && state.missing().equals(List.of("RN-NSP", "RN-RCA/circuit/max")),
                "主配方完成不能丢掉子批次及逐级电路重建权益门槛");
        check(Hk3ResearchRequirementPolicy.evaluate(requirements, CURRENT::contains).allowed(),
                "合并批次全部真实门槛完成才通过");
    }

    private static void rejectLegacyAndMalformed() {
        for (String invalid : List.of("R1", "RN-UNKNOWN", "RN-RCA/circuit/unknown", "", " RN-LES")) {
            var requirements = read(List.of(invalid), List.of(), false);
            var queried = new AtomicInteger();
            var state = Hk3ResearchRequirementPolicy.evaluate(requirements, id -> {
                queried.incrementAndGet(); return true;
            });
            check(!state.allowed() && !requirements.valid() && requirements.invalid().equals(List.of(invalid)),
                    "旧、未知或变形ID即使存在完成标记也拒绝：" + invalid);
            check(queried.get() == 0, "未知ID不得调用旧完成状态查询：" + invalid);
        }
        var wrongList = read(List.of("RN-LES"), List.of(12, "RN-CQS"), false);
        check(!wrongList.valid() && !Hk3ResearchRequirementPolicy.evaluate(wrongList, id -> true).allowed(),
                "非字符串列表元素不能被静默忽略");
        var wrongTag = read(List.of(), List.of(), true);
        check(!wrongTag.valid() && !Hk3ResearchRequirementPolicy.evaluate(wrongTag, id -> true).allowed(),
                "错误批次NBT类型不能退化成零门槛");
        var unknownChild = read(List.of("RN-LES"), List.of("R2"), false);
        check(!Hk3ResearchRequirementPolicy.evaluate(unknownChild, id -> true).allowed(),
                "主配方合法不覆盖子批次旧ID错误");
    }

    private static void snapshots() {
        var registered = new ArrayList<>(List.of("RN-LES"));
        var batch = new ArrayList<>(List.of("RN-CQS"));
        var requirements = read(registered, batch, false);
        registered.clear(); batch.clear();
        check(requirements.requirements().equals(List.of("RN-LES", "RN-CQS")), "读取后快照不随输入变化");
        boolean immutable = false;
        try { requirements.requirements().clear(); } catch (UnsupportedOperationException expected) { immutable = true; }
        check(immutable, "导出和界面不能写回权限集合");
        var state = Hk3ResearchRequirementPolicy.evaluate(requirements, id -> false);
        immutable = false;
        try { state.missing().clear(); } catch (UnsupportedOperationException expected) { immutable = true; }
        check(immutable && !state.allowed(), "界面不能删除缺失项以伪造通过");
    }

    private static Hk3ResearchRequirementPolicy.Requirements read(List<String> registered, List<?> batch, boolean malformed) {
        return Hk3ResearchRequirementPolicy.collect(registered, batch, malformed, CURRENT::contains);
    }

    private static void check(boolean condition, String message) {
        checks++;
        if (!condition) throw new AssertionError(message);
    }
}
