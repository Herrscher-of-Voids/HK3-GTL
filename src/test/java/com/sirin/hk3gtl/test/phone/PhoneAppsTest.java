package com.sirin.hk3gtl.test.phone;
import com.sirin.hk3gtl.common.phone.*;
import net.minecraft.nbt.*;
import java.util.*;
/** 【变更记录 #1】2026-09-30 19:06:42（修订114）：删除无；新增小游戏与私人笔记/搜索回归；修改无；用途：生产逻辑验证，不冒充实机界面验收。 */
/** 【变更记录 #2】2026-10-31 21:56:17（第2次备注 · 内测5修订191）：删除无；新增交错双人操作、断线重载后的旧版本拒绝、显式重读再保存及草稿另存回归；修改测试入口运行恢复场景；用途：验证真实账本CAS、独立配额及版本上溢边界，不冒充网络与界面实机验收。 */
/** 【变更记录 #3】2026-11-05 01:51:41（第3次备注 · 内测5修订204）：删除无；新增收藏阅读与主动收藏回归入口；修改原手机测试同时执行隔离、版本和动作测试；用途：沿用runPhoneAppsTest接入check。 */
public final class PhoneAppsTest {
    static int checks;static void check(boolean b,String why){if(!b)throw new AssertionError(why);checks++;}
    static void tiles(){
        var t=new Hk3PhoneGames.Tiles(19);
        check(Arrays.stream(t.cells()).filter(n->n!=0).count()==2,"开局两块");
        for(int dir=0;dir<4;dir++){
            int[] state=new int[16];
            int[] positions=switch(dir){case 0->new int[]{0,4,8,12};case 1->new int[]{3,2,1,0};case 2->new int[]{12,8,4,0};default->new int[]{0,1,2,3};};
            for(int pos:positions)state[pos]=2;t.restore(state,0);
            check(t.move(dir),"四方向移动");int[] cells=t.cells();
            check(cells[positions[0]]==4&&cells[positions[1]]==4&&t.score()==8,"四块相同只合并成两块");
            check(Arrays.stream(cells).filter(n->n!=0).count()==3,"变化后仅生一块");
        }
        t.restore(new int[]{2,4,8,16,32,64,128,256,512,1024,2,4,8,16,32,64},7);
        var before=t.cells();check(t.over(),"满盘无可合并");
        check(!t.move(3)&&Arrays.equals(before,t.cells())&&t.score()==7,"无效移动不生块不加分");
        t.restore(new int[]{1024,1024,0,0,0,0,0,0,0,0,0,0,0,0,0,0},0);t.move(3);check(t.won()&&t.score()==2048,"2048达成");
        t.restore(new int[]{2,2,4,0,0,0,0,0,0,0,0,0,0,0,0,0},0);t.move(3);check(t.cells()[0]==4&&t.cells()[1]==4,"新合并块不能再次合并");
        int[] capped=new int[16];Arrays.fill(capped,1<<29);t.restore(capped,0);check(t.over()&&!t.move(1),"数字上限不溢出且正确结束");
        boolean rejected=false;try{t.restore(new int[5],0);}catch(IllegalArgumentException e){rejected=true;}check(rejected,"拒绝坏棋盘");
    }
    static void snakes(){
        var s=new Hk3PhoneGames.Snake(7);s.turn(3);s.step();check(s.cells().get(0)==137,"不能反向");
        s=new Hk3PhoneGames.Snake(7);s.turn(0);s.turn(3);s.step();check(s.cells().get(0)==120,"一步最多转一次");
        s=new Hk3PhoneGames.Snake(7);for(int i=0;i<8;i++)s.step();check(s.over(),"撞墙结束");
        var before=s.cells();s.step();check(before.equals(s.cells()),"结束不推进");
        long chosen=0;while(new Hk3PhoneGames.Snake(chosen).food()!=137&&chosen<10000)chosen++;
        s=new Hk3PhoneGames.Snake(chosen);check(s.food()==137,"确定种子找到邻近食物");s.step();
        check(s.score()==1&&s.cells().size()==4,"吃一个食物增长一格");
        s.turn(2);s.step();s.turn(3);s.step();s.turn(0);s.step();
        check(!s.over(),"可进入本步离开的尾格");
        for(int seed=0;seed<40;seed++){
            s=new Hk3PhoneGames.Snake(seed);check(!s.cells().contains(s.food()),"食物不在蛇身");
            var r=new Random(seed);int ticks=0;while(!s.over()&&ticks++<2000){
                s.turn(r.nextInt(4));s.step();
                check(new HashSet<>(s.cells()).size()==s.cells().size(),"蛇身不得重复");
                if(!s.over())check(!s.cells().contains(s.food()),"吃食后新食物仍为空位");
                check(s.cells().size()==s.score()+3,"每个食物只增长一格");
            }
        }
    }
    static void notes(){
        UUID a=UUID.randomUUID(),b=UUID.randomUUID();var data=new Hk3PhoneNotes();
        check(data.saveNote(a,"",0,"配方记录","正文\n第二行",123),"创建");
        var n=data.list(a).get(0);check(data.list(b).isEmpty()&&data.find(b,n.id())==null,"玩家隔离");
        check(!data.saveNote(b,n.id(),1,"劫持","",124)&&!data.delete(b,n.id(),1),"他人不能改删");
        check(data.saveNote(a,n.id(),1,"新标题","新正文",125),"版本更新");
        check(!data.saveNote(a,n.id(),1,"旧副本","",126)&&!data.delete(a,n.id(),1),"旧版本不能覆盖或删除");
        check(!data.saveNote(a,"",0," ","",126),"标题必填");
        check(!data.saveNote(a,"",0,"a".repeat(65),"",126),"标题有界");
        check(!data.saveNote(a,"",0,"标题","a".repeat(4097),126),"正文有界");
        var loaded=Hk3PhoneNotes.load(data.save(new CompoundTag()));
        check(loaded.find(a,n.id()).body().equals("新正文")&&loaded.find(a,n.id()).version()==2,"持久化正文和版本");
        for(int i=1;i<64;i++)check(loaded.saveNote(a,"",0,"笔记"+i,"",127+i),"允许64条");
        check(!loaded.saveNote(a,"",0,"溢出","",199),"拒绝第65条");
        check(loaded.delete(a,n.id(),2)&&loaded.saveNote(a,"",0,"腾出空间","",200),"删除后可新建");
        check(loaded.saveNote(b,"",0,"独立配额","",200),"其他玩家独立配额");
        var inbox=new Hk3PhoneData();inbox.add(a,"r1","核验成果","长期保存正文",0,"research","",false);
        inbox.add(a,"r2","另一篇","其他",1);inbox.read(a,"r2");
        check(inbox.search(a,"all","正文").size()==1,"搜索正文");
        check(inbox.search(a,"unread","另").isEmpty(),"搜索遵从未读筛选");
        check(inbox.search(b,"all","").isEmpty(),"搜索无跨人泄露");
    }
    static void noteRecovery(){
        UUID a=UUID.randomUUID(),b=UUID.randomUUID();var data=new Hk3PhoneNotes();
        check(data.saveNote(a,"",0,"原稿","原正文",1),"恢复前创建本人笔记");
        var stale=data.list(a).get(0);
        check(data.saveNote(b,"",0,"另一玩家","独立正文",2),"双人交错写入");
        check(data.saveNote(a,stale.id(),stale.version(),"已提交","服务器新正文",3),"先到修改提交");
        var restored=Hk3PhoneNotes.load(data.save(new CompoundTag()));
        check(!restored.saveNote(a,stale.id(),stale.version(),"断线旧草稿","旧正文",4),"重连后的旧版本仍拒绝");
        check(!restored.delete(a,stale.id(),stale.version()),"重连后的旧删除不生效");
        check(!restored.saveNote(b,stale.id(),2,"越权","",4)&&restored.find(b,stale.id())==null,"另一玩家不能借有效版本修改或读取");
        var latest=restored.find(a,stale.id());
        check(latest.version()==2&&latest.body().equals("服务器新正文"),"冲突保留服务器已提交正文");
        check(restored.saveNote(a,latest.id(),latest.version(),"重载后编辑","合并正文",5),"显式重读最新版本后可保存");
        check(restored.saveNote(a,"",0,"断线旧草稿","旧正文",6),"冲突草稿以零版本另存");
        check(restored.list(a).size()==2&&restored.find(a,stale.id()).version()==3,"另存保留原记录且生成独立ID");
        check(restored.list(b).size()==1&&restored.list(b).get(0).body().equals("独立正文"),"另一玩家账本不变");
        check(restored.delete(a,stale.id(),3)&&!restored.saveNote(a,stale.id(),3,"旧副本","",7),"删除后旧副本不能复活记录");
        check(!restored.saveNote(a,"",-1,"非法版本","",7),"新建拒绝负版本");
        var saved=restored.save(new CompoundTag());
        var max=saved.getCompound("Users").getList(a.toString(),Tag.TAG_COMPOUND).getCompound(0);max.putInt("Version",Integer.MAX_VALUE);
        var capped=Hk3PhoneNotes.load(saved);
        check(!capped.saveNote(a,max.getString("Id"),Integer.MAX_VALUE,"上溢","",8),"最大版本不溢出");
        check(capped.saveNote(a,"",0,"上限草稿另存","旧正文",8),"版本耗尽仍允许独立另存");
    }
    /** 【变更记录 #207】2026-11-05：手机回归增加文明总览全文阅读。 */
    public static void main(String[] args){tiles();snakes();notes();noteRecovery();PhoneCollectionTest.main(args);PhoneNotebookTest.main(args);PhoneTodoCalendarTest.main(args);PhoneCivilizationReadTest.main(args);PhoneAppHintsTest.main(args);PhoneGalleryTest.main(args);System.out.println("Phone apps: "+checks+" checks passed");}
}
