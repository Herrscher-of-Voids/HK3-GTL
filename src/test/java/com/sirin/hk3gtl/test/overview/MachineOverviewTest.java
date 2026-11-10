package com.sirin.hk3gtl.test.overview;

import com.sirin.hk3gtl.common.overview.Hk3MachineOverviewData;
import com.sirin.hk3gtl.common.overview.Hk3MachineOverviewData.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;

import java.util.*;

/**
 * 【文件职责】验证机器索引的团队隔离、状态生命周期、预算轮转与损坏保护。
 * 【变更记录 #1】2026-10-19 02:05:22（第1次备注 · 修订171）
 * 删除：无。新增：真实生产账本类的隔离测试，覆盖多维度、重启未加载、迁队和不可写穿。
 * 修改：无；测试只构造内存账本，不写玩家世界，不代替GT回调与整包GUI实机验收。
 * 用途：防止机器总览泄漏他队坐标或把卸载快照误报实时运行。
 */
/**
 * 【变更记录 #2】2026-10-19 02:25:53（第2次备注 · 修订171）
 * 删除：无。新增：调用真实过载策略回归，覆盖既有4097条目录保留和有预算恢复条件。
 * 修改：检查总数包含生产策略专项；用途：防止加载峰值删除有效索引，不冒充真实Forge事件测试。
 */
/**
 * 【变更记录 #3】2026-10-31 19:02:47（第3次备注 · 修订190）
 * 删除：无。新增：真实分页与独立排序基线对照、热查询后迁队撤权、改名与模块计数、卸载读档删除回归。
 * 修改：保留4097条轮转检查，增加分页边界及模块名与状态名碰撞验证。
 * 用途：核验派生目录与权威账本一致，不以纯逻辑结果替代整包生命周期和客户端验收。
 */
