# -*- coding: utf-8 -*-
"""从36份当前正式逐格蓝图制作控制器候选，不写正式资源或实例。

变更记录 #1 · 2026-10-26：保留四套既有控制器，另制32套三状态候选；
图案来自对应批准几何的正交投影、深度棱线和真实接口节点，不以换色/编号区分。
"""
from pathlib import Path
from project_paths import project_path
from datetime import datetime, timezone, timedelta
import hashlib
import html
import json
import shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'logs/controller-texture-candidates-20261026'
ASSETS = ROOT / 'src/main/resources/assets/hk3gtl'
LAYOUTS = ROOT / 'src/main/resources/data/hk3gtl/approved_architecture'
METADATA = ROOT / 'src/main/resources/data/hk3gtl/structures/approved'
PRESERVED = {'i01': 'i01_v2', 'i02': 'i02_v2', 'i03': 'i03_v2', 's01': 's01_v2'}
KEYS = ['i01', 'i01_2', 'i01_3', 'i01_4'] + [f'i{i:02}' for i in range(2, 29)] + [f's{i:02}' for i in range(1, 6)]
NAMES = {
    'i01': '一阶崩坏能采集塔', 'i01_2': '二阶崩坏能采集塔', 'i01_3': '三阶崩坏能采集塔',
    'i01_4': '四阶崩坏能采集塔', 'i02': '崩坏能样本光谱分析阵列', 'i03': '液态崩坏能分馏中心',
    'i04': '液态崩坏能稳定塔', 'i05': '稳定介质再生塔', 'i06': '崩坏能燃料调配厂',
    'i07': '崩坏能探测器校准台', 'i08': '仿制律者核心结晶室', 'i09': '魂钢前驱体混合釜',
    'i10': '纳米基础单元合成器', 'i11': '纳米机器人装配阵列', 'i12': '纳米自组织编程舱',
    'i13': '崩坏抗性包覆阵列', 'i14': '魂钢聚合压铸机', 'i15': '魂钢重构退火炉',
    'i16': '魂钢精密加工中心', 'i17': '浓缩崩坏能燃料精制厂', 'i18': '崩坏能燃料棒封装阵列',
    'i19': '小型崩坏能反应堆', 'i20': '中型崩坏能反应堆', 'i21': '大型崩坏能反应堆',
    'i22': '究极崩坏能反应堆', 'i23': '崩坏能相变释能机', 'i24': '量子异常观测阵列',
    'i25': '世界泡坐标解析中心', 'i26': '世界泡无人采掘调度台', 'i27': '世界泡整体捕获阵列',
    'i28': '真实世界泡终止回收机', 's01': '崩坏能现象研究所', 's02': '物质重构研究所',
    's03': '量子域研究所', 's04': '世界维系研究所', 's05': '文明认知穹顶',
}
MOTIFS = {
    'i01': '沿用雷达采集标志', 'i01_2': '保留采集塔轮廓，显示新增晶化及后处理建筑',
    'i01_3': '显示气态阶段的宽阔新增厂区与集流核心', 'i01_4': '显示能量态阶段的整体扩建轮廓',
    'i02': '沿用棱镜分光标志', 'i03': '沿用分馏塔与分流标志', 'i04': '稳定塔的竖直主体与侧向回路',
    'i05': 'V5塔冠反应段、左右回收塔与原位主控', 'i06': '调配筒体与分区处理设备',
    'i07': '校准主体、支架与测量工位', 'i08': '结晶主体及外围控制构架',
    'i09': '混合釜及旁置处理塔', 'i10': '多级合成筒与并列支撑', 'i11': '并列装配通道和上部总梁',
    'i12': '中央编程构架和两侧展开结构', 'i13': '实际包覆处理设备与输送结构',
    'i14': '压铸主梁、中心加工区与承压结构', 'i15': '退火主体与外侧换热区',
    'i16': '精密处理主体及分区加工设备', 'i17': '精制高塔与附属处理区',
    'i18': '实际封装总成及多通道作业线', 'i19': '单塔反应堆、环形堆区与附属厂房',
    'i20': '双岛扩建堆区及检修厂房', 'i21': '三回路联合厂区', 'i22': '四堆复合场区',
    'i23': 'V8双锥束流炉与外侧工艺构架', 'i24': '三碟长基线观测阵列',
    'i25': '截角二十面体世界泡壳与一体研究底座', 'i26': 'V5港区岸桥、左右对称作业面与疏散货场',
    'i27': '锁界回收坞的环形主体', 'i28': '双闸断界结构与归流炉', 's01': '沿用研究节点标志',
    's02': '第二阶段累计研究院区', 's03': '第三阶段量子研究扩建',
    's04': '第四阶段世界维系院区', 's05': '第五阶段文明认知穹顶和完整院区',
}
STATE_SUFFIX = {'idle': '', 'active': '_active', 'paused': '_paused'}
STATE_CN = {'idle': '空闲', 'active': '运行', 'paused': '暂停'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def current_overlay(key):
    if key in ('i01', 'i01_2', 'i01_3', 'i01_4'):
        return 'i01_v2'
    if key.startswith('s'):
        return 's01_v2'
    return PRESERVED.get(key, 'default_set')


def projection(pos):
    p = np.asarray(pos, dtype=np.float32)
    return np.column_stack(((p[:, 0] - p[:, 2]) * .8660254,
                            (p[:, 0] + p[:, 2]) * .42 - p[:, 1],
                            p[:, 0] + p[:, 2] + p[:, 1] * .35))


def projected_geometry(points, width, height, margin=1):
    uv = projection(points)
    lo, hi = uv[:, :2].min(axis=0), uv[:, :2].max(axis=0)
    scale = min((width - 1 - margin * 2) / max(hi[0] - lo[0], 1),
                (height - 1 - margin * 2) / max(hi[1] - lo[1], 1))
    offset = np.array([(width - 1 - (hi[0] - lo[0]) * scale) / 2,
                       (height - 1 - (hi[1] - lo[1]) * scale) / 2])
    pix = np.rint((uv[:, :2] - lo) * scale + offset).astype(np.int32)
    depth = np.full((height, width), -np.inf, dtype=np.float32)
    np.maximum.at(depth, (pix[:, 1], pix[:, 0]), uv[:, 2])
    valid = np.isfinite(depth)
    edge = np.zeros_like(valid)
    ridges = np.zeros_like(valid)
    threshold = max((uv[:, 2].max() - uv[:, 2].min()) * .035, 1)
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        neighbour = np.roll(valid, (dy, dx), (0, 1))
        nd = np.roll(depth, (dy, dx), (0, 1))
        edge |= valid & ~neighbour
        delta = np.zeros_like(depth)
        np.subtract(depth, nd, out=delta, where=valid & neighbour)
        ridges |= valid & neighbour & (np.abs(delta) > threshold)
    return depth, valid, edge, ridges, lo, scale, offset


def geometry_image(points, path):
    depth, valid, edge, ridges, *_ = projected_geometry(points, 600, 420, 12)
    rgb = np.full((420, 600, 3), (9, 20, 33), dtype=np.uint8)
    values = depth[valid]
    t = (values - values.min()) / max(float(values.max() - values.min()), 1)
    rgb[valid] = np.stack((35 + t * 28, 80 + t * 57, 102 + t * 64), axis=1).astype(np.uint8)
    rgb[ridges] = (103, 186, 199)
    rgb[edge] = (164, 223, 226)
    Image.fromarray(rgb).save(path)


def candidate_face(points, ports, controller, state):
    source = ASSETS / f'textures/block/overlay/i01_v2/overlay_front{STATE_SUFFIX[state]}.png'
    im = Image.open(source).convert('RGBA')
    d = ImageDraw.Draw(im)
    d.rectangle((9, 9, 54, 49), fill='#0b1427')
    depth, valid, edge, ridges, lo, scale, offset = projected_geometry(points, 44, 37)
    palettes = {
        'idle': ((25, 48, 64, 255), (63, 124, 146, 255), (99, 194, 207, 255)),
        'active': ((31, 75, 88, 255), (81, 185, 191, 255), (161, 255, 242, 255)),
        'paused': ((48, 44, 44, 255), (136, 113, 70, 255), (226, 183, 100, 255)),
    }
    fill, inner, outer = palettes[state]
    px = im.load()
    for y, x in zip(*np.nonzero(valid)):
        px[int(x) + 10, int(y) + 11] = outer if edge[y, x] else inner if ridges[y, x] else fill
    port_positions = []
    for p in ports:
        if not isinstance(p, dict) or not isinstance(p.get('pos'), list):
            continue
        port_positions.append(p['pos'])
    if port_positions:
        pp = projection(port_positions)
        xy = np.rint((pp[:, :2] - lo) * scale + offset).astype(np.int32)
        for x, y in xy:
            if 0 <= x < 44 and 0 <= y < 37:
                px[int(x) + 10, int(y) + 11] = (202, 222, 222, 255) if state != 'paused' else (215, 177, 103, 255)
    cp = projection([controller])[0]
    x, y = np.rint((cp[:2] - lo) * scale + offset).astype(int)
    if 0 <= x < 44 and 0 <= y < 37:
        px[int(x) + 10, int(y) + 11] = (230, 196, 123, 255)
    # 状态标记与主体图案分离，机器身份只由轮廓和棱线决定。
    d.rectangle((9, 54, 54, 59), fill='#38344e')
    for i, x in enumerate((10, 19, 28, 37, 46)):
        d.rectangle((x, 55, x + 5, 58), fill=outer if state == 'active' or i < 2 else '#30526e')
    if state == 'paused':
        d.rectangle((48, 10, 49, 15), fill='#e3bb65')
        d.rectangle((52, 10, 53, 15), fill='#e3bb65')
    return im, hashlib.sha256(np.packbits(valid).tobytes() + np.packbits(ridges).tobytes()).hexdigest()


def find_review(key, metadata, archive_index):
    candidates = [metadata.get('source_snapshot'), archive_index.get(key, {}).get('archive')]
    for candidate in candidates:
        if candidate:
            folder = project_path(candidate)
            if folder.is_dir():
                pages = sorted(folder.rglob('三维评审.html'))
                if pages:
                    return pages[0].as_uri()
    return None


def make_sheet(entries):
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 20)
    small = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 16)
    sheet = Image.new('RGB', (1920, 2680), '#101827')
    draw = ImageDraw.Draw(sheet)
    draw.text((30, 16), '36台批准建筑 · 独立控制器候选总览（4套保留 / 32套待审，未接入正式资源）', font=font, fill='#dce9f5')
    for n, entry in enumerate(entries):
        col, row = n % 4, n // 4
        x, y = 20 + col * 475, 65 + row * 289
        draw.rounded_rectangle((x, y, x + 460, y + 274), 10, fill='#17243a', outline='#35485e')
        draw.text((x + 12, y + 8), entry['label'] + '  ' + ('保留' if entry['preserved'] else '候选'), font=font, fill='#a1e5e4')
        draw.text((x + 12, y + 36), entry['name'], font=small, fill='#e0e5ed')
        for i, state in enumerate(STATE_SUFFIX):
            p = OUT / entry['candidate'][state]['path']
            sheet.paste(Image.open(p).convert('RGB').resize((128, 128), Image.Resampling.NEAREST), (x + 16 + i * 148, y + 69))
            draw.text((x + 58 + i * 148, y + 204), STATE_CN[state], font=small, fill='#9cb0c5')
        draw.text((x + 12, y + 240), f"实际蓝图 {entry['size_xyz'][0]}×{entry['size_xyz'][1]}×{entry['size_xyz'][2]} · {entry['blocks']:,}方块", font=small, fill='#9cb0c5')
    sheet.save(OUT / 'overview-36.png')


