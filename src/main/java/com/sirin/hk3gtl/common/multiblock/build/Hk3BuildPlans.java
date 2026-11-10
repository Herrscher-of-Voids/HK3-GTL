package com.sirin.hk3gtl.common.multiblock.build;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.google.gson.stream.JsonReader;
import com.gregtechceu.gtceu.api.machine.feature.multiblock.IMultiController;
import com.lowdragmc.lowdraglib.utils.BlockInfo;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3ApprovedArchitecture;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3StructureStream;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LargeArchitectureShapes;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3W01HallLayout;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3W01HallPattern;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3StructureBlocks;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LargeStructurePattern;
import com.sirin.hk3gtl.mixin.gtceu.Hk3BuildPatternAccess;
import com.gregtechceu.gtceu.api.pattern.TraceabilityPredicate;
import it.unimi.dsi.fastutil.ints.Int2ObjectOpenHashMap;
import it.unimi.dsi.fastutil.ints.IntOpenHashSet;
import it.unimi.dsi.fastutil.longs.LongOpenHashSet;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.NbtIo;
import net.minecraft.nbt.Tag;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.Property;

import java.io.ByteArrayInputStream;
import java.io.DataInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.BitSet;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.zip.GZIPInputStream;

/**
 * 【文件职责】把现行正式结构转换为统一稀疏建造蓝图，仓室实体数据与主控锚点保持源版本。
 * 【变更记录 #1】2026-10-30 01:22:07（第1次备注 · 内测5修订184）
 * - 删除：无；新增：W01零拷贝、巨构逐记录准备、普通批准NBT及小型GT模式四条适配路径。
 * - 修改：巨构仅读取实体坐标、调色板与少量实体NBT，不调用巨型getPreview或分配空气对象。
 * - 用途：统一建造数据入口；缺失、重复、截断或主控不符直接拒绝，不能回退错误旧建筑。
 * 【变更记录 #2】2026-10-30 02:11:33（第2次备注 · 内测5修订184）
 * - 删除：所有小元数据必有ports及巨构准备前默认朝北的假设。
 * - 新增：按台惰性读取正式接口合同；早期元数据缺接口时流式提取批准源，不展开blocks。
 * - 修改：无仓搭建接口返回合法填充壳且不复制仓室NBT；源朝向从真实主控调色板提前确定。
 * - 用途：防止接口缺字段使全部机器失效，避免赠送真实仓室或在错误朝向放置整座建筑。
 */
public final class Hk3BuildPlans {
    private static final String ROOT = "/data/hk3gtl/structures/";
    private Hk3BuildPlans() {}

    public static Hk3BuildPlan create(IMultiController controller) {
        if (!"hk3gtl".equals(controller.self().getDefinition().getId().getNamespace()))
            throw new IllegalArgumentException("统一蓝图入口只处理HK3GTL控制器");
        if (controller.getPattern() instanceof Hk3W01HallPattern pattern) return new HallPlan(pattern);
        if (controller instanceof com.sirin.hk3gtl.common.machine.w02.Hk3W02Machine) {
            InputStream input=Hk3BuildPlans.class.getResourceAsStream(ROOT+"w02_19c_a2.bin.gz");
            if(input==null)throw new IllegalStateException("缺少W02 A2完整搭建资源");
            PackedPlan plan=new PackedPlan(input,controller.self().getBlockState().getBlock());
            plan.creativeOnly=true;
            for(var pos:com.sirin.hk3gtl.common.machine.w02.Hk3W02Pattern.PORTS)plan.machinePartSlots.add(pos.asLong());
            return plan;
        }
        if (controller instanceof com.sirin.hk3gtl.common.machine.w03.Hk3W03Machine) {
            InputStream input=Hk3BuildPlans.class.getResourceAsStream(ROOT+"w03_c9.bin.gz");
            if(input==null)throw new IllegalStateException("缺少W03 C9完整搭建资源");
            PackedPlan plan=new PackedPlan(input,controller.self().getBlockState().getBlock());
            plan.creativeOnly=true;plan.captureFarView=false;
            for(int x:new int[]{-18,-14,-10,-6,6,10,14,18})plan.machinePartSlots.add(BlockPos.asLong(x,0,0));
            return plan;
        }
        if (controller instanceof com.sirin.hk3gtl.common.machine.hyperion.Hk3HyperionMachine) {
            InputStream input = Hk3BuildPlans.class.getResourceAsStream(ROOT + "hyperion_construction.bin.gz");
            if (input == null) throw new IllegalStateException("缺少1145格休伯利安原稿搭建资源");
            PackedPlan plan = new PackedPlan(input, controller.self().getBlockState().getBlock());
            plan.creativeOnly = true;
            plan.dataVersion = 3120;
            for (int z = -1; z <= 1; z++) {
                plan.machinePartSlots.add(BlockPos.asLong(-2, -1, z));
                plan.machinePartSlots.add(BlockPos.asLong(1, 1, z));
                if (z != 0) plan.machinePartSlots.add(BlockPos.asLong(0, 0, z));
            }
            return plan;
        }
        String machine = controller.self().getDefinition().getId().toString();
        String id = Keys.BY_MACHINE.get(machine);
        if (id != null) {
            SparsePlan plan;
            InputStream packed = Hk3StructureStream.open(id);
            if (packed != null) plan = new PackedPlan(packed, controller.self().getBlockState().getBlock());
            else try (InputStream input = Hk3BuildPlans.class.getResourceAsStream(ROOT + "approved/" + id + ".nbt")) {
                if (input == null) throw new IllegalStateException("缺少批准建造模板：" + id);
                plan = fromNbt(NbtIo.readCompressed(input), controller.self().getBlockState().getBlock());
            } catch (IOException failure) { throw new IllegalStateException("读取批准建造模板失败：" + id, failure); }
            try {
                plan.configure(Keys.PORTS.computeIfAbsent(id, Keys::loadPorts), controller);
                return plan;
            } catch (RuntimeException failure) {
                plan.close();
                throw failure;
            }
        }
        if (!machine.equals("hk3gtl:honkai_network_injector"))
            throw new IllegalStateException("控制器缺少正式建造蓝图：" + machine);
        int[] repetitions = Arrays.stream(controller.getPattern().aisleRepetitions).mapToInt(r -> r[0]).toArray();
        SparsePlan plan = fromPreview(controller.getPattern().getPreview(repetitions), controller.self().getBlockState().getBlock());
        var matches = ((Hk3BuildPatternAccess)(Object)controller.getPattern()).hk3gtl$blockMatches();
        if (matches.length != plan.depth || matches[0].length != plan.height || matches[0][0].length != plan.width)
            throw new IllegalStateException("小型建造模板与正式Pattern尺寸不符");
        for (int i=0; i<plan.size(); i++) {
            int x=plan.x(i)+plan.cx, y=plan.y(i)+plan.cy, z=plan.z(i)+plan.cz;
            var predicate = matches[z][y][x];
            if (!predicate.isAny()) plan.portPredicates.put(plan.positions[i],predicate);
        }
        return plan;
    }

