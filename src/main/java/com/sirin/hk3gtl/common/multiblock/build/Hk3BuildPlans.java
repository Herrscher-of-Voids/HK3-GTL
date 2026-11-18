package com.sirin.hk3gtl.common.multiblock.build;

import com.google.gson.JsonParser;
import com.sirin.hk3gtl.common.util.Hk3PackedResources;
import com.gregtechceu.gtceu.api.machine.feature.multiblock.IMultiController;
import com.lowdragmc.lowdraglib.utils.BlockInfo;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3ApprovedArchitecture;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3StructureStream;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LargeArchitectureShapes;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LiquidLineLayout;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LiquidLinePatterns;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3W01HallLayout;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3W01HallPattern;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3StructureBlocks;
import it.unimi.dsi.fastutil.ints.Int2ObjectOpenHashMap;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.NbtIo;
import net.minecraft.nbt.Tag;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.Property;

import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.BitSet;
import java.util.HashMap;
import java.util.Map;

public final class Hk3BuildPlans {
    /** 2026-11-11：工业依赖审计复用正式控制器身份，不从机号推测布局。 */
    public static String layoutForMachine(String machine) { return Keys.BY_MACHINE.get(machine); }
    private static final String ROOT = "/data/hk3gtl/structures/";
    private Hk3BuildPlans() {}

    public static boolean captureFarView(IMultiController controller) {
        return !(controller instanceof com.sirin.hk3gtl.common.machine.w03.Hk3W03Machine);
    }

    public static Hk3BuildPlan create(IMultiController controller) {
        if (!"hk3gtl".equals(controller.self().getDefinition().getId().getNamespace()))
            throw new IllegalArgumentException("统一蓝图入口只处理HK3GTL控制器");
        if (controller.getPattern() instanceof Hk3W01HallPattern pattern) return new HallPlan(pattern);
        if (controller instanceof com.sirin.hk3gtl.common.machine.w02.Hk3W02Machine) {
            InputStream input=Hk3BuildPlans.class.getResourceAsStream(ROOT+"w02_19c_a2.bin.gz");
            if(input==null)throw new IllegalStateException("缺少W02 A2完整搭建资源");
            PackedPlan plan=new PackedPlan(input,controller.self().getBlockState().getBlock());
            plan.creativeOnly=false;
            return plan;
        }
        if (controller instanceof com.sirin.hk3gtl.common.machine.w03.Hk3W03Machine) {
            InputStream input=Hk3BuildPlans.class.getResourceAsStream(ROOT+"w03_c9.bin.gz");
            if(input==null)throw new IllegalStateException("缺少W03 C9完整搭建资源");
            PackedPlan plan=new PackedPlan(input,controller.self().getBlockState().getBlock());
            plan.creativeOnly=false;plan.captureFarView=captureFarView(controller);
            return plan;
        }
        if (controller instanceof com.sirin.hk3gtl.common.machine.wonder.Hk3WonderMachine wonder) {
            if(!com.sirin.hk3gtl.common.machine.wonder.Hk3WonderCatalog.hasBlueprint(wonder.researchRole()))
                throw new IllegalStateException(wonder.researchRole()+"完整蓝图尚未完成，不能搭建或成型");
            InputStream input=Hk3PackedResources.resource(Hk3BuildPlans.class,ROOT+wonder.researchRole().toLowerCase(java.util.Locale.ROOT)+"_candidate.bin.gz");
            if(wonder.researchRole().equals("W11"))return new Hk3W11BuildPlan(input,controller.self().getBlockState().getBlock());
            return new PackedPlan(input,controller.self().getBlockState().getBlock());
        }
        if (controller instanceof com.sirin.hk3gtl.common.machine.hyperion.Hk3HyperionMachine) {
            InputStream input = Hk3BuildPlans.class.getResourceAsStream(ROOT + "hyperion_construction.bin.gz");
            if (input == null) throw new IllegalStateException("缺少1145格休伯利安原稿搭建资源");
            PackedPlan plan = new PackedPlan(input, controller.self().getBlockState().getBlock());
            plan.creativeOnly = false;
            plan.dataVersion = 3120;
            return plan;
        }
        String machine = controller.self().getDefinition().getId().toString();
        if (machine.equals("hk3gtl:ae_nexus"))
            return fromNbt(com.sirin.hk3gtl.common.machine.ae.Hk3NexusStructure.template(),
                    controller.self().getBlockState().getBlock());
        String id = Keys.BY_MACHINE.get(machine);
        if (id != null) {
            SparsePlan plan;
            InputStream packed = Hk3StructureStream.open(id);
            if (packed != null) plan = new PackedPlan(packed, controller.self().getBlockState().getBlock());
            else try (InputStream input = Hk3BuildPlans.class.getResourceAsStream(ROOT + "approved/" + id + ".nbt")) {
                if (input == null) throw new IllegalStateException("缺少批准建造模板：" + id);
                plan = fromNbt(NbtIo.readCompressed(input), controller.self().getBlockState().getBlock());
            } catch (IOException failure) { throw new IllegalStateException("读取批准建造模板失败：" + id, failure); }
            return plan;
        }
        if (!machine.equals("hk3gtl:honkai_network_injector"))
            throw new IllegalStateException("控制器缺少正式建造蓝图：" + machine);
        return fromPreview(Hk3LiquidLinePatterns.shape((com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition)
                controller.self().getDefinition(),Hk3LiquidLineLayout.Kind.INJECTION).getBlocks(),
                controller.self().getBlockState().getBlock());
    }

