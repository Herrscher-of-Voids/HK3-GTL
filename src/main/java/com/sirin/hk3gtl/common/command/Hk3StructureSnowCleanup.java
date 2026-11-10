package com.sirin.hk3gtl.common.command;

import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.mojang.logging.LogUtils;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LargeStructurePattern;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.server.ServerStoppingEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/** 玩家显式启动的分批除雪；不加载新区块、不删除真实建材，沿用原版破坏权限事件。 */
@Mod.EventBusSubscriber(modid="hk3gtl")
public final class Hk3StructureSnowCleanup {
    private static final Map<MinecraftServer, Job> JOBS = new ConcurrentHashMap<>();
    private Hk3StructureSnowCleanup() {}

    public static int start(ServerPlayer player, BlockPos pos) {
        if (!player.isCreative() || !player.hasPermissions(2) || !player.getAbilities().mayBuild
                || !player.serverLevel().mayInteract(player, pos)) {
            tell(player, "除雪需要有建造权限的创造模式OP。"); return 0;
        }
        if (!(MetaMachine.getMachine(player.serverLevel(), pos) instanceof Hk3WorkableMultiblockMachine machine)
                || !(machine.getPattern() instanceof Hk3LargeStructurePattern pattern)
                || machine.getFrontFacing().getAxis().isVertical() || machine.getUpwardsFacing()!=Direction.NORTH || machine.isFlipped()) {
            tell(player, "请指定水平放置的HK3GTL批准巨构控制器。"); return 0;
        }
        Job job = new Job(player, machine, pattern);
        if (JOBS.putIfAbsent(player.server, job) != null) {
            tell(player, "已有一项巨构除雪任务，请等待结束。"); return 0;
        }
        tell(player, "开始分批清理该巨构表面雪层；未加载区域会跳过，实体雪块和建筑方块保留。");
        return 1;
    }

    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        Job job = JOBS.get(event.getServer());
        if (job == null) return;
        try { if (job.step()) JOBS.remove(event.getServer(), job); }
        catch (RuntimeException failure) {
            JOBS.remove(event.getServer(), job);
            LogUtils.getLogger().error("巨构除雪任务失败", failure);
            var player = event.getServer().getPlayerList().getPlayer(job.owner);
            if (player != null) tell(player, "除雪已停止，已清理部分保留；详见日志。");
        }
    }
    @SubscribeEvent public static void stopping(ServerStoppingEvent event) { JOBS.remove(event.getServer()); }
    private static void tell(ServerPlayer player, String text) { player.sendSystemMessage(Component.literal(text)); }

    private static final class Job {
        final MinecraftServer server;
        final UUID owner;
        final Hk3WorkableMultiblockMachine machine;
        final Hk3LargeStructurePattern pattern;
        final Direction facing;
        int cursor, removed, unloaded, denied;
        Job(ServerPlayer player, Hk3WorkableMultiblockMachine machine, Hk3LargeStructurePattern pattern) {
            server=player.server; owner=player.getUUID(); this.machine=machine; this.pattern=pattern; facing=machine.getFrontFacing();
        }
        boolean step() {
            var player=server.getPlayerList().getPlayer(owner);
            var level=machine.getLevel();
            if (player==null) return true;
            if (player.level()!=level || !player.isCreative() || !player.hasPermissions(2)
                    || !player.getAbilities().mayBuild || machine.isInValid() || machine.getFrontFacing()!=facing
                    || machine.getUpwardsFacing()!=Direction.NORTH || machine.isFlipped()
                    || machine.getPattern()!=pattern || !level.isLoaded(machine.getPos())
                    || MetaMachine.getMachine(level,machine.getPos())!=machine) {
                tell(player,"除雪已停止：玩家或控制器状态改变。"); return true;
            }
            long until=System.nanoTime()+1_000_000;
            for (int count=0; cursor<pattern.snowSurfaceCandidates() && count<4096 && System.nanoTime()<until; count++,cursor++) {
                var surface=pattern.snowSurface(cursor,machine.getPos(),facing);
                if (surface==null) continue;
                BlockPos pos=surface.support().above();
                if (level.isOutsideBuildHeight(pos)) continue;
                if (!level.hasChunkAt(pos)) { unloaded++; continue; }
                var support=level.getBlockState(surface.support());
                if (support!=surface.expected() && support!=surface.active()) continue;
                if (!level.getBlockState(pos).is(Blocks.SNOW)) continue;
                if (!level.mayInteract(player,pos) || !player.mayUseItemAt(pos,Direction.UP,player.getMainHandItem())
                        || !player.gameMode.destroyBlock(pos)) { denied++; continue; }
                removed++;
            }
            if (cursor<pattern.snowSurfaceCandidates()) return false;
            tell(player,"巨构除雪结束：清除 "+removed+" 处雪层，跳过未加载表面 "+unloaded+" 处，受保护 "+denied+" 处。");
            return true;
        }
    }
}
