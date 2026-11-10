package com.sirin.hk3gtl.common.dimension.height;

/** 【变更记录 #4】2026-10-31 00:46:39（第4次备注 · 修订187）：删除无；新增降落入口普通、高层、封顶、原高入口与NaN五项边界校验；修改共用生产策略；用途：补足高空入口回归，不代替实际飞行。 */

import net.minecraft.nbt.CompoundTag;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.function.Consumer;

/**
 * 【文件职责】直接执行生产高度策略与NBT合同，覆盖旧边界保留、编码极限和损坏数据拒绝。
 * 【变更记录 #1】2026-10-17 21:31:07（修订166）
 * - 删除：无。新增：保存重开、类型校验、未知版本、只读快照和2032极限等独立行为回归。
 * - 修改：不启动Minecraft、不构造世界、不写存档；由项目测试任务运行主方法。
 * - 用途：保证合同错误不会静默降高；本测试不代替Mixin、光影、实体传送与区块重进验收。
 *
 * 【变更记录 #2】2026-10-17 21:41:50（修订166）
 * - 删除：无；保留新世界可先持有空快照的构造测试。
 * - 新增：启用合同尚未冻结时禁止序列化、载入时空快照必须拒绝的两项行为回归。
 * - 修改：直接调用生产NBT读写入口，验证先保存后启动不能绕过持久合同边界。
 * - 用途：防止初始空快照落盘，或既有存档清空快照后被服务重新冻结而忽略资源变化。
 */
/** 【变更记录 #3】2026-10-29 23:06:53（本轮高度与预览修复）：删除无；新增纯临时目录名单及备份回归；修改主入口先运行升级保护检查；用途：拒绝误选旧档和无可信备份的扩高，不代替游戏重开验收。 */
public final class Hk3HeightContractTest {
    private static int checked;

    private Hk3HeightContractTest() {
    }

    public static void main(String[] args) throws java.io.IOException {
        Hk3HeightWorldUpgradeTest.main(args);
        policyBoundaries();
        check(Hk3HeightLandingPolicy.arrivalY(600, 70) == 600, "普通地表保持原降落入口");
        check(Hk3HeightLandingPolicy.arrivalY(600, 901) == 909, "高空建筑上方留足降落净空");
        check(Hk3HeightLandingPolicy.arrivalY(600, 1024) == 1032, "封顶建筑允许从建筑上方进入");
        check(Hk3HeightLandingPolicy.arrivalY(1200, 901) == 1200, "原本更高的入口不降低");
        boolean rejected=false;try{Hk3HeightLandingPolicy.arrivalY(Double.NaN, 0);}catch(IllegalArgumentException expected){rejected=true;}
        check(rejected, "非法降落高度拒绝");
        persistenceContract();
        malformedContracts();
        System.out.println("高度合同生产逻辑检查通过：" + checked + "项；未执行游戏验收。");
    }

    private static void policyBoundaries() {
        check(Hk3HeightPolicy.expand(-64, 384, 384, 1024)
                .equals(new Hk3HeightBounds(-64, 384, 384, 1088, 1024)), "主世界保持负64最低高度");
        check(Hk3HeightPolicy.expand(0, 256, 128, 1024).logicalHeight() == 128,
                "下界保留128逻辑高度");
        check(Hk3HeightPolicy.expand(0, 512, 448, 528).newHeight() == 528,
                "最低配置仍扩展已有512高度维度");
        check(Hk3HeightPolicy.expand(0, 64, 64, 1024).originalHeight() == 64,
                "小型维度保留原始64高度快照");
        check(Hk3HeightPolicy.expand(0, 1536, 1536, 1024).newTopExclusive() == 1536,
                "高于目标的原始范围不缩小");
        check(Hk3HeightPolicy.expand(-2032, 16, 0, 2032).newHeight() == 4064,
                "原版编码上下极限共同可达");
        check(Hk3HeightPolicy.expand(2016, 16, 0, 528).newHeight() == 16,
                "目标低于高空原维度时保持原范围");
        rejects(() -> Hk3HeightPolicy.expand(-64, 384, 384, 512), "512未扩展现有512维度而不允许作为目标");
        rejects(() -> Hk3HeightPolicy.expand(-64, 384, 384, 1025), "非16对齐目标拒绝");
        rejects(() -> Hk3HeightPolicy.expand(-64, 384, 384, 2048), "超过编码上界拒绝");
        rejects(() -> Hk3HeightPolicy.expand(-2048, 384, 384, 1024), "最低高度低于编码范围拒绝");
        rejects(() -> Hk3HeightPolicy.expand(-63, 384, 384, 1024), "原最低高度未对齐拒绝");
        rejects(() -> Hk3HeightPolicy.expand(-64, 383, 383, 1024), "原高度未对齐拒绝");
        rejects(() -> Hk3HeightPolicy.expand(2016, 32, 32, 1024), "原上界越过2032拒绝");
        rejects(() -> Hk3HeightPolicy.expand(0, 256, -1, 1024), "负逻辑高度拒绝");
        rejects(() -> Hk3HeightPolicy.expand(0, 256, 257, 1024), "逻辑高度高于原范围拒绝");
        rejects(() -> Hk3HeightPolicy.expand(Integer.MAX_VALUE, Integer.MAX_VALUE, 0, 1024),
                "损坏整数不得借溢出绕过范围");
        rejects(() -> new Hk3HeightBounds(0, 512, 448, 256, 256), "快照不得缩小原范围");
        rejects(() -> new Hk3HeightBounds(-64, 384, 384, 1088, 1088), "快照上界必须包含最低高度");
    }

