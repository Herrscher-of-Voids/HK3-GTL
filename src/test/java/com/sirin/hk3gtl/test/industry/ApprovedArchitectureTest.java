package com.sirin.hk3gtl.test.industry;

import com.sirin.hk3gtl.common.multiblock.pattern.Hk3ApprovedArchitecture;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LateIndustrialPatterns;
import com.google.gson.JsonParser;
import net.minecraft.nbt.NbtIo;
import net.minecraft.nbt.Tag;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;

/** 2026-10-15 01:12:48（修订156）：21 个正式入口、必要能力可安置性及七次逐块继承硬断言。 */
/**
 * 【变更记录 #1】2026-10-15 02:00:40（内测5修订157）
 * 删除：无；新增：正式模板预览验收入口；修改：资源验收尾部执行稀疏与普通空气兼容回归。
 * 用途：将预览完整坐标、真实仓室与主控方向检查纳入原有批准建筑测试任务。
 */
/**
 * 【变更记录 #2】2026-10-15 02:35:08（香港时间；内测5修订158）
 * 删除：无。新增：夹具身份及GT生命周期清理安全回归入口。
 * 修改：正式资源与预览验收后调用纯逻辑安全测试，不改变批准结构与四向规则。
 * 用途：防止清理误删外部同方块新实体，或误保留仅server_tick变化的自有GT仓。
 */
/**
 * 【变更记录 #3】2026-10-15 03:02:02（第3次备注 · 香港时间 · 内测5修订159）
 * 删除：无。新增：HK3控制器结构锁的双线程回归入口。
 * 修改：资源、预览和清理身份验收后检查互斥、异常释放、非阻塞尝试及同线程重入。
 * 用途：将真实并发安全验证纳入已有正式结构验收任务，不改变建筑与匹配规则。
 */
/**
 * 【变更记录 #4】2026-10-23T13:37:15+08:00（第4次备注 · 内测5修订175）
 * 删除：旧面板几何16项实体计数、21入口与固定六口的测试限制；历史备注保留。
 * 新增：I14–I18五形态尺寸数量、17口、input/output择一组及工业主控宽度居中/净空/背壳断言。
 * 修改：26形态与批准V2一致，原接口能力、真实仓模板及I01逐格继承回归继续执行。
 * 用途：防止新坐标与Pattern/NBT脱节；不替代游戏成型、配方或生存验收。
 */
public final class ApprovedArchitectureTest {
    /**
     * 【变更记录 #5】2026-10-26 20:50:18（修订177）
     * 删除：把全部正式入口固定为26的限制；新增：I05批准V5主控与滤芯口精确坐标回归。
     * 修改：原26形态仍独立验收全部几何、模板与继承，新十台交由高阶专项测试。
     * 用途：同步已批准V5且保留其余机器中轴检查，不把新机器混入旧版本总量预期。
     */
    private static final Map<String,int[]> SIZES=Map.ofEntries(
            Map.entry("i01",new int[]{17,33,17}), Map.entry("i01_2",new int[]{25,37,25}),
            Map.entry("i01_3",new int[]{37,45,37}), Map.entry("i01_4",new int[]{53,81,53}),
            Map.entry("i02",new int[]{39,25,35}), Map.entry("i03",new int[]{41,29,39}),
            Map.entry("i04",new int[]{35,43,35}), Map.entry("i05",new int[]{43,49,37}),
            Map.entry("i06",new int[]{55,29,41}), Map.entry("i07",new int[]{45,27,37}),
            Map.entry("i08",new int[]{45,40,43}), Map.entry("i09",new int[]{43,41,39}),
            Map.entry("i10",new int[]{51,33,43}), Map.entry("i11",new int[]{55,31,45}),
            Map.entry("i12",new int[]{45,37,39}), Map.entry("i13",new int[]{53,45,45}),
            Map.entry("i14",new int[]{47,39,43}),
            Map.entry("i15",new int[]{57,49,57}),
            Map.entry("i16",new int[]{49,29,57}),
            Map.entry("i17",new int[]{49,35,55}),
            Map.entry("i18",new int[]{45,33,65}),
            Map.entry("s01",new int[]{17,17,25}), Map.entry("s02",new int[]{33,27,37}),
            Map.entry("s03",new int[]{49,37,57}), Map.entry("s04",new int[]{73,55,73}),
            Map.entry("s05",new int[]{129,105,129}));
    private static final Map<String,Integer> COUNTS=Map.ofEntries(
            Map.entry("i01",1390),Map.entry("i01_2",3346),Map.entry("i01_3",7994),Map.entry("i01_4",23623),
            Map.entry("i02",2452),Map.entry("i03",4179),Map.entry("i04",4005),Map.entry("i05",7519),
            Map.entry("i06",9705),Map.entry("i07",5277),Map.entry("i08",8333),Map.entry("i09",5004),
            Map.entry("i10",8759),Map.entry("i11",11881),Map.entry("i12",8405),Map.entry("i13",13323),
            Map.entry("i14",13818),Map.entry("i15",17816),Map.entry("i16",18640),Map.entry("i17",13254),Map.entry("i18",17576),
            Map.entry("s01",1930),Map.entry("s02",7720),Map.entry("s03",17185),Map.entry("s04",44225),Map.entry("s05",160406));

