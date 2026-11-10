package com.sirin.hk3gtl.common.easter;
import net.minecraft.core.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.tags.BlockTags;
import com.gregtechceu.gtceu.api.pattern.MultiblockWorldSavedData;
import java.util.*;
/** 【变更记录 #1】2026-10-01 05:41:36（修订128）：删除无；新增实际本人放置的四向门、21层立柱、7×7与9×9地板和16×10矩形；排除已登记GT结构成员；修改无；用途：只读当前已加载建筑，不生成结构或授予工程验收。 */
/** 【变更记录 #2】2026-10-01 05:44:13（修订128）：删除：旧固定上限或被替代的分支；新增/修改：四向门检测完整16格跨度，双色地板要求不同地图颜色而非仅不同注册方块；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public final class Hk3EggBuildings {
    private Hk3EggBuildings(){}
    public static boolean ordinary(ServerPlayer p,BlockPos pos,BlockState state){
        return !state.hasBlockEntity()&&state.isCollisionShapeFullBlock(p.level(),pos)&&
            (state.is(BlockTags.PLANKS)||state.is(BlockTags.STONE_BRICKS)||state.is(BlockTags.BASE_STONE_OVERWORLD)||state.is(BlockTags.WOOL)||state.is(Blocks.BRICKS)||state.is(Blocks.COBBLESTONE)||state.is(Blocks.DIRT)||net.minecraft.core.registries.BuiltInRegistries.BLOCK.getKey(state.getBlock()).getPath().endsWith("_concrete"));
    }
    public static boolean outsideStructure(ServerPlayer p,BlockPos pos){
        for(var structure:MultiblockWorldSavedData.getOrCreate(p.serverLevel()).getControllerInChunk(new net.minecraft.world.level.ChunkPos(pos)))if(structure.isPosInCache(pos))return false;return true;
    }
    public static void placed(ServerPlayer p,BlockPos pos,BlockState block){
        var memory=Hk3EggBuildMemory.get(p.serverLevel());memory.placed(p,pos);
        if(block.getBlock() instanceof DoorBlock&&!com.sirin.hk3gtl.common.narrative.Hk3NarrativeLog.isUnlocked(p,"E-EG-284")){
            var doors=new ArrayList<Hk3EggDoorPattern.Door>();for(var at:memory.near(p,pos,16)){var state=p.level().getBlockState(at);if(state.getBlock() instanceof DoorBlock)doors.add(new Hk3EggDoorPattern.Door(at.getX()-pos.getX(),at.getY()-pos.getY(),at.getZ()-pos.getZ(),state.getValue(DoorBlock.FACING).get2DDataValue()));}
            if(Hk3EggDoorPattern.matches(doors))Hk3EggVanilla.caseEvent(p,284);
        }
        if(!ordinary(p,pos,block)||!outsideStructure(p,pos))return;
        var s=Hk3EggRuntime.state(p);String dim=p.level().dimension().location().toString();
        var last=BlockPos.of(s.getLong("pillarLast"));int height=s.contains("pillarLast")&&s.getString("pillarDimension").equals(dim)&&pos.equals(last.above())?s.getInt("pillarLength")+1:1;
        s.putInt("pillarLength",Math.min(21,height));s.putLong("pillarLast",pos.asLong());s.putString("pillarDimension",dim);
        if(height>=21){boolean valid=true;for(int y=0;y<21;y++){var at=pos.below(y);if(!memory.owns(p,at)||!ordinary(p,at,p.level().getBlockState(at))||!outsideStructure(p,at)){valid=false;break;}}if(valid)Hk3EggVanilla.caseEvent(p,301);}
        if(!com.sirin.hk3gtl.common.narrative.Hk3NarrativeLog.isUnlocked(p,"E-EG-315")&&floor(p,pos,7,7,block.getBlock(),null,true))Hk3EggVanilla.caseEvent(p,315);
        if(!s.getBoolean("floor1610")&&(floor(p,pos,16,10,null,null,false)||floor(p,pos,10,16,null,null,false)))s.putBoolean("floor1610",true);
        if(!com.sirin.hk3gtl.common.narrative.Hk3NarrativeLog.isUnlocked(p,"E-EG-319")){
            var alternatives=new HashSet<Block>();for(var dir:Direction.Plane.HORIZONTAL){var at=pos.relative(dir);if(p.level().hasChunkAt(at)){var other=p.level().getBlockState(at);if(other.getBlock()!=block.getBlock()&&other.getMapColor(p.level(),at).col!=block.getMapColor(p.level(),pos).col&&ordinary(p,at,other))alternatives.add(other.getBlock());}}
            for(var other:alternatives)if(floor(p,pos,9,9,block.getBlock(),other,false)){Hk3EggVanilla.caseEvent(p,319);break;}
        }
    }
    private static boolean floor(ServerPlayer p,BlockPos center,int width,int depth,Block first,Block second,boolean ground){
        var memory=Hk3EggBuildMemory.get(p.serverLevel());boolean[][] cells=new boolean[width*2-1][depth*2-1];
        for(int x=0;x<cells.length;x++)for(int z=0;z<cells[x].length;z++){
            var at=center.offset(x-width+1,0,z-depth+1);if(!memory.owns(p,at))continue;var state=p.level().getBlockState(at);
            if(!ordinary(p,at,state)||!outsideStructure(p,at))continue;
            if(first!=null&&!state.is(second==null||Math.floorMod(at.getX()+at.getZ()-center.getX()-center.getZ(),2)==0?first:second))continue;
            if(ground&&!p.level().getBlockState(at.below()).isFaceSturdy(p.level(),at.below(),Direction.UP))continue;
            cells[x][z]=true;
        }return Hk3EggFloorPattern.contains(cells,width,depth);
    }
}
