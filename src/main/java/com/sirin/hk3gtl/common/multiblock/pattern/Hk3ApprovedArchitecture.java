package com.sirin.hk3gtl.common.multiblock.pattern;

/** 2026-10-30（修订182）：加入I40 V1、I41 V3、I42 V1、I43 V1、I44车站V2、I45黑金列车V2；共52形态，I37仍排除。 */

import com.sirin.hk3gtl.common.util.Hk3WeightedCache;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.List;



/**
 * 【变更记录 #1】2026-09-25 02:18:00（内测5修订70）
 * 删除：无；旧布局在归档中保留。新增：四台获批建筑的只读逐格资源加载器。
 * 修改：成型、模板与验收共享已确认坐标，单位为方块，顺序为X/Y/Z。
 * 用途：防止预览与实际结构各自维护；资源缺失或非法坐标直接报错，禁止回退旧结构。
 */
/**
 * 【变更记录 #2】2026-09-27 02:38:43（第 2 次备注 · 内测5修订87 · 正式六机接入）
 * 删除：相关正式入口对旧I04/I05结构的依赖；历史备注与旧布局数据保留。
 * 新增：将已获负责人明确批准的I04/I05加入正式建筑键，原四台顺序保持不变。
 * 修改：沿获批逐格资源接入23×27×23稳定塔与27×19×23再生中心，数量与方向由正式资源确定。
 * 用途：统一成型、放置模板和诊断坐标；不改变研究费用，不启动游戏，不视为成型验收。
 */
/**
 * 【变更记录 #3】2026-09-27 23:52:00（内测5修订91）
 * 删除：无文件删除；替换逐格对象常驻与无容量限制的缓存实现。
 * 新增：8MiB估算权重的LRU缓存、流式紧凑布局与只读元数据访问。
 * 修改：仍从相同获批资源加载，顺序、坐标、状态和端口不变；异常不缓存。
 * 用途：兼顾原包与增强版的低内存设备，不持有世界或渲染对象。
 */
/**
 * 【变更记录 #4】2026-10-15 01:15:46（第4次备注 · 内测5修订156）
 * 删除：对正式入口仍停留在16项的限制；历史资源加载和缓存规则保留。
 * 新增：I13及S02–S05五个已经确认的资源键，总数21项。
 * 修改：共享资源清单对应I01四阶V8、I02–I08 V7、I09–I13 V6、S01–S05 V1。
 * 用途：统一最新批准建筑的Pattern、模板、诊断和验收；未批准I14不进入此清单。
 */
/**
 * 【变更记录 #5】2026-10-23 13:35:32（第5次备注 · 内测5修订175）
 * - 删除：I14–I18不在批准清单的当前限制，旧历史说明保留。
 * - 新增：本轮明确批准的五台融合置中V2资源键，总数26形态。
 * - 修改：新增设备与既有工业、研究所共用精确布局加载和身份校验。
 * - 用途：保持Pattern、模板和诊断同源；不把结构批准当作工艺或生存验收。
 */
/**
 * 【变更记录 #6】2026-10-26 19:41:15（第6次备注 · 内测5修订177）
 * - 删除：正式入口止于I18的限制；新增：负责人要求实装的I19–I28十个资源键。
 * - 修改：与原26种形态共用批准资源、模板及诊断索引；旧I01四阶保持指定V2。
 * - 用途：将真实控制器与批准建筑接为同一资源来源，不把配方计划等同于验收。
 */
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
    // 【变更记录 #7】2026-10-27（修订180）：新增已批准I29–I33，原36份建筑保持原样。
/**
 * 【变更记录 #8】2026-10-27 22:31:22（第8次备注 · 内测5修订181）
 * - 删除：无，原41种批准形态和历史备注保留。
 * - 新增：batch09明确批准的I34 V2、I35 V3、I36 V1、I38 V1、I39 V1资源键。
 * - 修改：正式资源白名单扩为46形态，未批准的I37不加入。
 * - 用途：控制器、严格Pattern和完整预览仅读取相应批准建筑，不开放工艺或生存配方。
 */
    public static final List<String> IDS=List.of("i01","i01_2","i01_3","i01_4","i02","i03","s01","s02","s03","s04","s05","i04","i05","i06","i07","i08","i09","i10","i11","i12","i13","i14","i15","i16","i17","i18","i19","i20","i21","i22","i23","i24","i25","i26","i27","i28","i29","i30","i31","i32","i33","i34","i35","i36","i38","i39","i40","i41","i42","i43","i44","i45");
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
