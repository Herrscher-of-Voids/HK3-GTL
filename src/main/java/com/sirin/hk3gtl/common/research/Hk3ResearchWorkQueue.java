package com.sirin.hk3gtl.common.research;

/**
 * 【文件职责／本轮边界】增加原任务取消及归属快照，正式课题与独立实验共享槽位、持久化进度和重复tick防护。
 */


import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;
import java.util.function.BooleanSupplier;
import java.util.function.Predicate;

public final class Hk3ResearchWorkQueue {
    public enum Outcome { MISSING, PAUSED, DUPLICATE_TICK, RUNNING, WAITING_COMPLETION, STAGE_COMPLETED, COMPLETED }

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

    public record Snapshot(Quote quote, double progress, long order, UUID id) {}
    public record Entry(UUID scope, Snapshot snapshot) {}
    public java.util.List<Entry> entries() {
        return jobs.entrySet().stream().map(e -> new Entry(e.getKey().owner(),
                e.getValue().snapshot())).toList();
    }
    private static String slotTopic(String topic) {
        return topic.startsWith("LAB-ERM-") ? "LAB-ERM" : topic;
    }
    public int usedSlots(String facility) {
        return (int) jobs.values().stream().filter(job -> job.quote.facility().equals(facility))
                .map(job -> slotTopic(job.quote.topic())).distinct().count();
    }
    public boolean cancel(UUID scope, String topic) {
        rejectReentry();
        return jobs.remove(new Key(scope, topic)) != null;
    }
    private record Key(UUID owner, String topic) {}
    private static final class Job {
        private final Quote quote;
        private final long order;
        private final UUID id;
        private double progress;
        private long lastTick = Long.MIN_VALUE;
        private Job(Quote quote, long order, UUID id) { this.quote = quote; this.order = order; this.id = id; }
        private Snapshot snapshot() { return new Snapshot(quote, progress, order, id); }
    }
    private final Map<Key, Job> jobs = new LinkedHashMap<>();
    private long nextOrder;
    private boolean inCallback;

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
        for (var entry : jobs.entrySet()) {
            Quote existing = entry.getValue().quote;
            if (!existing.facility().equals(quote.facility())) continue;
            // 运行中的设施不能换所有者或阶级，避免借槽与升级绕过。
            if (!entry.getKey().owner().equals(owner) || existing.lab() != quote.lab()) return false;
        }
        boolean continuing = jobs.values().stream().anyMatch(job -> job.quote.facility().equals(quote.facility())
                && slotTopic(job.quote.topic()).equals(slotTopic(quote.topic())));
        if (!continuing && usedSlots(quote.facility()) >= Hk3ResearchMath.slots(quote.lab())) return false;
        if (!call(debit)) return false;
        Job job = new Job(quote, nextOrder++, UUID.randomUUID());
        jobs.put(key, job);
        return true;
    }

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
        if (job.progress < job.quote.ticks()) {
            if (!call(debitEnergy)) return Outcome.PAUSED;
            job.progress = Math.min(job.quote.ticks(), job.progress + speed);
        }
        job.lastTick = tick;
        if (job.progress < job.quote.ticks()) return Outcome.RUNNING;
        if (!call(complete)) return Outcome.WAITING_COMPLETION;
        jobs.remove(key);
        return Outcome.COMPLETED;
    }

    private boolean call(BooleanSupplier callback) {
        inCallback = true;
        try { return callback.getAsBoolean(); }
        finally { inCallback = false; }
    }
    private void rejectReentry() {
        if (inCallback) throw new IllegalStateException("Research callback reentry");
    }

    public Snapshot snapshot(UUID owner, String topic) {
        Job job = jobs.get(new Key(owner, topic));
        return job == null ? null : job.snapshot();
    }

    public java.util.List<Snapshot> active(UUID owner, String facility) {
        return jobs.entrySet().stream().filter(e -> e.getKey().owner().equals(owner)
                && e.getValue().quote.facility().equals(facility))
                .map(e -> e.getValue().snapshot()).toList();
    }

    /** 固定插入顺序序列化，费用/进度/最后tick一并保存；不读墙钟。 / Serialize receipts, progress and tick in insertion order, never wall-clock time. */
    public CompoundTag save() {
        CompoundTag tag = new CompoundTag();
        tag.putInt("Version", 1);
        tag.putLong("NextOrder", nextOrder);
        ListTag list = new ListTag();
        jobs.forEach((key, job) -> {
            Quote q = job.quote;
            CompoundTag item = new CompoundTag();
            item.putUUID("Owner", key.owner()); item.putString("Topic", q.topic());
            item.putString("Facility", q.facility()); item.putInt("Lab", q.lab());
            item.putLong("Ticks", q.ticks()); item.putLong("EUt", q.eut());
            item.putString("Payment", q.payment()); item.put("Paid", q.paid());
            item.putDouble("Progress", job.progress); item.putLong("LastTick", job.lastTick);
            item.putLong("Order", job.order); item.putUUID("Id", job.id);
            list.add(item);
        });
        tag.put("Jobs", list);
        return tag;
    }

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
            long order = item.contains("Order", Tag.TAG_LONG) ? item.getLong("Order") : i;
            UUID id = item.hasUUID("Id") ? item.getUUID("Id") : UUID.nameUUIDFromBytes(
                    (owner + "/" + q.topic() + "/" + q.facility()).getBytes(java.nio.charset.StandardCharsets.UTF_8));
            Job job = new Job(q, order, id); job.progress = item.getDouble("Progress"); job.lastTick = item.getLong("LastTick");
            result.nextOrder = Math.max(result.nextOrder, order + 1);
            if (!Double.isFinite(job.progress) || job.progress < 0 || job.progress > q.ticks()
                    || (job.lastTick < 0 && job.lastTick != Long.MIN_VALUE)) throw new IllegalArgumentException("Invalid research progress");
            if (result.jobs.putIfAbsent(new Key(owner, q.topic()), job) != null)
                throw new IllegalArgumentException("Duplicate paid research");
            if (result.usedSlots(q.facility()) > Hk3ResearchMath.slots(q.lab())) throw new IllegalArgumentException("Research capacity exceeded");
            for (var entry : result.jobs.entrySet()) {
                Quote other = entry.getValue().quote;
                if (other.facility().equals(q.facility()) && (!entry.getKey().owner().equals(owner) || other.lab() != q.lab()))
                    throw new IllegalArgumentException("Conflicting research facility binding");
            }
        }
        result.nextOrder = Math.max(result.nextOrder, tag.getLong("NextOrder"));
        return result;
    }

    private static void requireType(CompoundTag tag, String field, int type) {
        if (!tag.contains(field, type)) throw new IllegalArgumentException("Invalid research field: " + field);
    }
}

