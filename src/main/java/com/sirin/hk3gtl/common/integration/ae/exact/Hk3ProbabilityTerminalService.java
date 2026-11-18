package com.sirin.hk3gtl.common.integration.ae.exact;

import appeng.api.networking.IGrid;
import appeng.api.networking.security.IActionHost;
import appeng.api.stacks.AEKey;
import appeng.menu.me.crafting.CraftAmountMenu;
import com.sirin.hk3gtl.common.network.Hk3Network;
import com.sirin.hk3gtl.common.network.Hk3ProbabilityOrderStatusPacket;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.network.PacketDistributor;

import java.io.IOException;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.WeakHashMap;

public final class Hk3ProbabilityTerminalService {
    private static final Map<CraftAmountMenu, Session> SESSIONS = new WeakHashMap<>();
    private static final Map<ServerPlayer, Long> ACTIONS = new WeakHashMap<>();

    private record Preview(List<Hk3ProbabilityOrderService.Candidate> routes, BigInteger amount,
                           BigInteger attempts, Map<AEKey, BigInteger> additional, CompoundTag quote, String description) {}

    private static final class Session {
        final IGrid grid;
        final AEKey target;
        List<Hk3ProbabilityOrderService.Candidate> candidates = List.of();
        final List<Hk3ProbabilityOrderService.Candidate> routes = new ArrayList<>();
        List<UUID> orders = List.of();
        List<AEKey> outputOptions = List.of();
        final Map<AEKey, BigInteger> additional = new LinkedHashMap<>();
        int candidateIndex;
        int outputIndex;
        UUID order;
        Preview preview;
        Hk3ProbabilityOrderStatusPacket last;

        Session(IGrid grid, AEKey target) {
            this.grid = grid;
            this.target = target;
        }
    }

    private Hk3ProbabilityTerminalService() {}

