package com.sirin.hk3gtl.common.integration.ae.exact;

import java.math.BigInteger;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** 压缩程序游标；推进次数取决于真实投料，不展开巨量循环。 */
public final class Hk3ExactProgramCursor<R> {
    public record Position(int step, int recipe, BigInteger repetitions, boolean waiting) {}

    private final List<Hk3ExactPlanner.Step<R>> steps;
    private int step;
    private int recipe;
    private BigInteger repetitions;
    private boolean waiting;

    public Hk3ExactProgramCursor(List<Hk3ExactPlanner.Step<R>> steps) {
        this(steps, new Position(0, 0, steps.isEmpty() ? BigInteger.ZERO : steps.get(0).repetitions(), false));
    }

    public Hk3ExactProgramCursor(List<Hk3ExactPlanner.Step<R>> steps, Position saved) {
        this.steps = List.copyOf(steps);
        for (var part : steps) {
            if (part.recipes().isEmpty() || part.repetitions().signum() <= 0)
                throw new IllegalArgumentException("执行程序含空步骤或非正重复次数");
        }
        step = saved.step(); recipe = saved.recipe(); repetitions = saved.repetitions(); waiting = saved.waiting();
        if (step < 0 || step > steps.size() || repetitions == null
                || (step == steps.size() ? recipe != 0 || repetitions.signum() != 0
                : recipe < 0 || recipe >= steps.get(step).recipes().size() || repetitions.signum() <= 0
                    || repetitions.compareTo(steps.get(step).repetitions()) > 0))
            throw new IllegalArgumentException("执行程序游标损坏，不能重置后重发");
    }

    public Position position() { return new Position(step, recipe, repetitions, waiting); }
    public boolean waiting() { return waiting; }
    public boolean exhausted() { return step == steps.size(); }
    public boolean done() { return exhausted() && !waiting; }
    public R current() { return waiting || exhausted() ? null : steps.get(step).recipes().get(recipe); }

    public void pushed() {
        if (current() == null) throw new IllegalStateException("前一步尚未回流或程序已结束");
        if (++recipe == steps.get(step).recipes().size()) {
            recipe = 0;
            repetitions = repetitions.subtract(BigInteger.ONE);
            if (repetitions.signum() == 0 && ++step < steps.size()) repetitions = steps.get(step).repetitions();
        }
        waiting = true;
    }

    public void returned() { waiting = false; }

    public Map<R, BigInteger> remainingCounts() {
        Map<R, BigInteger> counts = new LinkedHashMap<>();
        for (int i = step; i < steps.size(); i++) {
            var part = steps.get(i);
            for (int j = 0; j < part.recipes().size(); j++) {
                BigInteger count = i == step ? repetitions.subtract(j < recipe ? BigInteger.ONE : BigInteger.ZERO)
                        : part.repetitions();
                if (count.signum() > 0) counts.merge(part.recipes().get(j), count, BigInteger::add);
            }
        }
        return Map.copyOf(counts);
    }
}
