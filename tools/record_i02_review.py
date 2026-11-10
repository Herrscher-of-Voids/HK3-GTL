# -*- coding: utf-8 -*-
"""Change #1 2026-09-23: approved I02 direction, generated building, pending final acceptance.
记录结构证据与本地预览资源来源；不将建筑稿称为运行机器。
"""
from pathlib import Path
from datetime import datetime
import json,html,shutil,zipfile
root=Path(__file__).resolve().parents[1]
out=root/'doc/HK3GTL-内测5/03_机器结构/I02结构审核_v1'
stamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
b=json.loads((out/'blueprint.json').read_text(encoding='utf-8'))
palette=sorted(b['counts'].items())
style='body{max-width:1150px;margin:auto;padding:28px;background:#10182a;color:#e1edf8;font:16px/1.8 system-ui}a{color:#8adfe9}h1,h2{color:#a9b8ff}section{padding:20px;border:1px solid #3c5068;margin:18px 0;border-radius:12px}img{max-width:100%}td,th{padding:7px;border-bottom:1px solid #3b4b63;text-align:left}table{width:100%}code{overflow-wrap:anywhere}.go{display:inline-block;background:#304863;padding:14px;border-radius:8px}strong{color:#ffe39c}'
body=f'''<h1>I02 样本光谱分析阵列 · 完整建筑审核</h1><p>{stamp} · Asia/Hong_Kong</p>
<p><a class="go" href="http://127.0.0.1:5182/">打开可旋转、可截层的实际材质预览</a></p>
<section><h2>本轮交付</h2><p><strong>17宽 × 21长 × 17高，1,587个方块。</strong>独立完成双光谱廊、中央样品舱、三道上部校准横架、前侧台阶与控制台、底层分流管路、后侧仪器柜，以及两侧检修环路。此前的曲线占位稿保留，但本结构从零重新设计。</p><p>负责人已通过建筑方向；这一份完整建筑仍待外观审核。控制台和接口为位置预留，<strong>尚未注册I02运行控制器，未接实验配方，未迁移GTCEu Pattern</strong>。</p></section>
<section><h2>怎么查看</h2><ol><li>点击上面的预览入口，拖动鼠标旋转，滚轮缩放。</li><li>点击右上方正面、背面、侧面、俯视按钮。</li><li>拖动左上角截层滑块，停在Y5查看检修通道，停在Y11查看光谱廊与样品舱内部，回到Y16显示完整建筑。</li><li>电脑重启后若网页打不开，在此目录双击“打开I02预览.cmd”，它会启动本地服务并打开网页。</li></ol><p>机壳、管道、玻璃和警示方块采用目标实例GTCEu贴图；浏览器的光照和玻璃连接效果仍可能与Minecraft不同。</p></section>
<section><h2>结构检查</h2><ul><li>所有方块位于17×17×21的NBT包围盒内。</li><li>以X8为中轴逐方块验证左右镜像，原版连接属性随后由Lodestone补全。</li><li>两侧X1–2／X14–15及前后联络道的Y3–5逐格为空，目标净宽2格、净高3格。</li><li>5种模组方块均有预览资源映射，且预览别名不与建筑实际原版方块冲突。</li><li>浏览器完整视图和截层功能已检查。未在玩家世界放置，未进行成型验收。</li></ul></section>
<section><h2>完整文件</h2><ul><li><a href="i02-spectrum-array-v1.nbt">原始完整结构NBT</a>：真实模组ID，不包含临时控制器注册。</li><li><a href="blueprint.json">逐方块坐标与接口位置</a>；<a href="palette-sources.json">材质来源和实例JAR校验值</a>。</li><li><a href="i02-review-datapack.zip">独立预览数据包</a>：不自动放置，也未安装到存档。仅在空白测试区域手动使用，模板名hk3gtl_review:i02_spectrum_array。</li><li><a href="../../../../tools/build_i02_review.mjs">建筑生成脚本</a>。</li></ul></section>
<section><h2>方块清单</h2><table><tr><th>方块／状态</th><th>数量</th></tr>{''.join('<tr><td><code>'+html.escape(k)+'</code></td><td>'+str(v)+'</td></tr>' for k,v in palette)}</table></section>
<section><h2>来源与许可</h2><p>建筑设计为本项目原创。NBT由已安装的minecraft-builder-skill及Lodestone生成；本地查看器衍生自该Skill，保留原许可文件。5种GTCEu方块材质从指定实例gtceu-1.20.1-1.4.4.jar本地提取，仅供此次本机预览，没有上传或发布这些资源；不将本次提取视为获得再分发授权。默认材质包自带LICENSE.md保留于viewer/public/pack。</p><p>开发范围：新增建筑、预览及审核文档，未修改游戏Java、研究数据或实例存档，修订61模组包保持原样。</p></section>'''
image=Path('C:/Users/OWNER/AppData/Local/Temp/hk3-i02-final.png')
if image.exists():
    shutil.copy2(image,out/'完整预览.png')
    body+='<section><h2>完整建筑预览</h2><img src="完整预览.png" alt="I02完整建筑浏览器渲染截图"></section>'
