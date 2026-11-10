package com.sirin.hk3gtl.common.easter;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.feature.IRecipeLogicMachine;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.capability.recipe.*;
import it.unimi.dsi.fastutil.objects.Object2IntMap;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.entity.BlockEntity;
import java.util.*;
import java.math.BigInteger;
/** 【变更记录 #1】2026-10-01 06:45:17（修订128）：删除：无；新增/修改：新增配方输出实际EU计量及只读阅读关闭回执，模拟与网络搬运均不计发电；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #2】2026-10-01 13:40:41（修订128）：删除：无；新增/修改：发电读取单项计数且只写一次已满足回执，减少高频分配与重复脏标记；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public final class Hk3EggGeneration {
    private record Capture(MetaMachine machine,long[] energy){}
    private static final ThreadLocal<ArrayDeque<Capture>> ACTIVE=ThreadLocal.withInitial(ArrayDeque::new);
    private Hk3EggGeneration(){}
    public static boolean tick(GTRecipe recipe,IO io,IRecipeLogicMachine logic,Map<RecipeCapability<?>,Object2IntMap<?>> cache){
        var cap=new Capture(logic.self(),new long[1]);var q=ACTIVE.get();q.push(cap);
        try{return recipe.handleTickRecipeIO(io,logic,cache);}
        finally{q.pop();if(q.isEmpty())ACTIVE.remove();if(io==IO.OUT&&cap.energy[0]>0)record(cap.machine,cap.energy[0]);}
    }
    public static void accepted(long amount){var q=ACTIVE.get();if(q.isEmpty()){ACTIVE.remove();return;}if(amount>0)q.peek().energy[0]=Hk3EggProductionData.plus(q.peek().energy[0],amount);}
    private static void record(MetaMachine machine,long amount){
        if(!(machine.getLevel() instanceof ServerLevel level)||!(machine.getHolder() instanceof BlockEntity be)||!level.getServer().isSameThread())return;
        UUID owner=machine instanceof com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine own?own.getOwnerUUID():be.getPersistentData().hasUUID(Hk3EggProduction.OWNER)?be.getPersistentData().getUUID(Hk3EggProduction.OWNER):null;if(owner==null)return;
        var data=Hk3EggProductionData.get(level.getServer());data.produced(owner,"context:generated_eu",amount);
        if(data.count(owner,"receipt:68")==0&&data.count(owner,"context:generated_eu")>=1234567890L)data.produced(owner,"receipt:68",1);
        var n=be.getPersistentData();long now=level.getServer().overworld().getGameTime();long[] values=n.getLongArray("hk3EggEuWindow"),ticks=n.getLongArray("hk3EggEuTicks");
        if(values.length!=20||ticks.length!=20||!n.hasUUID("hk3EggEuOwner")||!n.getUUID("hk3EggEuOwner").equals(owner)){values=new long[20];ticks=new long[20];Arrays.fill(ticks,Long.MIN_VALUE);}
        int slot=Math.floorMod(now,20);if(ticks[slot]!=now){ticks[slot]=now;values[slot]=0;}values[slot]=Hk3EggProductionData.plus(values[slot],amount);
        BigInteger total=BigInteger.ZERO;for(int i=0;i<20;i++)if(ticks[i]<=now&&ticks[i]>now-20)total=total.add(BigInteger.valueOf(values[i]));
        long threshold=com.sirin.hk3gtl.common.constants.Hk3Values.VA_LONG[com.sirin.hk3gtl.common.constants.Hk3Tiers.QCV];
        if(data.count(owner,"receipt:34")==0&&total.compareTo(BigInteger.valueOf(threshold).multiply(BigInteger.valueOf(20)))>=0)data.produced(owner,"receipt:34",1);
        n.putUUID("hk3EggEuOwner",owner);n.putLongArray("hk3EggEuWindow",values);n.putLongArray("hk3EggEuTicks",ticks);be.setChanged();
    }
}
