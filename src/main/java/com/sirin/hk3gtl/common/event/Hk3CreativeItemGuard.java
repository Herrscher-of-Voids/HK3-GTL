package com.sirin.hk3gtl.common.event;

/**
 * 【文件职责】
 * - 限制非创造模式玩家与 GT 创造级机器（创造箱 gtceu:creative_chest / 创造储罐 gtceu:creative_tank）交互。
 * - 当前策略：保留获取途径，但在生存/冒险模式右键时阻止打开其 GUI，并由爱莉希雅(粉色)发话。
 * - 关键调用链：Forge 事件总线 RightClickBlock -> onRightClickBlock -> 判定机器/模式 -> 拒绝 useBlock + 发话。
 *
 * 【变更记录 #1】2026-06-01 13:45:00（第 1 次备注 · 内测三第 4 次更新）
 * - 删除：
 *   1) 无（新建文件）。原 KubeJS 版（kubejs/server_scripts/recipes/removal.js 的 inventoryChanged 块）失效，
 *      因整合包实例的 kubejs 目录与项目不同步、根本不含该脚本，故迁移为 Java 实现。
 * - 新增：
 *   1) Hk3CreativeItemGuard：服务端每秒(每 20 tick)扫描玩家背包，命中创造箱/创造储罐则清除并提示。
 *   2) 触发条件：仅当玩家既非创造模式也非旁观模式（生存/冒险）时没收；创造/旁观放行。
 *   3) 物品 ID 通过 BuiltInRegistries 动态解析并懒缓存，缺失则跳过，避免硬依赖；GTCEu 缺失也不崩。
 * - 修改：
 *   1) 行为等价于原 KubeJS 逻辑，但随模组 jar 加载，不依赖实例 kubejs 同步，从根本上修复“不生效”。
 * - 用途：
 *   1) 业务目标：封堵生存模式获取创造级存储物品，维持工业进程的正常性。
 *   2) 风险点：PlayerTickEvent 高频触发，已按 20 tick 节流；仅服务端执行；背包扫描为 O(背包格数)。
 *
 * 【变更记录 #2】2026-06-01 13:55:00（第 2 次备注 · 内测三第 5 次更新）
 * - 删除：
 *   1) 没收后的普通红字提示 "§c[崩坏三-GTL] 禁止在生存模式持有创造级物品，已清除。"。
 * - 新增：
 *   1) 改由西琳出面发话：translatable("hk3gtl.guard.creative_item.sirin")，语气为劝阻“偷鸡”(走捷径)。
 *   2) 语言键已在 zh_cn / en_us 同步。
 * - 用途：
 *   1) 在没收创造级物品的同时给出符合世界观的西琳台词，强化“不许偷鸡”的设定表达。
 *   2) 行为不变：仍是检测→清除→发话；不依赖 kubejs，覆盖任何获取途径。
 *
 * 【变更记录 #3】2026-06-01 14:05:00（第 3 次备注 · 内测三第 6 次更新，策略改写）
 * - 删除：
 *   1) 整段“每 tick 扫描背包 + 没收创造箱/储罐 + 西琳发话”的逻辑（PlayerTickEvent、背包扫描、物品 ID 缓存）。
 *   2) 原因：需求变更为“保留获取方式，不再删除物品”，没收逻辑与新需求冲突。
 * - 新增：
 *   1) 监听 PlayerInteractEvent.RightClickBlock：生存/冒险模式右键创造箱/创造储罐机器时，
 *      setUseBlock(DENY) 阻止其打开 GUI（精准只挡方块激活，不影响手持方块的放置等）。
 *   2) 被阻止时由爱莉希雅(粉色 §d)在聊天栏发话：translatable("hk3gtl.guard.creative_item.elysia")。
 *   3) 机器判定复用 GT 的 IMachineBlockEntity/MetaMachine：namespace=gtceu 且 path∈{creative_chest,creative_tank}。
 *   4) 每玩家 3 秒发话冷却（ConcurrentHashMap），避免连点刷屏；仅服务端发消息。
 * - 修改：
 *   1) 由“事后没收”改为“事前拦截 GUI”，玩家可持有但生存模式无法打开其界面。
 * - 用途：
 *   1) 业务目标：保留创造级存储物品的获取，但禁止生存模式利用其无限存储“偷鸡”。
 *   2) 风险点：RightClickBlock 双端触发，仅服务端发消息；useBlock=DENY 精准拦截，避免误伤放置/副手。
 */

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
