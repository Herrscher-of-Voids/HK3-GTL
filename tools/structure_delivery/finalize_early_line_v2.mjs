/** 生成中文评审入口、材料数量、独立讨论记录和指定实例交付清单；不操作游戏或旧存档。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const relative='doc/HK3GTL-内测5/03_机器结构/初期四机外观重设计_v2';
const out=path.join(root,relative);
const manifest=JSON.parse(await fs.readFile(path.join(out,'manifest.json'),'utf8'));
const symmetry=JSON.parse(await fs.readFile(path.join(out,'I03对称性与尺寸核验.json'),'utf8'));
const style=`body{max-width:1320px;margin:auto;padding:28px;background:#0b1020;color:#e9effb;font:16px/1.8 'Microsoft YaHei',sans-serif}h1,h2,h3,a{color:#83e8e0}a{overflow-wrap:anywhere}nav,.note,section{padding:20px;background:#141e31;border:1px solid #35455f;margin:20px 0;border-radius:8px}.note{border-left:4px solid #e5bc70}table{border-collapse:collapse;width:100%}td,th{border:1px solid #35455f;padding:10px;text-align:left}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:16px}img{max-width:100%;border:1px solid #394c66}figure{margin:0}code{color:#efcd94}small{color:#a7bad3}button{cursor:pointer}ul{padding-left:22px}`;
const descriptions={
  i01:'上扬雷达锅、纵向采集主轴与镜像处理双翼。保留采样物品输入、液态输出以及原有额外物品能力；两侧检修带保持净空。',
  i02:'双光路镜像阵列与高位扫描桥，中央三格宽检修廊贯通。保留物品输入／输出与两个可选物品接口；不新增流体或并行仓要求。',
  s01:'双翼实验厅、中央操作廊和后部阶梯认知穹顶。研究点／材料仍通过既有研究系统与玩家背包支付；两处后接口仅表达原有可选有线／无线崩坏能输入。',
  i03:'保留高分馏柱、低位净化舱、滤芯柜、冷凝支路与十字检修带的功能分区，修正柜体中心和局部镜像，收短净化舱。'
};
const cards=[],rows=[],materialRows=[];
for(const m of manifest){
  const [w,h,d]=m.size;
  const audit=JSON.parse(await fs.readFile(path.join(out,m.key,'audit.json'),'utf8'));
  const markers=Object.entries(audit.palette).filter(([k])=>k.startsWith('minecraft:')).reduce((s,[,v])=>s+v,0);
  const gt=Object.entries(audit.palette).filter(([k])=>k.startsWith('gtceu:')||k.startsWith('gtlcore:')).reduce((s,[,v])=>s+v,0);
  const custom=Object.entries(audit.palette).filter(([k])=>k.startsWith('kubejs:')).reduce((s,[,v])=>s+v,0);
  const normal=m.blocks-markers;
  materialRows.push(`<tr><td>${m.key.toUpperCase()}</td><td>${gt}（${(gt/normal*100).toFixed(2)}%）</td><td>${custom}（${(custom/normal*100).toFixed(2)}%）</td><td>0</td><td>0</td><td>${markers}</td></tr>`);
  rows.push(`<tr><td><a href="#${m.key}">${m.title}</a></td><td>${w} × ${d} × ${h}</td><td>${w*d} 格²</td><td>${m.blocks}</td><td>${m.ports.length}</td></tr>`);
  cards.push(`<section id="${m.key}"><h2>${m.title}</h2><p>${descriptions[m.key]}</p><p><a href="${m.key}/三维评审.html"><strong>打开可旋转三维预览</strong></a>　·　<a href="${m.key}/${m.name}.schem">下载／打开 Sponge 结构</a>　·　<a href="${m.key}/${m.name}.nbt">原版 NBT</a>　·　<a href="${m.key}/audit.json">逐格与通道核验</a></p><div class="grid">${[['01_前左整体','整体造型'],['04_俯视布局','俯视占地'],['06_正前投影','正前正交投影'],['08_控制器特写','专用控制器']].map(([f,t])=>`<figure><a href="${m.key}/${f}.png"><img loading="lazy" src="${m.key}/${f}.png" alt="${m.title} ${t}"></a><figcaption>${t}</figcaption></figure>`).join('')}</div><p>主控 (8,2,2)，正面 -Z。接口坐标和访问面见三维页；钻石矿为接口标记，钻石块为主控标记。</p></section>`);
}
const instance='C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech-Leisure-1.4.5.2/minecraft';
const copies=[];
for(const m of manifest)for(const suffix of ['schematics','config/worldedit/schematics']){
  const src=path.join(out,m.key,m.name+'.schem'),dst=path.join(instance,suffix,m.name+'.schem');
  const bytes=await fs.readFile(src),hash=crypto.createHash('sha256').update(bytes).digest('hex');
  await fs.mkdir(path.dirname(dst),{recursive:true});
  let existing;try{existing=await fs.readFile(dst);}catch(e){if(e.code!=='ENOENT')throw e;}
  if(existing&&!existing.equals(bytes))throw Error('目标已有不同内容，停止覆盖：'+dst);
  if(!existing)await fs.writeFile(dst,bytes);
  if(!bytes.equals(await fs.readFile(dst)))throw Error('复制校验失败：'+dst);
  copies.push({machine:m.key,destination:dst,sha256:hash});
}
await fs.writeFile(path.join(out,'实例交付校验.json'),JSON.stringify(copies,null,2),'utf8');
const html=`<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>初期四机外观重设计 v2 · 评审入口</title><style>${style}</style></head><body>
<h1>初期四机外观重设计 · v2</h1><p>2026-09-25 · Asia/Hong_Kong · HK3GTL 内测5第一条工业线</p>
<nav><a href="#i01">采集塔</a>　<a href="#i02">光谱阵列</a>　<a href="#s01">一阶研究所</a>　<a href="#i03">分馏中心</a>　<a href="#compare">I03 新旧对比</a>　<a href="#controllers">控制器</a>　<a href="#validation">验证范围</a></nav>
<div class="note"><strong>本次交付：四台实际逐格建筑、Sponge／NBT 文件、对应三维页和32张多角度预览截图；四台专用控制器纹理已接入 Java 渲染定义。</strong><p>这些是建筑评审文件，主控和接口仍使用规定的钻石标记。当前 Java Pattern 没有迁移到新版建筑，不能仅替换钻石块就认定机器可成型。现有工艺、配方、研究扣费及运行逻辑未改。</p></div>
<table><tr><th>设备</th><th>宽 X × 长 Z × 高 Y</th><th>外接占地</th><th>实体格数</th><th>接口标记</th></tr>${rows.join('')}</table><p>原点为前左下角，前方 -Z；尺寸包含两端方块。四台均属普通级，分级按最大水平边长。三维页支持旋转、缩放、分层、隐藏玻璃、正交观察和原始钻石标记切换。</p>
${cards.join('')}
<section id="compare"><h2>I03：旧版与新版同视角对比</h2><p>下列图片是离线预览器的实际渲染截图，不是游戏截图；采用实例资源的首帧纹理，游戏动态染色与照明尚未复现。</p><div class="grid"><figure><a href="../I03分馏中心实物样例_v1/I03分馏中心_三维评审.html"><img src="../I03分馏中心实物样例_v1/01_前左整体.png"><figcaption>旧版 v1，点击交互查看</figcaption></a></figure><figure><a href="i03/三维评审.html"><img src="i03/01_前左整体.png"><figcaption>新版 v2，点击交互查看</figcaption></a></figure></div>
<h3>尺寸与对称性结论</h3><ul><li><strong>低位净化舱：宽 X=11，长 Z=7。</strong>外壳 X=3..13、Z=5..11，原版 Z=5..12 为8格。舱体 Y=3..10（8格高），屋顶附属件仍到 Y=11；包含下部支座为 Y=1..11（11格）。相邻转送桥属于连接构件，不计入净化舱外轮廓。</li><li>两座滤芯柜改为宽5、深3、高8，X=19..23，Z分别为5..7和9..11，关于 Z=8 镜像，维护窗均朝 -X。中心 X=21 与上方管线对齐，消除旧4格柜体中心20.5与管线21之间的半格偏移。</li><li>旧柜体按其原镜像平面 Z=9 核对，96个比较位置中有 ${symmetry.cabinets.old.differenceCount} 处材质／有无方块差异，属于实际布局差异，不能全部归因于视角。新版柜体120个对应位置差异为0。</li><li>净化舱689个、主柱2658个对应位置比较差异为0；分别排除明确记录的右侧歧管入口和冷凝支路入口及镜像位置。整机不同分区承担不同功能，未强制整机左右对称。</li><li>主柱中轴是原脚本明确生成的回流内芯，并非误加。保留 X=8、Z=21、Y=3..20 的贯通轴，恢复 Y=6、11、16 的分离盘节点。它表达建筑工艺，不是另加一套运行逻辑。</li></ul><p><a href="I03对称性与尺寸核验.json">查看逐格比较范围、例外坐标与完整结果</a></p></section>
<section id="controllers"><h2>四机控制器：统一机壳，四种独立符号</h2><p>64×64原创像素纹理：深紫金属壳、银色边框、金色内框、青色显示与状态灯。采集塔为雷达、光谱阵列为棱镜、分馏中心为分流管路、研究所为研究节点。均提供空闲／运行／暂停状态，保留旧贴图目录供追溯。</p><img src="四机控制器对比.png" alt="四机控制器三状态对照"><p>Java绑定文件：<code>Hk3MachinesImpl.java</code>、<code>Hk3MachinesAbyssStage.java</code>。新资源：<code>textures/block/casings/industrial_controller_shell.png</code> 与 <code>textures/block/overlay/{i01,i02,i03,s01}_v2/</code>。</p></section>
<section><h2>材料与接口衔接</h2><p>统一使用 MAX 机壳、分子机械方块、计算机机壳、高功率机壳、超导线圈、聚变／层压玻璃及中子素管道机壳／齿轮箱；全部为已核对模型的完整立方体。建筑调色板无旧版 HK3GTL 海渊方块。百分比以普通实体建材统计，钻石标记单列。</p><table><tr><th>设备</th><th>GTCEu／GTLCore</th><th>KubeJS</th><th>其他模组</th><th>原版普通建材</th><th>标记格数</th></tr>${materialRows.join('')}</table><p>所有仓位保持对应资源类别；同类输入／输出位置可在后续 Pattern 实现中互换，物品仓不被标为流体仓。I03仍为6流体位、3物品位、1可选并行位。研究所没有改成仓内扣材料，也没有引入必须的物品仓或实体EU能源仓。</p><p>本轮保留既有材料审计的覆盖缺口：动态配方、全部前置与生存可达阶段未完整复核，不能称为生存材料链验收通过。详细来源见各台 materials.json／audit.json。</p></section>
<section id="validation"><h2>验证与实施边界</h2><ul><li>四台 Sponge v2 与原版 NBT 回读一致，尺寸、索引、调色板、完整方块模型和禁用材料检查通过。</li><li>四台全部维护通道净空和19处接口、4处主控的行走可达性检查通过。</li><li>四台离线预览页验证通过，无脚本异常；共32张截图，含俯视、正交投影、剖面和控制器近看。</li><li><code>gradlew.bat --gradle-user-home .gradle-home-task67 compileJava processResources --offline</code> 通过；存在项目原有弃用API警告。</li><li><strong>未启动游戏、未改存档、未替换运行中的模组JAR。</strong>未修改配方或机器运行逻辑。</li><li>现有研究所 Pattern 仍为3×3×3，规划建筑为17×25×17；本轮按规划制作建筑，未冒充其已经匹配原 Pattern。其余三台同样待新版建筑 Pattern 接入及全新存档成型验收。</li></ul><p><a href="实例交付校验.json">指定实例两个结构目录的复制校验</a> · <a href="manifest.json">四台结构清单与哈希</a></p><p>四个新文件已复制到指定 GTL 实例的 <code>minecraft/schematics</code> 和 <code>minecraft/config/worldedit/schematics</code>；可刷新 Forgematica 列表，加载名称含 <code>v2</code> 的对应文件。原文件保留。后续实机测试必须新建允许作弊的超平坦创造存档，不操作 Infinity Legacy II。</p></section>
<section><h2>来源、复现与记录</h2><p>依据：原 I03 实物样例及关联设计资料、内测5第一条工业线步骤指南、当前机器注册与研究代码、巨构提示词规范和本次明确修改要求。三维采用实例 GTCEu／GTLCore／KubeJS 材质，权利归原作者，仅本地评审；Three.js 许可见本目录文本。</p><p>确定性结构源码：<code>early-line-buildings-v2.mjs</code>、<code>i03-fractionation-v2.mjs</code>；生成、打包与验证工具均在 <code>tools/structure_delivery/</code>。控制器脚本只生成本轮原创纹理。所有新文本使用 UTF-8。</p></section></body></html>`;
await fs.writeFile(path.join(out,'评审入口.html'),html,'utf8');
const oldEntry=path.join(out,'../I03分馏中心实物样例_v1/评审入口.html');
let old=await fs.readFile(oldEntry,'utf8');
if(!old.includes('id="four-machine-v2"'))old=old.replace('<body>','<body><div class="note" id="four-machine-v2"><strong>此页为历史 v1。</strong> <a href="../初期四机外观重设计_v2/评审入口.html">打开最新四机外观重设计 v2 与 I03 修正对比</a>；历史文件继续保留。</div>');
await fs.writeFile(oldEntry,old,'utf8');
const recordDir=path.join(root,'doc/HK3GTL-内测5/讨论记录');
await fs.mkdir(recordDir,{recursive:true});
await fs.writeFile(path.join(recordDir,'2026-09-25_01-53_四机外观重设计与I03结构修正.html'),`<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>四机外观重设计与I03结构修正</title><style>${style}</style><body><h1>四机外观重设计与I03结构修正</h1><p>2026-09-25 01:53，Asia/Hong_Kong。本轮负责人已授权制作，建筑效果仍待评审，不等同于确认最终外观。</p><h2>要求与落实</h2><p>重设计I01、I02、一阶研究所建筑及四台控制器；I03净化舱改为外轮廓长7宽11，核对对称、滤芯柜与中轴，结构文件与预览同步。已完成建筑文件、三维预览、镜像审计和控制器资源绑定，编译通过。</p><h2>范围与禁止推测</h2><p>不更改机器工艺、配方或研究扣费；保留旧文件供比对。中轴经原脚本确认是回流内芯，保留并恢复分离节点。不同工艺分区不强行整机镜像。不将投影或静态验证写成游戏内成型。不复用旧存档，不操作另一整合包。</p><h2>待确认和后续</h2><p>负责人外观评审待确认；新版Pattern尚未接入，研究所旧3立方结构与规划尺寸不一致已公开记录。生存材料链、运行时纹理、真实成型和工艺运行需后续验证。</p><h2>文件与来源</h2><p><a href="../03_机器结构/初期四机外观重设计_v2/评审入口.html">完整交付、来源、核验记录和截图</a>。参考第一条工业线步骤指南、原I03样例、机器设计资料、巨构提示词和指定实例模组资源。原创控制器纹理；外部模组材质仅本地评审，未对外发布，Three许可随目录保留。</p></body></html>`,'utf8');
console.log(JSON.stringify({entry:path.join(out,'评审入口.html'),copies:copies.length,htmlBytes:Buffer.byteLength(html)}));

// 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名及工具互引同步，保留历史证据路径。
