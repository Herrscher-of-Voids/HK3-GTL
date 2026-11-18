package com.sirin.hk3gtl.test.worldbubble;

import com.sirin.hk3gtl.common.worldbubble.Hk3WorldBubbleData;
import com.sirin.hk3gtl.common.worldbubble.Hk3WorldBubbleLedger;
import com.sirin.hk3gtl.common.worldbubble.Hk3WorldResourceBatches;
import com.sirin.hk3gtl.common.worldbubble.Hk3WorldResourceCatalog;
import com.sirin.hk3gtl.common.worldbubble.Hk3WorldResourceSettlement;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.nbt.Tag;

import java.util.List;
import java.util.UUID;

import static com.sirin.hk3gtl.common.worldbubble.Hk3WorldBubbleLedger.*;

/** 世界泡公共存档恢复回归；调用实际加载与结算代码，不启动游戏、不交付库存。 */
public final class WorldBubbleResourceRestoreTest {
    private static final UUID ACTOR = new UUID(1, 1), TEAM = new UUID(2, 2);
    private static int checks;

    private record Fixture(Hk3WorldBubbleLedger ledger, Hk3WorldResourceBatches resources,
                           UUID operation, UUID target) {
        CompoundTag save() {
            var root = new CompoundTag();
            root.put("Ledger", ledger.save());
            root.putInt("ResourceVersion", 1);
            root.put("Resources", resources.save());
            return root;
        }
    }

    public static void main(String[] args) {
        settledSources();
        legacyCompatibility();
        pendingAndCancelled();
        malformedSchema();
        malformedSettlements();
        System.out.println("世界泡资源恢复：" + checks + "项检查通过");
    }

    private static void settledSources() {
        for (boolean delivered : new boolean[]{false, true}) {
            var fixture = settled(false, delivered);
            var saved = fixture.save();
            var restored = loadUnchanged(saved);
            check(restored.save(new CompoundTag()).equals(saved), "完整资源存档逐字段往返");
            var tx = restored.ledger().transaction(fixture.operation());
            check(tx.delivered() == delivered && tx.phase() == Phase.SETTLED, "交付状态不变");
            check(restored.ledger().real(fixture.target()).miningCount() == 1, "已结算采掘次数不变");
            check(restored.ledger().pendingDeliveries(ACTOR).size() == (delivered ? 0 : 1), "待交付集合不变");
            var missing = withoutResources(saved);
            rejectUnchanged(missing, "已结算非空资源引用不允许同时缺两字段");
            check(loadUnchanged(saved).save(new CompoundTag()).equals(saved), "拒绝损坏副本后完整原件仍可加载");
        }
        var simulation = settled(true, false);
        var saved = simulation.save();
        check(loadUnchanged(saved).save(new CompoundTag()).equals(saved), "模拟终止资源正常往返");
        rejectUnchanged(withoutResources(saved), "模拟资源来源不能通过双删字段绕过");
    }

    private static void legacyCompatibility() {
        var empty = new CompoundTag();
        empty.put("Ledger", new Hk3WorldBubbleLedger().save());
        var upgraded = loadUnchanged(empty).save(new CompoundTag());
        check(upgraded.getInt("ResourceVersion") == 1
                && upgraded.getCompound("Resources").getList("Packages", Tag.TAG_COMPOUND).isEmpty(), "空旧档补齐空资源表");
        check(loadUnchanged(upgraded).save(new CompoundTag()).equals(upgraded), "升级空旧档再次加载稳定");

        var legacy = begin(false);
        legacy.ledger().settle(legacy.operation(), ACTOR, receipt(legacy.operation(), Action.MINE));
        var old = withoutResources(legacy.save());
        var loaded = loadUnchanged(old);
        check(loaded.ledger().transaction(legacy.operation()).receipt()
                .equals(legacy.ledger().transaction(legacy.operation()).receipt()), "无资源字段的真实旧收据保持");
        var modern = loaded.save(new CompoundTag());
        check(loadUnchanged(modern).save(new CompoundTag()).equals(modern), "无资源引用旧档可稳定升级");

        var emptyList = begin(false);
        emptyList.ledger().cancel(emptyList.operation(), ACTOR);
        UUID capture = new UUID(5, 2);
        emptyList.ledger().begin(capture, ACTOR, Domain.REAL, emptyList.target(), Action.CAPTURE);
        var done = Hk3WorldResourceSettlement.prepare(emptyList.ledger(), emptyList.resources(), capture,
                ACTOR, TEAM, receipt(capture, Action.CAPTURE), catalog(), 42);
        Hk3WorldResourceSettlement.validate(emptyList.ledger(), emptyList.resources(), capture, ACTOR, TEAM, done);
        emptyList.ledger().settle(capture, ACTOR, done);
        var captureOld = withoutResources(emptyList.save());
        check(loadUnchanged(captureOld).ledger().transaction(capture).receipt().equals(done), "空资源列表旧收据兼容");
    }

