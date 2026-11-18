package com.sirin.hk3gtl.common.capability;

import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.sirin.hk3gtl.common.util.Hk3LedgerValidation;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.MinecraftServer;

import java.util.List;
import java.util.function.Consumer;
import java.util.function.Function;

/** 正常保存时把未完成退款与HW放入同一账本；跨文件硬崩原子性不在此保证范围。 */
public final class Hk3RefundJournal {
    public interface Action extends Runnable { CompoundTag snapshot(); }
    private Hk3RefundJournal() {}

    public static Hk3EnergyTick open(MetaMachine machine) {
        var target = Hk3RefundTarget.capture(machine);
        var data = HonkaiWirelessNetwork.journalData(target.server());
        String key = Hk3RefundTarget.key(machine);
        if (data.pendingRefund(key) != null) throw new IllegalStateException("旧退款未完成，禁止开启新工作");
        return new Hk3EnergyTick(checkpoint(data, key, target.address()));
    }

    public static Hk3EnergyTick resume(MetaMachine machine) {
        MinecraftServer server = machine.getLevel().getServer();
        var data = HonkaiWirelessNetwork.journalData(server);
        String key = Hk3RefundTarget.key(machine);
        var pending = data.pendingRefund(key);
        if (pending == null) return null;
        var controller = pending.getCompound("Controller");
        if (new Hk3RefundTarget(server, controller).machine() != machine)
            throw new IllegalStateException("控制器退款身份不匹配");
        return restore(data, key, row -> Hk3RefundActions.restore(server, data, row));
    }

    static Consumer<List<Runnable>> checkpoint(HonkaiWirelessSavedData data, String key, CompoundTag controller) {
        return pending -> {
            if (pending.isEmpty()) { data.putPendingRefund(key, controller, null); return; }
            var row = new CompoundTag();
            row.putInt("Version", 1);
            row.putString("Key", key);
            row.put("Controller", controller.copy());
            var actions = new ListTag();
            for (Runnable refund : pending) {
                CompoundTag action;
                try {
                    action = refund instanceof Action durable ? durable.snapshot() : unsupported(refund);
                    Hk3RefundActions.validate(action);
                }
                catch (RuntimeException unknown) { action = unsupported(refund); }
                actions.add(action);
            }
            row.put("Actions", actions);
            validate(row);
            data.putPendingRefund(key, controller, row);
        };
    }

    static Hk3EnergyTick restore(HonkaiWirelessSavedData data, String key, Function<CompoundTag, Runnable> decode) {
        var row = data.pendingRefund(key);
        if (row == null) return null;
        validate(row);
        var pending = row.getList("Actions", Tag.TAG_COMPOUND).stream()
                .map(tag -> decode.apply(((CompoundTag) tag).copy())).toList();
        return Hk3EnergyTick.refunding(pending, checkpoint(data, key, row.getCompound("Controller")));
    }

    private static CompoundTag unsupported(Runnable refund) {
        var tag = new CompoundTag();
        tag.putString("Kind", "unsupported");
        tag.putString("Class", refund.getClass().getName());
        return tag;
    }

    static void validate(CompoundTag row) {
        Hk3LedgerValidation.type(row, "Version", Tag.TAG_INT);
        Hk3LedgerValidation.require(row.getInt("Version") == 1, "退款日志版本");
        Hk3LedgerValidation.type(row, "Key", Tag.TAG_STRING);
        Hk3LedgerValidation.type(row, "Controller", Tag.TAG_COMPOUND);
        var controller = row.getCompound("Controller");
        Hk3RefundTarget.validate(controller, false);
        Hk3LedgerValidation.require(row.getString("Key").equals(controller.getString("Dimension") + "/"
                + controller.getLong("Position")), "退款控制器索引");
        var actions = Hk3LedgerValidation.list(row, "Actions", Tag.TAG_COMPOUND);
        Hk3LedgerValidation.require(!actions.isEmpty(), "空退款日志");
        for (Tag action : actions) Hk3RefundActions.validate((CompoundTag) action);
    }
}
