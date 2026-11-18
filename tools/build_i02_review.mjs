/** Change #1 2026-09-23: I02 authored 17×21×17 spectral laboratory, approved layout.
 * 单台原创完整建筑，先生成最终体素再导出；整数坐标为方块，不修改游戏世界。
 * Build one complete architectural candidate, not a functional controller or an approved GT Pattern.
 * 固定左右镜像、外侧2×3净空检修环路；无随机性，不复用旧曲线占位造型。
 * Deterministic mirrored optics, a clear two-wide/three-high service loop, and no reused placeholder geometry.
 */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=path.join(root,'doc/HK3GTL-内测5/03_机器结构/I02结构审核_v1');
export default function(api) {
  const size=[17,17,21], blocks=new Map();
  const P={shell:'gtceu:clean_machine_casing',frame:'gtceu:solid_machine_casing',pipe:'gtceu:steel_pipe_casing',
    glass:'gtceu:tempered_glass',warning:'gtceu:yellow_stripes_block_a',
    trim:'minecraft:smooth_quartz',dark:'minecraft:polished_deepslate',lamp:'minecraft:sea_lantern',
    cyan:'minecraft:cyan_stained_glass',purple:'minecraft:purple_stained_glass',core:'minecraft:amethyst_block',
    rail:'minecraft:iron_bars',screen:'minecraft:black_stained_glass',silver:'minecraft:iron_block',
    grate:'minecraft:iron_trapdoor[facing=north,half=top,open=false,powered=false,waterlogged=false]',
    step:'minecraft:quartz_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]',
    slab:'minecraft:smooth_quartz_slab[type=bottom,waterlogged=false]',tint:'minecraft:light_gray_concrete'};
  function put(x,y,z,key){
    if(![x,y,z].every(Number.isInteger)||x<0||x>=17||y<0||y>=17||z<0||z>=21) throw Error(`Bounds ${x},${y},${z}`);
    blocks.set(`${x},${y},${z}`,P[key]??key);
  }
  function box(x0,y0,z0,x1,y1,z1,key){for(let x=x0;x<=x1;x++)for(let y=y0;y<=y1;y++)for(let z=z0;z<=z1;z++)put(x,y,z,key);}
  function pair(x,y,z,key){put(x,y,z,key);put(16-x,y,z,key);}
  // 底座有离散承重梁，管线沿底层分流；检修主甲板统一位于Y2。
  // Discrete foundation beams carry separate service pipes below the level-two main deck.
  for(let z=2;z<=20;z++)for(let x=0;x<17;x++)put(x,0,z,(x%4===0||z%5===0)?'frame':'dark');
  for(let x=0;x<17;x++)for(let z=2;z<=20;z++) {
    if(x===0||x===16||z===2||z===20||x===8)put(x,1,z,'frame');
    put(x,2,z,(x===0||x===16||z===20)?'trim':'tint');
  }
  for(let z=4;z<=19;z++)for(const x of [4,12]) {put(x,1,z,'pipe');put(x,2,z,z%3===0?'grate':'shell');}
  for(let x=3;x<=13;x++)put(x,1,19,'pipe');
  for(let z=0;z<=2;z++)box(6,z,z,10,z,z,'step');
  for(let z=3;z<=19;z++){pair(0,3,z,'rail'); if(z%3===0){pair(1,2,z,'lamp');pair(2,2,z,'cyan');}}
  for(let x=1;x<=15;x++)put(x,3,20,'rail');
  // 外围承重柱和斜切肩托；通道X1–2/X14–15,Y3–5保持净空。
  // Perimeter piers and stepped shoulders leave the service corridor entirely unobstructed.
  for(const z of [6,12,18]) {
    for(let y=3;y<=12;y++)pair(0,y,z,y%3===0?'frame':'shell');
    pair(1,11,z,'frame');pair(1,12,z,'shell');pair(2,12,z,'shell');
    pair(2,13,z,'frame');pair(3,13,z,'shell');
    for(let x=3;x<=13;x++)put(x,14,z,x%4===0?'lamp':'shell');
    for(let x=4;x<=12;x++)put(x,15,z,'slab');
    for(let x=4;x<=12;x++)put(x,13,z,'cyan');
  }
  // 两套对照光谱廊：下方仪器基座，上方中空圆角扫描筒，五道机械环。
  // Paired optics have instrument beds, hollow rounded scan chambers and five mechanical collars.
  for(const cx of [4,12]) {
    for(const z of [6,9,12,15]) {
      box(cx-1,3,z,cx+1,3,z,'frame');box(cx,4,z,cx,6,z,'pipe');
      pair(4,5,z,'lamp');
    }
    for(let z=5;z<=16;z++) {
      for(const [dx,dy] of [[-1,-2],[0,-2],[1,-2],[-2,-1],[-2,0],[-2,1],[-1,2],[0,2],[1,2],[2,-1],[2,0],[2,1]])
        put(cx+dx,8+dy,z,[5,8,11,14,16].includes(z)?'shell':'glass');
      put(cx,8,z,z%3===0?'lamp':'cyan');
      if([5,8,11,14,16].includes(z)) {put(cx,11,z,'frame');put(cx,12,z,'pipe');}
    }
    // 端面保留可见光孔，而非填满实心机壳。
    // End caps keep a visible optical aperture rather than a solid casing face.
    for(const z of [5,16]){put(cx,8,z,'glass');put(cx-1,8,z,'cyan');put(cx+1,8,z,'cyan');}
  }
  // 中央样品舱独立悬架与观察窗，紫色样品仅在中心，保留透视感。
  // Suspended central sample chamber; violet accents stay in the specimen core and windows remain transparent.
  box(7,3,10,9,4,12,'frame');box(8,5,10,8,6,12,'pipe');
  for(let y=6;y<=12;y++)for(let x=6;x<=10;x++)for(let z=8;z<=14;z++){
    const edge=x===6||x===10||z===8||z===14;
    if(edge)put(x,y,z,y===6||y===12?'shell':(x===6||x===10)&&(z===8||z===14)?'frame':'glass');
  }
  for(let y=7;y<=11;y++)put(8,y,11,y===9?'core':'purple');
  for(const y of [6,12]) {put(8,y,8,'lamp');put(8,y,14,'lamp');}
  for(let z=9;z<=13;z++) {put(7,16,z,'trim');put(9,16,z,'trim');put(8,15,z,'purple');}
  box(7,13,9,7,15,9,'frame');box(9,13,9,9,15,9,'frame');
  box(7,13,13,7,15,13,'frame');box(9,13,13,9,15,13,'frame');
  // 前控制台及两侧分离的服务接头；仅标注预留，尚无I02控制器逻辑。
  // Front console and separate service faces are architectural reservations, not functional I02 controllers.
  box(7,3,5,9,3,5,'shell');box(7,4,5,9,4,5,'screen');put(8,5,5,'slab');
  for(const x of [4,12]){put(x,3,2,'pipe');put(x,4,2,'warning');put(x,5,2,'slab');put(x,3,19,'pipe');put(x,4,19,'shell');}
  // 后方仪器背板，侧边光带与护罩：背部也有明确结构，不留空白立面。
  // Rear service cabinets and guarded light strips keep the rear elevation fully authored.
  for(const cx of [4,12])for(let y=5;y<=10;y++){
    put(cx,y,19,'frame');put(cx-1,y,19,y%2?'shell':'screen');put(cx+1,y,19,y%2?'shell':'screen');
  }
  // 初始图纸使用实体方块验证净空和镜像，运行时连接属性交由Minecraft/Lodestone补全。
  // Validate geometry before export; connection states are updated by Minecraft/Lodestone afterward.
  const routes=[];
  for(let z=3;z<=18;z++)for(const x of [1,2,14,15])routes.push([x,z]);
  for(const z of [3,4,17,18])for(let x=1;x<=15;x++)routes.push([x,z]);
  for(const [x,z] of routes)for(let y=3;y<=5;y++)if(blocks.has(`${x},${y},${z}`))throw Error(`Blocked service path ${x},${y},${z}`);
  for(const [key,b] of blocks){const [x,y,z]=key.split(',').map(Number);if(blocks.get(`${16-x},${y},${z}`)!==b)throw Error(`Asymmetry ${key}`);}
  const structure=api.createStructure(size), counts={};
  const cells=[...blocks].map(([key,block])=>({pos:key.split(',').map(Number),block})).sort((a,b)=>a.pos[1]-b.pos[1]||a.pos[2]-b.pos[2]||a.pos[0]-b.pos[0]);
  for(const {pos,block} of cells){api.setBlock(structure,pos,block);counts[block]=(counts[block]??0)+1;}
  fs.mkdirSync(out,{recursive:true});
  fs.writeFileSync(path.join(out,'blueprint.json'),JSON.stringify({size,blocks:cells,counts,ports:{controller:[8,3,5],input:[4,3,2],output:[12,3,2],rearServices:[[4,3,19],[12,3,19]]},
    validation:{mirrorX:true,clearServiceWidth:2,clearServiceHeight:3,routeCells:new Set(routes.map(p=>p.join(','))).size},
    status:'Complete architectural candidate; controller, recipe and Pattern pending structure acceptance.'},null,2));
  return {structure,metadata:{name:'i02-spectrum-array-v1'}};
}