public final class MachineOverviewTest {
    private static int checks;
    private static final UUID TEAM_A = new UUID(1, 1), TEAM_B = new UUID(2, 2);
    private static final Descriptor HK = new Descriptor("hk3gtl:test_controller", "测试控制器", "测试执行器", true);
    private static final Descriptor GT = new Descriptor("gtceu:test_controller", "GT测试控制器", "第三方执行器", false);
    private static final Observation RUNNING = new Observation(State.RUNNING, "真实运行快照");
    private static void check(boolean condition, String message) { if (!condition) throw new AssertionError(message); checks++; }
    public static void main(String[] args) {
        queryIndexLifecycle();
        var data = new Hk3MachineOverviewData();
        check(data.register(TEAM_A, "minecraft:overworld", 5L, HK, RUNNING, 20, true), "登记机器");
        UUID first = Hk3MachineOverviewData.identity("minecraft:overworld", 5L);
        check(data.visible(TEAM_A, first) != null && data.visible(TEAM_B, first) == null, "同队可见他队不可见");
        check(data.visible(TEAM_B, Hk3MachineOverviewData.identity("minecraft:overworld", 5L)) == null,
                "即使猜中稳定UUID也不能越队读取坐标");
        check(data.page(TEAM_A, 0, 4, "all").total() == 1 && data.page(TEAM_B, 0, 4, "all").total() == 0, "分页按团队隔离");
        check(!data.register(TEAM_B, "minecraft:overworld", 5L, GT, RUNNING, 21, false), "现场绑定不能抢其他团队机器");
        check(data.visible(TEAM_A, first).descriptor().equals(HK) && data.visible(TEAM_A, first).observedAt() == 20
                && data.visible(TEAM_A, first).team().equals(TEAM_A), "抢占拒绝后原归属、内容和时间保持");
        data.register(TEAM_B, "minecraft:overworld", 5L, HK, RUNNING, 22, true);
        check(data.visible(TEAM_A, first) == null && data.visible(TEAM_B, first) != null, "权威迁队立即撤销旧团队可见性");
        data.register(TEAM_A, "hk3gtl:test_dimension", 5L, GT, new Observation(State.UNADAPTED, "仅有注册身份"), 23, false);
        UUID second = Hk3MachineOverviewData.identity("hk3gtl:test_dimension", 5L);
        check(!first.equals(second), "同坐标不同维度不冲突");
        check(data.visible(TEAM_A, second).state() == State.UNADAPTED, "未适配不当停机");
        check(data.page(TEAM_A, 9999, 4, "gtceu").page() == 0, "页数裁剪");
        check(data.sources(TEAM_A).equals(List.of("gtceu")) && data.sources(TEAM_B).equals(List.of("hk3gtl")), "来源目录仅包含当前团队并按真实namespace生成");
        check(data.page(TEAM_A, 0, 4, "unadapted").total() == 1 && data.page(TEAM_A, 0, 4, "running").total() == 0, "来源和状态筛选真实");
        data.unloaded("hk3gtl:test_dimension", 5L);
        var unloaded = data.visible(TEAM_A, second);
        check(unloaded.state() == State.UNLOADED && unloaded.observation().state() == State.UNADAPTED && unloaded.observedAt() == 23, "卸载保留最后可信状态与时间");
        data.observe("hk3gtl:test_dimension", 5L, GT, new Observation(State.UNKNOWN, "无法安全读取配方状态"), 30);
        check(data.visible(TEAM_A, second).state() == State.UNKNOWN, "真实观察恢复加载但未知不伪造");
        check(!data.observe("minecraft:overworld", 99L, HK, RUNNING, 31), "观察不会自动认领未绑定机器");
        CompoundTag saved = data.save(new CompoundTag());
        var loaded = Hk3MachineOverviewData.load(saved);
        check(loaded.visible(TEAM_A, second).state() == State.UNLOADED && loaded.visible(TEAM_B, first).state() == State.UNLOADED, "重启全部先标未加载");
        check(loaded.visible(TEAM_B, first).observation().state() == State.RUNNING && loaded.visible(TEAM_B, first).observedAt() == 22, "重启保留历史运行证据但不冒充实时");
        check(loaded.visible(TEAM_A, first) == null, "重启不会恢复迁队前权限");
        saved.getList("Machines", 10).getCompound(0).putString("Name", "修改存盘副本");
        check(!loaded.visible(TEAM_B, first).descriptor().displayName().equals("修改存盘副本"), "存盘与索引互不写穿");
        try { loaded.page(TEAM_A, 0, 4, "all").rows().clear(); throw new AssertionError("分页结果可修改"); }
        catch (UnsupportedOperationException expected) { checks++; }
        for (State state : State.values()) {
            loaded.observe("hk3gtl:test_dimension", 5L, HK, new Observation(state, state.label()), 40 + state.ordinal());
            check(loaded.visible(TEAM_A, second).state() == state, "八态保真：" + state);
        }
        loaded.remove("minecraft:overworld", 5L);
        check(loaded.visible(TEAM_B, first) == null && loaded.page(TEAM_B, 0, 4, "all").total() == 0, "移除不保留幽灵机器");
        for (int i = 0; i < 200; i++) loaded.register(TEAM_A, "minecraft:overworld", i + 1000L, HK, RUNNING, 100, false);
        Set<UUID> visited = new HashSet<>();
        for (int i = 0; i < 4; i++) { var batch = loaded.refreshBatch(64); check(batch.size() <= 64, "固定刷新预算"); batch.forEach(e -> visited.add(e.id())); }
        check(visited.size() == 201, "轮转覆盖全部已登记位置");
        var firstPage = loaded.page(TEAM_A, 0, 4, "all");
        check(firstPage.total() == 201 && firstPage.rows().size() == 4, "四条分页与总数");
        check(loaded.page(TEAM_A, Integer.MAX_VALUE, 4, "all").page() == 50, "极端页数不溢出");
        // 固定预算为数据结构合同；这里只验证覆盖与不饥饿，不宣称大型基地的实机帧时。
        var large = new Hk3MachineOverviewData();
        for (int i = 0; i < 4097; i++) large.register(TEAM_A, "minecraft:overworld", i, HK, RUNNING, i, false);
        Set<UUID> largeVisited = new HashSet<>();
        for (int cycle = 0; cycle < 2; cycle++) {
            largeVisited.clear();
            for (int batchIndex = 0; batchIndex < 65; batchIndex++) {
                var batch = large.refreshBatch(64);
                check(batch.size() == 64, "4097条索引每次严格执行64项预算");
                check(batch.stream().map(Entry::id).distinct().count() == 64, "同批次没有重复索引");
                batch.forEach(e -> largeVisited.add(e.id()));
            }
            check(largeVisited.size() == 4097, "4097条索引轮转不饥饿：第" + (cycle + 1) + "轮");
        }
        check(large.refreshBatch(0).isEmpty(), "零预算不访问任何机器");
        large.remove("minecraft:overworld", 2048);
        Set<UUID> afterRemove = new HashSet<>();
        for (int i = 0; i < 64; i++) large.refreshBatch(64).forEach(e -> afterRemove.add(e.id()));
        check(afterRemove.size() == 4096 && !afterRemove.contains(Hk3MachineOverviewData.identity("minecraft:overworld", 2048)),
                "移除后4096条索引一轮恰好覆盖且没有幽灵项");
        expectFailure(() -> Hk3MachineOverviewData.load(new CompoundTag()));
        var broken = loaded.save(new CompoundTag()); broken.getList("Machines", 10).getCompound(0).putString("State", "FAKE");
        expectFailure(() -> Hk3MachineOverviewData.load(broken));
        var duplicate = loaded.save(new CompoundTag()); var rows = duplicate.getList("Machines", 10); rows.add(rows.getCompound(0).copy());
        expectFailure(() -> Hk3MachineOverviewData.load(duplicate));
        var wrongId = loaded.save(new CompoundTag()); wrongId.getList("Machines", 10).getCompound(0).putUUID("Id", new UUID(-1, -1));
        expectFailure(() -> Hk3MachineOverviewData.load(wrongId));
        var wrongList = new CompoundTag(); wrongList.putInt("Schema", 1); var strings = new ListTag(); strings.add(StringTag.valueOf("bad")); wrongList.put("Machines", strings);
        expectFailure(() -> Hk3MachineOverviewData.load(wrongList));
        var negativeTime = loaded.save(new CompoundTag()); negativeTime.getList("Machines", 10).getCompound(0).putLong("ObservedAt", -1);
        expectFailure(() -> Hk3MachineOverviewData.load(negativeTime));
        var missingTeam = loaded.save(new CompoundTag()); missingTeam.getList("Machines", 10).getCompound(0).remove("Team");
        expectFailure(() -> Hk3MachineOverviewData.load(missingTeam));
        var invalidRegistry = loaded.save(new CompoundTag()); invalidRegistry.getList("Machines", 10).getCompound(0).putString("Registry", "../foreign");
        expectFailure(() -> Hk3MachineOverviewData.load(invalidRegistry));
        var futureSchema = loaded.save(new CompoundTag()); futureSchema.putInt("Schema", 999);
        expectFailure(() -> Hk3MachineOverviewData.load(futureSchema));
        check(!Hk3MachineOverviewData.validFilter("../../all") && !Hk3MachineOverviewData.validFilter(""), "筛选不接受路径和空输入");
        checks += com.sirin.hk3gtl.common.overview.Hk3MachineOverviewLoadRecoveryTest.run();
        System.out.println("机器总览账本：" + checks + "项检查通过；GT生命周期和GUI仍需指定实例验收");
    }
    private static void expectFailure(Runnable action) {
        try { action.run(); throw new AssertionError("损坏数据被接受"); }
        catch (IllegalStateException expected) { checks++; }
    }