    private static final class Keys {
        static final Map<String, String> BY_MACHINE = load();
        static final Map<String, PortData> PORTS = new ConcurrentHashMap<>();
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

        private static PortData loadPorts(String key) {
            try (InputStream stream = Hk3BuildPlans.class.getResourceAsStream("/data/hk3gtl/compact_architecture/" + key + ".json")) {
                if (stream == null) throw new IOException("缺少接口身份：" + key);
                var metadata = JsonParser.parseReader(new InputStreamReader(stream, StandardCharsets.UTF_8)).getAsJsonObject();
                if (metadata.has("ports")) return ports(metadata, key, "size_xyz");
                // 早期小元数据没有接口；批准源把接口放在几何前，只读取所需字段即关闭。
                try (InputStream source = Hk3BuildPlans.class.getResourceAsStream("/data/hk3gtl/approved_architecture/" + key + ".json")) {
                    if (source == null) throw new IOException("缺少批准接口源：" + key);
                    try (JsonReader reader = new JsonReader(new InputStreamReader(source, StandardCharsets.UTF_8))) {
                        JsonObject selected = new JsonObject();
                        reader.beginObject();
                        while (reader.hasNext()) {
                            String name = reader.nextName();
                            if (name.equals("key") || name.equals("size") || name.equals("controller") || name.equals("ports")) {
                                if (selected.has(name)) throw new IOException("批准接口字段重复：" + name);
                                selected.add(name, JsonParser.parseReader(reader));
                            } else reader.skipValue();
                            if (selected.size() == 4) return ports(selected, key, "size");
                        }
                        throw new IOException("批准接口源缺少必要字段：" + key);
                    }
                }
            } catch (IOException | RuntimeException failure) {
                throw new IllegalStateException("读取批准接口坐标失败：" + key, failure);
            }
        }

        private static PortData ports(JsonObject metadata, String key, String sizeField) throws IOException {
            if (!metadata.has("key") || !key.equals(metadata.get("key").getAsString()))
                throw new IOException("批准接口身份不符：" + key);
            int[] size = triple(metadata, sizeField), center = triple(metadata, "controller");
            for (int axis=0; axis<3; axis++) if (size[axis]<1 || center[axis]<0 || center[axis]>=size[axis])
                throw new IOException("批准接口尺寸或主控越界：" + key);
            var values = metadata.getAsJsonArray("ports");
            if (values == null || values.isEmpty()) throw new IOException("批准接口列表缺失或为空：" + key);
            var result = new java.util.ArrayList<PortSlot>(values.size());
            var ids = new java.util.HashSet<String>();
            var occupied = new LongOpenHashSet();
            for (var raw : values) {
                var port = raw.getAsJsonObject();
                String id = port.get("id").getAsString(), group = port.get("group").getAsString();
                Direction face = Direction.byName(port.get("face").getAsString());
                int[] at = triple(port,"pos");
                if (id.isBlank() || group.isBlank() || !ids.add(id) || face==null || face.getAxis().isVertical())
                    throw new IOException("批准接口身份、分组或方向错误：" + key);
                for (int axis=0; axis<3; axis++) if (at[axis]<0 || at[axis]>=size[axis])
                    throw new IOException("批准接口坐标越界：" + key + "/" + id);
                if (Arrays.equals(at,center) || !occupied.add(BlockPos.asLong(at[0],at[1],at[2])))
                    throw new IOException("批准接口坐标重复或与主控重叠：" + key);
                result.add(new PortSlot(at[0],at[1],at[2],!group.startsWith("energy"),face));
            }
            return new PortData(size,center,List.copyOf(result));
        }

