package com.sirin.hk3gtl.common.machine.w02;

import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.feature.multiblock.IMultiPart;
import com.sirin.hk3gtl.common.multiblock.build.Hk3UniversalTerminalBuilder;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3StructureBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.common.ForgeHooks;
import net.minecraftforge.common.util.BlockSnapshot;
import net.minecraftforge.event.ForgeEventFactory;
import java.util.ArrayList;
import java.util.List;

/** 显式修正旧测试船坞；只替换原灯块及旧填充壳，遇到真实仓室或改建立即保留。 */
final class Hk3W02PortMigration {
    private record Change(BlockPos pos,BlockState before,BlockState after) {}
    static String apply(Hk3W02Machine machine,ServerPlayer player) {
        var level=player.serverLevel();
        if(!player.isCreative() || player.isSpectator() || machine.getLevel()!=level || !level.getServer().isSameThread()
                || !player.getAbilities().mayBuild || Hk3UniversalTerminalBuilder.isBuilding(machine))return "仅空闲的创造测试船坞可校正接口。";
        if(!machine.getPatternLock().tryLock())return "结构正在检查，请稍后校正。";
        List<BlockSnapshot> applied=new ArrayList<>();
        try {
            if(MetaMachine.getMachine(level,machine.getPos())!=machine)return "控制器已改变。";
            var filler=Hk3StructureBlocks.require("hk3gtl:industrial_port_casing").defaultBlockState();
            var rotation=Hk3UniversalTerminalBuilder.rotation(Direction.SOUTH,machine.getFrontFacing());
            List<Change> changes=new ArrayList<>();
            for(var local:Hk3W02Pattern.PORTS) {
                var pos=local.rotate(rotation).offset(machine.getPos());
                if(!level.hasChunkAt(pos))return "接口区块尚未加载。";
                var present=level.getBlockState(pos);
                if(present==filler || MetaMachine.getMachine(level,pos) instanceof IMultiPart)continue;
                if(present.getBlock()!=Blocks.SEA_LANTERN)return "新接口位置已被改建，保留原块："+pos.toShortString();
                changes.add(new Change(pos,present,filler));
            }
            for(int x:new int[]{-36,-28,-20,-12,12,20,28,36}) {
                var pos=new BlockPos(x,0,0).rotate(rotation).offset(machine.getPos());
                if(!level.hasChunkAt(pos))return "旧接口区块尚未加载。";
                var present=level.getBlockState(pos);
                if(present.isAir())continue;
                if(present!=filler)return "旧位置有真实仓室或改建，请先手动搬移，未修改方块："+pos.toShortString();
                changes.add(new Change(pos,present,Blocks.AIR.defaultBlockState()));
            }
            for(var change:changes) {
                if(!level.mayInteract(player,change.pos)||!player.mayUseItemAt(change.pos,Direction.UP,player.getMainHandItem())
                        ||!level.getWorldBorder().isWithinBounds(change.pos)
                        ||ForgeHooks.onBlockBreakEvent(level,player.gameMode.getGameModeForPlayer(),player,change.pos)==-1)
                    return "接口校正被保护规则拒绝，未修改方块。";
            }
            machine.onStructureInvalid();
            for(var change:changes) {
                if(level.getBlockState(change.pos)!=change.before)throw new IllegalStateException("校正期间方块改变");
                var before=BlockSnapshot.create(level.dimension(),level,change.pos);applied.add(before);
                if(!level.setBlock(change.pos,change.after,Block.UPDATE_CLIENTS|Block.UPDATE_KNOWN_SHAPE)
                        ||!change.after.isAir()&&ForgeEventFactory.onBlockPlace(player,before,Direction.UP)
                        ||level.getBlockState(change.pos)!=change.after)throw new IllegalStateException("接口校正未被世界接受");
            }
            machine.requestIntegrityCheck();
            return "八接口已移到主控周围，旧浮空填充壳已移除；正在重新完整检查。";
        }catch(RuntimeException failure) {
            for(int i=applied.size()-1;i>=0;i--)try {
                if(!applied.get(i).restore(true,false))throw new IllegalStateException("接口快照回退失败");
            }catch(RuntimeException rollback){failure.addSuppressed(rollback);}
            com.mojang.logging.LogUtils.getLogger().error("W02接口校正失败",failure);
            return "接口校正失败并尝试回退；请核对日志。";
        }finally {machine.getPatternLock().unlock();}
    }
}
