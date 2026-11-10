# -*- coding: utf-8 -*-
"""将现行设计依据与已批准截图汇编为可离线转交的单文件HTML。"""
import base64
import hashlib
import io
import json
import re
from html import escape, unescape
from pathlib import Path
from project_paths import project_path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/HK3GTL_模组框架世界观与多方块设计资料包_DeepSeek版_20261029'
LOG = ROOT / 'logs/deepseek-design-brief-20261107'
SNAPSHOT_DATE = '2026-11-08'
BASE = 'doc/HK3GTL-内测5/03_机器结构/内测5_69座多方块逐台占地规划与比例预览_v2.html'
MAP = 'doc/HK3GTL-内测5/02_工业计划/多方块结构电压映射提案_v1.html'
TREE = 'doc/HK3GTL-内测5/02_工业计划/HK3GTL工业计划树状图_v5.html'
V6 = 'doc/HK3GTL-内测5/02_工业计划/工业网络扩展雏形_v6.json'
INDEX = 'deliveries/多方块确认归档/当前归档索引.json'
PALETTE = 'src/main/resources/data/hk3gtl/catalog/voltage_palette.json'
SUMMARY = 'logs/beta5-completion-audit-20261030/current-summary.json'
WONDER_CASINGS = dict(zip(('W' + str(i).zfill(2) for i in range(1, 16)),
                         ['WFV', 'HBV', 'HCV', 'HRV', 'HDV', 'QSV', 'QCV', 'QEV', 'QAV', 'IMV', 'ICV', 'IRV', 'IWV', 'WSV', 'CEV']))


def read(path):
    return (ROOT / path).read_text(encoding='utf-8')


def js_json(path, marker):
    return json.JSONDecoder().raw_decode(read(path).split(marker, 1)[1].lstrip())[0]


def clean(text):
    return re.sub(r'\s+', ' ', unescape(re.sub(r'<[^>]+>', ' ', text))).strip()


def li(items):
    return '<ul>' + ''.join('<li>' + escape(s) + '</li>' for s in items) + '</ul>'


def para(items):
    return ''.join('<p>' + escape(s) + '</p>' for s in items)


def image_data(path, texture=False):
    with Image.open(path) as im:
        im = im.convert('RGB')
        if texture:
            im = im.crop((0, 0, im.width, im.width))
            fmt = 'PNG'
        else:
            im.thumbnail((1250, 880))
            fmt = 'JPEG'
        buf = io.BytesIO()
        im.save(buf, fmt, **({'quality': 85, 'optimize': True} if fmt == 'JPEG' else {}))
        return 'data:image/' + ('jpeg' if fmt == 'JPEG' else 'png') + ';base64,' + base64.b64encode(buf.getvalue()).decode('ascii')


def portable_path(path):
    path = path.replace('\\', '/')
    root = ROOT.as_posix()
    if path.lower().startswith(root.lower() + '/'):
        return path[len(root) + 1:]
    if '/instances/GregTech Leisure-增强版/' in path:
        return '目标实例/' + path.split('/instances/GregTech Leisure-增强版/', 1)[1]
    return path


baseline = js_json(BASE, 'const machines=')
v6 = json.loads(read(V6))
approval = json.loads(read(INDEX))
summary = json.loads(read(SUMMARY))
scope = summary['multiblock_scope']
candidate = summary['current_work']['design_candidate']
palettes = {p['key']: p for p in json.loads(read(PALETTE))['palettes']}
nodes = {}


def walk(rows):
    for row in rows:
        nodes[row['id']] = row
        walk(row.get('children', []))


walk(js_json(TREE, 'const nodes='))
framework = json.loads((LOG / 'framework-data.json').read_text(encoding='utf-8'))
lore = json.loads((LOG / 'lore-data.json').read_text(encoding='utf-8'))
approved = {e['id'].upper(): e for e in approval['entries']}
industrial = {m['id']: m for m in v6['machines']}
catalog_titles = {m['id']: m['title'] for m in v6['catalog']}
tiers = []
mapping = {}
for row in re.findall(r'<tr>(.*?)</tr>', read(MAP), flags=re.S):
    tier_match = re.search(r'<td class="tier">([A-Z]+)<br>', row)
    if not tier_match:
        continue
    tier = tier_match.group(1)
    cells = re.findall(r'<td[^>]*>(.*?)</td>', row, flags=re.S)
    keys = re.findall(r'<span class="chip">([ISWH]\d+(?:-\d+)?)\s', row)
    rank = len(tiers)
    tiers.append({'name': tier, 'rank': rank, 'theme': clean(cells[1]), 'machines': keys})
    for key in keys:
        assert key not in mapping, key
        mapping[key] = tier
assert len(baseline) == len({r['id'] for r in baseline}) == len(mapping) == 69
assert len(tiers) == 17 and len(industrial) == 48
assert approval['approved_structure_forms'] == len(approved) == 57
assert approval['formal_structure_forms'] == scope['formal_architecture_resources'] == 52
assert scope['agreed_scope'] == 74 and scope['paused_industry_candidates'] == 14
assert approval['pending_batch']['id']=='batch-12' and approval['pending_batch']['count']==0
assert 'I43' in approved and 'I37' not in approved and 'W02' in approved
assert candidate['id'] == 'W03' and not candidate['approved']