    public static void main(String[] args) throws Exception {
        var legacyIds=legacyIds();
        check(legacyIds.size()==26,"原批准形态入口数量");
        check(new HashSet<>(legacyIds).equals(SIZES.keySet()),"原批准形态入口集合");
        for(String id:legacyIds) {
            var data=Hk3ApprovedArchitecture.get(id);
            check(Arrays.equals(data.size(),SIZES.get(id)),"尺寸："+id);
            check(data.blocks().size()==COUNTS.get(id),"实体数量："+id);
            Map<List<Integer>,String> cells=new HashMap<>();
            for(var block:data.blocks()) {
                var pos=key(block.pos());
                check(cells.put(pos,block.state())==null,"重复方块："+id+pos);
                for(int axis=0;axis<3;axis++)check(block.pos()[axis]>=0&&block.pos()[axis]<data.size()[axis],"越界："+id);
                int x=block.pos()[0]-data.controller()[0],z=block.pos()[2]-data.controller()[2];
                for(int rotation=0;rotation<4;rotation++) {
                    int rx=x,rz=z;
                    for(int step=0;step<rotation;step++){int old=rx;rx=-rz;rz=old;}
                    for(int step=0;step<rotation;step++){int old=rx;rx=rz;rz=-old;}
                    check(rx==x&&rz==z,"四向逆变换："+id);
                }
            }
            check(cells.containsKey(key(data.controller())),"缺少主控方块："+id);
            if(id.startsWith("i")) {
                int[] control=data.controller();
                if(id.equals("i05"))
                    check(Arrays.equals(control,new int[]{20,3,16}),"I05负责人指定V5主控坐标");
                else check(control[0]==(data.size()[0]-1)/2,"工业主控宽度居中："+id);
                check(!cells.containsKey(key(new int[]{control[0],control[1],control[2]-1})),"主控正面净空："+id);
                check(cells.containsKey(key(new int[]{control[0],control[1],control[2]+1})),"主控实体背壳："+id);
            }
            check(data.ports().size()==(id.equals("i18")?17:6),"接口数量："+id);
            Set<String> portIds=new HashSet<>();
            for(var port:data.ports()) {
                check(portIds.add(port.id()),"重复端口："+id);
                check(cells.containsKey(key(port.pos())),"接口无方块："+id+port.id());
                check("hk3gtl:industrial_port_casing".equals(cells.get(key(port.pos()))),"接口机壳："+id+port.id());
                check("north".equals(port.face()),"接口北向："+id+port.id());
                int[] p=port.pos();
                check(!cells.containsKey(key(new int[]{p[0],p[1],p[2]-1})),"接口正面净空："+id+port.id());
            }
            if(id.equals("i05")) {
                var filter=data.ports().stream().filter(port -> port.id().equals("FILTER")).findFirst().orElseThrow();
                check(Arrays.equals(filter.pos(),new int[]{6,3,16}),"I05批准V5滤芯口坐标");
                check(!"hk3gtl:industrial_port_casing".equals(cells.get(List.of(14,3,16))),"I05旧滤芯口已还原壳体");
            }
            if(id.startsWith("i"))checkIndustrialPorts(id,data,cells);
            checkTemplate(id,data,cells);
            System.out.println(id+"：正式资源坐标和接口通过");
        }
        for(int stage=1;stage<=3;stage++)
            checkAdditive(stage==1?"i01":"i01_"+stage,"i01_"+(stage+1));
        for(int stage=1;stage<=3;stage++)
            checkTemplateAdditive(stage==1?"i01":"i01_"+stage,"i01_"+(stage+1));
        for(int stage=1;stage<=4;stage++)
            checkAdditive(String.format(Locale.ROOT,"s%02d",stage),String.format(Locale.ROOT,"s%02d",stage+1));
        IndustrialProcessRoleTest.main(args);
        ApprovedArchitecturePreviewTest.main(args);
        com.sirin.hk3gtl.common.command.ApprovedFixtureOwnershipTest.main(args);
        com.sirin.hk3gtl.common.machine.Hk3PatternLockTest.main(args);
    }

