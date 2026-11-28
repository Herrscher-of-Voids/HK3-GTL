from pathlib import Path
from zipfile import ZipFile
from collections import defaultdict, Counter
from html import escape
from html import unescape
import base64, json, hashlib, re

ROOT=Path(__file__).resolve().parents[2]
JAR=ROOT/'deliveries/HK3GTL-1.3.12_20261127-111219Z/HK3GTL-1.3.12.jar'
TARGET=ROOT/'deliveries/0000_官方研究系统教程_1.3.12_20261128/HK3GTL-1.3.12_官方研究系统教程.html'
sha=hashlib.sha256(JAR.read_bytes()).hexdigest()
assert sha=='5088beebab61b03534430dfb1671f14cbba81b3e4cf040695661339c842ae454'
z=ZipFile(JAR); paths=set(z.namelist()); base='data/hk3gtl/research/'
def read(path):return json.loads(z.read(path))
def res(name,key):return read(base+name+'.json')[key]
def byid(rows):return {r['id']:r for r in rows}
cat=byid(res('research_catalog','topics')); exe=byid(res('research_execution','topics')); costs=byid(res('research_costs','topics'))
names=read('data/hk3gtl/guide/tutorial_names.json'); machines=names['machines']; materials=names['materials']; lang=read('assets/hk3gtl/lang/zh_cn.json'); icons=res('research_icons','icons')
ap=read(base+'approved_industrial_processes.json'); obsolete=set(ap['superseded_ids']+ap['replacement_ids']); prefixes=tuple(ap['superseded_prefixes'])
def old(k):return any(s in obsolete or s.startswith(prefixes) for s in [k]+[k[i+1:] for i,c in enumerate(k) if c=='/'])
plans=byid(p for n in sorted(paths) if n.startswith(base) and n.endswith('_processes.json') and 'approved_industrial' not in n for p in read(n)['recipes'] if not old(p['id'])); plans.update(byid(ap['recipes'])); plans={k:p for k,p in plans.items() if p['role'] not in {'I19','I20','I21','I22'}}; plans.update(byid(res('reactor_fuel_processes','reactor_recipes')))
intro_names={'gtlcore:max_sensor':'MAX 传感器','minecraft:paper':'纸','gtceu:platinum_foil':'铂箔','gtceu:helium':'氦','gtceu:grade_16_purified_water':'16 级纯化水','gtceu:graphene_dust':'石墨烯粉','gtceu:graphene_foil':'石墨烯箔','gtceu:fullerene_dust':'富勒烯粉','gtceu:carbon_nanotubes_dust':'碳纳米管粉','gtceu:fullerene_polymer_matrix_pulp':'富勒烯聚合物基体浆料','gtceu:fullerene_polymer_matrix_pulp_foil':'富勒烯聚合物基体浆料箔','gtceu:lanthanum_embedded_fullerene_dust':'镧嵌入型富勒烯粉','gtceu:platinum_dust':'铂粉','gtceu:silicon_dioxide_dust':'二氧化硅粉','gtceu:sodium_hydroxide_dust':'氢氧化钠粉','gtceu:liquid_air':'液态空气'}
def display(id):
    k=id.lstrip('#'); ns,s=k.split(':',1) if ':' in k else ('hk3gtl',k)
    if k in materials:return materials[k]
    if k in intro_names:return intro_names[k]
    for prefix in ('item','block','fluid','material','fluid_type'):
        label=lang.get(f'{prefix}.{ns}.{s}');
        if label:return label
    if ns=='material' and '/' in s:
        a,b=s.split('/'); m={'soulium':'魂钢','honkai_adaptive_alloy':'崩坏能适配合金'}.get(a,lang.get('material.hk3gtl.'+a,a));return m+{'plate':'板','foil':'箔','frame':'框架','rod':'杆','dust':'粉','wire_fine':'细线'}.get(b,b)
    return id

def image(id,cls='ico'):
    return art_tag(item_art(id),cls)

def machine(role):return f'<span class="machine"><b>{escape(role)}</b> {escape(machines.get(role,role))}</span>'
def link(t):return f'<a href="#{t}">{t} {escape(cat[t]["title"])}</a>'
def links(ts):return '、'.join(link(t) for t in dict.fromkeys(ts)) or '无前置课题'
def fmt(n):return f'{int(n):,}'
def span(label,body):return f'<div class="field"><dt>{label}</dt><dd>{body}</dd></div>'
def duration(n):return f'{fmt(n)} tick（{n/20:g} 秒）'
def tags(arr):return '；'.join(f'<span class="ingredient" title="{escape(v["tag"])}">{image(v["tag"])}{escape(display(v["tag"]))} ×{fmt(v["count"])}</span>' for v in arr)
def things(arr,fluid=False):
    return '；'.join(f'<span class="ingredient" title="{escape(v["id"])}">{image(v["id"]) if not fluid else ""}{escape(display(v["id"]))} {fmt(v["amount"])} mB</span>' if fluid else f'<span class="ingredient" title="{escape(v["id"])}">{image(v["id"])}{escape(display(v["id"]))} ×{fmt(v["count"])}</span>' for v in arr)
