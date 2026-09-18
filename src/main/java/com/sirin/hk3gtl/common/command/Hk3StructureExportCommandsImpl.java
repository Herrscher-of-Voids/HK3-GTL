package com.sirin.hk3gtl.common.command;



import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.StringArgumentType;
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
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

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
 * 需求变更时，只需在 {@link #writeFiles} 中追加直接写入 src 的支路即可。
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
    private static final String EXPORT_DIR = "hk3gtl_exports";

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
        reply(source, "§a[HK3] 已清空选区");
        return 1;
    }

    private static int doSave(CommandSourceStack source, String name) {
        ServerPlayer player = source.getPlayer();
        if (player == null) return 0;

        ItemStack wand = findWand(player);
        if (wand.isEmpty()) {
            reply(source, "§c[HK3] 背包里没有结构导出棒");
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
        } catch (StructureScanner.ScanException e) {
            reply(source, "§c[HK3] 扫描失败：" + e.getMessage());
            return 0;
        }

        try {
            writeFiles(player, ctx);
        } catch (IOException e) {
            reply(source, "§c[HK3] 写入失败：" + e.getMessage());
            return 0;
        }

        reply(source, "§a[HK3] 导出完成：§f" + name);
        reply(source, "§7  目录：" + EXPORT_DIR + "/  |  尺寸：" + ctx.width + "×" + ctx.height + "×" + ctx.depth);
        if (!ctx.warnings.isEmpty()) {
            reply(source, "§e[HK3] 有 " + ctx.warnings.size() + " 条警告，详见 txt 头部");
        }
        return 1;
    }

    /**
     * 把四份产物写到 {@code <serverDir>/hk3gtl_exports/} 下。
     * 存在同名文件会被覆盖（符合命令语义，避免静默失败）。
     */
    private static void writeFiles(ServerPlayer player, ExportContext ctx) throws IOException {
        Path dir = player.server.getServerDirectory().toPath().resolve(EXPORT_DIR);
        Files.createDirectories(dir);

        String name = ctx.exportName;
        Files.writeString(dir.resolve(name + ".txt"),
                PlainTextWriter.render(ctx), StandardCharsets.UTF_8);
        Files.writeString(dir.resolve(name + "_pattern_impl.txt"),
                PatternCodeWriter.renderImpl(ctx), StandardCharsets.UTF_8);
        Files.writeString(dir.resolve(name + "_pattern_facade.txt"),
                PatternCodeWriter.renderFacade(ctx), StandardCharsets.UTF_8);
        Files.writeString(dir.resolve(name + "_machine.txt"),
                MachineCodeWriter.render(ctx), StandardCharsets.UTF_8);
    }

    /**
     * 定位玩家背包中第一把结构导出棒：
     * <ol>
     *   <li>优先匹配物品 = {@link Hk3Items#STRUCTURE_EXPORT_WAND}</li>
     *   <li>兜底匹配：含 NBT 键 {@code hk3gtl_export_pos1/2/ctrl} 的任意物品（兼容重命名 / 调试场景）</li>
     * </ol>
     */
    private static ItemStack findWand(ServerPlayer player) {
        if (Hk3Items.STRUCTURE_EXPORT_WAND != null) {
            for (ItemStack stack : player.getInventory().items) {
                if (stack.is(Hk3Items.STRUCTURE_EXPORT_WAND.get())) return stack;
            }
        }
        for (ItemStack stack : player.getInventory().items) {
            CompoundTag tag = stack.getTag();
            if (tag == null) continue;
            if (tag.contains(StructureExportWand.NBT_POS1)
                    || tag.contains(StructureExportWand.NBT_POS2)
                    || tag.contains(StructureExportWand.NBT_CTRL)) {
                return stack;
            }
        }
        return ItemStack.EMPTY;
    }

    private static String readOrDash(CompoundTag tag, String key) {
        if (!tag.contains(key)) return "§7— (未设置)";
        return "§f" + BlockPos.of(tag.getLong(key)).toShortString();
    }

    private static void reply(CommandSourceStack source, String text) {
        source.sendSystemMessage(Component.literal(text));
    }
}
