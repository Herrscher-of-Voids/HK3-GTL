# -*- coding: utf-8 -*-
"""I20交付封装与本轮部署顺序讨论记录，限定候选及日志。

【变更记录 #1】2026-10-23 18:12:31（候选封装，不增加模组修订）
删除：无。新增：最终评审身份检查、保护文件SHA复核、ZIP逐字节核对和讨论记录。
修改：较早视审仅作为历史，最终评审必须匹配当前蓝图及NBT。
用途：交付可复查的候选，同时准确记录上一批已实装和新批不足五台的事实。
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

from build_i20_qsv_second_unit_v1 import OUT, LOG, ROOT, NAME


def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p, value): p.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    folder = OUT/'i20'
    blueprint, nbt = sha(folder/'blueprint.json'), sha(folder/(NAME+'.nbt'))
    final = read(LOG/'independent-final-review.json')
    raw = json.dumps(final, ensure_ascii=False)
    assert blueprint in raw and nbt in raw, '终审必须对应当前蓝图及NBT'
    assert final.get('open_blocking_findings') == 0, '仍有终审阻断'
    before = read(LOG/'protected-before.json')
    altered = [p for p, identity in before['files'].items() if not Path(p).is_file() or sha(Path(p)) != identity]
    assert not altered, altered
    record = read(folder/'设计与检查.json')
    audit = record['audit']
    assert all(p['front_clear'] and p['backing_solid'] and p['walk_access'] for p in audit['access'])
    assert record['data']['block_count'] == 490655
    audit['protected_files_unchanged'] = len(before['files'])
    audit['final_review'] = {'file': '评审依据/independent-final-review.json', 'sha256': sha(LOG/'independent-final-review.json'),
                             'blueprint_sha256': blueprint, 'nbt_sha256': nbt, 'open_blocking_findings': 0,
                             'boundary': '静态独立复核不等于用户批准或游戏运行验收'}
    audit['checks'].append('复核修正燃料转运支线、透平回流端点和五道承重门架')
    audit['finalized_at'] = now.isoformat()
    save(folder/'设计与检查.json', record); save(OUT/'verification.json', audit)
    text = (folder/'data.js').read_text(encoding='utf-8')
    packed = re.search(r'window.HK3_PAYLOAD\s*=\s*"([^"\n]+)"', text)[1]
    payload = json.loads(gzip.decompress(base64.b64decode(packed)))
    payload['audit'] = audit
    packed = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 9)).decode('ascii')
    (folder/'data.js').write_text('/* I20待审候选；最终身份与检查范围见评审依据。 */\nwindow.HK3_PAYLOAD='+json.dumps(packed)+';', encoding='utf-8')
    evidence = OUT/'评审依据'; evidence.mkdir(exist_ok=True)
    for name in ('rules-read.json', 'design-truth.json', 'design-critique.json', 'material-tooling-audit.json',
                 'batch-deployment-recheck.json', 'independent-visual-review.json', 'independent-final-review.json'):
        shutil.copy2(LOG/name, evidence/name)
    save(evidence/'保护文件复核.json', {'time': now.isoformat(), 'checked': len(before['files']), 'changed': altered})
    scripts = OUT/'生成脚本'
    for name in ('build_i20_qsv_second_unit_v1.py', 'package_i20_qsv_candidate_20261023.py', 'finalize_i20_candidate_20261023.py'):
        shutil.copy2(ROOT/'tools/structure_delivery'/name, scripts/name)
    manifest = read(OUT/'manifest.json')
    manifest.update({'finalized_at': now.isoformat(), 'blueprint_sha256': blueprint,
                     'final_review': audit['final_review'], 'protected_files_unchanged': len(before['files'])})
    save(OUT/'manifest.json', manifest)
    page = (OUT/'index.html').read_text(encoding='utf-8')
    page = page.replace('<h2>电压、材料与实际能力</h2>', '<p><a href="评审依据/independent-final-review.json">最终独立复核</a> · <a href="评审依据/batch-deployment-recheck.json">2.9上一批部署现场复核</a></p><h2>电压、材料与实际能力</h2>')
    (OUT/'index.html').write_text(page, encoding='utf-8')
    broken = []
    for page_path in OUT.rglob('*.html'):
        for link in re.findall(r'(?:href|src)="([^"]+)"', page_path.read_text(encoding='utf-8')):
            name = link.split('#')[0].split('?')[0]
            if not name or '://' in name or name.endswith('.zip'): continue
            if not (page_path.parent/name).resolve().is_file(): broken.append([str(page_path), link])
    assert not broken, broken
    identities = {p.relative_to(OUT).as_posix(): {'bytes': p.stat().st_size, 'sha256': sha(p)}
                  for p in sorted(OUT.rglob('*')) if p.is_file() and p.name != '交付文件清单.json'}
    save(OUT/'交付文件清单.json', {'time': now.isoformat(), 'approval': '待用户审批', 'deployment_eligible': False,
                                'blueprint_sha256': blueprint, 'nbt_sha256': nbt, 'files': identities})
    archive = OUT.with_suffix('.zip')
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for p in sorted(OUT.rglob('*')):
            if p.is_file(): bundle.write(p, p.relative_to(OUT))
    with zipfile.ZipFile(archive) as bundle:
        assert bundle.testzip() is None
        assert all(bundle.read(name) == (OUT/name).read_bytes() for name in bundle.namelist())
    quote = '不对啊，现在是不是够5台了？够5台的话，那就先实装到2.9里，到时候更新以后，再看一下，在2.9.2能不能运行？能的话那就可以，不能的话再进行修改'
    topic = '五台批次实装复核与I20双岛扩建候选'
    discussion = ROOT/'doc/HK3GTL-内测5/讨论记录'/(now.strftime('%Y-%m-%d_%H-%M-%S')+'_'+topic+'.html')
    assert not discussion.exists()
    body = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>{topic}</title><style>body{{max-width:1060px;margin:35px auto;font:16px/1.9 'Microsoft YaHei';color:#243c48}}code{{overflow-wrap:anywhere}}</style><h1>{topic}</h1><p>实际记录时间：{now.isoformat()}，Asia/Hong_Kong；用户消息精确时间未知。</p>
<h2>用户明确决定</h2><blockquote>下一台吧</blockquote><blockquote>{html.escape(quote)}</blockquote><p>继续I20建筑候选；新决定解除上一轮等待2.9.2再部署的暂停。后续满五台明确批准后先装实际增强版2.9，负责人升级后再核验2.9.2运行，出现问题再修改。本轮不代升级整合包。</p>
<h2>批次数量与实际实例核对</h2><p>I14–I18五台已在2026-10-23 13:50:30随修订175停机实装2.9；当前现场JAR SHA256仍为46e75cb2515745f9e3c0635b9bbd0e76d6336661cc499d121cf4d8b235044453，与收据一致。26正式结构资源、I14–I18 NBT/布局及两个目录共10份对应Sponge与批准记录相符。本轮没有重复替换相同JAR。旧机器修订不再累计为新的五台，batch-07当前没有五台新批准。I19与I20候选不自动批准；用户当前条件授权不能据此虚造新批数量。</p>
<h2>本轮完成</h2><p>I20中型崩坏能反应堆QSV累积扩建候选V1：XYZ271×155×223，490,655实体；保留I19全部256,075块原位原状态及HBV颜色，新增234,580块，删除及异材覆盖为零。新主控[135,3,184]在整宽第136格，嵌真实联合仪控厅；旧主控与8旧接口原位保留。新增QSV敞口塔、圆顶核岛、燃料热室、泵房、联合控制厅与三段透平厅，16口按设备分布，无独立面板或托接口柱。</p><p>NBT/Sponge含空气全量逐格回读、实际尺寸、完整立方体、单一六面连通、六条维护道、主控与16口的净空/背接/静态步行操作位通过；独立复核中补齐燃料转运支线、透平回流端点和五道屋架。最终复核绑定当前蓝图与NBT身份，早期视审保留为历史，不冒充终稿身份。{len(before['files'])}份原I19/正式资源/实例模组文件SHA保持不变。</p>
<h2>未批准与未验收</h2><p>候选未获外观批准、未进入不可变确认归档或正式资源、未增加修订号。I20仅一条provisional能源计划，没有绑定真实I20控制器/Pattern的可执行燃料工艺，15条独立工艺及发电/热管理仍待实现。QSV主材有HDV工况源码路线，但RN-MCE/RN-SSQ研究仍provisional；完整材料祖先链与生存首建未验收。没有启动游戏或验证2.9.2，不把结构安装说成游戏运行通过。本地file页面自动化此前受协议策略限制，本轮未绕过；真实纹理静态图已审视。</p>
<p><a href="../../../deliveries/{OUT.name}/index.html">I20候选交付</a> · <a href="../../../deliveries/{archive.name}">ZIP</a> · <a href="../../../logs/i20-next-candidate-20261023/final-verification.json">最终校验</a> · <a href="2026-10-23_13-50-52_I01-I18居中融合V2正式实装修订175.html">上一批实装记录</a> · <a href="2026-10-23_16-40-58_I19单塔蓝湾候选与等待增强版2.9.2再实装.html">被本轮覆盖的等待升级决定</a></p><p>ZIP SHA256：<code>{sha(archive)}</code>。</p><p>变更#1：新增I20候选、六规则读取/独立检查、规则#11及本轮讨论；删除无；修改部署顺序为满五台先装2.9、升级后验兼容；用途为保留真实批次与候选边界。下一步由负责人审阅候选，后续按明确批准数量累计。</p></html>'''
    discussion.write_text(body, encoding='utf-8')
    result = {'time': now.isoformat(), 'candidate': str(OUT), 'blocks': record['data']['block_count'],
              'size_xyz': record['data']['size'], 'controller': record['data']['controller'], 'ports': len(record['data']['ports']),
              'blueprint_sha256': blueprint, 'hashes': audit['hashes'], 'protected_files_unchanged': len(before['files']),
              'candidate_approved': False, 'formal_resources_changed': False, 'instance_changed': False,
              'previous_batch_already_deployed': 'batch-06 I14–I18 r175 2.9', 'new_approved_batch_full': False,
              'zip': str(archive), 'zip_sha256': sha(archive), 'zip_files': len(identities)+1,
              'zip_all_bytes_verified': True, 'local_links_valid': True, 'discussion': str(discussion),
              'final_review_sha256': sha(LOG/'independent-final-review.json')}
    save(LOG/'final-verification.json', result)
    save(LOG/'protected-after.json', {'time': now.isoformat(), 'checked': len(before['files']), 'changed': altered})
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
