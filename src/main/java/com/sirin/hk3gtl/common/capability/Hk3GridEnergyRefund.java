package com.sirin.hk3gtl.common.capability;

import com.hepdd.gtmthings.api.misc.GlobalVariableStorage;
import com.hepdd.gtmthings.data.WirelessEnergySavaedData;
import com.hepdd.gtmthings.utils.TeamUtil;
import net.minecraft.server.MinecraftServer;
import net.minecraftforge.server.ServerLifecycleHooks;

import java.math.BigInteger;
import java.util.Map;
import java.util.UUID;







public record Hk3GridEnergyRefund(MinecraftServer server, Map<UUID, BigInteger> accounts,
                                  WirelessEnergySavaedData data, UUID account) {
    public static Hk3GridEnergyRefund capture(MinecraftServer server, UUID owner) {
        if (server == null || !server.isSameThread() || server != ServerLifecycleHooks.getCurrentServer()
                || WirelessEnergySavaedData.INSTANCE == null)
            throw new IllegalStateException("EU账本未就绪或不在服务器线程");
        return forAccount(server, TeamUtil.getTeamUUID(owner));
    }

    public static Hk3GridEnergyRefund forAccount(MinecraftServer server, UUID account) {
        if (server == null || !server.isSameThread() || server != ServerLifecycleHooks.getCurrentServer()
                || WirelessEnergySavaedData.INSTANCE == null || account == null)
            throw new IllegalStateException("原EU退款账户未就绪");
        return new Hk3GridEnergyRefund(server, GlobalVariableStorage.GlobalEnergy,
                WirelessEnergySavaedData.INSTANCE, account);
    }

    public void undo(BigInteger applied) {
        if (server != ServerLifecycleHooks.getCurrentServer() || !server.isSameThread()
                || accounts != GlobalVariableStorage.GlobalEnergy || data != WirelessEnergySavaedData.INSTANCE)
            throw new IllegalStateException("EU退款账本已变化，拒绝跨存档写入");
        // 已核对GTMThings及GTLADD实际余额均存于此表；不经TeamUtil二次映射原团队UUID。
        reverse(accounts, account, applied, data::setDirty);
    }

    public static void reverse(Map<UUID, BigInteger> accounts, UUID account, BigInteger applied, Runnable markDirty) {
        synchronized (accounts) {
            BigInteger restored = accounts.getOrDefault(account, BigInteger.ZERO).subtract(applied);
            if (restored.signum() < 0) throw new IllegalStateException("EU产出已被外部消费，等待可逆退款");
            markDirty.run();
            accounts.put(account, restored);
        }
    }
}
