package com.sirin.hk3gtl.common.multiblock.loading;

import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.machine.feature.multiblock.IMultiController;
import com.gregtechceu.gtceu.api.pattern.MultiblockState;
import com.gregtechceu.gtceu.api.pattern.Predicates;
import com.gregtechceu.gtceu.api.pattern.TraceabilityPredicate;
import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.sirin.hk3gtl.common.farview.Hk3FarViewData;
import com.sirin.hk3gtl.common.multiblock.build.Hk3BuildPlans;
import com.sirin.hk3gtl.common.multiblock.build.Hk3UniversalTerminalBuilder;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3InterfacePredicates;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LargeArchitectureShapes;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3NativeWonderPattern;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3WonderPatternSource;
import it.unimi.dsi.fastutil.longs.Long2ObjectOpenHashMap;
import it.unimi.dsi.fastutil.longs.LongOpenHashSet;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.DaylightDetectorBlock;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import org.gtlcore.gtlcore.api.pattern.FixedPatternLayout;
import org.gtlcore.gtlcore.api.pattern.PatternMatchLayout;

import java.util.Arrays;
import java.util.concurrent.ConcurrentHashMap;

public final class Hk3NativeWonderCheck implements AutoCloseable {
    public static final String POSITIONS="hk3gtlNativeWonderPositions";
    public static final String CHECK="hk3gtlNativeWonderCheck";
    private static final int BATCH=512;
    private static final ConcurrentHashMap<String,Hk3WonderPatternSource.Header> HEADERS=new ConcurrentHashMap<>();
    private final Hk3PatternLoading loading;
    private final Hk3WonderPatternSource source;
    private final Hk3WonderPatternSource.Header header;
    private final TraceabilityPredicate[] materials;
    private final TraceabilityPredicate controller;
    private final Rotation rotation;
    private final boolean captureFarView;
    private final Hk3WonderPositionSet positions,active;
    private final LongOpenHashSet chunks=new LongOpenHashSet();
    private Hk3WonderPatternSource.Cell next;
    private PatternMatchLayout.Slice slice;
    private int sourceX;
    private long chunk,deadline;
    private boolean started,dirty,inMatcher;

