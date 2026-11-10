"""2026-09-28：核验已找到旧包的内部版本、哈希和CRC，只读原文件。"""
from pathlib import Path
from structure_delivery.project_paths import project_path
import datetime
import hashlib
import json
import re
import zipfile
from html import escape

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'logs/historical-build-search-20260928'
scan=json.loads((OUT/'scan-results.json').read_text(encoding='utf-8'))
rows=[]
sources=[]
for drive in scan['roots']:
    for c in drive['candidates']:
        p=project_path(c['path'])
        if 'Infinity Legacy II' in str(p):
            continue
        if c.get('match')=='source':
            s=p.read_text(encoding='utf-8',errors='replace')
            data={k:re.search(r'^'+k+r'\s*=\s*(.*)$',s,re.M).group(1) for k in ['mod_id','mod_version','mod_name','archives_base_name'] if re.search(r'^'+k+r'\s*=\s*(.*)$',s,re.M)}
            data={k:re.sub(r'\\u([0-9a-fA-F]{4})',lambda m:chr(int(m[1],16)),v) for k,v in data.items()}
            sources.append({'path':str(p),'properties':data})
        if not re.search(r'hk3|崩坏.*GTL|崩壞.*GTL',p.name,re.I) or '.jar' not in p.name.lower():
            continue
        if '0.5.0' in p.name or '内测5' in p.name:
            continue
        try:
            with zipfile.ZipFile(p) as z:
                names=z.namelist()
                toml=z.read('META-INF/mods.toml').decode('utf-8') if 'META-INF/mods.toml' in names else ''
                manifest=z.read('META-INF/MANIFEST.MF').decode('utf-8') if 'META-INF/MANIFEST.MF' in names else ''
                def field(k):
                    m=re.search(r'^\s*'+k+r'\s*=\s*"([^"]*)"',toml,re.M)
                    return m[1] if m else None
                if field('modId')!='hk3gtl':
                    rows.append({'path':str(p),'status':'非hk3gtl发布元数据','entries':len(names)})
                    continue
                timestamp=re.search(r'^Implementation-Timestamp:\s*(.*)$',manifest,re.M)
                rows.append({'path':str(p),'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                             'mod_id':field('modId'),'version':field('version'),'display_name':field('displayName'),
                             'build_timestamp':timestamp[1].strip() if timestamp else None,
                             'entries':len(names),'compiled_classes':sum(n.endswith('.class') for n in names),
                             'beta5_catalog_present':'data/hk3gtl/research/beta5_catalog.json' in names,
                             'crc_failure':z.testzip(),'game_tested':False})
        except (OSError,zipfile.BadZipFile,UnicodeError) as exc:
            rows.append({'path':str(p),'error':str(exc)})
payload={'time':datetime.datetime.now().astimezone().isoformat(),'jars':rows,'source_candidates':sources,
         'scope':'只读扫描C/D/E可访问目录文件名，再按项目名称筛选；未穷举无关压缩包内部，不跟随链接；系统拒绝访问目录未扫描；Infinity Legacy II不进行内容检查。',
         'listed_artifact_paths':sum(r['listed_artifact_paths'] for r in scan['roots']),
         'scan_errors':sum(r['error_count'] for r in scan['roots'])}
