package com.sirin.hk3gtl.common.multiblock.pattern;

import com.gregtechceu.gtceu.api.GTValues;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;

/**
 * 第一条工业线的正式逐格结构数据，坐标单位为方块，顺序为宽、高、深。
 * 【变更记录 #1】2026-09-24 16:32:00（内测5修订66）
 * 删除：不复用旧盒形结构；旧实现已归档。新增：七台独立工艺布局与固定物流口。
 * 修改：以同一确定性数据供成型和测试使用。用途：避免结构、方块清单和接口脱节。
 * 不依赖游戏注册表，允许在普通虚拟机中验证尺寸、通道和符号；不生成预览资源。
 *
 * 【变更记录 #2】2026-09-24 18:56:36（内测5修订67）
 * 删除：液态工业线中仍使用 GTCEu 基础洁净机壳、钢机壳、钢管机壳和原版装饰方块的材料映射。
 * 新增：MAX 阶段统一材料契约、分层外观骨架和边缘服务脊，所有主体材料改为 HK3GTL 海渊高阶方块。
 * 修改：端口位置仍由蓝图确定，但输入/输出方向交由 Pattern 的同类能力谓词判定，允许同类端口互换。
 * 用途：让第一条工业线的结构材料与 MAX 配方电压一致，同时保持结构尺寸和成型数据可复现。
 */
public final class Hk3LiquidLineLayout {
    public enum Kind {
        SEPARATION(25, 25, 29), STABILIZATION(21, 33, 21), REGENERATION(21, 29, 25),
        BLENDING(25, 21, 33), CALIBRATION(19, 19, 21), CONCENTRATION(33, 29, 41),
        INJECTION(41, 33, 45);
        public final int width, height, depth;
        Kind(int width, int height, int depth) { this.width=width; this.height=height; this.depth=depth; }
    }

    /**
     * 第一条工业线的科技契约。所有液态线配方以 MAX（GT tier 14）为起点，
     * 结构主体不得回退到 HV 或普通 GTCEu 机壳。
     */
    public static final int VOLTAGE_TIER = GTValues.MAX;
    public static final String TECHNOLOGY_LEVEL = "MAX";

    /**
     * 第一条工业线允许使用的 MAX 结构材料白名单。
     * 只列出本模组注册的海渊机壳、功能构件与稳定玻璃，防止后续布局误把
     * HV/普通 GTCEu 机壳或原版装饰方块当作正式 MAX 主体材料。
     */
    public static final Set<String> MAX_MATERIALS = Set.of(
            "hk3gtl:casing_abyss_energy",
            "hk3gtl:casing_abyss_mechanical",
            "hk3gtl:coil_abyss_flux",
            "hk3gtl:glass_honkai_stabilized",
            "hk3gtl:structure_abyss_cooling_unit",
            "hk3gtl:structure_communication_array",
            "hk3gtl:structure_data_pillar",
            "hk3gtl:casing_abyss_research",
            "hk3gtl:casing_reinforced_soulium");

    /**
     * 各符号对应的 MAX/海渊材料；物流能力在 Pattern 适配层单独处理，禁止空气替代缺失方块。
     * C/F/R/B 是承重层，P/K/W/L 是工艺层，G/V 是观察层。
     */
    public static final Map<Character,String> MATERIALS = Map.ofEntries(
            Map.entry('C',"hk3gtl:casing_abyss_energy"),
            Map.entry('F',"hk3gtl:casing_abyss_mechanical"),
            Map.entry('P',"hk3gtl:coil_abyss_flux"),
            Map.entry('G',"hk3gtl:glass_honkai_stabilized"),
            Map.entry('K',"hk3gtl:structure_abyss_cooling_unit"),
            Map.entry('W',"hk3gtl:structure_communication_array"),
            Map.entry('L',"hk3gtl:structure_data_pillar"),
            Map.entry('R',"hk3gtl:casing_abyss_research"),
            Map.entry('B',"hk3gtl:casing_reinforced_soulium"),
            Map.entry('V',"hk3gtl:casing_abyss_research"));
    public final Kind kind;
    private final char[][][] cells;

    /** 首充设备只用原生MAX前可制作材料，避免旧魂钢机壳把HW起步锁在后段。 */
    private static final Map<Character,String> INJECTION_MATERIALS = Map.ofEntries(
            Map.entry('C',"gtceu:max_machine_casing"),
            Map.entry('F',"gtceu:solid_machine_casing"),
            Map.entry('P',"gtceu:steel_pipe_casing"),
            Map.entry('G',"gtceu:tempered_glass"),
            Map.entry('K',"gtceu:computer_heat_vent"),
            Map.entry('W',"gtceu:computer_casing"),
            Map.entry('L',"gtceu:assembly_line_grating"),
            Map.entry('R',"gtceu:steel_gearbox"),
            Map.entry('B',"gtceu:max_machine_casing"));

