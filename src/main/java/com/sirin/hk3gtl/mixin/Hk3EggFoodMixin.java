package com.sirin.hk3gtl.mixin;
import net.minecraft.world.food.FoodData;
import net.minecraft.world.entity.player.Player;
import net.minecraft.server.level.ServerPlayer;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(FoodData.class)
public abstract class Hk3EggFoodMixin {
    @Unique private float hk3gtl$health;
    @Inject(method="tick",at=@At("HEAD"))private void hk3gtl$before(Player p,CallbackInfo ci){hk3gtl$health=p.getHealth();}
    @Inject(method="tick",at=@At("RETURN"))private void hk3gtl$after(Player p,CallbackInfo ci){
        if(!(p instanceof ServerPlayer server))return;var s=com.sirin.hk3gtl.common.easter.Hk3EggRuntime.state(server);
        if(p.getHealth()>=p.getMaxHealth()){
            if(p.getHealth()>hk3gtl$health&&s.getBoolean("foodRecovery"))com.sirin.hk3gtl.common.easter.Hk3EggVanilla.caseEvent(server,443);
            s.remove("foodRecovery");
        }
    }
}
