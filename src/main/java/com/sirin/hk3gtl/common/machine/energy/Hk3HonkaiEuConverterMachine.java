package com.sirin.hk3gtl.common.machine.energy;



import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;

import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

import java.util.Collections;
import java.util.Set;
import java.util.WeakHashMap;

/**
 * 崩坏能 ↔ GT 原生 EU 双向转换矩阵（{@code honkai_eu_converter} 多方块的专用机器类）。
 *
 * <h3>工作原理</h3>
 * <ol>
 *   <li>结构里放置 <b>崩坏能输入仓</b> + <b>GT 能源输入仓</b> 时：
 *       从崩坏能仓抽 N 崩坏能 → 按 {@link Hk3Constants#HONKAI_TO_EU_RATIO 1:1000} 转为 N×1000 EU → 注入 GT 能源容器</li>
 *   <li>结构里放置 <b>崩坏能输出仓</b> 且 GT 能源容器有电时：
 *       从 GT 能源容器抽 N×1000 EU → 转为 N 崩坏能 → 注入崩坏能仓</li>
 *   <li>两个方向由"哪边仓有空"自动决定；都能双向时优先崩坏能 → EU（下游机器更需要）</li>
 * </ol>
 *
 * <h3>转换损耗</h3>
 * 本轮为 1:1000 无损，便于玩家理解与测试。后续可在 {@link #CONVERSION_LOSS_PERCENT} 引入损耗
 * （例如 10% = 0.9 倍系数）。
 *
 * <h3>每 tick 传输带宽</h3>
 * {@link #TRANSFER_RATE_PER_TICK} 限制每 tick 最多转换量，避免单 tick 灌爆仓室。
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>改比率：{@link Hk3Constants#HONKAI_TO_EU_RATIO}（会影响全模组崩坏能-EU 换算）</li>
 *   <li>改损耗：调整 {@link #CONVERSION_LOSS_PERCENT}（0 = 无损；10 = 扣 10%）</li>
 *   <li>改带宽：{@link #TRANSFER_RATE_PER_TICK}</li>
 *   <li>加方向偏好开关（玩家选）：在机器 NBT 里存 direction 字段，改 {@link #tickConvert} 逻辑</li>
 * </ul>
 */
