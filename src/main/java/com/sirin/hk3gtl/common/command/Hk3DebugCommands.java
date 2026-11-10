package com.sirin.hk3gtl.common.command;


/**
 * 【文件职责】
 * - 维护 Hk3DebugCommands 的核心功能实现。
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
 */
/**
 * 【变更记录 #1】2026-09-29 17:51:46（内测5修订93）
 * - 删除：旧正文活动引用被审核原文替代；保留历史资源和存档。
 * - 新增／修改：调试重开清除新检查点；正式终审读取本存档玩家IF账本，不使用旧跨存档掩码。
 * - 用途：接通审核正文；其他系统触发及归属不据此宣称完成。
 */
import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.dimension.Hk3Dimensions;
import com.sirin.hk3gtl.common.dimension.Hk3GraduationData;
import com.sirin.hk3gtl.common.entity.Hk3Entities;
import com.sirin.hk3gtl.common.entity.VoidQueenSirinEntity;
import com.sirin.hk3gtl.common.gaze.Hk3GazeManager;
import com.sirin.hk3gtl.common.dialogue.DialogueSessionManager;
import com.sirin.hk3gtl.common.dialogue.SirinIfProgressStore;
import com.sirin.hk3gtl.common.dialogue.definition.SirinDialogueDefinitions;
import com.sirin.hk3gtl.common.narrative.Hk3NarrativeLog;
import com.sirin.hk3gtl.common.narrative.Hk3NarrativeNodes;
import com.sirin.hk3gtl.common.research.Hk3ResearchManager;
import com.sirin.hk3gtl.common.research.Hk3ResearchNodes;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.ArrayList;
import java.util.List;

@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
/** 【变更记录 #2】2026-09-30 23:34:26（修订119）：删除：世界级结果对所有玩家的隐式授权；新增/修改：毕业/传送/彩蛋/调试改为查询当前玩家，实体避免在已有坏结局演出时开启新会面；用途：个人结算不覆盖其他玩家，未完成的资格采集仍单独接入。 */
/** 【变更记录 #3】2026-10-01 16:49:18（修订135）：删除调试触发正文直接走正式毕业的路径；新增个人准入账本随本人调试重置；修改trigger_dialogue为审核正文预览；用途：继续支持测试文本和演出，不产生真实资格或消耗正式IF五选。 */
public class Hk3DebugCommands {

    private static final String TAG = "§a[HK3DEBUG] §f";
    private static final String ERR = "§c[HK3DEBUG] ";
    private static final String DIALOGUE_DONE_TAG = "hk3gtl_dialogue_done";

    @SubscribeEvent
    public static void onRegisterCommands(RegisterCommandsEvent event) {
        register(event.getDispatcher());
    }

    private static void register(CommandDispatcher<CommandSourceStack> dispatcher) {
        dispatcher.register(Commands.literal("hk3debug")
                .requires(src -> src.hasPermission(2))

                // ══ 对话 & 维度 ══
                .then(Commands.literal("reset_dialogue").executes(ctx -> resetDialogue(ctx.getSource())))
                .then(Commands.literal("trigger_dialogue").executes(ctx -> triggerDialogue(ctx.getSource())))
                .then(Commands.literal("tp_imaginary").executes(ctx -> tpImaginary(ctx.getSource())))
                .then(Commands.literal("force_tp_imaginary").executes(ctx -> forceTpImaginary(ctx.getSource())))
                .then(Commands.literal("reset_if_progress").executes(ctx -> resetIfProgress(ctx.getSource())))
                .then(Commands.literal("spawn_sirin").executes(ctx -> spawnSirin(ctx.getSource())))

                // ══ 状态查询 ══
                .then(Commands.literal("status").executes(ctx -> queryStatus(ctx.getSource())))

                // ══ 研究系统 ══
                .then(Commands.literal("research_status").executes(ctx -> researchStatus(ctx.getSource())))
                .then(Commands.literal("research_reset").executes(ctx -> researchReset(ctx.getSource())))
                .then(Commands.literal("research_complete")
                        .then(Commands.argument("id", StringArgumentType.string())
                                .executes(ctx -> researchComplete(ctx.getSource(), StringArgumentType.getString(ctx, "id")))))

                // ══ 叙事系统 ══
                .then(Commands.literal("narrative_status").executes(ctx -> narrativeStatus(ctx.getSource())))
                .then(Commands.literal("narrative_reset").executes(ctx -> narrativeReset(ctx.getSource())))
                .then(Commands.literal("narrative_unlock_all").executes(ctx -> narrativeUnlockAll(ctx.getSource())))

                // ══ 事件系统 ══
                .then(Commands.literal("event_status").executes(ctx -> eventStatus(ctx.getSource())))
                .then(Commands.literal("event_reset").executes(ctx -> eventReset(ctx.getSource())))
                .then(Commands.literal("event_trigger")
                        .then(Commands.argument("id", StringArgumentType.string())
                                .executes(ctx -> eventTrigger(ctx.getSource(), StringArgumentType.getString(ctx, "id")))))

                // ══ 注视度 ══
                .then(Commands.literal("gaze_query").executes(ctx -> gazeQuery(ctx.getSource())))
                .then(Commands.literal("gaze_set")
                        .then(Commands.argument("level", IntegerArgumentType.integer(0))
                                .executes(ctx -> gazeSet(ctx.getSource(), IntegerArgumentType.getInteger(ctx, "level")))))

                // ══ 数据转储 ══
                .then(Commands.literal("data_dump").executes(ctx -> dataDump(ctx.getSource(), "hk3gtl_"))
                        .then(Commands.argument("prefix", StringArgumentType.string())
                                .executes(ctx -> dataDump(ctx.getSource(), StringArgumentType.getString(ctx, "prefix")))))

                // ══ 全部重置 ══
                .then(Commands.literal("reset_all").executes(ctx -> resetAll(ctx.getSource())))
        );
    }

