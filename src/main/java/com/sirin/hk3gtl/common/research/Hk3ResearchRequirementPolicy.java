package com.sirin.hk3gtl.common.research;

import java.util.ArrayList;
import java.util.Collection;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Objects;
import java.util.function.Predicate;

/**
 * 【变更记录 #1】2026-10-17 15:07:22（内测5修订163）
 * 新增：研究门槛的纯Java合并和全量判定策略，执行、JEI和导出共用同一结果。
 * 用途：旧研究、未知研究、错类型批次元数据不能因已存完成标记或空列表回退而放行。
 * 边界：仅判定知识门槛，不替代研究付款、归属、成型、能源及真实实验验收。
 */
public final class Hk3ResearchRequirementPolicy {
    public static final String METADATA_KEY = "hk3gtlResearchRequirements";
    public static final String MALFORMED_METADATA = "<invalid research requirements metadata>";

    private Hk3ResearchRequirementPolicy() {}

    public record Requirements(List<String> requirements, List<String> invalid) {
        public Requirements {
            requirements = List.copyOf(requirements);
            invalid = List.copyOf(invalid);
        }
        public boolean valid() { return invalid.isEmpty(); }
    }

    public record Evaluation(int completed, int total, List<String> missing, boolean valid) {
        public Evaluation { missing = List.copyOf(missing); }
        public boolean allowed() { return valid && missing.isEmpty(); }
    }

    /** 批次可缺省；存在但不是字符串列表时必须保留错误，不能转成“无门槛”。 */
    public static Requirements collect(Collection<String> registered, Collection<?> batch,
                                       boolean malformedBatch, Predicate<String> current) {
        Objects.requireNonNull(current, "current");
        var requirements = new LinkedHashSet<String>();
        var invalid = new LinkedHashSet<String>();
        if (malformedBatch) invalid.add(MALFORMED_METADATA);
        for (Object value : registered) add(value, current, requirements, invalid);
        for (Object value : batch) add(value, current, requirements, invalid);
        return new Requirements(List.copyOf(requirements), List.copyOf(invalid));
    }

    private static void add(Object value, Predicate<String> current,
                            LinkedHashSet<String> requirements, LinkedHashSet<String> invalid) {
        if (!(value instanceof String id)) {
            invalid.add(MALFORMED_METADATA);
            return;
        }
        requirements.add(id);
        if (!current.test(id)) invalid.add(id);
    }

    /** 不调用未知研究的完成查询，避免旧个人NBT完成标记成为授权依据。 */
    public static Evaluation evaluate(Requirements requirements, Predicate<String> completed) {
        Objects.requireNonNull(completed, "completed");
        int done = 0;
        var missing = new ArrayList<String>();
        for (String id : requirements.requirements()) {
            if (!requirements.invalid().contains(id) && completed.test(id)) done++;
            else missing.add(id);
        }
        return new Evaluation(done, requirements.requirements().size(), missing, requirements.valid());
    }
}
