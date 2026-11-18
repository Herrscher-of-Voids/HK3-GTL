package com.sirin.hk3gtl.test.research;

import com.sirin.hk3gtl.common.research.*;
import java.util.Arrays;
import java.util.Random;
import java.util.List;
import net.minecraft.nbt.CompoundTag;

public final class ResearchMaterialTest {
    /** 不启动游戏，不伪造Forge初始化；验证可独立运行的生产逻辑。 / Verify isolated production logic without starting a game or faking Forge initialization. */
    public static void main(String[] args) {
        allocation(); plans();
        inventory();
        System.out.println("Research materials: exhaustive allocation, 100 plans, shared debit rollback, NBT snapshots and replay passed");
    }

    /** 用固定种子生成1000个小问题对照穷举，不把实现本身复制为预期结果。
     * Compare 1000 seeded small cases against independent exhaustive search, not a copy of max flow.
     */
    private static void allocation() {
        check(Arrays.equals(Hk3MaterialAllocation.allocate(new long[]{1,1},new long[]{1,1},
                new boolean[][]{{true,true},{true,false}}),new long[]{1,1}),"overlap must reroute");
        check(Hk3MaterialAllocation.allocate(new long[]{1},new long[]{1,1},new boolean[][]{{true,true}})==null,"cannot count one twice");
        Random random=new Random(6006);
        for (int test=0;test<1000;test++) {
            long[] stock=new long[3], cost={1+random.nextInt(3),1+random.nextInt(3)};
            boolean[][] match=new boolean[3][2];
            for (int i=0;i<3;i++) { stock[i]=random.nextInt(3); for (int j=0;j<2;j++) match[i][j]=random.nextBoolean(); }
            boolean expected=brute(stock.clone(),cost.clone(),match,0);
            long[] result=Hk3MaterialAllocation.allocate(stock,cost,match);
            check(expected==(result!=null),"allocation differs from exhaustive search");
            if (result!=null) {
                check(Arrays.stream(result).sum()==Arrays.stream(cost).sum(),"exact required amount");
                for (int i=0;i<3;i++) check(result[i]>=0 && result[i]<=stock[i],"slot bound");
            }
        }
    }

    /** 按需求逐个选择实物单位的穷举判定，仅用于极小测试。 / Exhaustive per-item assignment oracle for tiny cases only. */
    private static boolean brute(long[] stock,long[] cost,boolean[][] match,int requirement) {
        if (requirement==cost.length) return true;
        if (cost[requirement]==0) return brute(stock,cost,match,requirement+1);
        for (int slot=0;slot<stock.length;slot++) if (stock[slot]>0 && match[slot][requirement]) {
            stock[slot]--; cost[requirement]--;
            boolean ok=brute(stock,cost,match,requirement);
            stock[slot]++; cost[requirement]++;
            if (ok) return true;
        }
        return false;
    }

    /** 每项有正费用和材料路线，加载不自动授予知识/实验。 / Every topic has positive costs and a material alternative; loading grants nothing. */
    private static void plans() {
        check(Hk3ResearchPlans.all().size()==100,"all topic plans");
        for (var plan:Hk3ResearchPlans.all().values()) {
            check(plan.points()>0 && plan.ticks()>0 && !plan.materials().isEmpty(),"paid timed research");
            check(!plan.evidence().isBlank(),"explicit experimental requirement");
        }
        check(Hk3ResearchPlans.get("RN-UNKNOWN")==null,"no free fallback");
        var owner=java.util.UUID.fromString("55555555-5555-5555-5555-555555555555");
        var data=new Hk3ResearchData();
        check(!data.hasExperiment(owner,"RN-HED"),"knowledge starts without fabricated experiments");
        check(data.recordExperiment(owner,"RN-HED") && !data.recordExperiment(owner,"RN-HED"),"trusted evidence is idempotent");
        check(!data.completed(owner,"RN-HED"),"experiment alone does not complete research");
        check(!data.recordExperiment(owner,"RN-UNKNOWN"),"unknown evidence refused");
        var restored=Hk3ResearchData.load(data.save(new CompoundTag()));
        check(restored.hasExperiment(owner,"RN-HED"),"evidence survives restart");
    }

    /** 对生产共用提交内核使用NBT值库存，测试一次扣款、回滚和防御性副本；不冒充实物适配验收。
     * Test the production kernel with NBT-valued inventory, including rollback and defensive copies; this is not ItemStack integration acceptance.
     */
    private static void inventory() {
        java.util.List<CompoundTag> inventory=new java.util.ArrayList<>(List.of(stack(5),stack(8),stack(64)));
        List<CompoundTag> before=List.of(stack(5),stack(8)), after=List.of(stack(2),stack(6));
        var debit=new Hk3InventoryDebit<>(before,after,inventory::get,inventory::set,CompoundTag::equals,CompoundTag::copy,()->{});
        before.get(0).putString("batch","external change");
        check(debit.commit(),"defensive snapshot accepted");
        check(inventory.get(0).getInt("count")==2 && inventory.get(2).getInt("count")==64 && !debit.commit(),"exact payment, excluded slot, replay");
        inventory.set(0,stack(5)); inventory.set(1,stack(8));
        var stale=new Hk3InventoryDebit<>(List.of(stack(5),stack(8)),after,inventory::get,inventory::set,CompoundTag::equals,CompoundTag::copy,()->{});
        inventory.get(0).putString("batch","changed");
        check(!stale.commit() && inventory.get(0).getInt("count")==5,"changed NBT rejects before writing");
        inventory.set(0,stack(5));
        java.util.concurrent.atomic.AtomicBoolean fail=new java.util.concurrent.atomic.AtomicBoolean(true);
        var rollback=new Hk3InventoryDebit<>(List.of(stack(5),stack(8)),after,inventory::get,(slot,value)->{
            inventory.set(slot,value);
            if (slot==1 && fail.getAndSet(false)) throw new IllegalStateException("injected write failure");
        },CompoundTag::equals,CompoundTag::copy,()->{});
        try { rollback.commit(); throw new AssertionError("expected failed commit"); } catch (IllegalStateException expected) { }
        check(inventory.get(0).equals(stack(5)) && inventory.get(1).equals(stack(8)),"rollback restores all touched slots");
        check(!rollback.commit(),"failed transaction cannot replay");
    }
    private static CompoundTag stack(int count) { CompoundTag tag=new CompoundTag(); tag.putInt("count",count); tag.putString("batch","preserved"); return tag; }
    private static void check(boolean ok,String message) { if (!ok) throw new AssertionError(message); }
}