    // ════════════════════════════════════════════
    //  对话 & 维度（原有）
    // ════════════════════════════════════════════

    private static int resetDialogue(CommandSourceStack source) {
        ServerPlayer player = source.getPlayer();
        if (player == null) return 0;

        player.getPersistentData().remove(DIALOGUE_DONE_TAG);
        player.getPersistentData().remove("hk3gtl_finale_checkpoint_v5");
        Hk3GraduationData.get(player.serverLevel()).resetForDebug(player.getUUID());
        com.sirin.hk3gtl.common.finale.Hk3FinaleData.get(player.server).change(l->{l.resetForDebug(player.getUUID());return true;});
        com.sirin.hk3gtl.common.badending.Hk3BadEndingData.get(player.serverLevel()).resetForDebug(player.getUUID());

        DialogueSessionManager.onPlayerDisconnect(player.getUUID());

        ServerLevel imaginary = player.server.getLevel(Hk3Dimensions.IMAGINARY);
        if (imaginary != null) {
            VoidQueenSirinEntity.ensurePlatformAndEntity(imaginary);
            VoidQueenSirinEntity.respawnSirinFresh(imaginary);
        }

        source.sendSuccess(() -> Component.literal(TAG + "对话状态已重置（persistentData + 毕业标记 + 西琳实体已重生）。"), true);
        return 1;
    }

    private static int triggerDialogue(CommandSourceStack source) {
        ServerPlayer player = source.getPlayer();
        if (player == null) return 0;

        int availableMask = com.sirin.hk3gtl.common.dialogue.Hk3FinaleIfData.get(player).selectedMask(player.getUUID());
        boolean ok = DialogueSessionManager.startDialogue(player, com.sirin.hk3gtl.common.dialogue.definition.Hk3ApprovedDialogues.FINALE_PREVIEW, availableMask);
        source.sendSuccess(() -> Component.literal(TAG + (ok ? "终局正文预览已启动；不授予正式资格、不毕业、不占用IF五选。" : "预览启动失败（可能已有活跃对话）。")), true);
        return ok?1:0;
    }

    private static int tpImaginary(CommandSourceStack source) {
        return tpImaginaryInternal(source, false);
    }

    private static int forceTpImaginary(CommandSourceStack source) {
        return tpImaginaryInternal(source, true);
    }

