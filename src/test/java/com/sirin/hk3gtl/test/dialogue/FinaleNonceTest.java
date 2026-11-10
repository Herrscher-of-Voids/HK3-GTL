package com.sirin.hk3gtl.test.dialogue;

import com.sirin.hk3gtl.common.dialogue.DialogueSessionManager.DialogueSession;
import com.sirin.hk3gtl.common.network.*;
import io.netty.buffer.Unpooled;
import com.sirin.hk3gtl.common.finale.Hk3FinalePlayerMode;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.level.GameType;
import net.minecraft.network.FriendlyByteBuf;
import java.util.function.BiConsumer;
import java.util.function.Function;

/** 修订198：检查会话重开、同段循环及四种包的令牌往返，不代替实机网络验收。 */
public final class FinaleNonceTest {
    public static void run() {
        modes();
        var first = new DialogueSession("sirin_finale", "F06", 0, 41L);
        var resumed = new DialogueSession("sirin_finale", "F06", 0, 42L);
        check(first.accepts("sirin_finale", 41L), "当前令牌可用");
        check(!resumed.accepts("sirin_finale", 41L), "重开同段拒绝旧令牌");
        check(!resumed.accepts("sirin_finale", 0L), "无令牌拒绝");
        check(!resumed.accepts("preview", 42L), "跨对话令牌拒绝");
        var loop = new DialogueSession("sirin_finale", "F06", 0, 43L);
        check(!loop.accepts("sirin_finale", 42L), "循环返回同段仍拒绝旧选择与关闭");
        var generated = new DialogueSession("sirin_finale", "FU01", 0);
        check(generated.nonce() > 0, "服务端生成非零令牌");
        roundTrip(new DialogueOpenS2CPacket("sirin_finale", "F06", 31, 41L), DialogueOpenS2CPacket::encode, DialogueOpenS2CPacket::decode);
        roundTrip(new DialogueAdvanceS2CPacket("sirin_finale", "FU01", 31, 42L), DialogueAdvanceS2CPacket::encode, DialogueAdvanceS2CPacket::decode);
        roundTrip(new DialoguePlayerChoiceC2SPacket("sirin_finale", "F06", 2, 41L), DialoguePlayerChoiceC2SPacket::encode, DialoguePlayerChoiceC2SPacket::decode);
        roundTrip(new DialogueCloseC2SPacket("sirin_finale", true, 42L), DialogueCloseC2SPacket::encode, DialogueCloseC2SPacket::decode);
    }
    private static void modes() {
        for (GameType original : GameType.values()) {
            var first = new CompoundTag();
            var second = new CompoundTag();
            Hk3FinalePlayerMode.remember(first, original);
            Hk3FinalePlayerMode.remember(first, GameType.ADVENTURE);
            Hk3FinalePlayerMode.remember(second, GameType.SPECTATOR);
            var restored = new CompoundTag();
            com.sirin.hk3gtl.common.event.Hk3PlayerDataCloneHandler.copyPersistentState(first, restored);
            check(Hk3FinalePlayerMode.take(restored) == original, "恢复保留最初模式，不被同次重连覆盖");
            check(Hk3FinalePlayerMode.take(restored) == null, "恢复后清除旧模式，下次重新采集");
            check(Hk3FinalePlayerMode.take(second) == GameType.SPECTATOR, "不同玩家模式隔离");
            Hk3FinalePlayerMode.remember(restored, GameType.CREATIVE);
            check(Hk3FinalePlayerMode.take(restored) == GameType.CREATIVE, "后续入场重新保存当前个人模式");
        }
        check(Hk3FinalePlayerMode.take(new CompoundTag()) == null, "旧档缺原模式不编造历史");
    }
    private static <T> void roundTrip(T packet, BiConsumer<T, FriendlyByteBuf> encode, Function<FriendlyByteBuf, T> decode) {
        var input = new FriendlyByteBuf(Unpooled.buffer());
        var output = new FriendlyByteBuf(Unpooled.buffer());
        FriendlyByteBuf copy = null;
        try {
            encode.accept(packet, input);
            copy = new FriendlyByteBuf(input.copy());
            T restored = decode.apply(copy);
            check(!copy.isReadable(), "网络包字段完整读取");
            encode.accept(restored, output);
            check(input.equals(output), "网络字段与令牌往返一致");
            check(input.getLong(input.writerIndex() - Long.BYTES) != 0, "令牌确已写入网络包");
        } finally {
            if (copy != null) copy.release();
            input.release();
            output.release();
        }
    }
    private static void check(boolean value, String message) {
        if (!value) throw new AssertionError(message);
    }
}