rules = [
    ('功能先行，轮廓独立', '从机器的正式名称、实际工艺和输入输出推导造型。结合崩坏3的科幻意象、格雷的重工业构造与现实设备的承力、检修、物流、热管理。允许大胆想象，不把机器做成只换名字的雕塑。不同机器应有不同主轮廓、核心动作和空间组织。'),
    ('运行电压与外观主材分列', '普通独立新结构按运行电压映射，使用对应 hk3gtl:voltage_machine_casing_<tier> 作为主方块和最多单材；辅材、配色分布和轮廓各具特色。W01–W15及I45另按下面明确的专项选材例外。MAX使用目标实例原生材料体系，不编造自定义MAX机壳。'),
    ('十五座奇观只以美观为外观前提', '负责人2026-11-08最新决定：W01–W15外观以美观为唯一前提，不强制对应电压或律者机壳主导、最多单材。名义尺寸不得作为裁切窗口；先完整生成，再由真实构件求实际包围盒并记录原点偏移；原作者方案的相交或尺寸冲突照实保留，不自行移位、缩短、压扁或删除。旧映射仅配色参考，旧数量、材料数、体积与高度递增只统计，不作外观否决项，不硬堆材料。运行电压、供电、工艺、研究和角色身份保持，真实资源、通用接口及正式成型／性能独立验收；没有W16，H01不是第16奇观。'),
    ('I45黑金列车专项例外', 'I45运行电压仍QCV/V06；允许经目标实例真实模型与贴图核验的黑色材料主导车体及最多单材，辅以金色细线、浅银鼻部和少量冷光，QCV机壳不必主导。I44车站仍用QCV主体。该例外不推广其他机器；当前批准版本与接入状态另见目录。'),
    ('累积升阶保留旧阶段', '对需要累积扩建的系列保留低阶实体与原机壳颜色，由本阶机壳主导新增主体，并为新增内容中数量最多的单一材料；不要求超过累计全机全部通用机壳。I19–I22沿用I19的主控锚点。I01系列已经冻结，不因本条再改版。'),
    ('项目自有方块白名单', '目前只允许16种 hk3gtl:voltage_machine_casing_* 与 hk3gtl:industrial_port_casing。其他HK3GTL新增专用机壳、研究/量子/文明/舰船方块暂禁用于建筑，待负责人决定重做材质或明确批准确实必要的用途。GTCEu、GTLCore及目标整合包其他已有材料可核验后选用。不能为一个概念擅自注册新方块。'),
    ('材料少而有用，也可以多而克制', '主体、底座、骨架以格雷工业材料为主，不用海量原版混凝土、羊毛替代。不同材料各有构件职责；增加种类不代表每种都要大量铺满。允许少量铁栏杆表现钢缆，玻璃与玻璃板表现尾焰/光效；非完整方块限用途明确的细节，须核对真实模型，不能渲染为方盒。'),
    ('控制器和接口长在机器里面', '控制器与接口嵌入有真实用途、连续且有内部承接的设备表面，外侧可操作；不另立统一面板、柜墙、异风格柱子或悬空接口排。独立机器主控在宽度中线；奇数宽W的从1起算中格=(W+1)/2，从0起算X=(W-1)/2，需同时注明口径。累积反应堆系列保留I19原位锚点。'),
    ('预览占位与正式能力分开', '预览主控只放一块 minecraft:diamond_block，接口放 hk3gtl:industrial_port_casing；后者没有物品、流体、能源能力。正式Pattern需允许相应真实仓室替换并验证能力。每台及每阶控制器有呼应建筑/工艺的独立正面材质，不用默认面板换色或编号冒充；正式名称与中文提示须齐全。'),
    ('下限可以扩展，空白不算规模', '69项表中的宽×深×高是历史最低基线，不是最终尺寸、上限或实心填充要求；具体冻结版本和后来指定源文件优先。新设计逐轴检查真实实体包围盒，不能靠空白导出范围伪造。需超越下限以形成大气、精细、与命名一致的建筑。H01后来指定新舰体，旧尺寸不作为当前舰体设计目标。'),
    ('I26起按电压执行递增', '新设计按电压而非编号与所有较低电压结构比较：实体方块数、普通材料种类、真实包围盒体积及高度原则上严格更大，且视觉更复杂、华丽、细致，工艺更可读。同电压不强制排序。对应下限需从当前批准蓝图统计，不靠总表的旧小尺寸反推；不能靠无功能堆料、假边界或无意义跨度达标。W01–W15已获美观优先例外，旧数值只统计，不否决外观。'),
    ('高度例外只由负责人逐案决定', '为了构图协调可提出高度例外，记录实际高度、对照下限与理由；外部设计模型不能自行批准。不得硬加不协调的孤塔。高度例外不豁免方块数、材料种类、体积与视觉质量。其余疑似规则冲突应标明，不能静默改规则。'),
    ('现有建筑冻结与版本边界', 'I01–I25既有建筑原则上保留。I01-1至I01-4固定回到 I01-I18_控制器居中融合修订_V2_20261023，不再沿用后来的重构稿；I05既有修订保留，I06不采用高塔插滚筒的重构候选。I29用V1；I34用V2；I35用V3；I41用V3。不得用旧草稿当新设计依据。I37留到最后，旧V1–V4及后续未批准重设均不能复用。'),
    ('交付必须忠实于MC实体', '所有可读设计文档交付标准HTML，可在普通浏览器打开，不用Cursor专属TSX。结构预览使用真实Minecraft方块材质与正确模型，不是概念图替身或纯色大面。静态图、三维评审、导出的NBT/投影及正式结构须一致；正式接入应有游戏内完整结构预览，HTML不替代它。'),
    ('批准与接入各自留证', '每累计5台明确批准建筑后，按对应归档版本先接入目标游戏，再继续下一批；未回复、生成成功或HTML可看都不等于批准。归档保存独立时间戳、原件与SHA256；建筑批准、正式文件安装、游戏成型、配方与生存可达性分别记录，不互相冒充。'),
    ('全部接口通用', '不按接口位置固定物品/流体输入或输出。接口自然嵌入连续机体；正式接入时核验ADD仓室、终极样板总成等实际能力，已验证和未验证部分分别记录。外观位置不限定输入输出，预览占位不冒充真实舱室功能。'),
    ('角色必须等正式成形后出场', 'W01–W15保持十五座，其中十三座对应十三位律者；完整对应关系仍待逐台核准，不由旧名称或颜色补推。W03空之律者对应西琳，W15对应凌虛晴。只有正式Pattern确认整座成形后，才让对应实体出场并提供对话；预览、施工中或未成形不得触发。'),
    ('十周年彩蛋与ARG边界', '凌虛晴毕业建筑的十周年派对、特效动画与剧情银幕整体保留为预案，暂停开发。银幕仅彩蛋触发时临时出现，正常建筑没有黑墙或待机屏幕；结束或取消后撤去。西瓜维度ARG独立保留，不自行冻结谜底、奖励或新增毕业前置。'),
]
anti_patterns = [
    '反复使用“巨型底座＋四爪抓球”“四周工厂围住中央物体”，只更换内部名称或颜色。',
    '把几座塔直接插进滚筒；上部悬空却没有承力、悬挂或空间约束的明确设计说明。',
    '为增加材料种类把球面轮流涂成六块彩色分区，或者把每种材料都大面积铺一遍。',
    '把坐标解析、航路调度、实验验收等服务设备都画成反应堆；把世界泡仅当普通储液罐。',
    '为了规模用实心填充、无用途高塔和平台，或假定一千万到一亿方块全扫描与全区块常驻必然可行。',
]
performance = [
    '目标是电脑版与FCL手机版的实际运行内存尽量低于8GB，并能完整游玩至毕业；这是工程目标，不是已达成保证。存储文件大小、Java堆上限和游戏进程内存不是同一指标。',
    '先完成全部结构，再集中进行两平台、三场景测量：空载；全部最终建筑摆出但不强加载；沿用同布局并用FTB Chunks强加载全部覆盖区块。后两者必须分别记录实际加载区块，不能把申请数当成功数。',
    '性能工作包括AE自动下单/取料、结构检测与未加载区块处理、强加载内存、终极终端批量施工引发的检测风暴。这里的搭建工具是 gtlcore:ultimate_terminal，不是Building Gadgets 2。',
    '概念阶段优先真实有用的空心壳、桁架、舱室、管廊和模块分区；减少无用实体、方块实体与动态渲染。几何压缩、表面合并等预览技术不等于游戏世界减少方块或内存已经达标。',
    '锚点汇总、增量检测、分段施工、逻辑抽象和非活跃区块卸载可作为待验证技术方案，不能假定GTCEu/AE/FTB/终极终端已原生支持。若会改变完整结构检测/加载规则，需单独技术设计和实际验收。',
    '既定四台MAX复制系统以MX-C01–MX-C04内部需求号列入74项范围，四份外观已确认；名称、具体注册、物品白名单、配方及平衡仍待定，不把内部号冒充正式机器注册ID。它们与原69项中的MAX机器分开计数。',
    '本轮为结构设计与离线核验，没有操作图形客户端。负责人此前已授权恢复测试，实际运行另按任务安排；离线核验不计为实机测试。性能测量在全部结构完成后集中进行。',
]
facts = [
    '项目：HK3GTL（崩坏三×GregTech Leisure），当前工作版本为内测5，MAX之后的崩坏工业与文明工程扩展。是否改名正式版1.0仍需验收，不是既成决定。',
    '目标运行环境：GregTech Leisure-增强版3.0，Minecraft 1.20.1 / Forge 47.4.16 / Java 17；以增强版目标实例为准，不使用GTL十一周目替代。',
    '既定范围74项＝69项历史形态（48个工业形态、5阶研究所、15座奇观、1艘仿制休伯利安）＋4台MAX复制系统＋已有崩坏能网络注入器。69项尺寸表仅为其中历史基线，不是全范围。',
    '14个新增工业候选席位冻结，不为凑数扩建。先完成既定结构；只有逐项证明现有机器无法承接真实工艺缺口，才提出新增方案等待负责人决定。',
    '当前批准57个形态、正式结构资源52份；batch-11的四台MAX与W02建筑文件已接入，batch-12为0/5。建筑外观批准、正式资源存在、部署、成形、工艺与生存验收分别记录，不能互相代替。',
    '固定审计保留74项分母和52份资源覆盖（70.27%），原口径差距22项；另按冻结规则单列缺正式结构资源20项：I37、W02–W15、H01、四台MAX。W01整座成形验收与网络注入器结构重构另计，不能借口径差异改分母。',
    'I43 V1、I44 V2、I45 V2已经批准并接入正式结构资源；四台MAX与W02 V2外观已批准且建筑文件已接入，正式Pattern与运行验收另计。I37留到最后；本次资料更新不新增批准或接入。',
    '资料目的：让DeepSeek提出符合本项目的建筑外观方案。它可以自由设计新机器轮廓，但不能擅自改变正式名称、电压、功能、配方、剧情或既有批准版本。',
]
references = [
    ('I26', '整座I26完整全景.png', '港区物流', '葵涌货柜码头的作业秩序：岸线、龙门架、仓库、道路和稀疏运营中的彩色货柜/集卡。彩色在这里有货物分类用途；不把“全机统一涂色”当规则。'),
    ('I27', '等轴预览.png', '捕获与回收', '锁界环形回收坞把世界泡视作被约束、靠泊和处理的对象。参考的是功能可读性，后续机器不得照抄一圈厂房的轮廓。'),
    ('I34', '完整预览.png', '开穹观测', '开穹悬弦观测仪：开放空间、观测基准与悬挂关系构成识别。内部虚数树可用另行实现的贴图/动画表达，不能因此假称特效已接入游戏。'),
    ('I35', '完整预览.png', '跨界工程', '越界悬索桥的一端连接本维度，另一端穿过门界进入虚数空间；这是从“锚定联系”功能推导出的独特剪影。'),
    ('I41', '完整预览.png', '宇宙能源港', '宇宙海关与十二港约束环城：中央约束笼、外环调度港构成复合巨构。法院、监狱以及能流/熵流均为建筑隐喻；I41仍只做授权负载调度，不新增捕获、发电、宇宙囚犯或熵债规则。'),
    ('I42', '完整预览.png', '步进预制船坞', '巨构龙骨、步进工位、吊装物流和预制件形成线性工厂；可读出材料进入、构件成型、检验和出厂的过程。'),
]
reference_html = []
reference_text = []
reference_evidence = []
for key, filename, label, description in references:
    e = approved[key]
    directory = project_path(e['archive'])
    assert directory.is_dir(), directory
    path = directory / filename
    assert path.is_file(), path
    data = image_data(path)
    caption = f"{key} {e['approved_version']} · {label}"
    reference_html.append(f'<figure><img src="{data}" alt="{escape(caption)}的批准结构真实材质全景" loading="lazy"><figcaption><b>{escape(caption)}</b><p>{escape(description)}</p></figcaption></figure>')
    reference_text.append(caption + '：' + description)
    reference_evidence.append({'id': key, 'version': e['approved_version'], 'image': portable_path(str(path)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})

catalog = []
for r in baseline:
    key = r['id']
    node = nodes[key]
    m = industrial.get(key)
    if m:
        function = '；'.join(m['proposed_families'])
        boundary = m['boundary']
    else:
        function = node.get('input', '') + ' → ' + node.get('output', '')
        boundary = node.get('plan', '')
        if key == 'S05':
            boundary += '；W09与S05为独立结构，不共享一个实体。'
        if key == 'H01':
            boundary = '独立且毕业必需的仿制舰；不是第16奇观。后来指定新舰体源文件优先，不能按历史尺寸重造旧船。'
    state = '未批准新建筑'
    e = approved.get(key)
    actual = ''
    if e:
        state = f"外观已批准 {e.get('approved_version', '')}"
        state += '；正式结构资源已接入（运行逐项另验）' if e.get('formal_resource_present') else '；建筑文件已接入，正式Pattern另计' if e.get('game_files_installed') else '；等待批次接入'
        if e.get('size_xyz') and e.get('block_count'):
            w, h, d = e['size_xyz']
            actual = f"{w}×{d}×{h}；{e['block_count']:,}格"
    if key.startswith('I01-'):
        state = '冻结：主控居中融合V2（2026-10-23），停止改版'
    elif key == 'I37':
        state = '延期最后重设；旧候选不采用'
    elif key == 'W01':
        state = '已有蓝图与Pattern源码；整座搭建成形验收待完成'
    elif key == 'W03':
        state = 'V1～V6与完整边界修复候选保留；Gork原案V7已交付，W03各候选均未批准、未部署'
    if key.startswith('W'):
        boundary += '；' + ('W03实体对应西琳，不是凌虛晴。' if key=='W03' else
            'W15对应凌虛晴，正常建筑内无银幕。' if key=='W15' else '角色实体身份未逐台核准，不凭名称或配色自行指派。')
        boundary += '只有正式Pattern确认整座成形才允许对应实体出场互动。'
    group = '工业机器' if key.startswith('I') else '研究所' if key.startswith('S') else '文明奇观' if key.startswith('W') else '独立舰船'
    casing_tier = WONDER_CASINGS.get(key, mapping[key])
    casing = 'hk3gtl:voltage_machine_casing_' + casing_tier.lower() if casing_tier != 'MAX' else '目标实例原生MAX材料体系'
    casing_note = '普通结构按运行电压选主体；累积升阶系列按既有规则保留旧阶段。'
    if key in WONDER_CASINGS:
        casing = '按美观自由选用现有真实材料，原机壳映射仅参考'
        casing_note = '2026-11-08美观优先：不强制电压或律者机壳主导，不为数字递增堆料；名义尺寸不作裁切窗，按完整实体导出，原案冲突留给原作者修改；运行职责及真实资源／接口／成型验收独立保留。'
    elif key == 'I45':
        casing = '经目标实例核验的黑色车体主材；QCV机壳不要求主导或最多'
        casing_note = '负责人批准黑金原作配色选材例外；运行仍为QCV，建筑V2已批准接入，运行验收另计。'
    catalog.append({'id': key, 'title': catalog_titles.get(key, r['name']), 'tier': mapping[key], 'group': group,
                    'exterior_casing': casing, 'exterior_palette': ('可选历史参考：' if key in WONDER_CASINGS else '')+palettes[casing_tier]['name'] if casing_tier != 'MAX' and key != 'I45' else '黑金原作配色' if key == 'I45' else '原生MAX',
                    'exterior_note': casing_note,
                    'minimum': r['size'], 'function': function, 'boundary': boundary, 'state': state, 'actual': actual,
                    'candidate_actual': ''})
assert len(WONDER_CASINGS) == 15 and all(c['tier'] == mapping[c['id']] for c in catalog)
assert all('按美观自由选用' in c['exterior_casing'] for c in catalog if c['id'] in WONDER_CASINGS)
max_roles={
    'MX-C01':('以崩坏能和真实耗材制备直构介质，为后续复制工序供料。','介质、配方与数值仍待冻结，不免除成本。'),
    'MX-C02':('扫描真实样本、形成可供后续处理的物质谱系或图谱。','样本消耗、解锁规则及白名单另验，不凭扫描复制全部物品。'),
    'MX-C03':('存储和管理构建图谱，供授权重构工序读取。','不把图谱存储等同研究解锁或无成本复制。'),
    'MX-C04':('依据授权图谱，消耗直构介质、真实物料与能源执行精密重构。','物品白名单、消耗与工艺数值尚未冻结；不越级生产。')}
for identity,(function,boundary) in max_roles.items():
    e=approved[identity];meta=json.loads((project_path(e['archive'])/'manifest.json').read_text(encoding='utf-8'))
    w,h,d=e['size_xyz'];mapping[identity]='MAX';tiers[0]['machines'].append(identity)
    catalog.append(dict(id=identity,title=meta['title'],tier='MAX',group='MAX复制系统',
        exterior_casing='目标实例原生MAX材料体系',exterior_palette='原生MAX',
        exterior_note='内部需求号与暂名，不是正式机器注册ID；已确认外观不代表工艺冻结。',minimum=[],
        function=function,boundary=boundary,state=f"外观{e['approved_version']}已确认；batch-11建筑文件已接入，正式Pattern、成型与运行另验",
        actual=f"{w}×{d}×{h}；{e['block_count']:,}格",candidate_actual=''))
network_id='honkai_network_injector'
mapping[network_id]='MAX';tiers[0]['machines'].append(network_id)
catalog.append(dict(id=network_id,title='崩坏能网络注入器',tier='MAX',group='工业机器',
    exterior_casing='目标实例原生MAX材料体系',exterior_palette='原生MAX',minimum=[],
    exterior_note='已有正式机器，结构重构另计；遵守现行项目方块白名单，不复用旧专用机壳方案。',
    function='消耗燃料或结晶组合及配套材料和电力，向所属玩家的无线崩坏能网络充能。',
    boundary='配方成功完成后才结算网络能量；不凭空发电，不把充网入口当I41能源调度。',
    state='已有机器与Pattern；新的外观结构重构待完成，不计为新增机器或新批准',actual='',candidate_actual=''))
assert len(catalog)==len({c['id'] for c in catalog})==len(mapping)==scope['agreed_scope']==74

sources = []
for path in [BASE, MAP, TREE, V6, INDEX, PALETTE, SUMMARY, 'AGENTS.md', 'rule/当前多方块设计规则.md', 'rule/崩坏三-gtl (hk3gtl) 项目规则.md',
             'src/main/java/com/sirin/hk3gtl/common/machine/Hk3MachinesMaxStage.java',
             'doc/HK3GTL-内测5/09_测试发布/千万亿级巨构工程优化与四台MAX机器方案_20261028.html']:
    sources.append({'path': path, 'line': 1})
for bundle in [lore, framework]:
    for s in bundle['sections']:
        sources.extend(s['sources'])
dedup_sources = list({(portable_path(s['path']), s['line']): {'path': portable_path(s['path']), 'line': s['line']} for s in sources}.values())


def render_sections(bundle, skip=()):
    result = []
    for i, section in enumerate(bundle['sections']):
        if i in skip:
            continue
        result.append('<article class="prose-card"><h3>' + escape(section['title']) + '</h3>' + para(section.get('paragraphs', [])) + (li(section['bullets']) if section.get('bullets') else '') + '</article>')
    return ''.join(result)


def plain_sections(bundle, skip=()):
    result = []
    for i, s in enumerate(bundle['sections']):
        if i not in skip:
            result.extend([s['title']] + s.get('paragraphs', []) + s.get('bullets', []))
    return '\n\n'.join(result)


voltage_html = []
for tier in tiers:
    name = tier['name']
    tile = ''
    casing = '目标实例原生MAX机械机壳；不属于新增16种'
    if tier['rank']:
        casing = 'hk3gtl:voltage_machine_casing_' + name.lower()
        texture = ROOT / f'src/main/resources/assets/hk3gtl/textures/block/voltage_casings/{name.lower()}/casing.png'
        tile = '<img class="texture" src="' + image_data(texture, True) + '" alt="' + name + '现存机壳贴图首帧">'
    voltage_html.append('<tr><th>' + tile + '<b>' + name + '</b><small>' + ('GTL原生档' if not tier['rank'] else f"V{tier['rank']:02d} · MAX后第{tier['rank']}档") + '</small></th><td><code>' + casing + '</code><p>' + escape(tier['theme']) + '</p></td><td>' + escape('、'.join(tier['machines']) or '69项中尚无；不能自动新增候选') + '</td></tr>')

catalog_html = []
for c in catalog:
    minimum = '×'.join(map(str, c['minimum'])) if c['minimum'] else '未冻结新尺寸下限'
    actual = '<p class="muted">批准建筑实际：' + c['actual'] + '</p>' if c['actual'] else ''
    if c['candidate_actual']:actual += '<p class="muted">候选实际：' + c['candidate_actual'] + '</p>'
    size_note = '历史值；新指定舰体优先' if c['id'] == 'H01' else '历史下限；不是最终尺寸' if c['minimum'] else '不在69项历史尺寸表中；不伪造下限'
    catalog_html.append(f'<tr data-machine="{c["id"]}" data-group="{c["group"]}"><th><b>{c["id"]}</b><span class="badge">运行 {c["tier"]}</span><p>{escape(c["title"])}</p><small>外观主机壳：<code>{escape(c["exterior_casing"])}</code> · {escape(c["exterior_palette"])}</small></th><td><b>{minimum}</b><small>{size_note}</small>{actual}</td><td><p>{escape(c["function"])}</p><details><summary>工艺与选材边界</summary><p>{escape(c["boundary"])}</p><p>{escape(c["exterior_note"])}</p></details></td><td><small>{escape(c["state"])}</small><button class="pick" data-pick="{c["id"]}" type="button">生成该台设计任务</button></td></tr>')

legacy_lines = [x for x in v6['legacy'] if x.get('id', '').startswith('L')]
assert [x['id'] for x in legacy_lines] == ['L' + str(i) for i in range(1, 15)]
line_html = '<div class="line-grid">' + ''.join('<div><b>' + escape(x['id']) + '</b> ' + escape(x.get('title', x.get('name', ''))) + (' <span class="badge">提案</span>' if x.get('id') in ['L13', 'L14'] else '') + '</div>' for x in legacy_lines) + '</div>'
groups_html = '<div class="group-grid">' + ''.join('<div><b>' + escape(g['id']) + '</b><small>' + escape(g['subtitle']) + '</small></div>' for g in v6['groups']) + '</div>'

request_contract = '''你的任务是为HK3GTL设计Minecraft多方块建筑外观。当前口径：增强版3.0、批准57个形态／正式结构资源52份、既定74项范围；14个新增工业候选冻结。先阅读本资料，不套用你对官方崩坏剧情、普通GT机器或旧草稿的默认想象。
1. 先分别复述目标机器的正式名称、运行目标电压、外观主机壳、职责、上下游、禁区及版本状态。W01–W15按美观自由选材，不强制原机壳映射或数量递增，不据机壳档名改变运行电压；I45保留黑金主材例外。资料缺项标“待负责人确认”，不擅自补造世界观、材料、机器或配方。
2. 提出3种明显不同的建筑概念。每种说明核心视觉隐喻、现实工程原型、正面/侧面/俯视轮廓、工艺路线及与已有机器的区别；不要3个换色版本。
3. 推荐一种，再展开：主体形体与分区、宽深高建议、承力和悬挂关系、物流/能流/冷却/检修路线、主辅材职责、该台指定外观主机壳占据何处、控制器与接口如何嵌入设备；接口位置全部通用、不固定输入输出，所有管道须说明连接的两端设备；W01–W15外观不强制任何机壳档位，按美观选材。
4. 给出俯视分区示意和正/侧立面描述，说明玩家从远处能否认出用途，以及走近可见的5–10处具体工程细节。不要只说“科幻、宏伟、复杂”。
5. 给出可施工的Minecraft材料候选。只有本资料提供的项目方块ID可当已知准确ID；其他跨模组ID必须标“需目标实例核验”，未知方块可写外观/工程用途，不编造注册名。材质丰富不等于满屏彩虹或大面积使用每一种材料。
6. 标注最低尺寸、递增门槛和可能冲突；不能声称概念已经满足真实方块数、材料种类、游戏Pattern、性能或生存可达性。W01–W15已有美观优先例外，旧数值只统计，不作外观否决项；其他结构高度例外仍不能代替负责人批准。
7. 最后提交一段适合结构生成者执行的完整外观说明，以及可选的概念图提示词。概念图只能辅助沟通，实际交付以Minecraft真实方块模型和HTML三维预览为准。先给设计方案，不直接改代码、注册配方、重做冻结建筑或宣称批准。
8. 十五座奇观中十三座对应十三位律者，完整映射待逐台核准；W03对应西琳，W15对应凌虛晴，不从旧名称猜其余实体归属。只有正式Pattern确认整座成形后实体才出场互动；十周年派对与临时剧情银幕仍为预案，正常建筑没有银幕。西瓜维度ARG独立保留，不新增毕业门槛。'''

whole_text = '\n\n'.join([
    'HK3GTL · 模组框架、背景故事与多方块建筑设计资料包\n修订口径日期：' + SNAPSHOT_DATE + '。资料来自项目本地内测5文档、最新负责人裁定与归档索引；固定入口保留原目录名。',
    '一、先读事实与任务边界\n' + '\n'.join(facts),
    '二、背景与叙事\n' + plain_sections(lore),
    '三、系统与代码框架\n' + plain_sections(framework, (1,)),
    '四、工业网络\n' + '\n'.join(g['id'] + '：' + g['subtitle'] for g in v6['groups']) + '\n' + '\n'.join(x['id'] + '：' + x.get('title', x.get('name', '')) for x in legacy_lines) + '\nN01–N32为v6提案工艺支线，不替代L1–L12；L13/L14为新增提案，不能当作已经实现。',
    '五、运行目标电压与机壳资源\n' + '\n'.join(t['name'] + (' / 原生MAX' if not t['rank'] else f' / V{t["rank"]:02d} / hk3gtl:voltage_machine_casing_{t["name"].lower()}') + '：' + '、'.join(t['machines']) for t in tiers) + '\n上表机器分组按运行目标电压，不保证外观取同档机壳。W01–W15以美观为唯一外观前提，旧律者机壳映射仅参考，见下面逐台目录；I45用黑金主材例外。QAV是MAX后的第8个自定义档，不是从ULV起算的第8档。机壳配色请同时查看HTML内嵌真实贴图，不按档名猜颜色。',
    '六、硬性建筑规则\n' + '\n\n'.join(title + '：' + content for title, content in rules),
    '七、已批准建筑的参考逻辑（图片在HTML内嵌）\n' + '\n\n'.join(reference_text),
    '八、明确不接受的重复模板\n' + '\n'.join(anti_patterns),
    '九、运行与优化边界\n' + '\n\n'.join(performance),
    '十、既定74项结构职责目录\n尺寸一律宽×深×高；69项历史形态＋4台MAX复制系统＋已有网络注入器。尺寸与工艺方向不是游戏运行验收结论。\n' + '\n\n'.join(c['id'] + ' ' + c['title'] + '\n运行目标电压：' + c['tier'] + '\n外观主机壳：' + c['exterior_casing'] + ' · ' + c['exterior_palette'] + '\n选材边界：' + c['exterior_note'] + '\n历史下限：' + ('×'.join(map(str, c['minimum'])) if c['minimum'] else '未冻结新尺寸下限，不伪造') + ('（H01以后来指定舰体为准）' if c['id'] == 'H01' else '') + ('\n批准建筑实际：' + c['actual'] if c['actual'] else '') + ('\n候选实际：' + c['candidate_actual'] if c['candidate_actual'] else '') + '\n用途/方向：' + c['function'] + '\n边界：' + c['boundary'] + '\n状态：' + c['state'] for c in catalog),
    '十一、设计请求与交付格式\n' + request_contract,
    '资料版本不自动代表最新批准；负责人后续明确决定优先。外部模型只输出建议，审批与实际实现由项目内复核。',
])

style = '''
:root{color-scheme:dark;--bg:#0d1420;--panel:#141f2d;--border:#29394b;--text:#e9eef4;--muted:#a3b2c2;--accent:#88d8ce;--gold:#e9c782}*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:30px}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.8 system-ui,"Microsoft YaHei",sans-serif}a{color:var(--accent)}button,select,input,textarea{font:inherit}button{cursor:pointer;border:1px solid #476366;border-radius:7px;background:#1c353b;color:#e4fffa;padding:9px 15px}button:hover{background:#2b4c50}button:focus-visible,input:focus-visible,select:focus-visible,summary:focus-visible{outline:3px solid var(--gold);outline-offset:3px}button.primary{background:var(--accent);color:#10282b;font-weight:700}button.secondary{background:transparent}header,main,footer{max-width:1400px;margin:auto;padding:34px 36px}header{padding-top:62px;padding-bottom:26px}.kicker{color:var(--accent);font-size:13px;letter-spacing:3px}h1{font-size:clamp(32px,4vw,58px);line-height:1.2;margin:18px 0 22px;letter-spacing:-1px}h1 span{display:block;color:#a7b9cf;font-size:.6em;margin-top:13px;font-weight:500}h2{font-size:28px;margin:0 0 18px;line-height:1.5}h3{font-size:19px;color:#d9edea;margin:0 0 12px}p{margin:10px 0 15px}small,.muted{color:var(--muted)}small{display:block;font-size:13px;line-height:1.7}.lead{font-size:18px;max-width:1000px;color:#c5d2df}.toolbar{display:flex;gap:10px;flex-wrap:wrap;margin:24px 0}.facts{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:26px 0}.fact{border:1px solid var(--border);padding:18px 20px;border-radius:10px;background:linear-gradient(135deg,#172837,#141c29)}.fact strong{font-size:33px;color:var(--gold);display:block;line-height:1.3}.fact span{font-size:13px;color:var(--muted)}nav{border-block:1px solid var(--border);padding:14px 0;display:flex;flex-wrap:wrap;gap:12px 24px}nav a{text-decoration:none;font-size:14px}.callout{border-left:3px solid var(--gold);padding:16px 20px;background:#262820;border-radius:0 8px 8px 0}.callout p{margin:0}section{padding:34px 0 40px;border-bottom:1px solid var(--border)}.section-head{display:flex;align-items:baseline;gap:15px;flex-wrap:wrap}.section-head>span{font-size:12px;color:var(--accent);letter-spacing:2px}.prose-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}.prose-card{border:1px solid var(--border);border-radius:10px;padding:24px;background:var(--panel);break-inside:avoid}.prose-card p:last-child{margin-bottom:0}ul,ol{padding-left:23px;margin:12px 0}li{margin:8px 0}.flow{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin:26px 0}.flow>div{padding:18px 15px;border-top:3px solid var(--accent);background:#142633;border-radius:5px}.flow b{color:#d8edea}.flow p{font-size:14px;color:#b6c7d5;margin-bottom:0}.group-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:20px 0}.group-grid>div{background:#192433;border:1px solid var(--border);padding:14px;border-radius:8px}.line-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:14px}.line-grid>div{border-bottom:1px solid var(--border);padding:10px}.line-grid b{color:var(--accent);margin-right:8px}.table-wrap{overflow:auto;max-width:100%;border:1px solid var(--border);border-radius:10px;margin:20px 0}table{border-collapse:collapse;width:100%;font-size:14px}th,td{padding:15px 17px;text-align:left;border-bottom:1px solid var(--border);vertical-align:top}thead{background:#233344}thead th{white-space:nowrap}tbody tr:nth-child(2n){background:#101c29}tbody th{font-weight:400}tbody th>b{font-weight:750}td p{margin:5px 0 10px}code{font-family:Consolas,monospace;font-size:.88em;overflow-wrap:anywhere}.texture{height:48px;width:48px;image-rendering:pixelated;float:left;margin:2px 12px 3px 0}.badge{font-size:11px;display:inline-block;margin-left:8px;padding:1px 7px;border:1px solid #4e675e;border-radius:4px;color:#b3e4d3}.gallery{display:grid;grid-template-columns:1fr 1fr;gap:18px}figure{margin:0;background:var(--panel);border:1px solid var(--border);border-radius:10px;overflow:hidden;break-inside:avoid}figure img{display:block;width:100%;aspect-ratio:1.5;object-fit:contain;background:#111b2a}figcaption{padding:20px}figcaption b{color:var(--gold)}figcaption p{font-size:14px;color:#bbccda;margin-bottom:0}.rules{counter-reset:rules;display:grid;grid-template-columns:1fr 1fr;gap:15px}.rule{padding:22px;border:1px solid var(--border);border-radius:8px;background:#111e2b;break-inside:avoid}.rule h3:before{counter-increment:rules;content:counter(rules,decimal-leading-zero) " / ";color:var(--gold);font-size:15px}.rule p{font-size:14px;margin-bottom:0}.filters{display:flex;gap:10px;flex-wrap:wrap;align-items:center}input,select,textarea{border:1px solid #405369;background:#111c2a;color:var(--text);border-radius:6px;padding:9px 12px;min-width:0}input{flex:1;min-width:190px}.pick{font-size:12px;padding:6px 9px;margin-top:10px}#catalog th:first-child{min-width:200px;width:20%}#catalog td:nth-child(2){min-width:165px;width:17%}#catalog td:nth-child(3){min-width:290px;width:44%}#catalog td:nth-child(4){min-width:170px}#resultCount{font-size:13px;color:var(--muted)}summary{cursor:pointer;color:var(--accent)}details p{font-size:13px;color:#adbfce}details[open]{margin:12px 0}.prompt-box{padding:24px;background:#162331;border:1px solid var(--border);border-radius:10px}textarea{width:100%;min-height:320px;resize:vertical;font-size:14px;line-height:1.8}.prompt-label{display:block;font-size:14px;color:#c4d5df;margin:12px 0 6px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:14px/1.85 system-ui,"Microsoft YaHei",sans-serif;margin:15px 0;padding:22px;border-radius:8px;background:#0c1723}.source-list{font-size:12px;columns:2;column-gap:30px;overflow-wrap:anywhere}.source-list li{break-inside:avoid;color:#a8b9c7}.source-list code{font-size:12px}footer{font-size:13px;color:#879cac;padding-bottom:55px}#toast{position:fixed;right:22px;bottom:22px;background:#c2e8dc;color:#11352d;border:1px solid #88b6a8;border-radius:8px;padding:13px 20px;max-width:calc(100% - 44px);z-index:20;box-shadow:0 8px 35px #0009}#toast:empty{display:none}[hidden]{display:none!important}@media(max-width:850px){header,main,footer{padding:26px 20px}.facts{grid-template-columns:1fr 1fr}.prose-grid,.gallery,.rules,.line-grid{grid-template-columns:1fr}.group-grid{grid-template-columns:1fr 1fr}.flow{grid-template-columns:1fr 1fr}.flow>div:last-child{grid-column:1/-1}.source-list{columns:1}.prose-card{padding:20px}h2{font-size:25px}nav{gap:10px 17px}section{padding-block:26px}}@media print{:root{color-scheme:light;--text:#172333;--muted:#526474;--bg:white;--panel:white;--border:#bfcad1;--accent:#1d6561;--gold:#775c22}body{font-size:11px}header,main,footer{padding:10px;max-width:none}h1{font-size:30px}h2{font-size:21px}h3{font-size:15px}section{padding:15px 0}.toolbar,nav,.filters,.pick,.prompt-box,#toast{display:none}.fact,.flow>div,.group-grid>div,.rule,tbody tr:nth-child(2n),pre{background:white}.source-list{font-size:10px}.gallery{gap:10px}figure img{max-height:230px}.callout{background:#faf6ed}.table-wrap{overflow:visible}td,th{padding:7px}details{display:block}.rules p{font-size:11px}code{font-size:10px}#whole-copy{display:none}}
'''

machine_options = ''.join('<option value="' + c['id'] + '"' + (' selected' if c['id'] == 'I44' else '') + '>' + escape(c['id'] + ' · ' + c['title'] + ' · 运行 ' + c['tier'] + ' · 外观 ' + c['exterior_palette']) + '</option>' for c in catalog)
sources_html = '<ol class="source-list">' + ''.join('<li><code>' + escape(s['path']) + ':' + str(s['line']) + '</code></li>' for s in dedup_sources) + '</ol>'
runtime_layers = [
    ('运行与集成', 'Forge模组入口、注册、网络；GTCEu机器/配方/Pattern；LDLib与客户端界面。'),
    ('数据与规则', '研究合同、前置、设备权限、工艺边界；配方不能绕过首建可达性和流程分工。'),
    ('服务端事实', '玩家UUID能源、团队研究与文明成果、世界泡对象与结算回执；身份和权限分别核验。'),
    ('玩家交互', '手机通信、研究界面、文明总览、控制器与终极终端；界面读事实，不凭点击造完成记录。'),
    ('叙事与终局', '事件发现→真实实验/生产→工程成果→分级审查；个人会面与团队工程分别核验。'),
]

html = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="供DeepSeek进行HK3GTL多方块外观设计的完整独立资料：模组框架、原创背景、74项结构职责、电压机壳、已批准建筑与硬性规则。"><title>HK3GTL · 模组框架、背景故事与多方块设计资料包</title><style>' + style + '</style></head><body>'
html += '''<header><div class="kicker">HK3GTL / DESIGN BRIEF / 2026.11.07</div><h1>先理解这个文明，<br>再为它建造机器。<span>模组框架 · 背景故事 · 多方块建筑设计资料包</span></h1><p class="lead">交给 DeepSeek 的项目上下文。世界观解释“为什么建”，工业框架解释“用来做什么”，建筑规则决定“应该怎样建”。所有文字、机壳贴图与建筑参考图均内嵌在这一份 HTML 中，离线可读。</p><div class="toolbar"><button type="button" class="primary" id="copyAll">复制完整文字资料</button><button type="button" id="copyContract">复制设计请求模板</button><button type="button" class="secondary" id="print">打印 / 存为PDF</button><a href="#prompt">选一台生成设计任务 ↓</a></div><small>可直接把本HTML发给DeepSeek；或先复制完整文字资料，再把页内参考图一并提供。纯文字复制不含图片；内嵌图片是否能被对方模型读取，取决于其文件解析能力。</small><div class="facts"><div class="fact"><strong>74</strong><span>既定结构范围；14个新增工业候选冻结</span></div><div class="fact"><strong>16 + MAX</strong><span>16个自定义档与原生MAX起步</span></div><div class="fact"><strong>56 / 52</strong><span>批准形态 / 索引记录正式结构文件</span></div><div class="fact"><strong>4 / 5</strong><span>batch-11：四台MAX外观确认，未部署</span></div></div><nav aria-label="资料章节"><a href="#brief">01 项目边界</a><a href="#lore">02 背景故事</a><a href="#framework">03 底层框架</a><a href="#industry">04 工业网络</a><a href="#voltage">05 电压材质</a><a href="#references">06 批准建筑</a><a href="#rules">07 造型规则</a><a href="#performance">08 运行目标</a><a href="#catalog">09 全目录</a><a href="#prompt">10 设计任务</a><a href="#sources">11 依据</a></nav></header><main>'''
html += '<section id="brief"><div class="section-head"><span>01 / SCOPE</span><h2>这是什么项目，哪些事已经决定</h2></div>' + li(facts) + '<div class="callout"><p>这是外观设计上下文，不是新一轮全库完成度审计。描述“目标”“提案”“已有代码”“已批准建筑”和“游戏验收”时使用各自含义；不把它们混为已完成。</p></div></section>'
html += '<section id="lore"><div class="section-head"><span>02 / LORE</span><h2>新树海中的工业文明</h2></div><p class="muted">以下采用项目自身确认的二创世界观；不是对官方《崩坏3》设定的逐条考据。</p><div class="prose-grid">' + render_sections(lore) + '</div></section>'
html += '<section id="framework"><div class="section-head"><span>03 / FRAMEWORK</span><h2>机器、知识、能源与文明证据怎样连接</h2></div><div class="flow">' + ''.join('<div><b>' + title + '</b><p>' + text + '</p></div>' for title, text in runtime_layers) + '</div><div class="prose-grid">' + render_sections(framework, (1,)) + '</div></section>'
html += '<section id="industry"><div class="section-head"><span>04 / INDUSTRY</span><h2>工业链是一张网络，不是一排万能机器</h2></div><p>普通分离、化工、机加工和基础物流继续依托格雷工业。HK3专用设施负责含崩坏能的特殊介质、纳米魂钢、仿制核心、世界泡和空间工程。生产、分析、研究、任务调度、工程验收有不同职责，不把所有设备硬凑成普通物品配方机。</p>' + groups_html + '<h3>保留的主线与新增提案</h3>' + line_html + '<p class="muted">v6的N01–N32是上述网络的支撑工艺支线，不取代L1–L12；L13/L14、支线产品和新工艺仍属扩展提案，不能据此宣称已注册全部配方。</p></section>'
html += '<section id="voltage"><div class="section-head"><span>05 / VOLTAGE</span><h2>运行目标电压与真实机壳资源</h2></div><p>下表机器分组沿用负责人授权的运行目标电压映射，机壳贴图列是现有材料资源。W01–W15的外观主机壳按各自律者身份选择，逐台对应见全目录；不按运行档强制同色。I45另保留黑金车体主材例外。QAV是MAX后的第8个自定义电压；辅材与空间轮廓仍须各有特色。贴图取本地现存资源首帧，屏幕光照会影响观感；不按档名推测配色。</p><div class="table-wrap"><table id="voltages"><thead><tr><th>档名 / 材料贴图</th><th>已有机壳资源 / 工业主题</th><th>按运行目标电压分组的历史形态</th></tr></thead><tbody>' + ''.join(voltage_html) + '</tbody></table></div><small>运行目标映射并不自动证明正式Controller tier、配方耗能、材料首建可达性或运行合同已验收。奇观换用其他档名机壳属于负责人批准的选材例外，不是运行改档。I16按HDV映射，设计要求最迟HDV阶段可建，不能被后期材料反锁。</small></section>'
html += '<section id="references"><div class="section-head"><span>06 / APPROVED REFERENCES</span><h2>已经被认可的，不同机器的不同样子</h2></div><p>以下六张均取自对应明确批准归档的真实方块预览。学习工艺组织、材质和独立剪影；不要复制一个外壳套在所有机器上。图片已内嵌，转发HTML不会丢图。</p><div class="gallery">' + ''.join(reference_html) + '</div></section>'
html += '<section id="rules"><div class="section-head"><span>07 / DESIGN RULES</span><h2>可以大胆想象，但必须守住这些边界</h2></div><div class="rules">' + ''.join('<article class="rule"><h3>' + escape(title) + '</h3><p>' + escape(content) + '</p></article>' for title, content in rules) + '</div><h3 style="margin-top:28px">负责人已经否决的重复套路</h3>' + li(anti_patterns) + '</section>'
html += '<section id="performance"><div class="section-head"><span>08 / RUNTIME TARGETS</span><h2>巨构要能建，也要能运行</h2></div>' + li(performance) + '<div class="callout"><p>外观提案可以解释如何减少无意义实体和常驻逻辑，但不得为节省性能擅自缩小已批准建筑、违反尺寸基线，或声称亿级结构在8GB内已获验证。</p></div></section>'
html += '<section id="catalog"><div class="section-head"><span>09 / MACHINE CATALOG</span><h2>既定74项结构职责目录</h2></div><p>列出的工艺家族与服务方向供造型推导，精确参数仍以正式合同和后续确认优先。尺寸统一为<strong>宽×深×高</strong>；历史下限不等于最终规模，也不能覆盖后来的冻结/指定原稿。已批准建筑同时列出实际体量，防止把旧小尺寸误当现行版本。</p><div class="filters"><label for="search">查找</label><input id="search" type="search" placeholder="编号、名称、电压或用途" aria-label="按编号名称电压用途查找"><select id="group" aria-label="筛选机器种类"><option value="">全部种类</option><option>工业机器</option><option>研究所</option><option>文明奇观</option><option>独立舰船</option><option>MAX复制系统</option></select><span id="resultCount">74 / 74 项</span></div><div class="table-wrap"><table><thead><tr><th>编号 / 名称 / 电压</th><th>历史下限 W×D×H</th><th>用途与工艺方向</th><th>外观版本状态</th></tr></thead><tbody>' + ''.join(catalog_html) + '</tbody></table></div></section>'
html += '<section id="prompt"><div class="section-head"><span>10 / HANDOFF PROMPT</span><h2>选定机器，再请它提出三个不同概念</h2></div><p>先把完整资料交给DeepSeek，再复制这里的单台任务。已有建筑默认仅供参考；选中已批准或延期机器并不授权重构。</p><div class="prompt-box"><label class="prompt-label" for="machine">目标机器（默认示例I44，不代表本轮启动制作）</label><select id="machine" style="width:100%">' + machine_options + '</select><label class="prompt-label" for="targetNotes">这次额外偏好（可留空）</label><input id="targetNotes" style="width:100%" placeholder="例如：像大型通信天线与空间灯塔；避免环城轮廓"><label class="prompt-label" for="machinePrompt">单台设计任务</label><textarea id="machinePrompt" readonly aria-label="可复制的单台设计任务"></textarea><div class="toolbar"><button id="copyMachine" type="button" class="primary">复制这台设计任务</button><button type="button" id="selectPrompt" class="secondary">选中文字</button></div></div><details><summary>展开通用设计请求与输出格式</summary><pre id="contract">' + escape(request_contract) + '</pre></details><details id="whole-copy"><summary>展开完整文字资料（复制失败时可手动全选）</summary><pre id="fullText">' + escape(whole_text) + '</pre></details></section>'
html += '<section id="sources"><div class="section-head"><span>11 / PROVENANCE</span><h2>资料来源与快照边界</h2></div><p>汇编时间：' + SNAPSHOT_DATE + '（按客户端America/New_York日期）。修订口径日期2026-11-08；固定入口保留20261029目录名。以当前项目规则及负责人较新明确裁定覆盖旧稿；工业树只提取职责，不搬用旧占位外形。以下为项目相对路径与一基行号；“目标实例/…jar!/…”表示实际安装归档内文本。资料本身可独立阅读，无需这些路径存在于接收者电脑。</p>' + sources_html + '</section></main><footer>HK3GTL 内测5 · 提供外部建筑设计模型的资料快照。原文背景、已确认决定与设计建议已分开表述；本资料不新增批准、不改动游戏实例，也不提供未经测量的完成率或性能承诺。</footer><div id="toast" role="status" aria-live="polite"></div>'
script = r'''
const machines=__DATA__;
const contract=document.getElementById('contract').textContent;
const byId=new Map(machines.map(m=>[m.id,m]));
function notify(text){document.getElementById('toast').textContent=text;}
async function copyText(text){
  try{await navigator.clipboard.writeText(text);notify('已复制，可粘贴给DeepSeek。');}
  catch(e){const tmp=document.createElement('textarea');tmp.value=text;tmp.style.position='fixed';tmp.style.opacity='0';document.body.append(tmp);tmp.select();const ok=document.execCommand('copy');tmp.remove();notify(ok?'已复制，可粘贴给DeepSeek。':'浏览器未允许复制。请展开完整文字资料，手动选中复制。');}
}
function updatePrompt(){
  const m=byId.get(document.getElementById('machine').value);
  const notes=document.getElementById('targetNotes').value.trim();
  document.getElementById('machinePrompt').value=[
    '请在已提供的《HK3GTL模组框架、背景故事与多方块设计资料包》范围内进行外观概念设计。口径日期2026-11-08：增强版3.0，批准57／正式52，既定74项；14个新增工业候选冻结。',
    '目标：'+m.id+' '+m.title+'；运行目标电压：'+m.tier+'。',
    '外观主机壳：'+m.exterior_casing+'；配色：'+m.exterior_palette+'。',
    '选材边界：'+m.exterior_note,
    '职责/方向：'+m.function,'功能边界：'+m.boundary,
    '历史尺寸下限（宽×深×高）：'+(m.minimum.length?m.minimum.join('×'):'未冻结新尺寸下限，不伪造')+'；这不是最终尺寸或上限。'+(m.id==='H01'?'H01另有负责人指定新舰体，不以历史尺寸重造。':''),
    m.actual?'已批准建筑实际体量参考：'+m.actual+'。':m.candidate_actual?'待审候选实际体量：'+m.candidate_actual+'。':'尚无该台批准建筑的体量依据，不编造方块数量。',
    '当前状态：'+m.state+'。已批准/冻结/延期项目仅作参考，未获另行明确授权不得重做；若本次确实要改版，先指出需要负责人决定。',
    '主体按本台上述外观主机壳与已批准选材例外制作；接口嵌入有用途的设备本体，不按位置固定输入输出；所有管道说明两端连接，预览钻石主控＋工业接口占位；保持真实MC材质，避免四爪抓球、重复环城和强凑高塔。普通工业结构I26起仍按运行电压与全部低阶结构核验递增；W01–W15已获美观优先例外，旧数值只统计，不为达标堆料；其他新例外不可自行批准。',
    notes?'本次额外偏好：'+notes:'',contract
  ].filter(Boolean).join('\n\n');
}
document.getElementById('machine').addEventListener('change',updatePrompt);
document.getElementById('targetNotes').addEventListener('input',updatePrompt);
document.getElementById('copyMachine').addEventListener('click',()=>copyText(document.getElementById('machinePrompt').value));
document.getElementById('selectPrompt').addEventListener('click',()=>{document.getElementById('machinePrompt').select();});
document.getElementById('copyAll').addEventListener('click',()=>copyText(document.getElementById('fullText').textContent));
document.getElementById('copyContract').addEventListener('click',()=>copyText(contract));
document.getElementById('print').addEventListener('click',()=>window.print());
document.querySelectorAll('[data-pick]').forEach(btn=>btn.addEventListener('click',()=>{document.getElementById('machine').value=btn.dataset.pick;updatePrompt();document.getElementById('prompt').scrollIntoView();document.getElementById('machine').focus({preventScroll:true});}));
function filter(){
  const q=document.getElementById('search').value.trim().toLowerCase();
  const exactId=machines.some(m=>m.id.toLowerCase()===q);
  const group=document.getElementById('group').value;let count=0;
  document.querySelectorAll('[data-machine]').forEach(row=>{const match=exactId?row.dataset.machine.toLowerCase()===q:row.textContent.toLowerCase().includes(q);row.hidden=!!((q&&!match)||(group&&row.dataset.group!==group));if(!row.hidden)count++;});
  document.getElementById('resultCount').textContent=count+' / 74 项';
}
document.getElementById('search').addEventListener('input',filter);
document.getElementById('group').addEventListener('change',filter);
updatePrompt();window.BRIEF_READY=true;
'''
script = script.replace('__DATA__', json.dumps(catalog, ensure_ascii=False).replace('<', '\\u003c'))
html += '<script>' + script + '</script></body></html>'
assert len(catalog) == 74 and html.count('data-machine=') == 74
assert html.count('class="texture"') == 16 and len(reference_evidence) == 6
assert 'C:/Users/OWNER' not in html and 'C:\\Users\\OWNER' not in html
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'index.html').write_bytes(html.encode('utf-8'))
evidence = {
    'created_at': SNAPSHOT_DATE, 'purpose': '外部模型多方块外观设计资料；非新批准或实装',
    'output': str((OUT / 'index.html').relative_to(ROOT)).replace('\\', '/'),
    'counts': {'catalog': len(catalog), 'industrial': len(industrial), 'tiers_including_native_MAX': len(tiers), 'custom_casing_tiles': 16, 'embedded_approved_images': 6,
               'approved_forms': len(approved), 'formal_structure_files_per_index': approval['formal_structure_forms'], 'pending_batch': approval['pending_batch']['count'], 'agreed_scope': 74, 'historical_baseline': 69},
    'source_snapshot': [{'path': p, 'sha256': hashlib.sha256((ROOT / p).read_bytes()).hexdigest()} for p in [BASE, MAP, TREE, V6, INDEX, PALETTE, SUMMARY, 'rule/当前多方块设计规则.md', 'AGENTS.md', 'logs/deepseek-design-brief-20261107/lore-data.json', 'logs/deepseek-design-brief-20261107/framework-data.json']],
    'reference_images': reference_evidence,
    'text_characters': len(whole_text), 'html_bytes': len(html.encode('utf-8')),
    'html_sha256': hashlib.sha256(html.encode('utf-8')).hexdigest(),
    'scope': '仅同步设计资料；批准57／正式52、74项范围与角色规则。W02 V2外观已批准，建筑文件已接入；I37最后；未改批准、审计分数、游戏与实例。',
}
(LOG / 'build-evidence.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'output': evidence['output'], 'html_bytes': evidence['html_bytes'], 'text_characters': len(whole_text), 'counts': evidence['counts']}, ensure_ascii=False))
