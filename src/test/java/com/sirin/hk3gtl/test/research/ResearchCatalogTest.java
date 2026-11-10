package com.sirin.hk3gtl.test.research;

import com.sirin.hk3gtl.common.research.Hk3ResearchCatalog;
import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import java.util.List;
import java.util.Set;
import java.util.UUID;

/**
 * 【变更记录 #1】2026-09-22 14:55:00（内测5第3次代码更新）
 * 新增：真实目录解析、无效图拒绝、独立样本权限与NBT往返测试；无旧测试删除。
 * Validate actual catalog, reject invalid graphs, verify independent circuit entitlements and NBT round trips.
 * 测试直接调用服务端账本模拟已完成结算，不代表研究机/物料过程已实装。
 * Direct ledger writes simulate trusted settlement; these tests do not claim machine execution is implemented.
 * 【变更记录 #2】2026-09-22 15:22:30（内测5第4次代码更新）
 * 删除：无，旧测试已归档。修改：未知条目保留断言精确比较Accounts，允许新增Jobs字段。
 * 新增：核对旧存档升级后含任务队列；用途：兼容持久化格式扩展而不放宽知识保留验证。
 * Compare Accounts exactly while asserting the new Jobs field, preserving unknown-knowledge regression coverage.
 */
/**
 * 【变更记录 #3】2026-09-23 03:09:00（内测5修订52）
 * 删除：无。新增：实际故事资源加载及100课题覆盖、未知ID拒绝测试。
 * 修改：构建门禁读取正式加载器，防止缺资源直到打开界面才崩溃。
 * 用途：验证叙事资源与现有研究目录一致，不改研究账本或实验。
 * Exercise the production story loader in build checks to catch missing assets before opening the GUI.
 */
/**
 * 【变更记录 #4】2026-09-30 02:17:47（第4次备注 · 内测5修订107）
 * 删除：本文件可执行代码中的旧电压键及常量引用，不保留旧键注册别名。
 * 新增：16档正式缩写作为唯一电压标识；逐文件映射见logs/voltage-keys-r107。
 * 修改：注册、配方、查询或标签引用按原tier序号一一迁移；数值、层级与资源内容保持原义。
 * 用途：避免显示名与实际注册键不一致；历史备注保留，旧存档不自动改写。
 */
public final class ResearchCatalogTest {
    private static final UUID PLAYER = UUID.fromString("00000000-0000-0000-0000-000000000001");
    private static final UUID OTHER = UUID.fromString("00000000-0000-0000-0000-000000000002");

    /** 失败抛错终止构建，不依赖-ea、不读取真实存档。 / Fail the build on errors without -ea or live saves. */
    public static void main(String[] args) {
        var catalog = Hk3ResearchCatalog.bundled();
        check(catalog.topics().size() == 100, "100 approved topics loaded");
        for(String id:catalog.topics().keySet()) check(!com.sirin.hk3gtl.common.research.Hk3ResearchStory.get(id).isBlank(),"story present: "+id);
        expectFailure(() -> com.sirin.hk3gtl.common.research.Hk3ResearchStory.get("RN-UNKNOWN"));
        check(catalog.get("RN-RCA").prerequisites().equals(List.of("RN-CCE","RN-CPT")), "reason core dependencies preserved");
        check(!catalog.prerequisitesMet("RN-RCA",Set.of("RN-CCE","RN-CPT"),1), "S01 cannot research S02 core");
        check(!catalog.prerequisitesMet("RN-UNKNOWN",Set.of(),5), "unknown topic fails closed");
        check(!catalog.prerequisitesMet("RN-RCA",Set.of("RN-CCE","RN-CPT"),6), "invalid lab rejected");
        expectFailure(() -> new Hk3ResearchCatalog(List.of(topic("RN-A","RN-B"))));
        expectFailure(() -> new Hk3ResearchCatalog(List.of(topic("RN-A","RN-A"))));
        expectFailure(() -> new Hk3ResearchCatalog(List.of(topic("RN-A","RN-B"),topic("RN-B","RN-A"))));
        expectFailure(() -> new Hk3ResearchCatalog(List.of(topic("RN-A"),topic("RN-A"))));
        ledger();
        malformed();
        System.out.println("Industrial research: 100-topic DAG, lab gates, per-tier analysis, isolation and NBT round trips passed");
    }

    /** 前置图边界用小图验证，不镜像解析实现。 / Use small counterexamples for dependency-graph validation. */
    private static Hk3ResearchCatalog.Topic topic(String id, String... prerequisites) {
        return new Hk3ResearchCatalog.Topic(id,1,0,List.of(prerequisites));
    }