    public Map<Character,String> materials() {
        return kind == Kind.INJECTION ? INJECTION_MATERIALS : MATERIALS;
    }

    private Hk3LiquidLineLayout(Kind kind) {
        this.kind=kind;
        cells=new char[kind.depth][kind.height][kind.width];
        for (var slice:cells) for(var row:slice) Arrays.fill(row,'#');
    }
    public char at(int x,int y,int z) { return cells[z][y][x]; }
    public String[] aisle(int z) {
        String[] rows=new String[kind.height];
        for(int y=0;y<rows.length;y++) rows[y]=new String(cells[z][y]);
        return rows;
    }
    private void put(int x,int y,int z,char material) {
        if(x<0||x>=kind.width||y<0||y>=kind.height||z<0||z>=kind.depth)
            throw new IllegalArgumentException("结构坐标越界："+kind+" "+x+","+y+","+z);
        cells[z][y][x]=material;
    }
    private void box(int x1,int y1,int z1,int x2,int y2,int z2,char material) {
        for(int z=z1;z<=z2;z++) for(int y=y1;y<=y2;y++) for(int x=x1;x<=x2;x++) put(x,y,z,material);
    }
    /** 圆形筒体包含金属底盖、玻璃壁、分层箍圈和独立轴芯；内部保留空腔。 */
    private void vessel(int cx,int cz,int radius,int bottom,int top) {
        for(int y=bottom;y<=top;y++) for(int z=cz-radius;z<=cz+radius;z++) for(int x=cx-radius;x<=cx+radius;x++) {
            int d=(x-cx)*(x-cx)+(z-cz)*(z-cz);
            if(d>radius*radius) continue;
            if(y==bottom||y==top) put(x,y,z,'C');
            else if(d>=(radius-1)*(radius-1)) put(x,y,z,(y-bottom)%5==0?'F':'G');
            else if(x==cx&&z==cz) put(x,y,z,(y%4==0)?'L':'K');
        }
    }
    private void ring(int cx,int cz,int radius,int y,char material) {
        for(int z=cz-radius;z<=cz+radius;z++) for(int x=cx-radius;x<=cx+radius;x++) {
            int d=(x-cx)*(x-cx)+(z-cz)*(z-cz);
            if(d<=radius*radius&&d>=(radius-2)*(radius-2))put(x,y,z,material);
        }
    }
    /** 通用基础仅负责承重和通行；各机主体由下面独立的设计方法构造。 */
    private void foundation() {
        int w=kind.width,d=kind.depth;
        box(0,0,0,w-1,0,d-1,'B');
        box(1,0,1,w-2,0,d-2,'C');
        for(int z=2;z<d-2;z+=4) { put(0,1,z,'L');put(w-1,1,z,'L'); }
        for(int x=2;x<w-2;x+=4) { put(x,1,0,'R');put(x,1,d-1,'R'); }
        for(int x:new int[]{2,w-3}) for(int z:new int[]{3,d-4}) box(x,1,z,x,6,z,'F');
        for(int z:new int[]{3,d-4})box(2,6,z,w-3,6,z,'F');
        for(int x:new int[]{2,w-3})box(x,6,3,x,6,d-4,'P');

        // 下层服务脊把能源、通讯和数据层分开，避免整座机器只剩一种平面机壳。
        for (int z=2; z<d-2; z+=6) {
            put(1,1,z,'W');
            put(w-2,1,z,'W');
        }
        for (int x=2; x<w-2; x+=6) {
            put(x,1,1,'R');
            put(x,1,d-2,'R');
        }
    }

