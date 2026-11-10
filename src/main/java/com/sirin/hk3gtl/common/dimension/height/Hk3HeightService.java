package com.sirin.hk3gtl.common.dimension.height;

import com.mojang.logging.LogUtils;
import com.sirin.hk3gtl.mixin.height.Hk3DimensionTypeHeightAccessor;
import net.minecraft.core.RegistryAccess;
import net.minecraft.core.registries.Registries;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.dimension.DimensionType;
import net.minecraft.world.level.storage.LevelResource;
import org.slf4j.Logger;

import java.util.Map;
import java.util.Optional;
import java.util.TreeMap;
import java.util.UUID;

/**
 * 【文件职责】在首个Level构造前统一应用本世界注册类型，客户端只接收服务端原生注册表同步。
 * 【变更记录 #1】2026-10-17 21:19:41（第1次备注 · 修订166）
 * - 删除：无。新增：逐类型原边界快照、重开漂移拒绝和可读状态API。
 * - 修改：仅已启用世界实例的物理height，保留minY、logicalHeight及生成器；不使用全局构造器改高。
 * - 用途：让区块、Radium缓存、照明和网络在创建前取得一致高度；坏合同或资源漂移停止加载，防止截断存档。
 * 【变更记录 #2】2026-10-17 21:43:13（第2次备注 · 修订166）
 * - 删除：无，保留历史与创建世界前的访问器应用流程。
 * - 新增：首次保存前只读冻结原始维度边界；启用合同缺少注册表时拒绝写出。
 * - 修改：客户端启动服务器前的提前保存也携带完整快照，不再持久化空合同后猜测原高度。
 * - 用途：使客户端新建与专服新建都保留可信的原边界，后续保存不重新读取已经扩高的类型。
 * 【变更记录 #3】2026-10-17 21:46:43（第3次备注 · 修订166）
 * - 删除：无，保留前两次历史及空快照封存逻辑。
 * - 新增：保存前依据本世界应用标记核验原始或已扩高边界，拒绝未注册的内嵌维度类型。
 * - 修改：非空合同不再跳过注册表一致性检查，资源漂移在首次提前写盘前即停止。
 * - 用途：避免旧合同重开时先写入不相容生成设置；合法键引用仍由原生编解码和网络同步处理。
 */
/**
 * 【变更记录 #4】2026-10-29 23:06:53（第4次备注 · 本轮高度与预览修复）
 * - 删除：无合同旧档一律不提供启用路径的限制；未入名单仍保持原样。
 * - 新增：按准确存档文件夹选择旧档，冻结原始注册表并校验元数据备份，失败拒绝创建Level。
 * - 修改：扩高仍只在首个Level和区段缓存创建前进行；原minY、逻辑高度、生成器与已保存合同保持。
 * - 用途：重开后服务端和原生客户端注册表一致，避免在运行中改高导致已有区块区段索引不一致。
 */
public final class Hk3HeightService {
    private static final Logger LOGGER = LogUtils.getLogger();
    private Hk3HeightService() {}

    public static Optional<Hk3HeightWorldState> state(MinecraftServer server) {
        return server.getWorldData() instanceof Hk3HeightWorldData data
            ? Optional.ofNullable(data.hk3gtl$getHeightState()) : Optional.empty();
    }

    public static Hk3HeightWorldState freezeBeforeSave(RegistryAccess registryAccess, Hk3HeightWorldState state, boolean applied) {
        if (!state.enabled()) return state;
        validateReferencedTypes(registryAccess);
        var registry = registryAccess.registryOrThrow(Registries.DIMENSION_TYPE);
        Map<String, Hk3HeightBounds> original = new TreeMap<>();
        for (var entry : registry.entrySet()) {
            String id = entry.getKey().location().toString();
            var type = entry.getValue();
            if (state.dimensions().isEmpty()) {
                if (applied) throw new IllegalStateException("高度已应用却缺少原始边界，拒绝保存。");
                original.put(id, Hk3HeightPolicy.expand(type.minY(), type.height(), type.logicalHeight(), state.topExclusive()));
            } else {
                var saved = state.dimensions().get(id);
                if (saved == null || type.minY() != saved.originalMinY() || type.logicalHeight() != saved.logicalHeight()
                    || type.height() != (applied ? saved.newHeight() : saved.originalHeight()))
                    throw new IllegalStateException("高度合同与当前维度边界不一致，拒绝保存：" + id);
                original.put(id, saved);
            }
        }
        if (original.isEmpty()) throw new IllegalStateException("维度类型注册表为空，拒绝保存未冻结的高度合同。");
        if (!state.dimensions().isEmpty() && !state.dimensions().keySet().equals(original.keySet()))
            throw new IllegalStateException("高度合同中的维度类型已缺失，拒绝保存。");
        return state.dimensions().isEmpty() ? state.withDimensions(original) : state;
    }