    private static Hk3HeightWorldState sample() {
        return new Hk3HeightWorldState(UUID.fromString("42d5217c-e034-4ced-819f-7dd293ea9c23"), 1, 1024, true,
                Map.of("minecraft:overworld", Hk3HeightPolicy.expand(-64, 384, 384, 1024),
                        "minecraft:the_nether", Hk3HeightPolicy.expand(0, 256, 128, 1024),
                        "sgjourney:lantea", Hk3HeightPolicy.expand(0, 512, 448, 1024)));
    }

    private static void persistenceContract() {
        Hk3HeightWorldState original = sample();
        Hk3HeightWorldState reopened = Hk3HeightWorldState.fromNbt(original.toNbt());
        check(original.equals(reopened), "保存重开完整保留世界UUID、策略和三种维度快照");
        check(reopened.topExclusive() == 1024 && reopened.enabled() && reopened.contractVersion() == 1,
                "重开从合同恢复冻结上界");
        check(original.equals(Hk3HeightWorldState.fromNBT(original.toNBT())), "大小写别名保持相同合同");
        Map<String, Hk3HeightBounds> mutable = new HashMap<>(original.dimensions());
        Hk3HeightWorldState copied = original.withDimensions(mutable);
        mutable.clear();
        check(copied.dimensions().size() == 3, "外部修改来源map不会改变已冻结快照");
        try {
            copied.dimensions().clear();
            throw new AssertionError("合同快照不应允许外部原位修改");
        } catch (UnsupportedOperationException expected) {
            checked++;
        }
        Hk3HeightWorldState disabled = new Hk3HeightWorldState(UUID.randomUUID(), 1, 1024, false,
                Map.of("minecraft:overworld", Hk3HeightPolicy.unchanged(-64, 384, 384)));
        check(disabled.equals(Hk3HeightWorldState.fromNbt(disabled.toNbt())), "禁用合同只保存原始范围");
        check(!original.dimensions().equals(Map.of("minecraft:overworld",
                Hk3HeightPolicy.expand(-64, 512, 384, 1024))), "相同新上界不能掩盖原资源边界变化");
        Hk3HeightWorldState fresh = original.withDimensions(Map.of());
        check(fresh.dimensions().isEmpty() && fresh.worldId().equals(original.worldId()),
                "新世界可先冻结身份再填维度快照");
        rejects(() -> fresh.toNbt(), "启用合同未冻结维度快照前不得持久化");
    }

    private static void malformedContracts() {
        bad(tag -> tag.putInt("contractVersion", 2), "未知合同版本拒绝");
        bad(tag -> tag.remove("worldId"), "缺世界身份拒绝");
        bad(tag -> tag.putIntArray("worldId", new int[]{1, 2, 3}), "UUID数组长度错误拒绝");
        bad(tag -> tag.putString("worldId", UUID.randomUUID().toString()), "UUID字符串不能冒充官方UUID编码");
        bad(tag -> tag.putLong("topExclusive", 1024L), "可转换的错误数字类型仍拒绝");
        bad(tag -> tag.putInt("topExclusive", 512), "载入不降级到512");
        bad(tag -> tag.putInt("topExclusive", 2032), "改配置不能冒充新合同上界");
        bad(tag -> tag.putByte("enabled", (byte) 2), "布尔标记非0非1拒绝");
        bad(tag -> tag.putInt("enabled", 1), "整数不能冒充布尔标记");
        bad(tag -> tag.putString("dimensions", "{}"), "维度对象错误类型拒绝");
        bad(tag -> tag.put("dimensions", new CompoundTag()), "载入时启用合同空快照拒绝");
        bad(tag -> tag.getCompound("dimensions").putString("minecraft:overworld", "错误"),
                "单个维度快照错误类型拒绝");
        bad(tag -> tag.getCompound("dimensions").getCompound("minecraft:overworld").remove("logicalHeight"),
                "不完整维度快照拒绝");
        bad(tag -> tag.getCompound("dimensions").getCompound("minecraft:overworld").putInt("newHeight", 384),
                "损坏快照不得被解释成旧高度");
        bad(tag -> tag.getCompound("dimensions").getCompound("minecraft:overworld").putLong("originalMinY", -64),
                "快照数字类型严格校验");
        bad(tag -> tag.putBoolean("enabled", false), "已扩展合同不能只改启用标记降高");
        bad(tag -> tag.putInt("unexpected", 1), "根合同未知字段拒绝");
        bad(tag -> tag.getCompound("dimensions").put("INVALID:Type", tag.getCompound("dimensions")
                .getCompound("minecraft:overworld").copy()), "大写或无效维度类型ID拒绝");
        rejects(() -> new Hk3HeightWorldState(UUID.randomUUID(), 1, 1024, true,
                Map.of("overworld", Hk3HeightPolicy.expand(0, 256, 256, 1024))), "快照键必须具有命名空间");
        rejects(() -> Hk3HeightWorldState.fromNbt(new CompoundTag()), "空合同不冒充已有世界默认配置");
    }

    private static void bad(Consumer<CompoundTag> corrupt, String message) {
        CompoundTag tag = sample().toNbt();
        corrupt.accept(tag);
        rejects(() -> Hk3HeightWorldState.fromNbt(tag), message);
    }

    private static void rejects(Runnable action, String message) {
        try {
            action.run();
        } catch (IllegalArgumentException expected) {
            checked++;
            return;
        }
        throw new AssertionError(message);
    }

    private static void check(boolean valid, String message) {
        if (!valid) throw new AssertionError(message);
        checked++;
    }
}
