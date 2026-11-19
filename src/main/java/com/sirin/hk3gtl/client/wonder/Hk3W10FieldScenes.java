package com.sirin.hk3gtl.client.wonder;

import com.sirin.hk3gtl.common.util.Hk3PackedResources;
import com.sirin.hk3gtl.common.machine.w10.Hk3W10FieldPacket;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3InterfacePredicates;
import it.unimi.dsi.fastutil.longs.Long2ObjectOpenHashMap;
import net.minecraft.client.Minecraft;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.state.BlockState;
import java.io.DataInputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.concurrent.CompletableFuture;

public final class Hk3W10FieldScenes {
    public record Scene(Hk3W10FieldPacket state,long received,Hk3W08Ports ports) {}
    private static volatile List<Scene> scenes=List.of();
    private static volatile Long2ObjectOpenHashMap<long[]> mask;
    private static CompletableFuture<?> loading;
    private static Object level;
    private Hk3W10FieldScenes(){}
    public static List<Scene> scenes(){return scenes;}
    public static boolean active(){return mask!=null&&Hk3W10FxRenderer.ready()&&!scenes.isEmpty();}
    public static void accept(Hk3W10FieldPacket packet){
        var mc=Minecraft.getInstance();if(mc.level==null||!mc.level.dimension().location().equals(packet.dimension()))return;
        if(level!=mc.level){clear();level=mc.level;}
        var previous=scenes.stream().filter(s->s.state.pos().equals(packet.pos())).findFirst().orElse(null);
        boolean existed=previous!=null;
        var next=new ArrayList<>(scenes);next.removeIf(s->s.state.pos().equals(packet.pos()));
        if(packet.formed()){
            var ports=previous!=null&&java.util.Arrays.equals(previous.state.ports(),packet.ports())?previous.ports:new Hk3W08Ports(packet.ports());
            if(previous!=null&&ports!=previous.ports)previous.ports.close();
            next.add(new Scene(packet,mc.level.getGameTime(),ports));
        }else if(previous!=null)previous.ports.close();
        scenes=List.copyOf(next);
        if(mask==null&&loading==null)loading=CompletableFuture.runAsync(Hk3W10FieldScenes::loadMask);
        if(existed!=packet.formed()&&Hk3W10FxRenderer.ready())Hk3WonderSectionRefresh.request("W10");
    }
    public static void maintain(){
        var mc=Minecraft.getInstance();if(level!=mc.level){clear();return;}
        if(mc.level!=null&&scenes.stream().anyMatch(s->mc.level.getGameTime()-s.received>120)){
            scenes.stream().filter(s->mc.level.getGameTime()-s.received>120).forEach(s->s.ports.close());
            scenes=scenes.stream().filter(s->mc.level.getGameTime()-s.received<=120).toList();Hk3WonderSectionRefresh.request("W10");
        }
    }
    public static void clear(){scenes.forEach(s->s.ports.close());scenes=List.of();level=null;}
    public static boolean hidden(BlockPos world,BlockState state){
        var cells=mask;if(!active()||Hk3InterfacePredicates.isInterface(state))return false;
        var data=Hk3W10FxRenderer.data();int[] control=data.controller_blueprint(),offset=data.blueprint_to_export_offset_xyz(),size=data.sizeXYZ();
        for(var scene:scenes){
            var s=scene.state;int dx=world.getX()-s.pos().getX(),dz=world.getZ()-s.pos().getZ(),x=dx,z=dz;
            switch(s.facing()){
                case EAST->{x=dz;z=-dx;}case SOUTH->{x=-dx;z=-dz;}case WEST->{x=-dz;z=dx;}default->{}
            }
            x+=control[0]+offset[0];z+=control[2]+offset[2];int y=world.getY()-s.pos().getY()+control[1]+offset[1];
            if(x<0||x>=size[0]||y<0||y>=size[1]||z<0||z>=size[2])continue;
            var bits=cells.get(BlockPos.asLong(x>>4,y>>4,z>>4));int bit=((y&15)*16+(z&15))*16+(x&15);
            if(bits!=null&&(bits[bit>>>6]&(1L<<(bit&63)))!=0)return true;
        }
        return false;
    }
    public static long signature(){
        if(!active())return 0;long value=17;
        for(var scene:scenes)value=value*31+scene.state.pos().asLong()*7+scene.state.facing().ordinal();
        return value;
    }
    public static void addColumns(Set<Long> columns){
        if(!active())return;
        var data=Hk3W10FxRenderer.data();int[] control=data.controller_blueprint(),offset=data.blueprint_to_export_offset_xyz(),size=data.sizeXYZ();
        for(var scene:scenes){
            int minX=Integer.MAX_VALUE,maxX=Integer.MIN_VALUE,minZ=Integer.MAX_VALUE,maxZ=Integer.MIN_VALUE;
            var rotation=com.sirin.hk3gtl.common.multiblock.build.Hk3UniversalTerminalBuilder.rotation(net.minecraft.core.Direction.NORTH,scene.state.facing());
            for(int x:new int[]{0,size[0]-1})for(int z:new int[]{0,size[2]-1}){
                var p=new BlockPos(x-offset[0]-control[0],0,z-offset[2]-control[2]).rotate(rotation).offset(scene.state.pos());
                minX=Math.min(minX,p.getX());maxX=Math.max(maxX,p.getX());minZ=Math.min(minZ,p.getZ());maxZ=Math.max(maxZ,p.getZ());
            }
            for(int x=minX>>6;x<=maxX>>6;x++)for(int z=minZ>>6;z<=maxZ>>6;z++)columns.add(net.minecraft.world.level.ChunkPos.asLong(x,z));
        }
    }
    private static void loadMask(){
        try(var raw=Hk3PackedResources.resource(Hk3W10FieldScenes.class,"/data/hk3gtl/structures/w10_a3_mask.bin.gz");
            var input=new DataInputStream(Hk3PackedResources.decompress(raw))){
            if(input.readInt()!=0x5731304d)throw new IOException("W10遮罩格式不符");
            int count=input.readInt();var result=new Long2ObjectOpenHashMap<long[]>(count);
            for(int i=0;i<count;i++){long key=input.readLong();long[] bits=new long[64];for(int n=0;n<64;n++)bits[n]=input.readLong();result.put(key,bits);}
            mask=result;Minecraft.getInstance().execute(()->Hk3WonderSectionRefresh.request("W10"));
        }catch(IOException failure){com.mojang.logging.LogUtils.getLogger().error("W10实体遮罩读取失败",failure);}
    }
}
