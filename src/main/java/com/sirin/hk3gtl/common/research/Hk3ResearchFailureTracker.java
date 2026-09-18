package com.sirin.hk3gtl.common.research;



import com.sirin.hk3gtl.common.dialogue.DialogueSessionManager;
import com.sirin.hk3gtl.common.event.Hk3EventManager;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;

/**
 * 研究失败追踪器 —— "非酋"彩蛋实装。
 *
 * <h3>规则</h3>
 * <ul>
 *   <li>默认每次研究失败概率 {@value #DEFAULT_FAIL_CHANCE}（1%）</li>
 *   <li>累计失败 {@value #UNLUCKY_THRESHOLD} 次时一次性触发彩蛋（聊天提示），之后失败概率永久减半</li>
 *   <li>状态存储在玩家 persistentData，与 {@link Hk3ResearchManager} 同存储层（不区分死亡保留）</li>
 * </ul>
 *
 * <h3>NBT 键</h3>
 * <ul>
 *   <li>{@code hk3gtl_total_fails} — int，累计失败次数</li>
 *   <li>{@code hk3gtl_unlucky_egg} — boolean，彩蛋是否已触发</li>
 * </ul>
 *
 * <h3>Phase 3 备注</h3>
 * 当研究系统从零重写时，本类可继续保留并扩展。当前接口面 {@link #getFailChance} /
 * {@link #onResearchFailed} 由 Hk3ResearchMatrixMachine 调用。
 */
public final class Hk3ResearchFailureTracker {

    public static final double DEFAULT_FAIL_CHANCE = 0.01;
    public static final double UNLUCKY_FAIL_CHANCE = 0.005;
    public static final int UNLUCKY_THRESHOLD = 10;

    private static final String NBT_TOTAL_FAILS = "hk3gtl_total_fails";
    private static final String NBT_UNLUCKY_EGG_TRIGGERED = "hk3gtl_unlucky_egg";

    private Hk3ResearchFailureTracker() {}

    /**
     * 当前玩家适用的研究失败概率。彩蛋触发后永久减半。
     */
    public static double getFailChance(Player player) {
        CompoundTag data = player.getPersistentData();
        return data.getBoolean(NBT_UNLUCKY_EGG_TRIGGERED) ? UNLUCKY_FAIL_CHANCE : DEFAULT_FAIL_CHANCE;
    }

    /**
     * 累计失败次数。
     */
    public static int getTotalFails(Player player) {
        return player.getPersistentData().getInt(NBT_TOTAL_FAILS);
    }

    /**
     * 彩蛋是否已触发过。
     */
    public static boolean isEasterEggTriggered(Player player) {
        return player.getPersistentData().getBoolean(NBT_UNLUCKY_EGG_TRIGGERED);
    }

    /**
     * 一次研究失败 → 累加计数 → 若达阈值则触发彩蛋。
     *
     * @param failedNodeNameKey 失败节点的翻译键（用于聊天回显）
     */
    public static void onResearchFailed(ServerPlayer player, String failedNodeNameKey) {
        CompoundTag data = player.getPersistentData();
        int total = data.getInt(NBT_TOTAL_FAILS) + 1;
        data.putInt(NBT_TOTAL_FAILS, total);

        player.sendSystemMessage(Component.translatable(
                "hk3gtl.research.matrix.failed",
                Component.translatable(failedNodeNameKey),
                total));

        if (total >= UNLUCKY_THRESHOLD && !data.getBoolean(NBT_UNLUCKY_EGG_TRIGGERED)) {
            data.putBoolean(NBT_UNLUCKY_EGG_TRIGGERED, true);
            player.sendSystemMessage(Component.translatable("hk3gtl.research.matrix.unlucky_egg"));
            // 叙事/研究桥：一次性事件（解锁 EG-003 等）
            Hk3EventManager.tryTriggerFirstTime(player, "E-EGG-001", "hk3gtl.event.egg001");
            DialogueSessionManager.startDialogue(player, "unlucky_egg");
        }
    }
}