@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public class Hk3HonkaiEuConverterMachine extends Hk3WorkableMultiblockMachine {

    private static final Logger LOGGER = LogUtils.getLogger();

    /** 无损：0；有损示例 10%：把 1000 → 900 */
    private static final int CONVERSION_LOSS_PERCENT = 0;

    /** 单 tick 最多转换的崩坏能单位（对应 EU = × 1000） */
    private static final long TRANSFER_RATE_PER_TICK = 100_000L;

    /** 活跃转换机实例集合，由 {@link #onServerTick} 统一调度 */
    private static final Set<Hk3HonkaiEuConverterMachine> INSTANCES =
            Collections.synchronizedSet(Collections.newSetFromMap(new WeakHashMap<>()));

    public Hk3HonkaiEuConverterMachine(IMachineBlockEntity holder) {
        super(holder);
        INSTANCES.add(this);
    }

    /**
     * 崩坏能↔EU 转换由 onServerTick 驱动、不跑标准配方，
     * 必须排除“多配方同时运行”，避免误挂配方逻辑干扰能量转换。
     */
    @Override
    protected boolean enableMultiRecipe() {
        return false;
    }

    @SubscribeEvent
    public static void onServerTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        synchronized (INSTANCES) {
            for (Hk3HonkaiEuConverterMachine m : INSTANCES) {
                try {
                    if (m != null) m.tickConvert();
                } catch (Throwable t) {
                    LOGGER.error("[HK3GTL] 双转换矩阵 tick 异常", t);
                }
            }
        }
    }

    /**
     * 每 tick 的双向转换决策。
     *
     * <p>流程（优先"崩坏能 → EU"，因为下游 GT 机器更常缺 EU）：</p>
     * <ol>
     *   <li>检查崩坏能仓的可抽出量 {@code hkSim = consumeHonkai(RATE, simulate=true)}</li>
     *   <li>检查 GT 能源容器的可注入量 {@code euFreeSim = fillGtEnergy(hkSim × RATIO, simulate=true)}</li>
     *   <li>实际转换量 = min(hkSim, euFreeSim / RATIO)；真正 consume/fill 一次</li>
     *   <li>若无法做崩坏能 → EU，检查反向</li>
     * </ol>
     */
    public void tickConvert() {
        if (!(getHolder() instanceof BlockEntity be) || be.getLevel() == null) return;
        if (be.getLevel().isClientSide()) return;
        if (getHonkaiHatches().isEmpty()) return;

        long ratio = Hk3Constants.HONKAI_TO_EU_RATIO;
        long lossDiv = 100L;
        long lossMul = 100L - CONVERSION_LOSS_PERCENT;

        // 方向 1：崩坏能 → EU
        long hkSim = consumeHonkai(TRANSFER_RATE_PER_TICK, true);
        if (hkSim > 0) {
            long wouldProduce = applyLoss(hkSim * ratio, lossMul, lossDiv);
            long euFilled = fillGtEnergy(wouldProduce, true);
            long possibleHk = euFilled / ratio; // EU 仓只能吃这么多对应回去的 HK
            long actualHk = Math.min(hkSim, possibleHk);
            if (actualHk > 0) {
                long actualEu = applyLoss(actualHk * ratio, lossMul, lossDiv);
                long usedHk = consumeHonkai(actualHk, false);
                fillGtEnergy(usedHk * ratio * lossMul / lossDiv, false);
                return;
            }
        }

        // 方向 2：EU → 崩坏能（反向）
        long hkFreeSim = fillHonkai(TRANSFER_RATE_PER_TICK, true);
        if (hkFreeSim > 0) {
            long euNeeded = hkFreeSim * ratio;
            long euAvailable = consumeGtEnergy(euNeeded, true);
            long resultHk = applyLoss(euAvailable / ratio, lossMul, lossDiv);
            if (resultHk > 0) {
                long usedEu = resultHk * ratio * lossDiv / lossMul; // 反算真实扣除量
                consumeGtEnergy(usedEu, false);
                fillHonkai(resultHk, false);
            }
        }
    }

    private long fillGtEnergy(long amount, boolean simulate) {
        if (amount <= 0) return 0;
        try {
            Object container = this.getClass().getMethod("getEnergyContainer").invoke(this);
            if (container == null) return 0;
            long stored = ((Number) container.getClass().getMethod("getEnergyStored").invoke(container)).longValue();
            long cap = ((Number) container.getClass().getMethod("getEnergyCapacity").invoke(container)).longValue();
            long accepted = Math.min(amount, Math.max(0, cap - stored));
            if (accepted > 0 && !simulate) {
                try {
                    container.getClass().getMethod("changeEnergy", long.class).invoke(container, accepted);
                } catch (NoSuchMethodException e) {
                    container.getClass().getMethod("addEnergy", long.class).invoke(container, accepted);
                }
            }
            return accepted;
        } catch (ReflectiveOperationException | RuntimeException e) {
            return 0;
        }
    }

    private long consumeGtEnergy(long amount, boolean simulate) {
        if (amount <= 0) return 0;
        try {
            Object container = this.getClass().getMethod("getEnergyContainer").invoke(this);
            if (container == null) return 0;
            long stored = ((Number) container.getClass().getMethod("getEnergyStored").invoke(container)).longValue();
            long extracted = Math.min(amount, Math.max(0, stored));
            if (extracted > 0 && !simulate) {
                container.getClass().getMethod("removeEnergy", long.class).invoke(container, extracted);
            }
            return extracted;
        } catch (ReflectiveOperationException | RuntimeException e) {
            return 0;
        }
    }

    /** 应用有损转换系数；loss=0 时等于恒等 */
    private static long applyLoss(long value, long mul, long div) {
        if (mul == div) return value;
        return value * mul / div;
    }
}
