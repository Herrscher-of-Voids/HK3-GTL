package com.sirin.hk3gtl.common.narrative.story;

import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.builder.LiteralArgumentBuilder;
import com.sirin.hk3gtl.common.communication.Hk3TeamContactData;
import com.sirin.hk3gtl.common.phone.Hk3PhoneData;
import com.sirin.hk3gtl.common.phone.Hk3PhoneRuntime;
import com.sirin.hk3gtl.common.phone.Hk3PhoneService;
import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import com.sirin.hk3gtl.common.research.Hk3ResearchExecutionContracts;
import com.sirin.hk3gtl.common.research.Hk3ResearchTeams;
import com.sirin.hk3gtl.common.review.Hk3ReviewData;
import com.sirin.hk3gtl.common.review.Hk3ReviewLedger;
import com.sirin.hk3gtl.common.review.Hk3ReviewReturnData;
import com.sirin.hk3gtl.common.finale.Hk3FinaleData;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.Locale;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Mod.EventBusSubscriber(modid = "hk3gtl")
public final class Hk3StoryService {
    private static final String PREFIX = "hk3phone apps story";
    private static final Map<String, String> WINDOWS = Map.of("academy", "学园时期", "moon", "月面时期");
    private record Entry(UUID team, Hk3StoryCatalog.Node node, long delivered) {}
    private Hk3StoryService() {}

    private static UUID team(ServerPlayer player) { return Hk3ResearchTeams.scope(player.server, player.getUUID()); }
    private static long time(MinecraftServer server) { return server.overworld().getGameTime(); }
    private static String mail(UUID team, String id) { return "story_" + team + "_" + id; }

    public static void fact(ServerPlayer player, String id) {
        if (Hk3StoryData.get(player.server).fact(player.getUUID(), id, time(player.server)))
            refresh(player.server, player.getUUID(), team(player));
    }

    public static void teamFact(MinecraftServer server, UUID team, String id) {
        if (!Hk3StoryData.get(server).teamFact(team, id, time(server))) return;
        for (UUID actor : Hk3ResearchData.get(server).members(team)) refresh(server, actor, team);
    }

    public static void choice(ServerPlayer player, String key, String value) {
        Hk3StoryData.get(player.server).choice(player.getUUID(), team(player), key, value);
    }

    public static boolean has(ServerPlayer player, String id) {
        return Hk3StoryData.get(player.server).has(player.getUUID(), team(player), id);
    }

    public static boolean introduced(MinecraftServer server, UUID team, String faction) {
        return Hk3StoryData.get(server).teamHas(team, "contact_" + faction);
    }

    private static boolean eligible(MinecraftServer server, UUID actor, UUID team, Hk3StoryCatalog.Node node) {
        var data = Hk3StoryData.get(server);
        var contacts = Hk3TeamContactData.get(server);
        return node.requires().stream().allMatch(id -> data.has(actor, team, id))
                && (node.route().isEmpty() || node.route().equals(contacts.route(team)))
                && (!node.id().startsWith("otto_") || contacts.cooperationActive(team));
    }

    private static void effects(MinecraftServer server, UUID team, List<String> facts) {
        for (String id : facts) {
            Hk3StoryData.get(server).teamFact(team, id, time(server));
            if (id.equals("otto_port_closed")) Hk3TeamContactData.get(server).closeCooperation(team, time(server));
        }
    }

    private static void refresh(MinecraftServer server, UUID actor, UUID team) {
        var data = Hk3StoryData.get(server);
        var phone = Hk3PhoneData.get(server);
        for (var node : Hk3StoryCatalog.NODES) {
            if (data.completed(actor, team, node.id())) effects(server, team, node.onComplete());
            boolean available = eligible(server, actor, team, node);
            if (!data.delivered(actor, team, node.id())) {
                if (!available) continue;
                data.deliver(actor, team, node.id(), time(server));
            }
            if (available) effects(server, team, node.onDelivery());
            Hk3PhoneService.deliver(server, actor, mail(team, node.id()), node.speaker() + "｜" + node.title(),
                    node.body(), "story", team + "/" + node.id(), available && !data.completed(actor, team, node.id()));
            phone.pending(actor, mail(team, node.id()), available && !data.completed(actor, team, node.id()));
        }
    }