    private static int tpImaginaryInternal(CommandSourceStack source, boolean bypassGraduationCheck) {
        ServerPlayer player = source.getPlayer();
        if (player == null) return 0;

        ServerLevel imaginary = player.server.getLevel(Hk3Dimensions.IMAGINARY);
        if (imaginary == null) {
            source.sendFailure(Component.literal(ERR + "虚数维度未加载。"));
            return 0;
        }

        Hk3GraduationData graduationData = Hk3GraduationData.get(player.serverLevel());
        if (!bypassGraduationCheck && graduationData.isGraduated(player.getUUID())) {
            source.sendFailure(Component.literal(ERR + "当前玩家已通过终审，请使用 /hk3debug force_tp_imaginary 强制重测。"));
            return 0;
        }
        if (bypassGraduationCheck) {
            graduationData.resetForDebug(player.getUUID());
            com.sirin.hk3gtl.common.finale.Hk3FinaleData.get(player.server).change(l->{l.resetForDebug(player.getUUID());return true;});
        com.sirin.hk3gtl.common.badending.Hk3BadEndingData.get(player.serverLevel()).resetForDebug(player.getUUID());
        }

        VoidQueenSirinEntity.ensurePlatformAndEntity(imaginary);
        VoidQueenSirinEntity.respawnSirinFresh(imaginary);
        player.getPersistentData().remove(DIALOGUE_DONE_TAG);
        player.setGameMode(net.minecraft.world.level.GameType.ADVENTURE);
        player.teleportTo(imaginary,
                Hk3Dimensions.SPAWN_X + 0.5, Hk3Dimensions.SPAWN_Y, Hk3Dimensions.SPAWN_Z + 0.5, 0f, 0f);
        String msg = bypassGraduationCheck ? "已强制重置毕业状态并传送至虚数维度。" : "已传送至虚数维度。";
        source.sendSuccess(() -> Component.literal(TAG + msg), true);
        return 1;
    }

    private static int resetIfProgress(CommandSourceStack source) {
        ServerPlayer player = source.getPlayer();
        if (player == null) return 0;
        SirinIfProgressStore.resetForPlayer(player);
        source.sendSuccess(() -> Component.literal(TAG + "已重置当前玩家的 10 条 IF 已读进度。"), true);
        return 1;
    }

    private static int spawnSirin(CommandSourceStack source) {
        ServerPlayer player = source.getPlayer();
        if (player == null) return 0;

        ServerLevel level = player.serverLevel();
        if (level.dimension() == Hk3Dimensions.IMAGINARY) {
            VoidQueenSirinEntity.removeAllSirins(level);
        }
        VoidQueenSirinEntity sirin = Hk3Entities.VOID_QUEEN_SIRIN.get().create(level);
        if (sirin == null) { source.sendFailure(Component.literal(ERR + "实体创建失败。")); return 0; }

        sirin.setPos(player.getX(), player.getY(), player.getZ());
        sirin.setYRot(player.getYRot() + 180);
        level.addFreshEntity(sirin);
        source.sendSuccess(() -> Component.literal(TAG + "西琳已召唤。"), true);
        return 1;
    }

    // ════════════════════════════════════════════
    //  综合状态查询
    // ════════════════════════════════════════════

    private static int queryStatus(CommandSourceStack source) {
        ServerPlayer player = source.getPlayer();
        if (player == null) return 0;
        CompoundTag data = player.getPersistentData();

        boolean dialogueDone = data.getBoolean(DIALOGUE_DONE_TAG);
        boolean graduated = Hk3GraduationData.get(player.serverLevel()).isGraduated(player.getUUID());
        int gazeLevel = data.getInt("hk3gtl_gaze_level");

        int resCount = countByPrefix(data, "hk3gtl_res_");
        int narCount = countByPrefix(data, "hk3gtl_nar_");
        int evtCount = countByPrefix(data, "hk3gtl_evt_");

        source.sendSuccess(() -> Component.literal(
                "§6§l══ HK3GTL 状态 ══\n" +
                TAG + "对话完成: " + bool(dialogueDone) + "\n" +
                TAG + "个人终审通过: " + bool(graduated) + "\n" +
                TAG + "注视度: §e" + gazeLevel + "\n" +
                TAG + "研究完成: §e" + resCount + " §f个\n" +
                TAG + "叙事解锁: §e" + narCount + " §f个\n" +
                TAG + "事件触发: §e" + evtCount + " §f个"
        ), false);
        return 1;
    }

    // ════════════════════════════════════════════
    //  研究系统
    // ════════════════════════════════════════════

    private static int researchStatus(CommandSourceStack source) {
        ServerPlayer player = source.getPlayer();
        if (player == null) return 0;

        StringBuilder sb = new StringBuilder("§6§l══ 研究状态 ══\n");
        for (var node : Hk3ResearchNodes.ordered()) {
            boolean done = Hk3ResearchManager.isCompleted(player, node.id());
            sb.append(done ? "§a✓ " : "§c✗ ").append("§f").append(node.id()).append("\n");
        }
        source.sendSuccess(() -> Component.literal(sb.toString()), false);
        return 1;
    }