def make_i(id,count):return {'id':id,'count':count}
def make_f(id,amount):return {'id':id,'amount':amount}
# The registered versions of these two experiments are furnished by Java.
CNAME={'S01':'崩坏现象研究所','S02':'物质重构研究所','S03':'量子域研究所','S04':'世界维系研究所','S05':'文明认知穹顶'}
ZH='零一二三四五六七八九'
fwords='''all_fourteen_wonders 十四座奇观工程实绩
anchor_basic 基础稳定锚运行
anchor_enhanced 强化稳定锚运行
binding_test 约束测试
bounded_computation 有界演算验证
circuit_etching 电路蚀刻
circuit_packaging 电路封装
cocoon_authorization 终焉之茧的一审许可
composite_production 复合材料生产
compression_test 压缩测试
contradiction_retest 矛盾样本复核
coordinate_solution 坐标解析
cross_domain_report 跨域报告
cross_machine_order 跨机工单核验
cryogenic_test 极低温测试
crystal_growth 结晶生长
distinct_legacy_sources 不同世界泡的遗留资料
distinct_mining_routes 不同采掘航线
divine_key_assembly 神之键部件装配
drone_assembly 无人装备装配
drone_return 无人机采掘返航
electromagnetic_test 电磁测试
energy_collection 能量态采集
enhanced_beacon_signal 强化信标信号
first_mining_legacy 首份采掘遗留资料
flame_test 火焰测试
flow_test 流动测试
formal_communication 正式跨界通信
gas_collection 气态采集
gas_exhaust 尾气处理
gas_purification 气体净化
hw_injection 崩坏能注入
hw_load 崩坏能实际负载
hyperion_engineering 休伯利安工程
imaginary_anchor 虚数锚定
imaginary_observation 虚数观测
lab_four_interface 四阶研究所接口核验
large_reactor_load 大型反应堆负载
liquid_collection 首次液态采样
manual_dispatch 手动调度
manual_dispatch_multiple 多负载手动调度
medium_reactor_load 中型反应堆负载
nano_assembly 纳米装配
nano_building 纳米构件生产
nano_coating 抗侵蚀纳米包覆
nano_control 纳米控制
phase_conversion 相变释能
prefabrication 奇观构件预制
reactor_load 反应堆装料
reactor_spent_rod 乏燃料棒产出
real_capture 真实世界泡捕获
real_termination 真实世界泡终止
recovery_heat 热冷却液回收
recovery_medium 废介质回收
recovery_spent_rods 乏燃料后处理
ship_acceptance 舰船工程验收
ship_archive 舰船档案回收
ship_components 舰船部件制造
simulation_created 模拟世界泡构筑
simulation_full_chain 模拟世界泡全流程
simulation_stabilized 模拟世界泡稳定
solid_collection 固态采集
soulium_polymerization 魂钢聚合
soulium_precursor 魂钢前驱体生产
soulium_processing 魂钢精密加工
soulium_reconstruction 魂钢重构
substrate_growth 基板生长
three_domain_difference 三领域差异分析
three_domains 三领域联合分析
ultimate_reactor_load 究极反应堆负载
ultra_reactor_load 超大型反应堆负载
vessel_shell 容器壳体生产
wonder_application 奇观应用
world_maintenance 世界维系'''
flabel=dict(v.split(' ',1) for v in fwords.splitlines());flabel.update({f'wonder_W{i:02}':f'W{i:02} 奇观工程证明' for i in range(1,16)})
def factlink(k):return f'<a href="#fact-{k}">{escape(flabel[k])}</a>'
manual={
'liquid_collection':'在 I01-1 完成从液态空气采集崩坏能的整批工艺，见 RN-HED。控制器绑定的玩家须已取得奥托观察资料。',
'formal_communication':'在团队通信中完成正式联络并让系统登记结算；私人补谈或旧队历史不能代替本队的正式通信。',
'cocoon_authorization':'通过一审，取得本队的终焉之茧许可。',
'anchor_basic':'在 I36 开启连续稳定场并成功供电，让基础场至少实际运行一刻。',
'anchor_enhanced':'完成 RN-JOK，把仿制犹大的誓约放进 I36 的输入总线，供足强化场功率，等它实际运行。',
'hw_load':'让绑定付款玩家的负载机器真正工作一刻，同时成功结算正数 EU 和 HW。仅向电网充值不会留下负载记录。',
'manual_dispatch':'在 I41 为已授权负载发出手动启动指令，让它完成实际生产，再手动停止。',
'manual_dispatch_multiple':'用同一队的 I41 对两台不同负载分别完成手动启动、有效生产、停止；同一台反复启停不能替代第二台。',
'lab_four_interface':'先让四阶研究所 S04 真正完成一次正式研究（独立实验不算），再完成三领域联合分析，在 I43 运行四阶接口分析。',
'bounded_computation':'本队先取得首次液态采样。在 I32 做有界演算，再到 I43 验证该批结果。',
'contradiction_retest':'先有三领域联合分析，再依次完成矛盾来源取样、样本复测和最终复核。',
'cross_machine_order':'先建立真实的跨机交接：上一台机器的输出成为另一台机器的输入，另取得手动调度记录，最后完成跨机工单核验。',
'all_fourteen_wonders':'让同一队取得 W01 至 W14 各自的奇观工程记录。十四座都只搭好外壳、或同一种运行十四次，均不算。',
'drone_return':'在 I26 让无人机对真实世界泡完成采掘，并结算返航批次。',
'distinct_mining_routes':'用 I26 完成至少两条采掘航线，目标须为两个不同的真实世界泡。',
'first_mining_legacy':'用 I26 完成一次真正带回遗留资料的采掘。普通资源回收不算。',
'distinct_legacy_sources':'在两个不同的真实世界泡各采得遗留资料；重复采同一个目标不算。',
'ship_archive':'让 I26 的真实采掘结算带回舰船档案，不能用普通遗留资料替代。',
'real_capture':'用 I27 捕获一个已定位的真实世界泡并结算。',
'real_termination':'用 I28 终止已封存的真实世界泡并完成回收结算。',
'simulation_created':'完成 RN-SWC 后，在 I29 完成模拟世界泡构筑，等本队世界泡账本登记创建。它同时写入 RN-SWS 的独立实验；后期 W14 的有效构筑也可记入。',
'simulation_stabilized':'先用 I29 构筑，再用 I30 稳定同一个模拟世界泡，等稳定批次入账。',
'simulation_full_chain':'对同一个模拟世界泡依次完成构筑（I29）、稳定（I30）、终止回收（I31）；丢弃或换另一个目标都不能补全这条记录。',
'三域':'先取得本队三个不同批次：首次液态采样、模拟世界泡构筑、虚数观测。'}
manual['three_domains']=manual['三域']+'在 I32 完成三领域联合分析。';manual['three_domain_difference']=manual.pop('三域')+'在 I32 运行三领域差异分析。'
manual_ids={'bounded_computation':['industrial_bounded_computation','industrial_bounded_result_verification'],'contradiction_retest':['industrial_contradictory_source_sampling','industrial_contradiction_sample_retest','industrial_contradiction_review'],'cross_machine_order':['industrial_cross_machine_order_verification'],'lab_four_interface':['industrial_lab_four_interface_analysis'],'three_domains':['industrial_three_domain_analysis'],'three_domain_difference':['industrial_three_domain_difference'],'simulation_created':['industrial_simulated_world_construction'],'liquid_collection':['approved_hbv_r11']}
extra={'enhanced_beacon_signal':'I44 的强化观测除 RN-QLE 外，还要本队的一审许可。基础信标校准不能代替。','cross_domain_report':'取四座奇观的实际运行记录（W09、W11、W13、W14），再在 W09 做跨域验证。','all_fourteen_wonders':'','recovery_medium':'RN-OPR 的三份证据中，这一份按 I03 的 HBV:C02 来做。','recovery_heat':'RN-OPR 的三份证据中，这一份按 I03 的 HBV:C03 来做。','recovery_spent_rods':'RN-OPR 的三份证据中，这一份按 I05 的 HDV:P25 来做。'}

