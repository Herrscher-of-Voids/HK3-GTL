package com.sirin.hk3gtl.test.persistence;

import com.sirin.hk3gtl.common.capability.Hk3EnergyTick;
import com.sirin.hk3gtl.common.capability.Hk3GridEnergyPayment;
import com.sirin.hk3gtl.common.recipe.power.Hk3PowerBudget;
import com.sirin.hk3gtl.common.recipe.power.Hk3PortPayment;
import com.sirin.hk3gtl.common.recipe.power.Hk3PowerPlanner;
import org.objectweb.asm.ClassReader;
import org.objectweb.asm.tree.ClassNode;
import org.objectweb.asm.tree.MethodInsnNode;

import java.math.BigInteger;
import java.util.List;
import java.util.Objects;

/**
 * 【变更记录 #1】2026-10-17 16:29:01（第1次备注 · 修订165）
 * 删除：无；新增：CEV边界、多仓功率与额定分离、精确金额、模拟、拒付、退款及生产接线验证。
 * 修改：算术与真实生产支付/票据共用，不启动游戏；用途：禁止把纯逻辑通过当作第三方高阶设备可运行。
 */
/**
 * 【变更记录 #2】2026-10-17 16:47:08（第2次备注 · 修订165）
 * 删除：单路额定被当成用户限制的断言；新增：GTL总功率、多仓拒付和部分退款重试反例。
 * 修改：独立算术模式与完整生产接线分开输出；用途：静态验证不冒充目标实例运行验收。
 */
/**
 * 【变更记录 #3】2026-10-17 17:58:50（第3次备注 · 修订165）
 * 删除：无；新增：继承规划器正例、替换选方/完工入口及自建规划器负例和生产接线断言。
 * 修改：未知GTLAdd规划器不能因继承标准工作循环而被误接受；用途：防止吃料后丢失data及原始费用。
 */
/**
 * 【变更记录 #4】2026-11-04 22:10:32（第4次备注 · 内测5修订201）
 * 删除：无；新增：超额扣款、反向加款及其失败后精确撤销反例。
 * 修改：隔离端口夹具可注入一次非法实际改量；用途：验证生产支付内核不遗失已知余额变更，不冒充真实仓验收。
 */
/**
 * 【变更记录 #5】2026-11-04 22:14:54（第5次备注 · 内测5修订201）
 * 删除：无；新增：反向部分退款及异常回执下保留带符号余量的回归。
 * 修改：退款阶段分别注入正/负欠额的符号翻转；用途：防止重试重复抵消余额改量，仍不宣称真实仓验收。
 */
public final class RecipePowerTest {
    private static final long MAX_VOLTAGE = 2_147_483_648L;
    private static final long HBV_COST = 8_053_063_680L;
    private static final long HCV_COST = 32_212_254_720L;
    private static final BigInteger LONG_MAX = BigInteger.valueOf(Long.MAX_VALUE);
    private static int checks;

    private static void check(boolean accepted, String reason) {
        checks++;
        if (!accepted) throw new AssertionError(reason);
    }

    private static void reject(Runnable action) {
        try { action.run(); throw new AssertionError("非法能源输入被接受"); }
        catch (IllegalArgumentException | IllegalStateException expected) { checks++; }
    }

    public static void main(String[] arguments) throws Exception {
        ratings(); amounts(); payment(); ports(); planners();
        boolean isolated = List.of(arguments).contains("--arithmetic-only");
        if (!isolated) wiring();
        System.out.println("高阶配方能源：" + checks + "项算术、支付票据" + (isolated ? "检查通过；生产接线未运行" : "和生产接线检查通过") + "；指定实例运行未验收");
    }

