package com.sirin.hk3gtl.common.phone;

/** 【变更记录 #1】2026-09-29 18:57:18（内测5修订95）：服务端向本人发送手机主页与分页通知。 */
import java.util.function.Supplier;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.network.NetworkEvent;

/**
 * 【变更记录 #2】2026-09-30 16:20:43（内测5修订110）
 * 删除：被新版通知读取流程替代的旧分支，历史备注保留。
 * 新增／修改：网络处理延迟到客户端分发，专用服务端不在处理路径直接加载屏幕类。
 * 用途：通知与业务结果分离，服务端授权和个人持久化；不改结构、贴图和贸易。
 */
/** 【变更记录 #3】2026-10-01 00:44:40（修订123）：删除无；新增/修改：复用服务端只读包为实体卷轴提供正式经历，不开启免费手机；用途：个人交流、团队决定及额外收藏分开，保留真实记录。 */
public record Hk3PhonePacket(CompoundTag view) {
    public static void encode(Hk3PhonePacket p,FriendlyByteBuf b){b.writeNbt(p.view);}
    public static Hk3PhonePacket decode(FriendlyByteBuf b){var n=b.readNbt();return new Hk3PhonePacket(n==null?new CompoundTag():n);}
    public static void handle(Hk3PhonePacket p,Supplier<NetworkEvent.Context> context){
        context.get().enqueueWork(()->net.minecraftforge.fml.DistExecutor.unsafeRunWhenOn(net.minecraftforge.api.distmarker.Dist.CLIENT,
                ()->()->{
                    if(p.view.getString("Mode").equals("codex_progress"))com.sirin.hk3gtl.client.narrative.Hk3NarrativeCodexScreen.openProgress(p.view);
                    else com.sirin.hk3gtl.client.phone.Hk3PhoneScreen.open(p.view);
                }));
        context.get().setPacketHandled(true);
    }
}
