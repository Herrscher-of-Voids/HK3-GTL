package com.sirin.hk3gtl.test.dialogue;

import com.sirin.hk3gtl.common.badending.Hk3FinaleAttackData;
import net.minecraft.nbt.CompoundTag;

import java.util.UUID;

/** 【变更记录 #1】2026-09-30 23:35:44（修订119）：删除无；新增个人终局回归入口；修改测试主函数；用途：check同时覆盖生产数据隔离。 */
public final class FinaleAttackDataTest {
    public static void main(String[] args) {
        UUID first = UUID.fromString("00000000-0000-0000-0000-000000000001");
        UUID second = UUID.fromString("00000000-0000-0000-0000-000000000002");
        UUID meeting = UUID.fromString("00000000-0000-0000-0000-000000000003");
        UUID next = UUID.fromString("00000000-0000-0000-0000-000000000004");
        Hk3FinaleAttackData data = new Hk3FinaleAttackData();
        check(data.recordDirectHit(first, meeting) == -1, "unopened meeting rejected");
        data.begin(first, meeting);
        for (int i = 1; i <= 4; i++) check(data.recordDirectHit(first, meeting) == i, "first player's hits");
        data.begin(first, meeting);
        check(data.count(first, meeting) == 4, "reconnect retains count");
        data.begin(second, meeting);
        check(data.recordDirectHit(second, meeting) == 1, "other player isolated");
        check(data.count(first, meeting) == 4, "other player cannot advance first player");
        check(data.recordDirectHit(first, next) == -1, "stale meeting rejected");

        Hk3FinaleAttackData restored = Hk3FinaleAttackData.load(data.save(new CompoundTag()));
        check(restored.count(first, meeting) == 4, "saved progress restored");
        for (int i = 5; i <= 10; i++) check(restored.recordDirectHit(first, meeting) == i, "threshold");
        check(restored.recordDirectHit(first, meeting) == 10, "duplicate after threshold capped");
        restored.end(first, next);
        check(restored.count(first, meeting) == 10, "stale end ignored");
        restored.begin(first, next);
        check(restored.count(first, next) == 0, "new meeting resets count");
        restored.end(first, next);
        check(restored.recordDirectHit(first, next) == -1, "ended meeting rejected");
        check(restored.count(second, meeting) == 1, "second player unaffected");

        expectBad(new CompoundTag());
        CompoundTag malformed = restored.save(new CompoundTag());
        malformed.getCompound("Attempts").getCompound(second.toString()).putInt("Hits", 11);
        expectBad(malformed);
        FinalePersonalTest.run();
        System.out.println("Finale attack ledger: meeting/player isolation, ten hits, reload and corruption checks passed");
    }

    private static void expectBad(CompoundTag tag) {
        try {
            Hk3FinaleAttackData.load(tag);
            throw new AssertionError("damaged attack ledger accepted");
        } catch (IllegalStateException expected) {
            // Existing counts must not silently reset.
        }
    }

    private static void check(boolean ok, String message) {
        if (!ok) throw new AssertionError(message);
    }
}
