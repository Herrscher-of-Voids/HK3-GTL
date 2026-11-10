package com.sirin.hk3gtl.archive.entrance;

import com.sirin.hk3gtl.common.dimension.Hk3Dimensions;
import com.sirin.hk3gtl.common.entity.VoidQueenSirinEntity;
import com.sirin.hk3gtl.common.network.ClearParticlesS2CPacket;
import com.sirin.hk3gtl.common.network.Hk3Network;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.network.PacketDistributor;

/** Rift, formation and coronation scene restored from the pre-redesign build. */
public final class SirinEntranceAnimationArchive {
    public static final int INTRO_DURATION_TICKS = 180;
    public static final double INTRO_RIFT_Y = Hk3Dimensions.PLATFORM_Y + 1.0D;
    public static final double INTRO_FORM_START_Y = Hk3Dimensions.PLATFORM_Y + 2.2D;
    public static final double INTRO_END_Y = Hk3Dimensions.PLATFORM_Y + 1.0D;
    public static final float PLATFORM_FACE_PLAYER_YAW = Hk3Dimensions.sirinFacePlayerYaw();
    public static final float INTRO_SPIN_START_YAW = Mth.wrapDegrees(PLATFORM_FACE_PLAYER_YAW + 72.0F);
    private static final int RIFT_END_TICKS = 72;
    private static final int FORM_END_TICKS = 150;

    private SirinEntranceAnimationArchive() {}

    public static void applyFacingYaw(VoidQueenSirinEntity entity, float yaw) {
        entity.setYRot(yaw);
        entity.yBodyRot = yaw;
        entity.yHeadRot = yaw;
        entity.yRotO = yaw;
        entity.yBodyRotO = yaw;
    }

    public static void onStart(VoidQueenSirinEntity entity) {
        hideForIntro(entity);
        entity.setPos(0.5D, INTRO_RIFT_Y, 0.5D);
    }

    public static void hideForIntro(VoidQueenSirinEntity entity) {
        entity.setInvisible(true);
        entity.setDeltaMovement(Vec3.ZERO);
    }

    public static void reveal(VoidQueenSirinEntity entity) {
        entity.setInvisible(false);
        entity.setPos(0.5D, INTRO_END_Y, 0.5D);
        applyFacingYaw(entity, PLATFORM_FACE_PLAYER_YAW);
        entity.setDeltaMovement(Vec3.ZERO);
        if (entity.level() instanceof ServerLevel level) clearResidualParticles(level);
    }