page=f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I02完整建筑审核</title><style>{style}</style>{body}<footer>变更记录 #1 · {stamp} · 完整建筑候选；负责人实景审核待完成。</footer></html>'
(out/'审核入口.html').write_text(page,encoding='utf-8')
ps='''# Change #1: start only this loopback preview; never modify game saves.
$ErrorActionPreference = 'Stop'
$url = 'http://127.0.0.1:5182/'
$scriptPath = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\\..\\..\\..\\tools\\serve_i02_preview.mjs'))
$ready = $false
try { $catalog = Invoke-RestMethod ($url + '__minecraft_builder__/catalog.json'); $ready = $catalog.defaultId -eq 'I02' } catch {}
if (-not $ready) {
    Start-Process -FilePath 'node' -ArgumentList ('"' + $scriptPath + '"') -WindowStyle Hidden
    for ($i=0; $i -lt 20; $i++) {
        Start-Sleep -Milliseconds 500
        try { $catalog = Invoke-RestMethod ($url + '__minecraft_builder__/catalog.json'); if ($catalog.defaultId -eq 'I02') { $ready=$true; break } } catch {}
    }
}
if (-not $ready) { throw 'I02 preview could not start on port 5182.' }
Start-Process $url
'''
(out/'start-preview.ps1').write_text(ps,encoding='utf-8-sig')
(out/'打开I02预览.cmd').write_text('@echo off\r\npowershell -NoProfile -File "%~dp0start-preview.ps1"\r\n',encoding='utf-8')
record=root/'doc/HK3GTL-内测5/讨论记录'/f'{datetime.now():%Y-%m-%d_%H-%M}_I02结构方向确认与完整建筑待审.html'
record.write_text(f'<!doctype html><meta charset="utf-8"><title>I02方向确认与建筑待审</title><style>{style}</style><h1>I02方向确认与完整建筑待审</h1><p>{stamp} · Asia/Hong_Kong</p><section><h2>要求与结论</h2><p>负责人在GUI与I02风格审核稿交付后回复“ok”。按当前审核节点，确认I02双光谱廊＋中央样品舱、17×21×17和检修环路方向，继续制作这一台完整建筑；不将该回复视为尚未生成建筑的最终验收，也不视为GUI运行验证。</p><h2>执行</h2><p>使用minecraft-builder-skill生成1,587方块完整NBT；5种GTCEu方块本地纹理预览、截层、逐方块清单、数据包及启动入口已整理。具体内容见<a href="../03_机器结构/I02结构审核_v1/审核入口.html">结构交付页</a>。</p><h2>否决与边界</h2><p>不使用旧曲线占位稿，不复制旧结构接实验链，不修改玩家世界，不免费授予研究，不把建筑控制台冒充可运行控制器。</p><h2>待确认与后续</h2><p>负责人检查完整建筑后提出修改或验收；通过后才能进行Pattern与实验入口接入。I03/I04仍逐台审核。</p><h2>来源和风险</h2><p>工业树v5、I02结构审核稿v1、已安装Skill、目标实例GTCEu JAR；材质资源仅本地预览，许可说明见交付页。浏览器玻璃和光照与游戏可能不同，注册、配方可达性及结构成型需后续实机验证。</p></section>',encoding='utf-8')
draft=root/'doc/HK3GTL-内测5/03_机器结构/I02样本光谱分析阵列_结构审核稿_v1.html'
s=draft.read_text(encoding='utf-8'); s=s.replace('</html>',f'<section><h2>追加记录 #2 · {stamp}</h2><p>方向已确认，完整建筑现已生成；<a href="I02结构审核_v1/审核入口.html">进入本轮完整建筑审核</a>。完整结构最终验收仍待负责人确认。</p></section></html>');draft.write_text(s,encoding='utf-8')
report=root/'doc/崩坏三-GTL/00_项目总览/模组全面系统性分析报告.html'
s=report.read_text(encoding='utf-8'); entry=f'<section><h2>I02建筑候选 · {stamp}</h2><p>17×21×17，1,587方块；完成NBT与真实模组贴图本地预览，镜像及2×3检修净空检查通过。完整建筑待负责人审核，未部署世界、未注册I02控制器、未接RN-HSA实验链。游戏代码与修订61包未改动。</p></section>';s=s.replace('</body>',entry+'</body>') if '</body>' in s else s+entry;report.write_text(s,encoding='utf-8')
print(out/'审核入口.html')
