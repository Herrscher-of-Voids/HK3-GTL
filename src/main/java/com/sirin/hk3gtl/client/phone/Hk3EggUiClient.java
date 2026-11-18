package com.sirin.hk3gtl.client.phone;
import com.sirin.hk3gtl.common.network.Hk3Network;
import com.sirin.hk3gtl.common.easter.Hk3EggUiPacket;

public final class Hk3EggUiClient {
    private Hk3EggUiClient(){}
    public static void send(String action,String value){if(net.minecraft.client.Minecraft.getInstance().getConnection()!=null)Hk3Network.CHANNEL.sendToServer(new Hk3EggUiPacket(action,value));}
}