    private static int researchReset(CommandSourceStack source) {
        ServerPlayer player = source.getPlayer();
        if (player == null) return 0;
        int count = clearByPrefix(player.getPersistentData(), "hk3gtl_res_");
        player.getPersistentData().remove("hk3gtl_total_fails");
        player.getPersistentData().remove("hk3gtl_unlucky_egg");
        Hk3ResearchManager.syncClientResearchState(player);
        source.sendSuccess(() -> Component.literal(TAG + "已清除 " + count + " 条研究记录。"), true);
        return 1;
    }

    private static int researchComplete(CommandSourceStack source, String id) {
        ServerPlayer player = source.getPlayer();
        if (player == null) return 0;
        Hk3ResearchManager.forceCompleteResearch(player, id);
        source.sendSuccess(() -> Component.literal(TAG + "已强制完成研究: " + id), true);
        return 1;
    }

    // ════════════════════════════════════════════
    //  叙事系统
    // ════════════════════════════════════════════

    private static int narrativeStatus(CommandSourceStack source) {
        ServerPlayer player = source.getPlayer();
        if (player == null) return 0;

        var unlocked = Hk3NarrativeLog.allUnlocked(player);
        var all = Hk3NarrativeNodes.all();
        StringBuilder sb = new StringBuilder("§6§l══ 叙事状态 ══ §f(" + unlocked.size() + "/" + all.size() + ")\n");
        for (var node : all) {
            boolean done = unlocked.contains(node.id());
            sb.append(done ? "§a✓ " : "§c✗ ").append("§7[").append(node.faction()).append("] ")
              .append("§f").append(node.id()).append("\n");
        }
        source.sendSuccess(() -> Component.literal(sb.toString()), false);
        return 1;
    }

    private static int narrativeReset(CommandSourceStack source) {
        ServerPlayer player = source.getPlayer();
        if (player == null) return 0;
        int count = clearByPrefix(player.getPersistentData(), "hk3gtl_nar_");
        source.sendSuccess(() -> Component.literal(TAG + "已清除 " + count + " 条叙事记录。"), true);
        return 1;
    }

    private static int narrativeUnlockAll(CommandSourceStack source) {
        ServerPlayer player = source.getPlayer();
        if (player == null) return 0;
        int count = 0;
        for (var node : Hk3NarrativeNodes.all()) {
            if (Hk3NarrativeLog.unlock(player, node.id())) count++;
        }
        int c = count;
        source.sendSuccess(() -> Component.literal(TAG + "已解锁 " + c + " 条叙事。"), true);
        return 1;
    }

    // ════════════════════════════════════════════
    //  事件系统
    // ════════════════════════════════════════════

    private static int eventStatus(CommandSourceStack source) {
        ServerPlayer player = source.getPlayer();
        if (player == null) return 0;
        CompoundTag data = player.getPersistentData();

        List<String> triggered = new ArrayList<>();
        for (String key : data.getAllKeys()) {
            if (key.startsWith("hk3gtl_evt_") && data.getBoolean(key)) {
                triggered.add(key.substring("hk3gtl_evt_".length()));
            }
        }
        triggered.sort(String::compareTo);

        StringBuilder sb = new StringBuilder("§6§l══ 事件状态 ══ §f(已触发 " + triggered.size() + " 个)\n");
        for (String id : triggered) {
            sb.append("§a✓ §f").append(id).append("\n");
        }
        source.sendSuccess(() -> Component.literal(sb.toString()), false);
        return 1;
    }

    private static int eventReset(CommandSourceStack source) {
        ServerPlayer player = source.getPlayer();
        if (player == null) return 0;
        int count = clearByPrefix(player.getPersistentData(), "hk3gtl_evt_");
        source.sendSuccess(() -> Component.literal(TAG + "已清除 " + count + " 条事件记录。"), true);
        return 1;
    }

    private static int eventTrigger(CommandSourceStack source, String eventId) {
        ServerPlayer player = source.getPlayer();
        if (player == null) return 0;
        player.getPersistentData().putBoolean("hk3gtl_evt_" + eventId, true);
        com.sirin.hk3gtl.common.research.Hk3ResearchManager.onEventTriggered(player, eventId);
        com.sirin.hk3gtl.common.narrative.Hk3NarrativeManager.onEventTriggered(player, eventId);
        source.sendSuccess(() -> Component.literal(TAG + "已触发事件: " + eventId), true);
        return 1;
    }

