package com.sirin.hk3gtl.test.dialogue;

import com.sirin.hk3gtl.common.dialogue.Hk3FinaleIfData;
import net.minecraft.nbt.CompoundTag;

import java.util.UUID;

/** 检查个人/存档隔离、五次上限、重复选择和损坏数据拒绝。 */
public final class FinaleIfDataTest {
    public static void main(String[] args) {
        UUID first = UUID.fromString("00000000-0000-0000-0000-000000000001");
        UUID second = UUID.fromString("00000000-0000-0000-0000-000000000002");
        Hk3FinaleIfData world = new Hk3FinaleIfData();
        for (int i = 0; i < 5; i++) check(world.select(first, i), "first five");
        check(world.selectedCount(first) == 5, "five counted");
        check(world.select(first, 2), "repeat remains readable");
        check(world.selectedCount(first) == 5, "repeat does not charge again");
        check(!world.select(first, 5), "sixth rejected");
        check(!world.select(first, 26) && !world.select(first, -1), "invalid indexes rejected");
        check(world.select(second, 25), "second player independent");
        check(new Hk3FinaleIfData().selectedCount(first) == 0, "other world independent");

        CompoundTag saved = world.save(new CompoundTag());
        Hk3FinaleIfData restored = Hk3FinaleIfData.load(saved);
        check(restored.selectedCount(first) == 5 && restored.selectedCount(second) == 1, "NBT round trip");
        check(!restored.select(first, 25), "limit survives reload");
        expectBad(new CompoundTag());
        CompoundTag malformed = new CompoundTag();
        malformed.putString("Selected", "bad");
        expectBad(malformed);
        CompoundTag entries = new CompoundTag();
        entries.putInt(first.toString(), 1 << 26);
        malformed.remove("Selected");
        malformed.put("Selected", entries);
        expectBad(malformed);
        entries.putInt(first.toString(), 0b11_1111);
        expectBad(malformed);
        entries.remove(first.toString());
        entries.putInt("not-a-uuid", 1);
        expectBad(malformed);
        System.out.println("Finale IF ledger: five selections, replay, player/world isolation, NBT and corruption checks passed");
    }

    private static void expectBad(CompoundTag tag) {
        try {
            Hk3FinaleIfData.load(tag);
            throw new AssertionError("damaged ledger accepted");
        } catch (IllegalStateException expected) {
            // 损坏账本必须拒绝，不能回退到零次选择。
        }
    }

    private static void check(boolean ok, String message) {
        if (!ok) throw new AssertionError(message);
    }
}