    private static final class Keys {
        static final Map<String, String> BY_MACHINE = load();
        private static Map<String, String> load() {
            Map<String, String> result = new HashMap<>();
            for (String key : Hk3ApprovedArchitecture.IDS) {
                try (InputStream stream = Hk3BuildPlans.class.getResourceAsStream("/data/hk3gtl/compact_architecture/" + key + ".json")) {
                    if (stream == null) throw new IOException("缺少批准身份：" + key);
                    var metadata = JsonParser.parseReader(new InputStreamReader(stream, StandardCharsets.UTF_8)).getAsJsonObject();
                    String previous = result.put(metadata.get("machine").getAsString(), key);
                    if (previous != null) throw new IOException("批准控制器身份重复：" + key);
                } catch (IOException | RuntimeException failure) {
                    throw new IllegalStateException("读取批准控制器身份失败：" + key, failure);
                }
            }
            return Map.copyOf(result);
        }

    }

    private static final class HallPlan implements Hk3BuildPlan {
        private final Hk3W01HallPattern pattern;
        private final Hk3W01HallLayout data = Hk3W01HallPattern.layout();
        HallPlan(Hk3W01HallPattern pattern) { this.pattern = pattern; }
        @Override public int size() { return data.cells().length; }
        @Override public int height() { return data.height(); }
        @Override public int x(int i) { return Hk3W01HallLayout.x(data.cells()[i]) - data.controllerX(); }
        @Override public int y(int i) { return Hk3W01HallLayout.y(data.cells()[i]) - data.controllerY(); }
        @Override public int z(int i) { return Hk3W01HallLayout.z(data.cells()[i]) - data.controllerZ(); }
        @Override public BlockState state(int i) { return pattern.expectedState(data.cells()[i], 0); }
        @Override public CompoundTag tag(int i) { return null; }
        @Override public Direction sourceFacing() { return Direction.WEST; }
        @Override public boolean contains(int x,int y,int z) {
            int a=x+data.controllerX(),b=y+data.controllerY(),c=z+data.controllerZ();
            if(a<0||a>=data.width()||b<0||b>=data.height()||c<0||c>=data.depth())return false;
            long coordinate=Hk3W01HallLayout.pack(a,b,c,0);
            int at=Arrays.binarySearch(data.cells(),coordinate);at=at>=0?at:-at-1;
            return at<data.cells().length&&(data.cells()[at]>>>16)==(coordinate>>>16);
        }
        @Override public BlockPos minOffset() { return new BlockPos(-data.controllerX(), -data.controllerY(), -data.controllerZ()); }
        @Override public BlockPos maxOffset() { return new BlockPos(data.width()-1-data.controllerX(), data.height()-1-data.controllerY(), data.depth()-1-data.controllerZ()); }
    }