def special_plan(id,role,need,circ,ticks,items,outs,fin=(),fout=()):
 return dict(id=id,role=role,requirements=[need],circuit=circ,ticks=ticks,energy_tier=14,energy_direction='input',input_eut=2013265920,item_inputs=[make_i(*x) for x in items],item_outputs=[make_i(*x) for x in outs],fluid_inputs=[make_f(*x) for x in fin],fluid_outputs=[make_f(*x) for x in fout],title=exe['RN-DMT' if role=='I07' else 'RN-CFR']['title'])
custom={'RN-DMT':special_plan(exe['RN-DMT']['recipe'],'I07','RN-BCE',1,800,[('hk3gtl:prototype_honkai_detector',1),('hk3gtl:honkai_reference_sample',4),('hk3gtl:analyzed_honkai_sample',4),('minecraft:paper',16),('gtceu:platinum_foil',16)],[('hk3gtl:prototype_honkai_detector',1),('hk3gtl:honkai_detector_calibration_report',1)]),'RN-CFR':special_plan(exe['RN-CFR']['recipe'],'I17','RN-HFB',6,2800,[('hk3gtl:honkai_energy_crystal',128),('hk3gtl:fuel_matrix',16),('hk3gtl:concentrated_honkai_impurity',4),('hk3gtl:honkai_adapted_circuit_substrate',8)],[('hk3gtl:fuel_blending_residue',8)],[('liquid_honkai_fuel',1200),('honkai_stabilization_medium',400),('honkai_coolant',300)],[('concentrated_liquid_honkai_fuel',800),('fuel_refining_residual',300),('hot_honkai_coolant',300)])}
from io import BytesIO
from PIL import Image, ImageEnhance,ImageDraw
from functools import lru_cache
from itertools import groupby
import material_icons
E=escape

