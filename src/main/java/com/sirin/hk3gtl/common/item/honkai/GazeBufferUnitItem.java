package com.sirin.hk3gtl.common.item.honkai;



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
