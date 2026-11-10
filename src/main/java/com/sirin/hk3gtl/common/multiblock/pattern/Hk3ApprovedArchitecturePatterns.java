package com.sirin.hk3gtl.common.multiblock.pattern;

import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.machine.multiblock.PartAbility;
import com.gregtechceu.gtceu.api.pattern.*;
import com.sirin.hk3gtl.common.machine.multiblock.part.Hk3PartAbility;
import java.util.*;
import static com.gregtechceu.gtceu.api.pattern.util.RelativeDirection.*;

/**
 * 【变更记录 #1】2026-09-25 02:18:00（内测5修订70）
 * 删除：四台正式入口不再使用旧海渊材料兼容布局。新增：批准蓝图到GT成型的精确适配。
 * 修改：钻石主控和接口标记转换为真实控制器与能力谓词；空腔严格要求空气。
 * 用途：保留工艺、电网和研究扣费；同类仓可互换，研究所能源口与并行位可封回MAX机壳。
 */
/**
 * 【变更记录 #2】2026-09-27 02:38:43（第 2 次备注 · 内测5修订87 · 正式六机接入）
 * 删除：相关正式入口对旧I04/I05结构的依赖；历史备注与旧布局数据保留。
 * 新增：两台各4物品槽、8流体槽、1可选并行槽；同类共享计数且每方向至少1个。I03预览改2流体进4出。
 * 修改：沿获批逐格资源接入23×27×23稳定塔与27×19×23再生中心，数量与方向由正式资源确定。
 * 用途：统一成型、放置模板和诊断坐标；不改变研究费用，不启动游戏，不视为成型验收。
 */
/**
 * 【变更记录 #3】2026-09-27 03:06:43（第 3 次备注 · 内测5修订88）
 * 删除：无，保留历史说明和原有结构几何。
 * 新增：I01–I05和S01接口支持新机械方块；I01仍须物品输入与流体输出，I02仍须物品一进一出，I03–I05两类仓各须一进一出。
 * 修改：接入工业接口机械方块；保留必要能力的全局数量约束。
 * 用途：让多余接口可以封闭，不用填充方块冒充真实仓室能力。
 */
public final class Hk3ApprovedArchitecturePatterns {
    private Hk3ApprovedArchitecturePatterns() {}

