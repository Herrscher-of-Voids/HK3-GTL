package com.sirin.hk3gtl.common.event;

/**
 * 【文件职责】
 * - 为特定玩家 ID（xiguamao）发放“专属首次进入世界礼物”的隐藏彩蛋处理器。
 * - 核心输入：玩家登录事件 PlayerLoggedInEvent。
 * - 核心输出：向匹配玩家背包发放礼物物品，并在聊天栏弹出西琳台词。
 * - 关键调用链：Forge 事件总线 -> onPlayerLoggedIn -> 名称匹配/去重标记 -> 发放物品 + 发送消息。
 *
 * 【变更记录 #1】2026-05-31 22:10:00（第 1 次备注 · 内测二第 1 次更新）
 * - 删除：
 *   1) 无（新建文件）。
 * - 新增：
 *   1) 新增 Hk3XiguamaoGiftHandler：监听 PlayerLoggedInEvent，对玩家名 xiguamao 发放首次入世礼物。
 *   2) 触发条件：玩家名等于 xiguamao（忽略大小写）且当前存档该玩家未触发过本彩蛋。
 *   3) 去重机制：写入 player.getPersistentData() 标记 GIFT_FLAG（与版本欢迎/事件标记同一持久化层），
 *      该数据随存档内玩家档案保存，故“每个世界仅触发一次”。
 *   4) 失败处理：礼物物品 ID 通过 ForgeRegistries 动态解析（wmp/sov 为外部模组），缺失时跳过并记 warn，
 *      不抛异常、不阻塞登录；超过最大堆叠数的数量按 maxStackSize 拆分发放，背包满则掉落地面。
 * - 修改：
 *   1) 无（新建文件，不改动既有彩蛋逻辑，避免污染 E-EG 事件/研究/叙事链）。
 * - 用途：
 *   1) 业务目标：给“多次站在西琳面前的文明建造者”的一次性礼物彩蛋。
 *   2) 系统位置：独立于 Hk3EasterEggChecker 的轻量登录处理器（SRP），不参与研究/叙事桥接。
 *   3) 风险点：仅服务端执行（ServerPlayer），动态解析外部模组物品需 null 兜底，避免硬依赖导致缺模组时崩溃。
 */

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
