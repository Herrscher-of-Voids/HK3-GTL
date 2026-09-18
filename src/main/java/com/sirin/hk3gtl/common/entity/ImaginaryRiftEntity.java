package com.sirin.hk3gtl.common.entity;

import com.sirin.hk3gtl.archive.entrance.SirinEntranceAnimationArchive;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;


public class ImaginaryRiftEntity extends Entity {

    private int particleTick;

    public ImaginaryRiftEntity(EntityType<? extends ImaginaryRiftEntity> type, Level level) {
        super(type, level);
        this.setNoGravity(true);
        this.setInvulnerable(true);
        this.noPhysics = true;
    }

    @Override
    protected void defineSynchedData() {}

    @Override
    public void tick() {
        super.tick();
        particleTick++;
        if (this.level() instanceof ServerLevel sl) {
            emitRiftParticles(sl);
        }
    }

    /** 原版粒子组成虚数裂隙（服务端发包，客户端可见）。 */
    private void emitRiftParticles(ServerLevel level) {
        double px = getX();
        double py = getY() + 0.9D;
        double pz = getZ();
        double spread = 0.12D + (particleTick % 40) * 0.002D;
        double height = 1.6D;
        level.sendParticles(ParticleTypes.REVERSE_PORTAL, px, py, pz, 10, spread, height, spread, 0.02D);
        level.sendParticles(ParticleTypes.PORTAL, px, py, pz, 8, spread * 0.8D, height * 0.75D, spread * 0.8D, 0.03D);
        level.sendParticles(ParticleTypes.END_ROD, px, py + 0.3D, pz, 4, spread * 0.5D, 0.5D, spread * 0.5D, 0.01D);
        if (particleTick % 20 == 0) {
            level.sendParticles(ParticleTypes.SMOKE, px, py, pz, 3, 0.06D, height * 0.5D, 0.06D, 0.0D);
        }
    }

    @Override
    public InteractionResult interact(Player player, InteractionHand hand) {
        if (!level().isClientSide() && player instanceof ServerPlayer sp && level() instanceof ServerLevel sl) {
            VoidQueenSirinEntity.onRiftInteracted(sl, sp);
            discard();
        }
        return InteractionResult.sidedSuccess(level().isClientSide());
    }

    @Override
    public boolean isPickable() {
        return true;
    }

    @Override
    public boolean displayFireAnimation() {
        return false;
    }

    @Override
    protected void readAdditionalSaveData(net.minecraft.nbt.CompoundTag tag) {}

    @Override
    protected void addAdditionalSaveData(net.minecraft.nbt.CompoundTag tag) {}

    public static void spawnAtPlatform(ServerLevel level) {
        ImaginaryRiftEntity rift = Hk3Entities.IMAGINARY_RIFT.get().create(level);
        if (rift == null) {
            return;
        }
        rift.moveTo(0.5D, SirinEntranceAnimationArchive.INTRO_RIFT_Y, 0.5D, 0.0F, 0.0F);
        level.addFreshEntity(rift);
    }
}