    static List<String> legacyIds() {
        return Hk3ApprovedArchitecture.IDS.stream().filter(id -> !Hk3LateIndustrialPatterns.IDS.contains(id)).toList();
    }

    /** 各阶相减主控位置后，所有旧非主控的世界坐标和状态必须完全一致。 */
    private static void checkAdditive(String previous,String following) {
            var before=Hk3ApprovedArchitecture.get(previous);
            var after=Hk3ApprovedArchitecture.get(following);
            Map<List<Integer>,String> next=new HashMap<>();
            for(var block:after.blocks())next.put(key(block.pos()),block.state());
            int[] a=before.controller(),b=after.controller();
            for(var block:before.blocks()) {
                if(Arrays.equals(block.pos(),a))continue;
                int[] pos=block.pos();
                check(Objects.equals(block.state(),next.get(key(new int[]{pos[0]+b[0]-a[0],pos[1]+b[1]-a[1],pos[2]+b[2]-a[2]}))),
                        previous+"→"+following+"扩建变更旧非主控："+Arrays.toString(pos));
            }
            System.out.println(previous+"→"+following+"逐块继承通过："+(before.blocks().size()-1)+"块");
    }

    /** 分别占用真实仓位的必要能力检查，防止六口全部填壳或槽位数量不足。 */
    private static void checkIndustrialPorts(String id,Hk3ApprovedArchitecture.Layout data,Map<List<Integer>,String> cells) {
        check(!cells.get(key(data.controller())).equals("minecraft:diamond_block"),"未替换真实工业主控："+id);
        List<Set<String>> choices=new ArrayList<>();
        for(var port:data.ports())choices.add(switch(port.group()) {
            case "item_input" -> Set.of("item_input");
            case "item_output" -> Set.of("item_output");
            case "item" -> Set.of("item_input","item_output");
            case "fluid_input" -> Set.of("fluid_input");
            case "fluid_output" -> Set.of("fluid_output");
            case "fluid" -> Set.of("fluid_input","fluid_output");
            case "input" -> Set.of("item_input","fluid_input");
            case "output" -> Set.of("item_output","fluid_output");
            case "service" -> Set.of();
            default -> throw new AssertionError("非法工业接口组："+id+port.group());
        });
        var required=new ArrayList<>(List.of("item_input"));
        if(!id.equals("i01"))required.add("item_output");
        if(!id.equals("i02")&&!id.equals("i07")) {
            if(!id.equals("i01"))required.add("fluid_input");
            if(!id.equals("i11"))required.add("fluid_output");
        }
        check(assign(required,choices,new HashSet<>()),"必要能力不能同时安置："+id);
        check(!assign(required,Collections.nCopies(data.ports().size(),Set.of()),new HashSet<>()),"填充壳不能作为工作仓："+id);
    }

    private static boolean assign(List<String> required,List<Set<String>> choices,Set<Integer> used) {
        if(required.isEmpty())return true;
        for(int slot=0;slot<choices.size();slot++)if(!used.contains(slot)&&choices.get(slot).contains(required.get(0))) {
            var next=new HashSet<>(used);next.add(slot);
            if(assign(required.subList(1,required.size()),choices,next))return true;
        }
        return false;
    }

