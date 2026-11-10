package com.sirin.hk3gtl.common.worldbubble;



import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;

import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;

/**
 * 【文件职责】真实目标与模拟批次的公共状态账本，供服务端机器后续接入；不发放物品。
 * 【变更记录 #1】2026-09-27 04:16:00（第 1 次备注 · 内测5修订90）
 * 删除：无。新增：稳定目标身份、十次采掘、捕获/终止约束、独立模拟批次及持久事务收据。
 * 修改：无旧存档迁移，无旧配方停用；仅新增可复用底层。状态由已确认事务重放恢复。
 * 用途：同一事务重试不能计次或结算两遍，失败预留可取消但保留编号，目标有待办时禁止冲突操作。
 * 边界：调用方必须在服务器线程校验权限、实际工序与费用；actor仅记操作归属，不定义团队产权。
 * 收据是待交付事实；交付方必须按事务ID幂等接收后确认，不宣称跨存档物品交付具有崩溃原子性。
 */
/**
 * 【变更记录 #2】2026-09-27 04:24:00（第 2 次备注 · 内测5修订90）
 * 删除：每次预留全表扫描。新增：领域与目标组成的待办索引。
 * 修改：预留写入索引，结算/取消释放；载入时随事务重建，不保存冗余字段。
 * 用途：防冲突查询保持常数时间，避免大量模拟批次造成载入平方级扫描。
 */
/**
 * 【变更记录 #3】2026-09-29 23:37:35（内测5修订101）
 * 删除：本轮被替代的单前置或旧提示分支；其余历史保留。
 * 新增／修改：模拟创建保留服务端来源回执，跨重启保留同批次身份。
 * 用途：补足研究接线并如实保留未接物理执行器及结构审批边界。
 * 追溯：logs/research-mainline-r101；R101_FINAL_RECORD。
 */
public final class Hk3WorldBubbleLedger {
    public static final int MAX_MINING = 10;
    public enum Domain { REAL, SIMULATED }
    public enum Action { MINE, CAPTURE, TERMINATE_REAL, STABILIZE_SIMULATION, TERMINATE_SIMULATION }
    public enum Phase { RESERVED, SETTLED, CANCELLED }
    public enum RealState { AVAILABLE, CAPTURED, TERMINATED }
    public enum SimulationState { CREATED, STABLE, TERMINATED }
    public record RealSnapshot(UUID id, String identity, RealState state, int miningCount) {}
    public record SimulationSnapshot(UUID id, UUID creator, String origin, SimulationState state, CompoundTag creationReceipt) {
        public SimulationSnapshot { creationReceipt=creationReceipt.copy(); }
        @Override public CompoundTag creationReceipt(){return creationReceipt.copy();}
    }
    public record Transaction(UUID id, UUID actor, Domain domain, UUID target, Action action,
                              Phase phase, CompoundTag receipt, boolean delivered) {
        public Transaction { receipt = receipt.copy(); }
        @Override public CompoundTag receipt() { return receipt.copy(); }
    }
    private static final class RealTarget {
        private final String identity;
        private RealState state = RealState.AVAILABLE;
        private int mined;
        private RealTarget(String identity) { this.identity = identity; }
    }
    private static final class Simulation {
        private final UUID creator;
        private final String origin;
        private final CompoundTag creationReceipt;
        private SimulationState state = SimulationState.CREATED;
        private Simulation(UUID creator, String origin,CompoundTag receipt) {
            this.creator = creator; this.origin = origin; this.creationReceipt=receipt.copy();
        }
    }
    private final Map<UUID, RealTarget> real = new LinkedHashMap<>();
    private final Map<UUID, Simulation> simulated = new LinkedHashMap<>();
    private final Map<UUID, Transaction> transactions = new LinkedHashMap<>();
    private record TargetKey(Domain domain, UUID id) {}
    private final Map<TargetKey, UUID> pending = new LinkedHashMap<>();
    private Runnable changed = () -> {};

