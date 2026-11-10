package com.sirin.hk3gtl.common.overview;

import com.sirin.hk3gtl.common.util.Hk3SavedDataGuard;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;

import java.nio.charset.StandardCharsets;
import java.util.*;

/**
 * 【文件职责】保存按团队隔离的机器实例索引；索引不含库存、个人能源或研究成果。
 * 【变更记录 #1】2026-10-19 02:03:00（第1次备注 · 修订171）
 * 删除：无。新增：稳定位置身份、八种状态、筛选分页、卸载快照和严格存档校验。
 * 修改：无；读写在服务端入口串行执行，返回不可变副本，不创建区块加载请求。
 * 用途：为机器总览提供重启后仍可信的目录；重启时全部实例先视为未加载，直到真实观察刷新。
 */
/**
 * 【变更记录 #2】2026-10-31 19:02:08（第2次备注 · 修订190）
 * 删除：每页全账本筛选、排序及全部可见行临时列表。新增：团队有序目录和模块引用计数。
 * 修改：登记、换队、观察、卸载、删除和读档同步维护派生目录；存档格式不变，不缓存玩家权限。
 * 用途：总览只扫描当前团队，分页仅复制至多64行；账本和索引仍随登记量线性增长，非固定内存。
 */
public final class Hk3MachineOverviewData extends SavedData {
    public enum State {
        RUNNING("运行"), STOPPED("停机"), NEED_ENERGY("缺电"), NEED_INPUT("缺料"),
        UNLOADED("未加载"), UNFORMED("未成型"), UNADAPTED("未适配"), UNKNOWN("未知");
        private final String label;
        State(String label) { this.label = label; }
        public String label() { return label; }
        public String key() { return name().toLowerCase(Locale.ROOT); }
    }

    public record Descriptor(String registryId, String displayName, String controllerType, boolean adapted) {
        public Descriptor {
            requireId(registryId); requireText(displayName, 256); requireText(controllerType, 512);
        }
        public String module() { return registryId.substring(0, registryId.indexOf(':')); }
    }
    public record Observation(State state, String detail) {
        public Observation {
            Objects.requireNonNull(state); Objects.requireNonNull(detail);
            if (detail.length() > 1024) throw new IllegalArgumentException("机器状态说明过长");
        }
    }
    public record Entry(UUID id, UUID team, String dimension, long position, Descriptor descriptor,
                        Observation observation, long observedAt, boolean loaded) {
        public Entry {
            Objects.requireNonNull(id); Objects.requireNonNull(team); requireId(dimension);
            Objects.requireNonNull(descriptor); Objects.requireNonNull(observation);
            if (observedAt < 0 || !id.equals(identity(dimension, position)))
                throw new IllegalArgumentException("机器索引身份或时间错误");
        }
        public State state() { return loaded ? observation.state() : State.UNLOADED; }
    }
    public record Page(int page, int total, List<Entry> rows) {
        public Page { rows = List.copyOf(rows); }
    }

    private final Map<UUID, Entry> entries = new LinkedHashMap<>();
    private final ArrayDeque<UUID> refreshQueue = new ArrayDeque<>();
    private static final Comparator<Entry> ORDER = Comparator.comparing((Entry e) -> e.descriptor().registryId())
            .thenComparing(Entry::dimension).thenComparingLong(Entry::position);
    private static final class TeamIndex {
        final NavigableSet<Entry> rows = new TreeSet<>(ORDER);
        final NavigableMap<String, Integer> modules = new TreeMap<>();
    }
    private final Map<UUID, TeamIndex> teams = new HashMap<>();