def tex(path):return Image.open(BytesIO(z.read(path))).convert('RGBA')
def cube(front,shell):
    front=front.resize((32,32),Image.Resampling.NEAREST);shell=shell.resize((32,32),Image.Resampling.NEAREST);face=Image.alpha_composite(shell,front)
    dest=Image.new('RGBA',(64,64)); px=dest.load()
    for y in range(63):
        for x in range(64):
            a=(x-32)/31; t=(y-1)/14
            if abs(a)<=1 and abs(a)<=t<=2-abs(a):
                u,v=(t+a)/2,(t-a)/2; src=shell;shade=1.06
            elif -1<=a<0 and 2+a<=t<2+a+2.35:
                u,v=a+1,(t-2-a)/2.35;src=face;shade=1
            elif 0<=a<=1 and 2-a<=t<2-a+2.35:
                u,v=a,(t-2+a)/2.35;src=shell;shade=.68
            else:continue
            r,g,b,alpha=src.getpixel((min(31,max(0,int(32*u))),min(31,max(0,int(32*v)))));px[x,y]=(min(255,int(r*shade)),min(255,int(g*shade)),min(255,int(b*shade)),alpha)
    return dest
shell=tex('assets/hk3gtl/textures/block/casings/industrial_controller_shell.png');overlays=[s for s in sorted(paths) if '/textures/block/overlay/' in s and s.endswith('/overlay_front.png') or '/textures/block/overlay/' in s and s.endswith('/overlay_front_inactive.png')];overlays+=[s for s in sorted(paths) if '/textures/block/overlay/' in s and s.endswith('/overlay_front') and s not in overlays];overlaydir='assets/hk3gtl/textures/block/overlay/'
art={};
def store(key,img):
 f=BytesIO();img.save(f,'PNG',optimize=True);art[key]=base64.b64encode(f.getvalue()).decode();return key
@lru_cache(None)
def machine_art(role):
 key='mac-'+role; stem={'I01-1':'i01','I37':'i35','H01':'hyperion_flagship'}.get(role,role.lower().replace('-','_')); alts=sorted([p for p in paths if p.startswith(overlaydir+stem) and (p[len(overlaydir)+len(stem):].startswith(('_','/'))) and p.endswith('/overlay_front.png')],key=lambda s:(('appearance_' not in s and 'unique_' not in s),len(s))); precise=[p for p in alts if re.fullmatch(re.escape(stem)+r'(?:_(?:appearance_.+|unique_.+|v\d+|puppetry_.+))?',p.split('/')[-2])];
 if not precise:return ''
 return store(key,cube(tex(precise[0]),shell))
def cube_research_computer():
 return cube(tex('assets/hk3gtl/textures/block/research_computer_r12/front.png'),tex('assets/hk3gtl/textures/block/research_computer_r12/side.png'))
@lru_cache(None)
def item_art(id):
 stem=id.split(':')[-1]; file='assets/hk3gtl/textures/item/'+stem+'.png'
 if stem=='i45_imitation_thousand_realms_train':return machine_art('I45')
 if stem=='research_point_computer':return store('it-'+stem,cube_research_computer())
 if 'circuits/' in id:
  path='data/forge/tags/items/circuits/'+id.split('/')[-1]+'.json'
  if path in paths:return item_art(read(path)['values'][0])
 external=material_icons.picture(id)
 if external:return store('it-'+re.sub('[^a-z0-9_-]','-',id),external)
 if file not in paths:
    mdl='assets/hk3gtl/models/item/'+stem+'.json'
    if mdl in paths:
     layer=read(mdl).get('textures',{}).get('layer0','');file='assets/'+layer.replace(':','/textures/')+'.png'
 if file not in paths:return ''
 im=tex(file);w,h=im.size
 if h>w:im=im.crop((0,0,w,w))
 im.thumbnail((40,40),Image.Resampling.NEAREST);return store('it-'+stem,im)
