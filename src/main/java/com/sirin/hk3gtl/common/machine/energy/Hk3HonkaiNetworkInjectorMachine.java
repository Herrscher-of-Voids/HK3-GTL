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









































public class Hk3HonkaiNetworkInjectorMachine extends com.sirin.hk3gtl.common.machine.research.Hk3LiquidProcessMachine {

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
     * 允许跨配方并行；父类把各原配方的产额乘实际并行数后汇总到运行批次。
     */
    @Override
    protected boolean enableMultiRecipe() {
        return true;
    }

    /**
     * 开工前检查在线归属、首封信资料及研究权限；无线网络使用无限容量。
     */
    /** 只有已成功完成一次输出结算的批次才记账；归属已在开工、运行和结算前验证。 */
    @Override
    protected void onRequiredProcessOutput(GTRecipe recipe) {
        java.math.BigInteger credit = recipe.data.contains(CREDIT,8)
                ? new java.math.BigInteger(recipe.data.getString(CREDIT))
                : java.math.BigInteger.valueOf(recipe.data.getLong(CREDIT));
        if (credit.signum() <= 0 || getOwnerUUID() == null)
            throw new IllegalStateException("注入批次缺少有效归属或产额");
        HonkaiWirelessNetwork.insert(getOwnerUUID(), credit, false);
    }

    /** GUI 追加当前网络余额行 */
    @Override
    public void addDisplayText(List<Component> textList) {
        super.addDisplayText(textList);
        var owner = getDualEnergyOwner();
        if (owner != null) {
            textList.add(Component.translatable("hk3gtl.machine.honkai_injector.balance",
                    Hk3HonkaiEnergyFormatter.formatCompact(HonkaiWirelessNetwork.getStoredAmount(owner)),
                    HonkaiWirelessNetwork.UNLIMITED_CAPACITY_TEXT)
                    .withStyle(net.minecraft.ChatFormatting.LIGHT_PURPLE));
        }
    }
}