    /** 所有调用均持账本锁；先撤销旧快照再登记新快照，避免换队和改名留下幽灵条目。 */
    private void index(Entry old, Entry next) {
        if (old != null) {
            TeamIndex team = teams.get(old.team());
            team.rows.remove(old);
            team.modules.compute(old.descriptor().module(), (module, count) -> count == 1 ? null : count - 1);
            if (team.rows.isEmpty()) teams.remove(old.team());
        }
        if (next != null) {
            TeamIndex team = teams.computeIfAbsent(next.team(), ignored -> new TeamIndex());
            team.rows.add(next);
            team.modules.merge(next.descriptor().module(), 1, Integer::sum);
        }
    }
    public static Hk3MachineOverviewData get(MinecraftServer server) {
        return Hk3SavedDataGuard.get(server, "hk3gtl_machine_overview", Hk3MachineOverviewData::load, Hk3MachineOverviewData::new);
    }
    public static UUID identity(String dimension, long position) {
        requireId(dimension);
        return UUID.nameUUIDFromBytes((dimension + "@" + position).getBytes(StandardCharsets.UTF_8));
    }
    public synchronized Entry entry(String dimension, long position) { return entries.get(identity(dimension, position)); }
    public synchronized Entry visible(UUID team, UUID id) {
        Entry row = entries.get(id); return row != null && row.team().equals(team) ? row : null;
    }

    /** 权威机器归属提供者可更新原队归属；普通现场绑定不得覆盖其他团队。 */
    public synchronized boolean register(UUID team, String dimension, long position, Descriptor descriptor,
                                         Observation observation, long tick, boolean authoritative) {
        UUID id = identity(dimension, position); Entry old = entries.get(id);
        if (old != null && !old.team().equals(team) && !authoritative) return false;
        Entry next = new Entry(id, team, dimension, position, descriptor, observation, tick, true);
        if (old == null) refreshQueue.addLast(id);
        if (!next.equals(old)) { index(old, next); entries.put(id, next); setDirty(); }
        return true;
    }
    public synchronized boolean observe(String dimension, long position, Descriptor descriptor, Observation observation, long tick) {
        Entry old = entry(dimension, position);
        return old != null && register(old.team(), dimension, position, descriptor, observation, tick, false);
    }
    public synchronized void unloaded(String dimension, long position) {
        Entry old = entry(dimension, position);
        if (old == null || !old.loaded()) return;
        Entry next = new Entry(old.id(), old.team(), old.dimension(), old.position(), old.descriptor(), old.observation(), old.observedAt(), false);
        index(old, next); entries.put(old.id(), next);
        setDirty();
    }
    public synchronized void remove(String dimension, long position) {
        UUID id = identity(dimension, position);
        Entry old = entries.remove(id);
        if (old != null) { index(old, null); refreshQueue.remove(id); setDirty(); }
    }
    public static boolean validFilter(String filter) {
        return filter != null && (filter.equals("all") || filter.matches("[a-z0-9_.-]{1,64}"));
    }
    public static boolean matches(Entry entry, String filter) {
        return filter.equals("all") || entry.descriptor().module().equals(filter) || entry.state().key().equals(filter);
    }
    /** 输出和复制开销为本队模块数O(M)，不扫描其他团队或复制机器条目。 */
    public synchronized List<String> sources(UUID team) {
        Objects.requireNonNull(team);
        TeamIndex index = teams.get(team);
        return index == null ? List.of() : List.copyOf(index.modules.navigableKeySet());
    }
    /** 最坏O(T)扫描本队T条目录，筛选计数与取页至多两遍；临时行数O(pageSize)，不加载区块。 */
    public synchronized Page page(UUID team, int requestedPage, int pageSize, String filter) {
        Objects.requireNonNull(team);
        if (pageSize < 1 || pageSize > 64 || !validFilter(filter)) throw new IllegalArgumentException("机器分页条件错误");
        TeamIndex index = teams.get(team);
        if (index == null) return new Page(0, 0, List.of());
        boolean all = filter.equals("all");
        int total = all ? index.rows.size() : 0;
        if (!all) for (Entry entry : index.rows) if (matches(entry, filter)) total++;
        int page = Math.min(Math.max(0, requestedPage), Math.max(0, (total - 1) / pageSize));
        List<Entry> rows = new ArrayList<>(pageSize);
        if (total == 0) return new Page(page, total, rows);
        int skip = page * pageSize;
        for (Entry entry : index.rows) {
            if (!all && !matches(entry, filter)) continue;
            if (skip > 0) { skip--; continue; }
            rows.add(entry);
            if (rows.size() == pageSize) break;
        }
        return new Page(page, total, rows);
    }