def art_tag(key,cl=''):return f'<i aria-hidden="true" class="sprite {key} {cl}"></i>' if key else ''
def machine(role):return f'<span class="machine">{art_tag(machine_art(role))}<b>{E(role)}</b> {E(machines.get(role,role))}</span>'
def image(id,cls='ico'):return art_tag(item_art(id),cls)
def uniq(xs):return list(dict.fromkeys(xs))
def fragment(s):
 parts=re.split(r'(RN-[A-Z0-9]+|(?<![A-Za-z0-9])(?:[ISWH]\d{2}(?:-\d)?)(?![A-Za-z0-9]))',s)
 return ''.join(link(x) if x in cat else machine(x) if x in machines else E(x) for x in parts)
def factid(k):return 'fact-'+k
def factlinks(keys):return '、'.join(factlink(k) for k in keys)
used=defaultdict(list);writers=defaultdict(list); successors=defaultdict(list)
for t,c in cat.items():
 for pre in c['prerequisites']:successors[pre].append(t)
for r,p in plans.items():
 for f in p.get('facts',[]):writers[f].append(p)
for t,e in exe.items():
 for f in uniq(e['facts']+plans.get(e['recipe'],{}).get('required_facts',[])):used[f].append(t)
facts=sorted(set(used)|{f for p in plans.values() for f in p.get('required_facts',[])}|set(writers)); assert all(f in flabel for f in facts)
rolesBy={m:t for t,v in exe.items() for m in v['unlocks']}

def plan_rows(p,compact=False):
 h=[];role=p['role'];h.append(span('实验设备' if not compact else '生产设备',machine(role))); circuit=p.get('circuit',0)
 h.append(span('编程电路',f'设为 <strong>{circuit}</strong> 号（不消耗）' if circuit else '未指定编号'))
 for k,label,fluid in [('item_inputs','投入物品',False),('item_catalysts','不消耗的工装',False),('fluid_inputs','输入流体',True),('item_outputs','输出物品',False),('fluid_outputs','输出流体',True)]:
    if p.get(k):h.append(span(label,things(p[k],fluid)))
 if p.get('chanced_item_outputs'):
    h.append(span('概率产物','；'.join(f'{E(display(s["id"]))} ×{s["count"]}（基础概率 {s["chance"]/100:g}%）' for s in p['chanced_item_outputs'])))
 tier=p['energy_tier']; eu=p.get('input_eut') or (480*4**(tier-3) if tier<30 else 2**63-1)
 if p.get('energy_direction')=='output':power='发电 '+fmt(p['output_eut'])+' EU/t'
 else:power=fmt(eu)+' EU/t'
 if 'input_hw' in p:power+=f' · {fmt(p["input_hw"])} HW/t'
 h.append(span('基础工况',power+' · '+duration(p['ticks'])));return ''.join(h)

def step1(t):
 e=exe[t]; c=cat[t]; r=e['recipe']; p=custom.get(t) or plans.get(r); h=[]
 if t in ('RN-ALE','RN-OPR','RN-ERM'):
    lab=e['executor'];h.append(span('在哪操作',machine(lab)+' 或更高阶普通研究所，打开课题后点「开始独立实验」。'));h.append(span('怎么完成',fragment(lang['hk3gtl.research.terminal.experiment.'+t[3:].lower()].removeprefix('独立实验：'))));h.append(span('开实验前',links(c['prerequisites'])))
    if t=='RN-ERM':h.append(span('两段实验','在同一台设施完成普通基线，再进行核心辅助段；显示已完成基线时不要换台。'))
 elif t=='RN-SWS':h.extend([span('实验设备',machine('I29')),span('怎么完成',fragment(manual['simulation_created'])),span('配方定位','<code>industrial_simulated_world_construction</code>')]);h.append(plan_rows(plans['industrial_simulated_world_construction'],True))
 else:
    if p.get('title') and p['title']!=r:h.append(span('找这条工艺',E(p['title'])))
    req=uniq(p.get('requirements',[])+(e['prerequisites'] if p.get('experiment') or t in custom else []));h.append(span('工艺开机前',links(req)));h.append(plan_rows(p));h.append(span('配方定位',E(p.get('design_uid',''))+' <code>'+E(r)+'</code>'))
    if p.get('role') in rolesBy and rolesBy[p['role']] not in req:h.append(span('设备研究',link(rolesBy[p['role']])))
    if t=='RN-HED':h.append(span('采样须知','采集塔的绑定玩家须已有奥托首信的观测资料；不用同意合作。让塔实际输出，背包样品不会补记。'))
 if e['facts'] or (p and p.get('required_facts')):h.insert(0,span('先取得记录',factlinks(uniq(e['facts']+(p.get('required_facts',[]) if p else [])))))
 return ''.join(h)

