/** 记录截图所示接口座单格移动，核对差异边界后更新指定实例结构副本。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
const root=process.cwd();
const base=path.join(root,'doc/HK3GTL-内测5/03_机器结构/初期四机外观重设计_v2');
const previous=path.join(root,'archive/i03-interface-shift-2026-09-25/i03');
const before=JSON.parse(await fs.readFile(path.join(previous,'blueprint.json'),'utf8'));
const after=JSON.parse(await fs.readFile(path.join(base,'i03/blueprint.json'),'utf8'));
const a=new Map(before.blocks.map(b=>[b.pos.join(','),b.state]));
const b=new Map(after.blocks.map(b=>[b.pos.join(','),b.state]));
const changes=[...new Set([...a.keys(),...b.keys()])].filter(k=>a.get(k)!==b.get(k));
for(const k of changes){const [x,y,z]=k.split(',').map(Number);if(x<2||x>5||y<1||y>3||z<2||z>5)throw Error('变更超出接口座范围：'+k);}
if(after.ports.find(p=>p.id==='M1').pos.join(',')!=='4,2,2')throw Error('接口移动错误');
const name=after.name+'.schem',source=await fs.readFile(path.join(base,'i03',name));
const old=await fs.readFile(path.join(previous,name));
const sha256=crypto.createHash('sha256').update(source).digest('hex');
const list=JSON.parse(await fs.readFile(path.join(base,'实例交付校验.json'),'utf8'));
for(const entry of list.filter(e=>e.machine==='i03')){
  const current=await fs.readFile(entry.destination);
  if(!current.equals(old)&&!current.equals(source))throw Error('实例文件存在未知修改：'+entry.destination);
  await fs.writeFile(entry.destination,source);
  if(!(await fs.readFile(entry.destination)).equals(source))throw Error('复制校验失败');
  entry.sha256=sha256;
}
await fs.writeFile(path.join(base,'实例交付校验.json'),JSON.stringify(list,null,2),'utf8');
const entryPath=path.join(base,'评审入口.html');let html=await fs.readFile(entryPath,'utf8');
const note='<div class="note" id="port-shift">2026-09-25 02:09 修订：截图红圈的前侧物品接口座 M1，按截图向左整体移动一格（本地 X：3→4）；底座、钻石矿接口标记和连接管同步移动。其他建筑构件及功能不变。结构双格式回读、通道净空和接口可达性通过。<a href="i03/三维评审.html">查看更新预览</a></div>';
if(!html.includes('id="port-shift"'))html=html.replace('<nav>',note+'<nav>');
await fs.writeFile(entryPath,html,'utf8');
const record=path.join(root,'doc/HK3GTL-内测5/讨论记录/2026-09-25_02-09_I03前侧接口座左移一格.html');
await fs.writeFile(record,`<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>I03前侧接口座左移一格</title><body><h1>I03前侧接口座左移一格</h1><p>2026-09-25 02:09，Asia/Hong_Kong。</p><p>负责人要求：按截图将红圈接口座向左移一格。已按前左视图方向将M1本地X从3移动到4，Y=2、Z=2保持；底座与连接管同步移动。用途、接口方向、其余结构和机器功能不变。</p><p>局部逐格差异${changes.length}处，均位于X=2..5、Y=1..3、Z=2..5；结构文件及预览同源更新。旧版本归档于archive/i03-interface-shift-2026-09-25，指定实例的两个结构副本同步并核对哈希。</p><p>未决：建筑Pattern仍待接入，未进行游戏内成型测试。本次未改Java、配方或游戏存档。来源为用户标注截图与既有I03结构，无新增外部资源或许可。</p><p><a href="../03_机器结构/初期四机外观重设计_v2/评审入口.html">评审入口</a></p></body></html>`,'utf8');
console.log(JSON.stringify({changedCells:changes.length,port:after.ports.find(p=>p.id==='M1'),sha256,copied:2}));
