/**
 * 崩坏能稳定介质再生塔预览生成器。
 * Honkai-energy stabilization-medium regeneration tower preview generator.
 * 21×25×29：双腔回收塔、横向回流廊、顶部冷凝器和侧向检修翼。
 */
export default function build(api) {
  const s = api.createStructure([21, 25, 29]);
  const { fill, hollowBox, setBlock, line, cylinder } = api;
  const B = {
    foundation: 'minecraft:polished_deepslate', casing: 'minecraft:deepslate_bricks', trim: 'minecraft:polished_blackstone',
    glass: 'minecraft:cyan_stained_glass', glass2: 'minecraft:purple_stained_glass', metal: 'minecraft:iron_block',
    pipe: 'minecraft:oxidized_copper', pipe2: 'minecraft:cut_copper', coil: 'minecraft:lightning_rod',
    light: 'minecraft:sea_lantern', accent: 'minecraft:amethyst_block', hazard: 'minecraft:yellow_concrete', air: 'minecraft:air'
  };
  fill(s, [0,0,0], [20,0,28], B.foundation);
  hollowBox(s, [1,1,1], [19,4,27], B.casing);
  fill(s, [2,1,2], [18,1,26], B.trim);
  // Two independent recovery chambers / 两个独立再生腔
  hollowBox(s, [3,5,3], [9,20,25], B.casing);
  hollowBox(s, [11,5,3], [17,20,25], B.casing);
  hollowBox(s, [5,7,5], [7,18,23], B.glass);
  hollowBox(s, [13,7,5], [15,18,23], B.glass2);
  // Central return corridor / 中央回流廊
  hollowBox(s, [9,6,5], [11,21,23], B.metal);
  for (const z of [7,11,15,19,23]) {
    line(s, [2, z, 10], [18, z, 10], B.pipe2);
    setBlock(s, [10,z,10], B.accent);
  }
  // Recovery coils and catalyst columns / 回收线圈与催化柱
  for (const x of [5,7,13,15]) {
    line(s, [x,8,7], [x,18,21], B.pipe);
    for (const z of [9,13,17,21]) setBlock(s, [x, z, z], B.light);
  }
  // Side maintenance wings / 侧向检修翼
  hollowBox(s, [1,7,10], [3,15,18], B.metal);
  hollowBox(s, [17,7,10], [19,15,18], B.metal);
  fill(s, [1,9,12], [1,13,16], B.glass);
  fill(s, [19,9,12], [19,13,16], B.glass2);
  // Top condenser and return manifold / 顶部冷凝器与回流歧管
  hollowBox(s, [3,21,3], [17,23,25], B.trim);
  cylinder(s, [10,0,14], 8, [22,22], B.pipe2, { filled: false });
  cylinder(s, [10,0,14], 5, [23,23], B.accent, { filled: false });
  line(s, [10,21,14], [10,24,14], B.metal);
  setBlock(s, [10,24,14], B.light);
  for (const [x,z] of [[10,3],[10,25],[2,14],[18,14]]) {
    line(s, [x,21,z], [x,23,z], B.coil); setBlock(s, [x,23,z], B.light);
  }
  // Clear front/back and side access corridors / 保持四向检修通道
  fill(s, [9,1,0], [11,4,5], B.air); fill(s, [9,1,23], [11,4,28], B.air);
  fill(s, [0,1,13], [5,4,15], B.air); fill(s, [15,1,13], [20,4,15], B.air);
  for (const x of [2,18]) fill(s, [x,2,8], [x,2,20], B.hazard);
  for (const z of [2,26]) fill(s, [8,2,z], [12,2,z], B.hazard);
  return { structure: s, metadata: { name: 'hk3gtl-stabilization-medium-regeneration-tower', footprint: '21x25x29', controller: [10,5,14] } };
}