    // ════════════════════════════════════════════
    //  注视度
    // ════════════════════════════════════════════

    private static int gazeQuery(CommandSourceStack source) {
        ServerPlayer player = source.getPlayer();
        if (player == null) return 0;
        int level = player.getPersistentData().getInt("hk3gtl_gaze_level");
        source.sendSuccess(() -> Component.literal(TAG + "当前注视度: §e" + level + " §7(阈值: 100/500/800)"), false);
        return 1;
    }

    private static int gazeSet(CommandSourceStack source, int level) {
        ServerPlayer player = source.getPlayer();
        if (player == null) return 0;
        // 统一走 Hk3GazeManager.setGaze：保证 min/max 夹取与阈值观察器触发，避免直写 NBT 绕过业务规则。
        Hk3GazeManager.setGaze(player, level);
        int actual = Hk3GazeManager.getGaze(player);
        source.sendSuccess(() -> Component.literal(TAG + "注视度已设为: §e" + actual), true);
        return 1;
    }

    // ════════════════════════════════════════════
    //  数据转储
    // ════════════════════════════════════════════

    private static int dataDump(CommandSourceStack source, String prefix) {
        ServerPlayer player = source.getPlayer();
        if (player == null) return 0;
        CompoundTag data = player.getPersistentData();

        List<String> entries = new ArrayList<>();
        for (String key : data.getAllKeys()) {
            if (key.startsWith(prefix)) {
                entries.add(key + " = " + data.get(key));
            }
        }
        entries.sort(String::compareTo);

        if (entries.isEmpty()) {
            source.sendSuccess(() -> Component.literal(TAG + "无匹配项 (前缀: " + prefix + ")"), false);
            return 1;
        }

        StringBuilder sb = new StringBuilder("§6§l══ Data Dump ══ §f(前缀: " + prefix + ", " + entries.size() + " 项)\n");
        for (String e : entries) {
            sb.append("§7").append(e).append("\n");
        }
        source.sendSuccess(() -> Component.literal(sb.toString()), false);
        return 1;
    }

    // ════════════════════════════════════════════
    //  全部重置
    // ════════════════════════════════════════════

    private static int resetAll(CommandSourceStack source) {
        ServerPlayer player = source.getPlayer();
        if (player == null) return 0;

        int total = 0;
        total += clearByPrefix(player.getPersistentData(), "hk3gtl_res_");
        total += clearByPrefix(player.getPersistentData(), "hk3gtl_nar_");
        total += clearByPrefix(player.getPersistentData(), "hk3gtl_evt_");
        player.getPersistentData().remove(DIALOGUE_DONE_TAG);
        player.getPersistentData().remove("hk3gtl_gaze_level");
        total += 2;

        Hk3GraduationData.get(player.serverLevel()).resetForDebug(player.getUUID());
        com.sirin.hk3gtl.common.badending.Hk3BadEndingData.get(player.serverLevel()).resetForDebug(player.getUUID());

        for (ServerLevel sl : player.server.getAllLevels()) {
            sl.getEntities(Hk3Entities.VOID_QUEEN_SIRIN.get(),
                    new AABB(-1e6, -1e6, -1e6, 1e6, 1e6, 1e6), e -> true
            ).forEach(VoidQueenSirinEntity::resetTriggeredPlayers);
        }

        int t = total;
        source.sendSuccess(() -> Component.literal(TAG + "§c全部重置完成！§f清除 " + t + " 条数据。"), true);
        return 1;
    }

    // ════════════════════════════════════════════
    //  工具方法
    // ════════════════════════════════════════════

    private static String bool(boolean v) { return v ? "§a是" : "§c否"; }

    private static int countByPrefix(CompoundTag data, String prefix) {
        int count = 0;
        for (String key : data.getAllKeys()) {
            if (key.startsWith(prefix) && data.getBoolean(key)) count++;
        }
        return count;
    }

    private static int clearByPrefix(CompoundTag data, String prefix) {
        List<String> toRemove = new ArrayList<>();
        for (String key : data.getAllKeys()) {
            if (key.startsWith(prefix)) toRemove.add(key);
        }
        toRemove.forEach(data::remove);
        return toRemove.size();
    }
}
