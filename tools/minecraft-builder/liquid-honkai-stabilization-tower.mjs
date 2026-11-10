/**
 * 液态崩坏能稳定塔预览生成器。
 * Liquid Honkai-energy stabilization tower preview generator.
 *
 * 21×33×21：阶梯式稳定塔、双层稳定环、四角冷却翼和顶部稳定天线。
 * The 21×33×21 build contains a stepped stabilization tower, dual stabilizer rings,
 * four cooling wings and a crown antenna.
 */
export default function build(api) {
  const s = api.createStructure([21, 33, 21]);
  const { fill, hollowBox, setBlock, line, cylinder } = api;
  const B = {
    foundation: 'minecraft:polished_deepslate',
    casing: 'minecraft:deepslate_bricks',
    trim: 'minecraft:polished_blackstone',
    glass: 'minecraft:cyan_stained_glass',
    glass2: 'minecraft:blue_stained_glass',
    metal: 'minecraft:iron_block',
    coil: 'minecraft:lightning_rod',
    light: 'minecraft:sea_lantern',
    pipe: 'minecraft:oxidized_copper',
    pipe2: 'minecraft:cut_copper',
    accent: 'minecraft:amethyst_block',
    hazard: 'minecraft:yellow_concrete',
    air: 'minecraft:air'
  };
  // Foundation and access plinth / 基础与检修平台
  fill(s, [0,0,0], [20,0,20], B.foundation);
  hollowBox(s, [1,1,1], [19,4,19], B.casing);
  fill(s, [2,1,2], [18,1,18], B.trim);
  // Four independent cooling wings / 四个独立冷却翼
  hollowBox(s, [1,5,7], [4,12,13], B.metal);
  hollowBox(s, [16,5,7], [19,12,13], B.metal);
  hollowBox(s, [7,5,1], [13,12,4], B.metal);
  hollowBox(s, [7,5,16], [13,12,19], B.metal);
  fill(s, [1,7,8], [1,10,12], B.glass);
  fill(s, [19,7,8], [19,10,12], B.glass2);
  fill(s, [8,7,1], [12,10,1], B.glass);
  fill(s, [8,7,19], [12,10,19], B.glass2);
  // Main stabilizer vessel / 主稳定压力容器
  hollowBox(s, [4,5,16], [16,27,16], B.casing);
  hollowBox(s, [6,7,14], [14,25,14], B.glass);
  fill(s, [7,8,13], [13,24,13], B.glass2);
  // Reinforced ribs and vertical conduits / 加强肋与垂直导管
  for (const [x,z] of [[4,4],[16,4],[4,16],[16,16]]) {
    line(s, [x,5,z], [x,27,z], B.trim);
    setBlock(s, [x,26,z], B.accent);
  }
  for (const [x,z] of [[7,7],[7,13],[13,7],[13,13]]) {
    line(s, [x,8,z], [x,24,z], B.pipe);
    for (const y of [10,15,20]) setBlock(s, [x,y,z], B.light);
  }
  // Horizontal stabilization manifolds / 横向稳定歧管
  for (const y of [10,15,20,25]) {
    line(s, [2,y,10], [18,y,10], B.pipe2);
    line(s, [10,y,2], [10,y,18], B.pipe2);
    setBlock(s, [10,y,10], B.accent);
  }
  // Dual containment rings / 双层约束环
  cylinder(s, [10,0,10], 9, [13,14], B.trim, { filled: false });
  cylinder(s, [10,0,10], 7, [14,15], B.pipe2, { filled: false });
  cylinder(s, [10,0,10], 9, [22,23], B.trim, { filled: false });
  cylinder(s, [10,0,10], 7, [23,24], B.pipe2, { filled: false });
  for (const [x,z] of [[10,1],[10,19],[1,10],[19,10]]) {
    line(s, [x,13,z], [x,15,z], B.coil);
    line(s, [x,22,z], [x,24,z], B.coil);
    setBlock(s, [x,15,z], B.light);
    setBlock(s, [x,24,z], B.light);
  }
  // Crown chamber and stabilizer antenna / 顶部稳定腔与天线
  hollowBox(s, [3,28,3], [17,30,17], B.trim);
  hollowBox(s, [6,29,6], [14,31,14], B.glass2);
  line(s, [10,28,10], [10,32,10], B.metal);
  cylinder(s, [10,0,10], 4, [31,31], B.pipe2, { filled: false });
  setBlock(s, [10,32,10], B.light);
  // Warning bands and four clear corridors / 警示带与四向贯通检修道
  for (const x of [2,18]) fill(s, [x,2,7], [x,2,13], B.hazard);
  for (const z of [2,18]) fill(s, [7,2,z], [13,2,z], B.hazard);
  fill(s, [9,1,0], [11,4,5], B.air);
  fill(s, [9,1,15], [11,4,20], B.air);
  fill(s, [0,1,9], [5,4,11], B.air);
  fill(s, [15,1,9], [20,4,11], B.air);
  // Door frames / 门框
  hollowBox(s, [9,1,5], [11,4,5], B.trim);
  hollowBox(s, [9,1,15], [11,4,15], B.trim);
  hollowBox(s, [5,1,9], [5,4,11], B.trim);
  hollowBox(s, [15,1,9], [15,4,11], B.trim);
  return { structure: s, metadata: { name: 'hk3gtl-liquid-honkai-stabilization-tower', footprint: '21x33x21', controller: [10, 5, 10] } };
}