    private static class SparsePlan implements Hk3BuildPlan {
        boolean captureFarView=true;
        @Override public boolean captureFarView(){return captureFarView;}
        @Override public boolean contains(int x,int y,int z){
            int a=x+cx,b=y+cy,c=z+cz;
            return a>=0&&a<width&&b>=0&&b<height&&c>=0&&c<depth&&Arrays.binarySearch(positions,linear(a,b,c))>=0;
        }
        final int width, height, depth, cx, cy, cz;
        final int[] positions;
        final short[] materials;
        final BlockState[] palette;
        final Int2ObjectOpenHashMap<CompoundTag> tags = new Int2ObjectOpenHashMap<>();
        Direction sourceFacing = Direction.NORTH;
        boolean creativeOnly;
        int dataVersion = net.minecraft.SharedConstants.getCurrentVersion().getDataVersion().getVersion();
        @Override public boolean creativeOnly() { return creativeOnly; }
        @Override public int sourceDataVersion() { return dataVersion; }
        SparsePlan(int width, int height, int depth, int cx, int cy, int cz, int count, BlockState[] palette) {
            Math.multiplyExact(Math.multiplyExact(width, height), depth);
            if (width < 1 || height < 1 || depth < 1 || count < 1 || count > (long) width*height*depth
                    || cx < 0 || cy < 0 || cz < 0 || cx >= width || cy >= height || cz >= depth
                    || palette.length < 1 || palette.length > 65536) throw new IllegalArgumentException("建造蓝图尺寸、调色板或主控越界");
            this.width = width; this.height = height; this.depth = depth;
            this.cx = cx; this.cy = cy; this.cz = cz; this.palette = palette;
            positions = new int[count]; materials = new short[count];
        }
        @Override public int size() { return positions.length; }
        @Override public int height() { return height; }
        @Override public int x(int i) { return positions[i] / depth / height - cx; }
        @Override public int y(int i) { return positions[i] / depth % height - cy; }
        @Override public int z(int i) { return positions[i] % depth - cz; }
        @Override public BlockState state(int i) { return palette[Short.toUnsignedInt(materials[i])]; }
        @Override public CompoundTag tag(int i) { return tags.get(i); }
        @Override public Direction sourceFacing() { return sourceFacing; }
        @Override public BlockPos minOffset() { return new BlockPos(-cx, -cy, -cz); }
        @Override public BlockPos maxOffset() { return new BlockPos(width-1-cx, height-1-cy, depth-1-cz); }
        int linear(int x, int y, int z) { return (x * height + y) * depth + z; }
        void put(int index, int linear, int material, CompoundTag tag) {
            if (linear < 0 || linear >= (long) width*height*depth || material < 0 || material >= palette.length
                    || palette[material].isAir()) throw new IllegalStateException("建造蓝图实体坐标或材料错误");
            positions[index] = linear; materials[index] = (short) material;
            if (tag != null) tags.put(index, tag);
        }
    }

