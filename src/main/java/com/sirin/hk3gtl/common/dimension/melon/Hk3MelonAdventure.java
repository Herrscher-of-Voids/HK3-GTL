package com.sirin.hk3gtl.common.dimension.melon;

import com.sirin.hk3gtl.common.compat.stargate.Hk3MelonStargate;
import com.sirin.hk3gtl.common.phone.Hk3PhoneCipherData;
import com.sirin.hk3gtl.common.phone.Hk3PhoneService;
import com.sirin.hk3gtl.common.phone.cipher.Hk3CipherPuzzles;
import com.sirin.hk3gtl.common.phone.cipher.Hk3RevelationService;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.event.entity.EntityTravelToDimensionEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = "hk3gtl")
public final class Hk3MelonAdventure {
    static final String LETTER = """
            给自己这种西瓜先生，给 xiguamao：

            那份写着「自己这种西瓜」的西瓜，那台以西瓜为燃料的发电机，还有西琳从储藏室角落借出的亚空之矛。这些名字放在一起，你应该认得出来。

            纸页终于展开，星门在你身后连起两端。你已经走到这里了。这一次，就在讲台前停一会儿，读完我们留给你的信。

            GTL 第一百八十八期，六千余个方块的四联超导电磁工厂。电解机、闪电处理机、两极磁化机和电磁选矿机，终于在同一座庞大的结构中运转。

            这样一座机器，足够让人把截图珍藏很久。而在你的工业道路上，它又接上了下一期、下一台机器，接上了仍然值得期待的明天。

            后来，你又开始了二周目。重新挖矿，重新制作电路，重新站在焦炉和电力高炉旁。已经走过一次的科技树，又被你从最初的枝干慢慢接起。

            同样的配方，可以换一种安排；同样的设备，可以组成另一套生产系统。上一次积累的经验，就这样成了新世界里更从容的第一步。

            从焦炉走到人造恒星，再回到焦炉旁。每次重新开始，你仍然能从熟悉的机器里找到新的乐趣。这份热爱，让我们记住了你一次又一次出发的身影。

            焦炉是练气，电力高炉是筑基，再往上还有金丹、元婴、化神与准圣。那些修仙般的标题，也把漫长的工业发展写成了一段段有趣的旅程。

            伏羲八卦锻天炉、鸿蒙奥术星图、太虚浊化阵、宇宙之心。一个个名字背后，是你亲手放下的方块，是逐渐备齐的材料，也是许多个认真度过的夜晚。

            我们知道，你也有有限的时间，也会疲倦。每一座庞大机器能够建成，都需要有人在许多个普通的日子里，愿意再把眼前的工作做完一点。

            电力不足，可以增加发电设备；材料产量不足，可以扩大生产线。人的耐心与兴趣，却需要慢慢珍惜。你一次次继续向前的样子，也给后来的人添了些勇气。

            尤其让我们记得的，是你愿意回到开头，做起 GTL 的教程。已经建造过人造恒星的人，又站在最初的焦炉旁，认真讲解开局、蒸汽设备和早期发电。

            机器为什么没有反应，电力高炉怎样才能运行，电压又该怎样选择。你已经熟悉的事情，仍然值得为第一次遇见它们的人，耐心讲清楚。

            也许某个深夜，有人正对着缺料的生产线发愁。看过你的讲解，他终于找到了问题，又愿意打开物品查看器，准备下一台机器的材料。

            那台机器重新响起的时候，你分享过的经验，也就在另一个世界里继续运转了。

            所以，我们也想为你认真准备一份东西。那份西瓜、发电机和亚空之矛，藏着我们想让你认出的心意；现在，门前的这一封信，终于能够交到你手中。

            你建造过许多世界。这一次，换我们为你留下一个。

            这里的瓜皮山脊、籽纹砂洲，还有你身后的那道星门，都属于这次相逢。愿这片籽海，能让你在长久的工业旅程中，安心歇一歇脚。

            等你想继续的时候，来时的路仍然通着。那边还有熟悉的厂房、等待整理的线缆，也有你下一次想亲手完成的设计。

            愿那些由你亲手搭起的生产线，今后仍有值得期待的下一次开机。

            一周目，是初入格雷；二周目，是重修大道。再往后的旅程，山河依旧，星海无穷。愿你每次回到那座最初的焦炉旁，都能带着自己的兴致，再一次开始。

            自己这种西瓜先生，你认真走过的工业之路，我们一直记得。往后的世界，也祝你玩得尽兴。

            ■■■与另一个我
            """;

    private Hk3MelonAdventure() {}

