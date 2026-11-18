package com.sirin.hk3gtl.common.communication;




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

@Mod.EventBusSubscriber(modid = "hk3gtl", bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class Hk3FirstContactService {
    private static final TagKey<Item> MAX_CIRCUIT = TagKey.create(Registries.ITEM,
            new ResourceLocation("gtceu", "circuits/max"));
    private Hk3FirstContactService() {}

    public static void checkInventory(ServerPlayer player) {
        Hk3CommunicationData data = Hk3CommunicationData.get(player);
        if (data.state(player.getUUID()) != Hk3FirstContactState.LOCKED) return;
        for (int slot = 0; slot < player.getInventory().getContainerSize(); slot++) {
            if (qualifies(player.getInventory().getItem(slot))) { discover(player); return; }
        }
    }

    private static boolean qualifies(ItemStack stack) { return !stack.isEmpty() && stack.is(MAX_CIRCUIT); }

    private static void discover(ServerPlayer player) {
        Hk3CommunicationData.get(player).discover(player.getUUID());
        Hk3TeamContactService.ensure(player);
    }

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

    @SubscribeEvent public static void onCraft(PlayerEvent.ItemCraftedEvent event) {
        if (event.getEntity() instanceof ServerPlayer player && qualifies(event.getCrafting())) discover(player);
    }

    @SubscribeEvent public static void register(RegisterCommandsEvent event) { registerCommands(event.getDispatcher()); }
    private static void registerCommands(CommandDispatcher<CommandSourceStack> dispatcher) {
        dispatcher.register(Hk3TeamContactService.commands());
    }

    /** 文档0为首信、1/2为回信预览；必须已有首信，预览不提交选择。 / Documents 0/1/2 are letter/accept/decline; previews never submit a reply. */
    public static int open(ServerPlayer player, int document) {
        return Hk3TeamContactService.open(player,document);
    }

    private static void notifyLetter(ServerPlayer player) {
        com.sirin.hk3gtl.common.phone.Hk3PhoneService.letter(player,"first_contact_letter",
                "奥托的首信",Component.translatable("hk3gtl.letter.received").getString(),0,true);
    }
}