    public static void action(CraftAmountMenu menu, String action) {
        if (!(menu.getPlayer() instanceof ServerPlayer player) || player.containerMenu != menu
                || !menu.isValidMenu()) return;
        if (action.equals("leave")) { SESSIONS.remove(menu); return; }
        Session session = SESSIONS.get(menu);
        try {
            long now = player.server.getTickCount();
            Long previous = ACTIONS.get(player);
            require(previous == null || now - previous >= 10, "操作过快，请稍候重试");
            ACTIONS.put(player, now);
            var source = menu.getActionSource();
            if (!(menu.getTarget() instanceof IActionHost host) || source == null
                    || source.player().orElse(null) != player)
                throw new IllegalArgumentException("终端缺少本人的AE操作来源");
            var node = host.getActionableNode();
            if (node == null || !node.isActive()) throw new IllegalArgumentException("当前AE终端未连接有效网络");
            var target = menu.getWhatToCraft();
            if (target == null) throw new IllegalArgumentException("请先在AE终端选择概率目标资源");
            if (session == null || session.grid != node.getGrid() || !session.target.equals(target.what())) {
                session = new Session(node.getGrid(), target.what());
                SESSIONS.put(menu, session);
            }
            String[] parts = action.split("\\|", -1);
            String verb = parts[0];
            String note = "";
            switch (verb) {
                case "open", "scan" -> {
                    session.candidates = Hk3ProbabilityOrderService.candidates(player, session.grid, session.target);
                    session.candidateIndex = 0;
                    session.routes.clear();
                    session.additional.clear();
                    selectCandidate(player, session);
                }
                case "candidate_previous", "candidate_next" -> {
                    require(!session.candidates.isEmpty(), "没有可选的绑定总成，请重新查找");
                    session.candidateIndex = Math.floorMod(session.candidateIndex
                            + (verb.equals("candidate_next") ? 1 : -1), session.candidates.size());
                    selectCandidate(player, session);
                }
                case "route_add", "route_remove" -> {
                    require(!session.candidates.isEmpty(), "没有可选的绑定总成，请重新查找");
                    var candidate = session.candidates.get(session.candidateIndex);
                    if (verb.equals("route_add")) {
                        require(session.routes.size() < 16, "最多选择16条独占路线");
                        if (!session.routes.contains(candidate)) session.routes.add(candidate);
                    } else session.routes.remove(candidate);
                    selectCandidate(player, session);
                }
                case "goal_next", "goal_set", "goal_remove" -> {
                    require(!session.outputOptions.isEmpty(), "当前配方没有其他可选的固定数量产物");
                    if (verb.equals("goal_next")) {
                        session.outputIndex = (session.outputIndex + 1) % session.outputOptions.size();
                    } else {
                        var key = session.outputOptions.get(session.outputIndex);
                        if (verb.equals("goal_set")) {
                            require(parts.length == 2, "请填写附加目标数量");
                            session.additional.put(key, Hk3ExactOrder.parsePositiveDecimal(parts[1]));
                        } else session.additional.remove(key);
                        session.preview = null;
                    }
                }
                case "preview", "start" -> {
                    require(parts.length == 3, "订单须包含目标数量与尝试预算");
                    BigInteger amount = Hk3ExactOrder.parsePositiveDecimal(parts[1]);
                    BigInteger attempts = Hk3ExactOrder.parsePositiveDecimal(parts[2]);
                    require(!session.candidates.isEmpty(), "没有符合独占合同的概率总成");
                    var routes = routes(session);
                    require(Hk3ProbabilityOrderService.candidates(player, session.grid, session.target).containsAll(routes),
                            "原绑定已不在当前终端网络，或独占合同已变化，请重新查找");
                    if (verb.equals("preview")) {
                        session.preview = new Preview(routes, amount, attempts, Map.copyOf(session.additional),
                                Hk3ProbabilityOrderService.quote(player, routes, session.target),
                                Hk3ProbabilityOrderService.preview(player, routes, session.target, amount, attempts, session.additional));
                    } else {
                        var preview = session.preview;
                        require(preview != null && preview.routes().equals(routes)
                                && preview.amount().equals(amount) && preview.attempts().equals(attempts)
                                && preview.additional().equals(session.additional),
                                "绑定、数量或尝试预算已变化，请先重新预览");
                        require(preview.quote().equals(Hk3ProbabilityOrderService.quote(player, routes, session.target)),
                                "原机器、总成、样板或配方费用已变化，请重新预览");
                        session.order = Hk3ProbabilityOrderService.start(player, routes, session.target, amount, attempts, session.additional);
                        session.preview = null;
                        note = "概率订单已提交；按真实机器产出结算，原尝试预算不会自动增加。\n";
                    }
                }
                case "order_previous", "order_next" -> {
                    refreshOrders(player, session);
                    require(!session.orders.isEmpty(), "当前目标没有本人的概率订单");
                    int index = session.orders.indexOf(session.order);
                    session.order = session.orders.get(Math.floorMod(index
                            + (verb.equals("order_next") ? 1 : -1), session.orders.size()));
                }
                case "cancel", "resume", "claim", "forget" -> {
                    refreshOrders(player, session);
                    require(session.order != null, "请先选择本人的概率订单");
                    switch (verb) {
                        case "cancel" -> Hk3ProbabilityOrderService.cancel(player, session.order);
                        case "resume" -> Hk3ProbabilityOrderService.resume(player, session.order);
                        case "claim" -> note = "本次实际入库：" + Hk3ProbabilityOrderService.claim(player, session.order) + "\n";
                        case "forget" -> {
                            Hk3ProbabilityOrderService.forget(player, session.order);
                            session.order = null;
                            note = "已清理无在途、无托管余额的终态订单。\n";
                        }
                    }
                }
                case "status" -> { }
                default -> throw new IllegalArgumentException("未知概率订单动作");
            }
            refreshOrders(player, session);
            send(player, menu, session, note + describe(player, session));
        } catch (RuntimeException | IOException failure) {
            if (session != null) session.preview = null;
            send(player, menu, session, "操作未完成：" + failure.getMessage());
        }
    }

