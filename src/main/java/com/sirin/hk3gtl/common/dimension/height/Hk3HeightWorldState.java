package com.sirin.hk3gtl.common.dimension.height;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;

import java.util.Collections;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeMap;
import java.util.UUID;
import java.util.regex.Pattern;

/**
 * 【文件职责】保存每个世界独立的高度合同及按维度类型ID冻结的原始边界快照。
 * 【变更记录 #1】2026-10-17 21:24:01（修订166）
 * - 删除：无。
 * - 新增：世界UUID、版本1合同、不可变维度快照与严格NBT读写、替换快照副本入口。
 * - 修改：未知版本、缺字段、错误类型和不一致边界一律拒绝，不将损坏合同降级为低高度世界。
 * - 用途：供PrimaryLevelData实例持有并写入世界数据；配置重载不隐式改变既有世界合同。
 *
 * 【变更记录 #2】2026-10-17 21:41:50（修订166）
 * - 删除：启用合同空快照直接读写NBT的通道。
 * - 新增：序列化与反序列化均拒绝启用且维度快照为空的合同；构造器仍允许新建时短暂持有空快照。
 * - 修改：首次提前保存必须先由服务冻结注册表快照，旧存档不能靠清空快照绕过资源漂移核验。
 * - 用途：闭合客户端先保存后启动服务器的真实路径，防止错误合同被再次解释为待初始化新世界。
 */