    /** 正式放置模板必须和 Pattern 一致；只有声明端口允许换真实工作仓。 */
    private static void checkTemplate(String id,Hk3ApprovedArchitecture.Layout data,Map<List<Integer>,String> cells) throws Exception {
        var template=template(id);
        check(template.keySet().equals(cells.keySet()),"模板实体坐标不一致："+id);
        Set<List<Integer>> ports=new HashSet<>();
        var abilities=new HashSet<String>();
        for(var port:data.ports()) {
            var pos=key(port.pos());ports.add(pos);
            String state=template.get(pos),block=state.split("\\[",2)[0];
            if(block.equals("hk3gtl:industrial_port_casing"))continue;
            String ability=switch(block) {
                case "gtceu:max_input_bus" -> "item_input";
                case "gtceu:max_output_bus" -> "item_output";
                case "gtceu:max_input_hatch", "gtceu:max_input_hatch_4x" -> "fluid_input";
                case "gtceu:max_output_hatch", "gtceu:max_output_hatch_4x" -> "fluid_output";
                default -> throw new AssertionError("模板未知仓："+id+state);
            };
            check(state.endsWith("[facing=north]"),"模板接口朝向："+id);
            check(port.group().equals(ability)||(port.group().equals("item")&&ability.startsWith("item_"))
                    ||(port.group().equals("fluid")&&ability.startsWith("fluid_"))
                    ||(port.group().equals("input")&&ability.endsWith("_input"))
                    ||(port.group().equals("output")&&ability.endsWith("_output")),"模板接口组不匹配："+id);
            abilities.add(ability);
        }
        for(var cell:cells.entrySet())if(!ports.contains(cell.getKey())&&!cell.getKey().equals(key(data.controller())))
            check(cell.getValue().equals(template.get(cell.getKey())),"模板变更普通建筑块："+id+cell.getKey());
        try(var stream=ApprovedArchitectureTest.class.getResourceAsStream("/data/hk3gtl/structures/approved/"+id+".json")) {
            check(stream!=null,"缺模板清单："+id);
            var manifest=JsonParser.parseString(new String(stream.readAllBytes(),StandardCharsets.UTF_8)).getAsJsonObject();
            check(template.get(key(data.controller())).equals(manifest.get("machine").getAsString()+"[facing=north]"),"模板真实主控："+id);
            if(id.startsWith("i")) {
                check(cells.get(key(data.controller())).equals(manifest.get("machine").getAsString()),"Pattern主控注册ID："+id);
                for(var required:manifest.getAsJsonArray("required_abilities"))
                    check(abilities.contains(required.getAsString()),"模板缺工作能力："+id+required);
            }
            try(var layout=ApprovedArchitectureTest.class.getResourceAsStream("/data/hk3gtl/approved_architecture/"+id+".json")) {
                String digest=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(layout.readAllBytes()));
                check(digest.equals(manifest.get("sha256").getAsString()),"模板引用资源哈希："+id);
            }
        }
    }

    private static Map<List<Integer>,String> template(String id) throws IOException {
        try(var stream=ApprovedArchitectureTest.class.getResourceAsStream("/data/hk3gtl/structures/approved/"+id+".nbt")) {
            check(stream!=null,"缺正式NBT模板："+id);
            var nbt=NbtIo.readCompressed(stream);var palette=nbt.getList("palette",Tag.TAG_COMPOUND);
            var cells=new HashMap<List<Integer>,String>();
            for(var raw:nbt.getList("blocks",Tag.TAG_COMPOUND)) {
                var block=(net.minecraft.nbt.CompoundTag)raw;var pos=block.getList("pos",Tag.TAG_INT);
                var state=palette.getCompound(block.getInt("state"));String text=state.getString("Name");
                var props=state.getCompound("Properties");
                if(!props.isEmpty()) {
                    var pairs=new ArrayList<String>();
                    for(String key:new TreeSet<>(props.getAllKeys()))pairs.add(key+"="+props.getString(key));
                    text+="["+String.join(",",pairs)+"]";
                }
                check(cells.put(List.of(pos.getInt(0),pos.getInt(1),pos.getInt(2)),text)==null,"模板重复坐标："+id);
            }
            return cells;
        }
    }

    private static void checkTemplateAdditive(String previous,String following) throws IOException {
        var before=Hk3ApprovedArchitecture.get(previous);var after=Hk3ApprovedArchitecture.get(following);
        var old=template(previous);var next=template(following);
        int[] a=before.controller(),b=after.controller();
        for(var entry:old.entrySet())if(!entry.getKey().equals(key(a))) {
            var p=entry.getKey();
            check(entry.getValue().equals(next.get(List.of(p.get(0)+b[0]-a[0],p.get(1)+b[1]-a[1],p.get(2)+b[2]-a[2]))),
                    "正式模板扩建替换旧非主控："+previous+"→"+following+p);
        }
    }

    private static List<Integer> key(int[] p){return List.of(p[0],p[1],p[2]);}
    private static void check(boolean value,String message){if(!value)throw new AssertionError(message);}
}
