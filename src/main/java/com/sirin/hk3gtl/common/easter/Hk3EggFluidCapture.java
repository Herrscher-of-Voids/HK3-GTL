package com.sirin.hk3gtl.common.easter;
import com.gregtechceu.gtceu.api.cover.CoverBehavior;
/** 【变更记录 #1】2026-10-01 06:15:25（修订128）：删除无；新增嵌套隔离的同步流体结果观察；修改无；用途：只在指定覆盖板原调用作用域记录transferFluids实际返回，不读模拟。 */
/** 【变更记录 #2】2026-10-01 12:33:29（修订128）：删除：无；新增/修改：零传输只有源端仍有流体且接收端全部实际满容量才记录暂停，不把缺料或过滤拒绝冒充满载；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #3】2026-10-01 13:40:41（修订128）：删除：无；新增/修改：仅在覆盖板同步作用域扫描流体罐；调用栈随作用域finally清理，普通传输无扫描开销；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
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