    /** identity必须由可信坐标解析器给出规范键，不能用物品NBT或每次随机UUID冒充目标身份。 */
    public UUID discover(String identity) {
        text(identity);
        UUID id = UUID.nameUUIDFromBytes(("hk3gtl:real-world-bubble/" + identity).getBytes(StandardCharsets.UTF_8));
        RealTarget old = real.get(id);
        if (old != null) {
            if (!old.identity.equals(identity)) throw invalid("Target identity collision");
            return id;
        }
        real.put(id, new RealTarget(identity)); changed.run(); return id;
    }

    /** 每次已完成模拟构筑采用独立批次ID；重试沿用该ID，已终止批次不能重新初始化。 */
    public void createSimulation(UUID batch, UUID creator, String origin) {
        createSimulation(batch,creator,origin,new CompoundTag());
    }
    /** 修订101：真实构筑保存投入产出回执；旧空回执批次不能冒充已验证构筑。 */
    public void createSimulation(UUID batch, UUID creator, String origin,CompoundTag receipt) {
        Objects.requireNonNull(batch); Objects.requireNonNull(creator); text(origin);
        Simulation old = simulated.get(batch);
        if (old != null) {
            if (!old.creator.equals(creator) || !old.origin.equals(origin) || !old.creationReceipt.equals(receipt)) throw invalid("Simulation identity conflict");
            return;
        }
        simulated.put(batch, new Simulation(creator, origin,receipt)); changed.run();
    }

    /** 预留本次操作，不扣费、不计次数。每个目标只允许一项待办，防止采掘与捕获并行结算。 */
    public Transaction begin(UUID operation, UUID actor, Domain domain, UUID target, Action action) {
        Objects.requireNonNull(operation); Objects.requireNonNull(actor); Objects.requireNonNull(domain);
        Objects.requireNonNull(target); Objects.requireNonNull(action);
        Transaction existing = transactions.get(operation);
        if (existing != null) {
            if (!existing.actor().equals(actor) || existing.domain() != domain
                    || !existing.target().equals(target) || existing.action() != action)
                throw invalid("Operation identity conflict");
            return existing;
        }
        TargetKey key = new TargetKey(domain, target);
        if (pending.containsKey(key)) throw invalid("Target has pending operation");
        validateTransition(domain, target, action);
        Transaction tx = new Transaction(operation, actor, domain, target, action, Phase.RESERVED, new CompoundTag(), false);
        transactions.put(operation, tx); pending.put(key, operation); changed.run(); return tx;
    }

    /** 工序实际成功后提交固定收据与状态；空资源结果是否计次由后续工艺裁定，此层不抽资源。 */
    public Transaction settle(UUID operation, UUID actor, CompoundTag receipt) {
        Objects.requireNonNull(receipt);
        if (receipt.isEmpty()) throw invalid("Missing settlement receipt");
        Transaction tx = require(operation, actor);
        if (tx.phase() == Phase.SETTLED) {
            if (!tx.receipt().equals(receipt)) throw invalid("Settlement receipt conflict");
            return tx;
        }
        if (tx.phase() != Phase.RESERVED) throw invalid("Cancelled operation cannot settle");
        validateTransition(tx.domain(), tx.target(), tx.action());
        // 所有校验及收据复制先完成，状态与收据在同一账本中变更，不调用外部支付/发奖回调。
        Transaction settled = new Transaction(tx.id(), tx.actor(), tx.domain(), tx.target(), tx.action(), Phase.SETTLED, receipt, false);
        if (tx.domain() == Domain.REAL) {
            RealTarget target = real.get(tx.target());
            switch (tx.action()) {
                case MINE -> target.mined++;
                case CAPTURE -> target.state = RealState.CAPTURED;
                case TERMINATE_REAL -> target.state = RealState.TERMINATED;
                default -> throw invalid("Invalid real action");
            }
        } else {
            simulated.get(tx.target()).state = tx.action() == Action.STABILIZE_SIMULATION
                    ? SimulationState.STABLE : SimulationState.TERMINATED;
        }
        transactions.put(operation, settled); pending.remove(new TargetKey(tx.domain(), tx.target()));
        changed.run(); return settled;
    }

