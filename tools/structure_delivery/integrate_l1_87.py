# -*- coding: utf-8 -*-
"""修订87：接入已批准I04/I05，保留旧备注及修改前备份；同步模板、诊断入口和回归断言。"""
from pathlib import Path
from datetime import datetime
import json, re, shutil, hashlib
import nbtlib as n

ROOT=Path(__file__).resolve().parents[2]
LOG=ROOT/'logs/revision87'
STAMP=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
J='src/main/java/com/sirin/hk3gtl/'
changed=[]

def put(rel,s):
    p=ROOT/rel; backup=LOG/'backup'/rel
    if p.exists() and not backup.exists():
        backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,backup)
    p.write_text(s,encoding='utf-8');changed.append(rel)

def change(rel,edits,description):
    s=(ROOT/rel).read_text(encoding='utf-8')
    assert '正式六机接入' not in s, '已经接入，禁止重复应用'
    for old,new in edits:
        assert old in s,(rel,old[:100])
        s=s.replace(old,new,1)
    count=max([int(v) for v in re.findall(r'变更记录 #(\d+)',s)]+[0])+1
    note=f'''/**
 * 【变更记录 #{count}】{STAMP}（第 {count} 次备注 · 内测5修订87 · 正式六机接入）
 * 删除：相关正式入口对旧I04/I05结构的依赖；历史备注与旧布局数据保留。
 * 新增：{description}
 * 修改：沿获批逐格资源接入23×27×23稳定塔与27×19×23再生中心，数量与方向由正式资源确定。
 * 用途：统一成型、放置模板和诊断坐标；不改变研究费用，不启动游戏，不视为成型验收。
 */
'''
    start=s.index('@Mod.EventBusSubscriber') if '@Mod.EventBusSubscriber' in s else s.index('public ')
    s=s[:start]+note+s[start:];put(rel,s)

change(J+'common/multiblock/pattern/Hk3ApprovedArchitecture.java',[
    ('List.of("i01","i02","i03","s01")','List.of("i01","i02","i03","s01","i04","i05")')],
    '将已获负责人明确批准的I04/I05加入正式建筑键，原四台顺序保持不变。')

rel=J+'common/multiblock/pattern/Hk3LiquidLinePatterns.java'
s=(ROOT/rel).read_text(encoding='utf-8')
old=s[s.index('        if(kind==Hk3LiquidLineLayout.Kind.STABILIZATION||'):s.index("        builder.where('h'")]
change(rel,[
    ('        var layout=Hk3LiquidLineLayout.create(kind);','        if(kind==Hk3LiquidLineLayout.Kind.STABILIZATION)return Hk3ApprovedArchitecturePatterns.create(definition,"i04");\n        if(kind==Hk3LiquidLineLayout.Kind.REGENERATION)return Hk3ApprovedArchitecturePatterns.create(definition,"i05");\n        var layout=Hk3LiquidLineLayout.create(kind);'),
    (old,"        builder.where('i',itemPort(2)).where('o',itemPort(2)).where('u',fluidPort(4)).where('v',fluidPort(4));\n")],
    'I04/I05与I03同样委托统一批准结构适配器；其余四台继续原入口。')

change(J+'common/multiblock/pattern/Hk3ApprovedArchitecturePatterns.java',[
    ('case "i03" ->','case "i03", "i04", "i05" ->'),
    ('        if(!id.equals("s01")) {','        boolean loopMachine=id.equals("i04")||id.equals("i05");\n        if(!id.equals("s01")) {'),
    ('.setMinGlobalLimited(1).setPreviewCount(1);','.setMinGlobalLimited(1).setPreviewCount(loopMachine?2:1);'),
    ('setPreviewCount(id.equals("i01")?0:1)','setPreviewCount(id.equals("i01")?0:loopMachine?2:1)'),
    ('if(id.equals("i01")||id.equals("i03"))','if(id.equals("i01")||id.equals("i03")||loopMachine)'),
    ('setPreviewCount(id.equals("i03")?3:0)','setPreviewCount(loopMachine?4:id.equals("i03")?2:0)'),
    ('if(id.equals("i03"))fluidIn','if(!id.equals("i01"))fluidIn'),
    ('setPreviewCount(id.equals("i03")?3:1)','setPreviewCount(id.equals("i01")?1:4)'),
    ('if(id.equals("i03"))builder.where','if(id.equals("i03")||loopMachine)builder.where')],
    '两台各4物品槽、8流体槽、1可选并行槽；同类共享计数且每方向至少1个。I03预览改2流体进4出。')

