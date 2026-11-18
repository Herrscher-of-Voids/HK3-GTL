package com.sirin.hk3gtl.client.farview;

import com.sirin.hk3gtl.common.farview.Hk3FarSection;
import java.util.*;
import java.util.concurrent.atomic.AtomicLong;

/** 直接调用生产缓存、采样器与双源合并，不以源码关键词代替行为验证。 */
public final class Hk3WorldFarViewTest {
    private static int checks;
    public static void main(String[] args){
        compression();limits();sources();sampling();fairness();
        System.out.println("通用静态远景："+checks+"项行为检查通过；覆盖游程逐格往返、LRU/字节上限、HK双源与已知空气、采样预算、脏更新、卸载与公平轮转；未运行客户端画面验收。");
    }
    private static int[] filled(int state){int[] cells=new int[4096];Arrays.fill(cells,state);return cells;}
    private static void compression(){
        int[] cells=filled(7);var packed=Hk3WorldFarCache.Packed.encode(cells);cells[0]=99;
        check(packed.state(0)==7&&packed.state(4095)==7&&packed.bytes()<256,"实体深层分区应压缩且不得持有采样数组");
        var random=new Random(27);
        for(int sample=0;sample<30;sample++){
            for(int i=0;i<cells.length;i++)cells[i]=sample%2==0?random.nextInt(20):(i/37)%5;
            packed=Hk3WorldFarCache.Packed.encode(cells);
            for(int i=0;i<cells.length;i++)if(packed.state(i)!=cells[i])throw new AssertionError("游程改变了实际方块");
            check(true,"逐格往返");
        }
        check(Hk3WorldFarCache.Packed.air().empty(),"纯空气分区应无需稠密存储");
        check(packed.same(Hk3WorldFarCache.Packed.encode(cells))&&!packed.same(null),"相同重采快照应可去重且不误认缺失来源");
        try{Hk3WorldFarCache.Packed.encode(new int[1]);throw new AssertionError("应拒绝截断分区");}catch(IllegalArgumentException expected){checks++;}
        cells[0]=-1;
        try{Hk3WorldFarCache.Packed.encode(cells);throw new AssertionError("应拒绝负状态");}catch(IllegalArgumentException expected){checks++;}
    }
    private static void limits(){
        var tile=Hk3WorldFarCache.Packed.encode(filled(4));var removed=new ArrayList<Long>();
        var cache=new Hk3WorldFarCache(tile.bytes()*2,2);
        cache.put(0,tile,removed::add);cache.put(1,tile,removed::add);cache.get(0);cache.put(2,tile,removed::add);
        check(cache.size()==2&&cache.get(0)!=null&&cache.get(1)==null&&removed.equals(List.of(1L)),"LRU应保留最近访问的分区");
        cache.put(0,Hk3WorldFarCache.Packed.air(),removed::add);
        check(cache.get(0)==null&&removed.contains(0L),"实际空气重采必须撤销旧世界快照");
        int[] noisy=new int[4096];for(int i=0;i<noisy.length;i++)noisy[i]=i+1;
        cache.put(3,Hk3WorldFarCache.Packed.encode(noisy),removed::add);
        check(cache.get(3)==null&&cache.bytes()<=tile.bytes()*2,"超预算单分区不能撑大缓存");
        cache.clear();check(cache.size()==0&&cache.bytes()==0,"退出会话后应清空压缩数据");
    }
    private static void sources(){
        var source=new Hk3FarTileSource();int[] cells=filled(4);source.world(Hk3WorldFarCache.Packed.encode(cells));
        var structure=new Hk3FarSection();structure.set(0,9);source.structure(structure.snapshot());
        check(source.state(0)==9&&source.state(1)==4,"HK已知实体优先且不能抹去周围世界");
        check(source.snapshot(index->index==0).state(0)==0&&source.snapshot(index->index==0).state(1)==4,"动态坐标遮罩只能排除命中的真实位置");
        structure.set(0,0);source.structure(structure.snapshot());source.structure(structure.snapshot());
        check(source.state(0)==0&&source.snapshot(null).state(0)==0,"连续空气更新不能复活旧世界中的已拆HK方块");
        structure.set(0,8);source.structure(structure.snapshot());check(source.state(0)==8,"重新存在的HK方块应清除空气覆盖");
        source.structure(null);check(source.state(0)==4&&!source.hasStructure(),"真正撤销HK成员后应恢复世界来源");
        source.structure(structure.snapshot());source.world(null);
        check(source.state(0)==8&&source.state(1)==0&&!source.empty(),"世界LRU淘汰不能删除HK来源");
        source.structure(null);check(source.empty()&&source.snapshot(null).state(0)==0,"两个来源都撤销后应为空");
    }
    private static final class Input implements Hk3WorldFarSampler.Source {
        final int[][] values;
        final Map<Integer,Hk3WorldFarCache.Packed> published=new HashMap<>();
        int reads,publishes;boolean valid=true;
        Input(int...states){values=new int[states.length][];for(int i=0;i<states.length;i++)values[i]=filled(states[i]);}
        @Override public boolean valid(){return valid;}
        @Override public int sections(){return values.length;}
        @Override public boolean empty(int section){for(int value:values[section])if(value!=0)return false;return true;}
        @Override public int state(int section,int index){reads++;return values[section][index];}
        @Override public void publish(int section,Hk3WorldFarCache.Packed snapshot){published.put(section,snapshot);publishes++;}
    }
    private static void tick(Hk3WorldFarSampler queue,int cells){queue.tick(1,cells,8,()->0);}
    private static void sampling(){
        var queue=new Hk3WorldFarSampler(2);var input=new Input(5,6);queue.add(1,input);tick(queue,64);
        check(input.reads==64&&input.publishes==0,"每次采样格数必须受限且不能发布半成品");
        var clock=new AtomicLong();queue.tick(2,4096,8,clock::getAndIncrement);
        check(input.reads<=192&&input.publishes==0,"截止时间后不能继续扫描整个区块");
        tick(queue,4096);check(input.published.containsKey(0),"完整分区必须可逐步交付");
        queue.remove(1);check(input.published.get(0).state(0)==5&&!input.published.containsKey(1),"中途卸载保留已完成分区而不发布未完成分区");
        input.values[0][0]=0;queue.changed(1,0,input);queue.changed(1,0,input);tick(queue,4096);
        check(input.published.get(0).state(0)==0&&input.published.get(0).state(1)==5,"去重后的块更新应重采正确分区");
        var empty=new Input(0);queue.add(2,empty);tick(queue,1);
        check(empty.reads==0&&empty.published.get(0).empty(),"纯空气应直接发布清除，不读取4096格");
        var replaced=new Input(8);queue.add(3,replaced);tick(queue,64);var fresh=new Input(9);queue.add(3,fresh);tick(queue,4096);
        check(replaced.publishes==0&&fresh.published.get(0).state(0)==9,"整区新包必须取消旧的部分采样");
        queue.add(4,new Input(1));queue.add(5,new Input(2));queue.add(6,new Input(3));
        check(queue.pending()==2,"事件积压必须受固定队列容量限制");
        queue.clear();check(queue.pending()==0,"关闭或换维度必须撤销待采任务");
        var dead=new Input(3);queue.add(7,dead);dead.valid=false;tick(queue,4096);
        check(dead.reads==0&&dead.publishes==0&&queue.pending()==0,"失效来源不得继续读取或交付");
        var editedDuringRead=new Input(7);queue.add(8,editedDuringRead);tick(queue,64);
        editedDuringRead.values[0][0]=8;queue.changed(8,0,editedDuringRead);
        tick(queue,4096);tick(queue,4096);
        check(editedDuringRead.publishes==2&&editedDuringRead.published.get(0).state(0)==8,
                "采样途中更改已读格必须保留脏位并最终重新采集，不能永久留下混合快照");
    }
    private static void fairness(){
        var queue=new Hk3WorldFarSampler(8);var hot=new Input(1,2);var other=new Input(3);
        queue.add(1,hot);queue.add(2,other);
        for(int i=0;i<4;i++){queue.changed(1,0,hot);tick(queue,4096);}
        check(other.publishes==1&&hot.published.containsKey(1),"持续变更的首分区不能饿死其他区块或本区块后续分区");
    }
    private static void check(boolean condition,String message){if(!condition)throw new AssertionError(message);checks++;}
}
