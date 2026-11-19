package com.sirin.hk3gtl.common.multiblock.loading;

import com.gregtechceu.gtceu.api.capability.forge.GTCapability;
import com.gregtechceu.gtceu.api.capability.ICleanroomReceiver;
import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.gregtechceu.gtceu.api.machine.feature.multiblock.IMultiPart;
import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import com.gregtechceu.gtceu.common.machine.multiblock.electric.CleanroomMachine;
import com.sirin.hk3gtl.common.multiblock.build.Hk3BuildChunkWindow;
import com.sirin.hk3gtl.common.multiblock.build.Hk3InterfaceChunks;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3NativeWonderPattern;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LargeStructurePattern;
import it.unimi.dsi.fastutil.ints.Int2ObjectOpenHashMap;
import it.unimi.dsi.fastutil.longs.Long2ObjectOpenHashMap;
import it.unimi.dsi.fastutil.longs.LongArrayList;
import it.unimi.dsi.fastutil.longs.LongOpenHashSet;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.chunk.PalettedContainer;
import java.util.Set;

/** 分批读取真实区块；原匹配器及形成回调共用同一份只读证据。 */
public final class Hk3PatternLoading implements AutoCloseable {
    private static final ThreadLocal<Hk3PatternLoading> CURRENT=new ThreadLocal<>();
    static final Pending PENDING=new Pending();
    static final class Pending extends RuntimeException {
        private Pending(){super(null,null,false,false);}
    }
    final MultiblockControllerMachine controller;
    final ServerLevel level;
    private boolean forming,rollingBack;
    private final Direction facing,up;
    private final Hk3BuildChunkWindow window;
    private final Hk3InterfaceChunks candidates;
    private final LongArrayList order=new LongArrayList();
    private final LongOpenHashSet requested=new LongOpenHashSet();
    private final LongOpenHashSet retainedPositions=new LongOpenHashSet();
    private final Long2ObjectOpenHashMap<ICleanroomReceiver> cleanroomReceivers=new Long2ObjectOpenHashMap<>();
    private final Long2ObjectOpenHashMap<Int2ObjectOpenHashMap<PalettedContainer<BlockState>>> snapshots=new Long2ObjectOpenHashMap<>();
    private int cursor;
    private long revision;
    private boolean transferred;
    private final Hk3NativeWonderCheck nativeCheck;
    private final Hk3LargeStructurePattern.Check largeCheck;

    Hk3PatternLoading(MultiblockControllerMachine controller){
        this.controller=controller;level=(ServerLevel)controller.getLevel();
        facing=controller.getFrontFacing();up=controller.getUpwardsFacing();
        window=new Hk3BuildChunkWindow(level,controller.getPos().asLong());
        candidates=new Hk3InterfaceChunks(level,controller.getPos());candidates.retain(controller.getPos());
        var pattern=controller.getPattern();
        nativeCheck=pattern instanceof Hk3NativeWonderPattern wonder?new Hk3NativeWonderCheck(this,wonder):null;
        largeCheck=pattern instanceof Hk3LargeStructurePattern large?large.newCheck(this):null;
        request(ChunkPos.asLong(controller.getPos().getX()>>4,controller.getPos().getZ()>>4));
    }

