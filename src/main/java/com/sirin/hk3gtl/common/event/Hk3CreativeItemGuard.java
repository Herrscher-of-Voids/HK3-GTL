package com.sirin.hk3gtl.common.event;



import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraftforge.eventbus.api.Event;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class Hk3CreativeItemGuard {

    /** 受限的 GT 创造级机器 path（namespace 固定 gtceu） */
    private static final Set<String> BANNED_MACHINE_PATHS = Set.of("creative_chest", "creative_tank");

    /** 发话冷却（毫秒），避免连点刷屏 */
    private static final long TALK_COOLDOWN_MS = 3000L;
    private static final ConcurrentHashMap<UUID, Long> LAST_TALK = new ConcurrentHashMap<>();

    private Hk3CreativeItemGuard() {}

    @SubscribeEvent
    public static void onRightClickBlock(PlayerInteractEvent.RightClickBlock event) {
        Player player = event.getEntity();
        if (player == null || player.isCreative() || player.isSpectator()) {
            return; // 创造/旁观放行
        }
        if (!isBannedCreativeMachine(event.getLevel(), event.getPos())) {
            return;
        }

        // 生存/冒险模式：拒绝方块激活以阻止 GUI 打开（不影响手持物品的放置等其它交互）
        event.setUseBlock(Event.Result.DENY);

        if (!event.getLevel().isClientSide() && player instanceof ServerPlayer serverPlayer) {
            long now = System.currentTimeMillis();
            Long last = LAST_TALK.get(serverPlayer.getUUID());
            if (last == null || now - last >= TALK_COOLDOWN_MS) {
                LAST_TALK.put(serverPlayer.getUUID(), now);
                serverPlayer.sendSystemMessage(Component.translatable("hk3gtl.guard.creative_item.elysia"));
            }
        }
    }

    /** 判定 pos 处方块是否为 gtceu 的创造箱/创造储罐机器。 */
    private static boolean isBannedCreativeMachine(Level level, BlockPos pos) {
        BlockEntity be = level.getBlockEntity(pos);
        if (!(be instanceof IMachineBlockEntity mbe)) {
            return false;
        }
        MetaMachine machine = mbe.getMetaMachine();
        if (machine == null) {
            return false;
        }
        ResourceLocation id = machine.getDefinition().getId();
        return "gtceu".equals(id.getNamespace()) && BANNED_MACHINE_PATHS.contains(id.getPath());
    }
}
