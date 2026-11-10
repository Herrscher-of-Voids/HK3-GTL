package com.sirin.hk3gtl.common.easter;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.entity.*;
import net.minecraft.world.level.block.state.properties.ChestType;
import net.minecraft.core.*;
import java.util.*;
/** 【变更记录 #1】2026-10-01 05:53:29（修订128）：删除无；新增单双箱原生Container解析及告示牌核验；修改无；用途：只认当前菜单真实容器对象，不按玩家视线猜箱子，不强载邻区块。 */
public final class Hk3EggChests {
    public static final String SIGN_AUTHOR="hk3gtl_egg_sign_author",ROTTEN_AUTHOR="hk3gtl_egg_rotten_author";
    private Hk3EggChests(){}
    public static List<ChestBlockEntity> parts(ServerPlayer p,Container container){
        if(container instanceof ChestBlockEntity chest)return List.of(chest);
        if(!(container instanceof CompoundContainer pair))return List.of();
        var out=new ArrayList<ChestBlockEntity>();var pos=p.chunkPosition();
        for(int x=pos.x-1;x<=pos.x+1;x++)for(int z=pos.z-1;z<=pos.z+1;z++){
            var chunk=p.serverLevel().getChunkSource().getChunkNow(x,z);if(chunk==null)continue;
            for(var be:chunk.getBlockEntities().values())if(be instanceof ChestBlockEntity chest&&pair.contains(chest))out.add(chest);
        }return out.size()==2?List.copyOf(out):List.of();
    }
    public static Container container(ServerPlayer p,ChestBlockEntity chest){
        var state=chest.getBlockState();if(!(state.getBlock() instanceof ChestBlock block))return null;
        if(state.getValue(ChestBlock.TYPE)!=ChestType.SINGLE&&!p.level().hasChunkAt(chest.getBlockPos().relative(ChestBlock.getConnectedDirection(state))))return null;
        return ChestBlock.getContainer(block,state,p.level(),chest.getBlockPos(),true);
    }
    public static boolean text(SignBlockEntity sign,String expected){
        for(boolean front:new boolean[]{true,false}){var b=new StringBuilder();for(var line:sign.getText(front).getMessages(false))b.append(line.getString().strip());if(b.toString().equals(expected))return true;}return false;
    }
    public static boolean marked(ServerPlayer p,List<ChestBlockEntity> parts,String label,boolean authored){
        for(var chest:parts){
            if(!authored&&chest.hasCustomName()&&chest.getName().getString().equals(label))return true;
            for(var dir:Direction.values()){var at=chest.getBlockPos().relative(dir);if(!p.level().hasChunkAt(at))continue;
                if(p.level().getBlockEntity(at) instanceof SignBlockEntity sign&&text(sign,label)&&(!authored||(sign.getPersistentData().hasUUID(SIGN_AUTHOR)&&sign.getPersistentData().getUUID(SIGN_AUTHOR).equals(p.getUUID()))))return true;
            }
        }return false;
    }
    public static void isolated(ServerPlayer p,Container container,List<ChestBlockEntity> parts){
        if(parts.isEmpty()||parts.stream().noneMatch(c->c.getPersistentData().hasUUID(ROTTEN_AUTHOR)&&c.getPersistentData().getUUID(ROTTEN_AUTHOR).equals(p.getUUID()))||!marked(p,parts,"隔离",true))return;
        boolean found=false;for(int i=0;i<container.getContainerSize();i++){var stack=container.getItem(i);if(!stack.isEmpty()){if(!stack.is(net.minecraft.world.item.Items.ROTTEN_FLESH))return;found=true;}}
        if(found)Hk3EggVanilla.caseEvent(p,383);
    }
}