    public static Hk3PatternLoading current(Level level){
        var loading=CURRENT.get();return loading!=null&&loading.level==level&&!loading.rollingBack?loading:null;
    }
    static Hk3NativeWonderCheck currentNative(){
        var loading=CURRENT.get();return loading!=null&&!loading.forming&&!loading.rollingBack?loading.nativeCheck:null;
    }
    boolean running(){return CURRENT.get()==this;}
    boolean nativeChunkReady(long chunk){return window.ready(0,1,index->chunk,index->index+1);}
    public Hk3LargeStructurePattern.Check largeCheck(){return largeCheck;}
    public void checkpoint(BlockPos pos,long[] chunks,long deadline){
        if(System.nanoTime()>=deadline||!window.ready(0,chunks.length,index->chunks[index],index->index+1)
                ||level.getChunkSource().getChunkNow(pos.getX()>>4,pos.getZ()>>4)==null)throw PENDING;
    }
    private boolean streaming(){return nativeCheck!=null||largeCheck!=null;}
    boolean valid(){
        return !controller.isInValid()&&controller.getLevel()==level
                &&controller.getFrontFacing()==facing&&controller.getUpwardsFacing()==up;
    }
    private void request(long chunk){if(requested.add(chunk))order.add(chunk);}
    private Int2ObjectOpenHashMap<PalettedContainer<BlockState>> snapshot(long chunk){
        var data=snapshots.get(chunk);
        if(data==null){request(chunk);throw PENDING;}
        return data;
    }
    boolean capture(long deadline){
        if(streaming())return true;
        int copied=0;
        while(cursor<order.size()&&copied<8&&System.nanoTime()<deadline){
            if(!window.ready(cursor,order.size(),order::getLong,i->i+1))return false;
            long key=order.getLong(cursor);
            var chunk=level.getChunkSource().getChunkNow(ChunkPos.getX(key),ChunkPos.getZ(key));
            var data=new Int2ObjectOpenHashMap<PalettedContainer<BlockState>>();
            var sections=chunk.getSections();
            for(int i=0;i<sections.length;i++)if(!sections[i].hasOnlyAir())data.put(chunk.getMinSection()+i,sections[i].getStates().copy());
            snapshots.put(key,data);
            // 匹配器会读取真实方块实体；先保留候选，成型后只移交实际访问的实体区块。
            for(var pos:chunk.getBlockEntities().keySet())candidates.retain(pos);
            cursor++;copied++;
        }
        if(cursor==order.size()){window.close();return true;}
        return false;
    }
    public BlockState blockState(BlockPos pos){
        if(level.isOutsideBuildHeight(pos))return Blocks.VOID_AIR.defaultBlockState();
        if(streaming()){
            var chunk=level.getChunkSource().getChunkNow(pos.getX()>>4,pos.getZ()>>4);
            if(chunk==null){
                if(nativeCheck!=null)nativeCheck.missingChunk();
                if(largeCheck!=null)largeCheck.missingChunk();
                throw PENDING;
            }
            return chunk.getBlockState(pos);
        }
        long key=ChunkPos.asLong(pos.getX()>>4,pos.getZ()>>4);
        LevelChunk live=level.getChunkSource().getChunkNow(pos.getX()>>4,pos.getZ()>>4);
        if(forming&&live!=null)return live.getBlockState(pos);
        var data=snapshot(key);
        if(live!=null)return live.getBlockState(pos);
        var section=data.get(pos.getY()>>4);
        return section==null?Blocks.AIR.defaultBlockState():section.get(pos.getX()&15,pos.getY()&15,pos.getZ()&15);
    }
    public BlockEntity blockEntity(BlockPos pos){
        if(!blockState(pos).hasBlockEntity())return null;
        if(!streaming())candidates.retain(pos);
        var chunk=level.getChunkSource().getChunkNow(pos.getX()>>4,pos.getZ()>>4);
        if(chunk==null)throw PENDING;
        var entity=chunk.getBlockEntity(pos);
        if(streaming()&&entity instanceof IMachineBlockEntity holder&&holder.getMetaMachine() instanceof IMultiPart)
            candidates.retain(pos);
        if(forming&&entity!=null)retainedPositions.add(pos.asLong());
        if(!forming&&entity!=null&&controller instanceof CleanroomMachine)
            entity.getCapability(GTCapability.CAPABILITY_CLEANROOM_RECEIVER).ifPresent(receiver->cleanroomReceivers.put(pos.asLong(),receiver));
        return entity;
    }
    public boolean loaded(BlockPos pos){
        if(level.isOutsideBuildHeight(pos))return false;
        if(forming||streaming())return level.getChunkSource().getChunkNow(pos.getX()>>4,pos.getZ()>>4)!=null;
        snapshot(ChunkPos.asLong(pos.getX()>>4,pos.getZ()>>4));return true;
    }
    void changed(BlockPos pos,BlockState state){
        if(nativeCheck!=null){nativeCheck.changed(pos);return;}
        if(largeCheck!=null){if(largeCheck.changed(pos))revision++;return;}
        var data=snapshots.get(ChunkPos.asLong(pos.getX()>>4,pos.getZ()>>4));
        if(data==null)return;
        var section=data.get(pos.getY()>>4);
        if(section==null){
            section=new PalettedContainer<>(Block.BLOCK_STATE_REGISTRY,Blocks.AIR.defaultBlockState(),PalettedContainer.Strategy.SECTION_STATES);
            data.put(pos.getY()>>4,section);
        }
        section.set(pos.getX()&15,pos.getY()&15,pos.getZ()&15,state);revision++;
    }
    int check(long deadline){
        if(nativeCheck!=null){if(nativeCheck.dirty())return -1;nativeCheck.deadline(deadline);}
        if(largeCheck!=null){if(largeCheck.dirty())return -1;largeCheck.deadline(deadline);}
        if(!controller.getPatternLock().tryLock())return 0;
        long before=revision;
        if(!streaming()){retainedPositions.clear();cleanroomReceivers.clear();}
        CURRENT.set(this);
        try{
            if(!controller.checkPattern())return -1;
            if(revision!=before)return 0;
            Set<ICleanroomReceiver> receivers=controller.getMultiblockState().getMatchContext().getOrDefault("cleanroomReceiver",Set.of());
            for(var entry:cleanroomReceivers.long2ObjectEntrySet())if(receivers.contains(entry.getValue()))retainedPositions.add(entry.getLongKey());
            controller.setFlipped(controller.getMultiblockState().isNeededFlip());
            forming=true;
            controller.onStructureFormed();
            if(!controller.isFormed())return -1;
            Hk3WorkingChunks.collect(controller,pos->retainedPositions.add(pos.asLong()));
            if(revision!=before){rollbackFormation();return 0;}
            return 1;
        }catch(Pending pending){
            if(controller.isFormed())rollbackFormation();
            return 0;
        }finally{forming=false;rollingBack=false;CURRENT.remove();controller.getPatternLock().unlock();}
    }
    private void rollbackFormation(){
        rollingBack=true;
        controller.onStructureInvalid();
    }
    Hk3InterfaceChunks retainUsed(){
        var required=new LongOpenHashSet();
        required.add(ChunkPos.asLong(controller.getPos().getX()>>4,controller.getPos().getZ()>>4));
        for(long packed:retainedPositions){
            var pos=BlockPos.of(packed);candidates.retain(pos);
            required.add(ChunkPos.asLong(pos.getX()>>4,pos.getZ()>>4));
        }
        for(var part:controller.getParts()){
            var pos=part.self().getPos();candidates.retain(pos);
            required.add(ChunkPos.asLong(pos.getX()>>4,pos.getZ()>>4));
        }
        candidates.keepOnly(required);transferred=true;return candidates;
    }
    @Override public void close(){window.close();if(!transferred)candidates.close();snapshots.clear();if(nativeCheck!=null)nativeCheck.close();if(largeCheck!=null)largeCheck.close(transferred);}
}
