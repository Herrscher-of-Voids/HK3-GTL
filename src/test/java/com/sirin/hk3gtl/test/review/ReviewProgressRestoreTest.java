package com.sirin.hk3gtl.test.review;

import com.sirin.hk3gtl.common.review.Hk3ReviewData;
import com.sirin.hk3gtl.common.review.Hk3ReviewLedger;
import net.minecraft.nbt.*;

import java.util.*;
import java.util.function.Consumer;

/** 会面持久化字段损坏必须拒读，不能把已问问题与重播进度静默清空。 */
public final class ReviewProgressRestoreTest {
    private static int checks;
    private static final UUID TEAM = new UUID(5, 6), A = new UUID(7, 8), B = new UUID(9, 10);
    private static final List<Integer> QUESTIONS = List.of(2, 7, 4);
    private record Fixture(Hk3ReviewLedger ledger, UUID meeting) {}

    private static void check(boolean value, String message) {
        if (!value) throw new AssertionError(message);
        checks++;
    }

    private static CompoundTag sources() {
        var tag = new CompoundTag();
        tag.putString("Source", "仅离线夹具，不是生产资格");
        return tag;
    }

    private static Fixture first(int count) {
        var ledger = new Hk3ReviewLedger();
        check(ledger.qualify(TEAM, Hk3ReviewLedger.Kind.FIRST, sources()), "夹具取得一审资格");
        var meeting = ledger.beginFirst(TEAM, List.of(A), new Random(6));
        check(ledger.openingRead(meeting.id(), A), "夹具读完开场");
        for (int i = 0; i < count; i++) {
            int q = QUESTIONS.get(i);
            check(ledger.choose(meeting.id(), A, q) && ledger.answerRead(meeting.id(), A, q), "夹具依次读完问题");
        }
        ledger.depart(A);
        return new Fixture(ledger, meeting.id());
    }

    private static CompoundTag loadUnchanged(CompoundTag source, boolean data) {
        var before = source.copy();
        var result = data ? Hk3ReviewData.load(source).save(new CompoundTag()) : Hk3ReviewLedger.load(source).save();
        check(source.equals(before), "正常加载不得修改输入NBT");
        return result;
    }

    private static void firstRestarts() {
        for (int count = 0; count <= 3; count++) {
            var fixture = first(count);
            var saved = fixture.ledger.save();
            check(loadUnchanged(saved, false).equals(saved), "一审合法账本逐字段回读");
            var loaded = Hk3ReviewLedger.load(loadUnchanged(saved, true));
            var at = loaded.meeting(fixture.meeting);
            check(at.phase() == Hk3ReviewLedger.Phase.PAUSED && at.questions().equals(QUESTIONS.subList(0, count)), "一审0至3题重启保存题序");
            check(!loaded.settled(TEAM, Hk3ReviewLedger.Kind.FIRST) && !loaded.experienced(A, Hk3ReviewLedger.Kind.FIRST), "暂停不误授许可或亲历");
            at = loaded.restartFirst(fixture.meeting, A, List.of(A), new Random(6));
            check(at != null && at.replayIndex() == 0 && at.questions().size() == count, "重开重置重播指针而不清问题");
            check(loaded.openingRead(fixture.meeting, A), "恢复后重读开场");
            for (int i = 0; i < count; i++) check(loaded.answerRead(fixture.meeting, A, QUESTIONS.get(i)), "原问题依次重播");
            for (int i = count; i < 3; i++) {
                int q = QUESTIONS.get(i);
                check(loaded.choose(fixture.meeting, A, q) && loaded.answerRead(fixture.meeting, A, q), "仅补剩余新问题");
            }
            var result = loaded.finishFirst(fixture.meeting, A);
            check(result != null && result.firstTeamSettlement() && loaded.finishFirst(fixture.meeting, A) == null, "完整三问仅结算一次");
            var completed = Hk3ReviewLedger.load(loadUnchanged(loaded.save(), true));
            check(completed.meeting(fixture.meeting).phase() == Hk3ReviewLedger.Phase.COMPLETE
                    && completed.meeting(fixture.meeting).questions().equals(QUESTIONS)
                    && completed.settlement(TEAM, Hk3ReviewLedger.Kind.FIRST).equals(fixture.meeting), "完成会面与原许可回执保存");
        }
    }