    /** 在不同工艺外形上叠加统一的 MAX 级边缘服务脊，保持四向层次语言一致。 */
    private void serviceSpines() {
        int w=kind.width,d=kind.depth;
        int upper=Math.min(kind.height-2, 10);
        for (int y=2; y<=upper; y+=4) {
            for (int yy=1; yy<y; yy++) {
                put(1,yy,1,'F');
                put(w-2,yy,1,'F');
                put(1,yy,d-2,'F');
                put(w-2,yy,d-2,'F');
            }
            put(1,y,1,'R');
            put(w-2,y,1,'R');
            put(1,y,d-2,'R');
            put(w-2,y,d-2,'R');
        }
        for (int z=3; z<d-3; z+=6) {
            if (kind.height>4) {
                put(1,1,z,'F');
                put(w-2,1,z,'F');
                put(1,2,z,'W');
                put(w-2,2,z,'W');
            }
        }
    }
    private void separation() {
        vessel(6,14,4,2,22);vessel(18,14,4,2,22);
        for(int x:new int[]{6,18}) {ring(x,14,5,8,'P');ring(x,14,5,18,'K');box(x,23,14,x,24,14,'L');}
        box(6,20,5,18,20,5,'P');box(6,7,23,18,7,23,'P');
        for(int x:new int[]{6,18})box(x,1,5,x,19,5,'F');
        for(int x:new int[]{6,18}) {box(x,3,4,x+1,10,6,'V');box(x,7,18,x,7,24,'P');}
    }
    private void stabilization() {
        vessel(10,11,5,6,28);
        for(int y:new int[]{10,18,26}) {ring(10,11,7,y,'K');ring(10,11,7,y+1,'F');}
        for(int x:new int[]{3,17})for(int z:new int[]{4,17}) {box(x,1,z,x,26,z,'P');put(x,27,z,'L');}
        box(9,29,10,11,30,12,'V');box(10,31,11,10,32,11,'L');
    }
    private void regeneration() {
        vessel(5,8,3,2,14);vessel(15,16,3,2,25);
        for(int z=6;z<=18;z+=4) {
            box(3,1,z,6,1,z,'F');box(14,1,z,17,1,z,'F');
            box(3,2,z,6,3,z,'K');box(14,2,z,17,3,z,'K');
        }
        box(5,15,8,15,15,8,'P');box(15,15,8,15,15,16,'P');
        ring(15,16,4,23,'P');box(14,26,15,16,27,17,'V');put(15,28,16,'L');
        box(3,7,20,7,8,22,'G');box(3,6,20,7,6,22,'F');
        for(int x:new int[]{3,7})box(x,1,21,x,5,21,'F');
    }
    private void blending() {
        vessel(6,9,4,2,16);vessel(18,9,4,2,16);
        vessel(12,23,5,6,17);
        box(6,12,9,6,12,23,'P');box(18,12,9,18,12,23,'P');box(6,12,23,18,12,23,'P');
        for(int z=20;z<=26;z+=3)box(6,18,z,18,18,z,'F');
        box(11,19,22,13,19,24,'V');put(12,20,23,'L');
    }
    private void calibration() {
        for(int z:new int[]{5,10,15}) {
            box(4,1,z,4,14,z,'F');box(14,1,z,14,14,z,'F');box(4,14,z,14,14,z,'K');
            box(5,5,z,5,12,z,'V');box(13,5,z,13,12,z,'V');
        }
        for(int x:new int[]{2,16}) {box(x,2,4,x,10,16,'C');box(x,7,6,x,8,14,'G');}
        box(7,5,8,11,5,12,'C');box(8,6,9,10,6,11,'L');
        for(int x:new int[]{7,11})box(x,1,10,x,4,10,'F');
        box(8,15,9,10,17,11,'P');put(9,18,10,'L');
    }
    private void concentration() {
        vessel(8,10,5,2,18);vessel(24,20,5,2,26);vessel(8,31,5,2,22);
        for(int z:new int[]{10,20,31})box(8,15,z,24,15,z,'P');
        box(24,15,10,24,15,31,'P');box(8,8,10,8,8,31,'P');
        ring(24,20,6,23,'K');ring(8,31,6,19,'K');
        box(23,27,19,25,27,21,'V');put(24,28,20,'L');
        for(int z=8;z<35;z+=4)box(29,2,z,30,12,z,'F');
    }
    private void injection() {
        // 切角双层基台、左右进料罐和三段立式注入门架共用真实逐格源。
        for (int x=0; x<kind.width; x++) for (int z=0; z<kind.depth; z++) {
            int bevel=Math.min(x,kind.width-1-x)+Math.min(z,kind.depth-1-z);
            if (bevel>=4) { put(x,0,z,'C');put(x,1,z,'C'); }
        }
        for (int x : new int[]{8,32}) {
            box(x-4,2,7,x+4,3,19,'C');
            vessel(x,13,4,4,20);
            box(x-2,21,11,x+2,22,15,'C');
            box(x-1,23,12,x+1,24,14,'K');
            box(x,10,17,x,11,26,'P');
            box(Math.min(x,20),10,26,Math.max(x,20),11,26,'P');
        }
        for (int z : new int[]{17,27,37}) {
            for (int x : new int[]{5,35}) {
                box(x-1,2,z-2,x+1,5,z+2,'C');
                box(x,6,z,x,30,z,'C');
            }
            box(5,30,z,35,30,z,'C');
            for (int x=8; x<=32; x++) for (int y=5; y<=29; y++) {
                int r=(x-20)*(x-20)+(y-17)*(y-17);
                if (r>=100 && r<=144) {
                    box(x,y,z-1,x,y,z+1,r<=115?'P':'C');
                }
            }
            box(5,17,z,8,17,z,'F');box(32,17,z,35,17,z,'F');
            box(18,2,z-1,22,5,z+1,'C');
            box(19,17,z,21,29,z,'L');
        }
        box(19,16,8,21,18,40,'G');
        box(20,17,8,20,17,40,'W');
        box(17,2,40,23,8,43,'C');
        box(18,9,41,22,26,42,'C');
        box(19,27,41,21,31,42,'W');put(20,32,41,'K');
        box(19,17,40,21,18,42,'R');
        for (int x : new int[]{2,38}) {
            box(x,2,6,x,4,40,'C');
            for (int z=7; z<=39; z+=4) box(x,5,z,x,7,z+1,'K');
        }
        // 正面同面3×3：中央真实主控，八个接口都有背壳和基础支承。
        box(17,1,0,23,5,3,'C');box(18,6,1,22,6,3,'K');
        for (int x=19; x<=21; x++) for (int y=1; y<=3; y++) put(x,y,0,'i');
        put(20,2,0,'S');
        box(19,1,4,21,3,kind.depth-1,'#');
    }
    /**
     * 规划物流接口面：保留连续的后侧检修带和前侧控制器通道。
     * 具体输入/输出方向不在布局数据中硬编码，由 Pattern 允许同类端口互换。
     */
    private void portsAndAccess() {
        int mid=kind.width/2,back=kind.depth-1;
        box(mid-1,1,0,mid+1,3,back,'#');
        box(mid-2,0,0,mid-2,0,back,'W');box(mid+2,0,0,mid+2,0,back,'W');
        put(mid,1,0,'F');put(mid,2,0,'S');
        for(int x:new int[]{2,3})put(x,2,back,'i');
        for(int x:new int[]{kind.width-4,kind.width-3})put(x,2,back,kind==Kind.INJECTION?'C':'o');
        for(int x=4;x<=7;x++)put(x,2,back,kind==Kind.CALIBRATION?'C':'u');
        for(int x=kind.width-8;x<=kind.width-5;x++)put(x,2,back,
                kind==Kind.CALIBRATION||kind==Kind.INJECTION?'C':'v');
        put(1,2,back,'h');
        // 后部物流口有连续支座，并保留中间三格通道。
        box(1,1,back,mid-2,1,back,'F');box(mid+2,1,back,kind.width-2,1,back,'F');
    }
    public static Hk3LiquidLineLayout create(Kind kind) {
        validateTechnologyPalette();
        var layout=new Hk3LiquidLineLayout(kind);
        if (kind==Kind.INJECTION) { layout.injection();return layout; }
        layout.foundation();
        switch(kind) {
            case SEPARATION -> layout.separation();case STABILIZATION -> layout.stabilization();
            case REGENERATION -> layout.regeneration();case BLENDING -> layout.blending();
            case CALIBRATION -> layout.calibration();case CONCENTRATION -> layout.concentration();
            case INJECTION -> layout.injection();
        }
        layout.serviceSpines();
        layout.portsAndAccess();return layout;
    }

    /** 防止后续新增布局误把 HV/原版装饰材料混入 MAX 结构。 */
    private static void validateTechnologyPalette() {
        if (VOLTAGE_TIER != GTValues.MAX || !"MAX".equals(TECHNOLOGY_LEVEL)) {
            throw new IllegalStateException("第一条工业线的结构科技等级必须为 MAX");
        }
        for (String id : MATERIALS.values()) {
            if (!MAX_MATERIALS.contains(id)) {
                throw new IllegalStateException("MAX 液态工业线材料不在批准白名单中：" + id);
            }
        }
    }
    public Map<Character,Integer> counts() {
        Map<Character,Integer> result=new LinkedHashMap<>();
        for(var slice:cells)for(var row:slice)for(char c:row)result.merge(c,1,Integer::sum);
        return result;
    }
}
