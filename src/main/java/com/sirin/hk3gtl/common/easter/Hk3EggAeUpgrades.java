package com.sirin.hk3gtl.common.easter;
import appeng.parts.automation.UpgradeablePart;
import appeng.core.definitions.AEItems;
import appeng.menu.implementations.UpgradeableMenu;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.inventory.AbstractContainerMenu;
import java.util.*;
/** 【变更记录 #1】2026-10-01 06:31:11（修订128）：删除无；新增联动真实安装/传输观察；修改无；用途：模拟、仅持有与空过滤不冒充成功，按本人安装归属。 */
public final class Hk3EggAeUpgrades {
    private Hk3EggAeUpgrades(){}
    public static List<Integer> snapshot(AbstractContainerMenu menu){
        if(!(menu instanceof UpgradeableMenu<?> ae)||!(ae.getHost() instanceof UpgradeablePart part))return List.of();
        return List.of(part.getUpgrades().getInstalledUpgrades(AEItems.SPEED_CARD),part.getUpgrades().getInstalledUpgrades(AEItems.REDSTONE_CARD),part.getUpgrades().getInstalledUpgrades(AEItems.INVERTER_CARD),part.getUpgrades().getInstalledUpgrades(AEItems.FUZZY_CARD));
    }
    private static String key(UpgradeablePart part,int card){return "hk3EggAeCard_"+part.getSide().getName()+"_"+card;}
    public static void installed(ServerPlayer p,AbstractContainerMenu menu,List<Integer> before){
        if(before.size()!=4||p.containerMenu!=menu||!menu.stillValid(p)||!(menu instanceof UpgradeableMenu<?> ae)||!(ae.getHost() instanceof UpgradeablePart part))return;
        var after=snapshot(menu);var be=part.getHost().getBlockEntity();
        for(int i=0;i<4;i++)if(after.get(i)>before.get(i)){be.getPersistentData().putUUID(key(part,i),p.getUUID());be.setChanged();}else if(after.get(i)==0){be.getPersistentData().remove(key(part,i));be.setChanged();}
    }
    public static void cleared(appeng.parts.AEBasePart part){if(part instanceof UpgradeablePart u&&u.getHost()!=null&&u.getSide()!=null){var be=u.getHost().getBlockEntity();for(int i=0;i<4;i++)be.getPersistentData().remove(key(u,i));be.setChanged();}}
    public static void receipt(UpgradeablePart part,int card,int egg,boolean witness){
        var be=part.getHost().getBlockEntity();if(!(be.getLevel() instanceof net.minecraft.server.level.ServerLevel level)||!be.getPersistentData().hasUUID(key(part,card)))return;
        var owner=be.getPersistentData().getUUID(key(part,card));
        if(witness){var p=level.getServer().getPlayerList().getPlayer(owner);if(p==null||p.level()!=level||p.position().distanceToSqr(net.minecraft.world.phys.Vec3.atCenterOf(be.getBlockPos()))>256)return;}
        Hk3EggProductionData.get(level.getServer()).produced(owner,"receipt:"+egg,1);
    }
}