rel=J+'common/machine/Hk3MachinesImpl.java'
s=(ROOT/rel).read_text(encoding='utf-8');edits=[]
for name in ('LIQUID_HONKAI_STABILIZATION_TOWER','STABILIZATION_MEDIUM_REGENERATION_TOWER'):
    start=s.index('        '+name+' = registrate()');end=s.index('                .register();',start)
    old=s[start:end]
    new=old.replace('.appearanceBlock(CasingBlocks.CASING_ABYSS_ENERGY)', '.appearanceBlock(() -> com.sirin.hk3gtl.common.multiblock.pattern.Hk3StructureBlocks.require("gtceu:max_machine_casing"))').replace('casingTex("casing_abyss_energy")','casingTex("industrial_controller_shell")')
    edits.append((old,new))
change(rel,edits,'两台主控改用已存在的内测5控制器外壳纹理与GT MAX外观块，保留注册ID及工作覆盖层。')

rel='src/test/java/com/sirin/hk3gtl/test/industry/ApprovedArchitectureTest.java'
change(rel,[
    ('{17,17,25}}','{17,17,25},{23,27,23},{27,19,23}}'),
    ('{1390,1006,3014,1718},portCounts={3,4,10,2}','{1390,1006,3014,1718,2260,1524},portCounts={3,4,10,2,13,13}'),
    ('            System.out.println(id+', '''            if(id.equals("i04")||id.equals("i05")) {
                int middle=data.size()[0]/2;
                for(int z=0;z<data.size()[2];z++)for(int x=middle-1;x<=middle+1;x++)for(int y=1;y<=3;y++)
                    check(!cells.containsKey(Arrays.toString(new int[]{x,y,z})),"底层检修通道堵塞："+id);
                check(data.ports().stream().filter(p->p.id().startsWith("M")).count()==4,"四个物品槽");
                check(data.ports().stream().filter(p->p.id().startsWith("F")).count()==8,"八个流体槽");
                check(data.ports().stream().filter(p->p.id().equals("P1")).count()==1,"唯一并行槽");
            }
            System.out.println(id+''')], '六台正式资源校验；新增稳定塔和再生中心尺寸、实体数量、端口及三格通道断言。')

change(J+'common/command/Hk3ApprovedStructureRuntimeCheck.java',[
    ('if (fixture==16)', 'if (fixture==com.sirin.hk3gtl.common.multiblock.pattern.Hk3ApprovedArchitecture.IDS.size()*4)'),
    ('16座四向夹具，112项成型、破坏与恢复检查','24座四向夹具，168项成型、破坏与恢复检查'),
    ('四台正式结构：四个水平朝向共112项','六台正式结构：四个水平朝向共168项'),
    ('Math.min(fixture,15)','Math.min(fixture,com.sirin.hk3gtl.common.multiblock.pattern.Hk3ApprovedArchitecture.IDS.size()*4-1)')],
    '显式游戏诊断夹具覆盖六台四向结构；仍只允许指定实例专用创造存档由玩家手动启动。')
change(J+'common/command/Hk3ApprovedStructureCommands.java',[
    ('开始四台正式结构的四向成型验收。','开始六台正式结构的四向成型验收。')],
    '放置子命令自动包含i04/i05，核验提示改为六台；不自动放置或执行验收。')