def topic(t):
 c,e,k=cat[t],exe[t],costs[t];lab=c['formalExecutor'].split()[0];dc=c['lab']; role=e['executor'] if t!='RN-SWS' else 'I29';form=machine(lab)+('：该课题仅限 W13 专属研究。' if lab=='W13' else ' 或更高阶普通研究所。'); a=step1(t); b=span('已完成课题',links(c['prerequisites']))+span('正式研究设施',form)+span('支付（二选一）',f'<strong>{fmt(k["points"])} 个人研究点</strong>，或基础材料：'+tags(k['materials']))+span('研究工况',fmt(k['eut'])+' EU/t · '+duration(k['ticks'])); after=span('研究成果',E(c['result']));
 if e['unlocks']:after+=span('解锁设备','、'.join(machine(x) for x in e['unlocks']))
 if successors[t]:after+=span('以此为前置的课题',links(successors[t]))
 return f'<details class="topic entry" id="{t}" data-stage="{dc}" data-key="{E(t+" "+c["title"]+" "+c["english"]+" "+role+" "+machines.get(role,role),quote=True)}"><summary>{image(icons[t],"topicicon")}<span class="summarytext"><small>{t}</small><strong>{E(c["title"])}</strong></span><span class="from">{E(role)} → {E(lab)}</span></summary><div class="inner"><h4>① 取得本队实验证据</h4><dl>{a}</dl><h4>② 正式开题</h4><dl>{b}</dl><h4>③ 完成以后</h4><dl>{after}</dl><a class="back" href="#lookup">↑ 回课题目录</a></div></details>'

def bookfacts(k):
 rows=writers[k]; manual_ps=[plans[r] for r in manual_ids.get(k,[]) if r in plans];blurb=manual.get(k,'在下列设备完成任意一条列出的工艺，等机器实际结算输出。')
 groups='';listed=rows if rows else manual_ps
 for role,group in groupby(sorted(listed,key=lambda p:p['role']),lambda p:p['role']):
    lines=[]
    for p in group:
      r=p['id'];name=p.get('title',r);design=p.get('design_uid','');named=E(name)+' · ' if name!=r else '';out=p.get('item_outputs',[])[:2]+p.get('fluid_outputs',[])[:1];product=' / '.join(E(display(x['id'])) for x in out);hint=' · '+product if product else '';circ=' · 电路 '+str(p['circuit'])+' 号' if p.get('circuit') else ''
      pre=('；工艺前置：'+links(p['requirements'])) if len(listed)<=6 and p['requirements'] else ''
      lines.append(f'<li>{named}<code>{E(r)}</code>{hint}{circ}'+(' · '+E(design) if design else '')+pre+'</li>')
    inside='<ul>'+''.join(lines)+'</ul>'
    groups+=f'<details class="srcgroup"><summary>{machine(role)} · {len(lines)} 条来源配方</summary>{inside}</details>' if len(lines)>8 else f'<div class="srcgroup">{machine(role)}{inside}</div>'
 usedby=('<p>相关研究：'+links(used[k])+'</p>') if used[k] else ''
 return f'<details class="record entry" id="fact-{k}"><summary><span class="summarytext"><small>{E(k)}</small><strong>{E(flabel[k])}</strong></span></summary><div class="inner"><p>{fragment(blurb)}</p>'+(f'<p>{fragment(extra[k])}</p>' if extra.get(k) else '')+groups+usedby+'</div></details>'
# The 1.3.12 lecture pages can be distributed as one file. Images and search stay offline.
centers=['S01','S02','S03','S04','S05']

