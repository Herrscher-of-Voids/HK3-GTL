package com.sirin.hk3gtl.common.machine.multiblock.part;


/**
 * 【文件职责】
 * - 定义 HonkaiEnergyHatchPartMachine 机器行为与结构逻辑。
 * - 关键调用链：由上层系统入口调用 -> 本文件核心方法 -> 下游模块。
 *
 * 【变更记录】2026-05-19
 * - 删除：
 *   1) 初始归档备注：自 v0.3 基线梳理，无本次 diff。
 * - 新增：
 *   1) 新增统一变更备注块，便于后续维护与审计追踪。
 * - 修改：
 *   1) 未改动业务逻辑，仅补充文件级职责与维护注释模板。
 * - 用途：
 *   1) 帮助维护者快速理解文件职责、变更背景与风险点。
 *
 * 【段内说明】
 * - 复杂方法补充“干什么 / 边界 / 线程侧”精简中文注释。
 *
 * 【变更记录 #2】2026-07-19 19:16:14（第 2 次备注 · 内测四第 31 次更新）
 * - 删除：
 *   1) 删除退役无线仓直接把 BigInteger 网络余额作为 long 返回的非法类型假设。
 * - 新增：
 *   1) 无。
 * - 修改：
 *   1) WirelessView 对旧 long 能力接口使用 Long.MAX_VALUE 饱和视图，真实账户余额不截断、不回写。
 * - 用途：
 *   1) 保持残留 Java 类型可编译，同时明确无限精度只存在于无线网络核心 API。
 */
import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.gregtechceu.gtceu.api.machine.multiblock.part.TieredIOPartMachine;
import com.sirin.hk3gtl.common.block.energy.HonkaiHatchType;
import com.sirin.hk3gtl.common.capability.HonkaiEnergyStorage;
import com.sirin.hk3gtl.common.capability.HonkaiWirelessNetwork;
import com.sirin.hk3gtl.common.capability.IHonkaiEnergyContainer;

import net.minecraft.nbt.CompoundTag;

import javax.annotation.Nullable;
import java.util.UUID;

public class HonkaiEnergyHatchPartMachine extends TieredIOPartMachine {

    private final HonkaiHatchType type;
    private final HonkaiEnergyStorage localStorage;

    @Nullable
    private UUID ownerId;

    public HonkaiEnergyHatchPartMachine(IMachineBlockEntity holder, HonkaiHatchType type, Object... args) {
        // 中文备注：该处备注已按当前代码行为整理，不使用问号占位。
        super(holder, 0, type.canInsertFromOutside ? IO.IN : IO.OUT);
        this.type = type;

        if (type.creative) {
            this.localStorage = HonkaiEnergyStorage.creative();
        } else if (type.wireless) {
            this.localStorage = new HonkaiEnergyStorage(0, false, false, false);
        } else {
            this.localStorage = new HonkaiEnergyStorage(
                    type.localCapacity,
                    type.canInsertFromOutside,
                    type.canExtractFromOutside,
                    false);
        }
    }

    public HonkaiHatchType getHatchType() {
        return type;
    }

    @Nullable
    public UUID getOwnerId() {
        return ownerId;
    }

    public boolean ensureOwner(UUID playerId) {
        if (!type.wireless) return false;
        if (this.ownerId != null) return false;
        this.ownerId = playerId;
        return true;
    }

    public IHonkaiEnergyContainer getContainer() {
        if (type.wireless) {
            return new WirelessView();
        }
        return localStorage;
    }

    @Override
    public void saveCustomPersistedData(CompoundTag tag, boolean isItem) {
        super.saveCustomPersistedData(tag, isItem);
        tag.putString("type", type.id);
        if (ownerId != null) tag.putUUID("owner", ownerId);
        if (!type.wireless && !type.creative) {
            localStorage.saveNBT(tag);
        }
    }

    @Override
    public void loadCustomPersistedData(CompoundTag tag) {
        super.loadCustomPersistedData(tag);
        if (tag.hasUUID("owner")) this.ownerId = tag.getUUID("owner");
        if (!type.wireless && !type.creative) {
            localStorage.loadNBT(tag);
        }
    }

    private final class WirelessView implements IHonkaiEnergyContainer {
        @Override
        public long getAmount() {
            if (ownerId == null) return 0L;
            var stored = HonkaiWirelessNetwork.getStoredAmount(ownerId);
            return stored.bitLength() > 63 ? Long.MAX_VALUE : stored.longValue();
        }
        @Override
        public long getCapacity() {
            return Long.MAX_VALUE;
        }
        @Override
        public boolean canInsert() {
            return type == HonkaiHatchType.WIRELESS_INPUT;
        }
        @Override
        public boolean canExtract() {
            return type == HonkaiHatchType.WIRELESS_OUTPUT;
        }
        @Override
        public long insert(long request, boolean simulate) {
            if (ownerId == null || type != HonkaiHatchType.WIRELESS_INPUT) return 0;
            return HonkaiWirelessNetwork.insert(ownerId, request, simulate);
        }
        @Override
        public long extract(long request, boolean simulate) {
            if (ownerId == null || type != HonkaiHatchType.WIRELESS_OUTPUT) return 0;
            return HonkaiWirelessNetwork.extract(ownerId, request, simulate);
        }
    }
}
