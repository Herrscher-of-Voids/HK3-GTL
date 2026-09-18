package com.sirin.hk3gtl.common.machine.energy;

import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.sirin.hk3gtl.common.capability.HonkaiWirelessNetwork;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import com.sirin.hk3gtl.common.util.Hk3HonkaiEnergyFormatter;

import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 崩坏能网络注入器（{@code honkai_network_injector}）—— 双能源引擎的"充网"入口。
 *
 * <h3>定位（审计项 D-01 配套）</h3>
 * 双能源机器的崩坏能一律从无线网络直扣、没有输入仓，因此需要一台把
 * 液态崩坏能 / 崩坏能结晶 / EU 变成网络余额的机器。三条路线用编程电路区分：
 * <ol>
 *   <li>meta=1：液态崩坏能 → 网络（1 mB = 1 崩坏能）</li>
 *   <li>meta=2：崩坏能结晶 → 网络（1 结晶 = 100 崩坏能，便捷高价路线）</li>
 *   <li>meta=3：纯 EU → 网络（1000 EU = 1 崩坏能，与全模组换算比一致）</li>
 * </ol>
 * 大型崩坏能反应堆 / 崩坏能-EU 转换器仍可作为 EU 侧的替代来源。
 *
 * <h3>实现方式</h3>
 * 走标准 GT 配方（JEI 可见、仓室/超频/研究门控全兼容），产出"崩坏能"不是物品而是
 * 网络余额：配方无物品产出，完成时 {@link #afterWorking()} 按 {@link #YIELDS}
 * 登记的产额注入绑定玩家的 {@link HonkaiWirelessNetwork}。
 * 无线池使用 BigInteger 无限容量，完成产额可直接全量写入，不再需要剩余容量预检。
 *
 * 【变更记录 #1】2026-07-19 19:16:14（第 1 次备注 · 内测四第 31 次更新）
 * - 删除：
 *   1) 删除固定容量预检、池满等待和完成时溢出丢弃分支；无线网络现为 BigInteger 无限容量。
 * - 新增：
 *   1) 新增紧凑余额显示，并明确容量文本为无限。
 * - 修改：
 *   1) 配方完成时产额仍使用 long 登记，但注入后端立即转为 BigInteger，无累计上限。
 * - 用途：
 *   1) 让注入器持续积累超 64 位余额，并在有限 GUI 空间保持可读。
 */
public class Hk3HonkaiNetworkInjectorMachine extends Hk3WorkableMultiblockMachine {

    private static final Logger LOGGER = LogUtils.getLogger();

    /** 配方ID → 完成时注入网络的崩坏能产额 */
    private static final Map<ResourceLocation, Long> YIELDS = new ConcurrentHashMap<>();

    public Hk3HonkaiNetworkInjectorMachine(IMachineBlockEntity holder) {
        super(holder);
    }

    /** 配方注册侧登记产额（同时登记 gtceu:/hk3gtl: 两个命名空间，与研究门控 bind 同约定） */
    public static void bindYield(String recipeType, String recipeId, long honkaiYield) {
        if (honkaiYield <= 0) return;
        YIELDS.put(new ResourceLocation("gtceu", recipeType + "/" + recipeId), honkaiYield);
        YIELDS.put(new ResourceLocation("hk3gtl", recipeType + "/" + recipeId), honkaiYield);
    }

    private static long yieldOf(GTRecipe recipe) {
        if (recipe == null || recipe.id == null) return 0L;
        Long y = YIELDS.get(recipe.id);
        return y == null ? 0L : y;
    }

    /**
     * 注入产额按"配方原始 ID"结算，与并行/合并逻辑语义不匹配，
     * 因此本机固定走原版单配方逻辑。
     */
    @Override
    protected boolean enableMultiRecipe() {
        return false;
    }

    /**
     * 开工前预检：未绑定玩家或网络剩余容量吃不下本配方产额时拒绝开工（机器等待）。
     * 避免跑完配方后能量无处可去被丢弃。
     */
    @Override
    public boolean beforeWorking(GTRecipe recipe) {
        return super.beforeWorking(recipe);
    }

    /** 配方完成：把产额注入绑定玩家的崩坏能无线网络 */
    @Override
    public void afterWorking() {
        super.afterWorking();
        try {
            GTRecipe last = getRecipeLogic().getLastRecipe();
            long yield = yieldOf(last);
            if (yield <= 0) return;
            insertHonkaiToNetwork(yield, false);
        } catch (Exception e) {
            LOGGER.warn("[HK3GTL] 崩坏能网络注入失败", e);
        }
    }

    /** GUI 追加当前网络余额行 */
    @Override
    public void addDisplayText(List<Component> textList) {
        super.addDisplayText(textList);
        try {
            var owner = getDualEnergyOwner();
            if (owner != null) {
                textList.add(Component.translatable("hk3gtl.machine.honkai_injector.balance",
                        Hk3HonkaiEnergyFormatter.formatCompact(HonkaiWirelessNetwork.getStoredAmount(owner)),
                        HonkaiWirelessNetwork.UNLIMITED_CAPACITY_TEXT)
                        .withStyle(net.minecraft.ChatFormatting.LIGHT_PURPLE));
            }
        } catch (Throwable ignored) {
        }
    }
}
