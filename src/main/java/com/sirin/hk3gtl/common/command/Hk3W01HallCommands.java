package com.sirin.hk3gtl.common.command;

import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.sirin.hk3gtl.common.machine.Hk3W01HallMachine;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3W01HallPattern;
import it.unimi.dsi.fastutil.longs.LongOpenHashSet;
import net.minecraft.commands.Commands;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.arguments.coordinates.BlockPosArgument;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.ChunkPos;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.level.ChunkEvent;
import net.minecraftforge.event.server.ServerStoppingEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.loading.FMLPaths;

/** 专用新存档按每tick两区块准备完整W01；不放置建筑、不改isFormed、不跳过Pattern。 */
/**
 * 【变更记录 #1】2026-10-30 00:08:31（第1次备注 · 内测5修订183）
 * 删除：旧实体数固定文本；新增：无；修改：朝北测试加载使用西入口零转映射，数量读取当前资源。
 * 用途：限定测试命令与新主控、实际蓝图一致；不放置方块，不扩大测试世界或玩家权限。
 */
@Mod.EventBusSubscriber(modid="hk3gtl", bus=Mod.EventBusSubscriber.Bus.FORGE)
public final class Hk3W01HallCommands {
    private static ServerLevel level;
    private static ServerPlayer operator;
    private static long[] pending;
    private static int cursor;
    private static final LongOpenHashSet ADDED = new LongOpenHashSet();
    private Hk3W01HallCommands() {}

    @SubscribeEvent public static void commands(RegisterCommandsEvent event) {
        var root = Commands.literal("hk3w01").requires(s -> s.hasPermission(2));
        root.then(Commands.literal("load").then(Commands.argument("controller", BlockPosArgument.blockPos()).executes(c -> {
            var source = c.getSource();
            if (!allowed(source) || pending != null) { source.sendFailure(Component.literal("需要增强版专用hk3gtl-w01-azu-runtime-*创造测试存档，且不能重复启动加载。")); return 0; }
            if (level != null && level != source.getLevel()) release();
            level = source.getLevel(); operator = source.getPlayer();
            pending = Hk3W01HallPattern.requiredChunks(BlockPosArgument.getBlockPos(c, "controller"),
                    Hk3W01HallPattern.turnForFront(net.minecraft.core.Direction.NORTH)).toLongArray();
            cursor = 0;
            source.sendSuccess(() -> Component.literal("W01开始分批加载实际建筑占用的" + pending.length + "个区块（朝北）；不加载整片包围盒。"), false);
            return 1;
        })));
        root.then(Commands.literal("status").then(Commands.argument("controller", BlockPosArgument.blockPos()).executes(c -> {
            var source = c.getSource();
            if (!allowed(source)) return 0;
            var machine = MetaMachine.getMachine(source.getLevel(), BlockPosArgument.getLoadedBlockPos(c, "controller"));
            if (!(machine instanceof Hk3W01HallMachine hall)) { source.sendFailure(Component.literal("此处不是W01礼堂控制器。")); return 0; }
            source.sendSuccess(() -> Component.literal("W01真实GT状态：" + (hall.isFormed() ? "已成型" : "未成型")
                    + "；目标实体" + Hk3W01HallPattern.layout().cells().length + "格；无接口；空气自由。"), false);
            return hall.isFormed() ? 1 : 0;
        })));
        root.then(Commands.literal("unload").executes(c -> {
            if (!allowed(c.getSource())) return 0;
            release(); c.getSource().sendSuccess(() -> Component.literal("已释放本轮W01加载票据，未删除建筑。"), false); return 1;
        }));
        event.getDispatcher().register(root);
    }

    private static boolean allowed(CommandSourceStack source) {
        return source.getEntity() instanceof ServerPlayer player && player.isCreative() && player.hasPermissions(2)
                && source.getLevel() == source.getServer().overworld()
                && source.getServer().getWorldData().getLevelName().startsWith("hk3gtl-w01-azu-runtime-")
                && source.getServer().getWorldData().getAllowCommands()
                && FMLPaths.GAMEDIR.get().toAbsolutePath().normalize().equals(java.nio.file.Path.of(
                    "C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft").toAbsolutePath().normalize());
    }

    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || pending == null || level == null) return;
        for (int n = 0; n < 2 && cursor < pending.length; n++, cursor++) {
            long key = pending[cursor];
            if (!level.getForcedChunks().contains(key)) { level.setChunkForced(ChunkPos.getX(key), ChunkPos.getZ(key), true); ADDED.add(key); }
            level.getChunk(ChunkPos.getX(key), ChunkPos.getZ(key));
        }
        if (cursor == pending.length) {
            if (operator != null) operator.sendSystemMessage(Component.literal("W01实际占用区块已全部加载：" + cursor + "。等待GT逐格检查并打开控制器核验。"));
            pending = null; operator = null;
        }
    }
    @SubscribeEvent public static void stopping(ServerStoppingEvent event) { release(); }
    @SubscribeEvent public static void chunkUnloaded(ChunkEvent.Unload event) {
        if (event.getLevel() instanceof ServerLevel level)
            Hk3W01HallMachine.onBuildingChunkUnload(level, event.getChunk().getPos().toLong());
    }
    private static void release() {
        if (level != null) for (long key : ADDED) level.setChunkForced(ChunkPos.getX(key), ChunkPos.getZ(key), false);
        ADDED.clear(); level = null; pending = null; operator = null; cursor = 0;
    }
}
