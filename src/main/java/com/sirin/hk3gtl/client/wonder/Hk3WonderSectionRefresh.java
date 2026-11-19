package com.sirin.hk3gtl.client.wonder;

import com.sirin.hk3gtl.common.multiblock.build.Hk3UniversalTerminalBuilder;
import it.unimi.dsi.fastutil.longs.LongLinkedOpenHashSet;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.SectionPos;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

@Mod.EventBusSubscriber(modid="hk3gtl",value=Dist.CLIENT)
public final class Hk3WonderSectionRefresh {
    private record Bounds(int minX,int minY,int minZ,int maxX,int maxY,int maxZ){}
    private static final Map<String,List<Bounds>> PREVIOUS=new HashMap<>();
    private static final Set<Bounds> REQUESTED=new HashSet<>();
    private static final LongLinkedOpenHashSet SECTIONS=new LongLinkedOpenHashSet();
    private static ClientLevel level;
    private Hk3WonderSectionRefresh(){}

    public static void request(String... roles){
        var current=Minecraft.getInstance().level;
        if(level!=current)reset(current);
        if(level==null)return;
        for(String role:roles){
            REQUESTED.addAll(PREVIOUS.getOrDefault(role,List.of()));
            var next=bounds(role);REQUESTED.addAll(next);
            if(next.isEmpty())PREVIOUS.remove(role);else PREVIOUS.put(role,next);
        }
    }

    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event){
        if(event.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        if(level!=mc.level)reset(mc.level);
        if(level==null)return;
        var camera=mc.gameRenderer.getMainCamera().getBlockPosition();
        int cx=camera.getX()>>4,cz=camera.getZ()>>4,distance=mc.options.getEffectiveRenderDistance();
        for(var bounds:REQUESTED){
            int minX=Math.max((bounds.minX-1)>>4,cx-distance),maxX=Math.min((bounds.maxX+1)>>4,cx+distance);
            int minZ=Math.max((bounds.minZ-1)>>4,cz-distance),maxZ=Math.min((bounds.maxZ+1)>>4,cz+distance);
            int minY=Math.max((bounds.minY-1)>>4,level.getMinSection()),maxY=Math.min((bounds.maxY+1)>>4,level.getMaxSection()-1);
            for(int x=minX;x<=maxX;x++)for(int z=minZ;z<=maxZ;z++){
                if(!level.hasChunk(x,z))continue;
                for(int y=minY;y<=maxY;y++)SECTIONS.add(SectionPos.asLong(x,y,z));
            }
        }
        REQUESTED.clear();
        for(int count=0;count<256&&!SECTIONS.isEmpty();count++){
            long section=SECTIONS.removeFirstLong();int x=SectionPos.x(section),y=SectionPos.y(section),z=SectionPos.z(section);
            if(Math.abs(x-cx)<=distance&&Math.abs(z-cz)<=distance&&level.hasChunk(x,z))mc.levelRenderer.setSectionDirty(x,y,z);
        }
    }

    private static void reset(ClientLevel current){
        PREVIOUS.clear();REQUESTED.clear();SECTIONS.clear();level=current;
    }

    private static List<Bounds> bounds(String role){
        var result=new ArrayList<Bounds>();
        switch(role){
            case "W03"->{
                if(Hk3W03FxRenderer.ready()&&Hk3W03FieldScenes.maskReady())for(var scene:Hk3W03FieldScenes.scenes()){
                    var state=scene.state();add(result,state.pos(),state.facing(),Direction.NORTH,new int[]{416,27,187},new int[3],new int[]{833,636,833});
                }
            }
            case "W08"->{
                if(Hk3W08FieldScenes.active())for(var scene:Hk3W08FieldScenes.scenes()){
                    var state=scene.state();add(result,state.pos(),state.facing(),Direction.NORTH,new int[]{256,238,165},new int[3],new int[]{512,477,512});
                }
            }
            case "W10"->{
                if(Hk3W10FieldScenes.active()){
                    var data=Hk3W10FxRenderer.data();
                    for(var scene:Hk3W10FieldScenes.scenes()){
                        var state=scene.state();add(result,state.pos(),state.facing(),Direction.NORTH,data.controller_blueprint(),data.blueprint_to_export_offset_xyz(),data.sizeXYZ());
                    }
                }
            }
            case "W11"->{
                if(Hk3W11FieldScenes.active()){
                    var data=Hk3W11FxRenderer.data();
                    for(var scene:Hk3W11FieldScenes.scenes()){
                        var state=scene.state();add(result,state.pos(),state.facing(),Direction.SOUTH,data.controller_blueprint(),data.blueprint_to_export_offset_xyz(),data.sizeXYZ());
                    }
                }
            }
            case "W12"->{
                if(Hk3W12FieldScenes.active()){
                    var data=Hk3W12FxRenderer.data();
                    for(var scene:Hk3W12FieldScenes.scenes()){
                        var state=scene.state();add(result,state.pos(),state.facing(),Direction.NORTH,data.controller_blueprint(),data.blueprint_to_export_offset_xyz(),data.sizeXYZ());
                    }
                }
            }
            case "W13"->{
                if(Hk3W13FieldScenes.active()){
                    var data=Hk3W13FxRenderer.data();
                    for(var scene:Hk3W13FieldScenes.scenes())if(scene.state().running()){
                        var state=scene.state();add(result,state.pos(),state.facing(),Direction.SOUTH,data.controller_blueprint(),data.blueprint_to_export_offset_xyz(),data.sizeXYZ());
                    }
                }
            }
            default->{
                if(Hk3WonderFxScenes.active(role)){
                    var data=Hk3WonderFxRenderer.data(role);
                    for(var scene:Hk3WonderFxScenes.scenes())if(scene.state().role().equals(role)){
                        var state=scene.state();add(result,state.pos(),state.facing(),Direction.NORTH,data.controller_blueprint(),data.blueprint_to_export_offset_xyz(),data.sizeXYZ());
                    }
                }
            }
        }
        return result;
    }

    private static void add(List<Bounds> result,BlockPos pos,Direction facing,Direction source,int[] control,int[] offset,int[] size){
        int minX=Integer.MAX_VALUE,maxX=Integer.MIN_VALUE,minZ=Integer.MAX_VALUE,maxZ=Integer.MIN_VALUE;
        var rotation=Hk3UniversalTerminalBuilder.rotation(source,facing);
        for(int x:new int[]{0,size[0]-1})for(int z:new int[]{0,size[2]-1}){
            var corner=new BlockPos(x-control[0]-offset[0],0,z-control[2]-offset[2]).rotate(rotation).offset(pos);
            minX=Math.min(minX,corner.getX());maxX=Math.max(maxX,corner.getX());minZ=Math.min(minZ,corner.getZ());maxZ=Math.max(maxZ,corner.getZ());
        }
        int minY=pos.getY()-control[1]-offset[1];
        result.add(new Bounds(minX,minY,minZ,maxX,minY+size[1]-1,maxZ));
    }
}
