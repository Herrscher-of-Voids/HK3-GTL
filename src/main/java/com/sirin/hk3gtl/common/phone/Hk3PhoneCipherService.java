package com.sirin.hk3gtl.common.phone;

import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.builder.LiteralArgumentBuilder;
import com.sirin.hk3gtl.common.phone.cipher.Hk3CipherPuzzles;
import com.sirin.hk3gtl.common.phone.cipher.Hk3RevelationService;
import com.sirin.hk3gtl.common.dimension.melon.Hk3MelonAdventure;
import com.sirin.hk3gtl.common.dimension.melon.Hk3MelonData;
import com.sirin.hk3gtl.common.dimension.melon.Hk3MelonWorld;
import java.util.stream.Collectors;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;

public final class Hk3PhoneCipherService {
    private static final int TOTAL = Hk3CipherPuzzles.all().size();
    private Hk3PhoneCipherService() {}

    public static LiteralArgumentBuilder<CommandSourceStack> commands() {
        return Commands.literal("cipher")
                .executes(c -> open(c.getSource().getPlayerOrException(), -1, ""))
                .then(Hk3RevelationService.commands())
                .then(Commands.literal("return").executes(c -> returnGate(c.getSource().getPlayerOrException())))
                .then(Commands.literal("page").then(Commands.argument("page", IntegerArgumentType.integer(0, TOTAL))
                        .executes(c -> open(c.getSource().getPlayerOrException(), IntegerArgumentType.getInteger(c, "page"), ""))))
                .then(Commands.literal("hint").executes(c -> hint(c.getSource().getPlayerOrException())))
                .then(Commands.literal("answer").then(Commands.argument("answer", StringArgumentType.greedyString())
                        .executes(c -> answer(c.getSource().getPlayerOrException(), StringArgumentType.getString(c, "answer")))));
    }

    private static boolean allowed(ServerPlayer player) {
        return Hk3PhoneData.get(player).installed(player.getUUID()) && Hk3PhoneRuntime.requirePower(player);
    }

    public static int openCurrent(ServerPlayer player) {
        return open(player, -1, "");
    }

    private static int returnGate(ServerPlayer player) {
        return allowed(player) ? Hk3MelonAdventure.dialReturn(player) : 0;
    }

    private static int open(ServerPlayer player, int requested, String feedback) {
        if (!allowed(player)) return 0;
        return show(player, requested, feedback);
    }

    private static int show(ServerPlayer player, int requested, String feedback) {
        var progress = Hk3PhoneCipherData.get(player).progress(player.getUUID());
        int stage = progress.stage();
        int page = requested < 0 ? stage : Math.min(requested, stage);
        if (page == TOTAL) return Hk3RevelationService.open(player, -1, feedback);
        boolean complete = stage == TOTAL;
        var sea = Hk3MelonData.get(player.server).player(player.getUUID());
        var view = new CompoundTag();
        view.putString("Mode", "cipher");
        view.putInt("Stage", stage);
        view.putInt("Page", page);
        view.putInt("Total", TOTAL);
        view.putBoolean("Completed", complete);
        view.putBoolean("SeaVisited", sea.getBoolean("Visited"));
        view.putBoolean("GiftFound", sea.getBoolean("GiftFound"));
        view.putBoolean("InSeedSea", player.level().dimension().equals(Hk3MelonWorld.KEY));
        view.putString("Feedback", feedback);
        view.putString("Keys", Hk3CipherPuzzles.all().stream().limit(stage)
                .map(p -> p.title() + "：" + p.answer()).collect(Collectors.joining("\n")));
        var puzzle = Hk3CipherPuzzles.all().get(page);
        view.putString("Title", puzzle.title());
        view.putString("Body", puzzle.body());
        view.putString("Hint", (progress.hints() & 1 << page) != 0 ? puzzle.hint() : "");
        Hk3PhoneService.send(player, view);
        return 1;
    }

    private static int answer(ServerPlayer player, String answer) {
        if (!allowed(player)) return 0;
        var data = Hk3PhoneCipherData.get(player);
        int stage = data.progress(player.getUUID()).stage();
        if (stage == TOTAL) return show(player, TOTAL, "外封已经展开，航行档案仍在记录来信的去处。");
        if (!Hk3CipherPuzzles.accepts(stage, answer)) return show(player, stage, "译文还没有对上，纸页仍在等你。");
        data.advance(player.getUUID());
        return show(player, stage + 1, stage + 1 == TOTAL ? "外封已解。四张启示仍缺少实物的回应，航向藏在它们的页边。" : "折痕吻合。上一页的译文已收入钥匙簿。");
    }

    private static int hint(ServerPlayer player) {
        if (!allowed(player)) return 0;
        var data = Hk3PhoneCipherData.get(player);
        if (data.progress(player.getUUID()).stage() < TOTAL) data.hint(player.getUUID());
        return show(player, -1, "");
    }
}
