package com.sirin.hk3gtl.common.multiblock.pattern;

import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.machine.multiblock.PartAbility;
import com.gregtechceu.gtceu.api.pattern.BlockPattern;
import com.gregtechceu.gtceu.api.pattern.FactoryBlockPattern;
import com.gregtechceu.gtceu.api.pattern.Predicates;
import com.gregtechceu.gtceu.api.pattern.TraceabilityPredicate;
import static com.gregtechceu.gtceu.api.pattern.util.RelativeDirection.RIGHT;
import static com.gregtechceu.gtceu.api.pattern.util.RelativeDirection.UP;
import static com.gregtechceu.gtceu.api.pattern.util.RelativeDirection.BACK;

/**
 * 将正式工业布局接入 GT 成型系统，保留严格空气和后侧检修带。
 * 【变更记录 #1】2026-09-24 16:32:00（内测5修订66）
 * 删除：不允许整面机壳随意换仓。新增：七机共用材料映射与独立工艺布局。
 * 修改：按实际输入输出要求限定仓位；电力沿用玩家无线电网，无需创造能源仓。
 * 用途：所有材料缺失立即报错，校准台不要求流体仓，注入器不要求无用产出仓。
 *
 * 【变更记录 #2】2026-09-24 18:56:36（内测5修订67）
 * 删除：把物品输入、物品输出、流体输入和流体输出分别绑定到唯一能力的限制。
 * 新增：同类端口的双向能力谓词；物品仓/总线可在物品槽位互换，流体仓可在流体槽位互换。
 * 修改：结构材料改由 MAX 海渊材料契约提供，平行仓槽继续保持单槽上限。
 * 用途：保留配方输入输出的资源类型边界，同时避免玩家被迫按控制器背面固定左右位置安装端口。
 */
/**
 * 【变更记录 #3】2026-09-25 02:19:54（内测5修订70）
 * 删除：旧建筑退出四机正式入口，历史文件已归档。
 * 新增：已确认逐格建筑及一致的模板与验收入口。
 * 修改：同步主控坐标、材料或测试夹具，不改配方和研究扣费。
 * 用途：使预览、正式结构及游戏放置相互对应；未将静态验证写作实机通过。
 */
/**
 * 【变更记录 #4】2026-09-27 02:30:55（第 4 次备注 · 内测5修订87）
 * 删除：I04/I05同类端口按布局字母各自重复建立计数的限制；其他机器维持原逻辑。
 * 新增：I04/I05物品及流体各共享一组输入、输出谓词，每个方向至少一个端口。
 * 修改：允许同类槽位任意分配方向，预览保持2进2出物品口、4进4出流体口。
 * 用途：端口能力与既有工艺匹配；本次不批准或替换旧结构材料，不代表实机成型通过。
 */
/**
 * 【变更记录 #5】2026-09-27 02:38:43（第 5 次备注 · 内测5修订87 · 正式六机接入）
 * 删除：相关正式入口对旧I04/I05结构的依赖；历史备注与旧布局数据保留。
 * 新增：I04/I05与I03同样委托统一批准结构适配器；其余四台继续原入口。
 * 修改：沿获批逐格资源接入23×27×23稳定塔与27×19×23再生中心，数量与方向由正式资源确定。
 * 用途：统一成型、放置模板和诊断坐标；不改变研究费用，不启动游戏，不视为成型验收。
 */
/**
 * 【变更记录 #6】2026-09-27 03:06:43（第 6 次备注 · 内测5修订88）
 * 删除：无，保留历史说明和原有结构几何。
 * 新增：现行液态工业设备的空余物品、流体和可选并行位支持新机械方块；旧有合法替代件保留。
 * 修改：接入工业接口机械方块；保留必要能力的全局数量约束。
 * 用途：让多余接口可以封闭，不用填充方块冒充真实仓室能力。
 */
public final class Hk3LiquidLinePatterns {
    private Hk3LiquidLinePatterns() {}