    private static void ratings() {
        var maxHatches = Hk3PowerBudget.rating(List.of(new Hk3PowerBudget.Input(MAX_VOLTAGE, 64),
                new Hk3PowerBudget.Input(MAX_VOLTAGE, 64)));
        check(maxHatches.totalPower().equals(BigInteger.valueOf(MAX_VOLTAGE).multiply(BigInteger.valueOf(128))), "两仓功率精确汇总");
        check(Hk3PowerBudget.sufficientRating(maxHatches, HBV_COST, BigInteger.valueOf(HBV_COST)), "继承GTL多仓总输入功率，达到HBV工况需求");
        var hbvHatches = Hk3PowerBudget.rating(List.of(new Hk3PowerBudget.Input(HBV_COST, 1),
                new Hk3PowerBudget.Input(HBV_COST, 1)));
        check(Hk3PowerBudget.sufficientRating(hbvHatches, HBV_COST, BigInteger.valueOf(HBV_COST).multiply(BigInteger.TWO)), "理论同级两仓可覆盖两条同级费用");
        check(!Hk3PowerBudget.sufficientRating(hbvHatches, HCV_COST, BigInteger.valueOf(HBV_COST)), "费用不能低于声明需求功率阶段");
        check(!Hk3PowerBudget.sufficientRating(hbvHatches, HBV_COST, hbvHatches.totalPower().add(BigInteger.ONE)), "额定电压够但总功率不足拒绝");
        var cev = Hk3PowerBudget.rating(List.of(new Hk3PowerBudget.Input(Long.MAX_VALUE, Long.MAX_VALUE),
                new Hk3PowerBudget.Input(Long.MAX_VALUE, 1)));
        check(cev.totalPower().equals(LONG_MAX.multiply(LONG_MAX).add(LONG_MAX)), "CEV多仓乘加越过long仍精确");
        check(Hk3PowerBudget.sufficientRating(cev, Long.MAX_VALUE, LONG_MAX), "理论CEV额定边界不取反或溢出");
        var existingLaser = Hk3PowerBudget.rating(List.of(new Hk3PowerBudget.Input(MAX_VOLTAGE, Integer.MAX_VALUE)));
        check(existingLaser.totalPower().equals(new BigInteger("4611686016279904256")), "实际MAX极高安培激光额定功率复算");
        check(!Hk3PowerBudget.sufficientRating(existingLaser, Long.MAX_VALUE, LONG_MAX), "单台现有MAX激光仓不足CEV且不能升压");
        var zero = Hk3PowerBudget.rating(List.of(new Hk3PowerBudget.Input(Long.MAX_VALUE, 0)));
        check(zero.highestVoltage() == 0 && zero.totalPower().signum() == 0, "零安培不能贡献假额定");
        reject(() -> new Hk3PowerBudget.Input(-1, 1));
        reject(() -> new Hk3PowerBudget.Input(1, -1));
    }

    private static void amounts() {
        check(Hk3PowerBudget.cost(List.of(Long.MAX_VALUE)).equals(LONG_MAX), "CEV单条实际费用完整");
        check(Hk3PowerBudget.cost(List.of(Long.MAX_VALUE, Long.MAX_VALUE, 17L))
                .equals(LONG_MAX.multiply(BigInteger.TWO).add(BigInteger.valueOf(17))), "合并费用没有long饱和");
        reject(() -> Hk3PowerBudget.cost(List.of()));
        reject(() -> Hk3PowerBudget.cost(List.of(0L)));
        reject(() -> Hk3PowerBudget.cost(List.of(-1L)));
    }

    private static final class Account {
        BigInteger balance;
        int writes;
        boolean refuse;
        Account(BigInteger amount) { balance = amount; }
        boolean change(BigInteger delta, Hk3EnergyTick tick) {
            writes++;
            if (refuse || balance.add(delta).signum() < 0) return false;
            balance = balance.add(delta);
            tick.undoWith(() -> balance = balance.subtract(delta));
            return true;
        }
    }

