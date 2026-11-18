package com.sirin.hk3gtl.common.entity;

import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.level.Level;








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
