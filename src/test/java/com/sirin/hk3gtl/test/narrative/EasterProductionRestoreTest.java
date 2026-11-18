package com.sirin.hk3gtl.test.narrative;

import com.sirin.hk3gtl.common.easter.Hk3EggProductionData;
import net.minecraft.nbt.*;

import java.util.*;
import java.util.function.Consumer;

/** 只校验个人产量账本恢复，不批准彩蛋规则或注入实际产量。 */
public final class EasterProductionRestoreTest {
    private static int checks;
    private static final UUID A = new UUID(1, 11), B = new UUID(2, 22), C = new UUID(3, 33);
    private static final UUID ALIAS = UUID.fromString("abcdefab-cdef-abcd-efab-cdefabcdefab");

    private static void check(boolean value, String message) {
        if (!value) throw new AssertionError(message);
        checks++;
    }

    private static CompoundTag fixture() {
        var root = new CompoundTag();
        var users = new CompoundTag();
        var a = new CompoundTag();
        a.putLong("fixture:zero", 0); a.putLong("fixture:count", 123); a.putLong("fixture:max", Long.MAX_VALUE);
        var b = new CompoundTag();
        b.putLong("fixture:count", 456); b.putLong("fixture:other", 789);
        users.put(A.toString(), a); users.put(B.toString(), b); users.put(C.toString(), new CompoundTag());
        root.put("Users", users);
        return root;
    }

    private static Hk3EggProductionData roundTrip(CompoundTag root) {
        var before = root.copy();
        var data = Hk3EggProductionData.load(root);
        check(root.equals(before), "合法读取不得修改输入NBT");
        var saved = data.save(new CompoundTag());
        check(saved.equals(root), "合法多用户计数逐字段往返");
        check(Hk3EggProductionData.load(saved).save(new CompoundTag()).equals(root), "再次保存读取不能改变计数");
        return data;
    }

    private static void validData() {
        var root = fixture();
        var data = roundTrip(root);
        check(data.count(A, "fixture:zero") == 0 && data.counts(A).containsKey("fixture:zero"), "显式LONG零值保留");
        check(data.count(A, "fixture:max") == Long.MAX_VALUE && data.count(A, "fixture:count") == 123,
                "LONG最大值与普通产量保持");
        check(data.count(B, "fixture:count") == 456 && data.count(B, "fixture:other") == 789,
                "不同用户同名物品独立");
        check(data.counts(C).isEmpty() && data.save(new CompoundTag()).getCompound("Users").contains(C.toString(), Tag.TAG_COMPOUND),
                "合法空个人表仍保存");
        check(data.count(new UUID(99, 99), "fixture:count") == 0 && data.counts(new UUID(99, 99)).isEmpty(), "未知用户查询不生成产量");
        var empty = new CompoundTag(); empty.put("Users", new CompoundTag());
        check(roundTrip(empty).count(A, "fixture:count") == 0, "合法空用户表兼容");
        var oneEmpty = new CompoundTag(); var users = new CompoundTag(); users.put(A.toString(), new CompoundTag()); oneEmpty.put("Users", users);
        check(roundTrip(oneEmpty).counts(A).isEmpty(), "仅一个合法空个人表兼容");
        var aliasRoot = new CompoundTag(); var aliasUsers = new CompoundTag(); var aliasCounts = new CompoundTag();
        aliasCounts.putLong("fixture:count", 777); aliasUsers.put(ALIAS.toString().toUpperCase(Locale.ROOT), aliasCounts); aliasRoot.put("Users", aliasUsers);
        var aliasBefore = aliasRoot.copy();
        var aliasData = Hk3EggProductionData.load(aliasRoot);
        check(aliasRoot.equals(aliasBefore) && aliasData.count(ALIAS, "fixture:count") == 777, "唯一大写UUID行兼容且不修改输入");
        var aliasSaved = aliasData.save(new CompoundTag());
        check(aliasSaved.getCompound("Users").contains(ALIAS.toString(), Tag.TAG_COMPOUND)
                && Hk3EggProductionData.load(aliasSaved).count(ALIAS, "fixture:count") == 777, "唯一大小写别名按既有UUID格式保存而不清计数");
    }

