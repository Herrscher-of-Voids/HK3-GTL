package com.sirin.hk3gtl.common.capability;

import com.sirin.hk3gtl.common.recipe.power.Hk3PortPayment;
import com.sirin.hk3gtl.common.recipe.power.Hk3PowerPorts;
import com.sirin.hk3gtl.common.util.Hk3LedgerValidation;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.MinecraftServer;

import java.math.BigInteger;
import java.util.UUID;

/** 只记录实际剩余改量和原账户；未知退款保留阻断项，不猜测返款。 */
public final class Hk3RefundActions {
    private Hk3RefundActions() {}

    public static Hk3RefundJournal.Action hw(HonkaiWirelessSavedData data, UUID account, BigInteger amount) {
        var tag = money("hw", account, amount);
        return action(tag, () -> data.insert(account, amount, false));
    }

    public static Hk3RefundJournal.Action grid(Hk3GridEnergyRefund source, BigInteger applied) {
        return action(money("grid", source.account(), applied), () -> source.undo(applied));
    }

    public static Hk3RefundJournal.Action action(CompoundTag snapshot, Runnable work) {
        var saved = snapshot.copy();
        return new Hk3RefundJournal.Action() {
            @Override public void run() { work.run(); }
            @Override public CompoundTag snapshot() { return saved.copy(); }
        };
    }

    private static CompoundTag money(String kind, UUID account, BigInteger amount) {
        var tag = new CompoundTag();
        tag.putString("Kind", kind);
        tag.putUUID("Account", account);
        tag.putString("Amount", amount.toString());
        return tag;
    }

    static Runnable restore(MinecraftServer server, HonkaiWirelessSavedData data, CompoundTag tag) {
        validate(tag);
        return switch (tag.getString("Kind")) {
            case "hw" -> hw(data, tag.getUUID("Account"), number(tag, "Amount"));
            case "grid" -> action(tag, () -> Hk3GridEnergyRefund.forAccount(server,
                    tag.getUUID("Account")).undo(number(tag, "Amount")));
            case "port" -> Hk3PortPayment.refund(Hk3PowerPorts.restore(server, tag.getCompound("Target")),
                    number(tag, "Left"));
            case "item", "fluid" -> Hk3MaterialTick.restore(server, tag);
            default -> action(tag, () -> { throw new IllegalStateException("未知退款动作，保留日志等待核对"); });
        };
    }

    static void validate(CompoundTag tag) {
        Hk3LedgerValidation.type(tag, "Kind", Tag.TAG_STRING);
        switch (tag.getString("Kind")) {
            case "hw", "grid" -> {
                Hk3LedgerValidation.require(tag.hasUUID("Account"), "原退款账户");
                var amount = number(tag, "Amount");
                Hk3LedgerValidation.require(tag.getString("Kind").equals("grid") || amount.signum() > 0, "HW退款金额");
            }
            case "port" -> {
                number(tag, "Left");
                Hk3LedgerValidation.type(tag, "Target", Tag.TAG_COMPOUND);
                Hk3RefundTarget.validate(tag.getCompound("Target"), true);
            }
            case "item", "fluid" -> Hk3MaterialTick.validate(tag);
            case "unsupported" -> Hk3LedgerValidation.type(tag, "Class", Tag.TAG_STRING);
            default -> throw new IllegalStateException("未知退款格式，拒绝重置账本");
        }
    }

    private static BigInteger number(CompoundTag tag, String key) {
        Hk3LedgerValidation.type(tag, key, Tag.TAG_STRING);
        String raw = tag.getString(key);
        Hk3LedgerValidation.require(raw.length() <= 65535 && raw.matches("-?(0|[1-9][0-9]*)"), "退款金额");
        return new BigInteger(raw);
    }
}
