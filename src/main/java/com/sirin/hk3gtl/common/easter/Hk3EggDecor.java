package com.sirin.hk3gtl.common.easter;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.core.*;
import net.minecraft.world.item.*;
import net.minecraft.world.entity.decoration.ItemFrame;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.entity.*;
import net.minecraft.world.phys.AABB;
import java.util.*;
public final class Hk3EggDecor {
    private static final String OWNER="hk3gtl_egg_frame_author";
    private Hk3EggDecor(){}
    public static void framed(ServerPlayer p,ItemFrame frame){
        frame.getPersistentData().putUUID(OWNER,p.getUUID());
        if(Set.of("artifact_void_archives","imitation_void_archives","imitation_star_of_eden","imitation_oath_of_judah")
                .contains(net.minecraft.core.registries.BuiltInRegistries.ITEM.getKey(frame.getItem().getItem()).getPath())
                &&net.minecraft.core.registries.BuiltInRegistries.ITEM.getKey(frame.getItem().getItem()).getNamespace().equals("hk3gtl"))
            Hk3EggRuntime.observe(p,"divine_key_displayed",Map.of("display","item_frame","inserted","true"));
        if(frame.getItem().is(Items.CARVED_PUMPKIN))Hk3EggVanilla.caseEvent(p,386);
        for(var other:p.level().getEntitiesOfClass(ItemFrame.class,frame.getBoundingBox().inflate(5),f->f!=frame)){
            var n=other.getPersistentData();if(!n.hasUUID(OWNER)||!n.getUUID(OWNER).equals(p.getUUID())||frame.getDirection()!=other.getDirection())continue;
            var a=frame.blockPosition();var b=other.blockPosition();int dx=Math.abs(a.getX()-b.getX()),dz=Math.abs(a.getZ()-b.getZ());
            if(a.getY()!=b.getY()||!(dx==0||dz==0))continue;
            if(frame.getItem().is(Items.ENDER_EYE)&&other.getItem().is(Items.ENDER_EYE)){
                if(dx+dz==1)Hk3EggVanilla.caseEvent(p,397);
                if(dx+dz==4)Hk3EggVanilla.caseEvent(p,449);
            }
            if(dx+dz==1&&frame.getItem().getItem() instanceof SwordItem one&&other.getItem().getItem() instanceof SwordItem two&&one.getTier()!=two.getTier())Hk3EggVanilla.caseEvent(p,447);
        }
    }
    public static void ateCake(ServerPlayer p,BlockPos pos){
        if(Hk3EggBuildMemory.get(p.serverLevel()).owns(p,pos))Hk3EggVanilla.caseEvent(p,480);
    }
    public static void sign(ServerPlayer p,SignBlockEntity sign,boolean front){
        StringBuilder b=new StringBuilder();for(var line:sign.getText(front).getMessages(false))b.append(line.getString()).append(' ');String text=b.toString().strip();
        Hk3EggExtraScenes.sign(p,sign.getBlockPos(),text);
        var pos=sign.getBlockPos();
        if(text.equals("073"))for(var dir:Direction.Plane.HORIZONTAL){var at=pos.relative(dir);if(p.level().hasChunkAt(at)&&p.level().getBlockState(at).is(Blocks.WHEAT)&&Hk3EggBuildMemory.get(p.serverLevel()).owns(p,at))Hk3EggVanilla.caseEvent(p,390);}
        sign.getPersistentData().putUUID(Hk3EggChests.SIGN_AUTHOR,p.getUUID());sign.setChanged();
        if(text.equals("隔离"))for(var dir:Direction.values()){
            var at=pos.relative(dir);if(!p.level().hasChunkAt(at))continue;
            if(p.level().getBlockEntity(at) instanceof ChestBlockEntity chest){var container=Hk3EggChests.container(p,chest);if(container!=null)Hk3EggChests.isolated(p,container,Hk3EggChests.parts(p,container));}
        }
    }
    public static void container(ServerPlayer p,net.minecraft.world.inventory.AbstractContainerMenu menu,List<Hk3EggStorageFacts.Stack> before,List<Hk3EggStorageFacts.Stack> after){
        if(!(menu instanceof net.minecraft.world.inventory.ChestMenu chestMenu))return;
        var parts=Hk3EggChests.parts(p,chestMenu.getContainer());if(parts.isEmpty())return;var state=Hk3EggRuntime.state(p);
        if(Hk3EggStorageFacts.increased(before,after,"minecraft:rotten_flesh")){
            for(var chest:parts){chest.getPersistentData().putUUID(Hk3EggChests.ROTTEN_AUTHOR,p.getUUID());chest.setChanged();}
            Hk3EggChests.isolated(p,chestMenu.getContainer(),parts);
        }
        if(Hk3EggStorageFacts.increased(before,after,"minecraft:golden_apple")&&Hk3EggChests.marked(p,parts,"药箱",false))Hk3EggVanilla.caseEvent(p,407);
        if(Hk3EggStorageFacts.increased(before,after,"minecraft:mushroom_stew"))for(var chest:parts)for(var dir:Direction.Plane.HORIZONTAL){
            var at=chest.getBlockPos().relative(dir);if(p.level().hasChunkAt(at)&&p.level().getBlockState(at).getBlock() instanceof BedBlock){state.putString("stewBedDim",p.level().dimension().location().toString());state.putLong("stewBed",at.asLong());state.putLong("stewChest",chest.getBlockPos().asLong());}
        }
    }
    public static void sleeping(ServerPlayer p){
        if(p.getSleepingPos().filter(at->com.sirin.hk3gtl.common.machine.hyperion.Hk3HyperionMachine
                .containsVerifiedInterior(p.serverLevel(),at)).isPresent())
            Hk3EggRuntime.observe(p,"flagship_bed_entered",Map.of("sleeping","true","verified_interior","true"));
        var s=Hk3EggRuntime.state(p);if(!s.contains("stewChest")||!s.contains("stewBed")||!s.getString("stewBedDim").equals(p.level().dimension().location().toString()))return;
        var bed=p.getSleepingPos();if(bed.isEmpty()||bed.get().distSqr(BlockPos.of(s.getLong("stewBed")))>1)return;
        var at=BlockPos.of(s.getLong("stewChest"));if(!p.level().hasChunkAt(at)||!(p.level().getBlockEntity(at) instanceof ChestBlockEntity chest))return;
        var container=Hk3EggChests.container(p,chest);if(container==null)return;
        for(int i=0;i<container.getContainerSize();i++)if(container.getItem(i).is(Items.MUSHROOM_STEW)){Hk3EggVanilla.caseEvent(p,404);break;}
    }
}