    /** 同类物品端口允许输入仓、输出仓和对应总线互换，不能接受流体能力。 */
    private static TraceabilityPredicate itemPort(int previewCount) {
        return Hk3InterfacePredicates.abilities(PartAbility.IMPORT_ITEMS)
                .or(Hk3InterfacePredicates.abilities(PartAbility.EXPORT_ITEMS))
                .setMinGlobalLimited(1)
                .setPreviewCount(previewCount);
    }

    /** 同类流体端口允许输入仓和输出仓互换，不能接受物品能力。 */
    private static TraceabilityPredicate fluidPort(int previewCount) {
        return Hk3InterfacePredicates.abilities(PartAbility.IMPORT_FLUIDS)
                .or(Hk3InterfacePredicates.abilities(PartAbility.EXPORT_FLUIDS))
                .setMinGlobalLimited(1)
                .setPreviewCount(previewCount);
    }

    public static BlockPattern create(MultiblockMachineDefinition definition,Hk3LiquidLineLayout.Kind kind) {
        // 2026-09-25：I03使用已批准建筑；其余六台保留现有工艺与布局，旧分馏布局仅留作历史归档。
        if(kind==Hk3LiquidLineLayout.Kind.SEPARATION)return Hk3ApprovedArchitecturePatterns.create(definition,"i03");
        if(kind==Hk3LiquidLineLayout.Kind.STABILIZATION)return Hk3ApprovedArchitecturePatterns.create(definition,"i04");
        if(kind==Hk3LiquidLineLayout.Kind.REGENERATION)return Hk3ApprovedArchitecturePatterns.create(definition,"i05");
        var layout=Hk3LiquidLineLayout.create(kind);
        var builder=FactoryBlockPattern.start(RIGHT,UP,BACK);
        for(int z=0;z<kind.depth;z++)builder.aisle(layout.aisle(z));
        builder.where('S',Predicates.controller(Predicates.blocks(definition.getBlock())))
                .where('#',Hk3InterfacePredicates.clearance());
        for(var entry:layout.materials().entrySet())
            builder.where(entry.getKey(),Predicates.blocks(Hk3StructureBlocks.require(entry.getValue())));
        var filler=Predicates.blocks(Hk3StructureBlocks.require("hk3gtl:industrial_port_casing"));
        // 全部同类接口共享同一组计数，封闭多余槽位也必须保留一进一出。
        // 修订214：小型兼容结构同样不区分接口位置，仍保留物品与流体各一进一出。
        boolean injection=kind==Hk3LiquidLineLayout.Kind.INJECTION;
        var itemOut=Hk3InterfacePredicates.abilities(PartAbility.EXPORT_ITEMS).setPreviewCount(injection?0:1);
        var fluidOut=Hk3InterfacePredicates.abilities(PartAbility.EXPORT_FLUIDS).setPreviewCount(injection?0:1);
        if (!injection) { itemOut.setMinGlobalLimited(1);fluidOut.setMinGlobalLimited(1); }
        var items=Hk3InterfacePredicates.abilities(PartAbility.IMPORT_ITEMS).setMinGlobalLimited(1).setPreviewCount(1)
                .or(itemOut)
                .or(Hk3InterfacePredicates.abilities(PartAbility.IMPORT_FLUIDS).setMinGlobalLimited(1).setPreviewCount(1))
                .or(fluidOut).or(filler);
        if (injection) items=items.or(Predicates.abilities(PartAbility.PARALLEL_HATCH).setMaxGlobalLimited(1).setPreviewCount(0));
        var fluids=items;
        builder.where('i',items).where('o',items).where('u',fluids).where('v',fluids);
        builder.where('h',Predicates.blocks(Hk3StructureBlocks.require(layout.materials().get('C'))).or(filler)
                        .or(Predicates.abilities(PartAbility.PARALLEL_HATCH).setMaxGlobalLimited(1).setPreviewCount(0)).or(items));
        return builder.build();
    }
}
