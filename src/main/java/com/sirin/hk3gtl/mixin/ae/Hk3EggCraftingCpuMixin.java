package com.sirin.hk3gtl.mixin.ae;
import appeng.crafting.execution.CraftingCpuLogic;
import appeng.me.cluster.implementations.CraftingCPUCluster;
import appeng.api.networking.crafting.*;
import appeng.api.networking.IGrid;
import appeng.api.networking.security.IActionSource;
import appeng.api.networking.energy.IEnergyService;
import appeng.me.service.CraftingService;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.*;
import net.minecraft.core.registries.BuiltInRegistries;
import java.util.UUID;
import com.sirin.hk3gtl.common.easter.*;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.*;
@Mixin(value=CraftingCpuLogic.class,remap=false)
/** 【变更记录 #1】2026-10-01 06:27:59（修订128）：删除无；新增AE实际提交、完成与转化回执；修改无；用途：失败、取消、模拟及创造拿取不当生产，归属写入CPU存档。 */
public abstract class Hk3EggCraftingCpuMixin {
    @Shadow @Final CraftingCPUCluster cluster;
    @Shadow @Final private int[] usedOps;
    @Unique private UUID hk3gtl$owner,hk3gtl$token;
    @Unique private boolean hk3gtl$small,hk3gtl$coprocessor,hk3gtl$parallel,hk3gtl$palindrome;
    @Inject(method="trySubmitJob",at=@At("RETURN"))private void hk3gtl$submit(IGrid grid,ICraftingPlan plan,IActionSource source,ICraftingRequester requester,CallbackInfoReturnable<ICraftingSubmitResult> ci){
        if(!ci.getReturnValue().successful())return;
        hk3gtl$owner=null;hk3gtl$token=null;hk3gtl$small=false;hk3gtl$coprocessor=false;hk3gtl$parallel=false;hk3gtl$palindrome=plan.finalOutput().amount()==1221;
        var actor=source.player().orElse(null);if(!(actor instanceof ServerPlayer p))return;hk3gtl$owner=p.getUUID();hk3gtl$token=UUID.randomUUID();
        var blocks=cluster.getBlockEntities();net.minecraft.core.BlockPos first=null;
        while(blocks.hasNext()){var b=blocks.next();if(first==null)first=b.getBlockPos();String id=BuiltInRegistries.BLOCK.getKey(b.getBlockState().getBlock()).toString();hk3gtl$small|=id.equals("ae2:1k_crafting_storage");hk3gtl$coprocessor|=id.equals("ae2:crafting_accelerator");}
        if(first!=null)Hk3EggCraftingReceipts.started(p,hk3gtl$token,first,cluster.getLevel().dimension().location().toString());cluster.markDirty();
    }
    @Inject(method="tickCraftingLogic",at=@At("RETURN"))private void hk3gtl$parallel(IEnergyService energy,CraftingService crafting,CallbackInfo ci){if(hk3gtl$owner!=null&&usedOps[0]>1&&!hk3gtl$parallel){hk3gtl$parallel=true;cluster.markDirty();}}
    @Inject(method="finishJob",at=@At("RETURN"))private void hk3gtl$finished(boolean success,CallbackInfo ci){
        if(hk3gtl$owner!=null&&cluster.getLevel() instanceof ServerLevel level){
            var data=Hk3EggProductionData.get(level.getServer());if(success){if(hk3gtl$small)data.produced(hk3gtl$owner,"receipt:209",1);if(hk3gtl$coprocessor&&hk3gtl$parallel)data.produced(hk3gtl$owner,"receipt:210",1);if(hk3gtl$palindrome)data.produced(hk3gtl$owner,"receipt:335",1);}
            var p=level.getServer().getPlayerList().getPlayer(hk3gtl$owner);if(p!=null)Hk3EggCraftingReceipts.finished(p,hk3gtl$token,success);
        }
        hk3gtl$owner=null;hk3gtl$token=null;cluster.markDirty();
    }
    @Inject(method="writeToNBT",at=@At("RETURN"))private void hk3gtl$save(CompoundTag tag,CallbackInfo ci){
        tag.remove("hk3EggJob");if(hk3gtl$owner==null)return;var n=new CompoundTag();n.putUUID("owner",hk3gtl$owner);if(hk3gtl$token!=null)n.putUUID("token",hk3gtl$token);n.putBoolean("small",hk3gtl$small);n.putBoolean("coprocessor",hk3gtl$coprocessor);n.putBoolean("parallel",hk3gtl$parallel);n.putBoolean("palindrome",hk3gtl$palindrome);tag.put("hk3EggJob",n);
    }
    @Inject(method="readFromNBT",at=@At("RETURN"))private void hk3gtl$load(CompoundTag tag,CallbackInfo ci){var n=tag.getCompound("hk3EggJob");hk3gtl$owner=n.hasUUID("owner")?n.getUUID("owner"):null;hk3gtl$token=n.hasUUID("token")?n.getUUID("token"):null;hk3gtl$small=n.getBoolean("small");hk3gtl$coprocessor=n.getBoolean("coprocessor");hk3gtl$parallel=n.getBoolean("parallel");hk3gtl$palindrome=n.getBoolean("palindrome");}
}
