package com.sirin.hk3gtl.test.research;

import com.sirin.hk3gtl.common.research.Hk3ResearchCatalog;
import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import java.util.List;
import java.util.Set;
import java.util.UUID;

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