(OUT/'verified-builds.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(payload,ensure_ascii=False,indent=2))

# 变更#2：保存本轮检索讨论；用真实包元数据区分历史版本和沿用旧号的过渡包。
now=datetime.datetime.now().astimezone()
record=ROOT/'doc/HK3GTL-内测5/讨论记录'/(now.strftime('%Y-%m-%d_%H-%M-%S-%f')+'_内测1至4本机历史版本检索.html')
valid=[r for r in rows if r.get('mod_id')=='hk3gtl']
assert {'0.1.0','0.2.0','0.3.0','0.4.0'} <= {r['version'] for r in valid}
assert all(r['crc_failure'] is None for r in valid)
parts=['<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>内测1至4本机检索结果</title></head><body>',
       '<h1>内测1至4本机检索结果</h1>',
       '<p>记录时间：'+now.isoformat()+'；用户消息原始精确时间未知。用户要求在本机查找崩坏三GTL扩展内测1至4。本次暂停研究设计推进，执行只读检索。</p>',
       '<p>结论：内测1、2、3、4均找到含hk3gtl元数据及编译类的JAR，包内版本分别为0.1.0、0.2.0、0.3.0、0.4.0。另找到0.4.0-beta.1。以下哈希相同的路径属于同一份内容；不同哈希不擅自合并。</p>',
       '<p>验证：读取mods.toml与Manifest、计算SHA-256、遍历ZIP内容进行CRC检查。未执行旧模组，不证明可在当前原版/增强版实例正常加载；未更换、移动、删除原文件或部署。</p>']
groups={}
for r in valid:groups.setdefault(r['sha256'],[]).append(r)
for sha,group in groups.items():
    r=group[0]
    parts.append('<h2>'+escape(r['version'])+(' · 已含内测5研究目录，不能当作纯旧版基线' if r['beta5_catalog_present'] else '')+'</h2>')
    parts.append('<p>包内名称：'+escape(r['display_name'])+'；大小：'+str(r['size'])+'字节；编译类：'+str(r['compiled_classes'])+'；构建时间：'+escape(r['build_timestamp'] or 'Manifest未提供')+'；CRC通过。</p>')
    parts.append('<p>SHA-256：<code>'+sha+'</code></p><ul>')
    parts.extend('<li>'+escape(x['path'])+'</li>' for x in group)
    parts.append('</ul>')
parts.append('<h2>额外源码线索</h2>')
for source_row in sources:
    if source_row['properties'].get('mod_version') not in ['0.1.0','0.4.0-beta.1']:continue
    p=project_path(source_row['path']).parent
    java_count=len(list((p/'src/main/java').rglob('*.java')))
    parts.append('<p>'+escape(str(p))+'：'+escape(source_row['properties']['mod_version'])+'，'+str(java_count)+'份src/main/java源文件。仅有gradle.properties的目录不当作完整源码；未进行历史构建。</p>')
archive=ROOT/'archive/beta4-baseline-2026-09-22_13-33-45/pre-beta5-source.zip'
with zipfile.ZipFile(archive) as z:
    props=z.read('gradle.properties').decode('utf-8');assert 'mod_version=0.4.0-beta.1' in props
    assert z.testzip() is None
    parts.append('<p>'+escape(str(archive))+'：版本标记0.4.0-beta.1，含'+str(sum(n.endswith('.java') for n in z.namelist()))+'个Java条目，含构建脚本与源码资源，CRC通过；未验证可重建同一发布包。</p>')
parts.extend(['<h2>扫描范围与限制</h2><p>'+escape(payload['scope'])+'</p>',
              '<p>C/D/E枚举到'+str(payload['listed_artifact_paths'])+'条所筛选类型文件路径，记录'+str(payload['scan_errors'])+'条扫描错误。未读取认证配置或聊天内容，未穷举无关压缩包内部或执行数据恢复。</p>',
              '<p>详细路径、版本与哈希：logs/historical-build-search-20260928/verified-builds.json。仅新增检索脚本、日志与本讨论记录；原游戏与历史包未改动。</p>',
              '<p>后续研究系统讨论仍承接I44独立起步校准的已确认决定，本次查找不授权回退或删除任何版本。</p><footer>变更#1：新增检索与验证记录；删除无。</footer></body></html>'])
body='\n'.join(parts)
with record.open('x',encoding='utf-8') as f:f.write(body)
assert record.read_text(encoding='utf-8')==body
print(json.dumps({'discussion_record':str(record),'verified_versions':sorted(set(r['version'] for r in valid)),'jar_paths':len(valid),'distinct_hashes':len(groups),'read_back':True},ensure_ascii=False))