    /** 逐记录解码百万实体；取消/失败时close释放流与临时去重位图。 */
    private static final class PackedPlan extends SparsePlan {
        private Hk3StructureStream input;
        private BitSet occupied;
        private final net.minecraft.world.level.block.Block controller;
        private int cursor;
        private boolean foundController;
        PackedPlan(InputStream compressed, net.minecraft.world.level.block.Block controller) {
            this(open(compressed,controller), controller);
        }
        private PackedPlan(Header header, net.minecraft.world.level.block.Block controller) {
            super(header.width, header.height, header.depth, header.cx, header.cy, header.cz, header.count, header.palette);
            this.input = header.input; this.controller = controller;
            sourceFacing = header.sourceFacing;
            occupied = new BitSet(Math.multiplyExact(Math.multiplyExact(width,height),depth));
        }
        @Override public boolean prepareStep() {
            if (input == null) return true;
            try {
                var cell=input.next();int linear=cell.linear(),material=cell.state();
                if(occupied.get(linear))throw new IOException("巨构建造记录重复");
                CompoundTag tag=Hk3LargeArchitectureShapes.entity(cell.entity());
                put(cursor, linear, material, tag); occupied.set(linear);
                if (palette[material].getBlock() == controller && linear != linear(cx,cy,cz))
                    throw new IOException("巨构建造模板含重复主控");
                if (linear == linear(cx,cy,cz)) {
                    if (palette[material].getBlock() != controller) throw new IOException("巨构建造主控与定义不符");
                    if (facing(palette[material]) != sourceFacing) throw new IOException("巨构建造主控源朝向不一致");
                    foundController = true;
                }
                if (++cursor != size()) return false;
                input.finish();
                if (!foundController)
                    throw new IOException("巨构建造主控缺格，或包含尾随记录");
                close(); return true;
            } catch (IOException | RuntimeException failure) {
                close(); throw new IllegalStateException("读取巨构建造记录失败", failure);
            }
        }
        @Override public void close() {
            if (input != null) try { input.close(); } catch (IOException ignored) {} finally { input = null; }
            occupied = null;
        }
        private record Header(Hk3StructureStream input, int width, int height, int depth, int cx, int cy, int cz,
                              int count, BlockState[] palette, Direction sourceFacing) {}
        private static Header open(InputStream compressed, net.minecraft.world.level.block.Block controller) {
            Hk3StructureStream input=null;
            try {
                input=new Hk3StructureStream(compressed);var h=input.header();
                BlockState[] palette=h.palette().stream().map(Hk3BuildPlans::state).toArray(BlockState[]::new);
                return new Header(input,h.width(),h.height(),h.depth(),h.cx(),h.cy(),h.cz(),h.count(),palette,controllerFacing(palette,controller));
            }catch(IOException|RuntimeException failure) {
                try{if(input!=null)input.close();else compressed.close();}catch(IOException ignored){}
                throw new IllegalStateException("读取巨构建造头失败",failure);
            }
        }
    }

    private static SparsePlan fromNbt(CompoundTag template, net.minecraft.world.level.block.Block controller) {
        var size=template.getList("size",Tag.TAG_INT);
        var paletteTag=template.getList("palette",Tag.TAG_COMPOUND);
        if (size.size()!=3 || paletteTag.isEmpty()) throw new IllegalStateException("批准建造NBT头错误");
        BlockState[] palette=new BlockState[paletteTag.size()];
        for (int i=0;i<palette.length;i++) {
            CompoundTag entry=paletteTag.getCompound(i);
            String text=entry.getString("Name");
            if (entry.contains("Properties",Tag.TAG_COMPOUND)) {
                var properties=entry.getCompound("Properties");
                text += "[" + properties.getAllKeys().stream().sorted().map(k -> k+"="+properties.getString(k))
                        .collect(java.util.stream.Collectors.joining(",")) + "]";
            }
            palette[i]=state(text);
        }
        var blocks=template.getList("blocks",Tag.TAG_COMPOUND);
        int cx=-1,cy=-1,cz=-1;
        for (Tag raw:blocks) {
            var block=(CompoundTag)raw;
            int material=block.getInt("state");
            if (material<0 || material>=palette.length) throw new IllegalStateException("批准建造NBT材料越界");
            if (palette[material].getBlock()!=controller) continue;
            if (cx>=0) throw new IllegalStateException("批准建造NBT含重复主控");
            var pos=block.getList("pos",Tag.TAG_INT);
            if(pos.size()!=3)throw new IllegalStateException("批准建造NBT坐标错误");
            cx=pos.getInt(0);cy=pos.getInt(1);cz=pos.getInt(2);
        }
        SparsePlan result=new SparsePlan(size.getInt(0),size.getInt(1),size.getInt(2),cx,cy,cz,blocks.size(),palette);
        BitSet occupied=new BitSet(Math.multiplyExact(Math.multiplyExact(result.width,result.height),result.depth));
        int i=0;
        for(Tag raw:blocks) {
            var block=(CompoundTag)raw;var pos=block.getList("pos",Tag.TAG_INT);
            if(pos.size()!=3 || !block.contains("state",Tag.TAG_INT))throw new IllegalStateException("批准建造NBT坐标缺失");
            int x=pos.getInt(0),y=pos.getInt(1),z=pos.getInt(2),material=block.getInt("state");
            if(x<0||x>=result.width||y<0||y>=result.height||z<0||z>=result.depth)throw new IllegalStateException("批准建造NBT坐标越界");
            int linear=result.linear(x,y,z);
            if(occupied.get(linear))throw new IllegalStateException("批准建造NBT坐标重复");
            occupied.set(linear);result.put(i++,linear,material,block.contains("nbt",Tag.TAG_COMPOUND)?block.getCompound("nbt"):null);
            if(x==cx&&y==cy&&z==cz)result.sourceFacing=facing(palette[material]);
        }
        return result;
    }