def cardrow(a,b):return '<tr><th scope="row">'+a+'</th><td>'+b+'</td></tr>'
def chapter(num,title,body):return f'<section class="guide" id="{num}"><h2>{title}</h2>{body}</section>'
def tot(n):return sum(1 for c in cat.values() if c['lab']==n)
route=' <span aria-hidden="true">→</span> '.join(link(t) for t in ['RN-HED','RN-HSA','RN-LSE','RN-LES','RN-BCE'])
first=chapter('start','01　从 MAX 做完第一项研究',f'''<p class="lead">先用采集塔留下实验记录，再到研究所付款开题。两道工序在不同机器上完成。</p><ol class="steps"><li><b>确认首信和团队。</b> 让采集塔绑定的玩家取得奥托首信的观测资料。接受或拒绝合作都不影响采样；联机时先核对控制器和研究所属于同一研究队。</li><li><b>运行采集塔。</b> 在已成型的 {machine('I01-1')} 放入{image('hk3gtl:prototype_honkai_detector')}试作型崩坏能探测器（不消耗），输入 <b>1,000,000 mB 液态空气</b>，留出流体输出空间。无需编程电路。接玩家电网，以 <b>2,013,265,920 EU/t</b> 运行 600 tick；成功输出 <b>100 mB 液态崩坏能</b> 后，团队取得「首次液态采样」和本题实验记录。</li><li><b>在 {machine('S01')} 开题。</b> 选择 {link('RN-HED')}，付 <b>20 个人研究点</b>，或选择材料付款（基础报价为 MAX 级电路 ×2、钢板 ×16，实际以界面报价为准）。继续供电 600 tick，研究完成后再前往 I02。正常 20 TPS 下，采样和正式研究各用 30 秒。</li></ol><div class="note"><b>接下来五项怎么走</b><p>{route}</p><span>上面是正式课题的顺序。每个链接都列出了相应机器、投入、编号和输出，不能用上一步的样品代替下一步的生产。</span></div>''')
flow=chapter('how','02　读懂终端上的条件',f'''<div class="twocol"><div><h3>什么叫研究完成？</h3><ol><li>检查课题页的<b>正式前置</b>。上游研究必须已结算完成。</li><li>按<b>实验前置、设备、工装和工况</b>生产。多数题在机器实际输出时登记；设施实验、世界泡操作另有按钮或记录。</li><li>带材料或用个人研究点，到<b>指定研究所</b>正式开题。研究所持续供电直到结束；有凭据、能点按钮、已经付款，分别是不同进度。</li></ol></div><div><h3>三种东西别混用</h3><p><b>过程记录（fact）</b>：本队做过某项工艺或世界操作的记录；可供多个课题使用。<br><b>独立实验</b>：绑定到具体 RN 课题的实验证据。拿到材料、拥有记录，都不一定已做完本题实验。<br><b>研究点</b>：正式开题的个人支付方式，与团队证据分开。MAX 研究点计算机放入 MAX 或更高一级电路并供电；MAX 电路在设备持续加载、正常供电时每 200 tick 产 1 点。</p></div></div><h3>五阶设施与例外</h3><p>普通研究所在满足课题最低阶数时可开题。研究设施要成型、已绑定并允许工作；奇观另有本队的二审许可条件。研究所本身也可能需要先解锁；请按下列入口查看建造资格。「专用」课题另列。</p><div class="ladder">'''+''.join(f'<div>{machine(s)}<small>{tot(i)} 项 · '+('起步设施' if s not in rolesBy else '由 '+link(rolesBy[s])+' 解锁')+'</small></div>' for i,s in enumerate(centers,1))+f'''</div><p>{link('RN-WCE')} 与 {link('RN-TAA')} 在 {machine('I43')} 验证，正式开题须用 {machine('W13')}，普通五阶研究所不能代办这两项。</p><h3>付款与取回</h3><p>「使用研究点开始研究」扣付款玩家的个人余额。「使用材料开始研究」从玩家主物品栏和快捷栏的 36 格取料；材料标签允许同类替代，所示图标只是其中一种；基础数量会随研究所阶数、注视度、压制和材料敏感度调整。把材料只放在 AE 网络里，终端读不到这笔付款。需要退还的实验样件可用「领取待退材料」取回。</p>''')
trouble=chapter('stuck','03　我卡在哪一步？','<div class="scroll"><table>'+''.join(cardrow(a,b) for a,b in [
 ('采到了液态崩坏能，仍提示缺记录','查采样时塔绑定玩家的奥托首信资料、所属研究队、输出是否成功。买来的样品、从 AE 提取库存不追溯为本队实验。'+link('RN-HED')),
 ('I02 跑成了另一项实验','在课题页核对电路号、目标配方、工装和全部物品。同一编号可用于不同原料组合；先只给本次要求的物料，输出后再核对实验记录。例如初始光谱实验为 1 号，起步电路适配为 13 号。'),
 ('材料齐，但“开始独立实验”仍灰','先看是生产实验还是研究所内的实验。后者有 ALE、OPR、ERM 三类；OPR 还需本队三种真实回收批次，ERM 必须在同一台设施分两段完成。 '+links(['RN-ALE','RN-OPR','RN-ERM'])),
 ('实验做完，研究按钮仍是灰的','检查正式前置、研究所阶数与专用设施、队伍、可用工作位和付款方式。例如浓缩工艺只需 RN-HFB 就可做实验，但正式研究另要 RN-SSC、RN-FRP。 '+link('RN-CFR')),
 ('产物做过，但没有某项 fact','在下方记录索引搜索终端的英文键，核对具体配方、设备和来源。回收与世界泡操作还核对批次和目标；普通产物不能代替结算记录。'),
 ('已经下载图纸、做出控制器，为什么不算？','工程证明来自实际生产。'+factlink('all_fourteen_wonders')+' 要求 W01 至 W14 各自的工程实绩；同型控制器再多也不够。'),
 ('缺三领域，怎么查？','分别检查液态采样、模拟世界泡构筑、虚数观测，还要在 I32 完成相应分析；三批来源不能相同。 '+factlink('three_domains')),
 ('研究系统被服主关闭','先确认服务器启用研究系统。本教程的门槛和开题流程按研究系统开启编写；关闭后不需要逐题付款解锁。')])+'</table></div>')

