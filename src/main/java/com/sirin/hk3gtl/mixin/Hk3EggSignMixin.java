package com.sirin.hk3gtl.mixin;
import net.minecraft.world.level.block.entity.SignBlockEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.network.FilteredText;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import java.util.List;
/** 【变更记录 #1】2026-10-01 04:51:18（修订128）：删除无；新增有编辑权限的告示牌真实保存观察；用途：拒绝蜡封与他人编辑包，读取保存后的过滤文本，不旁路原校验。 */
@Mixin(SignBlockEntity.class)
public abstract class Hk3EggSignMixin {
    @Unique private boolean hk3gtl$authorized;
    @Unique private net.minecraft.world.level.block.entity.SignText hk3gtl$previous;
    @Inject(method="updateSignText",at=@At("HEAD"))private void hk3gtl$before(Player p,boolean front,List<FilteredText> lines,CallbackInfo ci){var s=(SignBlockEntity)(Object)this;hk3gtl$authorized=p instanceof ServerPlayer&&!s.isWaxed()&&p.getUUID().equals(s.getPlayerWhoMayEdit());hk3gtl$previous=s.getText(front);}
    @Inject(method="updateSignText",at=@At("RETURN"))private void hk3gtl$after(Player p,boolean front,List<FilteredText> lines,CallbackInfo ci){var s=(SignBlockEntity)(Object)this;if(hk3gtl$authorized&&p instanceof ServerPlayer server&&hk3gtl$previous!=s.getText(front))com.sirin.hk3gtl.common.easter.Hk3EggDecor.sign(server,s,front);hk3gtl$previous=null;hk3gtl$authorized=false;}
}