    private static void validateReferencedTypes(RegistryAccess access) {
        var types = access.registryOrThrow(Registries.DIMENSION_TYPE);
        for (var entry : access.registryOrThrow(Registries.LEVEL_STEM).entrySet()) {
            var holder = entry.getValue().type();
            var key = holder.unwrapKey();
            if (key.isEmpty() || types.get(key.get()) != holder.value())
                throw new IllegalStateException("暂不支持未注册的内嵌维度类型，拒绝启用高度合同：" + entry.getKey().location());
        }
    }

    public static void applyBeforeLevels(MinecraftServer server) {
        if (!(server.getWorldData() instanceof Hk3HeightWorldData data))
            throw new IllegalStateException("HK3GTL高度合同接口未加载，拒绝创建世界。");
        var state = data.hk3gtl$getHeightState();
        if (state == null && Hk3HeightWorldUpgrade.selected(server.getWorldPath(LevelResource.ROOT),
                Hk3HeightConfig.EXISTING_WORLDS.get())) {
            state = freezeBeforeSave(server.registryAccess(), new Hk3HeightWorldState(UUID.randomUUID(),
                Hk3HeightWorldState.CURRENT_VERSION, Hk3HeightConfig.TOP_EXCLUSIVE.get(), true, Map.of()), false);
            try {
                var backup = Hk3HeightWorldUpgrade.backup(server.getWorldPath(LevelResource.ROOT), state.topExclusive());
                LOGGER.info("[HK3GTL高度] 精确名单旧档已完成原元数据校验备份：{}", backup);
            } catch (java.io.IOException failure) {
                throw new IllegalStateException("高度升级备份失败，拒绝创建Level；原世界边界未修改。", failure);
            }
        }
        if (state == null || !state.enabled()) {
            LOGGER.info("[HK3GTL高度] 本世界没有启用合同，保持所有维度原高度；不自动迁移已有世界。");
            return;
        }
        if (data.hk3gtl$isHeightApplied()) return;
        Hk3HeightPolicy.requireTopExclusive(state.topExclusive());
        validateReferencedTypes(server.registryAccess());
        var registry = server.registryAccess().registryOrThrow(Registries.DIMENSION_TYPE);
        Map<String, Hk3HeightBounds> planned = new TreeMap<>();
        Map<String, DimensionType> types = new TreeMap<>();
        for (var entry : registry.entrySet()) {
            String id = entry.getKey().location().toString();
            var type = entry.getValue();
            if (!((Object)type instanceof Hk3DimensionTypeHeightAccessor))
                throw new IllegalStateException("HK3GTL高度访问器缺失：" + id);
            planned.put(id, Hk3HeightPolicy.expand(type.minY(), type.height(), type.logicalHeight(), state.topExclusive()));
            types.put(id, type);
        }
        if (planned.isEmpty()) throw new IllegalStateException("维度类型注册表为空，拒绝应用高度合同。");
        if (!state.dimensions().isEmpty() && !state.dimensions().equals(planned))
            throw new IllegalStateException("本世界高度合同与当前维度类型/原高度不一致。请恢复原模组与数据包，不得缩高或忽略合同打开。");
        for (var entry : types.entrySet()) {
            var bounds = planned.get(entry.getKey());
            ((Hk3DimensionTypeHeightAccessor)(Object)entry.getValue()).hk3gtl$setPhysicalHeight(bounds.newHeight());
        }
        data.hk3gtl$setHeightState(state.withDimensions(planned));
        data.hk3gtl$markHeightApplied();
        LOGGER.info("[HK3GTL高度] 世界合同{}已应用{}种维度类型；最高可建Y={}，原minY/逻辑高度/地形保持。",
            state.worldId(), planned.size(), state.topExclusive() - 1);
    }
}
