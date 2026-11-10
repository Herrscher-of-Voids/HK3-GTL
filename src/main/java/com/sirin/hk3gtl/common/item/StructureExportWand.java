package com.sirin.hk3gtl.common.item;


/**
 * 【文件职责】
 * - 注册或实现 StructureExportWand 物品行为。
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
 * - 删除：跨维度沿用旧坐标和非Long坐标的默认零值读取；移除不存在的ctrl命令说明。
 * - 新增：选点记录维度，维度变更先清空三个旧坐标；状态提示OP2导出权限。
 * - 修改：所有坐标展示与readPos只接受Long；服务端选点仍允许普通玩家，写文件由命令检查OP2。
 * - 用途：供导出命令读取真实工具选区，防止坐标类型错误和跨维度串用。
 */
import com.sirin.hk3gtl.common.multiblock.export.StructureScanner;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
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

/** 中文说明：该处说明已按当前代码行为整理。*/
public class StructureExportWand extends Item {

    public static final String NBT_POS1 = "hk3gtl_export_pos1";
    public static final String NBT_POS2 = "hk3gtl_export_pos2";
    public static final String NBT_CTRL = "hk3gtl_export_ctrl";
    public static final String NBT_DIMENSION = "hk3gtl_export_dimension";

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
        String dimension = level.dimension().location().toString();
        if (!dimension.equals(tag.getString(NBT_DIMENSION))) {
            tag.remove(NBT_POS1);
            tag.remove(NBT_POS2);
            tag.remove(NBT_CTRL);
            tag.putString(NBT_DIMENSION, dimension);
        }

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
        if (!tag.contains(key, Tag.TAG_LONG)) return;
        BlockPos pos = BlockPos.of(tag.getLong(key));
        tooltip.add(Component.literal("§7  " + label + " = " + pos.toShortString()));
    }

    private static void sendStatus(Player player, CompoundTag tag) {
        boolean empty = true;
        if (tag.contains(NBT_POS1, Tag.TAG_LONG)) { msg(player, "§7pos1 = " + posStr(tag, NBT_POS1)); empty = false; }
        if (tag.contains(NBT_POS2, Tag.TAG_LONG)) { msg(player, "§7pos2 = " + posStr(tag, NBT_POS2)); empty = false; }
        if (tag.contains(NBT_CTRL, Tag.TAG_LONG)) { msg(player, "§7ctrl = " + posStr(tag, NBT_CTRL)); empty = false; }
        if (empty) {
            msg(player, "§c[HK3] 导出棒尚未设置任何选区点。");
            msg(player, "§7潜行+右键 = pos1；右键控制器 = 指定控制器；右键其他方块 = pos2");
        } else {
            msg(player, "§a[HK3] 执行 §f/hk3export save <name> §a完成导出（需要OP2权限）");
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
     * 特殊控制器无法由名称判断时，需要调整识别规则；当前没有强制控制器子命令。
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
        if (tag == null || !tag.contains(key, Tag.TAG_LONG)) return null;
        return BlockPos.of(tag.getLong(key));
    }
}