    /** 取消只释放未结算的预留；不决定退款，保留事务编号防止旧请求被重新使用。 */
    public void cancel(UUID operation, UUID actor) {
        Transaction tx = require(operation, actor);
        if (tx.phase() == Phase.CANCELLED) return;
        if (tx.phase() != Phase.RESERVED) throw invalid("Settled operation cannot cancel");
        transactions.put(operation, new Transaction(tx.id(), tx.actor(), tx.domain(), tx.target(), tx.action(),
                Phase.CANCELLED, new CompoundTag(), false));
        pending.remove(new TargetKey(tx.domain(), tx.target())); changed.run();
    }

    /** 下游按事务ID幂等接收后确认；本方法不插入玩家/AE库存，也不自动重发物品。 */
    public boolean acknowledge(UUID operation, UUID actor) {
        Transaction tx = require(operation, actor);
        if (tx.phase() != Phase.SETTLED) throw invalid("No settled receipt");
        if (tx.delivered()) return false;
        transactions.put(operation, new Transaction(tx.id(), tx.actor(), tx.domain(), tx.target(), tx.action(),
                tx.phase(), tx.receipt(), true)); changed.run(); return true;
    }

    public RealSnapshot real(UUID id) {
        RealTarget target = real.get(id);
        return target == null ? null : new RealSnapshot(id, target.identity, target.state, target.mined);
    }
    public SimulationSnapshot simulation(UUID id) {
        Simulation target = simulated.get(id);
        return target == null ? null : new SimulationSnapshot(id, target.creator, target.origin, target.state,target.creationReceipt);
    }
    public java.util.List<SimulationSnapshot> simulations(){return simulated.keySet().stream().map(this::simulation).toList();}
    public java.util.List<Transaction> settledTransactions(){return transactions.values().stream().filter(t->t.phase()==Phase.SETTLED).toList();}
    public Transaction transaction(UUID id) { return transactions.get(id); }
    public java.util.List<Transaction> pendingDeliveries(UUID actor) {
        return transactions.values().stream().filter(t -> t.actor().equals(actor)
                && t.phase() == Phase.SETTLED && !t.delivered()).toList();
    }

    private Transaction require(UUID operation, UUID actor) {
        Transaction tx = transactions.get(operation);
        if (tx == null || !tx.actor().equals(actor)) throw invalid("Unknown operation or actor");
        return tx;
    }
    private void validateTransition(Domain domain, UUID id, Action action) {
        if (domain == Domain.REAL) {
            RealTarget target = real.get(id);
            if (target == null) throw invalid("Unknown real target");
            boolean valid = switch (action) {
                case MINE -> target.state == RealState.AVAILABLE && target.mined < MAX_MINING;
                case CAPTURE -> target.state == RealState.AVAILABLE;
                case TERMINATE_REAL -> target.state == RealState.CAPTURED;
                default -> false;
            };
            if (!valid) throw invalid("Illegal real target transition");
        } else {
            Simulation target = simulated.get(id);
            if (target == null) throw invalid("Unknown simulation");
            boolean valid = action == Action.STABILIZE_SIMULATION && target.state == SimulationState.CREATED
                    || action == Action.TERMINATE_SIMULATION && target.state == SimulationState.STABLE;
            if (!valid) throw invalid("Illegal simulation transition");
        }
    }

    /** 仅保存身份和有序事务；读回时重放校验，避免状态计数和收据互相矛盾。 */
    public CompoundTag save() {
        CompoundTag root = new CompoundTag(); root.putInt("Version", 1);
        ListTag targets = new ListTag();
        real.forEach((id, target) -> {
            CompoundTag tag = new CompoundTag(); tag.putUUID("Id", id); tag.putString("Identity", target.identity); targets.add(tag);
        }); root.put("Real", targets);
        ListTag batches = new ListTag();
        simulated.forEach((id, target) -> {
            CompoundTag tag = new CompoundTag(); tag.putUUID("Id", id); tag.putUUID("Creator", target.creator);
            tag.putString("Origin", target.origin);tag.put("CreationReceipt",target.creationReceipt.copy()); batches.add(tag);
        }); root.put("Simulations", batches);
        ListTag operations = new ListTag();
        transactions.forEach((id, tx) -> {
            CompoundTag tag = new CompoundTag(); tag.putUUID("Id", id); tag.putUUID("Actor", tx.actor());
            tag.putUUID("Target", tx.target()); tag.putString("Domain", tx.domain().name());
            tag.putString("Action", tx.action().name()); tag.putString("Phase", tx.phase().name());
            tag.put("Receipt", tx.receipt()); tag.putBoolean("Delivered", tx.delivered()); operations.add(tag);
        }); root.put("Operations", operations); return root;
    }

