package com.sirin.hk3gtl.common.easter;
import com.gregtechceu.gtceu.api.cover.CoverBehavior;
public final class Hk3EggFluidCapture {
    private record Context(CoverBehavior cover,int id,java.util.ArrayDeque<Boolean> transfers){}
    private static final ThreadLocal<java.util.ArrayDeque<Context>> ACTIVE=ThreadLocal.withInitial(java.util.ArrayDeque::new);
    private Hk3EggFluidCapture(){}
    public static void begin(CoverBehavior c,int id){ACTIVE.get().push(new Context(c,id,new java.util.ArrayDeque<>()));}
    public static void end(){var q=ACTIVE.get();if(!q.isEmpty())q.pop();if(q.isEmpty())ACTIVE.remove();}
    public static void beforeTransfer(com.lowdragmc.lowdraglib.side.fluid.IFluidTransfer source,com.lowdragmc.lowdraglib.side.fluid.IFluidTransfer target,long max){
        var q=ACTIVE.get();if(q.isEmpty()){ACTIVE.remove();return;}
        var c=q.peek();c.transfers.push(c.id==272&&max>0&&targetFull(source,target));
    }
    public static void afterTransfer(long amount){
        var q=ACTIVE.get();if(q.isEmpty()){ACTIVE.remove();return;}
        var calls=q.peek().transfers;transferResult(amount,!calls.isEmpty()&&calls.pop());
    }
    public static boolean targetFull(com.lowdragmc.lowdraglib.side.fluid.IFluidTransfer source,com.lowdragmc.lowdraglib.side.fluid.IFluidTransfer target){
        if(source.getTanks()>4096||target.getTanks()<1||target.getTanks()>4096)return false;
        boolean sourcePresent=false;for(int i=0;i<source.getTanks();i++)if(!source.getFluidInTank(i).isEmpty())sourcePresent=true;
        if(!sourcePresent)return false;for(int i=0;i<target.getTanks();i++)if(target.getTankCapacity(i)<=0||target.getFluidInTank(i).getAmount()<target.getTankCapacity(i))return false;return true;
    }
    public static void transferResult(long amount,boolean full){var q=ACTIVE.get();if(q.isEmpty()){ACTIVE.remove();return;}var c=q.peek();if(c.id==272)Hk3EggCovers.fluidResult(c.cover,amount,full);result(amount);}
    public static void result(long amount){var q=ACTIVE.get();if(q.isEmpty()){ACTIVE.remove();return;}if(amount>0){var c=q.peek();Hk3EggCovers.delivered(c.cover,c.id);}}
}
