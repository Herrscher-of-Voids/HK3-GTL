package com.sirin.hk3gtl.test.compat;

import com.sirin.hk3gtl.mixin.AvaritiaAbilityHandlerMixin;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.objectweb.asm.ClassReader;
import org.objectweb.asm.Opcodes;
import org.objectweb.asm.tree.ClassNode;
import org.objectweb.asm.tree.MethodInsnNode;
import java.util.*;
import java.util.concurrent.*;
import java.util.zip.ZipFile;

/**
 * 【文件职责】核验实际第三方jar的兼容入口，并直接执行生产Mixin回调检验并发集合。
 * 【变更记录 #1】2026-09-30 17:53:52（修订111）
 * 删除：无。新增：旧HashMap故障的确定性双线程复现、修复回调、六线程压力和字节码形状核验。
 * 修改：纳入check；用途：集合替换必须保留记录引用，不以关闭玩家能力处理隐藏问题。
 * 边界：不启动Forge，不能代替游戏实际Mixin应用及飞行行为验收。
 */
public final class AvaritiaAbilityConcurrencyTest {
    private static void check(boolean ok,String message){if(!ok)throw new AssertionError(message);}
    public static void main(String[] args)throws Exception{
        try(var zip=new ZipFile("libs/Re-Avaritia-forged-1.20.1-1.3.8.3.jar")){
            var node=new ClassNode();new ClassReader(zip.getInputStream(zip.getEntry("committee/nova/mods/avaritia/init/handler/AbilityHandler.class"))).accept(node,0);
            for(String name:List.of("entitiesWithFlight","entitiesWithHelmets","entitiesWithLeggings","entitiesWithBoots")){
                String descriptor=name.equals("entitiesWithFlight")?"Ljava/util/Map;":"Ljava/util/Set;";
                check(node.fields.stream().anyMatch(f->f.name.equals(name)&&f.desc.equals(descriptor)
                        &&(f.access&Opcodes.ACC_STATIC)!=0&&(f.access&Opcodes.ACC_FINAL)!=0),"目标字段形状 "+name);
            }
            check(node.methods.stream().anyMatch(m->m.name.equals("<clinit>")&&m.desc.equals("()V")),"目标类初始化存在");
            boolean compute=false;
            for(var m:node.methods)if(m.name.equals("handleChestStateChange"))for(var i:m.instructions)
                if(i instanceof MethodInsnNode call&&call.owner.equals("java/util/Map")&&call.name.equals("computeIfAbsent"))compute=true;
            check(compute,"原始异常调用点存在");
        }
        check(race(new HashMap<>()),"旧HashMap应确定性复现并发修改");
        Object sentinel=new Object();
        AvaritiaAbilityHandlerMixin.entitiesWithFlight=new HashMap<>(Map.of("existing",sentinel));
        AvaritiaAbilityHandlerMixin.entitiesWithHelmets=new HashSet<>(Set.of("existing"));
        AvaritiaAbilityHandlerMixin.entitiesWithLeggings=new HashSet<>(Set.of("existing"));
        AvaritiaAbilityHandlerMixin.entitiesWithBoots=new HashSet<>(Set.of("existing"));
        var method=AvaritiaAbilityHandlerMixin.class.getDeclaredMethod("hk3gtl$makeAbilityStateConcurrent",CallbackInfo.class);
        method.setAccessible(true);method.invoke(null,new CallbackInfo("<clinit>",false));
        var map=AvaritiaAbilityHandlerMixin.entitiesWithFlight;
        check(map instanceof ConcurrentMap,"生产回调返回并发Map");
        check(map.get("existing")==sentinel,"保留既有能力记录对象");
        for(var set:List.of(AvaritiaAbilityHandlerMixin.entitiesWithHelmets,AvaritiaAbilityHandlerMixin.entitiesWithLeggings,AvaritiaAbilityHandlerMixin.entitiesWithBoots))
            check(set.contains("existing"),"保留原装备状态集合");
        check(!race(map),"生产补丁应通过相同双线程交错");
        var pool=Executors.newFixedThreadPool(6);var start=new CountDownLatch(1);List<Future<?>> tasks=new ArrayList<>();
        try{
            for(int t=0;t<6;t++){int thread=t;tasks.add(pool.submit(()->{
                start.await();
                for(int i=0;i<10000;i++){
                    String key="player_"+thread+"_"+i;Object value=map.computeIfAbsent(key,k->new Object());
                    if(map.computeIfAbsent(key,k->{throw new AssertionError("已有值不重复构造");})!=value)throw new AssertionError("记录引用不稳定");
                    AvaritiaAbilityHandlerMixin.entitiesWithHelmets.add(key);AvaritiaAbilityHandlerMixin.entitiesWithHelmets.remove(key);
                    AvaritiaAbilityHandlerMixin.entitiesWithLeggings.add(key);AvaritiaAbilityHandlerMixin.entitiesWithLeggings.remove(key);
                    AvaritiaAbilityHandlerMixin.entitiesWithBoots.add(key);AvaritiaAbilityHandlerMixin.entitiesWithBoots.remove(key);
                }return null;
            }));}
            start.countDown();for(var task:tasks)task.get(30,TimeUnit.SECONDS);
        }finally{pool.shutdownNow();}
        check(map.size()==60003,"六万新键与三个原测试键均保存");
        check(AvaritiaAbilityHandlerMixin.entitiesWithHelmets.size()==1&&AvaritiaAbilityHandlerMixin.entitiesWithLeggings.size()==1&&AvaritiaAbilityHandlerMixin.entitiesWithBoots.size()==1,"并发添加删除未破坏集合");
        System.out.println("Avaritia compatibility: original CME reproduced; production callback and 60000-key/6-thread checks passed; live injection pending");
    }
    /** 控制两个逻辑端的交错顺序，验证计算期间另一个键插入；不依赖随机调度碰巧复现。 */
    private static boolean race(Map<String,Object> map)throws Exception{
        var entered=new CountDownLatch(1);var inserted=new CountDownLatch(1);var pool=Executors.newFixedThreadPool(2);
        try{
            var compute=pool.submit(()->{
                try{map.computeIfAbsent("client",key->{entered.countDown();try{
                    if(!inserted.await(3,TimeUnit.SECONDS))throw new AssertionError("交错超时");
                }catch(InterruptedException e){Thread.currentThread().interrupt();throw new AssertionError(e);}return new Object();});return false;}
                catch(ConcurrentModificationException expected){return true;}
            });
            var insert=pool.submit(()->{if(!entered.await(3,TimeUnit.SECONDS))throw new AssertionError("计算未开始");map.put("server",new Object());inserted.countDown();return null;});
            insert.get(5,TimeUnit.SECONDS);return compute.get(5,TimeUnit.SECONDS);
        }finally{pool.shutdownNow();}
    }
}
