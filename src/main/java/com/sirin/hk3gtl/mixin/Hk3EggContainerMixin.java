package com.sirin.hk3gtl.mixin;
import com.sirin.hk3gtl.common.easter.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.*;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import java.util.*;

@Mixin(AbstractContainerMenu.class)







public abstract class Hk3EggContainerMixin {
    @Unique private List<Hk3EggStorageFacts.Stack> hk3gtl$before=List.of(),hk3gtl$original=List.of(),hk3gtl$last=List.of();
    @Unique private boolean hk3gtl$changed,hk3gtl$filled64;
    @Unique private int hk3gtl$blanks=-1;
    @Unique private Hk3EggMenuTransactions.Snapshot hk3gtl$transaction;
    @Unique private Hk3EggAeDevices.View hk3gtl$devices;
    @Unique private Hk3EggVoltageSettings.Snapshot hk3gtl$voltage;
    @Unique private final Hk3EggMenuTransactions.Sorting hk3gtl$sorting=new Hk3EggMenuTransactions.Sorting();
    @Unique private final BitSet hk3gtl$authored=new BitSet(54);
    @Inject(method="clicked",at=@At("HEAD"))
    private void hk3gtl$before(int slot,int button,ClickType type,Player player,CallbackInfo ci){
        hk3gtl$before=List.of();hk3gtl$blanks=-1;hk3gtl$transaction=null;
        if(player instanceof ServerPlayer p&&p.containerMenu==(Object)this){
            if(net.minecraftforge.fml.ModList.get().isLoaded("gtlsupb"))hk3gtl$voltage=Hk3EggVoltageSettings.before(p,(AbstractContainerMenu)(Object)this);
            hk3gtl$devices=Hk3EggAeDevices.before((AbstractContainerMenu)(Object)this);
            hk3gtl$transaction=Hk3EggMenuTransactions.before(p,(AbstractContainerMenu)(Object)this);
            hk3gtl$blanks=Hk3EggAeMenus.blanks((AbstractContainerMenu)(Object)this);
            hk3gtl$before=Hk3EggContainers.snapshot((AbstractContainerMenu)(Object)this,p);
            if(!hk3gtl$last.isEmpty()){
                for(int i=hk3gtl$authored.nextSetBit(0);i>=0;i=hk3gtl$authored.nextSetBit(i+1))
                    if(i>=hk3gtl$before.size()||i>=hk3gtl$last.size()||!hk3gtl$before.get(i).equals(hk3gtl$last.get(i)))hk3gtl$authored.clear(i);
            }
            if(hk3gtl$original.isEmpty())hk3gtl$original=hk3gtl$before;
        }
    }
    @Inject(method="clicked",at=@At("RETURN"))
    private void hk3gtl$after(int slot,int button,ClickType type,Player player,CallbackInfo ci){
        if(hk3gtl$voltage!=null&&player instanceof ServerPlayer p)Hk3EggVoltageSettings.after(p,(AbstractContainerMenu)(Object)this,hk3gtl$voltage);hk3gtl$voltage=null;
        if(player instanceof ServerPlayer p)Hk3EggAeMenus.changed(p,(AbstractContainerMenu)(Object)this);
        if(player instanceof ServerPlayer p)Hk3EggAeDevices.after(p,(AbstractContainerMenu)(Object)this,hk3gtl$devices);hk3gtl$devices=null;
        if(player instanceof ServerPlayer p)Hk3EggMenuTransactions.after(p,(AbstractContainerMenu)(Object)this,hk3gtl$transaction,hk3gtl$sorting);hk3gtl$transaction=null;
        if(player instanceof ServerPlayer p)Hk3EggAeMenus.clicked(p,(AbstractContainerMenu)(Object)this,hk3gtl$blanks);hk3gtl$blanks=-1;
        if(player instanceof ServerPlayer p&&!hk3gtl$before.isEmpty()){
            var menu=(AbstractContainerMenu)(Object)this;var after=Hk3EggContainers.snapshot(menu,p);
            if(after.size()==hk3gtl$before.size()&&!after.equals(hk3gtl$before)){
                for(int i=0;i<after.size();i++)if(!after.get(i).equals(hk3gtl$before.get(i)))hk3gtl$authored.set(i);
                for(int i=0;i<after.size();i++)if(hk3gtl$before.get(i).count()==63&&after.get(i).count()==64&&hk3gtl$before.get(i).id().equals(after.get(i).id()))hk3gtl$filled64=true;
                hk3gtl$changed=true;hk3gtl$last=after;Hk3EggContainers.changed(p,menu,hk3gtl$before,after,hk3gtl$authored);
            }
        }hk3gtl$before=List.of();
    }
    @Inject(method="removed",at=@At("HEAD"))
    private void hk3gtl$closed(Player player,CallbackInfo ci){
        if(player instanceof ServerPlayer p&&hk3gtl$filled64&&hk3gtl$last.equals(Hk3EggContainers.snapshot((AbstractContainerMenu)(Object)this,p)))Hk3EggVanilla.caseEvent(p,317);
        hk3gtl$filled64=false;
        if(player instanceof ServerPlayer p)Hk3EggContainers.closed(p,(AbstractContainerMenu)(Object)this,hk3gtl$original,hk3gtl$last,hk3gtl$changed);
        hk3gtl$before=List.of();hk3gtl$original=List.of();hk3gtl$last=List.of();hk3gtl$changed=false;hk3gtl$authored.clear();
    }
}