    public static boolean unlocked(ServerPlayer player) {
        return Hk3PhoneCipherData.get(player).progress(player.getUUID()).stage() == Hk3CipherPuzzles.all().size()
                && Hk3RevelationService.complete(player);
    }

    public static boolean recipient(ServerPlayer player) {
        return player.getGameProfile().getName().equalsIgnoreCase("xiguamao");
    }

    public static String letter(ServerPlayer player) {
        return recipient(player) ? LETTER : "同行者抄本\n\n你替一份没有写全地址的礼物走到了这里。原信的收件人是自己这种西瓜；感谢你把这条通往他的路走完。\n\n以下是留给收件人的原信：\n\n" + LETTER;
    }

    public static String route(ServerPlayer player) {
        return exploration(player);
    }

    public static String exploration(ServerPlayer player) {
        var state = Hk3MelonData.get(player.server).player(player.getUUID());
        if (state.getBoolean("GiftFound")) return letter(player);
        return (state.getBoolean("Visited")
                ? "信就在来时星门正前方的讲台上。右键讲台，读完留给你的来信。\n\n"
                : "门符只记着来信的去处。用你亲手造出的星门拨响它，穿过门面，讲台上的信就在门前等你。\n\n")
                + "潜行右键同一个讲台，可请求来时星门的返程拨号，不消耗手机电量。来信不是研究或毕业资格。";
    }

    public static int dialReturn(ServerPlayer player) {
        if (!Hk3MelonStargate.dialReturn(player)) return 0;
        player.sendSystemMessage(Component.literal("返程星门正在拨号；穿过身后的稳定门面，就能回到来处。"));
        return 1;
    }

    private static void give(ServerPlayer player, ItemStack stack) {
        if (!player.addItem(stack)) player.drop(stack, false);
    }

    @SubscribeEvent public static void travelling(EntityTravelToDimensionEvent event) {
        if (!event.getDimension().equals(Hk3MelonWorld.KEY) || !(event.getEntity() instanceof ServerPlayer player)) return;
        if (!unlocked(player)) {
            event.setCanceled(true);
            player.sendSystemMessage(Component.literal("门面还没有认出你的来信。先解开五张外封，并亲自完成四页实物校读。"));
        }
    }

    @SubscribeEvent public static void arrived(PlayerEvent.PlayerChangedDimensionEvent event) {
        if (!event.getTo().equals(Hk3MelonWorld.KEY)) return;
        var player = (ServerPlayer) event.getEntity();
        Hk3MelonData.get(player.server).arrived(player.getUUID());
        Hk3PhoneService.notify(player, "melon_arg_landfall", "纸上的海，现在在脚下", "信就在星门正前方的讲台上。右键阅读；潜行右键同一个讲台可请求返程拨号，不消耗手机电量。", "chatter");
    }

    @SubscribeEvent public static void interact(PlayerInteractEvent.RightClickBlock event) {
        if (!event.getLevel().dimension().equals(Hk3MelonWorld.KEY) || event.getHand() != InteractionHand.MAIN_HAND
                || !event.getPos().equals(Hk3MelonWorld.LECTERN)
                || !event.getLevel().getBlockState(event.getPos()).is(Blocks.LECTERN)) return;
        event.setCanceled(true);
        event.setCancellationResult(InteractionResult.SUCCESS);
        if (!(event.getEntity() instanceof ServerPlayer player)) return;
        if (player.isShiftKeyDown()) {
            dialReturn(player);
            return;
        }
        if (!unlocked(player)) return;
        var data = Hk3MelonData.get(player.server);
        if (!data.player(player.getUUID()).getBoolean("Visited")) return;
        if (data.finish(player.getUUID())) {
            Hk3PhoneService.notify(player, "melon_arg_final_letter", recipient(player) ? "给自己这种西瓜的籽海来信" : "籽海来信 · 同行者抄本", letter(player), "chatter");
            var book = new ItemStack(Items.WRITTEN_BOOK);
            var tag = book.getOrCreateTag();
            tag.putString("title", recipient(player) ? "给自己这种西瓜" : "籽海同行者抄本");
            tag.putString("author", "■■■与另一个我");
            var pages = new ListTag();
            for (String page : letter(player).split("\n\n"))
                pages.add(StringTag.valueOf(Component.Serializer.toJson(Component.literal(page))));
            tag.put("pages", pages);
            give(player, book);
        }
        Hk3MelonWorld.placeLetter(player.serverLevel());
        player.level().getBlockState(event.getPos()).use(player.level(), player, event.getHand(), event.getHitVec());
    }
}
