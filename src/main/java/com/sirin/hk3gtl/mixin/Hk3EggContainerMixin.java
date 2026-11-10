package com.sirin.hk3gtl.mixin;
import com.sirin.hk3gtl.common.easter.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.*;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import java.util.*;
/** 【变更记录 #1】2026-10-01 04:12:10（修订128）：删除无；新增菜单点击前后及关闭快照；修改无；用途：仅有效服务器本人点击，失败不发记录；状态随菜单释放，不缓存世界引用。 */
@Mixin(AbstractContainerMenu.class)
/** 【变更记录 #2】2026-10-01 04:30:25（修订128）：删除：旧固定上限或被替代的分支；新增/修改：菜单级本人操作凭据随关闭释放，不保留全服容器引用；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #3】2026-10-01 04:41:04（修订128）：删除：旧固定上限或被替代的分支；新增/修改：每次点击前撤销已被外部变化覆盖的槽位归属，避免自动化内容被记作本人布局；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #4】2026-10-01 04:43:52（修订128）：删除：旧固定上限或被替代的分支；新增/修改：逐槽确认63补到64后关闭时仍保留真实布局，跨菜单不串计；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #5】2026-10-01 05:24:14（修订128）：删除：旧固定上限或被替代的分支；新增/修改：空白样板槽只对本人合法点击前后真实增加计数，不接受假槽预览；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #6】2026-10-01 06:01:37（修订128）：删除：无；新增/修改：切石成品与背包整理采用同次服务器点击前后守恒快照，预览无产出不计；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #7】2026-10-01 06:03:54（修订128）：删除：无；新增/修改：AE真实单元识别与容量卡实际扩槽仅观察本人菜单点击前后；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #8】2026-10-01 06:19:47（修订128）：删除：无；新增/修改：AE单元工作台只读资格在真实点击后即时撤销；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public abstract class Hk3EggContainerMixin {
    @Unique private List<Hk3EggStorageFacts.Stack> hk3gtl$before=List.of(),hk3gtl$original=List.of(),hk3gtl$last=List.of();
    @Unique private boolean hk3gtl$changed,hk3gtl$filled64;
    @Unique private int hk3gtl$blanks=-1;
    @Unique private Hk3EggMenuTransactions.Snapshot hk3gtl$transaction;
    @Unique private Hk3EggAeDevices.View hk3gtl$devices;
    @Unique private final Hk3EggMenuTransactions.Sorting hk3gtl$sorting=new Hk3EggMenuTransactions.Sorting();
    @Unique private final BitSet hk3gtl$authored=new BitSet(54);
    @Inject(method="clicked",at=@At("HEAD"))
    private void hk3gtl$before(int slot,int button,ClickType type,Player player,CallbackInfo ci){
        hk3gtl$before=List.of();hk3gtl$blanks=-1;hk3gtl$transaction=null;
        if(player instanceof ServerPlayer p&&p.containerMenu==(Object)this){
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