    Hk3NativeWonderCheck(Hk3PatternLoading loading,Hk3NativeWonderPattern pattern){
        this.loading=loading;source=Hk3WonderPatternSource.open(pattern.role());header=source.header();
        var machine=loading.controller;
        captureFarView=Hk3BuildPlans.captureFarView(machine);
        rotation=Hk3UniversalTerminalBuilder.rotation(header.facing(),machine.getFrontFacing());
        var inverse=Hk3UniversalTerminalBuilder.rotation(machine.getFrontFacing(),header.facing());
        positions=new Hk3WonderPositionSet(header,machine.getPos(),rotation,inverse);
        active=new Hk3WonderPositionSet(header,machine.getPos(),rotation,inverse);
        var ports=Hk3InterfacePredicates.interfaces();
        materials=header.palette().stream().map(Hk3LargeArchitectureShapes::state).map(state->state.rotate(rotation))
                .map(Hk3NativeWonderCheck::states).map(predicate->predicate.or(ports)).toArray(TraceabilityPredicate[]::new);
        controller=Predicates.controller(Predicates.blocks(machine.getDefinition().getBlock()));
        next=source.next();
    }
    public static Hk3NativeWonderCheck current(){return Hk3PatternLoading.currentNative();}
    void deadline(long value){deadline=value;}
    boolean dirty(){return dirty;}
    public boolean started(){return started;}
    public void initialize(MultiblockState state){
        started=true;state.getMatchContext().set(POSITIONS,positions);state.getMatchContext().set(CHECK,this);
        state.getMatchContext().set("vaBlocks",active);
        state.getMatchContext().set("ioMap",new Long2ObjectOpenHashMap<IO>(){
            @Override public IO put(long pos,IO io){return io==IO.BOTH?null:super.put(pos,io);}
        });
    }
    public void cache(BlockPos pos,MultiblockState state){
        positions.add(pos.asLong());chunks.add(ChunkPos.asLong(pos.getX()>>4,pos.getZ()>>4));
        if(captureFarView){
            var actual=state.getBlockState();
            if(actual.isAir())Hk3FarViewData.changed(loading.level,pos,actual);
            else Hk3FarViewData.observe(loading.level,pos,actual);
        }
    }
    public java.util.Collection<BlockPos> chunkRepresentatives(){
        return chunks.longStream().mapToObj(key->new BlockPos(ChunkPos.getX(key)<<4,loading.controller.getPos().getY(),ChunkPos.getZ(key)<<4)).toList();
    }
    void changed(BlockPos pos){if(positions.contains(pos))dirty=true;}
    void missingChunk(){if(inMatcher)dirty=true;}
    public PatternMatchLayout.Slice slice(){return slice;}
    public BlockPos position(int x,int y,int z){
        return new BlockPos(sourceX,y,x).rotate(rotation).offset(loading.controller.getPos());
    }
    public boolean match(int[] repetitions,int start,FixedPatternLayout.SliceMatcher matcher,Operation<Boolean> original){
        while(next!=null||slice!=null){
            if(System.nanoTime()>=deadline)throw Hk3PatternLoading.PENDING;
            if(slice==null)prepareSlice();
            if(!loading.nativeChunkReady(chunk))throw Hk3PatternLoading.PENDING;
            inMatcher=true;
            boolean matched;
            try {matched=original.call(repetitions,start,matcher);}finally{inMatcher=false;}
            if(!matched)return false;
            slice=null;
        }
        return true;
    }
    private void prepareSlice(){
        int[] xs=new int[BATCH],ys=new int[BATCH];
        TraceabilityPredicate[] predicates=new TraceabilityPredicate[BATCH];
        sourceX=next.x()-header.cx();
        var first=new BlockPos(sourceX,next.y()-header.cy(),next.z()-header.cz()).rotate(rotation).offset(loading.controller.getPos());
        chunk=ChunkPos.asLong(first.getX()>>4,first.getZ()>>4);
        int count=0;
        do {
            int y=next.y()-header.cy(),z=next.z()-header.cz();
            var pos=new BlockPos(next.x()-header.cx(),y,z).rotate(rotation).offset(loading.controller.getPos());
            if(next.x()-header.cx()!=sourceX||ChunkPos.asLong(pos.getX()>>4,pos.getZ()>>4)!=chunk)break;
            xs[count]=z;ys[count]=y;
            predicates[count++]=next.x()==header.cx()&&next.y()==header.cy()&&next.z()==header.cz()?controller:materials[next.material()];
            next=source.hasNext()?source.next():null;
        }while(next!=null&&count<BATCH);
        slice=new PatternMatchLayout.Slice(Arrays.copyOf(xs,count),Arrays.copyOf(ys,count),Arrays.copyOf(predicates,count),false);
    }
    private static TraceabilityPredicate states(BlockState state){
        if(state.getBlock() instanceof DaylightDetectorBlock){
            BlockState[] levels=new BlockState[16];
            for(int i=0;i<levels.length;i++)levels[i]=state.setValue(DaylightDetectorBlock.POWER,i);
            return Predicates.states(levels);
        }
        return Predicates.states(state);
    }
    public static BoundingBox bounds(IMultiController controller,Hk3NativeWonderPattern pattern){
        var h=HEADERS.computeIfAbsent(pattern.role(),role->{
            try(var source=Hk3WonderPatternSource.open(role)){return source.header();}
        });
        var rotation=Hk3UniversalTerminalBuilder.rotation(h.facing(),controller.self().getFrontFacing());
        var a=new BlockPos(-h.cx(),-h.cy(),-h.cz()).rotate(rotation).offset(controller.self().getPos());
        var b=new BlockPos(h.width()-1-h.cx(),h.height()-1-h.cy(),h.depth()-1-h.cz()).rotate(rotation).offset(controller.self().getPos());
        return new BoundingBox(Math.min(a.getX(),b.getX()),a.getY(),Math.min(a.getZ(),b.getZ()),Math.max(a.getX(),b.getX()),b.getY(),Math.max(a.getZ(),b.getZ()));
    }
    @Override public void close(){source.close();}
}
