package com.sirin.hk3gtl.test.communication;

import com.sirin.hk3gtl.common.communication.Hk3FirstContactState;
import com.sirin.hk3gtl.common.communication.Hk3CommunicationData;
import net.minecraft.nbt.CompoundTag;
import java.util.UUID;

/**
 * 【变更记录 #1】2026-09-22 14:01:00（内测5第2次代码更新）
 * 新增首信状态转换与NBT持久化测试；无删除，不依赖玩家存档或游戏窗口。
 * First-contact transition and actual NBT round-trip tests, isolated from player saves.
 * 覆盖两个终态、重复提交、未读拒绝、世界/玩家隔离与损坏数据保留。
 * Covers both replies, duplicates, unread denial, world/player isolation and malformed-state retention.
 */
public final class FirstContactTest {
    /** 完整测试入口，失败抛异常使构建失败；不依赖-ea。 / Test entry throws on failure without requiring -ea. */
    public static void main(String[] args) {
        transitions();
        persistence();
        malformed();
        System.out.println("First contact: transitions, isolation, NBT round trips and corruption checks passed");
    }

    /** 遍历所有状态，确保发现/阅读/回复确定且幂等。 / Exhaust states to verify deterministic, idempotent transitions. */
    private static void transitions() {
        for (Hk3FirstContactState state : Hk3FirstContactState.values()) {
            check(state.discover().discover() == state.discover(), "discover idempotent");
            check(state.read().read() == state.read(), "read idempotent");
            if (state != Hk3FirstContactState.READ) {
                check(state.reply(true) == state && state.reply(false) == state, "only read can reply");
            }
        }
        Hk3FirstContactState pending = Hk3FirstContactState.LOCKED.discover().read();
        check(pending == Hk3FirstContactState.READ, "reading does not auto-reply");
        for (boolean accept : new boolean[]{true,false}) {
            Hk3FirstContactState chosen = pending.reply(accept);
            check(chosen.hasObservationData(), "both branches retain information");
            check(chosen.reply(!accept) == chosen, "opposite replay rejected");
            check(chosen.reply(accept) == chosen, "same replay idempotent");
            check(chosen.replyFact().equals(accept ? "CM-MAX-REPLY-ACCEPT" : "CM-MAX-REPLY-DECLINE"), "stable fact ID");
        }
        check(!Hk3FirstContactState.LOCKED.hasObservationData(), "pre-MAX has no clue");
        check(Hk3FirstContactState.AVAILABLE.hasObservationData(), "delivery grants clue before reply");
    }

    /** 独立UUID与世界实例隔离，所有合法状态经过真实NBT往返仍保留。 / Separate players/world instances; round-trip every legal state through NBT. */
    private static void persistence() {
        UUID one = UUID.fromString("00000000-0000-0000-0000-000000000001");
        UUID two = UUID.fromString("00000000-0000-0000-0000-000000000002");
        Hk3CommunicationData data = new Hk3CommunicationData();
        check(!data.reply(one, true), "cannot reply before delivery");
        check(data.discover(one), "first discovery changes state");
        check(!data.discover(one), "duplicate discovery suppressed");
        check(!data.reply(one, false), "cannot reply before opening");
        check(data.read(one), "first read recorded");
        check(data.reply(one, false), "refusal submitted once");
        check(!data.reply(one, true), "contradictory replay rejected");
        check(data.state(two) == Hk3FirstContactState.LOCKED, "other player untouched");
        check(new Hk3CommunicationData().state(one) == Hk3FirstContactState.LOCKED, "other world untouched");
        for (Hk3FirstContactState state : Hk3FirstContactState.values()) {
            CompoundTag root = new CompoundTag();
            CompoundTag contacts = new CompoundTag();
            contacts.putString(one.toString(), state.name());
            root.put("Contacts", contacts);
            Hk3CommunicationData restored = Hk3CommunicationData.load(root);
            CompoundTag saved = restored.save(new CompoundTag());
            check(Hk3CommunicationData.load(saved).state(one) == state, "round-trip " + state);
        }
        Hk3CommunicationData restored = Hk3CommunicationData.load(data.save(new CompoundTag()));
        check(restored.state(one) == Hk3FirstContactState.DECLINED, "refusal survives reconnect/death data reload");
        check(restored.state(one).hasObservationData(), "refusal retains clue after reload");
        check(restored.hasFact(one, "CM-MAX-OTTO"), "new letter fact survives reload");
        check(restored.hasFact(one, "CM-MAX-REPLY-DECLINE"), "chosen branch fact present");
        check(!restored.hasFact(one, "CM-MAX-REPLY-ACCEPT"), "opposite branch absent");
        check(!restored.hasFact(one, "E-WL-001"), "never fabricates legacy gift fact");
    }

    /** 未知名字或类型不可当作新玩家重置；原始条目保持可恢复。 / Unknown names/types cannot reset to new-player state; preserve the original entry. */
    private static void malformed() {
        UUID id = UUID.fromString("00000000-0000-0000-0000-000000000003");
        for (boolean wrongType : new boolean[]{false,true}) {
            CompoundTag entries = new CompoundTag();
            if (wrongType) entries.putInt(id.toString(), 999);
            else entries.putString(id.toString(), "FUTURE_STATE");
            entries.putString("invalid-uuid", "ACCEPTED");
            CompoundTag root = new CompoundTag(); root.put("Contacts", entries);
            Hk3CommunicationData data = Hk3CommunicationData.load(root);
            try {
                data.discover(id);
                throw new AssertionError("Unknown state accepted");
            } catch (IllegalStateException expected) {
                check(data.save(new CompoundTag()).getCompound("Contacts").equals(entries), "unknown entries preserved");
            }
        }
    }

    /** 断言失败立即终止构建，不依赖JVM断言开关。 / Fail the build regardless of JVM assertion flags. */
    private static void check(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }
}