public record Hk3HeightWorldState(UUID worldId, int contractVersion, int topExclusive, boolean enabled,
                                 Map<String, Hk3HeightBounds> dimensions) {
    public static final String TAG_KEY = "hk3gtl:height_contract";
    public static final int CURRENT_VERSION = 1;
    private static final Pattern TYPE_ID = Pattern.compile("[a-z0-9_.-]+:[a-z0-9/._-]+");
    private static final Set<String> ROOT_KEYS = Set.of("worldId", "contractVersion", "topExclusive",
            "enabled", "dimensions");
    private static final Set<String> BOUNDS_KEYS = Set.of("originalMinY", "originalHeight",
            "logicalHeight", "newHeight", "newTopExclusive");

    public Hk3HeightWorldState {
        Objects.requireNonNull(worldId, "高度合同缺少世界身份");
        if (contractVersion != CURRENT_VERSION) {
            throw new IllegalArgumentException("无法读取未知高度合同版本：" + contractVersion);
        }
        Hk3HeightPolicy.requireTopExclusive(topExclusive);
        Objects.requireNonNull(dimensions, "高度合同缺少维度快照");
        Map<String, Hk3HeightBounds> snapshot = new TreeMap<>();
        for (Map.Entry<String, Hk3HeightBounds> entry : dimensions.entrySet()) {
            String id = entry.getKey();
            if (id == null || !TYPE_ID.matcher(id).matches()) {
                throw new IllegalArgumentException("高度合同维度类型ID无效：" + id);
            }
            Hk3HeightBounds bounds = Objects.requireNonNull(entry.getValue(), "高度合同缺少维度边界：" + id);
            Hk3HeightBounds expected = enabled
                    ? Hk3HeightPolicy.expand(bounds.originalMinY(), bounds.originalHeight(),
                            bounds.logicalHeight(), topExclusive)
                    : Hk3HeightPolicy.unchanged(bounds.originalMinY(), bounds.originalHeight(), bounds.logicalHeight());
            if (!expected.equals(bounds)) {
                throw new IllegalArgumentException("高度合同维度边界与冻结策略不一致：" + id);
            }
            snapshot.put(id, bounds);
        }
        dimensions = Collections.unmodifiableMap(snapshot);
    }

    public Hk3HeightWorldState withDimensions(Map<String, Hk3HeightBounds> snapshots) {
        return new Hk3HeightWorldState(worldId, contractVersion, topExclusive, enabled, snapshots);
    }

    public CompoundTag toNbt() {
        requirePersistableSnapshot(enabled, dimensions.isEmpty());
        CompoundTag root = new CompoundTag();
        root.putUUID("worldId", worldId);
        root.putInt("contractVersion", contractVersion);
        root.putInt("topExclusive", topExclusive);
        root.putBoolean("enabled", enabled);
        CompoundTag snapshots = new CompoundTag();
        dimensions.forEach((id, bounds) -> {
            CompoundTag snapshot = new CompoundTag();
            snapshot.putInt("originalMinY", bounds.originalMinY());
            snapshot.putInt("originalHeight", bounds.originalHeight());
            snapshot.putInt("logicalHeight", bounds.logicalHeight());
            snapshot.putInt("newHeight", bounds.newHeight());
            snapshot.putInt("newTopExclusive", bounds.newTopExclusive());
            snapshots.put(id, snapshot);
        });
        root.put("dimensions", snapshots);
        return root;
    }

    /** 仅接收完整合同；缺少整个合同的旧存档判定由上层入口处理，不在此处伪造默认值。 */
    public static Hk3HeightWorldState fromNbt(CompoundTag root) {
        if (root == null || !root.getAllKeys().equals(ROOT_KEYS)) {
            throw new IllegalArgumentException("世界高度合同字段缺失或包含未知字段");
        }
        requireType(root, "worldId", Tag.TAG_INT_ARRAY);
        if (!root.hasUUID("worldId")) {
            throw new IllegalArgumentException("世界高度合同UUID损坏");
        }
        requireType(root, "contractVersion", Tag.TAG_INT);
        int version = root.getInt("contractVersion");
        if (version != CURRENT_VERSION) {
            throw new IllegalArgumentException("无法读取未知高度合同版本：" + version);
        }
        requireType(root, "topExclusive", Tag.TAG_INT);
        requireType(root, "enabled", Tag.TAG_BYTE);
        byte flag = root.getByte("enabled");
        if (flag != 0 && flag != 1) {
            throw new IllegalArgumentException("世界高度合同启用标记损坏");
        }
        requireType(root, "dimensions", Tag.TAG_COMPOUND);
        CompoundTag snapshots = root.getCompound("dimensions");
        requirePersistableSnapshot(flag == 1, snapshots.isEmpty());
        Map<String, Hk3HeightBounds> bounds = new TreeMap<>();
        for (String id : snapshots.getAllKeys()) {
            requireType(snapshots, id, Tag.TAG_COMPOUND);
            CompoundTag snapshot = snapshots.getCompound(id);
            if (!snapshot.getAllKeys().equals(BOUNDS_KEYS)) {
                throw new IllegalArgumentException("世界高度合同维度快照字段损坏：" + id);
            }
            BOUNDS_KEYS.forEach(key -> requireType(snapshot, key, Tag.TAG_INT));
            bounds.put(id, new Hk3HeightBounds(snapshot.getInt("originalMinY"),
                    snapshot.getInt("originalHeight"), snapshot.getInt("logicalHeight"),
                    snapshot.getInt("newHeight"), snapshot.getInt("newTopExclusive")));
        }
        return new Hk3HeightWorldState(root.getUUID("worldId"), version,
                root.getInt("topExclusive"), flag == 1, bounds);
    }

    public CompoundTag toNBT() {
        return toNbt();
    }

    public static Hk3HeightWorldState fromNBT(CompoundTag root) {
        return fromNbt(root);
    }

    private static void requireType(CompoundTag tag, String key, int expectedType) {
        if (!tag.contains(key, expectedType)) {
            throw new IllegalArgumentException("世界高度合同字段类型损坏：" + key);
        }
    }

    private static void requirePersistableSnapshot(boolean enabled, boolean empty) {
        if (enabled && empty) {
            throw new IllegalArgumentException("启用的世界高度合同缺少冻结维度快照，拒绝保存或载入");
        }
    }
}
