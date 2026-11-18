/**
 * 初期三台机器的建筑评审定义。完整方块；坐标为 X/Y/Z；各台独立生成。
 * 保留机器职责和接口种类，不在建筑脚本里添加配方、研究扣费或电网功能。
 */
import {BLOCKS} from './i03-fractionation-v2.mjs';

class Builder {
  constructor(key,title,size){this.key=key;this.title=title;this.size=size;this.cells=new Map();this.ports=[];this.paths=[];this.zones=[];}
  put(x,y,z,role){
    if(![x,y,z].every((v,i)=>Number.isInteger(v)&&v>=0&&v<this.size[i]))throw Error(`越界 ${this.key} ${x},${y},${z}`);
    const k=`${x},${y},${z}`;if(role==='air')this.cells.delete(k);else this.cells.set(k,BLOCKS[role]??role);
  }
  box(x1,y1,z1,x2,y2,z2,r){for(let y=y1;y<=y2;y++)for(let z=z1;z<=z2;z++)for(let x=x1;x<=x2;x++)this.put(x,y,z,r);}
  shell(x1,y1,z1,x2,y2,z2,r){for(let y=y1;y<=y2;y++)for(let z=z1;z<=z2;z++)for(let x=x1;x<=x2;x++)if(x===x1||x===x2||y===y1||y===y2||z===z1||z===z2)this.put(x,y,z,r);}
  base(){const [w,,d]=this.size;for(let z=0;z<d;z++)for(let x=0;x<w;x++){
    if((x===0||x===w-1)&&(z===0||z===d-1))continue;
    this.put(x,0,z,(x===1||x===w-2||z===1||z===d-2)?'panel':(x===(w>>1))?'panel':'armor');
  }}
  mirroredBox(x1,y1,z1,x2,y2,z2,r){const w=this.size[0];this.box(x1,y1,z1,x2,y2,z2,r);this.box(w-1-x2,y1,z1,w-1-x1,y2,z2,r);}
  port(id,x,y,z,face,group,purpose){this.put(x,y-1,z,'armor');this.put(x,y,z,'port');this.ports.push({id,pos:[x,y,z],face,group,purpose});}
  control(x,y,z){this.controller=[x,y,z];this.box(x-2,y-1,z,x+2,y-1,z+1,'armor');this.put(x,y,z,'core');for(const dx of [-1,1])this.put(x+dx,y,z,'node');}
  path(name,min,max){this.paths.push({name,min,max});}
  finish(description){
    const blocks=[...this.cells].map(([k,state])=>({pos:k.split(',').map(Number),state})).sort((a,b)=>a.pos[1]-b.pos[1]||a.pos[2]-b.pos[2]||a.pos[0]-b.pos[0]);
    return {key:this.key,title:this.title,name:`hk3gtl-${this.key}-architecture-v2`,size:this.size,description,blocks,ports:this.ports,controller:this.controller,entrance:[this.size[0]>>1,0],paths:this.paths,zones:this.zones};
  }
}

export function i01(){
  const b=new Builder('i01','I01 一阶崩坏能采集塔',[17,33,17]);b.base();
  // 双翼采集设备严格以 X=8 镜像；入口与检修间隙不被跨梁堵塞。
  b.mirroredBox(2,1,5,4,2,13,'armor');
  for(const x of [3,13]){
    b.shell(x-1,3,6,x+1,10,12,'process');
    b.box(x,4,6,x,8,6,'window');b.box(x,4,12,x,8,12,'window');
    for(const y of [3,7,10])b.box(x-1,y,8,x+1,y,10,'coil');
    b.box(x,11,8,x,17,8,'pipe');
  }
  b.shell(6,1,6,10,24,10,'armor');
  for(const x of [6,10])b.box(x,4,7,x,23,9,'glass');
  for(const z of [6,10])b.box(7,4,z,9,23,z,'glass');
  for(const y of [3,9,15,21]){b.box(6,y,6,10,y,10,'coil');b.put(8,y,8,'node');}
  b.box(8,1,8,8,26,8,'pipe');
  b.box(3,17,8,13,17,8,'armor');b.box(3,18,8,13,18,8,'pipe');
  // 朝上的雷达锅采用离散抛物面：边缘高、中央低，馈源有实际支撑。
  for(let z=1;z<=15;z++)for(let x=1;x<=15;x++){
    const r2=(x-8)**2+(z-8)**2;if(r2>49)continue;
    const y=25+Math.floor(r2/12);
    b.put(x,y,z,r2>36?'armor':((x===8||z===8)?'process':'panel'));
    if(r2>36)b.put(x,y+1,z,'coil');
  }
  b.box(8,26,8,8,31,8,'pipe');b.put(8,32,8,'node');
  for(const dx of [-1,1])for(let step=0;step<=6;step++)b.put(8+dx*step,31-Math.floor(step/3),8,'armor');
  b.control(8,2,2);
  b.mirroredBox(3,1,3,5,2,3,'armor');
  b.port('M1',4,2,3,'north','物品接口','探测器、编程电路及采样材料输入');
  b.port('F1',12,2,3,'north','流体接口','液态崩坏能输出');
  b.port('M2',4,2,14,'south','可选物品接口','保留原结构额外物品输入能力，不增加并行仓');
  b.path('左侧检修通道',[0,1,1],[1,4,15]);b.path('右侧检修通道',[15,1,1],[16,4,15]);
  b.zones=[{name:'抛物面采集锅',pos:[8,29,8]},{name:'竖向采集核心',pos:[8,20,8]},{name:'左右镜像处理翼',pos:[3,9,9]}];
  return b.finish('保留雷达身份 · 镜像双翼 · 贯通采集主轴');
}

