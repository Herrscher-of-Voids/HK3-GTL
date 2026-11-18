package com.sirin.hk3gtl.mixin.gtlcore;
import org.gtlcore.gtlcore.integration.ae2.wireless.*;
import net.minecraft.server.level.ServerPlayer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import java.util.UUID;
@Mixin(value=WirelessNetworkBindingToolItem.class,remap=false)
 
public abstract class Hk3EggBindingMixin {
    @Redirect(method="bindTo",at=@At(value="INVOKE",target="Lorg/gtlcore/gtlcore/integration/ae2/wireless/WirelessAeSavedData;addMember(Ljava/util/UUID;Lorg/gtlcore/gtlcore/integration/ae2/wireless/WirelessAeSavedData$MemberKey;)Z"))
    private static boolean hk3gtl$bound(WirelessAeSavedData data,UUID network,WirelessAeSavedData.MemberKey target,ServerPlayer player,WirelessAeSavedData.MemberKey bindingTarget,UUID bindingNetwork,boolean rebind){
        boolean result=data.addMember(network,target);
        if(result&&network.equals(data.getMemberNetwork(target))&&WirelessAeNetworkRuntime.canAccessNetwork(player,network))com.sirin.hk3gtl.common.easter.Hk3EggVanilla.caseEvent(player,241);
        return result;
    }
}
