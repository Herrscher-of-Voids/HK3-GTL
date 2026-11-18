package com.sirin.hk3gtl.common.item;

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