    private static void secondToEnd(Hk3ReviewLedger ledger, UUID meeting, UUID actor) {
        for (int i = 0; i < 30; i++) {
            var at = ledger.meeting(meeting);
            if (at.checkpoint().equals("S209")) return;
            check(ledger.advanceSecond(meeting, actor, at.checkpoint(), 0), "二审沿批准正文推进");
        }
        throw new AssertionError("二审未在既有正文边界内结束");
    }

    private static void secondRestarts() {
        var fixture = first(3);
        var ledger = fixture.ledger;
        ledger.restartFirst(fixture.meeting, A, List.of(A, B), new Random(6));
        UUID representative = ledger.meeting(fixture.meeting).representative();
        ledger.openingRead(fixture.meeting, representative);
        for (int q : QUESTIONS) ledger.answerRead(fixture.meeting, representative, q);
        check(ledger.finishFirst(fixture.meeting, A) != null && ledger.finishFirst(fixture.meeting, B) != null, "二审夹具两人各自完成一审");
        check(ledger.qualify(TEAM, Hk3ReviewLedger.Kind.SECOND, sources()), "二审保留真实资格入口");
        var second = ledger.beginSecond(TEAM, A);
        check(second != null && ledger.advanceSecond(second.id(), A, "S201", 0)
                && ledger.advanceSecond(second.id(), A, "S202", 0), "二审进入既有中间检查点");
        ledger.depart(A);
        var tag = ledger.save();
        check(loadUnchanged(tag, false).equals(tag), "暂停二审完整回读");
        ledger = Hk3ReviewLedger.load(loadUnchanged(tag, true));
        check(ledger.meeting(second.id()).checkpoint().equals("S203") && ledger.resumeSecond(second.id(), A) != null, "二审重启不回退检查点");
        check(!ledger.settled(TEAM, Hk3ReviewLedger.Kind.SECOND) && !ledger.experienced(A, Hk3ReviewLedger.Kind.SECOND), "中间检查点不授二审许可");
        secondToEnd(ledger, second.id(), A);
        var firstResult = ledger.finishSecond(second.id(), A);
        check(firstResult != null && firstResult.firstTeamSettlement(), "首次二审结算有来源");
        var supplement = ledger.beginSecond(TEAM, B);
        check(supplement != null && supplement.supplement() && supplement.checkpoint().equals("SP01"), "补行标志和专用开场");
        ledger.depart(B);
        ledger = Hk3ReviewLedger.load(loadUnchanged(ledger.save(), true));
        check(ledger.meeting(supplement.id()).supplement() && ledger.resumeSecond(supplement.id(), B) != null
                && ledger.meeting(supplement.id()).checkpoint().equals("SP01"), "补行重启保留身份与检查点");
        secondToEnd(ledger, supplement.id(), B);
        var supplementResult = ledger.finishSecond(supplement.id(), B);
        check(supplementResult != null && !supplementResult.firstTeamSettlement(), "补行不重复发团队许可");
        ledger = Hk3ReviewLedger.load(loadUnchanged(ledger.save(), true));
        check(ledger.meeting(second.id()).phase() == Hk3ReviewLedger.Phase.COMPLETE
                && ledger.meeting(supplement.id()).phase() == Hk3ReviewLedger.Phase.COMPLETE
                && ledger.settlement(TEAM, Hk3ReviewLedger.Kind.SECOND).equals(second.id()), "完成二审与首份团队来源不被覆盖");

        var abandonedFixture = first(3);
        var abandoned = abandonedFixture.ledger;
        abandoned.restartFirst(abandonedFixture.meeting, A, List.of(A), new Random(6));
        abandoned.openingRead(abandonedFixture.meeting, A);
        for (int q : QUESTIONS) abandoned.answerRead(abandonedFixture.meeting, A, q);
        abandoned.finishFirst(abandonedFixture.meeting, A);
        abandoned.qualify(TEAM, Hk3ReviewLedger.Kind.SECOND, sources());
        var old = abandoned.beginSecond(TEAM, A);
        abandoned.leaveTeam(A);
        abandoned = Hk3ReviewLedger.load(loadUnchanged(abandoned.save(), true));
        check(abandoned.meeting(old.id()).phase() == Hk3ReviewLedger.Phase.ABANDONED
                && abandoned.resumeSecond(old.id(), A) == null
                && !abandoned.settled(TEAM, Hk3ReviewLedger.Kind.SECOND), "换队中止历史不复活或授予许可");
    }

