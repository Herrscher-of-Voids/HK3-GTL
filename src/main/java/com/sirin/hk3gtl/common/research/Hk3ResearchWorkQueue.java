package com.sirin.hk3gtl.common.research;

/**
 * 【文件职责／本轮边界】增加原任务取消及归属快照，正式课题与独立实验共享槽位、持久化进度和重复tick防护。
 * 【变更记录 #2】2026-09-29 21:06:40（第 2 次编号备注 · 内测5修订100）
 * 删除：取消已被批准规则替代的研究个人独占、旧数值或在线限定分支；历史备注与其他系统保留。
 * 新增／修改：增加原任务取消及归属快照，正式课题与独立实验共享槽位、持久化进度和重复tick防护。
 * 用途：接通实际证据→付款→研究完成与权限检查；不授予缺真实证据的课题。
 * 边界：编译和账本测试不代表游戏验收；S02至S05正式结构及未接线课题仍未完成。
 * 追溯：logs/research-mainline-r100；R100_FINAL_RECORD。
 */

/** 【变更记录 · 内测5修订100】2026-09-29：落实已批准研究费用、三公式及离线账户规则。 */

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;
import java.util.function.BooleanSupplier;
import java.util.function.Predicate;

/** 中文说明：该处说明已按当前代码行为整理。*/
/**
 * 【变更记录 #1】2026-09-27 04:14:21（第 1 次编号备注 · 内测5修订90）
 * 删除：无。新增：完成状态查询也受重入锁保护，拒绝空白课题。
 * 修改：保留既有数据键、配方数量和研究前置，仅修复一致性边界。
 * 用途：防止回调重入或系列专用输入破坏已确认的通用规则。
 */
public final class Hk3ResearchWorkQueue {
    public enum Outcome { MISSING, PAUSED, DUPLICATE_TICK, RUNNING, WAITING_COMPLETION, COMPLETED }

