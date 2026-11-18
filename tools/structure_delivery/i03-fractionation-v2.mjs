/**
 * I03 分馏中心第二版；修正净化舱七格长度、柜体镜像与回流轴连接。
 * 同一份确定性逐格数据用于 Lodestone 原版结构、Sponge 文件和三维预览。
 * 本文件只输出建筑，不改注册、配方或 Pattern；接口与主控均为规定的标记。
 */
export const SIZE = [25, 25, 29];
export const BLOCKS = {
  armor: 'gtceu:max_machine_casing',
  process: 'gtlcore:molecular_casing',
  panel: 'gtceu:computer_casing',
  node: 'gtceu:high_power_casing',
  coil: 'gtceu:superconducting_coil[active=false]',
  glass: 'gtceu:fusion_glass',
  window: 'gtceu:laminated_glass',
  pipe: 'kubejs:neutronium_pipe_casing',
  gear: 'kubejs:neutronium_gearbox',
  core: 'minecraft:diamond_block',
  port: 'minecraft:diamond_ore',
};

export function createBlueprint() {
  const cells = new Map();
  const ports = [];
  // 后写入的构件覆盖前一构件，越界立即失败；空气不计入实体材料数量。
  const put = (x, y, z, role) => {
    if (![x,y,z].every(Number.isInteger) || x<0 || y<0 || z<0 || x>=25 || y>=25 || z>=29)
      throw Error(`结构坐标越界：${x},${y},${z}`);
    const key=`${x},${y},${z}`;
    if (role === 'air') cells.delete(key); else cells.set(key, BLOCKS[role] ?? role);
  };
  const box=(x1,y1,z1,x2,y2,z2,role)=>{
    for(let y=y1;y<=y2;y++)for(let z=z1;z<=z2;z++)for(let x=x1;x<=x2;x++)put(x,y,z,role);
  };
  // 切角截面用完整立方体近似八边形，不使用框架、台阶或薄管线。
  const oct=(dx,dz,r)=>Math.max(Math.abs(dx),Math.abs(dz))<=r && Math.abs(dx)+Math.abs(dz)<=r+Math.ceil(r*.55);
  const ring=(cx,cz,r,y,role)=>{
    for(let z=cz-r;z<=cz+r;z++)for(let x=cx-r;x<=cx+r;x++)
      if(oct(x-cx,z-cz,r)&&!oct(x-cx,z-cz,r-1))put(x,y,z,role);
  };
  const hollow=(x1,y1,z1,x2,y2,z2,role)=>{
    for(let y=y1;y<=y2;y++)for(let z=z1;z<=z2;z++)for(let x=x1;x<=x2;x++)
      if(x===x1||x===x2||y===y1||y===y2||z===z1||z===z2)put(x,y,z,role);
  };

  // 基础采用切角边界；铺装内嵌输送脊、承重条及连续维护走道。
  for(let z=0;z<29;z++)for(let x=0;x<25;x++){
    if((x<2||x>22)&&(z<2||z>26))continue;
    put(x,0,z,'armor');
    if((x===2||x===13||x===18||x===22)&&z>=3&&z<=25)put(x,0,z,'panel');
    if((z===4||z===13||z===17||z===25)&&x>=2&&x<=22)put(x,0,z,'process');
    if(x>=15&&x<=17)put(x,0,z,x===16?'panel':'armor');
    if(z>=14&&z<=16)put(x,0,z,z===15?'panel':'armor');
  }
  for(const z of [3,9,17,25])for(const x of [0,24])put(x,0,z,'node');
  for(const x of [3,8,13,19,22])for(const z of [0,28])put(x,0,z,'panel');

  // 后部主分馏柱：实体支座、透明分离段、四级分布盘及收口顶冠。
  const cx=8,cz=21;
  for(let z=16;z<=27;z++)for(let x=2;x<=14;x++)
    if(oct(x-cx,z-cz,6))put(x,1,z,'armor');
  for(let y=2;y<=21;y++)for(let z=16;z<=26;z++)for(let x=3;x<=13;x++){
    const dx=x-cx,dz=z-cz;
    if(!oct(dx,dz,5))continue;
    const edge=!oct(dx,dz,4);
    if(y===2||y===21)put(x,y,z,'armor');
    else if(edge){
      const band=[3,8,13,18].includes(y);
      const rib=(Math.abs(dx)===5&&Math.abs(dz)<=1)||(Math.abs(dz)===5&&Math.abs(dx)<=1);
      put(x,y,z,band?'armor':rib?'process':'glass');
    }
  }
  for(const y of [4,9,14,19])ring(cx,cz,5,y,'coil');
  for(const y of [6,11,16]){
    for(let z=18;z<=24;z++)for(let x=5;x<=11;x++)
      if(oct(x-cx,z-cz,3) && ((x+z)%2===0||x===cx||z===cz))put(x,y,z,'process');
    put(cx,y,cz,'node');
  }
  // 中央回流轴是有意设置的工艺内芯；保留分离盘连接节点，不被贯通管覆盖。
  for(let y=3;y<=20;y++)put(cx,y,cz,[6,11,16].includes(y)?'node':'pipe');
  for(const [x,z] of [[3,18],[3,24],[13,18],[13,24]]){
    box(x,1,z,x,21,z,'armor');
    for(const y of [4,9,14,19])put(x,y,z,'node');
  }
  for(let y=22;y<=24;y++){
    const radius=25-y;
    for(let z=cz-radius;z<=cz+radius;z++)for(let x=cx-radius;x<=cx+radius;x++)
      if(oct(x-cx,z-cz,radius))put(x,y,z,y===23?'coil':'armor');
  }
  put(8,24,21,'node');

  // 前部净化舱：卧式切角容器，两端实体封盖，内部有可剖视的过滤轴。
  for(const z of [6,10])box(3,1,z,13,2,z,'armor');
  for(let z=5;z<=11;z++)for(let y=3;y<=10;y++)for(let x=3;x<=13;x++){
    const dx=Math.abs(x-8),dy=Math.abs(y-6.5);
    if(dx>5||dy>3.5||dx+dy>7)continue;
    const inner=dx<=4&&dy<=2.5&&dx+dy<=5.5;
    if(!inner||z===5||z===11){
      const band=z===5||z===8||z===11;
      put(x,y,z,band?'armor':y>=6&&y<=8?'glass':'process');
    }
  }
  box(8,6,6,8,6,10,'pipe');
  for(const z of [6,8,10]){
    box(6,5,z,10,5,z,'coil');box(6,7,z,10,7,z,'coil');
    put(6,6,z,'gear');put(10,6,z,'gear');
  }
  for(const z of [6,8,10])for(const x of [3,13]){put(x,4,z,'panel');put(x,5,z,'node');}
  box(6,10,6,10,10,10,'armor');
  for(const z of [6,10])box(7,11,z,9,11,z,'panel');

  // 右侧两座滤芯抽换柜；高位歧管接入净化舱，地面不穿越检修走道。
  for(const z of [5,9]){
    hollow(19,1,z,23,7,z+2,'armor');
    box(19,2,z,19,6,z+2,'panel');
    box(19,3,z+1,19,5,z+1,'window');
    box(23,2,z,23,6,z+2,'process');
    box(21,2,z+1,21,6,z+1,'coil');
    put(21,8,z+1,'gear');
  }
  box(21,9,6,21,9,10,'pipe');
  box(12,9,8,21,9,8,'pipe');
  for(const x of [14,18]){box(x,1,8,x,8,8,'armor');put(x,8,8,'node');}

  // 高位转送桥跨过中部三格通道，支点落在工艺舱，不形成悬空管路。
  box(8,11,12,8,11,16,'pipe');
  box(7,10,12,9,10,16,'armor');
  for(const z of [12,17]){box(6,1,z,6,12,z,'armor');box(10,1,z,10,12,z,'armor');box(6,12,z,10,12,z,'panel');}
  // 右后侧冷凝单元与三条支路：均使用完整管道方块，观察窗后有实体内芯。
  hollow(19,2,19,22,13,24,'armor');
  box(19,4,20,19,11,23,'glass');box(22,4,20,22,11,23,'glass');
  box(20,3,20,21,12,23,'coil');
  for(const y of [3,7,12]){box(18,y,19,23,y,19,'process');box(18,y,24,23,y,24,'process');}
  box(19,14,20,22,14,23,'panel');
  box(12,17,20,21,17,20,'pipe');box(21,14,20,21,17,20,'pipe');
  for(const x of [14,18]){box(x,6,20,x,16,20,'armor');put(x,16,20,'node');}
  box(18,1,20,18,5,20,'armor');

  // 主控位在前端凹入操作台；实体主机只在日后 Pattern 迁移时替换。
  box(6,1,2,10,1,3,'armor');box(7,2,3,9,2,4,'panel');
  put(8,2,2,'core');put(7,2,2,'node');put(9,2,2,'node');

  // 接口标记记录访问面与拟定用途；同类输入输出以后可互换，槽位不等于功能实现。
  function port(id,x,y,z,face,group,purpose){
    put(x,y-1,z,'armor');put(x,y,z,'port');
    ports.push({id,pos:[x,y,z],face,group,purpose});
  }
  for(const [id,z,purpose] of [['F1',18,'液态崩坏能输入'],['F2',21,'母液／试剂输入'],['F3',24,'第二净化流体或扩展输入']]){
    box(1,1,z-1,2,3,z+1,'armor');box(2,2,z,3,2,z,'pipe');port(id,1,2,z,'west','流体接口',purpose);
  }
  for(const [id,x,purpose] of [['F4',5,'粗制液／分离介质输出'],['F5',8,'母液／废试剂输出'],['F6',11,'分析试剂／工艺废液输出']]){
    box(x-1,1,26,x+1,3,27,'armor');box(x,2,25,x,2,26,'pipe');port(id,x,2,27,'south','流体接口',purpose);
  }
  // 2026-09-25：按前左截图将红圈 M1 接口座向画面左侧移一格，即本地 X 从3改为4；底座与连接管同步移动。
  for(const [id,x,purpose] of [['M1',4,'碳粉、滤芯、结晶基质、电路输入'],['M2',12,'固体产物输出，可与 M1 互换']]){
    box(x-1,1,2,x+1,3,3,'armor');box(x,2,3,x,2,5,'pipe');port(id,x,2,2,'north','物品接口',purpose);
  }
  box(22,1,2,23,3,4,'armor');port('M3',23,2,3,'east','物品接口','物品输入或输出扩展');
  box(22,1,16,23,3,18,'armor');port('P1',23,2,17,'east','扩展接口','可选并行仓；不用时换回指定机壳');
  // 纵向与横向检修带的净空是设计硬约束，发现穿插不静默抹除构件。
  const clearance=[];
  for(let z=0;z<29;z++)for(let x=15;x<=17;x++)for(let y=1;y<=4;y++)clearance.push([x,y,z]);
  for(let x=0;x<25;x++)for(let z=13;z<=15;z++)for(let y=1;y<=4;y++)clearance.push([x,y,z]);
  for(const [x,y,z] of clearance)if(cells.has(`${x},${y},${z}`))throw Error(`检修带受阻：${x},${y},${z}`);
  const blocks=[...cells].map(([key,state])=>({pos:key.split(',').map(Number),state})).sort((a,b)=>a.pos[1]-b.pos[1]||a.pos[2]-b.pos[2]||a.pos[0]-b.pos[0]);
  return {name:'hk3gtl-i03-fractionation-review-v2',title:'I03 崩坏能分馏中心',key:'i03',size:SIZE,blocks,ports,controller:[8,2,2],entrance:[16,0],
    description:'七格净化舱 · 镜像滤芯柜 · 连通回流轴',
    moduleBounds:{purifier:{min:[3,1,5],max:[13,11,11]},filterA:{min:[19,1,5],max:[23,8,7]},filterB:{min:[19,1,9],max:[23,8,11]}},
    zones:[{name:'低位净化舱',pos:[8,8,8]},{name:'分馏主柱',pos:[8,20,21]},{name:'滤芯抽换柜',pos:[21,7,9]},{name:'冷凝单元',pos:[21,13,22]}],
    paths:[{name:'纵向检修带',min:[15,1,0],max:[17,4,28]},{name:'横向检修带',min:[0,1,13],max:[24,4,15]}]};
}

export default function build(api){
  const data=createBlueprint();
  const structure=api.createStructure(data.size);
  for(const block of data.blocks)api.setBlock(structure,block.pos,block.state);
  return {structure,metadata:{name:data.name}};
}