    /** 将单台获批逐格资源编成模式；朝北时X向东、Y向上、Z向南，支持四个水平朝向。 */
    public static BlockPattern create(MultiblockMachineDefinition definition,String id) {
        // 修订214：兼容入口沿用当前工业通用接口，避免两套位置规则。
        if (!id.equals("s01")) return Hk3IndustrialApprovedPatterns.create(definition,id);
        var data=Hk3ApprovedArchitecture.get(id);int[] size=data.size();
        char[][][] cells=new char[size[2]][size[1]][size[0]];
        for(var slice:cells)for(var row:slice)Arrays.fill(row,'#');
        Map<String,Character> palette=new LinkedHashMap<>();
        int[] controller=data.controller();
        for(var cell:data.blocks()) {
            char symbol;
            if(Arrays.equals(cell.pos(),controller))symbol='S';
            else if(cell.state().equals("minecraft:diamond_ore"))symbol='?';
            else symbol=palette.computeIfAbsent(cell.state(),state -> (char)(0xE000+palette.size()));
            int[] p=cell.pos();cells[p[2]][p[1]][p[0]]=symbol;
        }
        for(var port:data.ports()) {
            char symbol=switch(id) {
                case "i01_2", "i01_3", "i01_4" -> 'u';
                case "i01" -> port.id().equals("F1")?'f':port.id().equals("M2")?'j':'i';
                case "i02" -> port.id().equals("M3")||port.id().equals("M4")?'j':'i';
                case "i03", "i04", "i05", "i06", "i07", "i08" -> port.id().startsWith("F")?'f':port.id().equals("P1")?'p':'i';
                case "i09", "i10", "i11", "i12" -> 'u';
                case "s01" -> 'h';
                default -> throw new IllegalArgumentException(id);
            };
            if (!id.equals("s01") && !id.equals("i01") && !id.equals("i02")
                    && !port.id().matches("[MF][0-9]+|P1")) symbol='u';
            if (id.equals("i01") && port.id().matches("[1-4]")) symbol='u';
            if (id.equals("i02") && !port.id().matches("[MF][0-9]+")) symbol='u';
            int[] p=port.pos();cells[p[2]][p[1]][p[0]]=symbol;
        }
        var builder=FactoryBlockPattern.start(RIGHT,UP,BACK);
        for(var slice:cells){String[] rows=new String[size[1]];for(int y=0;y<rows.length;y++)rows[y]=new String(slice[y]);builder.aisle(rows);}
        builder.where('S',Predicates.controller(Predicates.blocks(definition.getBlock()))).where('#',Hk3InterfacePredicates.clearance());
        for(var entry:palette.entrySet()) {
            // 超导线圈允许游戏切换运行状态，其余方块仍按精确注册ID匹配，不接受旧机壳替代。
            String blockId=entry.getKey().split("\\[",2)[0];
            builder.where(entry.getValue(),Predicates.blocks(Hk3StructureBlocks.require(blockId)));
        }
        var filler=Predicates.blocks(Hk3StructureBlocks.require("hk3gtl:industrial_port_casing"));
        var casing=Predicates.blocks(Hk3StructureBlocks.require("gtceu:max_machine_casing")).or(filler);
        boolean loopMachine=id.equals("i04")||id.equals("i05");
        boolean newLayout=data.ports().stream().anyMatch(port -> !port.id().matches("[MF][0-9]+|P1"));
        if (newLayout && !id.equals("s01")) {
            var itemIn=Hk3InterfacePredicates.abilities(PartAbility.IMPORT_ITEMS).setMinGlobalLimited(1);
            var ports=itemIn;
            if (!id.equals("i02") && !id.equals("i07"))
                ports=ports.or(Hk3InterfacePredicates.abilities(PartAbility.EXPORT_FLUIDS).setMinGlobalLimited(1));
            if (!id.startsWith("i01")) {
                ports=ports.or(Hk3InterfacePredicates.abilities(PartAbility.EXPORT_ITEMS).setMinGlobalLimited(1));
                if (!id.equals("i02") && !id.equals("i07"))
                    ports=ports.or(Hk3InterfacePredicates.abilities(PartAbility.IMPORT_FLUIDS).setMinGlobalLimited(1));
            }
            builder.where('u',ports.or(filler));
            return builder.build();
        }
        if(!id.equals("s01")) {
            // 在同类所有槽位共享能力计数，保证至少一进一出；采集塔只需物品进、流体出。
            var itemIn=Hk3InterfacePredicates.abilities(PartAbility.IMPORT_ITEMS).setMinGlobalLimited(1).setPreviewCount(loopMachine?2:1);
            var itemOut=Hk3InterfacePredicates.abilities(PartAbility.EXPORT_ITEMS).setPreviewCount(id.equals("i01")?0:loopMachine?2:1);
            if(!id.equals("i01"))itemOut.setMinGlobalLimited(1);
            var items=itemIn.or(itemOut);
            builder.where('i',items.or(filler)).where('j',casing.or(items));
            if(id.equals("i01")||id.equals("i03")||loopMachine) {
                var fluidIn=Hk3InterfacePredicates.abilities(PartAbility.IMPORT_FLUIDS).setPreviewCount(loopMachine?4:id.equals("i03")?2:0);
                if(!id.equals("i01"))fluidIn.setMinGlobalLimited(1);
                var fluidOut=Hk3InterfacePredicates.abilities(PartAbility.EXPORT_FLUIDS).setMinGlobalLimited(1).setPreviewCount(id.equals("i01")?1:4);
                builder.where('f',fluidIn.or(fluidOut).or(filler));
            }
            if(id.equals("i03")||loopMachine)builder.where('p',casing.or(Predicates.abilities(PartAbility.PARALLEL_HATCH).setMaxGlobalLimited(1).setPreviewCount(0)));
        }else {
            builder.where('h',casing.or(Predicates.abilities(Hk3PartAbility.HONKAI_ENERGY_INPUT).setPreviewCount(0))
                    .or(Predicates.abilities(Hk3PartAbility.WIRELESS_HONKAI_INPUT).setPreviewCount(0))
                    .or(Hk3InterfacePredicates.abilities(PartAbility.IMPORT_ITEMS,PartAbility.EXPORT_ITEMS,
                            PartAbility.IMPORT_FLUIDS,PartAbility.EXPORT_FLUIDS).setPreviewCount(0)));
        }
        return builder.build();
    }
}