    private static void payment() {
        List<Long> demand = List.of(Long.MAX_VALUE, Long.MAX_VALUE, 17L);
        BigInteger cost = Hk3PowerBudget.cost(demand);
        var simulated = new Account(cost); var unused = new Hk3EnergyTick();
        var estimate = Hk3GridEnergyPayment.input(demand, () -> simulated.balance,
                delta -> simulated.change(delta, unused), true);
        check(estimate.remaining() == null && simulated.writes == 0 && simulated.balance.equals(cost), "模拟足额不写余额");

        var declined = new Account(cost); declined.refuse = true; var rejected = new Hk3EnergyTick();
        var failure = Hk3GridEnergyPayment.input(demand, () -> declined.balance,
                delta -> declined.change(delta, rejected), false);
        check(failure.remaining().equals(demand) && failure.transferred().signum() == 0, "后端拒绝不能返回已支付");
        check(rejected.finish(false) && declined.balance.equals(cost), "失败不扣款");

        var insufficient = new Account(LONG_MAX); var partial = new Hk3EnergyTick();
        var remainder = Hk3GridEnergyPayment.input(demand, () -> insufficient.balance,
                delta -> insufficient.change(delta, partial), false);
        check(remainder.remaining() != null && !remainder.remaining().isEmpty(), "输入不足不能完成消费");
        check(partial.finish(false) && insufficient.balance.equals(LONG_MAX), "实际只付部分后工作失败精确退回");

        var ioFailure = new Account(cost); var failedWork = new Hk3EnergyTick();
        check(Hk3GridEnergyPayment.input(demand, () -> ioFailure.balance,
                delta -> ioFailure.change(delta, failedWork), false).remaining() == null, "先精确预留全部费用");
        check(failedWork.finish(false) && ioFailure.balance.equals(cost), "后续IO或推进失败全额退款");

        var completed = new Account(cost.add(BigInteger.valueOf(5))); var successful = new Hk3EnergyTick();
        check(Hk3GridEnergyPayment.input(demand, () -> completed.balance,
                delta -> completed.change(delta, successful), false).remaining() == null, "成功完整付款");
        check(successful.finish(true) && completed.balance.equals(BigInteger.valueOf(5)) && completed.writes == 1, "成功只扣一次完整总额");
        check(successful.finish(false) && completed.balance.equals(BigInteger.valueOf(5)), "成功封账后不能退款复制电能");
    }

    private static ClassNode node(String relative) throws Exception {
        try (var stream = RecipePowerTest.class.getResourceAsStream("/com/sirin/hk3gtl/" + relative + ".class")) {
            var result = new ClassNode();
            new ClassReader(Objects.requireNonNull(stream)).accept(result, 0);
            return result;
        }
    }

    private static final class Buffer implements Hk3PortPayment.Port {
        BigInteger stored;
        final BigInteger limit;
        boolean refuse;
        boolean partialRefund;
        boolean failAfterDebit;
        boolean failNextChange;
        BigInteger nextChange;
        int writes;
        Buffer(long stored, long power) { this.stored = BigInteger.valueOf(stored); limit = BigInteger.valueOf(power); }
        @Override public BigInteger available() { return stored; }
        @Override public BigInteger power() { return limit; }
        @Override public BigInteger change(BigInteger delta) {
            writes++;
            if (refuse && delta.signum() < 0) return BigInteger.ZERO;
            BigInteger actual = delta.signum() < 0 ? delta.negate().min(stored).negate() : delta;
            if (nextChange != null) { actual = nextChange; nextChange = null; }
            if (partialRefund) {
                actual = delta.signum() < 0 ? delta.max(BigInteger.ONE.negate()) : delta.min(BigInteger.ONE);
                partialRefund = false;
            }
            stored = stored.add(actual);
            if (failNextChange) {
                failNextChange = false;
                throw new Hk3PortPayment.ChangeFailure(actual, new IllegalStateException("模拟改量后异常"));
            }
            if (actual.signum() < 0 && failAfterDebit)
                throw new Hk3PortPayment.ChangeFailure(actual, new IllegalStateException("模拟余额已改后监听器失败"));
            return actual;
        }
    }

