package com.sirin.hk3gtl.common.item.abyss;

import com.sirin.hk3gtl.common.easter.Hk3EggVanilla;
import com.sirin.hk3gtl.common.easter.Hk3EggVoidArchivesFacts;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;

/** 虚空万藏可向空气使用；只记录本人可选收藏，不消费物品或授予研究。 */
public final class Hk3VoidArchivesItem extends Item {
    public Hk3VoidArchivesItem(Properties properties) { super(properties); }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack held = player.getItemInHand(hand);
        var hit = getPlayerPOVHitResult(level, player, ClipContext.Fluid.ANY);
        if (!Hk3EggVoidArchivesFacts.accepts(held.getItem() == this, held.getCount(), hit.getType()))
            return InteractionResultHolder.pass(held);
        var eye = player.getEyePosition();
        var ray = hit.getLocation().subtract(eye);
        // 方块射线不含实体；对着实体的交互回落不能冒充右键空气。
        if (ProjectileUtil.getEntityHitResult(player, eye, hit.getLocation(),
                player.getBoundingBox().expandTowards(ray).inflate(1),
                target -> !target.isSpectator() && target.isPickable(), ray.lengthSqr()) != null)
            return InteractionResultHolder.pass(held);
        var success = InteractionResultHolder.sidedSuccess(held, level.isClientSide);
        if (!level.isClientSide && player instanceof ServerPlayer serverPlayer)
            Hk3EggVanilla.caseEvent(serverPlayer, 79);
        return success;
    }
}