    /** 先模拟可信结算链，再测试电路权限不能因最高电压、旧事件、另一玩家而扩大。 / Simulate valid settlement, then reject cross-tier, legacy-event and cross-player authorization. */
    private static void ledger() {
        Hk3ResearchData data = new Hk3ResearchData();
        check(!data.recordCompletion(PLAYER,"RN-RCA",5), "cannot skip prerequisites");
        check(!data.recordCircuitAnalysis(PLAYER,"max"), "cannot analyze before core and technology");
        completeTree(data,"RN-RCA");
        check(data.completed(PLAYER,"RN-RCA"), "core knowledge recorded");
        check(!data.recordCompletion(PLAYER,"RN-RCA",5), "duplicate completion suppressed");
        check(!data.recordCircuitAnalysis(PLAYER,"max"), "core knowledge alone is not circuit technology");
        check(data.recordCircuitTechnology(PLAYER,"max"), "record trusted technology");
        check(!data.canReconstruct(PLAYER,"max"), "technology alone is not sample analysis");
        check(data.recordCircuitAnalysis(PLAYER,"max"), "record verified analysis");
        check(data.canReconstruct(PLAYER,"max"), "all knowledge proofs present");
        check(!data.canReconstruct(PLAYER,"ulv"), "MAX does not grant all tiers");
        check(!data.canReconstruct(OTHER,"max"), "other account cannot borrow knowledge");
        check(!data.canReconstruct(PLAYER,"hbv"), "new voltage not added to old whitelist");
        check(!data.permits(PLAYER,"R-WL-001"), "legacy gift not accepted");
        check(!data.permits(PLAYER,"RN-RCA/circuit/invalid"), "invalid circuit denied");
        CompoundTag serialized = data.save(new CompoundTag());
        Hk3ResearchData restored = Hk3ResearchData.load(serialized);
        check(restored.permits(PLAYER,"RN-RCA/circuit/max"), "entitlement survives save/load");
        check(!restored.permits(OTHER,"RN-RCA/circuit/max"), "account isolation survives reload");
        serialized.getCompound("Accounts").remove(PLAYER.toString());
        check(data.canReconstruct(PLAYER,"max"), "save output is a defensive copy");
        check(restored.canReconstruct(PLAYER,"max"), "load takes a defensive copy");
        check(!new Hk3ResearchData().canReconstruct(PLAYER,"max"), "world isolation");
    }

    /** 用实际目录按拓扑顺序结算，验证可达而不是随意写布尔值。 / Settle the actual prerequisite chain in topological order. */
    private static void completeTree(Hk3ResearchData data, String id) {
        var topic = Hk3ResearchCatalog.bundled().get(id);
        for (String parent : topic.prerequisites()) completeTree(data,parent);
        if (!data.completed(PLAYER,id)) check(data.recordCompletion(PLAYER,id,topic.lab()),"eligible settlement " + id);
    }

    /** 孤立完成标记及错误类型不能开权限，未知条目仍保留。 / Orphaned completion and malformed types cannot unlock; unknown entries are retained. */
    private static void malformed() {
        CompoundTag root = new CompoundTag();
        CompoundTag account = new CompoundTag();
        ListTag complete = new ListTag(); complete.add(StringTag.valueOf("RN-RCA")); complete.add(StringTag.valueOf("RN-FUTURE"));
        account.put("Completed",complete);
        CompoundTag accounts = new CompoundTag(); accounts.put(PLAYER.toString(),account); root.put("Accounts",accounts);
        var data = Hk3ResearchData.load(root);
        check(!data.completed(PLAYER,"RN-RCA"),"isolated core flag cannot unlock");
        CompoundTag upgraded = data.save(new CompoundTag());
        check(upgraded.getCompound("Accounts").equals(root.getCompound("Accounts")),"unknown entries preserved");
        check(upgraded.contains("Jobs", net.minecraft.nbt.Tag.TAG_COMPOUND),"legacy save gains job queue");
        account.putInt("Completed",1);
        accounts.put(PLAYER.toString(),account); root.put("Accounts",accounts);
        var broken = Hk3ResearchData.load(root);
        expectFailure(() -> broken.completed(PLAYER,"RN-RCA"));
    }

    private static void expectFailure(Runnable work) {
        try { work.run(); } catch (IllegalArgumentException expected) { return; }
        throw new AssertionError("Invalid research state accepted");
    }
    private static void check(boolean condition, String message) { if (!condition) throw new AssertionError(message); }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