    public static void tick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || event.getServer().getTickCount() % 40 != 0) return;
        var iterator = SESSIONS.entrySet().iterator();
        while (iterator.hasNext()) {
            var item = iterator.next();
            var menu = item.getKey();
            var player = (ServerPlayer) menu.getPlayer();
            var session = item.getValue();
            if (player.containerMenu != menu || !menu.isValidMenu()) {
                iterator.remove();
                continue;
            }
            refreshOrders(player, session);
            String text = describe(player, session);
            if (text.length() > 8000) text = text.substring(0, 8000);
            var status = new Hk3ProbabilityOrderStatusPacket(menu.containerId, session.order,
                    session.candidates.size(), session.orders.size(), session.preview != null, text);
            if (!status.equals(session.last)) {
                session.last = status;
                send(player, status);
            }
        }
    }

    public static void loggedOut(ServerPlayer player) {
        SESSIONS.keySet().removeIf(menu -> menu.getPlayer() == player);
        ACTIONS.remove(player);
    }

    public static void stopped(ServerStoppedEvent event) {
        SESSIONS.clear();
        ACTIONS.clear();
    }

    private static void refreshOrders(ServerPlayer player, Session session) {
        session.orders = Hk3ProbabilityOrderService.orders(player, session.grid, session.target);
        if (session.order == null || !session.orders.contains(session.order))
            session.order = session.orders.isEmpty() ? null : session.orders.get(session.orders.size() - 1);
    }

    private static void selectCandidate(ServerPlayer player, Session session) {
        session.preview = null;
        session.outputIndex = 0;
        session.outputOptions = session.candidates.isEmpty() ? List.of()
                : Hk3ProbabilityOrderService.additionalTargets(player, routes(session), session.target);
        session.additional.keySet().retainAll(session.outputOptions);
    }

    private static List<Hk3ProbabilityOrderService.Candidate> routes(Session session) {
        return session.routes.isEmpty() ? List.of(session.candidates.get(session.candidateIndex)) : List.copyOf(session.routes);
    }

    private static String describe(ServerPlayer player, Session session) {
        var text = new StringBuilder("目标：").append(session.target.getDisplayName().getString());
        if (session.candidates.isEmpty()) text.append("\n没有可绑定总成：需64格内本人／本队标准HK宿主、同网络独占总成及单张1:1概率样板。");
        else text.append("\n绑定 ").append(session.candidateIndex + 1).append("/")
                .append(session.candidates.size()).append("：").append(session.candidates.get(session.candidateIndex).label());
        if (!session.routes.isEmpty()) {
            text.append("\n已选共享路线 ").append(session.routes.size()).append(" 条：");
            for (int i = 0; i < session.routes.size(); i++)
                text.append("\n").append(i + 1).append(". ").append(session.routes.get(i).label());
        }
        if (!session.outputOptions.isEmpty()) text.append("\n附加产物 ").append(session.outputIndex + 1).append('/')
                .append(session.outputOptions.size()).append("：")
                .append(session.outputOptions.get(session.outputIndex).getDisplayName().getString())
                .append("；用左侧数量框设定后，再填写主目标数量并预览。");
        session.additional.forEach((key, amount) -> text.append("\n附加目标：")
                .append(key.getDisplayName().getString()).append(" × ").append(amount)
                .append(key instanceof appeng.api.stacks.AEFluidKey ? " mB" : " 个"));
        if (session.preview != null) text.append("\n\n预算预览（尚未投料）：\n").append(session.preview.description());
        if (session.order != null) text.append("\n\n订单 ").append(session.orders.indexOf(session.order) + 1)
                .append("/").append(session.orders.size()).append("：\n")
                .append(Hk3ProbabilityOrderService.status(player, session.order));
        else text.append("\n当前目标没有本人的概率订单。");
        return text.append("\n全部目标满足后停止；每批保留真实一次抽取，所有已选路线共享原尝试上限。").toString();
    }

    private static void send(ServerPlayer player, CraftAmountMenu menu, Session session, String text) {
        if (text.length() > 8000) text = text.substring(0, 8000);
        var packet = new Hk3ProbabilityOrderStatusPacket(menu.containerId,
                session == null ? null : session.order, session == null ? 0 : session.candidates.size(),
                session == null ? 0 : session.orders.size(), session != null && session.preview != null, text);
        if (session != null) session.last = packet;
        send(player, packet);
    }

    private static void send(ServerPlayer player, Hk3ProbabilityOrderStatusPacket packet) {
        Hk3Network.CHANNEL.send(PacketDistributor.PLAYER.with(() -> player), packet);
    }

    private static void require(boolean accepted, String reason) {
        if (!accepted) throw new IllegalArgumentException(reason);
    }
}