    @SubscribeEvent public static void login(PlayerEvent.PlayerLoggedInEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) synchronize(player);
    }

    private static void synchronize(ServerPlayer player) {
        var server = player.server; var actor = player.getUUID(); var team = team(player);
        var research = Hk3ResearchData.get(server); var data = Hk3StoryData.get(server); long tick = time(server);
        for (String id : Hk3ResearchExecutionContracts.all().keySet())
            if (research.completed(team, id)) data.teamFact(team, "research_" + id, tick);
        for (int index = 1; index <= 15; index++) {
            String role = String.format(Locale.ROOT, "W%02d", index);
            if (research.hasProcessFact(team, "wonder_" + role)) data.teamFact(team, "engineering_" + role, tick);
        }
        if (research.hasProcessFact(team, "hyperion_engineering")) data.teamFact(team, "engineering_H01", tick);
        if (research.hasProcessFact(team, "wonder_application")) data.teamFact(team, "engineering_application", tick);
        var reviews = Hk3ReviewData.get(server);
        boolean firstHome = reviews.experienced(actor, Hk3ReviewLedger.Kind.FIRST) && Hk3ReviewReturnData.get(server).point(actor) == null;
        if (firstHome) data.fact(actor, "first_review_completed", tick);
        if (firstHome && reviews.snapshot().qualified(team, Hk3ReviewLedger.Kind.SECOND)) data.teamFact(team, "second_review_ready", tick);
        if (reviews.experienced(actor, Hk3ReviewLedger.Kind.SECOND)) data.fact(actor, "second_review_completed", tick);
        String finale = Hk3FinaleData.get(server).snapshot().save().getCompound("People").getCompound(actor.toString()).getString("State");
        if (!finale.isEmpty()) data.fact(actor, "finale_admitted", tick);
        if (finale.equals("PASSED")) data.fact(actor, "finale_passed", tick);
        if (finale.equals("BAD")) data.fact(actor, "finale_bad", tick);
        refresh(server, actor, team);
    }

    public static LiteralArgumentBuilder<CommandSourceStack> commands() {
        return Commands.literal("story").executes(c -> index(c.getSource().getPlayerOrException(), 0))
                .then(Commands.argument("page", IntegerArgumentType.integer(0)).executes(c -> index(c.getSource().getPlayerOrException(), IntegerArgumentType.getInteger(c, "page"))))
                .then(Commands.literal("window").then(Commands.argument("id", StringArgumentType.word())
                        .executes(c -> index(c.getSource().getPlayerOrException(), 0, StringArgumentType.getString(c, "id")))
                        .then(Commands.argument("page", IntegerArgumentType.integer(0)).executes(c -> index(c.getSource().getPlayerOrException(),
                                IntegerArgumentType.getInteger(c, "page"), StringArgumentType.getString(c, "id"))))))
                .then(Commands.literal("read").then(Commands.argument("team", net.minecraft.commands.arguments.UuidArgument.uuid())
                        .then(Commands.argument("node", StringArgumentType.word()).executes(c -> open(c.getSource().getPlayerOrException(),
                                net.minecraft.commands.arguments.UuidArgument.getUuid(c, "team"), StringArgumentType.getString(c, "node"))))))
                .then(Commands.literal("choose").then(Commands.argument("team", net.minecraft.commands.arguments.UuidArgument.uuid())
                        .then(Commands.argument("node", StringArgumentType.word()).then(Commands.argument("choice", StringArgumentType.word())
                                .executes(c -> choose(c.getSource().getPlayerOrException(), net.minecraft.commands.arguments.UuidArgument.getUuid(c, "team"),
                                        StringArgumentType.getString(c, "node"), StringArgumentType.getString(c, "choice")))))));
    }

    private static boolean allowed(ServerPlayer player) {
        return Hk3PhoneData.get(player).installed(player.getUUID()) && Hk3PhoneRuntime.requirePower(player);
    }

    private static CompoundTag view(String mode) {
        var view = new CompoundTag(); view.putString("Mode", mode); view.putBoolean("Story", true); return view;
    }

    private static void button(ListTag actions, String title, String command) {
        var button = new CompoundTag(); button.putString("Title", title); button.putString("Command", command); actions.add(button);
    }

    public static int index(ServerPlayer player, int page) {
        return index(player, page, "");
    }

    private static int index(ServerPlayer player, int page, String window) {
        if (!allowed(player)) return 0;
        if (!window.isEmpty() && !WINDOWS.containsKey(window)) return 0;
        synchronize(player);
        var data = Hk3StoryData.get(player.server); var history = data.history(player.getUUID());
        var entries = new ArrayList<Entry>();
        for (String origin : history.getAllKeys()) for (var node : Hk3StoryCatalog.NODES) {
            var stored = history.getCompound(origin).getCompound(node.id());
            if (stored.contains("Delivered") && (window.isEmpty() || window.equals(node.window())))
                entries.add(new Entry(UUID.fromString(origin), node, stored.getLong("Delivered")));
        }
        entries.sort(Comparator.comparingLong(Entry::delivered).reversed().thenComparing(e -> e.node().id()));
        page = Math.min(page, Math.max(0, (entries.size() - 1) / 4));
        var view = view("diplomacy"); view.putString("Title", window.isEmpty() ? "文明往来" : "琪亚娜 · " + WINDOWS.get(window));
        view.putString("Body", "已收到的通信与经历｜" + (page + 1) + "/" + Math.max(1, (entries.size() + 3) / 4));
        var actions = new ListTag();
        if (window.isEmpty()) for (var port : WINDOWS.entrySet()) {
            if (entries.stream().anyMatch(entry -> entry.node().window().equals(port.getKey())))
                button(actions, "已建立窗口 · " + port.getValue(), PREFIX + " window " + port.getKey());
        }
        for (var entry : entries.stream().skip(page * 4L).limit(4).toList()) {
            String state = data.completed(player.getUUID(), entry.team(), entry.node().id()) ? "已记录"
                    : eligible(player.server, player.getUUID(), entry.team(), entry.node()) ? "待回应" : "历史";
            if (!entry.team().equals(team(player))) state = "历史";
            button(actions, state + " · " + entry.node().title(), PREFIX + " read " + entry.team() + " " + entry.node().id());
        }
        String pages = window.isEmpty() ? PREFIX : PREFIX + " window " + window;
        if (page > 0) button(actions, "上一页", pages + " " + (page - 1));
        if ((page + 1) * 4 < entries.size()) button(actions, "下一页", pages + " " + (page + 1));
        if (!window.isEmpty()) button(actions, "返回全部往来", PREFIX);
        view.put("Actions", actions); Hk3PhoneService.send(player, view); return 1;
    }

    public static int open(ServerPlayer player, UUID origin, String id) {
        if (!allowed(player)) return 0;
        var node = Hk3StoryCatalog.node(id); var data = Hk3StoryData.get(player.server); var actor = player.getUUID();
        if (node == null || !data.delivered(actor, origin, id)) return 0;
        var view = view("diplomacy_read"); view.putString("Id", mail(origin, id)); view.putString("Title", node.speaker() + "｜" + node.title());
        String body = node.body();
        if (!data.answer(actor, origin, id).isEmpty()) {
            var answer = node.choices().stream().filter(choice -> choice.id().equals(data.answer(actor, origin, id))).findFirst().orElseThrow();
            String reply = data.reply(actor, origin, id);
            body += "\n\n你的回应：" + answer.label() + "\n\n" + (reply.isEmpty() ? answer.reply() : reply);
        }
        view.putString("Body", body);
        var actions = new ListTag();
        if (origin.equals(team(player)) && !data.completed(actor, origin, id) && eligible(player.server, actor, origin, node))
            for (var choice : node.choices()) button(actions, choice.label(), PREFIX + " choose " + origin + " " + id + " " + choice.id());
        Hk3PhoneData.get(player).read(actor, mail(origin, id));
        view.put("Actions", actions); Hk3PhoneService.send(player, view); return 1;
    }

    private static int choose(ServerPlayer player, UUID origin, String id, String option) {
        if (!allowed(player) || !origin.equals(team(player))) return 0;
        var data = Hk3StoryData.get(player.server); var node = Hk3StoryCatalog.node(id); var actor = player.getUUID();
        if (node == null || !data.delivered(actor, origin, id) || data.completed(actor, origin, id)
                || !eligible(player.server, actor, origin, node) || node.choices().stream().noneMatch(choice -> choice.id().equals(option))) return 0;
        var choice = node.choices().stream().filter(answer -> answer.id().equals(option)).findFirst().orElseThrow();
        String reply = choice.memories().stream().filter(memory -> data.remembers(actor, origin, memory.fact()))
                .map(Hk3StoryCatalog.Memory::reply).findFirst().orElse(choice.reply());
        if (choice.defer()) data.defer(actor, origin, id, option, reply, time(player.server));
        else {
            data.complete(actor, origin, id, option, reply, time(player.server));
            effects(player.server, origin, node.onComplete());
            Hk3PhoneData.get(player).resolve(actor, mail(origin, id));
            for (UUID member : Hk3ResearchData.get(player.server).members(origin)) refresh(player.server, member, origin);
        }
        return open(player, origin, id);
    }
}
