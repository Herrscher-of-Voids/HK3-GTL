# -*- coding: utf-8 -*-
"""从V4完整几何派生纯静态预览，原动画候选仅作历史保存。"""
import base64
from copy import deepcopy
import gzip
import hashlib
from html import escape
import json
from pathlib import Path
import re
import shutil
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'deliveries/W02_Gemini_半构造星核船坞_V4_20261109'
OUT=ROOT/'deliveries/W02_Gemini_半构造星核船坞_V4S_静态_20261109'
LOG=ROOT/'logs/w02-static-v4s-20261109'
REPORT=ROOT/'logs/beta5-completion-audit-20261030'


def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def overlap_review(data):
    pairs=data['component_overlaps'];proof=[]
    with np.load(ROOT/'logs/w02-gemini-v4-20261109/original-components.npz') as raw:
        points={name:raw[name+'__p'] for name in data['component_bounds_blueprint']}
        keys={name:((p[:,1].astype(np.int64)+2048)*4096+p[:,2]+2048)*4096+p[:,0]+2048 for name,p in points.items()}
        for pair in pairs:
            a,b=pair['first'],pair['second'];shared=np.intersect1d(keys[a],keys[b],assume_unique=True)
            assert len(shared)==pair['shared_voxels'],pair
            coords=np.c_[shared%4096-2048,shared//(4096**2)-2048,shared//4096%4096-2048]
            kind='设计连接或过渡，未作材质冲突验收'
            if (a=='base' and b.startswith('wing:')) or (a.startswith('wing:') and b.startswith('print:')) or b=='crown:1':
                kind='独立构件实体相交'
            elif a.startswith('wing:') and b.startswith('C-arm:'):
                kind='连接处相交，原案14格悬浮间隙待复核'
            proof.append(dict(pair,classification=kind,overlap_bounds_blueprint=dict(min=coords.min(0).tolist(),max=coords.max(0).tolist()),
                example_shared_voxels_blueprint=coords[:8].tolist()))
    assert sum(p['classification']=='独立构件实体相交' for p in proof)==9
    return dict(total_pairs=len(proof),independent_intersection_pairs=9,floating_joint_review_pairs=12,
        intended_or_transition_pairs=24,pairs=proof,
        assessment='重工船坞与半构造星核方向可用；中心与翼架交叠仍需修订。取消动画不会消除静态实体相交。',
        geometry_changed=False,static_clearance_verified=False)


def main():
    OUT.mkdir(parents=True,exist_ok=True);LOG.mkdir(parents=True,exist_ok=True)
    baseline=LOG/'report-baseline'
    if not baseline.exists():
        baseline.mkdir()
        for n in ('index.html','current-summary.json'):shutil.copy2(REPORT/n,baseline/n)
        shutil.copy2(ROOT/'rule/当前多方块设计规则.md',LOG/'rule-before-v4s.backup')
        save(LOG/'old-v4-sha256.json',{str(p.relative_to(ROOT)):sha(p) for p in SOURCE.rglob('*') if p.is_file()})
    encoded=json.loads((SOURCE/'w02/data.js').read_text('utf8').split('=',1)[1].rstrip(';'))
    payload=json.loads(gzip.decompress(base64.b64decode(encoded)))
    data=payload['data'];check=payload['audit'];original_parts=deepcopy(payload['parts'])
    data.pop('motions');data.update(candidate_version='V4S-纯静态',animation_enabled=False,
        title='理之律者 · 万象·自律工业矩阵 · Gemini V4S纯静态候选',
        parent_candidate='V4',purpose='负责人要求取消动画；完整静态几何与原坐标保留，未批准、未部署。')
    data['source_conflicts']=[s for s in data['source_conflicts'] if not s.startswith('运行时内环翻转')]
    review=overlap_review(data)
    check.update(animation_removed=True,animation_loop_present=False,static_clearance_verified=False,
        dynamic_clearance_verified=None,geometry_unchanged_from_v4=True,
        source_raw_components=str((ROOT/'logs/w02-gemini-v4-20261109/original-components.npz').relative_to(ROOT)).replace('\\','/'),
        claim_boundary='纯静态离线候选。动画、时间轴及播放入口已移除；静态干涉未修复，无新增游戏测试。')
    assert original_parts==payload['parts']
    save(OUT/'manifest.json',data);save(OUT/'verification.json',check);save(OUT/'静态交叠复核.json',review)
    save(OUT/'原案参数与冲突.json',dict(source_conflicts=data['source_conflicts'],coordinate_interpretation=data['coordinate_interpretation'],
        component_overlaps=data['component_overlaps'],animation_enabled=False))
    shutil.copy2(SOURCE/'材料清单.json',OUT/'材料清单.json')
    view=OUT/'w02';view.mkdir(exist_ok=True)
    encoded=base64.b64encode(gzip.compress(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode(),6)).decode()
    (view/'data.js').write_text('window.W02_STATIC_PAYLOAD='+json.dumps(encoded)+';','utf8')
    page=(SOURCE/'w02/三维评审.html').read_text('utf8')
    page=page.replace('W02 Gemini V4 · 动态原案预览','W02 Gemini V4S · 纯静态预览').replace('← V4总览','← 静态版总览')
    page=page.replace('Gemini 最新原案 V4 ·','Gemini V4S 纯静态 ·').replace('动画为网页试览','全部构件保持原蓝图坐标')
    page,n=re.subn(r'<button id="play">.*?</label>','<button id="reset">重置视角</button>',page,count=1,flags=re.S);assert n==1
    page=page.replace('剖切高度（自动暂停并回原位）','剖切高度').replace('；动画扫掠单独扩展取景。','；完整实体取景。')
    page=page.replace('网页动画未接入游戏；原案静态相交与运动干涉待协调。','纯静态候选；静态相交仍待协调。')
    page=page.replace('window.W02_V4_PAYLOAD','window.W02_STATIC_PAYLOAD')
    (view/'三维评审.html').write_text(page,'utf8')
    source=(ROOT/'tools/structure_delivery/w02_gemini_viewer_v4_20261109.mjs').read_text('utf8')
    renderer=source[:source.index('  let seconds=0,playing=false')]
    renderer=renderer.replace('/** W02原案独立构件试览：一次上传体素表面，每帧只改组矩阵。 */','/** W02完整纯静态预览：仅相机或控件变化时重绘。 */')
    renderer=renderer.replace('W02_V4_PAYLOAD','W02_STATIC_PAYLOAD')
    renderer=renderer.replace('const groups=[],allMeshes=[],motions=new Map(data.motions.map(m=>[m.id,m]));','const groups=[],allMeshes=[];')
    old='''    const motion=motions.get(part.id), origin=new THREE.Vector3(...part.origin);
    const pivot=motion?new THREE.Vector3(...motion.pivot_blueprint).add(offset):origin.clone();
    group.position.copy(pivot);group.userData.pivot=pivot.clone();group.userData.motion=motion;'''
    assert old in renderer
    renderer=renderer.replace(old,'''    const origin=new THREE.Vector3(...part.origin),pivot=origin.clone();
    group.position.copy(origin);''')
    tail=(ROOT/'tools/structure_delivery/w02_static_viewer_tail_v4s_20261109.js').read_text('utf8')
    scripts=OUT/'生成脚本';scripts.mkdir(exist_ok=True)
    static_source=scripts/'w02_static_viewer_v4s_20261109.mjs'
    static_source.write_text(renderer+tail,'utf8')
    assert not any(word in (renderer+tail) for word in ('requestAnimationFrame','setInterval','function schedule','function seek','function apply','Math.sin('))
    assert not any(word in page for word in ('id="play"','id="time"','演出时间','动态原案预览'))
    shutil.copy2(__file__,scripts/Path(__file__).name)
    shutil.copy2(ROOT/'tools/structure_delivery/w02_static_viewer_tail_v4s_20261109.js',scripts/'w02_static_viewer_tail_v4s_20261109.js')
    size=data['size'];struct='../W02_Gemini_半构造星核船坞_V4_20261109/w02/'+data['name']
    (OUT/'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>W02 Gemini V4S · 纯静态版</title>
<style>:root{{color-scheme:dark}}body{{max-width:1340px;margin:30px auto;padding:0 24px;background:#0c1828;color:#e5f5ff;font:16px/1.8 system-ui}}a{{color:#85ddff}}img{{width:100%;display:block}}.note{{padding:16px;background:#19334c;border-left:3px solid #78dcff}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}@media(max-width:800px){{.grid{{display:block}}}}</style>
<h1>理之律者 · 万象·自律工业矩阵</h1><p>Gemini V4S · 纯静态候选 · 2026-11-09</p>
<p class="note">全部构件固定在原蓝图坐标；可用鼠标旋转镜头、缩放和剖切。实际{size[0]}×{size[2]}×{size[1]}（宽深高），{data['blocks']:,}实体方块，39个独立构件。</p>
<p><a href="w02/三维评审.html">打开完整静态三维预览</a> · <a href="静态交叠复核.json">静态交叠与坐标复核</a> · <a href="原案参数与冲突.json">原案参数</a> · <a href="verification.json">核验记录</a></p>
<img src="完整预览.png" alt="W02 V4S完整静态全景"><div class="grid"><img src="正面十二翼.png" alt="正面翼架"><img src="俯视布局.png" alt="四井与船坞"></div>
<p>造型方向可保留，当前布局还需修订。45对共享体素中，9对属于独立构件实体相交：最低两翼与基座2对、翼与打印站4对、中环与左右母架及前炮3对；12对翼根连接还需核对原案14格悬浮间隙，其余24对为设计连接或过渡，未据此认定全部无材质冲突。</p>
<div class="grid"><img src="半构造星核.png" alt="静态星核近景"><img src="侧面原案.png" alt="静态侧面"></div>
<p>本次仅取消转动、悬浮、脉动、扫描位移与播放控件；未通过移位、裁切或删除实体来掩盖交叠。组合NBT／Schematic与V4字节一致并复用历史文件；几何未变，尚未批准或实装测试。</p>
<p><a href="{struct}.nbt">组合NBT</a> · <a href="{struct}.schem">Schematic</a> · <a href="材料清单.json">材料清单</a> · <a href="../../logs/beta5-completion-audit-20261030/index.html">固定审计</a></p></html>''','utf8')
    save(LOG/'package-verification.json',dict(passed=True,animation_removed=True,animation_data_removed='motions' not in data,
        geometry_unchanged=True,parts_payload_equal=original_parts==payload['parts'],size_xyz=size,blocks=data['blocks'],
        independent_intersections=9,floating_joint_review_pairs=12,old_v4_preserved=True,new_game_test=False))
    print(json.dumps(dict(passed=True,blocks=data['blocks'],intersections=9),ensure_ascii=False))


if __name__=='__main__':main()
