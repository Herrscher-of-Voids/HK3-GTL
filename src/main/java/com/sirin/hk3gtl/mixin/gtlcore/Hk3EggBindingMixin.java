package com.sirin.hk3gtl.mixin.gtlcore;
import org.gtlcore.gtlcore.integration.ae2.wireless.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.UseOnContext;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import java.util.UUID;
@Mixin(value=WirelessNetworkBindingToolItem.class,remap=false)
/** 【变更记录 #1】2026-10-01 05:20:36（修订128）：删除无；新增联动工具事务后置核验；修改无；用途：只观察真实提交，不修改联动结果，不授正式资格。 */
public abstract class Hk3EggBindingMixin {
    @Redirect(method="onItemUseFirst",at=@At(value="INVOKE",target="Lorg/gtlcore/gtlcore/integration/ae2/wireless/WirelessAeSavedData;addMember(Ljava/util/UUID;Lorg/gtlcore/gtlcore/integration/ae2/wireless/WirelessAeSavedData$MemberKey;)Z"))
    private boolean hk3gtl$bound(WirelessAeSavedData data,UUID network,WirelessAeSavedData.MemberKey target,ItemStack stack,UseOnContext context){
        boolean result=data.addMember(network,target);
        if(result&&context.getPlayer() instanceof ServerPlayer p&&network.equals(data.getMemberNetwork(target))&&WirelessAeNetworkRuntime.canAccessNetwork(p,network))com.sirin.hk3gtl.common.easter.Hk3EggVanilla.caseEvent(p,241);
        return result;
    }
}