    /** 中文说明：该处备注已按当前代码行为整理，不使用问号占位。*/
    public record Quote(String topic, String facility, int lab, long ticks, long eut,
                        String payment, CompoundTag paid) {
        public Quote {
            Hk3ResearchMath.slots(lab);
            if (topic == null || topic.isBlank() || facility == null || facility.isBlank() || ticks < 1
                    || ticks > (1L << 53) || eut < 1
                    || !("points".equals(payment) || "materials".equals(payment))
                    || paid == null || paid.isEmpty()) throw new IllegalArgumentException("Invalid research quote");
            paid = paid.copy();
        }
        /** 不向GUI/调用者暴露可变支付快照。 / Never expose mutable receipt storage. */
        @Override public CompoundTag paid() { return paid.copy(); }
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public record Snapshot(Quote quote, double progress) {}
    /** 修订100 · 2026-09-29：暴露不可变归属快照，取消只移除实际存在的任务。 */
    public record Entry(UUID scope, Snapshot snapshot) {}
    public java.util.List<Entry> entries() {
        return jobs.entrySet().stream().map(e -> new Entry(e.getKey().owner(),
                new Snapshot(e.getValue().quote, e.getValue().progress))).toList();
    }
    public boolean cancel(UUID scope, String topic) {
        rejectReentry();
        return jobs.remove(new Key(scope, topic)) != null;
    }
    private record Key(UUID owner, String topic) {}
    private static final class Job {
        private final Quote quote;
        private double progress;
        private long lastTick = Long.MIN_VALUE;
        private Job(Quote quote) { this.quote = quote; }
    }
    private final Map<Key, Job> jobs = new LinkedHashMap<>();
    private boolean inCallback;

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public boolean start(UUID owner, Quote quote, Predicate<String> completed, boolean evidenceReady, BooleanSupplier debit) {
        rejectReentry();
        if (owner == null) throw new IllegalArgumentException("Missing owner");
        var experiment = Hk3LabExperimentRules.get(quote.topic());
        if (experiment!=null && (quote.lab()<experiment.lab() || quote.ticks()!=experiment.ticks()
                || !quote.payment().equals("materials"))) return false;
        var topic = Hk3ResearchCatalog.bundled().get(experiment==null?quote.topic():experiment.research());
        Key key = new Key(owner, quote.topic());
        if (topic == null || quote.lab() < topic.lab() || !evidenceReady || call(() -> completed.test(topic.id()))
                || jobs.containsKey(key) || !call(() -> topic.prerequisites().stream().allMatch(completed))) return false;
        int used = 0;
        for (var entry : jobs.entrySet()) {
            Quote existing = entry.getValue().quote;
            if (!existing.facility().equals(quote.facility())) continue;
            // 运行中的设施不能换所有者或阶级，避免借槽与升级绕过。
            // 中文备注：该处备注已按当前代码行为整理，不使用问号占位。
            if (!entry.getKey().owner().equals(owner) || existing.lab() != quote.lab()) return false;
            used++;
        }
        if (used >= Hk3ResearchMath.slots(quote.lab())) return false;
        Job job = new Job(quote);
        if (!call(debit)) return false;
        jobs.put(key, job);
        return true;
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public Outcome advance(UUID owner, String topic, String facility, long tick, boolean formed, boolean online,
                           double speed, BooleanSupplier debitEnergy, BooleanSupplier complete) {
        rejectReentry();
        if (tick < 0 || !Double.isFinite(speed) || speed <= 0 || speed > 3)
            throw new IllegalArgumentException("Invalid tick or research speed");
        Key key = new Key(owner, topic);
        Job job = jobs.get(key);
        if (job == null) return Outcome.MISSING;
        if (!job.quote.facility().equals(facility) || !formed || !online) return Outcome.PAUSED;
        if (tick <= job.lastTick) return Outcome.DUPLICATE_TICK;
        job.lastTick = tick;
        if (job.progress < job.quote.ticks()) {
            if (!call(debitEnergy)) return Outcome.PAUSED;
            job.progress = Math.min(job.quote.ticks(), job.progress + speed);
        }
        if (job.progress < job.quote.ticks()) return Outcome.RUNNING;
        if (!call(complete)) return Outcome.WAITING_COMPLETION;
        jobs.remove(key);
        return Outcome.COMPLETED;
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    private boolean call(BooleanSupplier callback) {
        inCallback = true;
        try { return callback.getAsBoolean(); }
        finally { inCallback = false; }
    }
    private void rejectReentry() {
        if (inCallback) throw new IllegalStateException("Research callback reentry");
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public Snapshot snapshot(UUID owner, String topic) {
        Job job = jobs.get(new Key(owner, topic));
        return job == null ? null : new Snapshot(job.quote, job.progress);
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public java.util.List<Snapshot> active(UUID owner, String facility) {
        return jobs.entrySet().stream().filter(e -> e.getKey().owner().equals(owner)
                && e.getValue().quote.facility().equals(facility))
                .map(e -> new Snapshot(e.getValue().quote, e.getValue().progress)).toList();
    }

    /** 固定插入顺序序列化，费用/进度/最后tick一并保存；不读墙钟。 / Serialize receipts, progress and tick in insertion order, never wall-clock time. */
    public CompoundTag save() {
        CompoundTag tag = new CompoundTag();
        tag.putInt("Version", 1);
        ListTag list = new ListTag();
        jobs.forEach((key, job) -> {
            Quote q = job.quote;
            CompoundTag item = new CompoundTag();
            item.putUUID("Owner", key.owner()); item.putString("Topic", q.topic());
            item.putString("Facility", q.facility()); item.putInt("Lab", q.lab());
            item.putLong("Ticks", q.ticks()); item.putLong("EUt", q.eut());
            item.putString("Payment", q.payment()); item.put("Paid", q.paid());
            item.putDouble("Progress", job.progress); item.putLong("LastTick", job.lastTick);
            list.add(item);
        });
        tag.put("Jobs", list);
        return tag;
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public static Hk3ResearchWorkQueue load(CompoundTag tag) {
        if (!tag.contains("Version", Tag.TAG_INT) || tag.getInt("Version") != 1
                || !tag.contains("Jobs", Tag.TAG_LIST)) throw new IllegalArgumentException("Invalid research queue format");
        ListTag list = tag.getList("Jobs", Tag.TAG_COMPOUND);
        if (list.size() != ((ListTag) tag.get("Jobs")).size()) throw new IllegalArgumentException("Invalid job list");
        Hk3ResearchWorkQueue result = new Hk3ResearchWorkQueue();
        for (int i = 0; i < list.size(); i++) {
            CompoundTag item = list.getCompound(i);
            for (String field : new String[]{"Topic", "Facility", "Payment"}) requireType(item, field, Tag.TAG_STRING);
            for (String field : new String[]{"Ticks", "EUt", "LastTick"}) requireType(item, field, Tag.TAG_LONG);
            requireType(item, "Lab", Tag.TAG_INT); requireType(item, "Progress", Tag.TAG_DOUBLE);
            requireType(item, "Paid", Tag.TAG_COMPOUND);
            if (!item.hasUUID("Owner")) throw new IllegalArgumentException("Missing research owner");
            UUID owner = item.getUUID("Owner");
            Quote q = new Quote(item.getString("Topic"), item.getString("Facility"), item.getInt("Lab"),
                    item.getLong("Ticks"), item.getLong("EUt"), item.getString("Payment"), item.getCompound("Paid"));
            Job job = new Job(q); job.progress = item.getDouble("Progress"); job.lastTick = item.getLong("LastTick");
            if (!Double.isFinite(job.progress) || job.progress < 0 || job.progress > q.ticks()
                    || (job.lastTick < 0 && job.lastTick != Long.MIN_VALUE)) throw new IllegalArgumentException("Invalid research progress");
            if (result.jobs.putIfAbsent(new Key(owner, q.topic()), job) != null)
                throw new IllegalArgumentException("Duplicate paid research");
            long used = result.jobs.entrySet().stream().filter(e -> e.getValue().quote.facility().equals(q.facility())).count();
            if (used > Hk3ResearchMath.slots(q.lab())) throw new IllegalArgumentException("Research capacity exceeded");
            for (var entry : result.jobs.entrySet()) {
                Quote other = entry.getValue().quote;
                if (other.facility().equals(q.facility()) && (!entry.getKey().owner().equals(owner) || other.lab() != q.lab()))
                    throw new IllegalArgumentException("Conflicting research facility binding");
            }
        }
        return result;
    }

    private static void requireType(CompoundTag tag, String field, int type) {
        if (!tag.contains(field, type)) throw new IllegalArgumentException("Invalid research field: " + field);
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
