package com.sirin.hk3gtl.common.multiblock.build;

import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import com.gregtechceu.gtceu.api.machine.feature.multiblock.IMultiController;
import com.gregtechceu.gtceu.api.machine.feature.multiblock.IMultiPart;
import com.gregtechceu.gtceu.api.pattern.MultiblockState;
import com.gregtechceu.gtceu.api.pattern.MultiblockWorldSavedData;
import com.mojang.logging.LogUtils;
import com.sirin.hk3gtl.common.machine.Hk3W01HallMachine;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.level.TicketType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.common.util.BlockSnapshot;
import net.minecraftforge.event.ForgeEventFactory;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.level.ChunkEvent;
import net.minecraftforge.event.server.ServerStoppingEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.gtlcore.gtlcore.common.item.UltimateTerminalBehavior.AutoBuildSetting;
import org.slf4j.Logger;

import java.util.Comparator;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 【文件职责】所有HK3GTL控制器共用的终端分批建造入口；材料事务与最终GT成型判定分离。
 * 【变更记录 #1】2026-10-30 01:32:51（第1次备注 · 内测5修订184）
 * - 新增：W01、批准NBT/稀疏结构及小型Pattern共用的限时建造任务；普通背包与AE材料逐格预扣。
 * - 修改：搭建期间抑制重复结构扫描；只维持控制器和当前目标区块的有限票据，不逐格扫描或强加载整座结构。
 * - 用途：统一终极终端和GT Pattern自动建造入口；放置后仍由原Pattern实际验证，不伪造成型。
 * 【变更记录 #2】2026-10-30（修订184）
 * - 修改：准备完成后建立稳定支撑顺序；检查朝向变化；暂停只保留控制器票，结束立即释放蓝图与票据。
 * - 用途：不把有限区块建造误称为整座已成型，不让等待原Pattern检查的任务永久占用建造入口。
 * 【变更记录 #3】2026-10-30 02:29:19（修订184）
 * - 删除：无效WAIT分支及重复失效回调；新增：开工锁、任务身份校验与异常清理。
 * - 修改：结束立即释放有限票据并恢复原GT检查；保护取消或回调中断时恢复快照、退还预扣材料。
 * - 用途：不覆盖玩家改向或取消后的世界，不把实体搭建完成视为整座区块已加载或已成型。
 * 【变更记录 #4】2026-10-30 02:34:31（修订184）
 * - 修改：同一快照只尝试回退一次；回退失败结算该格材料并停工，保留原异常及回退异常。
 * - 用途：避免保护取消或异常时方块仍在世界而材料已退回，需要人工核对的情况明确报告。
 * 【变更记录 #5】2026-10-30（修订184）：主控锚点按真实控制器身份与朝向验证，避免原建筑方块或运行态属性阻断建造。
 * 【变更记录 #6】2026-10-30：拆除复用分批预算、有限票据及取消清理；正式实体与合法仓位逐格校验，开工及结束清理GT匹配缓存。
 */
