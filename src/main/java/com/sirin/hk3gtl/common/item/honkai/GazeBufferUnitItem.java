package com.sirin.hk3gtl.common.item.honkai;


/**
 * 【文件职责】
 * - 注册或实现 GazeBufferUnitItem 物品行为。
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
import com.sirin.hk3gtl.common.gaze.Hk3GazeManager;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/**
 * 注视缓冲单元消耗品：右键激活后立即降低注视并进入 10 分钟缓冲状态。
 */
public class GazeBufferUnitItem extends Item {

    public GazeBufferUnitItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (!(player instanceof ServerPlayer serverPlayer)) {
            return InteractionResultHolder.sidedSuccess(stack, level.isClientSide());
        }

        Hk3GazeManager.activateBufferUnit(serverPlayer, 20 * 60 * 10);
        if (!player.getAbilities().instabuild) {
            stack.shrink(1);
        }
        serverPlayer.sendSystemMessage(Component.literal("§d[崩坏三-GTL] §b")
                .append(Component.translatable("hk3gtl.gaze.buffer_activated")));
        return InteractionResultHolder.sidedSuccess(stack, false);
    }
}