    public static Hk3WorldBubbleLedger load(CompoundTag root) { return load(root, () -> {}); }

    /** 损坏/重复/未来版本一律拒绝；不静默删除玩家记录，不回退为可再次领奖的空账本。 */
    static Hk3WorldBubbleLedger load(CompoundTag root, Runnable changed) {
        requireType(root, "Version", Tag.TAG_INT);
        if (root.getInt("Version") != 1) throw invalid("Unsupported world bubble ledger version");
        Hk3WorldBubbleLedger ledger = new Hk3WorldBubbleLedger();
        for (Tag entry : list(root, "Real")) {
            CompoundTag tag = (CompoundTag) entry; UUID id = uuid(tag, "Id");
            requireType(tag, "Identity", Tag.TAG_STRING);
            if (ledger.real.containsKey(id) || !ledger.discover(tag.getString("Identity")).equals(id))
                throw invalid("Duplicate or noncanonical target identity");
        }
        for (Tag entry : list(root, "Simulations")) {
            CompoundTag tag = (CompoundTag) entry; UUID id = uuid(tag, "Id");
            requireType(tag, "Origin", Tag.TAG_STRING);
            if (ledger.simulated.containsKey(id)) throw invalid("Duplicate simulation");
            if(tag.contains("CreationReceipt")&&!tag.contains("CreationReceipt",Tag.TAG_COMPOUND))throw invalid("Invalid creation receipt");
            ledger.createSimulation(id, uuid(tag, "Creator"), tag.getString("Origin"),tag.getCompound("CreationReceipt"));
        }
        for (Tag entry : list(root, "Operations")) {
            CompoundTag tag = (CompoundTag) entry; UUID id = uuid(tag, "Id"), actor = uuid(tag, "Actor");
            for (String field : new String[]{"Domain", "Action", "Phase"}) requireType(tag, field, Tag.TAG_STRING);
            requireType(tag, "Receipt", Tag.TAG_COMPOUND); requireType(tag, "Delivered", Tag.TAG_BYTE);
            if (tag.getByte("Delivered") != 0 && tag.getByte("Delivered") != 1) throw invalid("Invalid delivery state");
            if (ledger.transactions.containsKey(id)) throw invalid("Duplicate operation");
            ledger.begin(id, actor, Domain.valueOf(tag.getString("Domain")), uuid(tag, "Target"), Action.valueOf(tag.getString("Action")));
            Phase phase = Phase.valueOf(tag.getString("Phase"));
            if (phase == Phase.SETTLED) {
                ledger.settle(id, actor, tag.getCompound("Receipt"));
                if (tag.getBoolean("Delivered")) ledger.acknowledge(id, actor);
            } else {
                if (!tag.getCompound("Receipt").isEmpty() || tag.getBoolean("Delivered")) throw invalid("Unsettled delivery");
                if (phase == Phase.CANCELLED) ledger.cancel(id, actor);
            }
        }
        ledger.changed = Objects.requireNonNull(changed); return ledger;
    }
    void onChange(Runnable changed) { this.changed = Objects.requireNonNull(changed); }
    private static ListTag list(CompoundTag root, String name) {
        requireType(root, name, Tag.TAG_LIST);
        ListTag list = root.getList(name, Tag.TAG_COMPOUND);
        if (list.size() != ((ListTag) root.get(name)).size()) throw invalid("Invalid list " + name);
        return list;
    }
    private static UUID uuid(CompoundTag tag, String field) {
        if (!tag.hasUUID(field)) throw invalid("Missing UUID " + field);
        return tag.getUUID(field);
    }
    private static void requireType(CompoundTag tag, String field, int type) {
        if (!tag.contains(field, type)) throw invalid("Invalid field " + field);
    }
    private static void text(String value) {
        if (value == null || value.isBlank() || !value.equals(value.trim()) || value.length() > 1024)
            throw invalid("Invalid identity text");
    }
    private static IllegalArgumentException invalid(String message) { return new IllegalArgumentException(message); }
}
