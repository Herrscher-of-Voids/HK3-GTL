package com.sirin.hk3gtl.common.communication;

 





import com.google.gson.Gson;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.builder.LiteralArgumentBuilder;
import com.sirin.hk3gtl.common.phone.Hk3PhoneData;
import com.sirin.hk3gtl.common.phone.Hk3PhoneService;
import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import com.sirin.hk3gtl.common.research.Hk3ResearchTeams;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Mod.EventBusSubscriber(modid = "hk3gtl")
public final class Hk3ProgressCorrespondence {
    private record Choice(String label, String body, String feedback) {}
    private record Stage(String id, String research, String title, String speaker, String body, List<Choice> choices) {}
    private record Catalog(String acceptedOpening, String independentOpening, List<Stage> stages) {}
    private record Draft(String token, UUID team, String stage, int choice, long until) {}
    private static final Catalog CATALOG = load();
    private static final Map<UUID, Draft> DRAFTS = new HashMap<>();
    private static final Hk3ContactSessions STOP_SESSIONS = new Hk3ContactSessions();
    private static final String PREFIX = "hk3letter progress";
    private static final String STOP_STAGE = "cooperation_stopped";
    private static final String STOP_LETTER = "奥托先生：\n\n我们决定结束与旧天命正在进行的合作。已经交换的资料仍按原先约定处理，尚未开始的课题就停在这里。\n\n此后我们会继续自己的研究。\n\n异界文明的领导者";
    private static final String STOP_REPLY = "奥托\n\n我已收到你们的决定。双方的合作就此结束，已经交付的资料仍按原先约定保留。我不会再为你们安排新的共同课题。\n\n感谢你们在这段时间里投入的工作。祝你们之后的研究顺利。";
    private static final int PAGE_SIZE = 3;
    private static final long PREVIEW_TICKS = 6000;

    private Hk3ProgressCorrespondence() {}

    private static Catalog load() {
        try (var stream = Hk3ProgressCorrespondence.class.getResourceAsStream("/assets/hk3gtl/narrative/progress_correspondence.json")) {
            return new Gson().fromJson(new InputStreamReader(stream, StandardCharsets.UTF_8), Catalog.class);
        } catch (IOException exception) {
            throw new IllegalStateException("无法读取阶段来信正文", exception);
        }
    }

    private static UUID team(ServerPlayer player) { return Hk3ResearchTeams.scope(player.server, player.getUUID()); }
    private static Stage stage(String id) { return CATALOG.stages.stream().filter(s -> s.id.equals(id)).findFirst().orElse(null); }
    private static String id(UUID team, String stage) { return "progress_" + team + "_" + stage; }
    private static String feedbackId(UUID team, String stage) { return "progress_reply_" + team + "_" + stage; }
    private static boolean authorized(ServerPlayer player, UUID team) {
        return Hk3TeamContactData.get(player.server).canDecide(team, player.getUUID(),
                Hk3ResearchTeams.owner(player.server, team), Hk3ResearchData.get(player).isMember(player.getUUID(), team));
    }

    public static void refresh(ServerPlayer player) {
        UUID team = team(player);
        var contacts = Hk3TeamContactData.get(player.server);
        if (!contacts.settled(team)) return;
        var research = Hk3ResearchData.get(player);
        var data = Hk3ProgressCorrespondenceData.get(player.server);
        var inbox = Hk3PhoneData.get(player);
        var members = research.members(team);
        boolean active = contacts.cooperationActive(team);
        for (var stage : CATALOG.stages) {
            if (active && research.completed(team, stage.research))
                data.deliver(team, stage.id, contacts.state(team), System.currentTimeMillis());
            if (!data.delivered(team, stage.id)) continue;
            var answer = data.reply(team, stage.id);
            boolean pending = active && answer.isEmpty();
            for (UUID member : members) {
                Hk3PhoneService.deliver(player.server, member, id(team, stage.id), stage.speaker + "｜" + stage.title,
                        "收到一封新的阶段来信。可以阅读正文，并由队长或明确授权成员回信。",
                        "progress_letter", team + "/" + stage.id, pending);
                inbox.pending(member, id(team, stage.id), pending);
                if (!answer.isEmpty()) Hk3PhoneService.deliver(player.server, member, feedbackId(team, stage.id),
                        stage.speaker + "的回信｜" + stage.title, "本队的回信已发出，对方已经作出答复。打开可回看完整往来。",
                        "progress_letter", team + "/" + stage.id, false);
            }
        }
        if (contacts.route(team).equals("STOPPED"))
            for (UUID member : members) Hk3PhoneService.deliver(player.server, member, id(team, STOP_STAGE),
                    "合作结束确认｜奥托", "双方已确认结束旧天命合作，既有资料按原先约定保留。", "progress_letter", team + "/" + STOP_STAGE, false);
    }