    private static void queryIndexLifecycle() {
        var data = new Hk3MachineOverviewData();
        List<Entry> expected = new ArrayList<>();
        // 逆序登记并交错注册名、维度和有符号坐标，独立基线验证稳定页序。
        for (int i = 22; i >= 0; i--) {
            String dimension = i % 2 == 0 ? "minecraft:overworld" : "minecraft:the_nether";
            Descriptor descriptor = i % 3 == 0 ? GT : HK;
            long position = i - 11;
            data.register(TEAM_A, dimension, position, descriptor, RUNNING, i, false);
            expected.add(new Entry(Hk3MachineOverviewData.identity(dimension, position), TEAM_A, dimension,
                    position, descriptor, RUNNING, i, true));
        }
        assertQueries(data, expected);
        Entry old = expected.get(0);
        var previousPage = data.page(TEAM_A, 0, 64, "all");
        data.sources(TEAM_A);
        check(!data.register(TEAM_B, old.dimension(), old.position(), HK, RUNNING, 30, false), "热查询后的非权威抢占仍拒绝");
        assertQueries(data, expected);
        data.register(TEAM_B, old.dimension(), old.position(), HK, RUNNING, 31, true);
        expected.set(0, new Entry(old.id(), TEAM_B, old.dimension(), old.position(), HK, RUNNING, 31, true));
        assertQueries(data, expected);
        check(data.visible(TEAM_A, old.id()) == null
                && data.page(TEAM_A, 0, 64, "all").rows().stream().noneMatch(e -> e.id().equals(old.id())),
                "旧查询不能使迁队后分页或详情泄露权限");
        check(previousPage.rows().contains(old), "已交付不可变快照保留历史内容，不作为后续授权来源");

        Descriptor collision = new Descriptor("running:aaa", "状态同名模块", "测试执行器", true);
        Observation stopped = new Observation(State.STOPPED, "更新状态");
        data.observe(old.dimension(), old.position(), collision, stopped, 32);
        expected.set(0, new Entry(old.id(), TEAM_B, old.dimension(), old.position(), collision, stopped, 32, true));
        assertQueries(data, expected);
        check(data.sources(TEAM_B).equals(List.of("running")), "最后一台机器更换模块立即清理旧来源");
        check(data.page(TEAM_B, 0, 4, "running").total() == 1, "模块与状态同名时保留原有或匹配语义");
        data.unloaded(old.dimension(), old.position());
        expected.set(0, new Entry(old.id(), TEAM_B, old.dimension(), old.position(), collision, stopped, 32, false));
        assertQueries(data, expected);
        data = Hk3MachineOverviewData.load(data.save(new CompoundTag()));
        expected.replaceAll(e -> new Entry(e.id(), e.team(), e.dimension(), e.position(), e.descriptor(), e.observation(), e.observedAt(), false));
        assertQueries(data, expected);
        data.observe(old.dimension(), old.position(), HK, RUNNING, 33);
        expected.set(0, new Entry(old.id(), TEAM_B, old.dimension(), old.position(), HK, RUNNING, 33, true));
        assertQueries(data, expected);
        data.remove(old.dimension(), old.position()); expected.remove(0);
        data.remove(old.dimension(), old.position());
        assertQueries(data, expected);
        check(data.sources(TEAM_B).isEmpty(), "删除末台机器移除团队来源目录");
        data.register(TEAM_A, old.dimension(), old.position(), GT, RUNNING, 34, false);
        expected.add(new Entry(old.id(), TEAM_A, old.dimension(), old.position(), GT, RUNNING, 34, true));
        assertQueries(data, expected);
        check(data.refreshBatch(64).size() == expected.size(), "删除后同位置重新登记不重复轮转");
        for (int size : new int[]{0, 65}) {
            try { data.page(TEAM_A, 0, size, "all"); throw new AssertionError("接受无效分页大小"); }
            catch (IllegalArgumentException expectedFailure) { checks++; }
        }
    }

