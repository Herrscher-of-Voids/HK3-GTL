package com.sirin.hk3gtl.common.item;



import com.sirin.hk3gtl.common.multiblock.export.StructureScanner;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;

import javax.annotation.Nullable;
import java.util.List;

/**
 * 结构导出棒 —— 多方块结构导出工具，在游戏内以"点三下"的形式圈定选区并执行
 * {@code /hk3export save <name>} 命令。
 *
 * <h3>交互方式</h3>
 * <ul>
 *   <li><b>潜行 + 右键方块</b>：设置 pos1（选区角点 A）</li>
 *   <li><b>非潜行 + 右键方块</b>：
 *     <ul>
 *       <li>若该方块带水平朝向属性且不是 casing/glass/coil → 标记为控制器</li>
 *       <li>否则标记为 pos2（选区角点 B）</li>
 *     </ul>
 *   </li>
 *   <li><b>右键空气</b>：在聊天栏回显当前 pos1/pos2/controller 状态</li>
 * </ul>
 *
 * <h3>NBT 存储</h3>
 * <ul>
 *   <li>{@code hk3gtl_export_pos1} (long，BlockPos.asLong())</li>
 *   <li>{@code hk3gtl_export_pos2} (long)</li>
 *   <li>{@code hk3gtl_export_ctrl} (long)</li>
 * </ul>
 * 命令 {@link com.sirin.hk3gtl.common.command.Hk3StructureExportCommandsImpl} 读取这三个 NBT 完成导出。
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增交互态（如镜像检测）：复用 {@link #use}/{@link #useOn} 并添加新 NBT key</li>
 *   <li>调整控制器识别逻辑：集中在 {@link #looksLikeController}；过滤关键字与
 *       {@link com.sirin.hk3gtl.common.multiblock.export.StructureScanner#resolveFacing} 保持一致</li>
 *   <li>禁止在此类做导出本身的 IO / 文件写入：那是命令层的职责</li>
 *   <li>ClickBlockPos 必须用 {@link BlockPos#immutable()} 复制，GT / 原版返回的 BlockPos 可能被复用</li>
 * </ul>
 */
public class StructureExportWand extends Item {

    public static final String NBT_POS1 = "hk3gtl_export_pos1";
    public static final String NBT_POS2 = "hk3gtl_export_pos2";
    public static final String NBT_CTRL = "hk3gtl_export_ctrl";

    public StructureExportWand(Properties properties) {
        super(properties);
    }

    /** 右键方块时触发：根据是否潜行 + 方块类型，分派到 pos1 / pos2 / controller */
    @Override
    public InteractionResult useOn(UseOnContext context) {
        Player player = context.getPlayer();
        Level level = context.getLevel();
        if (player == null || level.isClientSide()) return InteractionResult.SUCCESS;

        BlockPos pos = context.getClickedPos().immutable();
        BlockState state = level.getBlockState(pos);
        ItemStack wand = context.getItemInHand();
        CompoundTag tag = wand.getOrCreateTag();

        if (player.isShiftKeyDown()) {
            tag.putLong(NBT_POS1, pos.asLong());
            msg(player, "§a[HK3] pos1 已设置为 " + pos.toShortString());
            return InteractionResult.CONSUME;
        }

        if (looksLikeController(state)) {
            tag.putLong(NBT_CTRL, pos.asLong());
            Direction facing = StructureScanner.resolveFacing(state);
            msg(player, "§b[HK3] 控制器已设置为 " + pos.toShortString()
                    + "（朝向 " + facing + "）");
            return InteractionResult.CONSUME;
        }

        tag.putLong(NBT_POS2, pos.asLong());
        msg(player, "§e[HK3] pos2 已设置为 " + pos.toShortString());
        return InteractionResult.CONSUME;
    }

    /** 右键空气时：显示当前选区状态 */
    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack wand = player.getItemInHand(hand);
        if (level.isClientSide()) {
            return InteractionResultHolder.success(wand);
        }
        CompoundTag tag = wand.getOrCreateTag();
        sendStatus(player, tag);
        return InteractionResultHolder.success(wand);
    }

    /** 背包内时附着简要 tooltip，方便玩家快速记起操作方式 */
    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level,
                                List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("item.hk3gtl.structure_export_wand.tooltip.0")
                .withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("item.hk3gtl.structure_export_wand.tooltip.1")
                .withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("item.hk3gtl.structure_export_wand.tooltip.2")
                .withStyle(ChatFormatting.GRAY));

        CompoundTag tag = stack.getTag();
        if (tag == null) return;
        appendPosTip(tooltip, tag, NBT_POS1, "pos1");
        appendPosTip(tooltip, tag, NBT_POS2, "pos2");
        appendPosTip(tooltip, tag, NBT_CTRL, "ctrl");
    }

    private static void appendPosTip(List<Component> tooltip, CompoundTag tag, String key, String label) {
        if (!tag.contains(key)) return;
        BlockPos pos = BlockPos.of(tag.getLong(key));
        tooltip.add(Component.literal("§7  " + label + " = " + pos.toShortString()));
    }

    private static void sendStatus(Player player, CompoundTag tag) {
        boolean empty = true;
        if (tag.contains(NBT_POS1)) { msg(player, "§7pos1 = " + posStr(tag, NBT_POS1)); empty = false; }
        if (tag.contains(NBT_POS2)) { msg(player, "§7pos2 = " + posStr(tag, NBT_POS2)); empty = false; }
        if (tag.contains(NBT_CTRL)) { msg(player, "§7ctrl = " + posStr(tag, NBT_CTRL)); empty = false; }
        if (empty) {
            msg(player, "§c[HK3] 导出棒尚未设置任何选区点。");
            msg(player, "§7潜行+右键 = pos1；右键控制器 = 指定控制器；右键其他方块 = pos2");
        } else {
            msg(player, "§a[HK3] 执行 §f/hk3export save <name> §a完成导出");
        }
    }

    private static String posStr(CompoundTag tag, String key) {
        return BlockPos.of(tag.getLong(key)).toShortString();
    }

    private static void msg(Player player, String text) {
        player.sendSystemMessage(Component.literal(text));
    }

    /**
     * 判断一个方块是否像多方块控制器：
     * <ol>
     *   <li>带水平朝向属性（{@link StructureScanner#resolveFacing} 非 null）</li>
     *   <li>路径不含 casing / glass / coil / frame 等装饰关键字</li>
     * </ol>
     * 若玩家需要强制把某个含 "casing" 但实际是控制器的方块设为 ctrl，
     * 只能通过命令 {@code /hk3export ctrl} 手动指定（命令层兜底）。
     */
    public static boolean looksLikeController(BlockState state) {
        if (StructureScanner.resolveFacing(state) == null) return false;
        String path = net.minecraft.core.registries.BuiltInRegistries.BLOCK
                .getKey(state.getBlock()).getPath();
        return !path.contains("casing")
                && !path.contains("glass")
                && !path.contains("coil")
                && !path.contains("frame");
    }

    /** 给外部命令/GUI 使用的读取快捷方法：读不到时返回 null */
    @Nullable
    public static BlockPos readPos(ItemStack stack, String key) {
        CompoundTag tag = stack.getTag();
        if (tag == null || !tag.contains(key)) return null;
        return BlockPos.of(tag.getLong(key));
    }
}