    /** 轮转固定预算的已登记位置；不枚举世界或区块，不因大基地把每次刷新变为全表校验。 */
    public synchronized List<Entry> refreshBatch(int budget) {
        if (budget < 0 || budget > 256) throw new IllegalArgumentException("机器刷新预算错误");
        List<Entry> out = new ArrayList<>(); int remaining = Math.min(budget, refreshQueue.size());
        while (remaining-- > 0) {
            UUID id = refreshQueue.removeFirst(); Entry entry = entries.get(id);
            if (entry != null) { refreshQueue.addLast(id); out.add(entry); }
        }
        return List.copyOf(out);
    }
    @Override public synchronized CompoundTag save(CompoundTag root) {
        root.putInt("Schema", 1); ListTag rows = new ListTag();
        for (Entry entry : entries.values()) {
            CompoundTag row = new CompoundTag(); row.putUUID("Id", entry.id()); row.putUUID("Team", entry.team());
            row.putString("Dimension", entry.dimension()); row.putLong("Position", entry.position());
            row.putString("Registry", entry.descriptor().registryId()); row.putString("Name", entry.descriptor().displayName());
            row.putString("ControllerType", entry.descriptor().controllerType()); row.putBoolean("Adapted", entry.descriptor().adapted());
            row.putString("State", entry.observation().state().name()); row.putString("Detail", entry.observation().detail());
            row.putLong("ObservedAt", entry.observedAt()); rows.add(row);
        }
        root.put("Machines", rows); return root;
    }
    public static Hk3MachineOverviewData load(CompoundTag root) {
        if (!root.contains("Schema", Tag.TAG_INT) || root.getInt("Schema") != 1 || !root.contains("Machines", Tag.TAG_LIST))
            throw new IllegalStateException("机器总览索引格式损坏");
        Hk3MachineOverviewData data = new Hk3MachineOverviewData(); Tag rawRows = root.get("Machines");
        if (!(rawRows instanceof ListTag rows) || (!rows.isEmpty() && rows.getElementType() != Tag.TAG_COMPOUND))
            throw new IllegalStateException("机器总览列表类型损坏");
        try {
            for (Tag raw : rows) {
                CompoundTag row = (CompoundTag) raw;
                if (!row.hasUUID("Id") || !row.hasUUID("Team") || !row.contains("Position", Tag.TAG_LONG)
                        || !row.contains("ObservedAt", Tag.TAG_LONG) || !row.contains("Adapted", Tag.TAG_BYTE))
                    throw new IllegalArgumentException("机器总览字段缺失");
                for (String key : List.of("Dimension", "Registry", "Name", "ControllerType", "State", "Detail"))
                    if (!row.contains(key, Tag.TAG_STRING)) throw new IllegalArgumentException("机器总览文字字段缺失");
                Descriptor descriptor = new Descriptor(row.getString("Registry"), row.getString("Name"), row.getString("ControllerType"), row.getBoolean("Adapted"));
                Observation observation = new Observation(State.valueOf(row.getString("State")), row.getString("Detail"));
                Entry entry = new Entry(row.getUUID("Id"), row.getUUID("Team"), row.getString("Dimension"), row.getLong("Position"), descriptor, observation, row.getLong("ObservedAt"), false);
                if (data.entries.putIfAbsent(entry.id(), entry) != null) throw new IllegalArgumentException("机器总览位置重复");
                data.index(null, entry);
                data.refreshQueue.addLast(entry.id());
            }
        } catch (RuntimeException error) { throw new IllegalStateException("机器总览索引内容损坏，拒绝重置", error); }
        return data;
    }
    private static void requireId(String id) {
        if (id == null || !id.matches("[a-z0-9_.-]+:[a-z0-9_./-]+") || id.length() > 256)
            throw new IllegalArgumentException("机器总览注册标识错误");
    }
    private static void requireText(String value, int limit) {
        if (value == null || value.isBlank() || value.length() > limit) throw new IllegalArgumentException("机器总览说明错误");
    }
}