def make_html(manifest):
    data = json.dumps(manifest, ensure_ascii=False).replace('</', '<\\/')
    page = r'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>36台独立控制器候选审阅</title>
<style>body{margin:0;background:#0d1523;color:#e4edf4;font:15px/1.6 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1580px;margin:auto;padding:28px}h1{font-size:28px}p{max-width:1200px}.bar{position:sticky;top:0;background:#0d1523ee;padding:12px 0;z-index:2;display:flex;gap:12px;flex-wrap:wrap}.bar input,.bar select{padding:10px;background:#1c2a3f;border:1px solid #50657d;color:white;border-radius:6px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:20px}.card{background:#17243a;border:1px solid #344960;border-radius:10px;padding:16px;scroll-margin-top:80px}.card h2{font-size:18px;margin:0 0 6px}.muted{color:#a6b8c9}.preserved{color:#a9dcaf}.pending{color:#f1cc85}.geometry{display:block;width:100%;aspect-ratio:10/7;object-fit:contain;background:#091421}.faces{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;text-align:center}.faces img{width:100%;image-rendering:pixelated;background:#101827}.faces small{font-size:12px}.facts{font-size:12px;overflow-wrap:anywhere}.badge{display:inline-block;padding:1px 7px;border:1px solid currentColor;border-radius:8px}a{color:#89d9e4}.note{border-left:3px solid #e2b967;padding:8px 18px;background:#242a35}details{margin-top:10px}summary{cursor:pointer}code{font:12px/1.5 monospace}.hidden{display:none}</style>
<main><h1>36台批准建筑 · 独立控制器候选</h1><p class="note">这是视觉候选页。4套既有贴图原样保留；其余32套只是候选，正式assets、机器注册、游戏实例均未因本页改变。未来52台尚未制作，88种独立控制器的目标没有完成。</p>
<p>统一沿用现有64×64金属面板边框。每台候选在屏幕中显示对应当前正式逐格蓝图的实际轮廓、深度棱线及接口节点；全部使用同一色系，以不同几何图案承担身份，不能靠换色和数字区分。建筑图为蓝图几何示意，未模拟原材质和细小方块，不代替原三维评审。</p>
<div class="bar"><input id="query" placeholder="搜索编号、名称、图案来源" aria-label="搜索"><select id="scope"><option value="all">全部36台</option><option value="pending">仅32套待审候选</option><option value="preserved">仅4套保留</option></select><a href="overview-36.png">打开完整总览图</a><a href="manifest.json">候选清单与SHA256</a><span id="count"></span></div><div id="grid" class="grid"></div></main>
<script>const M=__MANIFEST__;const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));const stateNames={idle:'空闲',active:'运行',paused:'暂停'};
document.querySelector('#grid').innerHTML=M.entries.map(e=>`<article class="card" id="${esc(e.key)}" data-find="${esc((e.label+' '+e.name+' '+e.motif).toLowerCase())}" data-status="${e.preserved?'preserved':'pending'}"><h2>${esc(e.label)} · ${esc(e.name)}</h2><span class="badge ${e.preserved?'preserved':'pending'}">${e.preserved?'既有贴图原样保留':'新候选 · 未批准'}</span><p class="muted">${esc(e.motif)}</p><img loading="lazy" class="geometry" src="${esc(e.geometry_image)}" alt="${esc(e.name)}的当前正式蓝图几何示意"><p class="facts">蓝图：${e.size_xyz.join(' × ')}（X/Y/Z），${e.blocks.toLocaleString()} 个实体方块；当前主控 [${e.controller.join(', ')}]。</p><div class="faces"><div><img src="${esc(e.old.idle.path)}" alt="当前正式空闲面板"><small>当前正式外观</small></div>${Object.entries(stateNames).map(([s,n])=>`<div><img src="${esc(e.candidate[s].path)}" alt="${esc(e.name)}${n}候选"><small>${e.preserved?'保留': '候选'}${n}</small></div>`).join('')}</div><details><summary>来源、三态对照与待批范围</summary><p>${e.preserved?'该套三态像素与当前正式资源SHA256完全一致，不请求重绘批准。':'本台三态面板整体待负责人审阅；未写正式assets，未变更本机注册。'}</p><p class="facts">正式注册ID：<code>${esc(e.machine)}</code><br>蓝图SHA256：<code>${esc(e.source.sha256)}</code><br>几何图案SHA256：<code>${esc(e.geometry_pattern_sha256??'既有符号')}</code></p><div class="faces">${Object.entries(stateNames).map(([s,n])=>`<div><img src="${esc(e.old[s].path)}" alt="当前正式${n}"><small>当前正式${n}</small></div>`).join('')}</div>${e.source_review?`<p><a href="${esc(e.source_review)}">打开原批准结构三维评审</a></p>`:''}<p class="facts">蓝图来源：<code>${esc(e.source.path)}</code></p></details></article>`).join('');
function filter(){let n=0;const q=document.querySelector('#query').value.toLowerCase().trim(),s=document.querySelector('#scope').value;document.querySelectorAll('.card').forEach(el=>{const show=(!q||el.dataset.find.includes(q))&&(s==='all'||s===el.dataset.status);el.classList.toggle('hidden',!show);n+=show});document.querySelector('#count').textContent=`显示 ${n} / 36 台`;}document.querySelector('#query').addEventListener('input',filter);document.querySelector('#scope').addEventListener('change',filter);filter();</script></html>'''
    (OUT / 'index.html').write_text(page.replace('__MANIFEST__', data), encoding='utf-8')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    before = {str(p.relative_to(ASSETS)): sha(p) for p in ASSETS.rglob('*') if p.is_file()}
    index = json.loads((ROOT / 'deliveries/多方块确认归档/当前归档索引.json').read_text(encoding='utf-8'))
    archives = {e['key']: e for e in index['entries']}
    entries = []
    patterns = set()
    for key in KEYS:
        source, meta_path = LAYOUTS / f'{key}.json', METADATA / f'{key}.json'
        layout, metadata = json.loads(source.read_text(encoding='utf-8')), json.loads(meta_path.read_text(encoding='utf-8'))
        assert key == layout['key'] == metadata['key']
        assert sha(source) == metadata['sha256'], f'正式资源SHA256不符：{key}'
        points = np.array([b['pos'] for b in layout['blocks']], dtype=np.float32)
        folder = OUT / key
        folder.mkdir(exist_ok=True)
        geometry_image(points, folder / 'approved-geometry.png')
        entry = {'key': key, 'label': key.upper().replace('_', '-'), 'name': NAMES[key], 'machine': metadata['machine'],
                 'preserved': key in PRESERVED, 'status': 'preserved_existing' if key in PRESERVED else 'candidate_pending_approval',
                 'size_xyz': layout['size'], 'blocks': len(layout['blocks']), 'controller': layout['controller'],
                 'motif': MOTIFS[key], 'source': {'path': str(source), 'sha256': sha(source)},
                 'formal_metadata': {'path': str(meta_path), 'sha256': sha(meta_path)},
                 'source_review': find_review(key, metadata, archives), 'geometry_image': f'{key}/approved-geometry.png',
                 'old': {}, 'candidate': {}}
        for state, suffix in STATE_SUFFIX.items():
            old = ASSETS / f'textures/block/overlay/{current_overlay(key)}/overlay_front{suffix}.png'
            old_out = folder / f'current_{state}.png'
            shutil.copyfile(old, old_out)
            entry['old'][state] = {'path': str(old_out.relative_to(OUT)).replace('\\', '/'), 'sha256': sha(old_out),
                                   'formal_source': str(old)}
            candidate = folder / f'overlay_front{suffix}.png'
            if key in PRESERVED:
                shutil.copyfile(old, candidate)
                assert sha(old) == sha(candidate)
            else:
                image, pattern_sha = candidate_face(points, layout.get('ports', []), layout['controller'], state)
                image.save(candidate)
                entry['geometry_pattern_sha256'] = pattern_sha
            entry['candidate'][state] = {'path': str(candidate.relative_to(OUT)).replace('\\', '/'), 'sha256': sha(candidate)}
        if not entry['preserved']:
            assert entry['geometry_pattern_sha256'] not in patterns, f'候选几何图案重复：{key}'
            patterns.add(entry['geometry_pattern_sha256'])
        entries.append(entry)
        print(json.dumps({'key': key, 'status': entry['status'], 'blocks': entry['blocks']}, ensure_ascii=True), flush=True)
        del layout, points
    after = {str(p.relative_to(ASSETS)): sha(p) for p in ASSETS.rglob('*') if p.is_file()}
    assert before == after, '正式assets发生改变，候选任务必须保持不变'
    assert len(entries) == 36 and len(patterns) == 32 and sum(e['preserved'] for e in entries) == 4
    manifest = {'schema_version': 1, 'created_at': datetime.now(timezone(timedelta(hours=8))).isoformat(),
                'scope': '当前36份批准建筑；4套既有资源原样保留，32套三态控制器候选未批准、未接入正式assets或实例。',
                'planned_total': 88, 'approved_geometry_count': 36, 'new_candidate_count': 32, 'preserved_existing_count': 4,
                'future_unmade_count': 52, 'candidate_state_count': 96, 'formal_assets_unchanged': True,
                'formal_registration_edited': False, 'game_instance_edited': False, 'candidate_approved': False,
                'geometry_source': 'src/main/resources/data/hk3gtl/approved_architecture/*.json；逐文件与正式结构元数据SHA256校验。',
                'visual_method': '共用既有64像素面板框；将当前批准蓝图逐格投影为每台独特的轮廓和深度棱线，不用数字或换色作为机器身份。几何缩略图为简化示意，不模拟真实材质。',
                'approval_boundary': '除i01/i02/i03/s01四套既有三态外，其余32套的空闲/运行/暂停图案整体待审；未制作未来52台。',
                'entries': entries}
    (OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    make_sheet(entries)
    make_html(manifest)
    print(json.dumps({'html': str(OUT / 'index.html'), 'manifest': str(OUT / 'manifest.json'),
                      'new_candidates': 32, 'preserved': 4, 'formal_assets_unchanged': True}, ensure_ascii=True))


if __name__ == '__main__':
    main()