    public static int home(ServerPlayer player) { return page(player, 0); }

    private static int page(ServerPlayer player, int page) {
        if (!Hk3DiplomacyService.allowed(player)) return 0;
        Hk3TeamContactService.ensure(player);
        refresh(player);
        clearPreview(player.getUUID());
        UUID team = team(player);
        var data = Hk3ProgressCorrespondenceData.get(player.server);
        var contacts = Hk3TeamContactData.get(player.server);
        boolean active = contacts.cooperationActive(team);
        var letters = CATALOG.stages.stream().filter(s -> data.delivered(team, s.id)).toList();
        int last = Math.max(0, (letters.size() - 1) / PAGE_SIZE);
        int current = Math.min(page, last);
        var view = Hk3DiplomacyService.view("diplomacy");
        view.putString("Title", "奥托与研究往来 · " + (current + 1) + "/" + (last + 1));
        String route = switch (contacts.route(team)) {
            case "DECLINED" -> "你们没有接受旧天命的合作邀请。奥托的共同研究来信在此停止，原首信与答复可以回看。";
            case "STOPPED" -> "你们已主动结束旧天命合作。已有往来仍保留，尚未开始的共同课题停止。";
            case "ACCEPTED" -> active ? "你们正在与旧天命保持合作。研究抵达新的阶段时，共同研究来信会送达。" : "旧天命合作已经结束，已有往来可继续回看。";
            default -> "先答复奥托的首信，再决定是否开展旧天命合作。";
        };
        view.putString("Body", route + "\n\n已收到 " + letters.size() + " 封阶段来信。来信、已发出的本队回信和对方反馈均可回看，预览后确认才会发送。");
        Hk3DiplomacyService.button(view, "奥托首信与个人补谈", "hk3letter");
        if (contacts.route(team).equals("STOPPED")) Hk3DiplomacyService.button(view, "回看合作结束确认", PREFIX + " read " + STOP_STAGE);
        for (var stage : letters.stream().skip((long) current * PAGE_SIZE).limit(PAGE_SIZE).toList())
            Hk3DiplomacyService.button(view, (data.reply(team, stage.id).isEmpty() ? active ? "待答复 · " : "历史来信 · " : "已往来 · ") + stage.title,
                    PREFIX + " read " + stage.id);
        if (current > 0) Hk3DiplomacyService.button(view, "上一页", PREFIX + " page " + (current - 1));
        if (current < last) Hk3DiplomacyService.button(view, "下一页", PREFIX + " page " + (current + 1));
        if (active && authorized(player, team)) Hk3DiplomacyService.button(view, "预览结束旧天命合作", PREFIX + " stop");
        Hk3DiplomacyService.button(view, "返回五方联络", "hk3letter diplomacy");
        Hk3DiplomacyService.send(player, view);
        return 1;
    }

    public static int read(ServerPlayer player, UUID origin, String stageId) {
        if (!Hk3DiplomacyService.allowed(player)) return 0;
        clearPreview(player.getUUID());
        if (stageId.equals(STOP_STAGE)) return stopped(player, origin);
        var stage = stage(stageId);
        var data = Hk3ProgressCorrespondenceData.get(player.server);
        var inbox = Hk3PhoneData.get(player);
        UUID current = team(player);
        if (stage == null || !data.delivered(origin, stageId)) return 0;
        if (!origin.equals(current) && inbox.entry(player.getUUID(), id(origin, stageId)) == null) return 0;
        var answer = data.reply(origin, stageId);
        String opening = data.route(origin, stageId).equals("ACCEPTED") ? CATALOG.acceptedOpening : CATALOG.independentOpening;
        var body = new StringBuilder(stage.speaker).append("\n\n").append(opening).append("\n\n").append(stage.body);
        if (!answer.isEmpty()) {
            var choice = stage.choices.get(answer.getInt("Choice"));
            body.append("\n\n本队已发出的回信\n\n").append(choice.body)
                    .append("\n\n").append(stage.speaker).append("的回信\n\n").append(choice.feedback);
        }
        var view = Hk3DiplomacyService.view("diplomacy_read");
        view.putString("Title", stage.speaker + "｜" + stage.title);
        view.putString("Body", body.toString());
        view.putString("Id", id(origin, stageId));
        view.putString("ProgressStage", stageId);
        boolean active = origin.equals(current) && Hk3TeamContactData.get(player.server).cooperationActive(current);
        view.putBoolean("ReadOnly", !active || !authorized(player, current) || !answer.isEmpty());
        if (active && answer.isEmpty()) {
            for (int i = 0; i < stage.choices.size(); i++)
                Hk3DiplomacyService.button(view, "预览：" + stage.choices.get(i).label, PREFIX + " preview " + stageId + " " + i);
        } else Hk3DiplomacyService.button(view, "返回持续来信", PREFIX);
        inbox.read(player.getUUID(), id(origin, stageId));
        inbox.read(player.getUUID(), feedbackId(origin, stageId));
        Hk3DiplomacyService.send(player, view);
        return 1;
    }

