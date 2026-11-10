package com.sirin.hk3gtl.common.easter;
import net.minecraft.core.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.*;
import net.minecraft.world.inventory.*;
import net.minecraft.world.level.block.*;
import net.minecraft.tags.*;
import java.util.*;
/** 【变更记录 #1】2026-10-01 05:59:33（修订128）：删除无；新增装饰方块的本人放置归属与箱子真实存入序列；修改无；用途：原条件的有界只读检测，不授研究资格。 */
/** 【变更记录 #2】2026-10-01 06:01:37（修订128）：删除：无；新增/修改：普通放置不扫描装饰窗口，只在羊毛放置时查询局部归属；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public final class Hk3EggExtraScenes {
    private Hk3EggExtraScenes(){}
    public static void placed(ServerPlayer p,BlockPos pos,net.minecraft.world.level.block.state.BlockState block){
        var memory=Hk3EggBuildMemory.get(p.serverLevel());var own=block.is(BlockTags.WOOL)?memory.near(p,pos,4):List.<BlockPos>of();
        if(block.is(BlockTags.WOOL)){
            // 5×5窗口可沿任一轴伸展，必须包含本次放置；高度亦限制5格。
            for(int dx=-4;dx<=0;dx++)for(int dz=-4;dz<=0;dz++)for(int dy=-4;dy<=0;dy++){
                var colors=new HashSet<Block>();for(var at:own)if(at.getX()>=pos.getX()+dx&&at.getX()<=pos.getX()+dx+4&&at.getZ()>=pos.getZ()+dz&&at.getZ()<=pos.getZ()+dz+4&&at.getY()>=pos.getY()+dy&&at.getY()<=pos.getY()+dy+4){var s=p.level().getBlockState(at);if(s.is(BlockTags.WOOL)&&Hk3EggBuildings.outsideStructure(p,at))colors.add(s.getBlock());}
                if(colors.size()>=4){Hk3EggVanilla.caseEvent(p,405);break;}
            }
        }
        if(block.is(Blocks.HONEY_BLOCK))for(var dir:Direction.values()){var at=pos.relative(dir);if(p.level().hasChunkAt(at)&&p.level().getBlockState(at).is(Blocks.ORANGE_WOOL)){Hk3EggRuntime.state(p).putBoolean("placedOrangeHoney",true);break;}}
        var spawn=p.getRespawnPosition();if(spawn==null||!p.getRespawnDimension().equals(p.level().dimension())||spawn.distSqr(pos)>256)return;
        boolean bed=false,table=false,torch=false,chest=false,light=false;
        for(var at:memory.near(p,spawn,16))if(spawn.distSqr(at)<=256){var s=p.level().getBlockState(at);bed|=s.getBlock() instanceof BedBlock;table|=s.is(Blocks.CRAFTING_TABLE);chest|=s.is(Blocks.CHEST)||s.is(Blocks.TRAPPED_CHEST);torch|=s.is(Blocks.TORCH)||s.is(Blocks.WALL_TORCH);light|=s.getLightEmission(p.level(),at)>0;}
        if(bed&&table&&torch)Hk3EggVanilla.caseEvent(p,423);
        if(bed&&table&&chest&&light)Hk3EggVanilla.caseEvent(p,472);
    }
    public static void played(ServerPlayer p,BlockPos pos){
        var memory=Hk3EggBuildMemory.get(p.serverLevel());if(!memory.owns(p,pos))return;
        for(var dir:List.of(Direction.EAST,Direction.SOUTH))for(int start=-2;start<=0;start++){
            var blocks=new HashSet<Block>();boolean valid=true;
            for(int i=0;i<3;i++){var at=pos.relative(dir,start+i);if(!memory.owns(p,at)){valid=false;break;}blocks.add(p.level().getBlockState(at).getBlock());}
            if(valid&&blocks.equals(Set.of(Blocks.JACK_O_LANTERN,Blocks.NOTE_BLOCK,Blocks.CAKE)))Hk3EggVanilla.caseEvent(p,453);
        }
    }
    public static void sign(ServerPlayer p,BlockPos pos,String text){
        var memory=Hk3EggBuildMemory.get(p.serverLevel());var own=memory.near(p,pos,5);
        if(text.equals("1048")&&own.stream().filter(at->p.level().getBlockState(at).is(Blocks.BROWN_WOOL)).count()>=5)Hk3EggVanilla.caseEvent(p,416);
        if(text.equals("深红之王"))for(var banner:own)if(p.level().getBlockState(banner).is(Blocks.RED_BANNER)||p.level().getBlockState(banner).is(Blocks.RED_WALL_BANNER)){
            if(banner.distSqr(pos)>2)continue;
            for(var dir:Direction.Plane.HORIZONTAL){var at=banner.relative(dir);if(p.level().hasChunkAt(at)&&blackStone(p.level().getBlockState(at).getBlock()))Hk3EggVanilla.caseEvent(p,389);}
        }
    }
    private static boolean blackStone(Block b){return b==Blocks.BLACKSTONE||b==Blocks.POLISHED_BLACKSTONE||b==Blocks.POLISHED_BLACKSTONE_BRICKS;}
    public static void stored(ServerPlayer p,AbstractContainerMenu menu,List<Hk3EggStorageFacts.Stack> before,List<Hk3EggStorageFacts.Stack> after){
        if(!(menu instanceof ChestMenu chest))return;
        var parts=Hk3EggChests.parts(p,chest.getContainer());if(parts.isEmpty())return;
        if(Hk3EggStorageFacts.increased(before,after,"minecraft:wooden_pickaxe"))Hk3EggRuntime.state(p).putBoolean("storedWoodPick",true);
        for(var part:parts){var pos=part.getBlockPos();
            if(Hk3EggStorageFacts.increased(before,after,"minecraft:iron_sword")){
                boolean surrounded=true;for(var dir:Direction.Plane.HORIZONTAL){var at=pos.relative(dir);if(!p.level().hasChunkAt(at)||!blackStone(p.level().getBlockState(at).getBlock())){surrounded=false;break;}}
                if(surrounded)Hk3EggVanilla.caseEvent(p,391);
            }
            if(Hk3EggStorageFacts.count(after,"minecraft:cobblestone")==51&&Hk3EggStorageFacts.increased(before,after,"minecraft:cobblestone")&&Hk3EggBuildMemory.get(p.serverLevel()).owns(p,pos)&&p.level().getBiome(pos).is(BiomeTags.IS_BEACH))Hk3EggVanilla.caseEvent(p,316);
        }
        // 同用途取真实工具类型，不通过物品名称猜测；至少其中一个槽由本次存入改变。
        for(int i=0;i+1<after.size();i++){
            var a=after.get(i);var b=after.get(i+1);if(a.empty()||b.empty()||a.id().split(":")[0].equals(b.id().split(":")[0])||(a.equals(before.get(i))&&b.equals(before.get(i+1))))continue;
            var one=net.minecraft.core.registries.BuiltInRegistries.ITEM.get(new net.minecraft.resources.ResourceLocation(a.id()));var two=net.minecraft.core.registries.BuiltInRegistries.ITEM.get(new net.minecraft.resources.ResourceLocation(b.id()));
            if((one instanceof PickaxeItem&&two instanceof PickaxeItem)||(one instanceof AxeItem&&two instanceof AxeItem)||(one instanceof ShovelItem&&two instanceof ShovelItem)||(one instanceof HoeItem&&two instanceof HoeItem)||(one instanceof SwordItem&&two instanceof SwordItem))Hk3EggVanilla.caseEvent(p,496);
        }
    }
    public static void tick(ServerPlayer p){
        var s=Hk3EggRuntime.state(p);
        if(s.getBoolean("storedWoodPick")&&p.getMainHandItem().getItem() instanceof PickaxeItem pick&&pick.getTier().getLevel()>Tiers.WOOD.getLevel()){Hk3EggVanilla.caseEvent(p,422);s.remove("storedWoodPick");}
    }
}
