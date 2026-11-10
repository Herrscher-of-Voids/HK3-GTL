package com.sirin.hk3gtl.common.phone;

import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.NetworkEvent;
import java.util.function.Supplier;

/**
 * 【文件职责】手机亮屏后台状态请求；无客户端电量、玩家身份或权限载荷。
 * 【变更记录 #1】2026-11-01 00:36:24（第1次备注 · 内测5修订192）
 * 删除：无；新增：仅服务端接收、无发送者拒绝、服务端主线程状态采样请求。
 * 修改：后台轮询改经专用包调用原Hk3PhoneRuntime.poll，沿用安装检查、20tick限流及每次8EU耗电。
 * 用途：长篇阅读时后台状态更新不再累积原版聊天命令垃圾计数，不放宽正文或业务权限。
 */
public record Hk3PhoneStatusRequestC2SPacket() {
    public static void encode(Hk3PhoneStatusRequestC2SPacket packet, FriendlyByteBuf buffer) {}
    public static Hk3PhoneStatusRequestC2SPacket decode(FriendlyByteBuf buffer) {
        return new Hk3PhoneStatusRequestC2SPacket();
    }
    public static void handle(Hk3PhoneStatusRequestC2SPacket packet, Supplier<NetworkEvent.Context> supplier) {
        var context = supplier.get();
        var sender = context.getSender();
        if (context.getDirection() == NetworkDirection.PLAY_TO_SERVER && sender != null) {
            context.enqueueWork(() -> Hk3PhoneRuntime.poll(sender));
        }
        context.setPacketHandled(true);
    }
}