    public static int feedback(ServerPlayer player, UUID origin, String stageId) {
        if (!Hk3DiplomacyService.allowed(player)) return 0;
        clearPreview(player.getUUID());
        var stage = stage(stageId);
        var data = Hk3ProgressCorrespondenceData.get(player.server);
        var inbox = Hk3PhoneData.get(player);
        UUID current = team(player);
        String responseId = feedbackId(origin, stageId);
        var answer = data.reply(origin, stageId);
        if (stage == null || !data.delivered(origin, stageId) || answer.isEmpty()
                || inbox.entry(player.getUUID(), responseId) == null) return 0;
        var choice = stage.choices.get(answer.getInt("Choice"));
        var view = Hk3DiplomacyService.view("diplomacy_read");
        view.putString("Title", stage.speaker + "的回信｜" + stage.title);
        view.putString("Body", stage.speaker + "\n\n" + choice.feedback + "\n\n本队已发出的回信\n\n" + choice.body);
        view.putString("Id", responseId);
        view.putString("ProgressStage", stageId);
        view.putBoolean("ReadOnly", true);
        Hk3DiplomacyService.button(view, "返回完整往来", "hk3phone message " + id(origin, stageId));
        if (origin.equals(current)) Hk3DiplomacyService.button(view, "返回持续来信", PREFIX);
        inbox.read(player.getUUID(), responseId);
        Hk3DiplomacyService.send(player, view);
        return 1;
    }

    public static int preview(ServerPlayer player, String stageId, int choice) {
        if (!Hk3DiplomacyService.allowed(player)) return 0;
        clearPreview(player.getUUID());
        UUID team = team(player);
        if (!Hk3TeamContactData.get(player.server).cooperationActive(team)) return home(player);
        var stage = stage(stageId);
        var data = Hk3ProgressCorrespondenceData.get(player.server);
        if (stage == null || choice < 0 || choice > 1 || !data.delivered(team, stageId) || !data.reply(team, stageId).isEmpty()) return 0;
        boolean permitted = authorized(player, team);
        String token = "";
        if (permitted) {
            token = UUID.randomUUID().toString();
            DRAFTS.put(player.getUUID(), new Draft(token, team, stageId, choice, player.server.overworld().getGameTime() + PREVIEW_TICKS));
        }
        var view = Hk3DiplomacyService.view("diplomacy_read");
        view.putString("Title", "回信预览｜" + stage.choices.get(choice).label);
        view.putString("Body", stage.choices.get(choice).body + (permitted
                ? "\n\n这是尚未发出的回信。按下发送后，本队将收到对方针对这一选择的答复。"
                : "\n\n当前为只读预览。由队长或明确授权成员代表本队发送。"));
        view.putBoolean("ProgressPreview", true);
        view.putString("ProgressStage", stageId);
        view.putInt("ProgressChoice", choice);
        view.putString("ProgressToken", token);
        view.putBoolean("ReadOnly", !permitted);
        Hk3DiplomacyService.button(view, "返回持续来信", PREFIX);
        Hk3DiplomacyService.send(player, view);
        return 1;
    }

    public static int reply(ServerPlayer player, String stageId, int choice, String token) {
        if (!Hk3DiplomacyService.allowed(player)) return 0;
        UUID team = team(player);
        var draft = DRAFTS.remove(player.getUUID());
        if (draft == null || !draft.token.equals(token) || !draft.team.equals(team) || !draft.stage.equals(stageId)
                || draft.choice != choice || player.server.overworld().getGameTime() >= draft.until || !authorized(player, team)
                || !Hk3TeamContactData.get(player.server).cooperationActive(team)) {
            player.sendSystemMessage(Component.literal("回信尚未发送：预览已失效，或团队、授权发生变化。请重新预览。"));
            return home(player);
        }
        var data = Hk3ProgressCorrespondenceData.get(player.server);
        if (!data.answer(team, stageId, player.getUUID(), choice, System.currentTimeMillis())) return home(player);
        refresh(player);
        player.sendSystemMessage(Component.literal("回信已发送，对方的答复已送达本队收件箱。"));
        return feedback(player, team, stageId);
    }