        private static int[] triple(JsonObject value, String field) throws IOException {
            var array = value.getAsJsonArray(field);
            if (array==null || array.size()!=3) throw new IOException("批准接口坐标缺失：" + field);
            return new int[]{array.get(0).getAsInt(),array.get(1).getAsInt(),array.get(2).getAsInt()};
        }
    }

    private record PortSlot(int x, int y, int z, boolean machinePart, Direction face) {}
    private record PortData(int[] size, int[] controller, List<PortSlot> slots) {}

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
        final LongOpenHashSet machinePartSlots = new LongOpenHashSet();
        final IntOpenHashSet filledPorts = new IntOpenHashSet();
        final Map<Integer, TraceabilityPredicate> portPredicates = new HashMap<>();
        final Map<Integer, Direction> portFaces = new HashMap<>();
        BlockState portFiller;
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
        @Override public BlockState state(int i) { return filledPorts.contains(positions[i]) ? portFiller : palette[Short.toUnsignedInt(materials[i])]; }
        @Override public CompoundTag tag(int i) { return filledPorts.contains(positions[i]) ? null : tags.get(i); }
        @Override public Direction sourceFacing() { return sourceFacing; }
        @Override public BlockPos minOffset() { return new BlockPos(-cx, -cy, -cz); }
        @Override public BlockPos maxOffset() { return new BlockPos(width-1-cx, height-1-cy, depth-1-cz); }
        @Override public boolean isMachinePartSlot(int x, int y, int z) { return machinePartSlots.contains(BlockPos.asLong(x,y,z)); }
        @Override public TraceabilityPredicate dismantlePort(int index) { return portPredicates.get(positions[index]); }
        @Override public Direction portFacing(int index) { return portFaces.get(positions[index]); }
        void configure(PortData data, IMultiController controller) {
            if (!Arrays.equals(data.size,new int[]{width,height,depth}) || !Arrays.equals(data.controller,new int[]{cx,cy,cz}))
                throw new IllegalStateException("批准接口合同与真实建造模板坐标不符");
            portFiller = Hk3StructureBlocks.require("hk3gtl:industrial_port_casing").defaultBlockState();
            for (var port : data.slots) {
                int at = linear(port.x,port.y,port.z);
                filledPorts.add(at);
                TraceabilityPredicate predicate;
                if (controller.getPattern() instanceof Hk3LargeStructurePattern large)
                    predicate = large.dismantlePort(port.x-cx,port.y-cy,port.z-cz);
                else {
                    var matches = ((Hk3BuildPatternAccess)(Object)controller.getPattern()).hk3gtl$blockMatches();
                    if (matches.length != depth || matches[port.z].length != height || matches[port.z][port.y].length != width)
                        throw new IllegalStateException("批准接口与固定Pattern尺寸不符");
                    predicate = matches[port.z][port.y][port.x];
                }
                if (predicate == null || predicate.isAny()) throw new IllegalStateException("批准接口缺少真实Pattern谓词");
                portPredicates.put(at,predicate);
                portFaces.put(at,port.face);
                if (port.machinePart) machinePartSlots.add(BlockPos.asLong(port.x-cx,port.y-cy,port.z-cz));
            }
            if (!(this instanceof PackedPlan)) {
                IntOpenHashSet missing = new IntOpenHashSet(filledPorts);
                for (int position : positions) missing.remove(position);
                if (!missing.isEmpty()) throw new IllegalStateException("批准接口在建造模板中缺格");
            }
        }
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
        private int foundPorts;
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
                if (filledPorts.contains(linear)) foundPorts++;
                if (palette[material].getBlock() == controller && linear != linear(cx,cy,cz))
                    throw new IOException("巨构建造模板含重复主控");
                if (linear == linear(cx,cy,cz)) {
                    if (palette[material].getBlock() != controller) throw new IOException("巨构建造主控与定义不符");
                    if (facing(palette[material]) != sourceFacing) throw new IOException("巨构建造主控源朝向不一致");
                    foundController = true;
                }
                if (++cursor != size()) return false;
                input.finish();
                if (!foundController || foundPorts != filledPorts.size())
                    throw new IOException("巨构建造主控或接口缺格，或包含尾随记录");
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
    private static Direction controllerFacing(BlockState[] palette, net.minecraft.world.level.block.Block controller) {
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
