package com.sirin.hk3gtl.common.command;


/**
 * 【文件职责】
 * - 维护 Hk3StructureExportCommandsImpl 的核心功能实现。
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
 * 【变更记录 #1】2026-10-31 17:42:29（第 1 次备注 · 内测5修订189）
 * - 删除：任意含选区NBT物品的导出棒兜底、逐份覆盖磁盘文件的路径。
 * - 新增：save的OP2命令树与执行双重检查、安全名称、选区维度校验及异常根因日志。
 * - 修改：info/clear仍面向持棒玩家；仅注册导出棒可被识别，四份文本先生成后交ExportFiles独占写入。
 * - 用途：让服务器写文件权限由服务端决定，并避免跨维度误读和同名导出数据损坏。
 */
import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.logging.LogUtils;
import com.sirin.hk3gtl.common.multiblock.export.ExportFiles;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.item.Hk3Items;
import com.sirin.hk3gtl.common.item.StructureExportWand;
import com.sirin.hk3gtl.common.multiblock.export.ExportContext;
import com.sirin.hk3gtl.common.multiblock.export.MachineCodeWriter;
import com.sirin.hk3gtl.common.multiblock.export.PatternCodeWriter;
import com.sirin.hk3gtl.common.multiblock.export.PlainTextWriter;
import com.sirin.hk3gtl.common.multiblock.export.StructureScanner;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import org.slf4j.Logger;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.io.IOException;
import java.nio.file.FileAlreadyExistsException;
import java.util.List;

/**
 * {@code /hk3export} 命令的真实实现，整体只做三件事：
 * <ol>
 *   <li>路由：通过 Brigadier 分派到 save / info / clear 三个子命令</li>
 *   <li>读取玩家手持/背包中的结构导出棒 NBT（pos1 / pos2 / controller）</li>
 *   <li>委托 {@link StructureScanner} 扫描 → 四个 Writer 生成文本 → 写入磁盘</li>
 * </ol>
 *
 * <h3>文件产物（全部写入 {@code <serverDir>/hk3gtl_exports/}）</h3>
 * <ul>
 *   <li>{@code <name>.txt} — 可视化结构切片 + 图例 + 警告</li>
 *   <li>{@code <name>_pattern_impl.txt} — Hk3XxxPatternImpl 源码草稿</li>
 *   <li>{@code <name>_pattern_facade.txt} — Hk3XxxPattern 门面源码草稿</li>
 *   <li>{@code <name>_machine.txt} — Hk3MachinesXxxStage 字段 + init 片段草稿</li>
 * </ul>
 *
 * <h3>为什么不直接写入 src/</h3>
 * 开发场景下要避免命令直接篡改源码树（防止覆盖同名文件 / 脏工作区），改为写文本让玩家手动挪。
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增子命令：在 {@link #register} 末尾追加 {@code .then(Commands.literal("xxx") ...)}</li>
 *   <li>调整产物文件：{@link #writeFiles}</li>
 *   <li>调整 wand 扫描策略：{@link #findWand}（当前按顺序遍历主背包 36 格，命中即返回）</li>
 *   <li>严禁在此类内写扫描 / 符号分配 / 代码生成等业务逻辑，要保留薄路由</li>
 * </ul>
 */
