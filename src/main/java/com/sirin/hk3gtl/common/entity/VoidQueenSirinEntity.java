package com.sirin.hk3gtl.common.entity;



import com.sirin.hk3gtl.archive.entrance.SirinEntranceAnimationArchive;
import com.sirin.hk3gtl.common.badending.Hk3BadEndingData;
import com.sirin.hk3gtl.common.badending.SirinBadEndingManager;
import com.sirin.hk3gtl.common.dimension.Hk3Dimensions;
import com.sirin.hk3gtl.common.dimension.Hk3GraduationData;
import com.sirin.hk3gtl.common.dialogue.DialogueSessionManager;
import com.sirin.hk3gtl.common.event.Hk3FactionEventChecker;
import com.sirin.hk3gtl.common.dialogue.SirinIfProgressStore;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityDimensions;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.Pose;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.network.chat.Component;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.LightBlock;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 空之律者·西琳 —— 虚数维度唯一实体 / 终局剧情 NPC。
 *
 * <h3>特性</h3>
 * <ul>
 *   <li>无敌，免疫所有伤害（包括 /kill 指令）</li>
 *   <li>不可推动、不可击退、不可清除</li>
 *   <li>无 AI，静止悬浮</li>
 *   <li>右键实体触发终局对话（通过 S2C 网络包）</li>
 *   <li>每个玩家只触发一次（防重复），世界毕业后全局禁用</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>调整无敌/属性：修改 {@link #createAttributes()} 或无敌系统区域方法</li>
 *   <li>对话触发逻辑：修改 {@link #tryStartDialogue(ServerPlayer)}</li>
 *   <li>平台生成：修改 {@link #ensurePlatformAndEntity(ServerLevel)}</li>
 *   <li>{@link #triggeredPlayers} 为运行时内存，服务端重启会清空；若需持久化应写入 save data</li>
 *   <li>禁止移除无敌相关重写方法，会破坏终局安全性</li>
 * </ul>
 */
public class VoidQueenSirinEntity extends Mob {

    private static final Logger LOGGER = LogUtils.getLogger();

    /** 出场动画结束高度：悬浮在平台中心上方一格。 */
    private static final double READY_Y = SirinEntranceAnimationArchive.INTRO_END_Y;

    /**
     * 坏结局体型缩放（同步字段）：1.0 = 正常，10.0 = 抓取阶段的十倍体型。
     * 通过 SynchedEntityData 同步到客户端，渲染器与碰撞箱都读取该值。
     */
    private static final EntityDataAccessor<Float> DATA_BAD_ENDING_SCALE =
            SynchedEntityData.defineId(VoidQueenSirinEntity.class, EntityDataSerializers.FLOAT);

    /** 伤害反弹倍率：玩家对西琳造成伤害的 1000% 反弹给玩家自身。 */
    private static final float DAMAGE_REFLECT_MULTIPLIER = 10.0F;

    /**
     * 记录已触发对话的玩家 UUID（服务端运行时内存，防止同一玩家重复触发）。
     * 使用 ConcurrentHashMap 保证服务端 tick 与交互线程下的并发安全。
     */
    private final ConcurrentHashMap<UUID, Boolean> triggeredPlayers = new ConcurrentHashMap<>();
    /** 正在等待出场动画结束后打开终局对话的玩家。 */
    private final ConcurrentHashMap<UUID, Integer> pendingDialogues = new ConcurrentHashMap<>();
    private boolean introCompleted;
    private boolean introPlaying;
    private int introTicks;

    /** 调试用：清除已触发记录，允许同一玩家重新走一次对话流程。 */
    public void resetTriggeredPlayers() {
        triggeredPlayers.clear();
        pendingDialogues.clear();
        introCompleted = false;
        introPlaying = false;
        introTicks = 0;
        applyInitialPose();
    }

    /**
     * 构造函数：禁用重力、设为无敌、设为常驻实体（不会因无人加载而卸载）。
     */
    public VoidQueenSirinEntity(EntityType<? extends VoidQueenSirinEntity> type, Level level) {
        super(type, level);
        this.setNoGravity(true);
        this.setInvulnerable(true);
        this.setPersistenceRequired();
    }

    /**
     * 实体属性构建器：全部拉满至 1.20.1 RangedAttribute 的合法钳制上限。
     * MAX_HEALTH=1024 / ATTACK_DAMAGE=2048 / ARMOR=30 / ARMOR_TOUGHNESS=20 均为属性系统硬上限，
     * 超出会被 sanitizeValue 静默钳制。真实防御由无敌系统保证，此处仅为数值层拉满。
     */
    public static AttributeSupplier.Builder createAttributes() {
        return Mob.createMobAttributes()
                .add(Attributes.MAX_HEALTH, 1024.0)
                .add(Attributes.MOVEMENT_SPEED, 0)
                .add(Attributes.KNOCKBACK_RESISTANCE, 1.0)
                .add(Attributes.ATTACK_DAMAGE, 2048.0)
                .add(Attributes.ARMOR, 30.0)
                .add(Attributes.ARMOR_TOUGHNESS, 20.0)
                .add(Attributes.FOLLOW_RANGE, 128.0);
    }

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(DATA_BAD_ENDING_SCALE, 1.0F);
    }

    // ══════════════════════════════════════
    //  坏结局体型缩放（服务端写入 → 自动同步客户端）
    // ══════════════════════════════════════

    public float getBadEndingScale() {
        return this.entityData.get(DATA_BAD_ENDING_SCALE);
    }

    /** 仅服务端调用；同步数据变更后双端各自 refreshDimensions。 */
    public void setBadEndingScale(float scale) {
        this.entityData.set(DATA_BAD_ENDING_SCALE, scale);
        this.refreshDimensions();
    }

    /** 碰撞箱随坏结局缩放同步放大。 */
    @Override
    public EntityDimensions getDimensions(Pose pose) {
        return super.getDimensions(pose).scale(getBadEndingScale());
    }

    /** 客户端收到缩放同步时刷新碰撞箱。 */
    @Override
    public void onSyncedDataUpdated(EntityDataAccessor<?> key) {
        super.onSyncedDataUpdated(key);
        if (DATA_BAD_ENDING_SCALE.equals(key)) {
            this.refreshDimensions();
        }
    }

    // ══════════════════════════════════════
    //  AI 禁用：不注册任何 AI Goal，也禁止移动
    // ══════════════════════════════════════

    /** 不注册任何 AI Goal，西琳完全静止。 */
    @Override
    protected void registerGoals() {}

    /** 禁用移动：无论外部如何施加速度，实体都不会位移。 */
    @Override
    public void travel(Vec3 movement) {}

    // ══════════════════════════════════════
    //  无敌系统：屏蔽所有伤害/清除/推动途径
    // ══════════════════════════════════════

    /**
     * 屏蔽所有伤害来源，包括 /kill 指令背后的 out_of_world。
     * 附加：玩家攻击时将伤害的 1000% 以 GENERIC_KILL 系伤害源（无视护甲/抗性/格挡/无敌帧）反弹给玩家。
     */
    @Override
    public boolean hurt(DamageSource source, float amount) {
        if (!this.level().isClientSide() && amount > 0
                && source.getEntity() instanceof ServerPlayer attacker
                && attacker.isAlive() && !attacker.isCreative()) {
            attacker.invulnerableTime = 0;
            attacker.hurt(absoluteDamageSource(), amount * DAMAGE_REFLECT_MULTIPLIER);
        }
        return false;
    }

    /**
     * 构建"绝对伤害源"：GENERIC_KILL 类型（/kill 同款），归属于西琳。
     * 该伤害类型位于 bypasses_armor / bypasses_effects / bypasses_invulnerability 等原版标签中，
     * 实现必中、无视防御、不可格挡/闪避。
     */
    private DamageSource absoluteDamageSource() {
        var damageType = this.level().registryAccess()
                .registryOrThrow(Registries.DAMAGE_TYPE)
                .getHolderOrThrow(DamageTypes.GENERIC_KILL);
        return new DamageSource(damageType, this);
    }

    @Override
    public void die(DamageSource source) {
        this.deathTime = 0;
        this.setHealth(this.getMaxHealth());
    }

    @Override
    public void setHealth(float health) {
        if (health <= 0.0F) {
            this.deathTime = 0;
            super.setHealth(this.getMaxHealth());
            return;
        }
        super.setHealth(health);
    }

    @Override
    public void remove(Entity.RemovalReason reason) {
        if (reason == Entity.RemovalReason.KILLED) {
            this.deathTime = 0;
            this.setHealth(this.getMaxHealth());
        } else {
            super.remove(reason);
        }
    }

    @Override
    protected void tickDeath() {
        this.deathTime = 0;
        this.setHealth(this.getMaxHealth());
    }

    /** 每 tick 强制回满生命值（≥ 每秒 100% 总生命值的回复效果）。 */
    private void tickFullRegeneration() {
        if (this.getHealth() < this.getMaxHealth()) {
            this.setHealth(this.getMaxHealth());
        }
    }

    /** 免疫所有药水/debuff 效果（玩家端减益全部无效）。 */
    @Override
    public boolean canBeAffected(MobEffectInstance effect) { return false; }

    /**
     * 专属必中攻击：使用 GENERIC_KILL 系伤害源，无视目标全部防御属性、
     * 不可被格挡/闪避/无敌帧减免，按拉满的 ATTACK_DAMAGE 属性造成全额伤害。
     */
    @Override
    public boolean doHurtTarget(Entity target) {
        float damage = (float) this.getAttributeValue(Attributes.ATTACK_DAMAGE);
        if (target instanceof LivingEntity living) {
            living.invulnerableTime = 0;
        }
        return target.hurt(absoluteDamageSource(), damage);
    }

    /** 禁用 kill()：/kill 指令无法销毁此实体。 */
    @Override
    public void kill() {}

    /** 禁止因玩家距离过远被自动清除。 */
    @Override
    public boolean removeWhenFarAway(double distance) { return false; }

    /** 标记为常驻实体。 */
    @Override
    public boolean isPersistenceRequired() { return true; }

    /** 对所有伤害源免疫（双重保险）。 */
    @Override
    public boolean isInvulnerableTo(DamageSource source) { return true; }

    /** 禁止被其他实体推动。 */
    @Override
    public boolean isPushable() { return false; }

    /** 禁用 push(Entity) 重写，阻止碰撞位移。 */
    @Override
    public void push(Entity entity) {}

    /** 禁用 push(xyz) 重写，阻止矢量位移。 */
    @Override
    public void push(double x, double y, double z) {}

    /** 禁止跨维度传送（避免离开虚数维度）。 */
    @Override
    public boolean canChangeDimensions() { return false; }

    /** 不可被玩家拴绳。 */
    @Override
    public boolean canBeLeashed(Player player) { return false; }

    // ══════════════════════════════════════
    //  玩家交互 → 触发对话
    // ══════════════════════════════════════

    /**
     * 玩家右键交互：服务端尝试触发终局对话。
     * 修改要点：若需要改为仅“主手 + 空手”触发，可在此处加手/物品判断。
     */
    @Override
    protected InteractionResult mobInteract(Player player, InteractionHand hand) {
        if (!player.level().isClientSide() && player instanceof ServerPlayer sp) {
            tryStartDialogue(sp);
        }
        return InteractionResult.sidedSuccess(player.level().isClientSide());
    }

    /** 出场动画 tick；不再靠近自动开对话，仅右键 {@link #mobInteract} 触发。 */
    @Override
    public void aiStep() {
        super.aiStep();
        if (this.level().isClientSide() || !(this.level() instanceof ServerLevel sl)) return;
        tickFullRegeneration();
        SirinBadEndingManager.tickBossFight(this, sl);
        if (SirinEntranceFeatures.ENTRANCE_ANIMATION_ENABLED && introPlaying) {
            tickEntranceAnimation(sl);
        }
    }

    /**
     * 尝试为指定玩家触发终局对话。
     *
     * <p>流程：对话完成检查 → 玩家去重 → {@link DialogueSessionManager} 启动通用对话。
     */
    private static final String DIALOGUE_DONE_TAG = "hk3gtl_dialogue_done";

    private void tryStartDialogue(ServerPlayer player) {
        if (Hk3GraduationData.get(player.serverLevel()).isGraduated()) return;
        if (player.getPersistentData().getBoolean(DIALOGUE_DONE_TAG)) return;
        // 坏结局流程激活后（含被抹除/终局文本阶段）不再走常规终局对话
        if (Hk3BadEndingData.get(player.serverLevel()).getStage() != Hk3BadEndingData.STAGE_NONE) return;

        UUID uuid = player.getUUID();
        if (triggeredPlayers.containsKey(uuid)) return;
        if (pendingDialogues.containsKey(uuid)) return;

        int availableMask = SirinIfProgressStore.availableMask(player);
        if (availableMask == 0 && SirinIfProgressStore.usesGlobalIfDedup(player)) {
            player.sendSystemMessage(Component.translatable("hk3gtl.dialogue.sirin.no_more_if"));
            return;
        }

        if (!introCompleted) {
            if (introPlaying) {
                player.sendSystemMessage(Component.translatable("hk3gtl.imaginary.sirin.revealing"));
            } else {
                player.sendSystemMessage(Component.translatable("hk3gtl.imaginary.sirin.touch_rift_first"));
            }
            return;
        }

        pendingDialogues.put(uuid, availableMask);
        openPendingDialogues();
    }

    // ══════════════════════════════════════
    //  数据持久化（预留，当前无附加字段需要存档）
    // ══════════════════════════════════════

    /** 保存附加数据：目前无额外字段。若后续记录"已触发玩家列表"应在此写入 NBT。 */
    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putBoolean("hk3gtl_intro_completed", introCompleted);
    }

    /** 读取附加数据：与 {@link #addAdditionalSaveData(CompoundTag)} 对应。 */
    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        introCompleted = tag.getBoolean("hk3gtl_intro_completed");
        introPlaying = false;
        introTicks = 0;
        pendingDialogues.clear();
        if (introCompleted || !SirinEntranceFeatures.ENTRANCE_ANIMATION_ENABLED) {
            ensureReadyPose();
        } else {
            prepareDormantPose();
        }
    }

    // ══════════════════════════════════════
    //  平台与实体生成
    // ══════════════════════════════════════

    /**
     * 在虚数维度生成 11×11 屏障平台并放置西琳实体（幂等）。
     * 由 ImaginaryDimensionHandler 在维度加载时调用。
     *
     * <p>幂等保证：通过中心方块是否为空气判断，非空气则直接返回，避免重复生成。
     * 修改要点：
     * <ul>
     *   <li>平台大小由 {@link Hk3Dimensions#PLATFORM_HALF} 控制</li>
     *   <li>平台高度由 {@link Hk3Dimensions#PLATFORM_Y} 控制</li>
     *   <li>若替换平台材质，修改 {@code platformBlock} 变量即可</li>
     * </ul>
     */
    public static void ensurePlatformAndEntity(ServerLevel level) {
        if (level.dimension() != Hk3Dimensions.IMAGINARY) return;

        int y = Hk3Dimensions.PLATFORM_Y;
        int half = Hk3Dimensions.PLATFORM_HALF;

        BlockPos centerPos = new BlockPos(0, y, 0);
        if (level.getBlockState(centerPos).isAir()) {
            LOGGER.info("[HK3GTL] 虚数维度首次加载，生成 11×11 平台...");
            var platformBlock = Blocks.BARRIER.defaultBlockState();
            for (int x = -half; x <= half; x++) {
                for (int z = -half; z <= half; z++) {
                    level.setBlock(new BlockPos(x, y, z), platformBlock, 3);
                }
            }
        }
        ensureLightSources(level, y);
        syncImaginaryEncounterState(level);
        ensureRift(level);
    }

    /**
     * 维度就绪时同步遭遇状态：未与裂隙交互前不保留西琳实体，仅已登场（introCompleted）的保留。
     */
    private static void syncImaginaryEncounterState(ServerLevel level) {
        int y = Hk3Dimensions.PLATFORM_Y;
        var entities = level.getEntities(
                Hk3Entities.VOID_QUEEN_SIRIN.get(),
                new AABB(-32, y - 8, -32, 32, y + 16, 32),
                e -> true);
        VoidQueenSirinEntity kept = null;
        for (VoidQueenSirinEntity sirin : entities) {
            if (sirin.introCompleted) {
                if (kept == null) {
                    kept = sirin;
                    sirin.ensureReadyPose();
                } else {
                    sirin.discard();
                }
            } else {
                sirin.discard();
            }
        }
    }

    /** 西琳已登场则移除裂隙；否则保证平台中央存在可右键裂隙。 */
    public static void ensureRift(ServerLevel level) {
        if (level.dimension() != Hk3Dimensions.IMAGINARY) {
            return;
        }
        VoidQueenSirinEntity sirin = findSirin(level);
        if (sirin != null && sirin.introCompleted) {
            removeAllRifts(level);
            return;
        }
        int y = Hk3Dimensions.PLATFORM_Y;
        var rifts = level.getEntities(
                Hk3Entities.IMAGINARY_RIFT.get(),
                new AABB(-8, y - 4, -8, 8, y + 12, 8),
                e -> true);
        if (rifts.isEmpty()) {
            ImaginaryRiftEntity.spawnAtPlatform(level);
        }
    }

    public static void removeAllRifts(ServerLevel level) {
        level.getEntities(
                Hk3Entities.IMAGINARY_RIFT.get(),
                new AABB(-1.0E6, -1.0E6, -1.0E6, 1.0E6, 1.0E6, 1.0E6),
                e -> true).forEach(Entity::discard);
    }

    public static VoidQueenSirinEntity findSirin(ServerLevel level) {
        int y = Hk3Dimensions.PLATFORM_Y;
        var list = level.getEntities(
                Hk3Entities.VOID_QUEEN_SIRIN.get(),
                new AABB(-32, y - 8, -32, 32, y + 16, 32),
                e -> true);
        return list.isEmpty() ? null : list.get(0);
    }

    /** 玩家右键虚数裂隙：播登场动画或立即现身，不打开终局对话。 */
    public static void onRiftInteracted(ServerLevel level, ServerPlayer player) {
        VoidQueenSirinEntity sirin = findSirin(level);
        if (sirin == null) {
            spawnSirinAtPlatform(level);
            sirin = findSirin(level);
        }
        if (sirin != null) {
            sirin.beginRevealFromRift(player);
        }
    }

    /** 裂隙交互后触发西琳登场（粒子动画或立即 reveal）。 */
    public void beginRevealFromRift(ServerPlayer player) {
        if (introCompleted || introPlaying) {
            return;
        }
        if (!SirinEntranceFeatures.ENTRANCE_ANIMATION_ENABLED) {
            ensureReadyPose();
            player.sendSystemMessage(Component.translatable("hk3gtl.imaginary.sirin.ready_hint"));
            return;
        }
        startEntranceAnimation();
    }

    /** 清除维度内全部西琳实体（重复传送/调试指令时避免重叠）。 */
    public static int removeAllSirins(ServerLevel level) {
        var entities = level.getEntities(
                Hk3Entities.VOID_QUEEN_SIRIN.get(),
                new AABB(-1.0E6, -1.0E6, -1.0E6, 1.0E6, 1.0E6, 1.0E6),
                e -> true
        );
        int count = entities.size();
        entities.forEach(Entity::discard);
        if (count > 0) {
            LOGGER.info("[HK3GTL] 已清除 {} 个空之律者实体", count);
        }
        return count;
    }

    /** 调试：重置为「仅裂隙」状态，便于重测右键裂隙 → 登场流程。 */
    public static void respawnSirinFresh(ServerLevel level) {
        if (level.dimension() != Hk3Dimensions.IMAGINARY) return;
        removeAllRifts(level);
        removeAllSirins(level);
        ensureRift(level);
    }

    private static void spawnSirinAtPlatform(ServerLevel level) {
        int y = Hk3Dimensions.PLATFORM_Y;
        VoidQueenSirinEntity sirin = Hk3Entities.VOID_QUEEN_SIRIN.get().create(level);
        if (sirin == null) return;
        sirin.prepareDormantPose();
        SirinEntranceAnimationArchive.applyFacingYaw(sirin, SirinEntranceAnimationArchive.PLATFORM_FACE_PLAYER_YAW);
        level.addFreshEntity(sirin);
        LOGGER.info("[HK3GTL] 空之律者·西琳已生成于 (0, {}, 0)", y + 1);
    }

    private static void ensureLightSources(ServerLevel level, int platformY) {
        var lightState = Blocks.LIGHT.defaultBlockState().setValue(LightBlock.LEVEL, 15);
        BlockPos[] lightPositions = new BlockPos[] {
                new BlockPos(0, platformY + 3, 0),
                new BlockPos(2, platformY + 1, 0),
                new BlockPos(-2, platformY + 1, 0),
                new BlockPos(0, platformY + 1, 2),
                new BlockPos(0, platformY + 1, -2)
        };
        for (BlockPos pos : lightPositions) {
            var current = level.getBlockState(pos);
            if (current.isAir() || current.is(Blocks.LIGHT)) {
                level.setBlock(pos, lightState, 3);
            }
        }
    }

    /** 内测二：直接悬浮现身，跳过裂隙/凝聚演出。 */
    private void ensureReadyPose() {
        this.introPlaying = false;
        this.introTicks = 0;
        this.introCompleted = true;
        this.setInvisible(false);
        this.setPos(0.5D, READY_Y, 0.5D);
        this.setDeltaMovement(Vec3.ZERO);
        SirinEntranceAnimationArchive.applyFacingYaw(this, SirinEntranceAnimationArchive.PLATFORM_FACE_PLAYER_YAW);
    }

    private void applyInitialPose() {
        if (introCompleted) {
            ensureReadyPose();
        } else {
            prepareDormantPose();
        }
    }

    /** 出场动画未播完前的隐形待机动位（仅 ENTANCE_ANIMATION_ENABLED 时使用）。 */
    private void prepareDormantPose() {
        this.introPlaying = false;
        this.introTicks = 0;
        this.setInvisible(true);
        this.setPos(0.5D, SirinEntranceAnimationArchive.INTRO_RIFT_Y, 0.5D);
        this.setDeltaMovement(Vec3.ZERO);
    }

    private void startEntranceAnimation() {
        if (introPlaying || introCompleted || !(this.level() instanceof ServerLevel)) return;
        introPlaying = true;
        introTicks = 0;
        SirinEntranceAnimationArchive.onStart(this);
        LOGGER.info("[HK3GTL] 空之律者·西琳开始终局出场动画");
    }

    private void tickEntranceAnimation(ServerLevel level) {
        introTicks++;
        if (!SirinEntranceAnimationArchive.tick(this, level, introTicks)) {
            return;
        }
        introPlaying = false;
        introCompleted = true;
        SirinEntranceAnimationArchive.reveal(this);
        for (ServerPlayer player : level.players()) {
            if (player.level() == level) {
                player.sendSystemMessage(Component.translatable("hk3gtl.imaginary.sirin.ready_hint"));
            }
        }
    }

    private void openPendingDialogues() {
        if (!(this.level() instanceof ServerLevel level) || pendingDialogues.isEmpty()) {
            return;
        }
        var server = level.getServer();
        for (var entry : pendingDialogues.entrySet()) {
            UUID uuid = entry.getKey();
            int availableMask = entry.getValue();
            ServerPlayer player = server.getPlayerList().getPlayer(uuid);
            pendingDialogues.remove(uuid);
            if (player == null || player.level() != level) continue;
            if (Hk3GraduationData.get(player.serverLevel()).isGraduated()) continue;
            if (player.getPersistentData().getBoolean(DIALOGUE_DONE_TAG)) continue;
            if (DialogueSessionManager.startDialogue(player, "sirin_finale", availableMask)) {
                triggeredPlayers.put(uuid, true);
                Hk3FactionEventChecker.onFinaleDialogueStarted(player);
                LOGGER.info("[HK3GTL] 终局对话触发 - 玩家: {}", player.getName().getString());
            }
        }
    }
}
