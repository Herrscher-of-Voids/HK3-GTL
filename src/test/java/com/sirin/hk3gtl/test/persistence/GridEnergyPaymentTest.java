package com.sirin.hk3gtl.test.persistence;

import com.sirin.hk3gtl.common.capability.Hk3GridEnergyPayment;
import com.sirin.hk3gtl.common.machine.Hk3RecipeLogic;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import org.objectweb.asm.*;
import org.objectweb.asm.tree.*;

import java.math.BigInteger;
import java.util.*;

/**
 * 【变更记录 #1】2026-10-01 17:33:35（修订138）
 * 删除：无；新增：大额、多项、竞争失败、模拟、输出失败和直接扣电边界回归。
 * 修改：用守恒性质及生产字节码接线核对，不启动或修改游戏账户。
 * 用途：验证EU适配报告与实际后端确认一致；第三方电网、机器推进及多人仍需实机验收。
 */
/** 【变更记录 #2】2026-10-01 17:41:38（修订139）：删除无；新增统一后端入口契约；修改原三处直接调用计数；用途：三条适配共用可退款提交且全部为BigInteger。 */
/**
 * 【变更记录 #3】2026-10-17 14:44:46（第3次备注 · 内测5修订162）
 * 删除：要求现役能源执行器继续调用退役虚数锚的字节码断言。
 * 新增：旧锚分支必须不存在的契约；修改：继续检查研究与注视度守卫接线。
 * 用途：匹配设备退役语义，能源支付、守恒、提交及退款回归保持执行。
 */
