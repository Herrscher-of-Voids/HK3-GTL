package com.sirin.hk3gtl.test.phone;

import com.sirin.hk3gtl.common.phone.Hk3PhoneStatusRequestC2SPacket;
import io.netty.buffer.Unpooled;
import net.minecraft.network.Connection;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.protocol.PacketFlow;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.NetworkEvent;
import org.objectweb.asm.ClassReader;
import org.objectweb.asm.tree.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.BiConsumer;

public final class PhoneStatusPacketTest {
    private static void check(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }
    public static void main(String[] args) throws Exception {
        var buffer = new FriendlyByteBuf(Unpooled.buffer());
        try {
            Hk3PhoneStatusRequestC2SPacket.encode(new Hk3PhoneStatusRequestC2SPacket(), buffer);
            check(buffer.readableBytes() == 0, "后台请求不得携带客户端电量或身份");
            check(Hk3PhoneStatusRequestC2SPacket.decode(buffer) != null, "空载荷必须正常解码");
        } finally {
            buffer.release();
        }
        var constructor = NetworkEvent.Context.class.getDeclaredConstructor(Connection.class, NetworkDirection.class, BiConsumer.class);
        constructor.setAccessible(true);
        for (var direction : new NetworkDirection[]{NetworkDirection.PLAY_TO_SERVER, NetworkDirection.PLAY_TO_CLIENT}) {
            var context = constructor.newInstance(new Connection(PacketFlow.SERVERBOUND), direction, null);
            var calls = new AtomicInteger();
            Hk3PhoneStatusRequestC2SPacket.handle(new Hk3PhoneStatusRequestC2SPacket(), () -> {
                calls.incrementAndGet();
                return context;
            });
            check(context.getPacketHandled() && calls.get() == 1, "无发送者须直接处理完毕，不依赖服务端工作队列或读取手机");
        }
        var node = new ClassNode();
        try (var stream = PhoneStatusPacketTest.class.getResourceAsStream("/com/sirin/hk3gtl/client/phone/Hk3PhoneScreen.class")) {
            check(stream != null, "缺少生产手机屏幕字节码");
            new ClassReader(stream).accept(node, 0);
        }
        var tick = node.methods.stream().filter(method -> method.name.equals("tick") && method.desc.equals("()V")).findFirst().orElseThrow();
        boolean request = false, send = false;
        for (var instruction : tick.instructions) {
            if (instruction instanceof MethodInsnNode call) {
                check(!call.name.equals("command") && !call.name.equals("sendCommand"), "后台tick不得累积聊天命令垃圾计数");
                request |= call.owner.equals("com/sirin/hk3gtl/common/phone/Hk3PhoneStatusRequestC2SPacket") && call.name.equals("<init>");
                send |= call.owner.equals("net/minecraftforge/network/simple/SimpleChannel") && call.name.equals("sendToServer");
            }
        }
        check(request && send, "亮屏tick必须实际发送专用状态包");
        System.out.println("PhoneStatusPacketTest: transport and sender boundaries passed");
    }
}
