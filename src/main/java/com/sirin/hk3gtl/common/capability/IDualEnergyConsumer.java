package com.sirin.hk3gtl.common.capability;

import org.jetbrains.annotations.Nullable;

import java.math.BigInteger;
import java.util.UUID;

/**
 * 双能源消耗者接口 —— 机器在消耗 EU 之外，还从崩坏能无线网络并行扣除崩坏能。
 *
 * <h3>设计要点（审计项 D-01 实装）</h3>
 * <ul>
 *   <li>不引入任何"崩坏能输入仓"：崩坏能一律从 {@link HonkaiWirelessNetwork}
 *       按绑定玩家 UUID 直扣（与 EU 走 GTMThings 无线电网同一交互模型）</li>
 *   <li>每 tick 消耗量由 {@link Hk3DualEnergyCosts} 决定（配方级覆盖 &gt; 机器级默认）</li>
 *   <li>崩坏能不足时整 tick 暂停：EU 与进度均不消耗（见 RecipeLogicMixin）</li>
 * </ul>
 *
 * 【变更记录 #1】2026-07-19 19:16:14（第 1 次备注 · 内测四第 31 次更新）
 * - 删除：
 *   1) 删除双能源 tick 依赖 long 模拟抽取再实扣的两步结算方式。
 * - 新增：
 *   1) 新增 tryExtractHonkaiFromNetwork(BigInteger)，按绑定 UUID 执行全额或零扣除的原子结算。
 * - 修改：
 *   1) 保留 long 注入接口服务现有注入器，余额后端由 HonkaiWirelessNetwork 统一升级为 BigInteger。
 * - 用途：
 *   1) 隔离 RecipeLogicMixin 与无线网络实现，使合并配方任意精度成本可安全结算。
 */
public interface IDualEnergyConsumer {

    /** 双能源结算归属的玩家 UUID；null = 未绑定（视为崩坏能不足，机器暂停） */
    @Nullable
    UUID getDualEnergyOwner();

    /**
     * 从绑定玩家的崩坏能无线网络扣除崩坏能。
     *
     * @param amount   请求量（崩坏能单位）
     * @param simulate true 仅模拟不落账
     * @return 实际（可）扣除量
     */
    default long extractHonkaiFromNetwork(long amount, boolean simulate) {
        UUID owner = getDualEnergyOwner();
        if (owner == null) return 0L;
        return HonkaiWirelessNetwork.extract(owner, amount, simulate);
    }

    /** 全额或零扣除，用于每 tick 双能源结算。 */
    default boolean tryExtractHonkaiFromNetwork(BigInteger amount) {
        UUID owner = getDualEnergyOwner();
        return owner != null && HonkaiWirelessNetwork.tryExtractExact(owner, amount);
    }

    /** 向绑定玩家的崩坏能无线网络注入崩坏能（发电/注入类机器用） */
    default long insertHonkaiToNetwork(long amount, boolean simulate) {
        UUID owner = getDualEnergyOwner();
        if (owner == null) return 0L;
        return HonkaiWirelessNetwork.insert(owner, amount, simulate);
    }
}