# 液态专用验收入口同样转向正式NBT，避免在新Pattern下仍放置旧尺寸夹具。
rel=J+'common/command/Hk3LiquidLineRuntimeCheck.java'
s=(ROOT/rel).read_text(encoding='utf-8')
old=s[s.index('        if(kind==Hk3LiquidLineLayout.Kind.SEPARATION) {',s.index('private static void place')):s.index('        var layout=Hk3LiquidLineLayout.create(kind);')]
new='''        if(approved!=null) {
            var rotation=switch(facing){case EAST -> net.minecraft.world.level.block.Rotation.CLOCKWISE_90;
                case SOUTH -> net.minecraft.world.level.block.Rotation.CLOCKWISE_180;
                case WEST -> net.minecraft.world.level.block.Rotation.COUNTERCLOCKWISE_90;
                default -> net.minecraft.world.level.block.Rotation.NONE;};
            controller=Hk3ApprovedStructureCommands.place(p.createCommandSourceStack(),approved,first,rotation);
            // 在同类槽之间轮换既有方块，保留输入输出数量，I03的2进4出不可反转成4进2出。
            if(swapPorts)for(String prefix:new String[]{"M","F"}) {
                var ports=com.sirin.hk3gtl.common.multiblock.pattern.Hk3ApprovedArchitecture.get(approved).ports().stream()
                        .filter(port->port.id().startsWith(prefix)).toList();
                var states=new ArrayList<BlockState>();
                for(var port:ports){int[] q=port.pos();states.add(level.getBlockState(position(kind,facing,q[0],q[1],q[2])));}
                for(int i=0;i<ports.size();i++) {
                    int[] q=ports.get(i).pos();var pos=position(kind,facing,q[0],q[1],q[2]);
                    level.setBlockAndUpdate(pos,states.get((i+1)%states.size()));
                    var part=MetaMachine.getMachine(level,pos);
                    if(part!=null)part.setFrontFacing(rotation.rotate(Direction.byName(ports.get(i).face())));
                }
            }
            machine(p).getRecipeLogic().setWorkingEnabled(false);return;
        }
'''
change(rel,[
    ('    /** 本地坐标与控制器朝向换算', '''    private static String approvedId(Hk3LiquidLineLayout.Kind kind) {
        return switch(kind){case SEPARATION -> "i03";case STABILIZATION -> "i04";case REGENERATION -> "i05";default -> null;};
    }
    /** 本地坐标与控制器朝向换算'''),
    ('if(kind==Hk3LiquidLineLayout.Kind.SEPARATION)\n', 'if(approvedId(kind)!=null)\n'),
    ('        var first=position(kind,facing,0,0,0);var last=position(kind,facing,kind.width-1,kind.height-1,kind.depth-1);', '''        String approved=approvedId(kind);
        int[] size=approved==null?new int[]{kind.width,kind.height,kind.depth}:
                com.sirin.hk3gtl.common.multiblock.pattern.Hk3ApprovedArchitecture.get(approved).size();
        var first=position(kind,facing,0,0,0);var last=position(kind,facing,size[0]-1,size[1]-1,size[2]-1);'''),
    (old,new),
    ('                    changed=kind==Hk3LiquidLineLayout.Kind.SEPARATION', '''                    String approved=approvedId(kind);
                    if(approved!=null) {
                        var data=com.sirin.hk3gtl.common.multiblock.pattern.Hk3ApprovedArchitecture.get(approved);
                        int[] q=stage==1?new int[]{8,0,8}:stage==3?
                                new int[]{data.size()[0]/2,2,5}:data.ports().get(0).pos();
                        // I03的纵向通道位于X=16，其余两台位于正中。
                        if(stage==3&&approved.equals("i03"))q=new int[]{16,2,5};
                        changed=position(kind,facing,q[0],q[1],q[2]);
                    }else changed=kind==Hk3LiquidLineLayout.Kind.SEPARATION''')],
    'I03/I04/I05使用批准模板与真实尺寸；同类端口轮换保持数量，破坏恢复夹具使用实际通道与端口。')

# I03净化已经有四种流体输出，默认放置模板同步为2进4出；外形与端口坐标不变。
p=ROOT/'src/main/resources/data/hk3gtl/structures/approved/i03.nbt'
backup=LOG/'backup'/p.relative_to(ROOT);backup.parent.mkdir(parents=True,exist_ok=True)
if not backup.exists():shutil.copy2(p,backup)
t=n.load(p);data=json.loads((ROOT/'src/main/resources/data/hk3gtl/approved_architecture/i03.json').read_text(encoding='utf-8'))
port=next(v for v in data['ports'] if v['id']=='F3')
st=n.Compound({'Name':n.String('gtceu:max_output_hatch'),'Properties':n.Compound({'facing':n.String(port['face'])})})
if st not in t['palette']:t['palette'].append(st)
for b in t['blocks']:
    if list(map(int,b['pos']))==port['pos']:b['state']=n.Int(list(t['palette']).index(st))
t.save(p,gzipped=True);changed.append(str(p.relative_to(ROOT)).replace('\\','/'))

rel='src/main/resources/assets/hk3gtl/changelog.json'
d=json.loads((ROOT/rel).read_text(encoding='utf-8'))
d['entries'][0]['changes'].append('记录补充 #87.2 '+STAMP+'：负责人批准I04/I05新结构；新增正式蓝图、NBT及Sponge文件，接入Pattern和放置命令；使用GT/GTL建材，旧布局不删除。I03默认流体口改2进4出；仍未游戏验收或部署。')
put(rel,json.dumps(d,ensure_ascii=False,indent=2)+'\n')
record=json.loads((LOG/'application.json').read_text(encoding='utf-8'))
for rel in changed:
    if not any(e['path']==rel for e in record['files']):
        backup=LOG/'backup'/rel
        record['files'].append({'path':rel,'before':hashlib.sha256(backup.read_bytes()).hexdigest() if backup.exists() else None})
for e in record['files']:e['after']=hashlib.sha256((ROOT/e['path']).read_bytes()).hexdigest()
record['structure_approval']='负责人已明确批准I04与I05所提方案；正式蓝图、Pattern、NBT及诊断入口已接入'
record['structure_integrated_at']=STAMP
(LOG/'application.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'time':STAMP,'modified':changed},ensure_ascii=False))

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
