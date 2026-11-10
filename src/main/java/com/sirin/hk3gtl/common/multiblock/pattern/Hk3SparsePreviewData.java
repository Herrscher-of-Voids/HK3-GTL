package com.sirin.hk3gtl.common.multiblock.pattern;

import com.google.gson.JsonParser;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** 自家预览直接读取正式实体源；JEI注册只读身份，打开页面后才准备完整蓝图。 */
public final class Hk3SparsePreviewData {
    public record Data(Hk3W01HallLayout layout,Map<Long,CompoundTag> entities,Direction front) {}
    private record Source(String key,Direction front) {}
    private static final Map<String,Source> SOURCES=sources();
    private Hk3SparsePreviewData() {}
    public static boolean supported(String id) { return SOURCES.containsKey(id); }
    public static Set<String> machines() { return SOURCES.keySet(); }
    private static Map<String,Source> sources() {
        Map<String,Source> sources=new HashMap<>();
        sources.put("hk3gtl:w01_origin_stellar_concert_court",new Source("w01",Direction.WEST));
        sources.put("hk3gtl:omnia_autonomous_industrial_matrix",new Source("w02_19c_a2",Direction.SOUTH));
        sources.put("hk3gtl:void_anchor_ring",new Source("w03_c9",Direction.NORTH));
        sources.put("hk3gtl:hyperion_flagship",new Source("hyperion_construction",Direction.EAST));
        for(String key:Hk3ApprovedArchitecture.IDS) {
            try(var stream=Hk3SparsePreviewData.class.getResourceAsStream("/data/hk3gtl/compact_architecture/"+key+".json")) {
                if(stream==null)throw new IOException("缺少预览身份："+key);
                var json=JsonParser.parseReader(new InputStreamReader(stream,StandardCharsets.UTF_8)).getAsJsonObject();
                String machine=json.get("machine").getAsString();
                if(sources.putIfAbsent(machine,new Source(key,Direction.NORTH))!=null)throw new IOException("预览主控身份重复："+machine);
            }catch(IOException failure) { throw new IllegalStateException("自家预览身份读取失败",failure); }
        }
        return Map.copyOf(sources);
    }
    public static Data load(String id) {
        var source=SOURCES.get(id);
        if(source==null)throw new IllegalArgumentException("没有正式预览源："+id);
        if(source.key.equals("w01"))return new Data(Hk3W01HallPattern.layout(),Map.of(),source.front);
        InputStream stream=Hk3ApprovedArchitecture.IDS.contains(source.key)?Hk3StructureStream.open(source.key)
                :Hk3SparsePreviewData.class.getResourceAsStream("/data/hk3gtl/structures/"+source.key+".bin.gz");
        if(stream==null)throw new IllegalStateException("缺少完整预览源："+source.key);
        class Read {
            Hk3LargeArchitectureShapes.Header header;
            long[] cells;
            int next;
            final Map<Long,CompoundTag> entities=new HashMap<>();
        }
        Read data=new Read();
        try(stream) {
            Hk3LargeArchitectureShapes.read(stream,h->{
                if(h.width()>4096||h.height()>4096||h.depth()>4096)throw new IllegalArgumentException("完整预览坐标超过十二位编码");
                data.header=h;data.cells=new long[h.count()];
            },(linear,state,entity)->{
                if((data.next&4095)==0 && Thread.currentThread().isInterrupted())throw new java.util.concurrent.CancellationException("预览读取已取消");
                var h=data.header;
                long cell=Hk3W01HallLayout.pack(linear/h.depth()/h.height(),linear/h.depth()%h.height(),linear%h.depth(),state);
                data.cells[data.next++]=cell;
                if(entity!=null)data.entities.put(cell>>>16,entity);
            });
        }catch(IOException failure) { throw new IllegalStateException("完整稀疏预览读取失败："+source.key,failure); }
        Arrays.sort(data.cells);var h=data.header;
        return new Data(new Hk3W01HallLayout(h.width(),h.height(),h.depth(),h.controllerX(),h.controllerY(),h.controllerZ(),h.palette(),data.cells),
                Map.copyOf(data.entities),source.front);
    }

    /** 没有独立资源的小型机器仍使用自家场景，读取其真实形状而非主控占位。 */
    public static Data load(com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition definition) {
        String id=definition.getId().toString();
        if(supported(id))return load(id);
        var shapes=definition.getMatchingShapes();
        if(shapes.isEmpty())throw new IllegalStateException("机器缺少完整预览形状："+id);
        var blocks=shapes.get(0).getBlocks();
        int w=blocks.length,h=blocks[0].length,d=blocks[0][0].length,cx=-1,cy=-1,cz=-1;
        Map<String,Integer> palette=new LinkedHashMap<>();java.util.ArrayList<Long> cells=new java.util.ArrayList<>();
        Map<Long,CompoundTag> entities=new HashMap<>();Direction front=Direction.NORTH;
        for(int x=0;x<w;x++)for(int y=0;y<h;y++)for(int z=0;z<d;z++) {
            var info=blocks[x][y][z];if(info==null||info.getBlockState().isAir())continue;
            var state=info.getBlockState();
            String text=net.minecraft.core.registries.BuiltInRegistries.BLOCK.getKey(state.getBlock()).toString();
            if(!state.getValues().isEmpty())text+="["+state.getValues().entrySet().stream()
                    .map(entry->entry.getKey().getName()+"="+propertyValue(entry.getKey(),entry.getValue())).sorted().collect(java.util.stream.Collectors.joining(","))+"]";
            int material=palette.computeIfAbsent(text,key->palette.size());long cell=Hk3W01HallLayout.pack(x,y,z,material);cells.add(cell);
            if(state.getBlock()==definition.getBlock()) {
                if(cx>=0)throw new IllegalStateException("预览含重复主控："+id);
                cx=x;cy=y;cz=z;var face=state.getBlock().getStateDefinition().getProperty("facing");
                if(face!=null)front=Direction.byName(state.getValue(face).toString());
            }
            if(info.hasBlockEntity()) {
                var entity=info.getBlockEntity(new net.minecraft.core.BlockPos(x,y,z));
                if(entity!=null)entities.put(cell>>>16,entity.saveWithFullMetadata());
                info.clearBlockEntityCache();
            }
        }
        if(cx<0)throw new IllegalStateException("预览缺少真实主控："+id);
        return new Data(new Hk3W01HallLayout(w,h,d,cx,cy,cz,List.copyOf(palette.keySet()),cells.stream().mapToLong(Long::longValue).toArray()),
                Map.copyOf(entities),java.util.Objects.requireNonNull(front));
    }
    @SuppressWarnings("unchecked") private static <T extends Comparable<T>> String propertyValue(
            net.minecraft.world.level.block.state.properties.Property<T> property,Comparable<?> value) {
        return property.getName((T)value);
    }
}
