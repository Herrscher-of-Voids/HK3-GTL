package com.sirin.hk3gtl.common.item;


/**
 * 【文件职责】
 * - 注册或实现 NarrativeCodexItem 物品行为。
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
import com.sirin.hk3gtl.common.narrative.Hk3NarrativeLog;
import com.sirin.hk3gtl.common.narrative.Hk3NarrativeNodes;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;

import javax.annotation.Nullable;
import java.util.List;

/** 中文说明：该处说明已按当前代码行为整理。*/
/** 【变更记录 #1】2026-10-01 00:44:40（修订123）：删除无；新增/修改：卷轴读取服务端本人经历，不消耗物品，不复制物品NBT中的资格；用途：个人交流、团队决定及额外收藏分开，保留真实记录。 */
public class NarrativeCodexItem extends Item {

    public NarrativeCodexItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (player.isShiftKeyDown()) {
            if (!level.isClientSide()) {
                sendStats(player);
            }
            return InteractionResultHolder.sidedSuccess(stack, level.isClientSide());
        }

        if (player instanceof net.minecraft.server.level.ServerPlayer serverPlayer) {
            com.sirin.hk3gtl.common.narrative.Hk3PersonalArchive.openCodex(serverPlayer);
        }
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide());
    }

    /** 潜行右键：总览统计 */
    private static void sendStats(Player player) {
        if (player instanceof net.minecraft.server.level.ServerPlayer serverPlayer)
            player.sendSystemMessage(Component.literal(com.sirin.hk3gtl.common.narrative.Hk3PersonalArchive.summary(serverPlayer)));
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level,
                                List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("item.hk3gtl.narrative_codex.tooltip.0")
                .withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("item.hk3gtl.narrative_codex.tooltip.1")
                .withStyle(ChatFormatting.DARK_GRAY, ChatFormatting.ITALIC));
    }
}