    private static void ports() {
        Buffer first = new Buffer(Long.MAX_VALUE, Long.MAX_VALUE), second = new Buffer(Long.MAX_VALUE, Long.MAX_VALUE);
        List<Hk3PortPayment.Port> ports = List.of(first, second);
        BigInteger cost = LONG_MAX.add(BigInteger.valueOf(17));
        Hk3EnergyTick success = new Hk3EnergyTick();
        check(Hk3PortPayment.pay(ports, cost, success), "多仓总费用超long仍足额分摊");
        check(success.finish(true) && first.stored.signum() == 0 && second.stored.equals(LONG_MAX.subtract(BigInteger.valueOf(17))), "成功付款总额无饱和");

        first = new Buffer(9, 20); second = new Buffer(9, 20); second.refuse = true;
        ports = List.of(first, second); var rejected = new Hk3EnergyTick();
        check(!Hk3PortPayment.pay(ports, BigInteger.valueOf(12), rejected), "第二仓拒付不能报告成功");
        check(rejected.finish(false) && first.stored.equals(BigInteger.valueOf(9)) && second.stored.equals(BigInteger.valueOf(9)), "多仓中途失败退还已扣第一仓");

        var small = new Buffer(2, 100); var insufficient = new Hk3EnergyTick();
        check(!Hk3PortPayment.pay(List.of(small), BigInteger.valueOf(3), insufficient) && small.writes == 0, "单仓余额不足预检失败不扣款");
        var lowPower = new Buffer(100, 2);
        check(!Hk3PortPayment.pay(List.of(lowPower), BigInteger.valueOf(3), new Hk3EnergyTick()) && lowPower.writes == 0, "输入功率不足预检不扣款");
        var retry = new Buffer(10, 20); var pending = new Hk3EnergyTick();
        check(Hk3PortPayment.pay(List.of(retry), BigInteger.valueOf(7), pending), "工作前正确预留");
        retry.partialRefund = true;
        check(!pending.finish(false) && retry.stored.equals(BigInteger.valueOf(4)), "部分退款保留真实余量");
        check(pending.finish(false) && retry.stored.equals(BigInteger.TEN), "重试只退剩余六EU，不复制第一EU");
        var callbackFailure = new Buffer(10, 20); callbackFailure.failAfterDebit = true; var failed = new Hk3EnergyTick();
        check(!Hk3PortPayment.pay(List.of(callbackFailure), BigInteger.valueOf(7), failed), "余额已改但监听器抛错不继续推进");
        check(failed.finish(false) && callbackFailure.stored.equals(BigInteger.TEN), "余额已改后抛错仍按真实改量退款");
        for (long wrong : new long[]{-12, 7}) {
            var invalid = new Buffer(20, 20); invalid.nextChange = BigInteger.valueOf(wrong);
            var invalidTick = new Hk3EnergyTick();
            reject(() -> Hk3PortPayment.pay(List.of(invalid), BigInteger.valueOf(7), invalidTick));
            check(invalid.stored.equals(BigInteger.valueOf(20 + wrong)), "端口已发生非法实际改量");
            invalid.partialRefund = true;
            check(!invalidTick.finish(false) && invalid.stored.equals(BigInteger.valueOf(20 + wrong - Long.signum(wrong))),
                    "带符号部分撤销保留剩余改量并暂停工作");
            check(invalidTick.finish(false) && invalid.stored.equals(BigInteger.valueOf(20)), "超额扣款或反向加款均按完整真实差量撤销");
            check(invalidTick.finish(false) && invalid.stored.equals(BigInteger.valueOf(20)), "非法改量撤销只执行一次");
        }
        for (long owed : new long[]{7, -7}) for (long refund : new long[]{12 * Long.signum(owed), -2 * Long.signum(owed)})
                for (boolean throwsAfterRefund : new boolean[]{false, true}) {
            var invalid = new Buffer(20, 20);
            var invalidTick = new Hk3EnergyTick();
            if (owed < 0) {
                invalid.nextChange = BigInteger.valueOf(-owed);
                reject(() -> Hk3PortPayment.pay(List.of(invalid), BigInteger.valueOf(7), invalidTick));
            } else check(Hk3PortPayment.pay(List.of(invalid), BigInteger.valueOf(owed), invalidTick), "退款前已按批准费用付款");
            BigInteger afterDebit = invalid.stored;
            invalid.nextChange = BigInteger.valueOf(refund);
            invalid.failNextChange = throwsAfterRefund;
            check(!invalidTick.finish(false) && invalid.stored.equals(afterDebit.add(BigInteger.valueOf(refund))),
                    "退款符号翻转先记录真实改量并暂停重试");
            check(invalidTick.finish(false) && invalid.stored.equals(BigInteger.valueOf(20)), "带符号退款余量重试后余额精确恢复");
            check(invalidTick.finish(false) && invalid.stored.equals(BigInteger.valueOf(20)), "反向退款恢复后幂等封账");
        }
    }

