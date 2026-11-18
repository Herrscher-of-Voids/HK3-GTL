# -*- coding: utf-8 -*-
"""I19候选封装：补充静态主控近景、检查边界、独立评审及讨论记录。

【变更记录 #1】2026-10-23 16:30:54（候选交付，不增加模组修订）
删除：无。新增：外部定位图、逐文件SHA清单、ZIP与部署暂停记录。
修改：只补充新交付和任务日志，不修改结构几何、正式资源或实例。
用途：让负责人能够审阅具体结构，保持候选审批、资源升级与实际部署分开。
"""
import base64
import datetime as dt
import gzip
import hashlib
import html
import json
import re
import shutil
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from build_i19_hbv_coastal_station_v3 import OUT, LOG, ROOT, NAME
from build_integration_revision_20261023 import access
from review_controller_integration_20261023 import front_image


def read(path): return json.loads(path.read_text(encoding='utf-8'))
def save(path, data): path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    folder = OUT / 'i19'
    data = read(folder / 'blueprint.json')
    payload = json.loads(gzip.decompress(base64.b64decode(re.search(r'window.HK3_PAYLOAD\s*=\s*"([^"\n]+)"', (folder/'data.js').read_text(encoding='utf-8'))[1])))
    image = front_image(data, payload['materials'])
    draw = ImageDraw.Draw(image)
    center = 35+95*14+7
    for y in range(65, image.height-40, 18): draw.line((center, y, center, y+8), fill='#6ef5ed', width=2)
    draw.text((35, 36), '宽191格 · 中间第96格 · X=95 · 主控[95,3,20]', font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 16), fill='#6ef5ed')
    image.save(OUT/'北立面定位.png')
    crop = image.crop((35+80*14, 65+(122-18)*14, 35+111*14, 65+123*14))
    crop.resize((crop.width*2, crop.height*2), Image.Resampling.NEAREST).save(OUT/'主控近景.png')
    reaches = access(data)
    assert all(x['front_clear'] and x['backing_solid'] and x['walk_access'] for x in reaches)
    before = read(LOG/'protected-before.json')
    changed = [p for p, old in before['files'].items() if not Path(p).is_file() or sha(Path(p)) != old]
    assert not changed, changed
    review = read(LOG/'independent-visual-review.json')
    geometry_review = read(LOG/'independent-geometry-review.json')
    for checked in (review, geometry_review):
        raw = json.dumps(checked, ensure_ascii=False)
        assert sha(folder/(NAME+'.nbt')) in raw and sha(folder/'blueprint.json') in raw, '独立评审不是当前结构身份'
        assert checked.get('open_blocking_findings') == 0, '仍有独立评审阻断项'
    evidence = OUT/'评审依据'; evidence.mkdir(exist_ok=True)
    for name in ('design-truth.json', 'material-tooling-audit.json', 'design-reference-review.json',
                 'independent-visual-review.json', 'independent-geometry-review.json', 'rules-read.json', 'deployment-hold.json'):
        shutil.copy2(LOG/name, evidence/name)
    record = read(folder/'设计与检查.json')
    record['audit']['access'] = reaches
    record['audit']['checks'].append('主控及八口均有实体背接、正面净空和静态步行操作路径（外围平地假设）')
    record['audit']['protected_files_unchanged'] = len(before['files'])
    record['audit']['independent_review'] = {'visual': '见评审依据/independent-visual-review.json',
                                             'geometry': '见评审依据/independent-geometry-review.json',
                                             'boundary': '独立静态评审不代表用户批准或实机验收。'}
    record['audit']['record_completed_at'] = now.isoformat()
    save(folder/'设计与检查.json', record)
    save(OUT/'verification.json', record['audit'])
    payload['audit'] = record['audit']
    packed = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 9)).decode('ascii')
    (folder/'data.js').write_text('/* I19待审候选；补记静态可达与未部署证据，不代表正式机器。 */\nwindow.HK3_PAYLOAD='+json.dumps(packed)+';', encoding='utf-8')
    page = (OUT/'index.html').read_text(encoding='utf-8')
    insert = '<h2>主控置中与静态近景</h2><p>黄色标记位于整宽第96格；钻石块直接落在有内部仪控连接的厂房北墙。</p><img src="主控近景.png" alt="主控嵌入厂房墙面近景"><p><a href="北立面定位.png">查看整座北立面与中心线</a> · <a href="评审依据/independent-visual-review.json">独立外观检查</a> · <a href="评审依据/independent-geometry-review.json">独立几何检查</a></p>'
    if '主控置中与静态近景' not in page: page = page.replace('<h2>从工艺组织厂区</h2>', insert+'<h2>从工艺组织厂区</h2>')
    (OUT/'index.html').write_text(page, encoding='utf-8')
    # 只检查本候选HTML的本地资源，不访问网络或尝试绕过浏览器协议策略。
    broken = []
    for page_path in OUT.rglob('*.html'):
        for link in re.findall(r'(?:href|src)="([^"]+)"', page_path.read_text(encoding='utf-8')):
            target = link.split('#')[0].split('?')[0]
            if not target or '://' in target or target.endswith('.zip'): continue
            if not (page_path.parent/target).resolve().is_file(): broken.append([str(page_path), link])
    assert not broken, broken
    for source in (Path(__file__), ROOT/'tools/structure_delivery/build_i19_hbv_coastal_station_v3.py'):
        shutil.copy2(source, OUT/'生成脚本'/source.name)
    manifest = read(OUT/'manifest.json')
    manifest.update({'finalized_at': now.isoformat(), 'access': reaches, 'protected_files_unchanged': len(before['files'])})
    save(OUT/'manifest.json', manifest)
    identities = {str(p.relative_to(OUT)): {'bytes': p.stat().st_size, 'sha256': sha(p)}
                  for p in sorted(OUT.rglob('*')) if p.is_file() and p.name != '交付文件清单.json'}
    save(OUT/'交付文件清单.json', {'time': now.isoformat(), 'approval': '待用户审批', 'deployment_allowed': False, 'files': identities})
    archive = OUT.with_suffix('.zip')
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for path in sorted(OUT.rglob('*')):
            if path.is_file(): bundle.write(path, path.relative_to(OUT))
    with zipfile.ZipFile(archive) as bundle:
        assert bundle.testzip() is None
        assert all(bundle.read(name) == (OUT/name).read_bytes() for name in bundle.namelist())
    topic = 'I19单塔蓝湾候选与等待增强版2.9.2再实装'
    discussion = ROOT/'doc/HK3GTL-内测5/讨论记录'/(now.strftime('%Y-%m-%d_%H-%M-%S')+'_'+topic+'.html')
    assert not discussion.exists(), '讨论文件不得覆盖'
    user = read(LOG/'deployment-hold.json')['user_request']
    content = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>{topic}</title><style>body{{max-width:1080px;margin:36px auto;padding:0 22px;font:16px/1.9 'Microsoft YaHei';background:#eff3f6;color:#19334b}}code{{overflow-wrap:anywhere}}a{{color:#175e93}}</style><h1>{topic}</h1><p>实际记录时间：{now.isoformat()}，Asia/Hong_Kong。用户消息精确发送时间未知。</p>
<h2>用户最新要求</h2><blockquote>{html.escape(user)}</blockquote><p>已确认继续下一台I19；完成后先不部署现有增强版2.9，等负责人自行更新2.9.2后再处理。此暂停覆盖旧五台一批自动实装规则；本轮不升级整合包。上游2.9.2为用户告知，并非本轮联网核验。</p>
<h2>已完成的候选</h2><p>I19正式名称“小型崩坏能反应堆”，既定HBV映射。全新单塔蓝湾厂区候选，宽深高191×175×123，{data['block_count']:,}实体方块。主控[95,3,20]，整宽第96格，嵌在真实透平厅北墙；8个工业接口分别落在泵房、燃料热室及送出舱。较旧目标宽190/高122/深174分别增加1格，尺寸调整属于本次候选设计，不冒充用户新批准。</p>
<p>巨型敞口双曲面冷却塔、三层屏蔽核岛、长跨透平厅、泵房和侧置燃料热室独立构图；两冷却干线错层分离、换热及燃料输送穿屏蔽层接到内部设备，透平屋面壳化。没有另立控制面板或异风格托接口柱。这里的“独立”仅指不沿用被否决V2布局，不擅自取消当前I19–I22累计扩建规则；本次只制作I19起点。</p>
<h2>实际检查及边界</h2><p>NBT/Sponge同源逐格回读、实际逐轴尺寸、完整立方体模型、塔口空气、六面连接、三条维护道及9个标记的净空/背接/静态步行操作位置均通过。独立外观与几何复核记录附交付。当前只读2.9纹理资源，未核验2.9.2。材料有效产出与HBV源码路线已摘录，完整生存祖先链与研究未验收。</p>
<p>I19仍无正式控制器/Pattern、真实燃料与冷却剂仓位结算、热管理或游戏发电生命周期；现有一条provisional能源合同不当成可执行燃料配方，15条独立工艺缺口保留。不增加能源系统完成分，不修改模组修订号。外观候选未获用户批准，未计入batch-07，未写正式资源或实例。</p>
<p>浏览器自动打开本地file三维页被安全策略拒绝，仅允许HTTP/HTTPS；没有使用其他浏览器、原始命令或本地代理绕过，三维交互未自动验收。静态真实纹理图、俯视、内部剖切和主控近景已生成审阅。</p>
<h2>文件与下一步</h2><p><a href="../../../deliveries/{OUT.name}/index.html">I19交付评审</a> · <a href="../../../deliveries/{archive.name}">完整ZIP</a> · <a href="../../../logs/i19-next-candidate-20261023/final-verification.json">最终校验</a> · <a href="2026-10-23_13-50-52_I01-I18居中融合V2正式实装修订175.html">上一批正式接入记录</a></p><p>ZIP SHA256：<code>{sha(archive)}</code>。已核对{len(before['files'])}份受保护模组/正式结构文件SHA不变；旧候选保持原样。下一步为负责人外观审阅；2.9.2更新后再按实际资源和批准版本处理实装，本轮不代为解除部署暂停。</p><p>变更记录#1：新增候选与讨论、规则#10暂停部署、独立检查和ZIP；删除无；正式机器/配方/资源及实例不改。六规则本轮实际阅读时间与身份见交付评审依据/rules-read.json；规则#10为读取后按用户新要求追加，前后身份分别保留。</p></html>'''
    discussion.write_text(content, encoding='utf-8')
    result = {'time': now.isoformat(), 'candidate': str(OUT), 'blocks': data['block_count'], 'size_xyz': data['size'],
              'controller': data['controller'], 'ports': len(data['ports']), 'hashes': manifest['hashes'],
              'protected_files_unchanged': len(before['files']), 'instance_changed': False, 'formal_resources_changed': False,
              'candidate_approved': False, 'deployment_allowed': False, 'zip': str(archive), 'zip_sha256': sha(archive),
              'zip_files': len(identities)+1, 'local_links_valid': True, 'discussion': str(discussion),
              'rule_after_sha256': sha(ROOT/'rule/当前多方块设计规则.md'),
              'browser_automated_review': False, 'browser_block': record['audit']['browser_review'], 'static_access': reaches}
    save(LOG/'final-verification.json', result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
