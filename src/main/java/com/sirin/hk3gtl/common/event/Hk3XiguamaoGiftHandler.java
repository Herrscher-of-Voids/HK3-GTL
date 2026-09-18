package com.sirin.hk3gtl.common.event;



import com.sirin.hk3gtl.common.constants.Hk3Constants;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.items.ItemHandlerHelper;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class Hk3XiguamaoGiftHandler {

    private static final Logger LOGGER = LogUtils.getLogger();

    /** 目标玩家 ID（忽略大小写匹配） */
    private static final String TARGET_PLAYER = "xiguamao";

    /** 去重标记键：写入玩家 persistentData，随存档保存，保证每个世界仅发放一次 */
    private static final String GIFT_FLAG = "hk3gtl_xiguamao_first_join_gift";

    /** 礼物清单：{命名空间:路径, 数量}，外部模组物品在运行时动态解析 */
    private static final String[][] GIFTS = {
            {"wmp:watermelon_generator", "1"},
            {"wmp:zijizhezhongxigua", "256"},
            {"wmp:hov", "1"},
            {"sov:spear_of_void", "1"},
    };

    private Hk3XiguamaoGiftHandler() {}

    @SubscribeEvent
    public static void onPlayerLoggedIn(PlayerEvent.PlayerLoggedInEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) {
            return;
        }
        if (!TARGET_PLAYER.equalsIgnoreCase(player.getGameProfile().getName())) {
            return;
        }
        CompoundTag data = player.getPersistentData();
        if (data.getBoolean(GIFT_FLAG)) {
            return;
        }
        data.putBoolean(GIFT_FLAG, true);

        grantGifts(player);

        // 右下角聊天栏弹出西琳台词
        player.sendSystemMessage(Component.translatable("hk3gtl.gift.xiguamao"));
    }

    /** 发放礼物：动态解析外部模组物品，缺失则跳过；数量超堆叠上限自动拆分。 */
    private static void grantGifts(ServerPlayer player) {
        for (String[] gift : GIFTS) {
            ResourceLocation id = ResourceLocation.tryParse(gift[0]);
            if (id == null || !BuiltInRegistries.ITEM.containsKey(id)) {
                LOGGER.warn("[HK3GTL] xiguamao 礼物物品缺失，已跳过: {}", gift[0]);
                continue;
            }
            Item item = BuiltInRegistries.ITEM.get(id);
            int remaining = Integer.parseInt(gift[1]);
            int maxStack = Math.max(1, new ItemStack(item).getMaxStackSize());
            while (remaining > 0) {
                int give = Math.min(remaining, maxStack);
                ItemHandlerHelper.giveItemToPlayer(player, new ItemStack(item, give));
                remaining -= give;
            }
        }
    }
}
