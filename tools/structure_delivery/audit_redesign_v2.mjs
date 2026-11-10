/** 对实际逐格数据进行镜像和尺寸检查，明确排除工艺连接，不把整机误称为完全对称。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createBlueprint as current} from './i03-fractionation-v2.mjs';
import {createBlueprint as previous} from './i03-fractionation-v1.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const out=path.join(root,'doc/HK3GTL-内测5/03_机器结构/初期四机外观重设计_v2');
function mirror(data,min,max,axis,twiceCenter,exclude=()=>false){
  const map=new Map(data.blocks.map(b=>[b.pos.join(','),b.state])),differences=[];let compared=0;
  for(let y=min[1];y<=max[1];y++)for(let z=min[2];z<=max[2];z++)for(let x=min[0];x<=max[0];x++){
    const p=[x,y,z],q=[x,y,z];q[axis]=twiceCenter-p[axis];
    if(exclude(p)||exclude(q))continue;compared++;
    const a=map.get(p.join(','))??'minecraft:air',b=map.get(q.join(','))??'minecraft:air';
    if(a!==b)differences.push({p,q,a,b});
  }
  return {compared,differenceCount:differences.length,differences};
}
const v1=previous(),v2=current();
const report={
  coordinateConvention:'坐标顺序 X/Y/Z；前方 -Z；宽沿 X；长沿 Z；外轮廓端点均计入。',
  purifier:{width:11,length:7,bodyHeight:8,bodyMin:[3,3,5],bodyMax:[13,10,11],roofTop:11,includingSupportsHeight:11,
    oldLength:8,exclude:'右侧歧管在 (12..13,9,8) 进入壳体；仅排除这两个位置及镜像位置，不排除其他缺块。',
    mirror:mirror(v2,[3,3,5],[13,11,11],0,16,p=>p[1]===9&&p[2]===8&&[3,4,12,13].includes(p[0]))},
  cabinets:{old:mirror(v1,[19,1,6],[22,8,8],2,18),current:mirror(v2,[19,1,5],[23,8,7],2,16),
    dimensions:[5,8,3],mirrorPlane:'Z=8',serviceFaces:'两座均朝 -X；前后镜像不反转检修朝向。'},
  tower:{shell:mirror(v2,[3,3,16],[13,24,26],0,16,p=>p[1]===17&&p[2]===20&&[3,4,12,13].includes(p[0])),
    exclude:'右侧冷凝支路在 X=12..13,Y=17,Z=20 进入塔身；其镜像位置不要求设置一条无用途支路。',
    axis:v2.blocks.filter(b=>b.pos[0]===8&&b.pos[2]===21&&b.pos[1]>=3&&b.pos[1]<=20),
    purpose:'原生成器显式设置的中央回流内芯；属于建筑工艺表达，无独立游戏逻辑。保留贯通轴并恢复 Y=6、11、16 分离盘节点。'},
  wholeMachine:'左右分区承担不同工艺；不要求整机左右镜像。净化舱、滤芯柜与塔壳按各自局部轴核对。'
};
await fs.writeFile(path.join(out,'I03对称性与尺寸核验.json'),JSON.stringify(report,null,2),'utf8');
console.log(JSON.stringify(report));
if(report.purifier.mirror.differenceCount||report.cabinets.current.differenceCount||report.tower.shell.differenceCount)process.exitCode=1;