    /** 基线只读取测试期望记录，不借助生产目录、筛选或分页实现。 */
    private static void assertQueries(Hk3MachineOverviewData data, List<Entry> expected) {
        for (UUID team : List.of(TEAM_A, TEAM_B, new UUID(3, 3))) {
            var owned = expected.stream().filter(e -> e.team().equals(team)).toList();
            check(data.sources(team).equals(owned.stream().map(e -> e.descriptor().module()).distinct().sorted().toList()),
                    "来源目录与团队记录一致");
            for (String filter : List.of("all", "gtceu", "hk3gtl", "running", "stopped", "unloaded", "missing")) {
                var matches = owned.stream().filter(e -> filter.equals("all") || e.descriptor().module().equals(filter)
                                || e.state().name().toLowerCase(Locale.ROOT).equals(filter))
                        .sorted(Comparator.comparing((Entry e) -> e.descriptor().registryId())
                                .thenComparing(Entry::dimension).thenComparingLong(Entry::position)).toList();
                for (int size : new int[]{4, 64}) {
                    int last = Math.max(0, (matches.size() - 1) / size);
                    for (int requested : new int[]{-1, 0, 1, 2, last, Integer.MAX_VALUE}) {
                        int page = Math.min(Math.max(0, requested), last);
                        int from = page * size;
                        Page actual = data.page(team, requested, size, filter);
                        check(actual.total() == matches.size() && actual.page() == page
                                        && actual.rows().equals(matches.subList(from, Math.min(from + size, matches.size()))),
                                "真实目录筛选及分页与独立基线一致：" + filter);
                    }
                }
            }
        }
    }
}