def shellbook():
 ts=''.join(f'<section class="tier" id="tier-{i}" data-stage="{i}"><h3>第{ZH[i]}阶 <small>{tot(i)} 项</small></h3>'+''.join(topic(k) for k,c in cat.items() if c['lab']==i)+'</section>' for i in range(1,6));fs=''.join(bookfacts(k) for k in facts)
 return '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>HK3GTL 1.3.12｜官方研究系统教程</title><style>'''+(Path(__file__).with_name('style.css').read_text(encoding='utf-8-sig'))+''.join(f'.{k}{{background-image:url(data:image/png;base64,{v})}}' for k,v in art.items())+'''</style></head><body><header id="top"><div class="mast"><span>HK3GTL　/　玩家手册</span><span>正式版 1.3.12</span></div><h1>研究系统教程</h1><p>从第一份液态样本，到最后一张工程凭证。按课题找机器，按缺失记录找工艺。</p><div class="stats"><span><b>100</b> 个正式课题</span><span><b>5</b> 阶研究所</span><span><b>'''+str(len(facts))+'''</b> 条记录索引</span></div></header><nav aria-label="目录"><div><a href="#start">第一次开题</a><a href="#how">终端与设施</a><a href="#stuck">卡点排查</a><a href="#lookup">课题检索</a><a href="#facts">记录来源</a></div></nav><main>'''+first+flow+trouble+'''<section id="lookup" class="guide"><h2>04　按课题查做法</h2><p>点开课题看两套条件：第一栏在指定机器完成实验，第二栏在研究所付款开题。功率是每刻，时间是基础工时（20 tick＝1 秒）；服务器降速、运行模式和加速会改变实际用时。</p><div class="controls"><label>查课题、设备、物料或记录键<input id="tquery" type="search" placeholder="例如：RN-CFR、光谱、I32、魂钢"></label><label>最低阶数<select id="stage"><option value="">全部阶数</option>'''+''.join(f'<option value="{i}">第{ZH[i]}阶</option>' for i in range(1,6))+'''</select></label><output id="tcount" aria-live="polite">100 项</output></div>'''+ts+'''</section><section id="facts" class="guide"><h2>05　按缺失记录查来源</h2><p>输入游戏提示中的英文键或中文名称。配方来源列的是当前版本可写入该记录的工艺；同一记录有多个来源时通常任选其一。需要连续动作、指定目标或特殊结算的例外在条目首行说明。</p><div class="controls"><label>查记录、设备或配方<input id="fquery" type="search" placeholder="例如：liquid_collection、三领域、I33"></label><output id="fcount" aria-live="polite">'''+str(len(facts))+''' 项</output></div>'''+fs+'''</section><footer><b>版本依据</b><p>正式发布包 HK3GTL-1.3.12.jar。课题、数值、配方和控制器图来自该包；独立实验、世界泡、采样与工程记录另按同版运行逻辑核对。此为版本教程，不代表每条路线都已在游戏中实测。</p><p class="hash">SHA-256　'''+sha+'''</p><a href="#top">↑ 返回页首</a></footer></main><script>'''+Path(__file__).with_name('search.js').read_text(encoding='utf-8-sig')+'''</script></body></html>'''
if __name__=='__main__':
 page=shellbook().replace('凌虛晴','■■■').replace('凌虚晴','■■■');TARGET.parent.mkdir(parents=True,exist_ok=True);TARGET.write_text(page,encoding='utf-8');print(TARGET, len(page.encode()), len(cat),len(facts),len(art))