export function i02(){
  const b=new Builder('i02','I02 崩坏能样本光谱分析阵列',[17,17,21]);b.base();
  // 双光路沿 Z 延伸，全部主构件以 X=8 镜像；中央三格通道贯通。
  for(const x of [4,12]){
    b.box(x-2,1,5,x+2,1,17,'armor');b.box(x,2,5,x,2,17,'panel');
    for(const z of [6,10,14,17]){
      b.shell(x-2,3,z,x+2,11,z,'armor');
      b.box(x-1,4,z,x+1,10,z,'air');
      b.box(x-2,5,z,x-2,9,z,'coil');b.box(x+2,5,z,x+2,9,z,'coil');
      b.box(x-1,11,z,x+1,11,z,'node');
    }
    b.box(x,6,5,x,6,17,'glass');
    for(const z of [5,9,13,17]){b.put(x,6,z,'process');b.put(x,7,z,'node');}
    for(const y of [3,10]){b.box(x-2,y,5,x-2,y,17,'process');b.box(x+2,y,5,x+2,y,17,'process');}
  }
  for(const z of [6,14]){
    b.box(2,12,z,14,12,z,'armor');b.box(3,13,z,13,13,z,'panel');b.box(7,14,z,9,14,z,'coil');
    b.put(8,15,z,'process');b.put(8,16,z,'node');
  }
  b.mirroredBox(1,2,7,1,7,16,'panel');b.mirroredBox(1,4,9,1,5,14,'window');
  b.control(8,2,2);
  b.port('M1',4,2,3,'north','物品接口','分析样本及实验材料输入');b.port('M2',12,2,3,'north','物品接口','分析样本及实验产物输出');
  b.port('M3',4,2,18,'south','可选物品接口','保留原有可选物品接口');b.port('M4',12,2,18,'south','可选物品接口','保留原有可选物品接口');
  b.path('中央实验检修通道',[7,1,4],[9,4,20]);
  b.zones=[{name:'左光谱通道',pos:[4,9,10]},{name:'右光谱通道',pos:[12,9,10]},{name:'横向扫描桥',pos:[8,14,14]}];
  return b.finish('双光路镜像阵列 · 开放扫描桥 · 中央检修廊');
}

export function s01(){
  const b=new Builder('s01','S01 一阶研究所',[17,17,25]);b.base();
  // 两翼分别表达计算与样本研究，中间为公共操作廊；不添加仓室扣材料的新功能。
  for(const x of [4,12]){
    b.shell(x-2,1,6,x+2,8,19,'armor');
    for(const z of [7,11,15]){
      b.box(x-2,3,z,x-2,6,z+2,'window');b.box(x+2,3,z,x+2,6,z+2,'window');
      b.box(x,2,z,x,5,z+1,'panel');b.put(x,6,z,'node');
    }
    b.box(x-2,9,7,x+2,9,18,'process');b.box(x-1,10,8,x+1,10,17,'panel');
  }
  // 后部认知中枢使用分级收拢的穹顶，内部研究台与外侧入口可达。
  for(let y=6;y<=16;y++){
    const r=Math.max(1,5-Math.floor((y-6)/3));
    for(let z=17-r;z<=17+r;z++)for(let x=8-r;x<=8+r;x++){
      const dx=Math.abs(x-8),dz=Math.abs(z-17);
      if(dx+dz>r+Math.ceil(r/2))continue;
      if(dx===r||dz===r||dx+dz===r+Math.ceil(r/2)||y===16)b.put(x,y,z,y%3===0?'armor':'glass');
    }
  }
  b.box(6,1,16,10,2,18,'armor');b.box(7,3,16,9,3,18,'panel');b.put(8,4,17,'node');
  for(const z of [6,12,21]){
    b.box(1,1,z,1,11,z,'armor');b.box(15,1,z,15,11,z,'armor');b.box(1,11,z,15,11,z,'armor');
    b.box(6,12,z,10,12,z,'process');
  }
  b.control(8,2,2);
  b.port('H1',4,2,22,'south','可选崩坏能接口','保留有线／无线崩坏能输入能力，不是物品仓');
  b.port('H2',12,2,22,'south','可选崩坏能接口','保留有线／无线崩坏能输入能力，非强制前置');
  b.path('前厅与研究操作廊',[7,1,4],[9,4,14]);
  b.zones=[{name:'双翼实验厅',pos:[4,9,12]},{name:'认知穹顶',pos:[8,15,17]},{name:'研究操作前厅',pos:[8,3,6]}];
  return b.finish('双翼实验厅 · 后部认知穹顶 · 玩家材料与研究点付款保持不变');
}

export function createBlueprint(key){if(key==='i01')return i01();if(key==='i02')return i02();if(key==='s01')return s01();throw Error('未知建筑：'+key);}
export default function build(api){const data=createBlueprint(process.env.HK3_REVIEW_MACHINE??'i01');const structure=api.createStructure(data.size);for(const b of data.blocks)api.setBlock(structure,b.pos,b.state);return {structure,metadata:{name:data.name}};}
