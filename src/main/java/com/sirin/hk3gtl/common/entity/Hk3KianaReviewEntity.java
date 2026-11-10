package com.sirin.hk3gtl.common.entity;

import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.level.Level;

/**
 * 【变更记录 #1】2026-10-01 19:03:37（修订141）
 * - 删除：无；新增：琪亚娜专用会面交互体，沿用盔甲架无AI与审查事件机制。
 * - 修改：会面由独立实体类型呈现，不再借不可见原版盔甲架表现人物。
 * - 用途：只供二审生命周期管理，无装备掉落、战斗或终审结算；注册为不保存实体。
 */
/** 【变更记录 #2】2026-10-01 19:08:10（修订141）：删除：无；新增／修改：扩大仅用于画面裁剪的包围盒，防止身体出画面时翅膀骤然消失；碰撞箱保持不变；用途：完整呈现二审人物及配件。 */
public final class Hk3KianaReviewEntity extends ArmorStand {
    public Hk3KianaReviewEntity(EntityType<? extends ArmorStand> type, Level level) {
        super(type, level);
        setNoGravity(true);
        setInvulnerable(true);
        setSilent(true);
        setShowArms(true);
        setNoBasePlate(true);
    }

    @Override public net.minecraft.world.phys.AABB getBoundingBoxForCulling() {
        return super.getBoundingBoxForCulling().inflate(2.5);
    }
}