@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public class Hk3StructureExportCommandsImpl {

    /** 输出目录名（相对 server 根目录）。修改会让历史导出失散，谨慎 */
    private static final String EXPORT_DIR = ExportFiles.DIRECTORY;
    private static final Logger LOGGER = LogUtils.getLogger();

    @SubscribeEvent
    public static void onRegisterCommands(RegisterCommandsEvent event) {
        register(event.getDispatcher());
    }

    /**
     * 命令树：
     * <pre>
     *   /hk3export save &lt;name&gt;   导出当前选区
     *   /hk3export info            聊天框打印当前选区状态
     *   /hk3export clear           清空导出棒上的选区
     * </pre>
     */
    private static void register(CommandDispatcher<CommandSourceStack> dispatcher) {
        dispatcher.register(Commands.literal("hk3export")
                .then(Commands.literal("info")
                        .executes(ctx -> doInfo(ctx.getSource())))
                .then(Commands.literal("clear")
                        .executes(ctx -> doClear(ctx.getSource())))
                .then(Commands.literal("save")
                        .requires(source -> source.hasPermission(2))
                        .then(Commands.argument("name", StringArgumentType.word())
                                .executes(ctx -> doSave(
                                        ctx.getSource(),
                                        StringArgumentType.getString(ctx, "name")))))
        );
    }

    private static int doInfo(CommandSourceStack source) {
        ServerPlayer player = source.getPlayer();
        if (player == null) return 0;
        ItemStack wand = findWand(player);
        if (wand.isEmpty()) {
            reply(source, "§c[HK3] 背包里没有结构导出棒，使用 §f/give <player> hk3gtl:structure_export_wand §c获取");
            return 0;
        }
        CompoundTag tag = wand.getOrCreateTag();
        reply(source, "§b[HK3] 当前选区：");
        reply(source, "  pos1 = " + readOrDash(tag, StructureExportWand.NBT_POS1));
        reply(source, "  pos2 = " + readOrDash(tag, StructureExportWand.NBT_POS2));
        reply(source, "  ctrl = " + readOrDash(tag, StructureExportWand.NBT_CTRL));
        return 1;
    }

    private static int doClear(CommandSourceStack source) {
        ServerPlayer player = source.getPlayer();
        if (player == null) return 0;
        ItemStack wand = findWand(player);
        if (wand.isEmpty()) {
            reply(source, "§c[HK3] 背包里没有结构导出棒");
            return 0;
        }
        CompoundTag tag = wand.getOrCreateTag();
        tag.remove(StructureExportWand.NBT_POS1);
        tag.remove(StructureExportWand.NBT_POS2);
        tag.remove(StructureExportWand.NBT_CTRL);
        tag.remove(StructureExportWand.NBT_DIMENSION);
        reply(source, "§a[HK3] 已清空选区");
        return 1;
    }

    private static int doSave(CommandSourceStack source, String name) {
        if (!source.hasPermission(2)) {
            reply(source, "§c[HK3] 结构导出需要OP2权限");
            return 0;
        }
        if (!ExportFiles.validName(name)) {
            reply(source, "§c[HK3] 名称须为1至64位小写字母、数字或下划线，以字母开头且不是系统保留名");
            return 0;
        }
        ServerPlayer player = source.getPlayer();
        if (player == null) return 0;

        ItemStack wand = findWand(player);
        if (wand.isEmpty()) {
            reply(source, "§c[HK3] 背包里没有结构导出棒");
            return 0;
        }

        CompoundTag selection = wand.getTag();
        if (selection == null || !selection.contains(StructureExportWand.NBT_DIMENSION, Tag.TAG_STRING)
                || !player.level().dimension().location().toString().equals(selection.getString(StructureExportWand.NBT_DIMENSION))) {
            reply(source, "§c[HK3] 选区维度不匹配或旧选区缺少维度，请在当前维度重新选点");
            return 0;
        }
        BlockPos pos1 = StructureExportWand.readPos(wand, StructureExportWand.NBT_POS1);
        BlockPos pos2 = StructureExportWand.readPos(wand, StructureExportWand.NBT_POS2);
        BlockPos ctrl = StructureExportWand.readPos(wand, StructureExportWand.NBT_CTRL);

        if (pos1 == null || pos2 == null || ctrl == null) {
            reply(source, "§c[HK3] 选区未完整，需要 pos1 + pos2 + ctrl 三者齐全");
            reply(source, "§7  潜行+右键 = pos1；右键控制器 = ctrl；右键其他方块 = pos2");
            return 0;
        }

        ExportContext ctx;
        try {
            ctx = StructureScanner.scan(player.level(), pos1, pos2, ctrl, name);
            writeFiles(player, ctx);
        } catch (StructureScanner.ScanException e) {
            reply(source, "§c[HK3] 扫描失败：" + e.getMessage());
            return 0;
        } catch (FileAlreadyExistsException e) {
            reply(source, "§c[HK3] 导出名称已存在，请另取名称；旧文件保持不变");
            return 0;
        } catch (IOException | RuntimeException e) {
            LOGGER.error("结构导出失败：玩家={}，名称={}", player.getGameProfile().getName(), name, e);
            reply(source, "§c[HK3] 导出失败（同名文件不会覆盖）：" + e.getMessage());
            return 0;
        }

        reply(source, "§a[HK3] 导出完成：§f" + name);
        reply(source, "§7  目录：" + EXPORT_DIR + "/  |  尺寸：" + ctx.width + "×" + ctx.height + "×" + ctx.depth);
        if (!ctx.warnings.isEmpty()) {
            reply(source, "§e[HK3] 有 " + ctx.warnings.size() + " 条警告，详见 txt 头部");
        }
        return 1;
    }

    /** 四份内容全部渲染成功后才创建文件；失败清理由ExportFiles负责。 */
    private static void writeFiles(ServerPlayer player, ExportContext ctx) throws IOException {
        ExportFiles.write(player.server.getServerDirectory().toPath(), ctx.exportName, List.of(
                PlainTextWriter.render(ctx), PatternCodeWriter.renderImpl(ctx),
                PatternCodeWriter.renderFacade(ctx), MachineCodeWriter.render(ctx)));
    }

    /** 只匹配正式注册的导出棒，任意物品携带选区NBT不获得工具身份。 */
    private static ItemStack findWand(ServerPlayer player) {
        if (Hk3Items.STRUCTURE_EXPORT_WAND != null) {
            for (ItemStack stack : player.getInventory().items) {
                if (stack.is(Hk3Items.STRUCTURE_EXPORT_WAND.get())) return stack;
            }
        }
        return ItemStack.EMPTY;
    }

    private static String readOrDash(CompoundTag tag, String key) {
        if (!tag.contains(key, Tag.TAG_LONG)) return "§7— (未设置)";
        return "§f" + BlockPos.of(tag.getLong(key)).toShortString();
    }

    private static void reply(CommandSourceStack source, String text) {
        source.sendSystemMessage(Component.literal(text));
    }
}
