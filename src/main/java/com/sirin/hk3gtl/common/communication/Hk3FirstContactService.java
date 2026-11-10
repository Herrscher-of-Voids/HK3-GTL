package com.sirin.hk3gtl.common.communication;

/** 【变更记录 #5】2026-09-30 23:58:50（修订121）：删除旧个人答复自动代表新队的生产路径；新增/修改：首信发现共享资料，实际答复交给团队服务；旧个人状态不自动决定合作；用途：团队外交、阅读与个人经历分账，不发研究或物品奖励。 */



/**
 * 【变更记录 #1】2026-09-29 17:51:46（内测5修订93）
 * - 删除：旧正文活动引用被审核原文替代；保留历史资源和存档。
 * - 新增／修改：开放审核附件及后续来信；服务端核验后续来信与真实回信状态一致，阅读不改写合作决定。
 * - 用途：接通审核正文；其他系统触发及归属不据此宣称完成。
 */
/** 【变更记录 #2】2026-09-29 18:57:18（内测5修订95）：首信与回信进入个人手机通知，重复登录不重复弹出。 */
import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.sirin.hk3gtl.common.network.Hk3Network;
import com.sirin.hk3gtl.common.network.Hk3LetterOpenPacket;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.ClickEvent;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.network.PacketDistributor;

/** 中文说明：该处说明已按当前代码行为整理。*/
/**
 * 【变更记录 #4】2026-09-30 16:20:43（内测5修订110）
 * 删除：被新版通知读取流程替代的旧分支，历史备注保留。
 * 新增／修改：通知记录直达已有首信/后续正文与附件；仅真实答复解除待处理，读取与预览不替玩家答复。
 * 用途：通知与业务结果分离，服务端授权和个人持久化；不改结构、贴图和贸易。
 */
/** 【变更记录 #6】2026-10-01 00:59:10（修订124）：删除无；新增/修改：每100 tick补查尚未收到首信者的背包，覆盖AE取出、容器转移及指令给予；用途：按五方交流系统整链收口，真实权限和本人经历不混用。 */
@Mod.EventBusSubscriber(modid = "hk3gtl", bus = Mod.EventBusSubscriber.Bus.FORGE)
/**
 * 【变更记录 #3】2026-09-29 23:37:35（内测5修订101）
 * 删除：本轮被替代的单前置或旧提示分支；其余历史保留。
 * 新增／修改：真实回复与登录时已存回复核验接入交流前置，阅读本身不授予实验。
 * 用途：补足研究接线并如实保留未接物理执行器及结构审批边界。
 * 追溯：logs/research-mainline-r101；R101_FINAL_RECORD。
 */
public final class Hk3FirstContactService {
    private static final TagKey<Item> MAX_CIRCUIT = TagKey.create(Registries.ITEM,
            new ResourceLocation("gtceu", "circuits/max"));
    private Hk3FirstContactService() {}

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public static void checkInventory(ServerPlayer player) {
        Hk3CommunicationData data = Hk3CommunicationData.get(player);
        if (data.state(player.getUUID()) != Hk3FirstContactState.LOCKED) return;
        for (int slot = 0; slot < player.getInventory().getContainerSize(); slot++) {
            if (qualifies(player.getInventory().getItem(slot))) { discover(player); return; }
        }
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    private static boolean qualifies(ItemStack stack) { return !stack.isEmpty() && stack.is(MAX_CIRCUIT); }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    private static void discover(ServerPlayer player) {
        Hk3CommunicationData.get(player).discover(player.getUUID());
        Hk3TeamContactService.ensure(player);
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    @SubscribeEvent public static void onLogin(PlayerEvent.PlayerLoggedInEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) return;
        Hk3FirstContactState before = Hk3CommunicationData.get(player).state(player.getUUID());
        checkInventory(player);
        Hk3TeamContactService.ensure(player);
        
    }

    @SubscribeEvent public static void inventoryTick(net.minecraftforge.event.TickEvent.PlayerTickEvent event){
        if(event.phase==net.minecraftforge.event.TickEvent.Phase.END&&event.player instanceof ServerPlayer p&&p.tickCount%100==0)checkInventory(p);
    }
    /** Forge成功拾取后的事件补足短暂入包，不使用可取消的拾取尝试事件。 / Observe successful pickups, not cancellable pickup attempts. */
    @SubscribeEvent public static void onPickup(PlayerEvent.ItemPickupEvent event) {
        if (event.getEntity() instanceof ServerPlayer player && qualifies(event.getStack())) discover(player);
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    @SubscribeEvent public static void onCraft(PlayerEvent.ItemCraftedEvent event) {
        if (event.getEntity() instanceof ServerPlayer player && qualifies(event.getCrafting())) discover(player);
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    @SubscribeEvent public static void register(RegisterCommandsEvent event) { registerCommands(event.getDispatcher()); }
    private static void registerCommands(CommandDispatcher<CommandSourceStack> dispatcher) {
        dispatcher.register(Hk3TeamContactService.commands());
    }

    /** 文档0为首信、1/2为回信预览；必须已有首信，预览不提交选择。 / Documents 0/1/2 are letter/accept/decline; previews never submit a reply. */
    public static int open(ServerPlayer player, int document) {
        return Hk3TeamContactService.open(player,document);
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    /** 中文说明：该处说明已按当前代码行为整理。*/
    private static void notifyLetter(ServerPlayer player) {
        com.sirin.hk3gtl.common.phone.Hk3PhoneService.letter(player,"first_contact_letter",
                "奥托的首信",Component.translatable("hk3gtl.letter.received").getString(),0,true);
    }
}