    private static void rejected(CompoundTag baseline, String label, Consumer<CompoundTag> mutation) {
        var corrupt = baseline.copy();
        mutation.accept(corrupt);
        var before = corrupt.copy();
        Hk3EggProductionData result = null;
        boolean rejected = false;
        try { result = Hk3EggProductionData.load(corrupt); }
        catch (IllegalArgumentException expected) { rejected = true; }
        check(rejected, label + "必须明确拒读");
        check(result == null, label + "不能返回已恢复的半份账本");
        check(corrupt.equals(before), label + "拒读不得改写原NBT");
    }

    private static List<Tag> nonLongTags() {
        var list = new ListTag(); list.add(LongTag.valueOf(1));
        return List.of(ByteTag.valueOf((byte) 1), ShortTag.valueOf((short) 1), IntTag.valueOf(1),
                FloatTag.valueOf(1), DoubleTag.valueOf(1), StringTag.valueOf("损坏"), list,
                new ByteArrayTag(new byte[]{1}), new IntArrayTag(new int[]{1}),
                new LongArrayTag(new long[]{1}), new CompoundTag());
    }

    private static void corruptData() {
        var baseline = fixture();
        rejected(baseline, "Users缺失", root -> root.remove("Users"));
        for (Tag wrong : nonLongTags()) {
            if (!(wrong instanceof CompoundTag)) rejected(baseline, "Users根表错型" + wrong.getId(), root -> root.put("Users", wrong.copy()));
        }
        rejected(baseline, "Users根表LONG错型", root -> root.putLong("Users", 1));
        for (Tag wrong : nonLongTags()) {
            if (!(wrong instanceof CompoundTag)) rejected(baseline, "个人行错型" + wrong.getId(),
                    root -> root.getCompound("Users").put(A.toString(), wrong.copy()));
        }
        rejected(baseline, "个人行LONG错型", root -> root.getCompound("Users").putLong(A.toString(), 1));
        rejected(baseline, "非法用户UUID", root -> root.getCompound("Users").put("不是UUID", new CompoundTag()));
        rejected(baseline, "同一UUID大小写别名冲突", root -> {
            var first = new CompoundTag(); first.putLong("fixture:count", 111);
            var second = new CompoundTag(); second.putLong("fixture:count", 222);
            root.getCompound("Users").put(ALIAS.toString(), first);
            root.getCompound("Users").put(ALIAS.toString().toUpperCase(Locale.ROOT), second);
        });
        rejected(baseline, "负LONG产量", root -> root.getCompound("Users").getCompound(A.toString()).putLong("fixture:count", -1));
        for (Tag wrong : nonLongTags()) rejected(baseline, "非LONG产量" + wrong.getId(),
                root -> root.getCompound("Users").getCompound(A.toString()).put("fixture:count", wrong.copy()));
        var after = roundTrip(baseline);
        check(after.count(A, "fixture:count") == 123 && after.count(B, "fixture:count") == 456,
                "混合坏行拒读后原合法用户计数没有被重置");
    }

    private static void saturation() {
        check(Hk3EggProductionData.plus(0, 0) == 0 && Hk3EggProductionData.plus(123, 456) == 579, "正常加法与零不变");
        check(Hk3EggProductionData.plus(Long.MAX_VALUE, 0) == Long.MAX_VALUE
                && Hk3EggProductionData.plus(0, Long.MAX_VALUE) == Long.MAX_VALUE, "最大值零加法不溢出");
        check(Hk3EggProductionData.plus(Long.MAX_VALUE - 1, 1) == Long.MAX_VALUE
                && Hk3EggProductionData.plus(Long.MAX_VALUE - 1, 2) == Long.MAX_VALUE
                && Hk3EggProductionData.plus(Long.MAX_VALUE, Long.MAX_VALUE) == Long.MAX_VALUE, "既有饱和规则保持");
        for (long[] pair : List.of(new long[]{-1, 0}, new long[]{0, -1}, new long[]{Long.MIN_VALUE, 1})) {
            boolean rejected = false;
            try { Hk3EggProductionData.plus(pair[0], pair[1]); }
            catch (IllegalArgumentException expected) { rejected = true; }
            check(rejected, "负产量加法仍拒绝");
        }
    }

    public static void main(String[] args) {
        validData(); corruptData(); saturation();
        System.out.println("工业彩蛋产量恢复：" + checks + "项检查通过；仅离线NBT与加法，未批准规则、未启动游戏。");
    }
}