    private static void rejected(CompoundTag baseline, String label, Consumer<CompoundTag> mutation) {
        for (boolean data : new boolean[]{false, true}) {
            var corrupt = baseline.copy();
            mutation.accept(corrupt.getList("Meetings", Tag.TAG_COMPOUND).getCompound(0));
            var before = corrupt.copy();
            boolean rejected = false;
            try {
                if (data) Hk3ReviewData.load(corrupt); else Hk3ReviewLedger.load(corrupt);
            } catch (IllegalArgumentException expected) { rejected = true; }
            check(rejected, label + "应由" + (data ? "Data" : "Ledger") + "拒读");
            check(corrupt.equals(before), label + "拒读不得改写原NBT");
        }
    }

    private static void corruptFields() {
        var fixture = first(2);
        fixture.ledger.restartFirst(fixture.meeting, A, List.of(A), new Random(6));
        fixture.ledger.depart(A);
        var baseline = fixture.ledger.save();
        check(fixture.ledger.meeting(fixture.meeting).replayIndex() == 0, "合法重播前暂停保留两题但指针为0");
        for (String key : List.of("Participants", "Questions", "Replay", "Checkpoint", "Supplement")) {
            rejected(baseline, key + "缺失", row -> row.remove(key));
            if (!key.equals("Checkpoint")) rejected(baseline, key + "字符串错型", row -> row.putString(key, "损坏"));
        }
        rejected(baseline, "Participants非列表", row -> row.put("Participants", new CompoundTag()));
        rejected(baseline, "Participants列表非字符串内容", row -> {
            var list = new ListTag(); list.add(IntTag.valueOf(1)); row.put("Participants", list);
        });
        rejected(baseline, "Questions普通整数列表", row -> {
            var list = new ListTag(); list.add(IntTag.valueOf(2)); list.add(IntTag.valueOf(7)); row.put("Questions", list);
        });
        rejected(baseline, "Questions长整型数组", row -> row.putLongArray("Questions", new long[]{2, 7}));
        rejected(baseline, "Checkpoint整数错型", row -> row.putInt("Checkpoint", 1));
        for (Tag wrong : List.of(ByteTag.valueOf((byte) 0), ShortTag.valueOf((short) 0), LongTag.valueOf(0),
                FloatTag.valueOf(0), DoubleTag.valueOf(0))) {
            rejected(baseline, "Replay数值错型" + wrong.getId(), row -> row.put("Replay", wrong.copy()));
        }
        for (Tag wrong : List.of(IntTag.valueOf(0), IntTag.valueOf(1), ShortTag.valueOf((short) 0),
                LongTag.valueOf(1), FloatTag.valueOf(0), DoubleTag.valueOf(1))) {
            rejected(baseline, "Supplement数值错型" + wrong.getId(), row -> row.put("Supplement", wrong.copy()));
        }
        rejected(baseline, "Supplement非法负BYTE", row -> row.putByte("Supplement", (byte) -1));
        rejected(baseline, "Supplement非法BYTE2", row -> row.putByte("Supplement", (byte) 2));
        check(loadUnchanged(baseline, false).equals(baseline), "全部坏字段拒读后合法进度不变");
        var restored = Hk3ReviewLedger.load(loadUnchanged(baseline, true));
        check(restored.meeting(fixture.meeting).questions().equals(List.of(2, 7))
                && restored.meeting(fixture.meeting).replayIndex() == 0
                && !restored.settled(TEAM, Hk3ReviewLedger.Kind.FIRST), "两题暂停恢复不清空或误授许可");
        var emptyPeople = baseline.copy();
        emptyPeople.getList("Meetings", Tag.TAG_COMPOUND).getCompound(0).put("Participants", new ListTag());
        check(loadUnchanged(emptyPeople, false).equals(emptyPeople), "暂停后的合法空参与者列表仍兼容");
    }

    public static void main(String[] args) {
        firstRestarts();
        secondRestarts();
        corruptFields();
        System.out.println("审查会面恢复：" + checks + "项检查通过；仅离线NBT与状态机，未启动游戏。");
    }
}