    private static void pendingAndCancelled() {
        for (boolean cancelled : new boolean[]{false, true}) {
            var fixture = begin(false);
            var done = prepare(fixture);
            check(done.getCompound("Outputs").getList("ResourcePackages", Tag.TAG_COMPOUND).size() == 1,
                    "使用生产准备与校验生成冻结包");
            if (cancelled) fixture.ledger().cancel(fixture.operation(), ACTOR);
            var saved = fixture.save();
            var loaded = loadUnchanged(saved);
            check(loaded.save(new CompoundTag()).equals(saved), "准备或取消后冻结资源逐字段往返");
            check(loaded.ledger().transaction(fixture.operation()).phase()
                    == (cancelled ? Phase.CANCELLED : Phase.RESERVED), "未结算状态不推进");
        }
    }

    private static void malformedSchema() {
        var valid = settled(false, false).save();
        var bad = valid.copy(); bad.remove("Resources");
        rejectUnchanged(bad, "只缺资源表拒绝");
        bad = valid.copy(); bad.remove("ResourceVersion");
        rejectUnchanged(bad, "只缺版本拒绝");
        bad = valid.copy(); bad.putString("ResourceVersion", "1");
        rejectUnchanged(bad, "版本错型拒绝");
        for (int version : new int[]{0, 2}) {
            bad = valid.copy(); bad.putInt("ResourceVersion", version);
            rejectUnchanged(bad, "不支持的资源版本拒绝");
        }
        bad = valid.copy(); bad.putString("Resources", "invalid");
        rejectUnchanged(bad, "资源表错型拒绝");
        bad = valid.copy(); bad.getCompound("Resources").putInt("Version", 2);
        rejectUnchanged(bad, "资源包未来版本拒绝");
        bad = valid.copy(); bad.getCompound("Resources").putString("Packages", "invalid");
        rejectUnchanged(bad, "冻结包列表错型拒绝");
        bad = valid.copy(); bad.remove("Ledger");
        rejectUnchanged(bad, "缺主账本拒绝");
        bad = valid.copy(); bad.putString("Ledger", "invalid");
        rejectUnchanged(bad, "主账本错型拒绝");
    }

    private static void malformedSettlements() {
        var valid = settled(false, false).save();
        var missing = valid.copy(); missing.getCompound("Resources").put("Packages", new ListTag());
        rejectUnchanged(missing, "有资源引用但冻结表为空拒绝");
        var mismatched = valid.copy();
        var item = mismatched.getCompound("Resources").getList("Packages", Tag.TAG_COMPOUND)
                .getCompound(0).getList("Items", Tag.TAG_COMPOUND).getCompound(0);
        item.putInt("Count", item.getInt("Count") == 64 ? 63 : 64);
        rejectUnchanged(mismatched, "数量合法但来源不一致拒绝");
        for (boolean schema : new boolean[]{false, true}) {
            var bad = schema ? valid.copy() : withoutResources(valid);
            outputs(bad).putString("ResourcePackages", "invalid");
            rejectUnchanged(bad, "资源引用错型不因缺资源表而绕过");
            bad = schema ? valid.copy() : withoutResources(valid);
            var list = new ListTag(); list.add(StringTag.valueOf("invalid"));
            outputs(bad).put("ResourcePackages", list);
            rejectUnchanged(bad, "资源列表元素错型不因缺资源表而绕过");
        }
    }