public final class GridEnergyPaymentTest {
    private static int checks;
    private static final BigInteger MAX = BigInteger.valueOf(Long.MAX_VALUE);
    private static void check(boolean pass, String reason) { checks++; if (!pass) throw new AssertionError(reason); }
    private static BigInteger sum(List<Long> values) {
        BigInteger total = BigInteger.ZERO;
        if (values != null) for (Long n : values) if (n != null) total = total.add(BigInteger.valueOf(n));
        return total;
    }
    private static final class Account {
        BigInteger amount;
        boolean refuse;
        int writes;
        BigInteger last = BigInteger.ZERO;
        Account(BigInteger initial) { amount = initial; }
        boolean change(BigInteger delta) {
            writes++; last = delta;
            if (refuse || amount.add(delta).signum() < 0) return false;
            amount = amount.add(delta); return true;
        }
    }
    public static void main(String[] args) throws Exception {
        largePayments(); failures(); direct(); simulation(); generatedCases(); tickCommit(); productionContract();
        System.out.println("Grid energy payment: " + checks + " checks passed; backend fixtures and wiring only, live machine acceptance pending");
    }
    private static void largePayments() {
        var demand = List.of(Long.MAX_VALUE, Long.MAX_VALUE, 25L);
        BigInteger full = MAX.multiply(BigInteger.TWO).add(BigInteger.valueOf(25));
        var account = new Account(full.add(BigInteger.valueOf(100)));
        var paid = Hk3GridEnergyPayment.input(demand, () -> account.amount, account::change, false);
        check(paid.transferred().equals(full) && paid.remaining() == null, "多个long费用全量支付");
        check(account.amount.equals(BigInteger.valueOf(100)) && account.last.equals(full.negate()), "后端接收完整BigInteger无饱和");
        check(account.writes == 1, "合并需求一次提交");
        account.amount = MAX.add(BigInteger.valueOf(3));
        var partial = Hk3GridEnergyPayment.input(demand, () -> account.amount, account::change, false);
        check(partial.transferred().equals(MAX.add(BigInteger.valueOf(3))), "余额可超过long并精确部分付款");
        check(partial.remaining().equals(List.of(Long.MAX_VALUE - 3, 25L)), "剩余清单分项无溢出");
        check(sum(partial.remaining()).add(partial.transferred()).equals(full), "部分支付守恒");
        var next = new Account(MAX);
        var tail = Hk3GridEnergyPayment.input(partial.remaining(), () -> next.amount, next::change, false);
        check(tail.remaining().equals(List.of(22L)) && tail.transferred().equals(MAX), "多个能源处理器连续接力不丢尾款");
        tail.remaining().add(1L);
        check(demand.equals(List.of(Long.MAX_VALUE, Long.MAX_VALUE, 25L)), "剩余可变且不改原需求");
        var output = new Account(BigInteger.TEN.pow(50)); var initial = output.amount;
        var stored = Hk3GridEnergyPayment.output(demand, output::change, false);
        check(stored.remaining() == null && output.amount.equals(initial.add(full)), "发电合并产额不截断");
        check(output.writes == 1 && output.last.equals(full), "发电实际仅提交一次");
    }
    private static void failures() {
        var account = new Account(BigInteger.valueOf(1000)); account.refuse = true;
        var demand = List.of(10L, 20L);
        var rejected = Hk3GridEnergyPayment.input(demand, () -> account.amount, account::change, false);
        check(rejected.transferred().signum() == 0 && rejected.remaining().equals(demand), "预查足够但实际拒绝不能伪成功");
        check(account.amount.intValueExact() == 1000 && account.writes == 1, "拒绝不重试或改账");
        rejected.remaining().set(0, 1L);
        check(demand.get(0) == 10L, "拒绝返回独立清单");
        var out = Hk3GridEnergyPayment.output(demand, account::change, false);
        check(out.transferred().signum() == 0 && out.remaining().equals(demand), "发电写入拒绝仍保留全部待处理量");
        check(Hk3GridEnergyPayment.change(-100L, () -> account.amount, account::change) == 0, "研究取电失败返回零");
        check(Hk3GridEnergyPayment.change(100L, () -> account.amount, account::change) == 0, "直接充电失败返回零");
        var stale = new Account(BigInteger.valueOf(4));
        var staleResult = Hk3GridEnergyPayment.input(List.of(10L), () -> BigInteger.valueOf(100), stale::change, false);
        check(staleResult.remaining().equals(List.of(10L)) && stale.amount.intValueExact() == 4, "模拟后余额变化按真实扣款拒绝");
        int before = account.writes;
        for (var invalid : List.of(List.of(-1L), List.of(Long.MAX_VALUE, -1L), List.of(Long.MIN_VALUE))) {
            try { Hk3GridEnergyPayment.input(invalid, () -> account.amount, account::change, false); throw new AssertionError("接受负耗电"); }
            catch (IllegalArgumentException expected) { checks++; }
            try { Hk3GridEnergyPayment.output(invalid, account::change, false); throw new AssertionError("接受负产电"); }
            catch (IllegalArgumentException expected) { checks++; }
        }
        check(account.writes == before, "非法数量必须在后端操作前拒绝");
        try {
            Hk3GridEnergyPayment.input(List.of(1L), () -> BigInteger.TEN, delta -> { throw new IllegalStateException("模拟后端异常"); }, false);
            throw new AssertionError("后端异常被伪装成成功");
        } catch (IllegalStateException expected) { checks++; }
    }
    private static void direct() {
        for (BigInteger amount : List.of(BigInteger.ZERO, BigInteger.TEN, MAX, MAX.add(BigInteger.ONE), BigInteger.TEN.pow(40))) {
            var account = new Account(amount);
            long changed = Hk3GridEnergyPayment.change(Long.MIN_VALUE, () -> account.amount, account::change);
            BigInteger expected = amount.min(MAX.add(BigInteger.ONE));
            check(BigInteger.valueOf(changed).equals(expected.negate()), "最小long请求精确负向返回");
            check(account.amount.equals(amount.subtract(expected)), "最小long请求余额守恒");
        }
        var a = new Account(BigInteger.valueOf(50));
        check(Hk3GridEnergyPayment.change(-200, () -> a.amount, a::change) == -50 && a.amount.signum() == 0, "余额不足直取按实际额度");
        check(Hk3GridEnergyPayment.change(Long.MAX_VALUE, () -> a.amount, a::change) == Long.MAX_VALUE, "直接大额充值");
        check(Hk3GridEnergyPayment.change(1, () -> a.amount, a::change) == 1 && a.amount.equals(MAX.add(BigInteger.ONE)), "累计充值越过long不溢出");
        int writes = a.writes;
        check(Hk3GridEnergyPayment.change(0, () -> { throw new AssertionError(); }, a::change) == 0 && a.writes == writes, "零改量无读写");
        check(Hk3GridEnergyPayment.visibleBalance(BigInteger.TEN.pow(50)) == Long.MAX_VALUE, "仅显示接口钳制long");
        check(Hk3GridEnergyPayment.visibleBalance(BigInteger.valueOf(-1)) == 0, "无负可用余额");
    }
    private static void simulation() {
        var a = new Account(BigInteger.valueOf(7));
        var demand = new ArrayList<Long>(Arrays.asList(0L, null, 5L, 10L));
        var before = new ArrayList<>(demand);
        var simulation = Hk3GridEnergyPayment.input(demand, () -> a.amount, a::change, true);
        check(simulation.transferred().intValueExact() == 7 && simulation.remaining().equals(List.of(8L)), "模拟按真实可用金额分摊");
        check(a.writes == 0 && a.amount.intValueExact() == 7 && demand.equals(before), "模拟不写账也不改传入列表");
        check(Hk3GridEnergyPayment.output(demand, a::change, true).remaining() == null && a.writes == 0, "发电模拟不写账");
        check(Hk3GridEnergyPayment.input(List.of(), () -> { throw new AssertionError(); }, a::change, false).remaining() == null, "空需求不读取账户");
        check(Hk3GridEnergyPayment.output(List.of(0L), delta -> { throw new AssertionError(); }, false).remaining() == null, "零发电不提交");
        var zero = Hk3GridEnergyPayment.input(List.of(8L), () -> BigInteger.valueOf(-10), a::change, false);
        check(zero.remaining().equals(List.of(8L)) && a.writes == 0, "负后端余额不当能源来源");
    }
    private static void generatedCases() {
        Random rng = new Random(138);
        for (int i = 0; i < 2000; i++) {
            var demand = new ArrayList<Long>();
            for (int j = 0, n = 1 + rng.nextInt(8); j < n; j++) demand.add(rng.nextLong() & Long.MAX_VALUE);
            var copy = new ArrayList<>(demand);
            BigInteger requested = sum(demand), initial = new BigInteger(68, rng);
            var a = new Account(initial); a.refuse = rng.nextBoolean(); boolean simulate = rng.nextBoolean();
            var result = Hk3GridEnergyPayment.input(demand, () -> a.amount, a::change, simulate);
            BigInteger expected = !simulate && a.refuse ? BigInteger.ZERO : initial.min(requested);
            check(result.transferred().equals(expected), "随机边界支付结果");
            check(sum(result.remaining()).add(result.transferred()).equals(requested), "随机边界原数=支付+剩余");
            check(a.amount.equals(simulate ? initial : initial.subtract(expected)), "随机边界账面守恒");
            check(demand.equals(copy) && a.writes <= 1 && (!simulate || a.writes == 0), "随机模拟/调用次数/输入不变");
        }
    }
    private static void productionContract() throws Exception {
        ClassNode node = new ClassNode();
        try (var stream = GridEnergyPaymentTest.class.getResourceAsStream("/com/sirin/hk3gtl/common/machine/trait/Hk3PlayerGridEnergyTrait.class")) {
            if (stream == null) throw new AssertionError("缺少生产适配class"); new ClassReader(stream).accept(node, 0);
        }
        var helpers = new HashSet<String>(); int precise = 0;
        for (var method : node.methods) for (var instruction : method.instructions) if (instruction instanceof MethodInsnNode call) {
            if (call.owner.endsWith("/Hk3GridEnergyPayment")) helpers.add(call.name);
            if (call.owner.endsWith("/WirelessEnergyManager") && call.name.equals("addEUToGlobalEnergyMap")) {
                check(call.desc.contains("Ljava/math/BigInteger;"), "生产写电网全部使用BigInteger入口"); precise++;
            }
        }
        check(helpers.containsAll(Set.of("input", "output", "change", "visibleBalance")), "所有生产路径已接精确适配");
        check(precise == 1, "消费、发电及直接改量共用一处可退款后端提交");
        check(node.methods.stream().noneMatch(m -> m.name.equals("saturatedSum")), "旧饱和少扣路径已移除");
        ClassNode multi = readNode("com/sirin/hk3gtl/common/machine/Hk3MultiRecipeLogic");
        check(multi.superName.equals("com/sirin/hk3gtl/common/machine/Hk3RecipeLogic"), "多配方包含tick提交检查");
        ClassNode machine = readNode("com/sirin/hk3gtl/common/machine/Hk3WorkableMultiblockMachine");
        var factory = machine.methods.stream().filter(m -> m.name.equals("createRecipeLogic")).findFirst().orElseThrow();
        boolean single = false;
        for (var insn : factory.instructions) if (insn instanceof TypeInsnNode type && type.getOpcode() == Opcodes.NEW
                && type.desc.equals("com/sirin/hk3gtl/common/machine/Hk3RecipeLogic")) single = true;
        check(single, "单配方工厂接到同一执行器");
        ClassNode gt = readNode("com/gregtechceu/gtceu/api/machine/trait/RecipeLogic");
        check(gt.methods.stream().anyMatch(m -> m.name.equals("handleTickRecipeIO") && m.desc.equals("(Lcom/gregtechceu/gtceu/api/recipe/GTRecipe;Lcom/gregtechceu/gtceu/api/capability/recipe/IO;)Z")), "当前GT实际IO虚方法签名契约");
        ClassNode custom = readNode("com/sirin/hk3gtl/common/machine/Hk3RecipeLogic");
        var guards = new HashSet<String>();
        for (var method : custom.methods) for (var insn : method.instructions) if (insn instanceof MethodInsnNode call) {
            if (call.owner.endsWith("/Hk3RecipeAccess") || call.owner.endsWith("/Hk3RecipeEnvironment")) guards.add(call.name);
        }
        check(guards.containsAll(Set.of("blocks", "throttlesByGaze")), "覆盖后保留现役研究与注视度守卫");
        check(!guards.contains("throttlesWithoutAnchor"), "退役虚数锚不再约束现役能源执行器");
    }
    private static ClassNode readNode(String name) throws Exception {
        try (var stream = GridEnergyPaymentTest.class.getResourceAsStream("/" + name + ".class")) {
            if (stream == null) throw new AssertionError(name);
            var node = new ClassNode(); new ClassReader(stream).accept(node, 0); return node;
        }
    }
    private static void tickCommit() {
        var calls = new ArrayList<String>();
        var failed = GTRecipe.ActionResult.fail(() -> net.minecraft.network.chat.Component.literal("测试缺电"));
        var result = Hk3RecipeLogic.commitTick(() -> failed,
                () -> { calls.add("input"); return true; }, () -> { calls.add("output"); return true; });
        check(result == failed && calls.isEmpty(), "模拟不通过保留原因且不执行实际IO");
        result = Hk3RecipeLogic.commitTick(() -> GTRecipe.ActionResult.SUCCESS,
                () -> { calls.add("input"); return false; }, () -> { calls.add("output"); return true; });
        check(!result.isSuccess() && calls.equals(List.of("input")), "输入提交失败不输出或报告推进成功");
        calls.clear();
        result = Hk3RecipeLogic.commitTick(() -> GTRecipe.ActionResult.SUCCESS,
                () -> { calls.add("input"); return true; }, () -> { calls.add("output"); return false; });
        check(!result.isSuccess() && calls.equals(List.of("input", "output")), "输出失败向推进器返回失败");
        calls.clear();
        result = Hk3RecipeLogic.commitTick(() -> GTRecipe.ActionResult.SUCCESS,
                () -> { calls.add("input"); return true; }, () -> { calls.add("output"); return true; });
        check(result.isSuccess() && calls.equals(List.of("input", "output")), "仅全部提交成功允许正常推进");
        var account = new Account(BigInteger.TEN); account.refuse = true; calls.clear();
        var demand = List.of(8L);
        result = Hk3RecipeLogic.commitTick(
                () -> Hk3GridEnergyPayment.input(demand, () -> account.amount, account::change, true).remaining() == null ? GTRecipe.ActionResult.SUCCESS : failed,
                () -> Hk3GridEnergyPayment.input(demand, () -> account.amount, account::change, false).remaining() == null,
                () -> { calls.add("output"); return true; });
        check(!result.isSuccess() && account.amount.equals(BigInteger.TEN) && calls.isEmpty(), "真实金额适配与推进器联测：后端拒付不输出");
        account.refuse = false;
        result = Hk3RecipeLogic.commitTick(() -> GTRecipe.ActionResult.SUCCESS,
                () -> Hk3GridEnergyPayment.input(demand, () -> account.amount, account::change, false).remaining() == null,
                () -> { calls.add("output"); return true; });
        check(result.isSuccess() && account.amount.intValueExact() == 2 && calls.size() == 1, "拒付后恢复正确支付并继续");
    }
}
