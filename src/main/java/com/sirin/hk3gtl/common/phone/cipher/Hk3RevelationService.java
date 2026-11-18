package com.sirin.hk3gtl.common.phone.cipher;

import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.builder.LiteralArgumentBuilder;
import com.sirin.hk3gtl.common.compat.stargate.Hk3MelonStargate;
import com.sirin.hk3gtl.common.dimension.melon.Hk3MelonAdventure;
import com.sirin.hk3gtl.common.dimension.melon.Hk3MelonData;
import com.sirin.hk3gtl.common.dimension.melon.Hk3MelonWorld;
import com.sirin.hk3gtl.common.phone.Hk3PhoneCipherData;
import com.sirin.hk3gtl.common.phone.Hk3PhoneData;
import com.sirin.hk3gtl.common.phone.Hk3PhoneRuntime;
import com.sirin.hk3gtl.common.phone.Hk3PhoneService;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.povstalec.sgjourney.common.sgjourney.Address;

public final class Hk3RevelationService {
    private static final String[] EDGES = {"起刻", "叶脉", "瓜纹", "籽痕", "止刻"};

    private Hk3RevelationService() {}

    public static LiteralArgumentBuilder<CommandSourceStack> commands() {
        return Commands.literal("relic")
                .executes(c -> open(c.getSource().getPlayerOrException(), -1, ""))
                .then(Commands.literal("page").then(Commands.argument("page", IntegerArgumentType.integer(0, 3))
                        .executes(c -> open(c.getSource().getPlayerOrException(), IntegerArgumentType.getInteger(c, "page"), ""))))
                .then(Commands.literal("submit").then(Commands.argument("slot", IntegerArgumentType.integer(0, 35))
                        .executes(c -> submit(c.getSource().getPlayerOrException(), IntegerArgumentType.getInteger(c, "slot")))))
                .then(Commands.literal("hint").executes(c -> hint(c.getSource().getPlayerOrException())));
    }

    public static boolean complete(ServerPlayer player) {
        return Hk3RevelationData.get(player.server).reader(player.getUUID()).getInt("Mask") == 15;
    }

    private static boolean allowed(ServerPlayer player) {
        return Hk3PhoneData.get(player).installed(player.getUUID())
                && Hk3PhoneCipherData.get(player).progress(player.getUUID()).stage() == Hk3CipherPuzzles.all().size()
                && Hk3PhoneRuntime.requirePower(player);
    }

    public static int open(ServerPlayer player, int page, String feedback) {
        if (!allowed(player)) return 0;
        var data = Hk3RevelationData.get(player.server);
        if (page >= 0) data.select(player.getUUID(), page);
        return show(player, data, feedback);
    }

    private static int submit(ServerPlayer player, int slot) {
        if (!allowed(player)) return 0;
        var data = Hk3RevelationData.get(player.server);
        int page = data.reader(player.getUUID()).getInt("Page");
        if (!Hk3RevelationItems.accepts(player, data.entry(page), data.circuit(), player.getInventory().getItem(slot)))
            return show(player, data, "这件物品与本页还未吻合。留意诗中的出处，以及它现在应有的状态。");
        data.verify(player.getUUID(), page);
        Hk3MelonStargate.ensureDestination(player.server);
        player.playNotifySound(SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.PLAYERS, .8F, 1.2F);
        player.serverLevel().sendParticles(ParticleTypes.END_ROD, player.getX(), player.getY() + 1, player.getZ(), 12, .3, .4, .3, .01);
        return show(player, data, "缺字浮现，籽纹接通。一段门符留在了页边；物件仍由你保管。");
    }

    private static int hint(ServerPlayer player) {
        if (!allowed(player)) return 0;
        var data = Hk3RevelationData.get(player.server);
        data.hint(player.getUUID(), data.reader(player.getUUID()).getInt("Page"));
        return show(player, data, "补充依据已展开。");
    }

    private static int show(ServerPlayer player, Hk3RevelationData data, String feedback) {
        var reader = data.reader(player.getUUID());
        int page = reader.getInt("Page");
        int mask = reader.getInt("Mask");
        var sea = Hk3MelonData.get(player.server).player(player.getUUID());
        int total = Hk3CipherPuzzles.all().size();
        var view = new CompoundTag();
        view.putString("Mode", "cipher");
        view.putInt("Stage", total);
        view.putInt("Page", total);
        view.putInt("Total", total);
        view.putBoolean("Completed", true);
        view.putBoolean("Revelation", true);
        view.putInt("RelicPage", page);
        view.putInt("RelicMask", mask);
        view.putBoolean("SeaVisited", sea.getBoolean("Visited"));
        view.putBoolean("GiftFound", sea.getBoolean("GiftFound"));
        view.putBoolean("InSeedSea", player.level().dimension().equals(Hk3MelonWorld.KEY));
        view.putString("Title", "未定址的来信 · 残页" + (page + 1));
        view.putString("Feedback", feedback);
        if ((reader.getInt("Hints") & 1 << page) != 0)
            view.putString("Hint", Hk3RevelationItems.evidence(data.entry(page)));
        var body = new StringBuilder("地址散在四件文明留下的事物中。写下名字没有用；选择一件你实际携带的物品，与此页校读。\n\n")
                .append(Hk3RevelationItems.verse(data.entry(page), data.circuit())).append("\n\n");
        if ((mask & 1 << page) != 0) body.append("补全的页边：\n").append(fragment(player, data, page)).append("\n\n");
        body.append("拼接说明：以「起刻」为首，让前页右边与后页左边同名的籽纹相接，直到「止刻」。按接好的先后抄出各段门符，段内顺序不倒转。页码不代表航向次序。\n\n");
        if (mask == 15) {
            body.append("四页补全抄录：\n");
            for (int i = 0; i < 4; i++) body.append("残页").append(i + 1).append("：").append(fragment(player, data, i)).append('\n');
            body.append("\n").append(Hk3MelonAdventure.exploration(player));
        }
        view.putString("Body", body.toString());
        var inventory = new ListTag();
        for (int slot = 0; slot < 36; slot++) {
            var stack = player.getInventory().getItem(slot);
            if (stack.isEmpty()) continue;
            var row = new CompoundTag();
            row.putInt("Slot", slot);
            row.putString("Name", stack.getHoverName().getString() + " ×" + stack.getCount());
            inventory.add(row);
        }
        view.put("Inventory", inventory);
        Hk3PhoneService.send(player, view);
        return 1;
    }

    private static String fragment(ServerPlayer player, Hk3RevelationData data, int page) {
        var address = new Address.Immutable(Hk3MelonStargate.ensureDestination(player.server));
        int section = data.order(page);
        var text = new StringBuilder(EDGES[section]).append(" ⟦ ");
        for (int i = section * address.getLength() / 4; i < (section + 1) * address.getLength() / 4; i++)
            text.append(address.symbolAt(i)).append(' ');
        return text.append("⟧ ").append(EDGES[section + 1]).toString();
    }
}