@Mod.EventBusSubscriber(modid = "hk3gtl", bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class Hk3UniversalTerminalBuilder {
    private static final Logger LOGGER = LogUtils.getLogger();
    private static final TicketType<Long> TICKET = TicketType.create("hk3gtl_multiblock_build", Comparator.<Long>naturalOrder());
    private static final Map<MinecraftServer, Job> JOBS = new ConcurrentHashMap<>();

    private Hk3UniversalTerminalBuilder() {}

    public static void use(Player player, MultiblockState state, AutoBuildSetting setting) {
        if (!(player instanceof ServerPlayer owner) || state == null || state.getController() == null
                || !(state.getController() instanceof MultiblockControllerMachine controller)
                || !(controller.getLevel() instanceof ServerLevel level)
                || owner.level() != level || !level.getServer().isSameThread()
                || !"hk3gtl".equals(controller.self().getDefinition().getId().getNamespace())) return;

        if (owner.isSpectator() || !owner.getAbilities().mayBuild || !level.mayInteract(owner,controller.getPos())
                || !owner.mayUseItemAt(controller.getPos(),Direction.UP,owner.getMainHandItem())) {
            tell(owner,"无权操作该HK3GTL控制器。"); return;
        }

        if (setting == null) setting = new AutoBuildSetting();
        if (controller.getFrontFacing().getAxis().isVertical() || controller.getUpwardsFacing() != Direction.NORTH
                || controller.isFlipped()) {
            tell(owner, "控制器朝向不受当前批准蓝图支持；请水平放置且保持顶部朝上。");
            return;
        }

        Job previous = JOBS.get(level.getServer());
        if (previous != null) {
            if (previous.controller != controller || !previous.owner.equals(owner.getUUID())) {
                tell(owner, "服务器当前已有一项HK3GTL多方块建造任务。");
            } else {
                if (previous.dismantle != setting.isDismantleMode()) {
                    release(previous, "HK3GTL终端任务已取消；已完成部分保留，再次使用可开始当前模式。", true);
                    return;
                }
                if (!previous.valid()) {
                    release(previous, "控制器或建造者状态已改变，原建造任务已停止；再次使用终端可重新开始。", true);
                    return;
                }
                previous.paused = !previous.paused;
                if (previous.paused) previous.removeTargetTickets();
                tell(owner, previous.paused ? "HK3GTL终端任务已暂停；再次使用相同模式可继续。" : "HK3GTL终端任务继续。" );
            }
            return;
        }

        if (!setting.isDismantleMode() && !supported(setting)) {
            tell(owner, "HK3GTL分批建造暂不支持当前终端选项；未放置方块，也未扣除材料。");
            return;
        }
        if (!controller.getPatternLock().tryLock()) {
            tell(owner, "该控制器正在检查结构，请稍后再次使用终端。"); return;
        }
        Hk3BuildPlan plan = null;
        Job job = null;
        try {
            if (controller.isInValid() || MetaMachine.getMachine(level,controller.getPos()) != controller) return;
            if (controller.isFormed() && !setting.isDismantleMode()) {
                tell(owner, "该多方块已通过真实成型检查，无需重建。"); return;
            }
            plan = Hk3BuildPlans.create(controller);
            if (plan.creativeOnly() && (!owner.isCreative() || setting.isDismantleMode())) {
                plan.close();
                tell(owner, "该批准蓝图当前仅开放创造模式搭建测试；生产与生存材料流程尚未开放。");
                return;
            }
            job = new Job(owner, controller, level, plan, setting);
            job.validateBounds();
            if (JOBS.putIfAbsent(level.getServer(),job) != null) {
                plan.close(); tell(owner, "服务器当前已有一项HK3GTL多方块建造任务。"); return;
            }
            job.addControllerTicket();
            var saved = MultiblockWorldSavedData.getOrCreate(level);
            saved.removeMapping(state);
            controller.onStructureInvalid();
            ((com.sirin.hk3gtl.mixin.gtceu.Hk3MultiblockStateAccess)(Object)state).hk3gtl$clean();
            state.setError(MultiblockState.UNINIT_ERROR);
            saved.removeAsyncLogic(controller);
            if (controller instanceof Hk3W01HallMachine hall) hall.setTerminalBuilding(true);
        } catch (BuildBoundaryFailure failure) {
            if (plan != null) plan.close();
            tell(owner, failure.getMessage());
            return;
        } catch (RuntimeException failure) {
            try {
                if (job != null && JOBS.get(level.getServer()) == job) release(job,null,true);
                else if (plan != null) plan.close();
            } catch (RuntimeException cleanup) { failure.addSuppressed(cleanup); }
            LOGGER.warn("HK3GTL建造启动失败：{}", controller.self().getDefinition().getId(), failure);
            tell(owner, "批准蓝图无法启动；未放置方块，也未扣除材料。");
            return;
        } finally { controller.getPatternLock().unlock(); }
        owner.displayClientMessage(Component.literal(setting.isDismantleMode() ? "HK3GTL分批拆除已启动；只处理批准实体和合法仓位，保留控制器。"
                : "HK3GTL分批建造已启动；逐格扣料，最终成型由机器原有结构检查确认。"),true);
    }

    public static boolean cancel(Player player, IMultiController target) {
        if (!(player instanceof ServerPlayer owner)) return false;
        Job job = JOBS.get(owner.server);
        if (job == null || job.controller != target || !job.owner.equals(owner.getUUID())) return false;
        if (!owner.server.isSameThread()) return false;
        release(job, "HK3GTL终端任务已取消；已完成部分保留。", true);
        return true;
    }

    public static boolean isBuilding(IMultiController controller) {
        if (controller == null) return false;
        if (!(controller.self().getLevel() instanceof ServerLevel level)) return false;
        Job job = JOBS.get(level.getServer());
        return job != null && job.controller == controller;
    }

    /** 仅接受当前操作者的帧耗时；客户端只能缩小自身建造限额。 */
    public static void clientFrameTime(ServerPlayer player, float millis) {
        Job job=JOBS.get(player.server);
        if(job!=null && job.owner.equals(player.getUUID()) && Float.isFinite(millis)
                && millis>=1 && millis<=1000 && job.level.getGameTime()-job.frameReportTick>=10) {
            job.frameMillis=millis; job.frameReportTick=job.level.getGameTime();
        }
    }

    public static String progress(IMultiController controller) {
        if(!(controller.self().getLevel() instanceof ServerLevel level)) return "";
        Job job=JOBS.get(level.getServer());
        return job==null || job.controller!=controller ? "" : (job.paused?"已暂停 · ":"")
                +(job.stage==Stage.BUILD?"搭建":job.preparation==null?"等待后台准备":job.preparation.progress(job.plan.size()))
                +" · "+Hk3BuildProgress.percent(job.checked,job.plan.size())+"％ · "+job.checked+"/"+job.plan.size()+" · 已放置 "+job.placed;
    }

    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        Job job = JOBS.get(event.getServer());
        if (job == null) return;
        long begin = System.nanoTime();
        long budget = Hk3W01BuildBudget.nanos(event.getServer().getAverageTickTime(),job.frameMillis);
        try {
            if (!job.valid()) { release(job, "HK3GTL终端任务中止；已完成部分保留。", true); return; }
            job.tick(begin + budget);
        } catch (RuntimeException failure) {
            LOGGER.error("HK3GTL终端任务失败；已完成部分保留，未提交建材按事务退还", failure);
            release(job, "HK3GTL终端任务失败；请核对日志中的材料或掉落。", true);
        }
    }

    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) {
            Job job = JOBS.get(player.server);
            if (job != null && job.owner.equals(player.getUUID()))
                release(job, "操作者离线，HK3GTL终端任务已停止；已完成部分保留。", true);
        }
    }

    @SubscribeEvent public static void chunkUnload(ChunkEvent.Unload event) {
        if (event.getLevel() instanceof ServerLevel level) {
            Job job = JOBS.get(level.getServer());
            if (job != null && job.level == level && job.controllerChunk == event.getChunk().getPos().toLong())
                release(job, "控制器区块卸载，HK3GTL终端任务已停止；已完成部分保留。", false);
        }
    }

    @SubscribeEvent public static void stopping(ServerStoppingEvent event) {
        Job job = JOBS.get(event.getServer());
        if (job != null) release(job, "服务器关闭，HK3GTL终端任务已清理。", false);
    }

    public static void controllerUnloaded(IMultiController controller) {
        if (!(controller.self().getLevel() instanceof ServerLevel level) || !level.getServer().isSameThread()) return;
        Job job = JOBS.get(level.getServer());
        if (job != null && job.controller == controller) release(job,null,false);
    }

    private static boolean supported(AutoBuildSetting setting) {
        return !setting.isDismantleMode() && !setting.isReplaceMode() && !setting.isFlipped()
                && setting.getRepeatCount() == 0 && setting.isNoHatchMode() && setting.getBlocks().isEmpty();
    }

    private static void release(Job job, String message, boolean restoreChecks) {
        MinecraftServer server = job.level.getServer();
        if (!JOBS.remove(server,job)) return;
        job.removeTickets();
        if(job.pipeline!=null) job.pipeline.close();
        try { if(job.preparation!=null) job.preparation.close(); else job.plan.close(); }
        catch (RuntimeException failure) { LOGGER.warn("关闭HK3GTL建造蓝图失败",failure); }
        job.controller.getPatternLock().lock();
        try {
            if (job.controller instanceof Hk3W01HallMachine hall && hall.isTerminalBuilding())
                hall.setTerminalBuilding(false);
            var saved = MultiblockWorldSavedData.getOrCreate(job.level);
            saved.removeMapping(job.controller.getMultiblockState());
            ((com.sirin.hk3gtl.mixin.gtceu.Hk3MultiblockStateAccess)(Object)job.controller.getMultiblockState()).hk3gtl$clean();
            job.controller.getMultiblockState().setError(MultiblockState.UNINIT_ERROR);
            saved.removeAsyncLogic(job.controller);
            if (restoreChecks && job.controllerPresent()) saved.addAsyncLogic(job.controller);
        } catch (RuntimeException failure) {
            LOGGER.error("恢复HK3GTL控制器结构检查失败：{}",job.controller.self().getDefinition().getId(),failure);
        } finally { job.controller.getPatternLock().unlock(); }
        ServerPlayer owner = server.getPlayerList().getPlayer(job.owner);
        if(restoreChecks && job.cursor>=job.plan.size() && !job.dismantle
                && job.controller instanceof com.sirin.hk3gtl.common.machine.hyperion.Hk3HyperionMachine ship)
            ship.requestIntegrityCheck();
        if(restoreChecks && job.cursor>=job.plan.size() && !job.dismantle
                && job.controller instanceof com.sirin.hk3gtl.common.machine.w03.Hk3W03Machine ring)
            ring.requestIntegrityCheck();
        if(restoreChecks && job.cursor>=job.plan.size() && !job.dismantle
                && job.controller instanceof com.sirin.hk3gtl.common.machine.Hk3CommissionMachine wonder)
            wonder.requestIntegrityCheck();
        if (owner != null && message != null) tell(owner, message);
        LOGGER.info("HK3GTL分批建造任务结束：{}，处理{}格，放置{}格", job.controller.self().getDefinition().getId(), job.checked, job.placed);
    }

    private static void tell(Player player, String message) { player.sendSystemMessage(Component.literal(message)); }
    private static final class BuildBoundaryFailure extends RuntimeException {
        private BuildBoundaryFailure(String message) { super(message); }
    }
    private enum Stage { PREPARE, BUILD }

    private static final class Job {
        private final UUID owner;
        private final MultiblockControllerMachine controller;
        private final ServerLevel level;
        private final Hk3BuildPlan plan;
        private final Hk3BuildMaterials materials;
        private final boolean dismantle;
        private final Hk3DismantleOperation removal;
        private final BlockPos center;
        private final Direction front;
        private final Rotation rotation;
        private final long controllerChunk;
        private final BlockPos.MutableBlockPos pos = new BlockPos.MutableBlockPos();
        private final BlockPos.MutableBlockPos lookAheadPos = new BlockPos.MutableBlockPos();
        private volatile Stage stage = Stage.PREPARE;
        private Hk3BuildOrder order;
        private Hk3BuildPreparation preparation;
        private long targetTicketChunk = Long.MIN_VALUE;
        private long waitingTicketChunk = Long.MIN_VALUE;
        private int cursor, checked, placed;
        private boolean paused;
        private boolean controllerTicket;
        private final Hk3BuildProgress notifications=new Hk3BuildProgress();
        private Hk3BuildPipeline<PreparedCell> pipeline;
        private float frameMillis=16;
        private long frameReportTick;
        private int chunkMinX,chunkMinZ,chunkWidth,chunkCount;
        private Hk3BuildChunkWindow chunkWindow;

        private Job(ServerPlayer owner, MultiblockControllerMachine controller, ServerLevel level,
                    Hk3BuildPlan plan, AutoBuildSetting setting) {
            this.owner = owner.getUUID(); this.controller = controller; this.level = level; this.plan = plan;
            this.materials = new Hk3BuildMaterials(owner, setting);
            dismantle = setting.isDismantleMode();
            removal = dismantle ? new Hk3DismantleOperation(owner,controller,setting) : null;
            if (!dismantle && !materials.isSupported()) throw new IllegalArgumentException("终端选项不支持");
            center = controller.getPos().immutable(); front = controller.getFrontFacing();
            rotation = rotation(plan.sourceFacing(), front);
            controllerChunk = ChunkPos.asLong(center.getX() >> 4, center.getZ() >> 4);
        }

        private void validateBounds() {
            BlockPos min = plan.minOffset(), max = plan.maxOffset();
            int lowX = Integer.MAX_VALUE, highX = Integer.MIN_VALUE;
            int lowZ = Integer.MAX_VALUE, highZ = Integer.MIN_VALUE;
            for (int x : new int[]{min.getX(), max.getX()}) for (int z : new int[]{min.getZ(), max.getZ()}) {
                int rx = rotation == Rotation.CLOCKWISE_90 ? -z : rotation == Rotation.CLOCKWISE_180 ? -x
                        : rotation == Rotation.COUNTERCLOCKWISE_90 ? z : x;
                int rz = rotation == Rotation.CLOCKWISE_90 ? x : rotation == Rotation.CLOCKWISE_180 ? -z
                        : rotation == Rotation.COUNTERCLOCKWISE_90 ? -x : z;
                lowX = Math.min(lowX, center.getX() + rx); highX = Math.max(highX, center.getX() + rx);
                lowZ = Math.min(lowZ, center.getZ() + rz); highZ = Math.max(highZ, center.getZ() + rz);
            }
            BlockPos low = new BlockPos(lowX, center.getY() + min.getY(), lowZ);
            BlockPos high = new BlockPos(highX, center.getY() + max.getY(), highZ);
            String heightError = Hk3BuildHeightPlacement.rejection(level.getMinBuildHeight(), level.getMaxBuildHeight(),
                    center.getY(), min.getY(), max.getY());
            if (heightError != null) throw new BuildBoundaryFailure(heightError);
            if (!level.getWorldBorder().isWithinBounds(low) || !level.getWorldBorder().isWithinBounds(high))
                throw new BuildBoundaryFailure("完整蓝图超出世界边界；请将控制器移向世界边界内侧后重试。未放置方块，也未扣除材料。");
            chunkMinX=lowX>>4;chunkMinZ=lowZ>>4;chunkWidth=(highX>>4)-chunkMinX+1;
            chunkCount=Math.multiplyExact(chunkWidth,(highZ>>4)-chunkMinZ+1);
        }

        private void addControllerTicket() {
            controllerTicket = true;
            level.getChunkSource().addRegionTicket(TICKET, new ChunkPos(controllerChunk), 2, center.asLong());
        }

        private boolean controllerPresent() {
            return !controller.isInValid() && controller.getLevel() == level
                    && level.getChunkSource().getChunkNow(center.getX() >> 4,center.getZ() >> 4) != null
                    && MetaMachine.getMachine(level,center) == controller;
        }

        private boolean valid() {
            ServerPlayer player = level.getServer().getPlayerList().getPlayer(owner);
            return player != null && player.isAlive() && player.level() == level
                    && (!plan.creativeOnly() || player.isCreative())
                    && !player.isSpectator() && player.getAbilities().mayBuild
                    && level.mayInteract(player,center)
                    && player.mayUseItemAt(center,Direction.UP,player.getMainHandItem())
                    && controller.getFrontFacing() == front && controller.getUpwardsFacing() == Direction.NORTH
                    && !controller.isFlipped() && controllerPresent();
        }

        private void tick(long deadline) {
            if (paused) return;
            if(stage==Stage.PREPARE) {
                if(preparation==null) preparation=new Hk3BuildPreparation(plan::prepareStep,
                        () -> !dismantle?new Hk3BuildOrder(plan,chunkCount,this::chunkAt):new Hk3BuildOrder(plan),plan::close);
                if(!preparation.done()) {
                    return;
                }
                order=preparation.finish();
                var rotated=new ConcurrentHashMap<BlockState,BlockState>();
                pipeline=new Hk3BuildPipeline<>(plan.size(),at->{
                    int index=dismantle?order.dismantleIndex(at):order.index(at);
                    int x=plan.x(index),y=plan.y(index),z=plan.z(index);
                    int rx=switch(rotation){case CLOCKWISE_90->-z;case CLOCKWISE_180->-x;case COUNTERCLOCKWISE_90->z;default->x;};
                    int rz=switch(rotation){case CLOCKWISE_90->x;case CLOCKWISE_180->-z;case COUNTERCLOCKWISE_90->-x;default->z;};
                    return new PreparedCell(index,center.getX()+rx,center.getY()+y,center.getZ()+rz,
                            rotated.computeIfAbsent(plan.state(index),state->state.rotate(rotation)));
                });
                stage=Stage.BUILD;
                if(!dismantle) chunkWindow=new Hk3BuildChunkWindow(level,center.asLong());
            }
            int tickPlaced=placed;
            int steps = Hk3W01BuildBudget.BUILD_STEPS;
            for (int n = 0; n < steps && System.nanoTime() < deadline; n++) {
                if (JOBS.get(level.getServer()) != this) return;
                if (cursor >= plan.size()) {
                    report();
                    release(this,null,true);
                    return;
                }
                var prepared=pipeline.peek();
                if(prepared==null) { report();return; }
                int index=prepared.index();
                pos.set(prepared.x(),prepared.y(),prepared.z());
                if (chunkWindow!=null) {
                    if(!chunkWindow.ready(cursor,plan.size(),at -> {
                        worldPos(order.index(at),lookAheadPos);
                        return ChunkPos.asLong(lookAheadPos.getX()>>4,lookAheadPos.getZ()>>4);
                    },order::nextChunkIndex)) return;
                } else if (!ensureChunk(pos)) return;
                BlockState expected = prepared.state();
                BlockState present = level.getBlockState(pos);
                if(!dismantle && (Hk3BuildState.matches(present,expected)||pos.equals(center)))
                    if(plan.captureFarView())com.sirin.hk3gtl.common.farview.Hk3FarViewData.observe(level,pos,present);
                if (dismantle) {
                    if (removal.matches(plan,index,pos,present,expected,rotation)) {
                        ServerPlayer ownerPlayer = player();
                        if (!removal.permitted(ownerPlayer,pos)) { pause("无权拆除：" + pos.toShortString()); return; }
                        if (JOBS.get(level.getServer()) != this || !valid()) return;
                        if (level.getBlockState(pos) != present || !removal.matches(plan,index,pos,present,expected,rotation)) continue;
                        if (!removal.remove(ownerPlayer,pos.immutable(),present,materials,
                                () -> JOBS.get(level.getServer()) == this && valid())) {
                            pause("拆除失败或目标已变化：" + pos.toShortString()); return;
                        }
                        placed++;
                    }
                    advance(); continue;
                }
                // 主控已由valid()验证身份与朝向，模板锚点可能仍是原建筑方块。
                if (!pos.equals(center) && !Hk3BuildState.matches(present,expected)) {
                    if (plan.isMachinePartSlot(plan.x(index), plan.y(index), plan.z(index))
                            && MetaMachine.getMachine(level, pos) instanceof IMultiPart) {
                        if(plan.captureFarView())com.sirin.hk3gtl.common.farview.Hk3FarViewData.observe(level,pos,present);
                        advance(); continue;
                    }
                    if (!present.canBeReplaced()) {
                        pause("建造冲突：" + pos.toShortString() + " 已有不可替换方块 "
                                + net.minecraft.core.registries.BuiltInRegistries.BLOCK.getKey(present.getBlock()));
                        return;
                    }
                    ServerPlayer ownerPlayer = player();
                    if (!valid()) { release(this,"控制器或建造者状态已改变，建造已停止。",true); return; }
                    if (!level.mayInteract(ownerPlayer, pos) || !ownerPlayer.mayUseItemAt(pos, Direction.UP, ownerPlayer.getMainHandItem())) {
                        pause("没有权限在 " + pos.toShortString() + " 建造。"); return;
                    }
                    Hk3BuildMaterials.Reservation reservation = plan.creativeOnly()
                            ? materials.reserveCreativeBlueprint() : materials.reserve(expected, plan.tag(index));
                    if (reservation == null) { pause("缺少精确蓝图材料或当前终端材料选项不兼容；停在 " + pos.toShortString() + "。"); return; }
                    try (reservation) {
                        if (JOBS.get(level.getServer()) != this) return;
                        if (level.getBlockState(pos) != present) { pause("扣料期间目标位置改变，已退还该格材料。"); return; }
                        BlockSnapshot before = BlockSnapshot.create(level.dimension(), level, pos.immutable());
                        String rollbackMessage = null;
                        RuntimeException placementFailure = null;
                        boolean stop = false;
                        try {
                            if (!level.setBlock(pos, expected, Block.UPDATE_CLIENTS | Block.UPDATE_KNOWN_SHAPE)) {
                                rollbackMessage = "方块放置失败，已退还该格材料。";
                            } else if (ForgeEventFactory.onBlockPlace(ownerPlayer, before, Direction.UP)) {
                                rollbackMessage = "放置保护拒绝该位置，已退还该格材料。";
                            } else if (JOBS.get(level.getServer()) != this || !valid()) {
                                rollbackMessage = "建造在放置回调中被取消或控制器状态改变，该格已回退。";
                                stop = true;
                            } else if (!Hk3BuildState.matches(level.getBlockState(pos),expected))
                                rollbackMessage = "放置后方块状态不符，已退还该格材料。";
                            else if (plan.creativeOnly() && plan.tag(index) != null) {
                                var entity = level.getBlockEntity(pos);
                                if (entity == null) throw new IllegalStateException("原稿实体未创建：" + pos);
                                var tag = plan.tag(index).copy();
                                tag.putString("id", net.minecraft.core.registries.BuiltInRegistries.BLOCK_ENTITY_TYPE
                                        .getKey(entity.getType()).toString());
                                tag.putInt("x", pos.getX()); tag.putInt("y", pos.getY()); tag.putInt("z", pos.getZ());
                                tag = (net.minecraft.nbt.CompoundTag) level.getServer().getFixerUpper().update(
                                        net.minecraft.util.datafix.fixes.References.BLOCK_ENTITY,
                                        new com.mojang.serialization.Dynamic<>(net.minecraft.nbt.NbtOps.INSTANCE, tag),
                                        plan.sourceDataVersion(), net.minecraft.SharedConstants.getCurrentVersion()
                                                .getDataVersion().getVersion()).getValue();
                                entity.load(tag);
                                entity.setChanged();
                                level.sendBlockUpdated(pos, expected, expected, Block.UPDATE_CLIENTS);
                            }
                        } catch (RuntimeException failure) {
                            placementFailure = failure;
                        }
                        if (rollbackMessage != null || placementFailure != null) {
                            if (!rollbackOrRetain(before,reservation,placementFailure)) return;
                            if (placementFailure != null) throw placementFailure;
                            if (stop) release(this,rollbackMessage,true);
                            else pause(rollbackMessage);
                            return;
                        }
                        reservation.commit(); placed++;
                        if(plan.captureFarView())com.sirin.hk3gtl.common.farview.Hk3FarViewData.observe(level,pos,expected);
                        if(placed-tickPlaced >= Hk3W01BuildBudget.placementLimit(frameMillis)) {
                            advance();report();return;
                        }
                    }
                }
                advance();
            }
            report();
        }

        private record PreparedCell(int index,int x,int y,int z,BlockState state) {}
        private void advance() { pipeline.advance();cursor++;checked++; }

        private boolean ensureChunk(BlockPos target) {
            long chunk = ChunkPos.asLong(target.getX() >> 4, target.getZ() >> 4);
            if (chunk == controllerChunk) {
                if (waitingTicketChunk != Long.MIN_VALUE) removeTicket(waitingTicketChunk);
                waitingTicketChunk = Long.MIN_VALUE;
                if (targetTicketChunk != Long.MIN_VALUE) removeTicket(targetTicketChunk);
                targetTicketChunk = Long.MIN_VALUE;
                return level.getChunkSource().getChunkNow(target.getX() >> 4, target.getZ() >> 4) != null;
            }
            if (chunk != targetTicketChunk) {
                if (waitingTicketChunk != chunk) {
                    if (waitingTicketChunk != Long.MIN_VALUE) removeTicket(waitingTicketChunk);
                    waitingTicketChunk = chunk;
                    level.getChunkSource().addRegionTicket(TICKET, new ChunkPos(chunk), 2, center.asLong());
                }
                if (level.getChunkSource().getChunkNow(target.getX() >> 4, target.getZ() >> 4) == null) return false;
                if (targetTicketChunk != Long.MIN_VALUE) removeTicket(targetTicketChunk);
                targetTicketChunk = waitingTicketChunk;
                waitingTicketChunk = Long.MIN_VALUE;
            }
            return level.getChunkSource().getChunkNow(target.getX() >> 4, target.getZ() >> 4) != null;
        }

        private void worldPos(int index, BlockPos.MutableBlockPos out) {
            int x = plan.x(index), y = plan.y(index), z = plan.z(index);
            switch (rotation) {
                case CLOCKWISE_90 -> out.set(center.getX() - z, center.getY() + y, center.getZ() + x);
                case CLOCKWISE_180 -> out.set(center.getX() - x, center.getY() + y, center.getZ() - z);
                case COUNTERCLOCKWISE_90 -> out.set(center.getX() + z, center.getY() + y, center.getZ() - x);
                default -> out.set(center.getX() + x, center.getY() + y, center.getZ() + z);
            }
        }

        // 后台排序只读蓝图和已冻结的坐标参数，不触碰世界或共享MutableBlockPos。
        private int chunkAt(int index) {
            int x=plan.x(index),z=plan.z(index);
            int rx=switch(rotation){case CLOCKWISE_90->-z;case CLOCKWISE_180->-x;case COUNTERCLOCKWISE_90->z;default->x;};
            int rz=switch(rotation){case CLOCKWISE_90->x;case CLOCKWISE_180->-z;case COUNTERCLOCKWISE_90->-x;default->z;};
            return (((center.getZ()+rz)>>4)-chunkMinZ)*chunkWidth+((center.getX()+rx)>>4)-chunkMinX;
        }

        private void pause(String message) {
            if (JOBS.get(level.getServer()) != this) return;
            paused = true;
            removeTargetTickets();
            ServerPlayer ownerPlayer = player();
            if (ownerPlayer != null) tell(ownerPlayer, message + " 再次使用终端继续。");
        }
        private boolean rollbackOrRetain(BlockSnapshot snapshot, Hk3BuildMaterials.Reservation reservation,
                                         RuntimeException original) {
            RuntimeException rollback;
            try {
                if (snapshot.restore(true,false)) return true;
                rollback = new IllegalStateException("建造放置快照回退失败：" + snapshot.getPos());
            } catch (RuntimeException failure) { rollback = failure; }
            // 回退失败可能留下目标方块；结算预扣材料，不能再由close退款。
            reservation.commit();
            if (original != null && original != rollback) original.addSuppressed(rollback);
            LOGGER.error("HK3GTL建造回退失败，材料保留扣除，需要人工核对：{}",snapshot.getPos(),original == null ? rollback : original);
            ServerPlayer ownerPlayer = player();
            try {
                if (ownerPlayer != null) tell(ownerPlayer,"回退失败，材料保留扣除，需要人工核对：" + snapshot.getPos().toShortString());
            } finally { release(this,null,true); }
            return false;
        }
        private ServerPlayer player() { return level.getServer().getPlayerList().getPlayer(owner); }
        private void report() {
            ServerPlayer ownerPlayer = player();
            if (ownerPlayer != null) notifications.report(checked,plan.size(),
                    percent->tell(ownerPlayer,"HK3GTL终端进度："+percent+"%"+(percent==100
                            ?dismantle?"；拆除处理完成，主控及不匹配方块保留。":"；实体处理完成，成型须通过结构检查。":"")));
        }
        private void removeTickets() {
            if (controllerTicket) { controllerTicket = false; removeTicket(controllerChunk); }
            removeTargetTickets();
        }
        private void removeTargetTickets() {
            if(chunkWindow!=null) chunkWindow.close();
            long target = targetTicketChunk, waiting = waitingTicketChunk;
            targetTicketChunk = Long.MIN_VALUE;
            waitingTicketChunk = Long.MIN_VALUE;
            if (target != Long.MIN_VALUE) removeTicket(target);
            if (waiting != Long.MIN_VALUE && waiting != target) removeTicket(waiting);
        }
        private void removeTicket(long chunk) {
            try { level.getChunkSource().removeRegionTicket(TICKET, new ChunkPos(chunk), 2, center.asLong()); }
            catch (RuntimeException failure) { LOGGER.warn("释放HK3GTL建造区块票据失败：{}",chunk,failure); }
        }
    }

    public static Rotation rotation(Direction source, Direction target) {
        for (Rotation candidate : Rotation.values()) if (candidate.rotate(source) == target) return candidate;
        throw new IllegalArgumentException("不能将蓝图主控朝向旋转至目标方向");
    }
}
