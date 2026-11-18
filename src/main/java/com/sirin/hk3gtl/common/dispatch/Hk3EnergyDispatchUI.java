package com.sirin.hk3gtl.common.dispatch;

import com.gregtechceu.gtceu.api.gui.GuiTextures;
import com.gregtechceu.gtceu.api.gui.UITemplate;
import com.lowdragmc.lowdraglib.gui.modular.ModularUI;
import com.lowdragmc.lowdraglib.gui.texture.GuiTextureGroup;
import com.lowdragmc.lowdraglib.gui.texture.TextTexture;
import com.lowdragmc.lowdraglib.gui.widget.ButtonWidget;
import com.lowdragmc.lowdraglib.gui.widget.LabelWidget;
import com.lowdragmc.lowdraglib.gui.widget.TextFieldWidget;
import com.sirin.hk3gtl.common.machine.research.Hk3LateIndustrialMachine;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;

public final class Hk3EnergyDispatchUI {
    private Hk3EnergyDispatchUI() {}

    public static ModularUI create(Hk3LateIndustrialMachine hub, Player player) {
        var session = new Selection(hub);
        return new ModularUI(330, 316, hub, player).background(GuiTextures.BACKGROUND)
                .widget(new LabelWidget(8, 8, "I41 文明能源调度 · 本人账户"))
                .widget(new LabelWidget(8, 24, "潜行右击：原工艺界面 · RN-CED解锁手动控制"))
                .widget(new TextFieldWidget(8, 43, 314, 16, () -> session.dimension, value -> session.dimension = value)
                        .setResourceLocationOnly().setMaxStringLength(128))
                .widget(new TextFieldWidget(8, 64, 100, 16, () -> Integer.toString(session.x), value -> session.x = Integer.parseInt(value))
                        .setNumbersOnly(-30_000_000, 30_000_000))
                .widget(new TextFieldWidget(115, 64, 100, 16, () -> Integer.toString(session.y), value -> session.y = Integer.parseInt(value))
                        .setNumbersOnly(-20_000, 20_000))
                .widget(new TextFieldWidget(222, 64, 100, 16, () -> Integer.toString(session.z), value -> session.z = Integer.parseInt(value))
                        .setNumbersOnly(-30_000_000, 30_000_000))
                .widget(button(8, 87, 100, "登记负载", () -> session.message = Hk3EnergyDispatch.register(hub,
                        (ServerPlayer) player, session.dimension, session.pos())))
                .widget(button(115, 87, 100, "手动启用", () -> session.message = Hk3EnergyDispatch.control(hub,
                        (ServerPlayer) player, session.dimension, session.pos(), true)))
                .widget(button(222, 87, 100, "手动暂停", () -> session.message = Hk3EnergyDispatch.control(hub,
                        (ServerPlayer) player, session.dimension, session.pos(), false)))
                .widget(button(8, 112, 100, "上一登记", () -> session.select(hub, (ServerPlayer) player, -1)))
                .widget(button(115, 112, 100, "下一登记", () -> session.select(hub, (ServerPlayer) player, 1)))
                .widget(button(222, 112, 100, "撤销登记", () -> session.message = Hk3EnergyDispatch.unregister(hub,
                        (ServerPlayer) player, session.dimension, session.pos())))
                .widget(new LabelWidget(8, 142, () -> session.message))
                .widget(new LabelWidget(8, 161, () -> hub.isRemote() ? "" : Hk3EnergyDispatch.status(hub,
                        (ServerPlayer) player, session.dimension, session.pos())))
                .widget(button(8, 184, 314, "新建交接工单（两台以上已暂停负载）", () -> {
                    var order = Hk3EnergyDispatch.newOrder(hub, (ServerPlayer) player);
                    session.message = order == null ? "工单未建立，见消息" : "已建立交接工单：" + order.toString().substring(0, 8);
                }))
                .widget(new LabelWidget(8, 211, "启用 → 实际HW工作与出料 → 暂停，形成控制时间线"))
                .widget(UITemplate.bindPlayerInventory(player.getInventory(), GuiTextures.SLOT, 77, 232, true));
    }

    private static ButtonWidget button(int x, int y, int width, String title, Runnable action) {
        return new ButtonWidget(x, y, width, 20, new GuiTextureGroup(GuiTextures.BUTTON, new TextTexture(title)),
                click -> { if (!click.isRemote) action.run(); });
    }

    private static final class Selection {
        String dimension;
        int x, y, z, index = -1;
        String message = "输入负载主控坐标，登记后手动启停";
        Selection(Hk3LateIndustrialMachine hub) {
            dimension = hub.getLevel().dimension().location().toString();
            x = hub.getPos().getX(); y = hub.getPos().getY(); z = hub.getPos().getZ();
        }
        BlockPos pos() { return new BlockPos(x, y, z); }
        void select(Hk3LateIndustrialMachine hub, ServerPlayer actor, int delta) {
            if (!actor.getUUID().equals(hub.getOwnerUUID())) { message = "此主控绑定其他玩家账户"; return; }
            var rows = Hk3EnergyDispatch.registered(hub);
            if (rows.isEmpty()) { message = "尚无登记负载"; return; }
            index = Math.floorMod(index + delta, rows.size());
            var row = rows.get(index);
            dimension = row.getString("Dimension");
            var pos = BlockPos.of(row.getLong("Position"));
            x = pos.getX(); y = pos.getY(); z = pos.getZ();
            message = "登记负载 " + (index + 1) + "/" + rows.size() + "：" + pos.toShortString();
        }
    }
}