    public static int stopPreview(ServerPlayer player) {
        if (!Hk3DiplomacyService.allowed(player)) return 0;
        Hk3TeamContactService.ensure(player);
        clearPreview(player.getUUID());
        UUID team = team(player);
        var contacts = Hk3TeamContactData.get(player.server);
        if (!contacts.cooperationActive(team)) return home(player);
        var view = Hk3DiplomacyService.view("diplomacy_read");
        view.putString("Title", "结束旧天命合作的回信预览");
        view.putString("Body", STOP_LETTER + "\n\n确认后，旧天命的共同研究来信与回信入口会停止。已经交付的资料和历史记录仍然保留。");
        view.putString("ProgressStage", STOP_STAGE);
        if (authorized(player, team)) {
            var preview = STOP_SESSIONS.issue(player.getUUID(), team, contacts.event(team), "stop", 0, player.server.overworld().getGameTime());
            Hk3DiplomacyService.button(view, "确认发送并结束合作", PREFIX + " stop_confirm " + preview.token());
        }
        Hk3DiplomacyService.button(view, "返回持续来信", PREFIX);
        Hk3DiplomacyService.send(player, view);
        return 1;
    }

    public static int stopConfirm(ServerPlayer player, String token) {
        if (!Hk3DiplomacyService.allowed(player)) return 0;
        UUID key;
        try { key = UUID.fromString(token); } catch (IllegalArgumentException invalid) { return 0; }
        UUID team = team(player);
        var preview = STOP_SESSIONS.consume(player.getUUID(), key, team, "stop", player.server.overworld().getGameTime());
        var contacts = Hk3TeamContactData.get(player.server);
        if (preview == null || !contacts.stopCooperation(team, player.getUUID(), Hk3ResearchTeams.owner(player.server, team),
                Hk3ResearchData.get(player).isMember(player.getUUID(), team), preview.event(), player.server.overworld().getGameTime())) return home(player);
        Hk3DiplomacyService.refresh(player);
        player.sendSystemMessage(Component.literal("结束合作的回信已发送，奥托已确认。"));
        return stopped(player, team);
    }

    private static int stopped(ServerPlayer player, UUID origin) {
        var inbox = Hk3PhoneData.get(player);
        if (!Hk3TeamContactData.get(player.server).route(origin).equals("STOPPED")
                || !origin.equals(team(player)) && inbox.entry(player.getUUID(), id(origin, STOP_STAGE)) == null) return 0;
        var view = Hk3DiplomacyService.view("diplomacy_read");
        view.putString("Title", "合作结束确认｜奥托");
        view.putString("Body", "本队已发出的回信\n\n" + STOP_LETTER + "\n\n" + STOP_REPLY);
        view.putString("Id", id(origin, STOP_STAGE));
        view.putString("ProgressStage", STOP_STAGE);
        view.putBoolean("ReadOnly", true);
        if (origin.equals(team(player))) Hk3DiplomacyService.button(view, "返回持续来信", PREFIX);
        inbox.read(player.getUUID(), id(origin, STOP_STAGE));
        Hk3DiplomacyService.send(player, view);
        return 1;
    }

    public static void clearPreview(UUID actor) { DRAFTS.remove(actor); STOP_SESSIONS.clear(actor); }

    public static LiteralArgumentBuilder<CommandSourceStack> commands() {
        return Commands.literal("progress").executes(c -> home(c.getSource().getPlayerOrException()))
                .then(Commands.literal("stop").executes(c -> stopPreview(c.getSource().getPlayerOrException())))
                .then(Commands.literal("stop_confirm").then(Commands.argument("token", StringArgumentType.word())
                        .executes(c -> stopConfirm(c.getSource().getPlayerOrException(), StringArgumentType.getString(c, "token")))))
                .then(Commands.literal("page").then(Commands.argument("page", IntegerArgumentType.integer(0))
                        .executes(c -> page(c.getSource().getPlayerOrException(), IntegerArgumentType.getInteger(c, "page")))))
                .then(Commands.literal("read").then(Commands.argument("stage", StringArgumentType.word()).executes(c -> {
                    var player = c.getSource().getPlayerOrException();
                    return read(player, team(player), StringArgumentType.getString(c, "stage"));
                })))
                .then(Commands.literal("preview").then(Commands.argument("stage", StringArgumentType.word())
                        .then(Commands.argument("choice", IntegerArgumentType.integer(0, 1)).executes(c -> preview(
                                c.getSource().getPlayerOrException(), StringArgumentType.getString(c, "stage"), IntegerArgumentType.getInteger(c, "choice"))))))
                .then(Commands.literal("reply").then(Commands.argument("stage", StringArgumentType.word())
                        .then(Commands.argument("choice", IntegerArgumentType.integer(0, 1))
                                .then(Commands.argument("token", StringArgumentType.word()).executes(c -> reply(
                                        c.getSource().getPlayerOrException(), StringArgumentType.getString(c, "stage"),
                                        IntegerArgumentType.getInteger(c, "choice"), StringArgumentType.getString(c, "token")))))));
    }

    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent event) { clearPreview(event.getEntity().getUUID()); }
    @SubscribeEvent public static void stop(ServerStoppedEvent event) { DRAFTS.clear(); STOP_SESSIONS.clear(); }
}