    public static boolean tick(VoidQueenSirinEntity entity, ServerLevel level, int introTicks) {
        double px = 0.5D;
        double pz = 0.5D;
        if (introTicks <= RIFT_END_TICKS) {
            hideForIntro(entity);
            entity.setPos(px, INTRO_RIFT_Y, pz);
            double progress = introTicks / (double) RIFT_END_TICKS;
            double slitHeight = 2.4D;
            double slitSpread = 0.12D + progress * 0.28D;
            double py = INTRO_RIFT_Y + 1.2D;
            level.sendParticles(ParticleTypes.REVERSE_PORTAL, px, py, pz, 40, slitSpread, slitHeight, 0.02D, 0.03D);
            level.sendParticles(ParticleTypes.PORTAL, px, py, pz, 32, slitSpread * 0.8D, slitHeight * 0.85D, 0.02D, 0.035D);
            level.sendParticles(ParticleTypes.SMOKE, px, py, pz, 10, 0.1D, slitHeight * 0.7D, 0.1D, 0.0D);
            level.sendParticles(ParticleTypes.SCULK_SOUL, px, py, pz, 6, slitSpread, slitHeight * 0.6D, 0.02D, 0.01D);
            spawnSpiralStream(level, px, INTRO_RIFT_Y + 0.2D, pz,
                    0.45D + progress * 0.7D, 2.4D, introTicks, ParticleTypes.END_ROD);
            if (introTicks % 6 == 0) {
                spawnHaloRing(level, px, py, pz, 0.8D + progress * 1.6D, ParticleTypes.WITCH);
                level.sendParticles(ParticleTypes.GLOW, px, py, pz, 4, slitSpread, 0.7D, 0.05D, 0.002D);
            }
            if (introTicks == RIFT_END_TICKS) {
                level.sendParticles(ParticleTypes.FLASH, px, py, pz, 1, 0, 0, 0, 0);
                spawnHaloRing(level, px, py, pz, 2.6D, ParticleTypes.END_ROD);
                level.sendParticles(ParticleTypes.SOUL_FIRE_FLAME, px, py, pz, 40, 1.4D, 1.0D, 1.4D, 0.06D);
            }
            return false;
        }
        if (introTicks <= FORM_END_TICKS) {
            hideForIntro(entity);
            double progress = (introTicks - RIFT_END_TICKS) / (double) (FORM_END_TICKS - RIFT_END_TICKS);
            double eased = 1.0D - Math.pow(1.0D - progress, 3.0D);
            double currentY = Mth.lerp(eased, INTRO_FORM_START_Y, INTRO_END_Y);
            entity.setPos(px, currentY, pz);
            applyFacingYaw(entity, Mth.rotLerp((float) eased, INTRO_SPIN_START_YAW, PLATFORM_FACE_PLAYER_YAW));
            double py = currentY + 1.0D;
            double radius = Mth.lerp((float) eased, 2.0F, 0.24F);
            level.sendParticles(ParticleTypes.END_ROD, px, py + 0.2D, pz, 22, radius, 1.2D, radius, 0.01D);
            level.sendParticles(ParticleTypes.ENCHANT, px, py + 0.4D, pz, 40, radius * 1.1D, 1.4D, radius * 1.1D, 0.03D);
            level.sendParticles(ParticleTypes.REVERSE_PORTAL, px, py, pz, 16, radius * 0.5D, 0.9D, radius * 0.5D, 0.01D);
            level.sendParticles(ParticleTypes.GLOW, px, py, pz, 8, radius, 1.0D, radius, 0.005D);
            spawnSpiralStream(level, px, currentY + 0.1D, pz, radius, 2.0D, -introTicks * 2, ParticleTypes.SOUL_FIRE_FLAME);
            if (introTicks % 5 == 0) spawnHaloRing(level, px, py, pz, Math.max(0.3D, radius), ParticleTypes.END_ROD);
            return false;
        }

        hideForIntro(entity);
        entity.setPos(px, INTRO_END_Y, pz);
        applyFacingYaw(entity, PLATFORM_FACE_PLAYER_YAW);
        double progress = (introTicks - FORM_END_TICKS) / (double) (INTRO_DURATION_TICKS - FORM_END_TICKS);
        double py = INTRO_END_Y + 1.0D;
        spawnSpearHalo(level, px, py, pz, 1.6D, introTicks, progress);
        if (introTicks % 3 == 0) {
            spawnHaloRing(level, px, py + 1.2D + progress * 0.6D, pz, 1.0D + progress * 1.2D, ParticleTypes.END_ROD);
        }
        level.sendParticles(ParticleTypes.ENCHANT, px, py + 0.6D, pz, 12, 0.5D, 1.0D, 0.5D, 0.02D);
        if (introTicks < INTRO_DURATION_TICKS) return false;
        level.sendParticles(ParticleTypes.FLASH, px, INTRO_END_Y + 1.1D, pz, 1, 0, 0, 0, 0);
        level.sendParticles(ParticleTypes.END_ROD, px, INTRO_END_Y + 1.0D, pz, 60, 0.4D, 1.4D, 0.4D, 0.04D);
        spawnHaloRing(level, px, INTRO_END_Y + 0.6D, pz, 2.4D, ParticleTypes.END_ROD);
        spawnHaloRing(level, px, INTRO_END_Y + 1.8D, pz, 1.4D, ParticleTypes.SOUL_FIRE_FLAME);
        return true;
    }

    public static void clearResidualParticles(ServerLevel level) {
        for (ServerPlayer player : level.players()) {
            Hk3Network.CHANNEL.send(PacketDistributor.PLAYER.with(() -> player), new ClearParticlesS2CPacket());
        }
    }

    private static void spawnSpearHalo(ServerLevel level, double cx, double cy, double cz,
                                       double radius, int phase, double lift) {
        double baseAngle = phase * 0.12D;
        double y = cy + lift;
        for (int i = 0; i < 6; i++) {
            double angle = baseAngle + Math.PI * 2.0D * i / 6;
            for (int seg = 1; seg <= 4; seg++) {
                double r = radius * (0.4D + seg * 0.2D);
                level.sendParticles(ParticleTypes.END_ROD, cx + Math.cos(angle) * r, y,
                        cz + Math.sin(angle) * r, 1, 0, 0, 0, 0);
            }
        }
    }

    private static void spawnHaloRing(ServerLevel level, double cx, double cy, double cz,
                                      double radius, ParticleOptions particle) {
        for (int i = 0; i < 24; i++) {
            double angle = Math.PI * 2.0D * i / 24;
            level.sendParticles(particle, cx + Math.cos(angle) * radius, cy,
                    cz + Math.sin(angle) * radius, 1, 0, 0, 0, 0);
        }
    }

    private static void spawnSpiralStream(ServerLevel level, double cx, double baseY, double cz,
                                          double radius, double height, int phase, ParticleOptions particle) {
        for (int i = 0; i < 6; i++) {
            double t = i / 6.0D;
            double angle = phase * 0.35D + t * Math.PI * 2.0D;
            double y = baseY + t * height;
            level.sendParticles(particle, cx + Math.cos(angle) * radius, y,
                    cz + Math.sin(angle) * radius, 1, 0, 0, 0, 0);
            level.sendParticles(particle, cx + Math.cos(angle + Math.PI) * radius, y,
                    cz + Math.sin(angle + Math.PI) * radius, 1, 0, 0, 0, 0);
        }
    }
}
