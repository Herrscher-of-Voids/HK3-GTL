package com.sirin.hk3gtl.client.phone;
import com.sirin.hk3gtl.common.network.Hk3Network;
import com.sirin.hk3gtl.common.easter.Hk3EggUiPacket;
/** 【变更记录 #1】2026-10-01 04:27:32（修订128）：删除无；新增手机具体操作回报；修改无；用途：只由实际保存/打开/关闭触发，无自动完成或跨系统奖励。 */
public final class Hk3EggUiClient {
    private Hk3EggUiClient(){}
    public static void send(String action,String value){if(net.minecraft.client.Minecraft.getInstance().getConnection()!=null)Hk3Network.CHANNEL.sendToServer(new Hk3EggUiPacket(action,value));}
}
