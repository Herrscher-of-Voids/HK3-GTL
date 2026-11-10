package com.sirin.hk3gtl.mixin.gtlsupb;
import com.gtlsupb.gtlsupb.common.item.PatternModifier;
import com.gregtechceu.gtceu.api.blockentity.MetaMachineBlockEntity;
import org.gtlcore.gtlcore.common.machine.multiblock.part.ae.MEPatternBufferPartMachine;
import appeng.api.inventories.InternalInventory;
import appeng.api.crafting.PatternDetailsHelper;
import appeng.blockentity.networking.CableBusBlockEntity;
import appeng.helpers.patternprovider.PatternProviderLogicHost;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.phys.Vec3;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import java.util.*;
@Mixin(value=PatternModifier.class,remap=false)
/** 【变更记录 #1】2026-10-01 05:20:36（修订128）：删除无；新增联动工具事务后置核验；修改无；用途：只观察真实提交，不修改联动结果，不授正式资格。 */
/** 【变更记录 #2】2026-10-01 05:21:03（修订128）：删除：旧固定上限或被替代的分支；新增/修改：使用当前GTLCore提供的样板总线类型，修正编译期包名；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public abstract class Hk3EggModifierMixin {
    @Unique private final ThreadLocal<List<ItemStack>> hk3gtl$before=new ThreadLocal<>();
    @Unique private final ThreadLocal<InternalInventory> hk3gtl$inventory=new ThreadLocal<>();
    @Unique private static InternalInventory hk3gtl$target(UseOnContext c){
        var tile=c.getLevel().getBlockEntity(c.getClickedPos());Object host=tile;
        if(tile instanceof CableBusBlockEntity cable){var pos=c.getClickedPos();Vec3 hit=c.getClickLocation().subtract(pos.getX(),pos.getY(),pos.getZ());host=cable.getCableBus().selectPartLocal(hit).part;}
        if(host instanceof PatternProviderLogicHost provider&&provider.getLogic()!=null)return provider.getLogic().getPatternInv();
        if(tile instanceof MetaMachineBlockEntity machine&&machine.getMetaMachine() instanceof MEPatternBufferPartMachine buffer)return buffer.getTerminalPatternInventory();
        return null;
    }
    @Inject(method="useOn",at=@At("HEAD"))
    private void hk3gtl$before(UseOnContext c,CallbackInfoReturnable<InteractionResult> cir){
        hk3gtl$before.remove();hk3gtl$inventory.remove();if(!(c.getPlayer() instanceof ServerPlayer p)||!p.isShiftKeyDown())return;
        var inv=hk3gtl$target(c);if(inv==null||inv.size()>4096)return;
        var copy=new ArrayList<ItemStack>();for(int i=0;i<inv.size();i++)copy.add(inv.getStackInSlot(i).copy());hk3gtl$before.set(copy);hk3gtl$inventory.set(inv);
    }
    @Inject(method="useOn",at=@At("RETURN"))
    private void hk3gtl$after(UseOnContext c,CallbackInfoReturnable<InteractionResult> cir){
        var before=hk3gtl$before.get();var inv=hk3gtl$inventory.get();hk3gtl$before.remove();hk3gtl$inventory.remove();
        if(before==null||inv==null||!(c.getPlayer() instanceof ServerPlayer p)||before.size()!=inv.size())return;
        for(int i=0;i<inv.size();i++){var old=before.get(i);var after=inv.getStackInSlot(i);
            if(!old.isEmpty()&&!after.isEmpty()&&!ItemStack.matches(old,after)&&PatternDetailsHelper.decodePattern(old,p.level())!=null&&PatternDetailsHelper.decodePattern(after,p.level())!=null){com.sirin.hk3gtl.common.easter.Hk3EggVanilla.caseEvent(p,261);break;}
        }
    }
}