    /** 仅用于没有批准外观模板的现有小机器；禁止巨构走此空气数组路径。 */
    private static SparsePlan fromPreview(BlockInfo[][][] preview, net.minecraft.world.level.block.Block controller) {
        if(preview.length==0||preview[0].length==0||preview[0][0].length==0)throw new IllegalStateException("机器建造预览为空");
        int width=preview.length,height=preview[0].length,depth=preview[0][0].length,count=0,cx=-1,cy=-1,cz=-1;
        Map<BlockState,Integer> materials=new java.util.LinkedHashMap<>();
        for(int x=0;x<width;x++)for(int y=0;y<height;y++)for(int z=0;z<depth;z++) {
            BlockInfo info=preview[x][y][z];
            if(info==null||info.getBlockState().isAir())continue;
            count++;materials.computeIfAbsent(info.getBlockState(),s -> materials.size());
            if(info.getBlockState().getBlock()==controller) {
                if(cx>=0)throw new IllegalStateException("机器建造预览含重复主控");
                cx=x;cy=y;cz=z;
            }
        }
        SparsePlan result=new SparsePlan(width,height,depth,cx,cy,cz,count,materials.keySet().toArray(BlockState[]::new));
        int i=0;
        for(int x=0;x<width;x++)for(int y=0;y<height;y++)for(int z=0;z<depth;z++) {
            BlockInfo info=preview[x][y][z];
            if(info==null||info.getBlockState().isAir())continue;
            var entity=info.hasBlockEntity()?info.getBlockEntity(BlockPos.ZERO):null;
            result.put(i++,result.linear(x,y,z),materials.get(info.getBlockState()),entity==null?null:entity.saveWithFullMetadata());
            if(x==cx&&y==cy&&z==cz)result.sourceFacing=facing(info.getBlockState());
            info.clearBlockEntityCache();
        }
        return result;
    }

    private static Direction facing(BlockState state) {
        Property<?> property=state.getBlock().getStateDefinition().getProperty("facing");
        if(property==null)throw new IllegalStateException("建造模板主控缺少朝向");
        Direction facing=Direction.byName(state.getValue(property).toString());
        if(facing==null||facing.getAxis().isVertical())throw new IllegalStateException("建造模板主控必须水平朝向");
        return facing;
    }
    static Direction controllerFacing(BlockState[] palette, net.minecraft.world.level.block.Block controller) {
        Direction result = null;
        for (BlockState state : palette) if (state.getBlock() == controller) {
            Direction next = facing(state);
            if (result != null && result != next) throw new IllegalStateException("建造模板主控源朝向存在歧义");
            result = next;
        }
        if (result == null) throw new IllegalStateException("建造模板调色板缺少主控");
        return result;
    }
    private static BlockState state(String text) {
        int start=text.indexOf('[');
        BlockState state=Hk3StructureBlocks.require(start<0?text:text.substring(0,start)).defaultBlockState();
        if(start>=0)for(String entry:text.substring(start+1,text.length()-1).split(",")) {
            String[] pair=entry.split("=",2);
            Property<?> property=pair.length==2?state.getBlock().getStateDefinition().getProperty(pair[0]):null;
            if(property==null)throw new IllegalStateException("建造模板属性错误："+text);
            state=property(state,property,pair[1]);
        }
        return state;
    }
    private static <T extends Comparable<T>> BlockState property(BlockState state,Property<T> property,String value) {
        return state.setValue(property,property.getValue(value).orElseThrow(()->new IllegalStateException("建造模板属性值错误："+value)));
    }
}
