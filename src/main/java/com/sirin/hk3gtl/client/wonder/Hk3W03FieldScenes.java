package com.sirin.hk3gtl.client.wonder;

import com.sirin.hk3gtl.common.machine.w03.Hk3W03FieldPacket;
import it.unimi.dsi.fastutil.longs.Long2ObjectOpenHashMap;
import net.minecraft.client.Minecraft;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import java.io.DataInputStream;
import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.zip.GZIPInputStream;

/** 只替换已成型C9的既有实体画面；碰撞、世界状态和GT判断仍读取真实方块。 */
public final class Hk3W03FieldScenes {
    public record Scene(Hk3W03FieldPacket state,long received){}
    private static volatile List<Scene> scenes=List.of();
    private static volatile Long2ObjectOpenHashMap<long[]> mask;
    private static CompletableFuture<?> loading;
    private static Object level;
    private Hk3W03FieldScenes(){}
    public static List<Scene> scenes(){return scenes;}
    public static boolean maskReady(){return mask!=null;}
    public static void accept(Hk3W03FieldPacket state){
        var mc=Minecraft.getInstance();if(mc.level==null||!mc.level.dimension().location().equals(state.dimension()))return;
        if(level!=mc.level){scenes=List.of();level=mc.level;}
        boolean existed=scenes.stream().anyMatch(s->s.state.pos().equals(state.pos()));
        var next=new ArrayList<>(scenes);next.removeIf(s->s.state.pos().equals(state.pos()));
        if(state.formed())next.add(new Scene(state,mc.level.getGameTime()));scenes=List.copyOf(next);
        if(mask==null&&loading==null)loading=CompletableFuture.runAsync(Hk3W03FieldScenes::loadMask);
        if(existed!=state.formed()&&Hk3W03FxRenderer.ready())mc.levelRenderer.allChanged();
    }
    public static void maintain(){
        var mc=Minecraft.getInstance();if(level!=mc.level){if(!scenes.isEmpty())clear();return;}
        if(mc.level!=null&&scenes.stream().anyMatch(s->mc.level.getGameTime()-s.received>120)){
            scenes=scenes.stream().filter(s->mc.level.getGameTime()-s.received<=120).toList();mc.levelRenderer.allChanged();
        }
    }
    public static void clear(){scenes=List.of();level=null;}
    public static boolean hidden(BlockPos world){
        var data=mask;if(data==null||scenes.isEmpty()||!Hk3W03FxRenderer.ready())return false;
        for(var scene:scenes){
            var s=scene.state;int dx=world.getX()-s.pos().getX(),y=world.getY()-s.pos().getY()+27,dz=world.getZ()-s.pos().getZ();
            int x=dx,z=dz;
            switch(s.facing()){
                case EAST->{x=dz;z=-dx;}
                case SOUTH->{x=-dx;z=-dz;}
                case WEST->{x=-dz;z=dx;}
                default->{}
            }
            x+=416;z+=187;if(x<0||x>=833||y<0||y>=636||z<0||z>=833)continue;
            if(y==27&&z==187&&(x==416||Arrays.binarySearch(PORT_X,x)>=0))continue;
            var bits=data.get(BlockPos.asLong(x>>4,y>>4,z>>4));int bit=((y&15)*16+(z&15))*16+(x&15);
            if(bits!=null&&(bits[bit>>>6]&(1L<<(bit&63)))!=0)return true;
        }return false;
    }
    private static final int[] PORT_X={398,402,406,410,422,426,430,434};
    private static void loadMask(){
        try(var raw=Hk3W03FieldScenes.class.getResourceAsStream("/data/hk3gtl/structures/w03_c9_mask.bin.gz");
            var input=new DataInputStream(new GZIPInputStream(Objects.requireNonNull(raw)))){
            if(input.readInt()!=0x5730334d)throw new java.io.IOException("C9遮罩格式错误");
            int count=input.readInt();if(count<1||count>150000)throw new java.io.IOException("C9遮罩数量错误");
            var result=new Long2ObjectOpenHashMap<long[]>(count);
            for(int i=0;i<count;i++){long key=input.readLong();long[] bits=new long[64];for(int n=0;n<64;n++)bits[n]=input.readLong();if(result.put(key,bits)!=null)throw new java.io.IOException("C9遮罩重复");}
            if(input.read()!=-1)throw new java.io.IOException("C9遮罩尾随数据");mask=result;
            Minecraft.getInstance().execute(()->Minecraft.getInstance().levelRenderer.allChanged());
        }catch(Exception failure){com.mojang.logging.LogUtils.getLogger().error("C9实体画面替换遮罩加载失败，保留原方块画面",failure);}
    }
}
