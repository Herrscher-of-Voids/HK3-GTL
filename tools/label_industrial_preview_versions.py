# -*- coding: utf-8 -*-
"""变更记录 #1 · 2026-09-23 · 旧结构预览与首页明确转向最新占地方案。
原69座NBT保留为历史造型，不将旧尺寸原型冒充最新占地成品。
"""
from pathlib import Path
from datetime import datetime
root=Path(__file__).resolve().parents[1]
base=root/'doc/HK3GTL-内测5'
now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
index=base/'index.html'
s=index.read_text(encoding='utf-8')
start=s.index('<section id="beta5-latest-footprints">')
end=s.index('</section>',start)+len('</section>')
section=s[start:end]
s=s[:start]+s[end:]
anchor='<h1>HK3GTL · 内测5文档目录</h1>'
assert anchor in s
s=s.replace(anchor,anchor+section,1)
index.write_text(s,encoding='utf-8')
old=base/'03_机器结构/结构预览_v2/index.html'
s=old.read_text(encoding='utf-8')
assert '内测5_69座多方块逐台占地规划与比例预览_v2.html' not in s
anchor='<h1>内测5多方块结构预览 v2</h1>'
assert anchor in s
banner=f'<div class="panel hold"><strong>重要：本页仍使用旧工业树候选占地的69座几何原型；它们未按最新尺寸重建，也不作为最终建筑验收。</strong><p><a href="../内测5_69座多方块逐台占地规划与比例预览_v2.html">打开69座最新逐台尺寸与等比例占地俯视图</a>。占地外包新方案仍待结构逐台审核，旧3D原型、actual-nbt和浏览器预览保留为历史参考。</p><p>变更记录 #2 · {now} · 在旧原型预览首页标注版本差异和新规划入口；未修改旧NBT。</p></div>'
s=s.replace(anchor,anchor+banner,1)
old.write_text(s,encoding='utf-8')
record=max((base/'讨论记录').glob('*_69座多方块占地重设与离线预览.html'))
s=record.read_text(encoding='utf-8')
addition=f'<section><h2>补充导航核对 · {now}</h2><p>已在旧69台几何原型预览首页明显标注旧尺寸身份，并在内测5文档主页标题后展示最新逐台方案入口。旧NBT未被覆盖。离线预览已用本机Edge打开并核对页面渲染，脚本语法与69条尺寸、分级和相对链接均通过检查；未经Minecraft内实建/成型测试。</p></section>'
s=s.replace('</footer>',addition+'</footer>',1) if '</footer>' in s else s+addition
record.write_text(s,encoding='utf-8')
print('Updated index and historical preview navigation',now)

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
