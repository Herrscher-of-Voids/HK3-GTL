"""Finalize batch7 HTML evidence only after successful game registry audit and entry screenshot.
Change #1 2026-09-22: record actual validation and include every changed file with clickable paths.
No source/resource changes; final built artifact remains unchanged.
"""
from pathlib import Path
from datetime import datetime
import json, re, hashlib, html, shutil
ROOT=Path(__file__).resolve().parents[1]
DOC=ROOT/'doc/HK3GTL-内测5/09_测试发布'
def logtext(path):
    b=path.read_bytes(); return b.decode('utf-16' if b[:2] in (b'\xff\xfe',b'\xfe\xff') else 'utf-8',errors='replace')
runtime=logtext(ROOT/'run-beta5-batch7-final.log'); build=logtext(ROOT/'build-beta5-batch7-final.log')
assert 'PASS: 238 physical entries, world server started' in runtime
assert 'BUILD SUCCESSFUL' in build
missing=[line for line in runtime.splitlines() if 'hk3gtl' in line and any(x in line for x in ('Missing textures in model','Unable to load model','Using missing texture'))]
assert not missing,missing
stamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
files=set(json.loads((ROOT/'tools/industrial_batch7_changed_files.json').read_text(encoding='utf-8')))
for p in (ROOT/'archive/beta5-batch7-before').rglob('*'):
    if p.is_file(): files.add(p.relative_to(ROOT/'archive/beta5-batch7-before').as_posix())
for rel in ['src/main/java/com/sirin/hk3gtl/common/registration/Hk3ContentRegistryAudit.java',
            'tools/industrial_content_catalog.py','tools/generate_industrial_content.py','tools/industrial_batch7_record.py','tools/industrial_batch7_finish.py','tools/industrial_game_smoke.py',
            'doc/HK3GTL-内测5/09_测试发布/代码落实进度与旧实现归档.html',
            'doc/崩坏三-GTL/00_项目总览/模组全面系统性分析报告.html',
            'doc/HK3GTL-内测5/讨论记录/2026-09-22_16-33_物理内容注册贴图与入游戏优先.html',
            'src/main/resources/assets/hk3gtl/changelog.json']: files.add(rel)
(ROOT/'tools/industrial_batch7_changed_files.json').write_text(json.dumps(sorted(files),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
jar=next(p for p in (ROOT/'build/libs').glob('*.jar') if not any(x in p.name for x in ('sources','dev','shadow')))
sha=hashlib.sha256(jar.read_bytes()).hexdigest()
report=DOC/'物品流体方块注册与贴图_批次7.html'; s=report.read_text(encoding='utf-8')
start=s.index('<h2 id="files">')
s=s[:start]+f'<h2>验证结果 · {stamp}</h2><p>clean build --offline通过，20任务执行；现有回归组通过。最终开发客户端（Forge 47.4.16、GTCEu 1.4.4、36模组）进入独立测试世界，238项真实物理注册含桶全部通过。新目录没有hk3gtl缺失模型/纹理警告。其他模组有既有材质和配方警告，不声称完整整合包零警告。</p>'
s+='<p>本次使用开发客户端，没有替换正在运行的Prism实例JAR，没有打开玩家旧存档。测试世界名称包含HK3GTL-Beta5-Registry-Smoke。验证范围为注册与启动，不是生产流程、终局或多方块成型验收。</p>'
s+='<p>尚未覆盖：最终建筑对应的新机器控制器、四种功能终端、更高阶研究所控制器的完整实现与模型；这些必须结合后续真实机器逻辑和逐台结构设计落实，本批没有用普通方块假冒它们。因此本批不能表述为全部内测5注册已最终完成。</p>'
s+=f'<p>构建产物：{html.escape(jar.name)}（沿用旧构建名，未发布）；SHA256：<code>{sha}</code>。</p>'
for name in ('内测5游戏内注册验证.png','内测5游戏内物品验证.png','内测5游戏内流体验证.png','内测5游戏内方块验证.png'):
    if (DOC/name).exists(): s+=f'<p><img src="{name}" alt="游戏内验证"></p>'
s+='<h2 id="files">完整改动文件</h2><p>新增Java均有双语说明；修改Java保留历史备注并追加批次7记录。JSON/PNG统一由本HTML说明，原文件备份在archive/beta5-batch7-before。</p><ul>'
s+=''.join(f'<li><a href="../../../../{html.escape(p)}">{html.escape(p)}</a></li>' for p in sorted(files))+'</ul></html>'
s=s.replace('构建及游戏验证待执行。','构建及游戏注册验证通过，范围限制见后文。')
report.write_text(s,encoding='utf-8')
for p in [DOC/'代码落实进度与旧实现归档.html',ROOT/'doc/崩坏三-GTL/00_项目总览/模组全面系统性分析报告.html']:
    s=p.read_text(encoding='utf-8')
    note=f'<p>批次7验证补记 {stamp}：最终clean build通过；开发客户端启动测试世界，238物理条目核验PASS。新增控制器及功能终端不在此次完成范围，注册工作尚不能视为整个内测5全部完成。</p>'
    p.write_text(s.replace('</body>',note+'</body>') if '</body>' in s else s+note,encoding='utf-8')
print(f'Final report: {len(files)} changed-file links; SHA256 {sha}')

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
