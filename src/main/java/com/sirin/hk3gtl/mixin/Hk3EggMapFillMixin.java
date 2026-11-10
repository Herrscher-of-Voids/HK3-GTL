package com.sirin.hk3gtl.mixin;
import net.minecraft.world.item.MapItem;
import net.minecraft.world.level.Level;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.saveddata.maps.MapItemSavedData;
import net.minecraft.server.level.ServerPlayer;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(MapItem.class)
/** 【变更记录 #1】2026-10-01 12:18:50（修订128）：删除：无；新增/修改：本人真实地图更新从未填满到全部已填后记录区域，预制探索地图或单纯拿取不授完成；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public abstract class Hk3EggMapFillMixin {
    @Unique private boolean hk3gtl$wasIncomplete;
    @Inject(method="update",at=@At("HEAD"))private void hk3gtl$before(Level level,Entity viewer,MapItemSavedData map,CallbackInfo ci){hk3gtl$wasIncomplete=false;if(viewer instanceof ServerPlayer&&!map.locked)for(byte color:map.colors)if(color==0){hk3gtl$wasIncomplete=true;break;}}
    @Inject(method="update",at=@At("RETURN"))private void hk3gtl$after(Level level,Entity viewer,MapItemSavedData map,CallbackInfo ci){
        if(!hk3gtl$wasIncomplete||!(viewer instanceof ServerPlayer p))return;hk3gtl$wasIncomplete=false;for(byte color:map.colors)if(color==0)return;
        var s=com.sirin.hk3gtl.common.easter.Hk3EggRuntime.state(p);s.putBoolean("filledMap",true);s.putString("filledMapDim",map.dimension.location().toString());s.putInt("filledMapX",map.centerX);s.putInt("filledMapZ",map.centerZ);s.putInt("filledMapScale",map.scale);
    }
}