    public static class KnownPlanner {
        public void findAndHandleRecipe() {}
        public void onRecipeFinish() {}
    }
    public static final class InheritedPlanner extends KnownPlanner {}
    public static final class ReplacedPlanner extends KnownPlanner {
        @Override public void findAndHandleRecipe() {}
        @Override public void onRecipeFinish() {}
    }
    public static final class CovertPlanner extends KnownPlanner {
        public Object getGTRecipe() { return null; }
    }

    private static void planners() {
        check(Hk3PowerPlanner.inherits(InheritedPlanner.class, KnownPlanner.class,
                "findAndHandleRecipe", "onRecipeFinish"), "继承已适配规划器的载体仍可用");
        check(!Hk3PowerPlanner.inherits(ReplacedPlanner.class, KnownPlanner.class,
                "findAndHandleRecipe", "onRecipeFinish"), "另建选方及完工入口的规划器拒绝");
        check(!Hk3PowerPlanner.inherits(CovertPlanner.class, KnownPlanner.class,
                "findAndHandleRecipe", "onRecipeFinish"), "另建getGTRecipe的隐蔽规划器拒绝");
    }

    private static boolean calls(ClassNode type, String owner, String name) {
        for (var method : type.methods) for (var instruction : method.instructions)
            if (instruction instanceof MethodInsnNode call && call.owner.endsWith(owner) && call.name.equals(name)) return true;
        return false;
    }

    private static void wiring() throws Exception {
        check(calls(node("mixin/EnhancedRecipeConditionsMixin"), "/Hk3RecipePower", "check"), "真实配方条件入口有守卫");
        check(calls(node("mixin/EnhancedRecipeTickMixin"), "/Hk3RecipePower", "check"), "增强版tick再次校验");
        var logic = node("common/machine/Hk3RecipeLogic");
        check(calls(logic, "/Hk3RecipePower", "check") && calls(logic, "/Hk3RecipePower", "pay"), "HK真实推进先复检再付款");
        check(calls(logic, "/Hk3RecipePower", "withoutEU"), "其余tick副本移除EU防止双扣");
        check(calls(logic, "/Hk3EnergyTick", "runWork"), "实际付款保留失败退款票据");
        var helper = node("common/machine/Hk3RecipeCalculationHelper");
        check(calls(helper, "/Hk3RecipePower", "scale") && calls(helper, "/Hk3RecipePower", "merge"), "倍乘合并保留最高额定和完整费用");
        check(calls(node("mixin/GTRecipeWidgetMixin"), "/Hk3RecipePower", "tooltip"), "JEI同源显示真实额定");
        var guard = node("common/recipe/power/Hk3RecipePower");
        check(calls(guard, "/Hk3PowerPlanner", "inherits"), "生产守卫检查真实规划入口而非仅工作循环");
        check(calls(guard, "/Hk3PlayerGridEnergyTrait", "handleRecipeInner"), "复用真实玩家网事务支付");
        check(!calls(guard, "/WirelessEnergyManager", "addEUToGlobalEnergyMap"), "不另开无退款后端扣款路径");
        check(calls(node("mixin/Hk3PowerLogicMixin"), "/Hk3RecipePower", "pay"), "标准GTL工作循环接入精确支付");
        check(calls(node("mixin/Hk3PowerLogicMixin"), "/Hk3EnergyTick", "runWork"), "标准GTL工作失败有退款作用域");
        check(calls(node("mixin/gtlcore/Hk3PowerBatchMixin"), "/Hk3RecipePower", "marked"), "原GTL批次器分流HK工况");
        check(calls(node("common/recipe/power/Hk3PowerPorts$Buffer"), "/IEnergyContainer", "changeEnergy"), "精确支付实际修改原有能源仓");
    }
}
