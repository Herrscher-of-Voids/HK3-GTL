"""应用负责人确认的贴图，备份旧资源并校验来源。

【变更记录 #1】2026-09-27（实际执行时间写入清单）
删除：无。新增：确认贴图应用、备份和哈希核验。
修改：仅指定二十件物品、推进器动画及资源记录；空核心按最新要求金黄。
用途：将评审成果落实到正式资源，不启动游戏，不修改业务配方。
"""
from pathlib import Path
from datetime import datetime
import json, shutil, hashlib, colorsys
from PIL import Image
import preview_art81 as a
import preview_art82 as b

ROOT=a.ROOT
LOG=ROOT/'logs/revision85'
TEX=a.TEX
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert not (LOG/'application.json').exists(), '已应用，不重复执行'
    LOG.mkdir(parents=True,exist_ok=True)
    before={str(p.relative_to(ROOT)):digest(p) for p in (ROOT/'src').rglob('*') if p.is_file()}
    selected={}
    for rev,names in [(81,['honkai_fuel_rod_casing','soulium_swarf','separation_filter','honkai_analysis_sample','hyperion_thruster_assembly','conducting_composite','reconstructing_composite','cognitive_composite']), (82,['sealed_real_world_bubble','imitation_flame_core','nano_building_unit','reconstruction_rule_carrier']), (83,['imitation_thunder_core','imitation_ice_core','imitation_wind_core','imitation_corruption_core','unmanned_resource_probe_a']), (84,['imitation_binding_core','imitation_rock_core'])]:
        manifest=json.loads((ROOT/f'logs/art-review{rev}/manifest.json').read_text('utf-8'))
        indexed={e['id']:e for e in manifest['entries']}
        for name in names:
            p=ROOT/f'logs/art-review{rev}/candidates/{name}.png'
            assert digest(p)==indexed[name]['sha256'],name
            selected['unmanned_resource_probe' if name.endswith('_probe_a') else name]=(p,indexed[name])
    # 仅将已展示空核心晶体的色相改为金黄，保留裂隙、金环和透明度。
    p=ROOT/'logs/art-review84/candidates/imitation_void_core.png'
    im=Image.open(p).convert('RGBA'); original=im.copy();_,check=b.core(.13)
    for xy in check['mask']:
        xy=tuple(xy);r,g,bl,alpha=im.getpixel(xy)
        h,s,v=colorsys.rgb_to_hsv(r/255,g/255,bl/255)
        im.putpixel(xy,tuple(round(c*255) for c in colorsys.hsv_to_rgb(.13,s,v))+(alpha,))
    mask={tuple(xy) for xy in check['mask']}
    assert all(im.getpixel((x,y))==original.getpixel((x,y)) for y in range(16) for x in range(16) if (x,y) not in mask)
    dest=LOG/'imitation_void_core_gold.png';im.save(dest)
    selected['imitation_void_core']=(dest,{'source':str(p.relative_to(ROOT)),'source_sha256':digest(p),'note':'负责人最新指定金黄色；保持原金环和裂隙','checks':{'outside_mask_unchanged':True}})
    assert len(selected)==20
    def backup(p):
        if p.exists():
            dest=LOG/'backup'/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True)
            assert not dest.exists();shutil.copy2(p,dest)
    entries=[];allowed=set()
    for name,(source,record) in selected.items():
        target=TEX/f'{name}.png';assert target.exists()
        model=ROOT/f'src/main/resources/assets/hk3gtl/models/item/{name}.json'
        assert json.loads(model.read_text('utf-8-sig'))['textures']['layer0']==f'hk3gtl:item/{name}'
        backup(target);shutil.copy2(source,target)
        assert digest(target)==digest(source)
        allowed.add(str(target.relative_to(ROOT)))
        meta=source.with_suffix('.png.mcmeta')
        if meta.exists():
            tmeta=target.with_suffix('.png.mcmeta');backup(tmeta);shutil.copy2(meta,tmeta);allowed.add(str(tmeta.relative_to(ROOT)))
        else: assert not target.with_suffix('.png.mcmeta').exists(),name+'存在未处理动画'
        entries.append({'id':name,'source':str(source.relative_to(ROOT)),'destination':str(target.relative_to(ROOT)),'sha256':digest(target),'provenance':record})
    now=datetime.now().astimezone()
    catalog=ROOT/'src/main/resources/data/hk3gtl/catalog/industrial_art85.json';assert not catalog.exists()
    catalog.write_text(json.dumps({'revision':85,'time':now.isoformat(),'_comment':'变更记录 #1：应用二十件已确认物品；删除无，历史候选保留。来源、像素约束及用途见各项记录。','entries':entries},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    allowed.add(str(catalog.relative_to(ROOT)))
    changelog=ROOT/'src/main/resources/assets/hk3gtl/changelog.json';backup(changelog)
    data=json.loads(changelog.read_text('utf-8-sig'));assert data['entries'][0]['revision']==80
    data['entries'].insert(0,{'version':'0.5.0','revision':85,'codename':'HK3GTL-内测5','date':now.strftime('%Y-%m-%d'),'time':now.strftime('%H:%M:%S'),'reason':'落实负责人已确认贴图；81至84是候选评审编号，不是已发布模组修订。','changes':['变更记录 #85：删除无；旧正式资源先备份，保留全部历史记录。','修改：二十件物品采用已确认候选，探测器采用A，空核心最终改金黄色。','新增：industrial_art85来源清单；推进组件保留原图两帧及动画元数据。','保留：理核心、试作探测器、电路资产及尚未选择A/B的约束复合材料、边角料。','用途：落实已确认美术；未修改玩法、模型、注册ID、配方。构建部署另行记录，不表示游戏验收。']})
    changelog.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');allowed.add(str(changelog.relative_to(ROOT)))
    after={str(p.relative_to(ROOT)):digest(p) for p in (ROOT/'src').rglob('*') if p.is_file()}
    changed={p for p in set(before)|set(after) if before.get(p)!=after.get(p)}
    assert changed<=allowed,changed-allowed
    report={'time':now.isoformat(),'entries':entries,'changed':sorted(changed),'only_allowed_resources_changed':True,'preserved':['imitation_reason_core','prototype_honkai_detector','confining_composite','composite_offcut']}
    (LOG/'application.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'applied_textures':len(entries),'changed_files':len(changed),'only_allowed_resources_changed':True}))
if __name__=='__main__':main()
