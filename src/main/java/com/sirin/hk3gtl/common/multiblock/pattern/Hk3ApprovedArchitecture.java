package com.sirin.hk3gtl.common.multiblock.pattern;

/** 2026-11-15：I37悬箱稳界试验坞A2接入完整紧凑蓝图，现有正式结构共53形态。 */

import com.sirin.hk3gtl.common.util.Hk3WeightedCache;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.List;











































public final class Hk3ApprovedArchitecture {
    public record Cell(int[] pos, String state) {}
    public record Port(String id, int[] pos, String face, String group, String purpose) {
        public Port { pos = pos == null ? null : pos.clone(); }
        @Override public int[] pos() { return pos == null ? null : pos.clone(); }
    }
    public record Layout(String key, int[] size, int[] controller, List<Cell> blocks, List<Port> ports) {
        public Layout { size = size.clone(); controller = controller.clone(); ports = List.copyOf(ports); }
        @Override public int[] size() { return size.clone(); }
        @Override public int[] controller() { return controller.clone(); }
    }
    private static final Hk3WeightedCache<String,Layout> CACHE =
            new Hk3WeightedCache<>(8L * 1024 * 1024, Hk3PackedArchitectureReader::estimatedBytes);
    /** 已确认并接入的结构资源键；S01–S05 为研究院区五阶，I13 为工业线 V6。 */








    public static final List<String> IDS=List.of("i01","i01_2","i01_3","i01_4","i02","i03","s01","s02","s03","s04","s05","i04","i05","i06","i07","i08","i09","i10","i11","i12","i13","i14","i15","i16","i17","i18","i19","i20","i21","i22","i23","i24","i25","i26","i27","i28","i29","i30","i31","i32","i33","i34","i35","i36","i37","i38","i39","i40","i41","i42","i43","i44","i45");
    private Hk3ApprovedArchitecture() {}

    /** 仅读取包内UTF-8资源并缓存；调用方不得修改返回坐标或集合。 */
    public static Layout get(String id) {
        if(!IDS.contains(id))throw new IllegalArgumentException("未批准的建筑："+id);
        return CACHE.get(id,key -> {
            var compact=Hk3StructureStream.open(key);
            if(compact!=null)try(var input=compact;var metadata=Hk3ApprovedArchitecture.class.getResourceAsStream("/data/hk3gtl/compact_architecture/"+key+".json")) {
                if(metadata==null)throw new java.io.IOException("缺少紧凑建筑元数据："+key);
                return Hk3PackedArchitectureReader.readCompact(input,new InputStreamReader(metadata,StandardCharsets.UTF_8),key);
            }catch(java.io.IOException error){throw new IllegalStateException("读取紧凑正式建筑失败："+key,error);}
            String file="/data/hk3gtl/approved_architecture/"+key+".json";
            try(var stream=Hk3ApprovedArchitecture.class.getResourceAsStream(file)) {
                if(stream==null)throw new IllegalStateException("缺少正式建筑资源："+file);
                return Hk3PackedArchitectureReader.read(new InputStreamReader(stream,StandardCharsets.UTF_8),key);
            }catch(java.io.IOException error){throw new IllegalStateException("读取正式建筑失败："+key,error);}
        });
    }
}
