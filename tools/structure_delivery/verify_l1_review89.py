# -*- coding: utf-8 -*-
"""候选89交付检查：不启动浏览器或游戏，不改变正式资源。
【变更记录 #1】2026-09-27 03:29:30
删除：无。新增：离线引用、材质覆盖、JS语法、逐格结构回读和发布包隔离核验。
修改：无正式文件。用途：将已核验与未核验事项分别写入候选审计。
【变更记录 #2】2026-09-27 03:38:33：增加接口调整版核验，独立保存报告并逐格确认设备未被通道切除。
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote
from datetime import datetime
from collections import Counter
import base64, hashlib, importlib.util, io, json, re, subprocess, zipfile, os
import nbtlib
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
# 【变更记录 #3】2026-09-27 03:43:01：逐格核验统一地板和两层全接口面板，新增槽不冒充必要仓室。
LAYOUT3=os.environ.get('HK3_REVIEW_LAYOUT')=='3'
LAYOUT2=LAYOUT3 or os.environ.get('HK3_REVIEW_LAYOUT')=='2'
OUT=ROOT/('doc/HK3GTL-内测5/03_机器结构/L1五机重设计_候选89'+('_统一地板' if LAYOUT3 else '_接口调整' if LAYOUT2 else ''))
LOG=ROOT/'logs/revision89'/('layout3' if LAYOUT3 else 'layout2' if LAYOUT2 else '')


class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.refs=[];self.ids=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:self.ids.append(attrs['id'])
        for key in ('src','href'):
            if key in attrs:self.refs.append(attrs[key])


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    spec=importlib.util.spec_from_file_location('buildings89',ROOT/'tools/structure_delivery/l1-review89-buildings.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    viewer=(LOG/'viewer-adapted.mjs').read_text(encoding='utf-8')
    required=set(re.findall(r"getElementById\('([^']+)'\)",viewer))
    pages=[]
    for page in OUT.rglob('*.html'):
        parser=Page();parser.feed(page.read_text(encoding='utf-8'))
        assert len(parser.ids)==len(set(parser.ids)),('重复DOM标识',page)
        for ref in parser.refs:
            if ref.startswith(('data:','#')):continue
            assert '://' not in ref,('离线页面依赖网络',ref)
            assert (page.parent/unquote(ref.split('?')[0].split('#')[0])).is_file(),(page,ref)
        if page.name=='三维评审.html':assert required<=set(parser.ids),(page,required-set(parser.ids))
        pages.append(str(page.relative_to(OUT)))
    assert len(pages)==6
    scripts=[ROOT/'tools/structure_delivery/build_l1_review89.mjs',LOG/'viewer-adapted.mjs',OUT/'viewer.bundle.js']
    for script in scripts:subprocess.run(['node','--check',str(script)],check=True,capture_output=True)
    materials_all=set();machines=[]
    for entry in json.loads((OUT/'manifest.json').read_text(encoding='utf-8')):
        folder=OUT/entry['key'];data=json.loads((folder/'blueprint.json').read_text(encoding='utf-8'))
        expected={tuple(b['pos']):b['state'] for b in data['blocks']}
        assert len(expected)==len(data['blocks'])
        assert all(all(0<=p[i]<data['size'][i] for i in range(3)) for p in expected)
        geometry=module.validate(data)
        if LAYOUT2:
            layout_spec=importlib.util.spec_from_file_location('layout2',ROOT/'tools/structure_delivery/l1-review89-layout2.py')
            layout=importlib.util.module_from_spec(layout_spec);layout_spec.loader.exec_module(layout)
            proposal=json.loads((ROOT/'logs/revision89/design-proposal.json').read_text(encoding='utf-8'))
            source=next(m for m in proposal['machines'] if m['id']==entry['key'])
            original=layout.Building(source);getattr(module,entry['key'])(original);module.enrich(original)
            assert all(expected.get(p)==s for p,s in original.cells.items() if p[1]>0),'主体有切除或覆盖'
            cx=data['size'][0]//2
            assert data['controller']==[cx,2,3]
            assert all(expected[cx,0,z]==('kubejs:module_base' if LAYOUT3 else 'gtceu:computer_casing') for z in range(data['size'][2]))
            assert all(p['face']=='north' and p['pos'][2]==3 and p['pos'][1] in (1,2) for p in data['ports'])
            if LAYOUT3:
                assert {s for p,s in expected.items() if p[1]==0}=={'kubejs:module_base'}
                half=max(2,(sum(source['ports'].values())+3)//4)
                # 变更记录 #4（2026-09-27 03:45:00）：分别核验白色外框和框内接口，避免再次混淆。
                panel={(x,y,3) for x in range(cx-half,cx+half+1) for y in (1,2)}
                assert panel=={tuple(p['pos']) for p in data['ports']}|{tuple(data['controller'])}
                assert all(expected[p] in ('minecraft:diamond_block','minecraft:diamond_ore') for p in panel)
                frame={(x,3,3) for x in range(cx-half-1,cx+half+2)}|{(x,y,3) for x in (cx-half-1,cx+half+1) for y in (1,2)}
                assert all(expected[p]=='gtceu:computer_casing' for p in frame)
                assert len([p for p in data['ports'] if not p['id'].startswith('E')])==sum(source['ports'].values())
            else:
                assert len(data['ports'])==sum(source['ports'].values())
                assert max(abs(p['pos'][0]-cx) for p in data['ports'])<=4
        materials=json.loads((folder/'materials.json').read_text(encoding='utf-8'))
        assert {m['state'] for m in materials}==set(expected.values())
        for m in materials:
            assert m['complete_cube']
            for face in ['north','south','east','west','up','down']:
                image=Image.open(io.BytesIO(base64.b64decode(m['faces'][face].split(',')[1])));image.verify()
        ordinary={s for s in expected.values() if not s.startswith('minecraft:')};materials_all.update(ordinary)
        schem=nbtlib.load(folder/(data['name']+'.schem'))
        w,h,d=data['size'];assert [int(schem[k]) for k in ['Width','Height','Length']]==[w,h,d]
        palette={int(v):str(k) for k,v in schem['Palette'].items()}
        dense=[];value=shift=0
        for byte in schem['BlockData']:
            byte=int(byte)&255;value|=(byte&127)<<shift
            if byte&128:shift+=7
            else:dense.append(value);value=shift=0
        assert shift==0 and len(dense)==w*h*d
        decoded={(i%w,i//(w*d),(i//w)%d):palette[v] for i,v in enumerate(dense) if palette[v]!='minecraft:air'}
        assert decoded==expected
        native=nbtlib.load(folder/(data['name']+'.nbt'))
        states=[str(p['Name'])+('['+','.join(f'{k}={v}' for k,v in p['Properties'].items())+']' if p.get('Properties') else '') for p in native['palette']]
        assert {tuple(map(int,b['pos'])):states[int(b['state'])] for b in native['blocks']}==expected
        machines.append({'key':entry['key'],'blocks':len(expected),'material_states':len(ordinary),'block_ids':len({s.split('[')[0] for s in ordinary}),'ports':len(data['ports']),'accessible_floor_cells':geometry['accessible_floor_cells'],'ordinary_placed_by_namespace':dict(Counter(s.split(':')[0] for s in expected.values() if not s.startswith('minecraft:'))),'structure_formats_exact':True})
    prior_build=json.loads((ROOT/'logs/revision88/package-verification.json').read_text(encoding='utf-8'))
    deployed=json.loads((ROOT/'logs/revision87/deployment.json').read_text(encoding='utf-8'))
    packages={str(Path(prior_build['jar'])):sha(Path(prior_build['jar'])),str(Path(deployed['target'])):sha(Path(deployed['target']))}
    assert packages[str(Path(prior_build['jar']))]==prior_build['sha256']
    assert packages[str(Path(deployed['target']))]==deployed['sha256']
    formal=[]
    with zipfile.ZipFile(prior_build['jar']) as jar:
        for p in (ROOT/'src/main/resources/data/hk3gtl').rglob('*'):
            if p.is_file() and ('approved' in str(p.parent) or 'approved_architecture' in str(p.parent)):
                relative=p.relative_to(ROOT/'src/main/resources').as_posix()
                assert jar.read(relative)==p.read_bytes(),('正式资源发生变化',relative)
                formal.append(relative)
    now=datetime.now().astimezone().isoformat()
    report={'time':now,'candidate_only':True,'html_pages':pages,'local_references_present':True,'viewer_dom_complete':True,'javascript_syntax_checks':len(scripts),'all_material_faces_decode':True,'distinct_material_states':len(materials_all),'distinct_block_ids':len({s.split('[')[0] for s in materials_all}),'material_namespaces':dict(Counter(s.split(':')[0] for s in materials_all)),'machines':machines,'protected_package_hashes':packages,'formal_resources_match_revision88_jar':formal,'browser_interaction_tested':False,'game_started':False,'game_tested':False,'deployed':False,'review_notes':['等轴图已人工查看；投影相机与可见面一致。','资源模型核验不等于运行时注册、碰撞、成型核验。','正式替换仍待负责人审批。']}
    (LOG/'delivery-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    if LAYOUT2:
        record={'number':1,'time':now,'deleted':'新候选取消无功能2×2装饰墩与强制贯穿切除；旧文件保留','added':'正面居中主控、紧邻左右的两层接口面板、沿自然空隙绕行的检修带','modified':'五机主体造型沿用，修复被旧通道切除的实体；独立生成接口调整版','purpose':'落实负责人确认的布局并交付审核；未替换正式资源或部署','equipment_preserved_verified':True,'controller_and_axis_centered_verified':True,'ports_front_two_rows_verified':True,'entry':str(OUT/'index.html')}
        if LAYOUT3:
            record.update(number=2,deleted='撤销误删白色外框；修改前候选和记录已备份',added='恢复顶部与左右白色计算机机壳外框，框内除居中主控外均为接口',modified='仅修正外框及对应可选槽数量，灰色地板、主体、原必要接口和并行上限不变',uniform_floor_verified=True,all_panel_cells_are_ports_or_controller_verified=True,white_frame_verified=True)
        (LOG/'layout-change.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps({'pages':len(pages),'machines':machines,'layout_checks':record,'deployed':False},ensure_ascii=False))
        return
    proposal_file=LOG/'design-proposal.json';proposal=json.loads(proposal_file.read_text(encoding='utf-8'))
    proposal['current_candidate_review']={'time':now,'entry':str(OUT/'index.html'),'scope':'仅离线候选；尚未批准正式替换','supersedes_material_scope':'覆盖原提案仅沿用九种材料的候选范围，原记录保留。','actual_material_states':sorted(materials_all),'actual_machine_statistics':machines,'scanned_candidates':980,'complete_resource_models':786,'gtladditions_note':'已调查3.3版JAR，未找到静态blockstates，不虚构可用建材；动态注册未穷尽。'}
    if not any(c.get('number')==2 for c in proposal.get('change_records',[])):
        proposal.setdefault('change_records',[]).append({'number':2,'time':now,'deleted':'无，保留原提案与历史范围','added':'整包扩大选材、五机几何、离线三维入口、同源NBT和Sponge、逐项材料隐藏','modified':'普通建材扩大至34种，每机18–20种；修正等轴图投影；正式结构未替换','purpose':'按负责人要求先展示更丰富的工业建筑，再审核'})
    proposal_file.write_text(json.dumps(proposal,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['html_pages','distinct_material_states','distinct_block_ids','material_namespaces','javascript_syntax_checks','browser_interaction_tested','game_tested','deployed']},ensure_ascii=False))


if __name__=='__main__':main()