    private static Fixture begin(boolean simulation) {
        var ledger = new Hk3WorldBubbleLedger();
        var resources = new Hk3WorldResourceBatches();
        UUID operation = new UUID(3, 1), target;
        if (simulation) {
            target = new UUID(4, 1);
            ledger.createSimulation(target, ACTOR, "fixture:restore_simulation");
            UUID stable = new UUID(3, 2);
            ledger.begin(stable, ACTOR, Domain.SIMULATED, target, Action.STABILIZE_SIMULATION);
            ledger.settle(stable, ACTOR, receipt(stable, Action.STABILIZE_SIMULATION));
            ledger.begin(operation, ACTOR, Domain.SIMULATED, target, Action.TERMINATE_SIMULATION);
        } else {
            target = ledger.discover("fixture:restore");
            ledger.begin(operation, ACTOR, Domain.REAL, target, Action.MINE);
        }
        return new Fixture(ledger, resources, operation, target);
    }

    private static Fixture settled(boolean simulation, boolean delivered) {
        var fixture = begin(simulation);
        fixture.ledger().settle(fixture.operation(), ACTOR, prepare(fixture));
        if (delivered) fixture.ledger().acknowledge(fixture.operation(), ACTOR);
        return fixture;
    }

    private static CompoundTag prepare(Fixture fixture) {
        var action = fixture.ledger().transaction(fixture.operation()).action();
        var done = Hk3WorldResourceSettlement.prepare(fixture.ledger(), fixture.resources(), fixture.operation(),
                ACTOR, TEAM, receipt(fixture.operation(), action), catalog(), 42);
        Hk3WorldResourceSettlement.validate(fixture.ledger(), fixture.resources(), fixture.operation(), ACTOR, TEAM, done);
        return done;
    }

    private static Hk3WorldResourceCatalog catalog() {
        return new Hk3WorldResourceCatalog("fixture", "v1",
                List.of(new Hk3WorldResourceCatalog.Entry("fixture:item", 1, "fixture:recipe")),
                List.of(new Hk3WorldResourceCatalog.Entry("fixture:fluid", 1, "fixture:fluid_recipe")));
    }

    private static CompoundTag receipt(UUID operation, Action action) {
        var tag = new CompoundTag();
        tag.putUUID("Batch", operation); tag.putUUID("Team", TEAM);
        tag.putString("Role", Hk3WorldResourceSettlement.role(action));
        tag.putString("Facility", "fixture:machine"); tag.putString("Recipe", "fixture:completed"); tag.putLong("Tick", 100);
        var inputs = new CompoundTag(); inputs.putInt("ConsumedFixture", 1);
        var outputs = new CompoundTag(); outputs.putInt("CompletedFixture", 1);
        tag.put("Inputs", inputs); tag.put("Outputs", outputs);
        return tag;
    }

    private static CompoundTag withoutResources(CompoundTag root) {
        var copy = root.copy(); copy.remove("ResourceVersion"); copy.remove("Resources"); return copy;
    }

    private static CompoundTag outputs(CompoundTag root) {
        return root.getCompound("Ledger").getList("Operations", Tag.TAG_COMPOUND).getCompound(0)
                .getCompound("Receipt").getCompound("Outputs");
    }

    private static Hk3WorldBubbleData loadUnchanged(CompoundTag root) {
        var before = root.copy();
        var loaded = Hk3WorldBubbleData.load(root);
        check(root.equals(before), "成功加载不修改调用者NBT");
        return loaded;
    }

    private static void rejectUnchanged(CompoundTag root, String reason) {
        var before = root.copy();
        try {
            Hk3WorldBubbleData.load(root);
        } catch (IllegalArgumentException expected) {
            check(root.equals(before), "拒绝加载不修改调用者NBT");
            check(true, reason);
            return;
        }
        throw new AssertionError(reason);
    }

    private static void check(boolean value, String reason) {
        checks++;
        if (!value) throw new AssertionError(reason);
    }
}
