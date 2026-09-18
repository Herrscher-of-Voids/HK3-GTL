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

/**
 * 《文明档案卷轴》—— 世界文本叙事系统的玩家入口物品。
 *
 * <h3>交互（当前阶段）</h3>
 * <ul>
 *   <li>右键空气：客户端打开卷轴 GUI 浏览叙事节点</li>
 *   <li>潜行右键：打印"总共 N / 已解锁 M"的统计行</li>
 * </ul>
 *
 * <h3>未来（下一轮扩展）</h3>
 * 本物品会升级为打开完整 GUI（{@code Hk3NarrativeLogScreen}），
 * 分章节显示阵营分类 + 节点详情 + 插画。
 * 本轮先提供聊天栏版本保证系统可用 + 可测试，避免玩家在没有 GUI 时看不到解锁进度。
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>GUI 落地后：在 {@link #use} 里改为打开 Screen，聊天栏逻辑保留为 fallback 或删除</li>
 *   <li>不要在此类做"解锁状态写入"：那是 {@link com.sirin.hk3gtl.common.narrative.Hk3NarrativeManager} 的职责</li>
 *   <li>聊天栏输出格式变动时保持 {@code §d[档案]} 前缀与 {@code Hk3NarrativeManager} 对齐</li>
 * </ul>
 */
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

        if (level.isClientSide()) {
            DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () ->
                    com.sirin.hk3gtl.client.narrative.Hk3NarrativeCodexScreen.open(player));
        }
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide());
    }

    /** 潜行右键：总览统计 */
    private static void sendStats(Player player) {
        int total = Hk3NarrativeNodes.totalCount();
        int unlocked = Hk3NarrativeLog.unlockedCount(player);
        player.sendSystemMessage(Component.literal("§d[档案] §f已解锁 §e" + unlocked
                + "§f / §7" + total + " §f条，继续你的文明史。"));
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
