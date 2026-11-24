package com.sirin.hk3gtl.common.integration.ae.nexus.crafting;

import com.sirin.hk3gtl.common.config.Hk3AeSettings;
import appeng.api.networking.security.IActionHost;
import appeng.api.stacks.AEKey;
import appeng.menu.me.crafting.CraftAmountMenu;
import com.sirin.hk3gtl.common.network.Hk3ExactOrderStatusPacket;
import com.sirin.hk3gtl.common.network.Hk3Network;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.PacketDistributor;

import java.math.BigInteger;
import java.util.Map;
import java.util.UUID;
import java.util.WeakHashMap;

public final class Hk3NexusTerminalOrders {
    private record Watch(Hk3NexusCrafting crafting, AEKey target, UUID order) {}
    private static final Map<CraftAmountMenu, Watch> WATCHES = new WeakHashMap<>();

    private Hk3NexusTerminalOrders() {}

    public static boolean action(CraftAmountMenu menu, String action) {
        if (!(menu.getPlayer() instanceof ServerPlayer player) || player.containerMenu != menu || !menu.isValidMenu()) return false;
        Watch previous = WATCHES.get(menu);
        if (action.equals("leave") || action.equals("cancel_preview")) {
            if (previous == null) return false;
            if (previous.order() != null) previous.crafting().discardPreview(previous.order());
            WATCHES.remove(menu);
            return true;
        }
        if (!(menu.getTarget() instanceof IActionHost host) || menu.getWhatToCraft() == null) return false;
        var node = host.getActionableNode();
        if (node == null || !node.isActive()) return false;
        var runtimes = Hk3NexusCrafting.forGrid(node.getGrid());
        if (runtimes.isEmpty()) return false;
        var crafting = previous != null && runtimes.contains(previous.crafting()) ? previous.crafting() : runtimes.get(0);
        AEKey target = menu.getWhatToCraft().what();
        String[] parts = action.split(":", 2);
        String verb = parts[0];
        if ((verb.equals("preview") || verb.equals("start")) && !Hk3AeSettings.nexusPlannerEnabled()) return false;
        UUID id = parts.length == 2 && !verb.equals("preview") ? UUID.fromString(parts[1])
                : previous != null && previous.crafting() == crafting && previous.target().equals(target) ? previous.order() : null;
        if (verb.equals("preview")) {
            if (previous != null && previous.order() != null) previous.crafting().discardPreview(previous.order());
            BigInteger amount = new BigInteger(parts[1]);
            if (amount.signum() <= 0) throw new IllegalArgumentException("数量必须为正数");
            id = crafting.prepare(target, amount, player.getUUID());
        } else {
            if (id == null) {
                var owned = crafting.orders().stream().filter(order -> order.owner().equals(player.getUUID()) && order.target().equals(target)).toList();
                if (!owned.isEmpty()) id = owned.get(owned.size() - 1).id();
            }
            UUID selected = id;
            var order = crafting.orders().stream().filter(row -> row.id().equals(selected)).findFirst().orElse(null);
            if (order != null && (!order.owner().equals(player.getUUID()) || !order.target().equals(target)))
                throw new IllegalArgumentException("订单不属于当前玩家与目标");
            if (order != null) switch (verb) {
                case "start" -> crafting.confirm(id);
                case "pause" -> crafting.pause(id);
                case "resume" -> crafting.resume(id);
                case "cancel" -> crafting.cancel(id);
                case "status" -> { }
                default -> throw new IllegalArgumentException("未知天枢订单操作");
            }
        }
        WATCHES.put(menu, new Watch(crafting, target, id));
        UUID selected = id;
        var order = crafting.orders().stream().filter(row -> row.id().equals(selected)).findFirst().orElse(null);
        String text = "已连接万象天枢。数量、字节与执行次数直接使用大数；不经过原生long子单。\n";
        if (order == null) text += "当前目标没有天枢订单，请先规划。";
        else {
            text += "订单：" + order.id() + "\n目标：" + order.target().getDisplayName().getString()
                    + "\n数量：" + order.requested() + "\n剩余：" + order.remaining() + "\n计划字节：" + order.bytes()
                    + "\n状态：" + order.state() + (order.dispatchNote().isEmpty() ? "" : "\n派单：" + order.dispatchNote()) + "\n" + (crafting.confirmed(id) ? "已确认。" : "尚未确认，不会扣料或执行。") + "\n";
            for (var missing : order.missing().entrySet()) {
                text += "缺少：" + missing.getKey().getDisplayName().getString() + " × " + missing.getValue() + "\n";
                if (text.length() > 7000) break;
            }
        }
        if (text.length() > 8000) text = text.substring(0, 8000);
        Hk3Network.CHANNEL.send(PacketDistributor.PLAYER.with(() -> player), new Hk3ExactOrderStatusPacket(menu.containerId, id, text));
        return true;
    }
}
