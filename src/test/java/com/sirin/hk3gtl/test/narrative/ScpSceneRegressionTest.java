package com.sirin.hk3gtl.test.narrative;

import com.sirin.hk3gtl.common.easter.*;
import com.sirin.hk3gtl.common.phone.*;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.*;
import net.minecraft.world.phys.*;
import org.objectweb.asm.ClassReader;
import org.objectweb.asm.tree.*;
import java.io.*;
import java.util.*;

/**
 * 【变更记录 #1】2026-10-01 16:31:00（修订134）：删除无；新增用户复现的浅角度高窗、反向笔记顺序、日期页及多人隔离回归。
 * 修改：无；用途：运行生产几何算法、笔记账本及当前依赖字节码检查，不冒充指定实例实机验收。
 */
public final class ScpSceneRegressionTest {
    private static int checks;
    private static void check(boolean value,String text){checks++;if(!value)throw new AssertionError(text);}
    public static void main(String[] args)throws Exception{
        dawn();notesAndArmor();date();contracts();
        System.out.println("SCP scene regression: "+checks+" checks passed; 401/411/417, real geometry/NBT/bytecode; game acceptance pending.");
    }
    private static final class Scene implements Hk3EggDawnSight.World {
        final Map<BlockPos,Boolean> blocks=new HashMap<>();
        boolean loaded=true;int rays;
        Scene glass(int x,int y,int z){blocks.put(new BlockPos(x,y,z),true);return this;}
        Scene stone(int x,int y,int z){blocks.put(new BlockPos(x,y,z),false);return this;}
        public boolean loaded(int x,int z){return loaded;}
        public boolean orange(BlockPos pos){return Boolean.TRUE.equals(blocks.get(pos));}
        public boolean sky(BlockPos pos){return blocks.keySet().stream().noneMatch(b->b.getX()==pos.getX()&&b.getZ()==pos.getZ()&&b.getY()>=pos.getY());}
        public BlockPos firstHit(Vec3 from,Vec3 to){
            rays++;BlockPos nearest=null;double distance=Double.POSITIVE_INFINITY;
            for(var pos:blocks.keySet()){
                var hit=new AABB(pos).clip(from,to);
                if(hit.isPresent()&&hit.get().distanceToSqr(from)<distance){nearest=pos;distance=hit.get().distanceToSqr(from);}
            }
            return nearest;
        }
    }
    private static void dawn(){
        Vec3 eye=new Vec3(.5,65.5,.5),look=new Vec3(1,.1,0).normalize();
        check(Hk3EggScpFacts.dawn(true,23000,look.y),"审核起始时刻与小于30度的仰视允许");
        check(Hk3EggScpFacts.dawn(true,23999,look.y),"23999仍为日出区间");
        check(!Hk3EggScpFacts.dawn(true,22999,look.y)&&!Hk3EggScpFacts.dawn(true,24000,look.y),"时间区间外拒绝");
        check(!Hk3EggScpFacts.dawn(false,23000,look.y),"其他维度拒绝");
        check(!Hk3EggScpFacts.dawn(true,23000,-.1),"不能看地面冒充天空");
        var window=new Scene();for(int y=64;y<=70;y++)window.glass(3,y,0);
        check(!window.sky(new BlockPos(3,66,0)),"复现旧判据：首块玻璃上方被同一高窗挡住");
        check(Hk3EggDawnSight.visible(eye,look,window),"修复后高窗浅角度看真实天空通过");
        check(Hk3EggScpFacts.dawn(true,23000,0)&&Hk3EggDawnSight.visible(eye,new Vec3(1,0,0),window),"水平朝无遮挡天际观察也不额外卡角度");
        window.glass(4,65,0).glass(4,66,0);
        check(Hk3EggDawnSight.visible(eye,look,window),"相邻多层橙色玻璃通过");
        window.stone(7,66,0);
        check(!Hk3EggDawnSight.visible(eye,look,window),"玻璃后实体遮挡拒绝");
        check(!Hk3EggDawnSight.visible(eye,look,new Scene().stone(1,65,0).glass(3,65,0)),"玻璃前障碍拒绝");
        check(!Hk3EggDawnSight.visible(eye,look,new Scene()),"没有橙玻璃的晴空不触发");
        check(Hk3EggDawnSight.visible(eye,new Vec3(0,1,0),new Scene().glass(0,68,0)),"正上方橙色玻璃天窗通过");
        var unloaded=new Scene().glass(3,65,0);unloaded.loaded=false;
        check(!Hk3EggDawnSight.visible(eye,look,unloaded)&&unloaded.rays==0,"区块未载入时不做世界查询");
        check(!Hk3EggDawnSight.visible(eye,new Vec3(Double.NaN,.1,0),window),"无效视向拒绝");
        int progress=0;for(int i=0;i<99;i++)progress=Hk3EggScpFacts.nextObservation(progress,true,true);
        check(progress==99,"不足五秒不完成");
        check(Hk3EggScpFacts.nextObservation(progress,true,true)==100,"100连续游戏刻完成");
        check(Hk3EggScpFacts.nextObservation(99,true,false)==0,"移开视线立即清零");
        check(Hk3EggScpFacts.nextObservation(99,false,true)==1,"重登或时间不连续重计");
        check(Hk3EggScpFacts.nextObservation(100,true,true)==100,"计数有界");
    }
    private static CompoundTag owners(UUID player){
        var n=new CompoundTag();for(String slot:Hk3EggScpFacts.ARMOR_SLOTS)n.putUUID("hk3_egg_armorer_"+slot,player);return n;
    }
    private static void notesAndArmor()throws Exception{
        UUID a=UUID.randomUUID(),b=UUID.randomUUID();var data=new Hk3PhoneNotes();boolean[] full={true,true,true,true};
        check(data.saveNote(a,"",0,"为什么？","调查编号5000",1),"先保存本人笔记");
        check(Hk3EggScpFacts.hasWhyNote(data.list(a)),"反向顺序：穿甲时可查已有笔记");
        var owned=owners(a);
        check(Hk3EggScpFacts.ownsArmor(owned,a,full)&&Hk3EggScpFacts.hasWhyNote(data.list(a)),"先笔记后本人完整盔甲满足");
        check(!Hk3EggScpFacts.hasWhyNote(data.list(b)),"他人笔记不满足");
        check(!Hk3EggScpFacts.ownsArmor(owned,b,full),"他人穿齐不能冒领");
        for(int i=0;i<4;i++){var missing=full.clone();missing[i]=false;check(!Hk3EggScpFacts.ownsArmor(owned,a,missing),"四个位置任意缺件都不通过");}
        owned.putUUID("hk3_egg_armorer_head",b);check(!Hk3EggScpFacts.ownsArmor(owned,a,full),"混合操作者不算本人整套");
        owned.remove("hk3_egg_armorer_head");check(!Hk3EggScpFacts.ownsArmor(owned,a,full),"自动换装清除归属后不能冒领");
        check(Hk3EggScpFacts.ownsArmor(owners(b),b,full),"正向顺序先确认完整盔甲");
        check(data.saveNote(b,"",0,"为什么？","5000",2)&&Hk3EggScpFacts.hasWhyNote(data.list(b)),"后保存对应笔记满足");
        check(Hk3EggScpFacts.whyNote(" 为什么? ","5000"),"全半角标点和边缘空格等价");
        check(!Hk3EggScpFacts.whyNote("为什么？","500")&&!Hk3EggScpFacts.whyNote("其他标题","5000"),"不相关笔记拒绝");
        check(data.saveNote(a,"",0,"即死年","1. 准备食物\n2. 储备饮水\n3. 检查避难所",3),"保存三项应急准备");
        check(data.saveNote(a,"",0,"其他笔记","后来另写的事",4),"随后保存其他笔记");
        check(Hk3EggScpFacts.hasEmergencyNote(data.list(a)),"日期页检查所有本人笔记，不限最后一条");
        check(!Hk3EggScpFacts.hasEmergencyNote(data.list(b)),"他人应急笔记隔离");
        check(Hk3EggScpFacts.emergencyNote("即死年","食物；饮水；床"),"分号分隔三项准备可识别");
        check(!Hk3EggScpFacts.emergencyNote("即死年","食物\n饮水"),"不足三项拒绝");
        check(!Hk3EggScpFacts.emergencyNote("即死年","1.\n2.\n3."),"空编号不能充数");
        check(!Hk3EggScpFacts.emergencyNote("即死年","食物\n食物\n食物"),"重复同一项不能充数");
        var output=new ByteArrayOutputStream();NbtIo.writeCompressed(data.save(new CompoundTag()),output);
        var restored=Hk3PhoneNotes.load(NbtIo.readCompressed(new ByteArrayInputStream(output.toByteArray())));
        check(Hk3EggScpFacts.hasWhyNote(restored.list(a))&&Hk3EggScpFacts.hasEmergencyNote(restored.list(a)),"实际笔记重载后仍能后续补操作");
        var note=restored.list(a).stream().filter(n->n.title().equals("即死年")).findFirst().orElseThrow();
        check(restored.delete(a,note.id(),note.version())&&!Hk3EggScpFacts.hasEmergencyNote(restored.list(a)),"删除笔记后不靠残留缓存触发");
    }
    private static void date(){
        check(Hk3PhoneDate.from(0).day()==1&&Hk3PhoneDate.from(0).clock().equals("06:00"),"第1天游戏起点");
        check(Hk3PhoneDate.from(23000).clock().equals("05:00"),"日出范围起点对应次日清晨前");
        check(Hk3PhoneDate.from(24000).day()==2&&Hk3PhoneDate.from(24000).tick()==0,"游戏日跨日");
        for(long t:new long[]{-1,0,23000,Long.MIN_VALUE,Long.MAX_VALUE})check(Hk3PhoneDate.from(t).tick()>=0&&Hk3PhoneDate.from(t).tick()<24000,"极端日历值不溢出");
        for(String id:List.of("401","411","417")){
            var rule=Hk3EggRules.all().stream().filter(r->r.id().equals("E-EG-"+id)).findFirst().orElseThrow();
            check(rule.matches("vanilla_case",Map.of("case",id)),"每条真实场景能到规则");
            check(!rule.matches("note_saved",Map.of("case",id)),"仅保存正文不可伪造场景");
        }
    }
    private static ClassNode node(String name)throws IOException{
        try(var in=ScpSceneRegressionTest.class.getResourceAsStream('/'+name+".class")){
            if(in==null)throw new AssertionError(name);var n=new ClassNode();new ClassReader(in).accept(n,0);return n;
        }
    }
    private static void calls(ClassNode node,String method,String target){
        check(node.methods.stream().filter(m->m.name.equals(method)).flatMap(m->Arrays.stream(m.instructions.toArray())).anyMatch(i->i instanceof MethodInsnNode call&&call.name.equals(target)),method+"实际调用"+target);
    }
    private static void contracts()throws Exception{
        var stand=node("net/minecraft/world/entity/decoration/ArmorStand");
        calls(stand,"swapItem","setItemSlot");
        var scenes=node("com/sirin/hk3gtl/common/easter/Hk3EggPersonalScenes");
        calls(scenes,"armored","hasWhyNote");calls(scenes,"note","completeArmor");
        var app=node("com/sirin/hk3gtl/common/phone/Hk3PhoneAppService");
        calls(app,"date","allowed");calls(app,"date","hasEmergencyNote");calls(app,"date","send");
        var sight=node("com/sirin/hk3gtl/common/easter/Hk3EggObservation");calls(sight,"tick","visible");
    }
}
