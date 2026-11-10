package com.sirin.hk3gtl.common.phone;
import java.util.*;
/**
 * 【变更记录 #1】2026-09-30 18:58:24（内测5修订114）
 * 删除：无；新增：2048和贪吃蛇纯逻辑；修改：无；用途：手机小游戏无奖励、不修改研究，支持确定种子回归。
 */
public final class Hk3PhoneGames {
    private Hk3PhoneGames(){}
    public static final class Tiles {
        private final Random random;private final int[] board=new int[16];private int score;
        public Tiles(long seed){random=new Random(seed);spawn();spawn();}
        public int[] cells(){return board.clone();}
        public int score(){return score;}
        public boolean won(){return Arrays.stream(board).anyMatch(n->n>=2048);}
        public void restore(int[] state,int value){
            if(state.length!=16||Arrays.stream(state).anyMatch(n->n<0||n>(1<<29)||(n!=0&&(n&(n-1))!=0))||value<0)throw new IllegalArgumentException("无效棋盘");
            System.arraycopy(state,0,board,0,16);score=value;
        }
        private void spawn(){
            var empty=new ArrayList<Integer>();for(int i=0;i<16;i++)if(board[i]==0)empty.add(i);
            if(!empty.isEmpty())board[empty.get(random.nextInt(empty.size()))]=random.nextInt(10)==0?4:2;
        }
        // 方向0上1右2下3左；同一块一次移动只合并一次。
        public boolean move(int dir){
            if(dir<0||dir>3)return false;int[] before=board.clone();
            for(int line=0;line<4;line++){
                int[] positions=new int[4],values=new int[4];int count=0;
                for(int i=0;i<4;i++){
                    int pos=switch(dir){case 0->i*4+line;case 1->line*4+3-i;case 2->(3-i)*4+line;default->line*4+i;};
                    positions[i]=pos;if(board[pos]!=0)values[count++]=board[pos];
                }
                int at=0;
                for(int i=0;i<count;i++){
                    int value=values[i];
                    if(i+1<count&&values[i+1]==value&&value<=1<<28){value*=2;i++;score=(int)Math.min(Integer.MAX_VALUE,(long)score+value);}
                    board[positions[at++]]=value;
                }
                while(at<4)board[positions[at++]]=0;
            }
            boolean changed=!Arrays.equals(before,board);if(changed)spawn();return changed;
        }
        public boolean over(){
            for(int i=0;i<16;i++)if(board[i]==0||(i%4<3&&board[i]<=1<<28&&board[i]==board[i+1])||(i<12&&board[i]<=1<<28&&board[i]==board[i+4]))return false;
            return true;
        }
    }
    public static final class Snake {
        public static final int SIZE=16;
        private final Random random;private final ArrayDeque<Integer> body=new ArrayDeque<>();
        private int direction=1,next=1,food,score;private boolean turned,over,won;
        public Snake(long seed){random=new Random(seed);body.add(8*SIZE+8);body.add(8*SIZE+7);body.add(8*SIZE+6);spawn();}
        public List<Integer> cells(){return List.copyOf(body);}
        public int food(){return food;}public int score(){return score;}public boolean over(){return over;}public boolean won(){return won;}
        public void turn(int dir){if(!turned&&dir>=0&&dir<4&&dir!=(direction+2)%4&&dir!=direction){next=dir;turned=true;}}
        private void spawn(){
            var empty=new ArrayList<Integer>();for(int i=0;i<SIZE*SIZE;i++)if(!body.contains(i))empty.add(i);
            if(empty.isEmpty()){won=true;over=true;food=-1;}else food=empty.get(random.nextInt(empty.size()));
        }
        public void step(){
            if(over)return;direction=next;turned=false;
            int head=body.peekFirst(),x=head%SIZE,y=head/SIZE;
            x+=direction==1?1:direction==3?-1:0;y+=direction==2?1:direction==0?-1:0;
            if(x<0||x>=SIZE||y<0||y>=SIZE){over=true;return;}
            int dest=y*SIZE+x;boolean grow=dest==food;
            if(body.contains(dest)&&(grow||dest!=body.peekLast())){over=true;return;}
            if(!grow)body.removeLast();body.addFirst(dest);
            if(grow){score++;spawn();}
        }
    }
}
