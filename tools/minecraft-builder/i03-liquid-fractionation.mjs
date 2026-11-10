/**
 * I03 液态崩坏能分馏中心预览生成器。
 * I03 liquid Honkai-energy fractionation center preview generator.
 *
 * 25×29×25：中心分馏塔、四向母液管廊、顶部冷凝环和侧向残渣处理舱。
 * The 25×29×25 build contains a central fractionation tower, four mother-liquor galleries,
 * a top condensation ring, and side residue-processing chambers.
 */
export default function build(api) {
  const s = api.createStructure([25, 29, 25]);
  const { fill, hollowBox, setBlock, line, cylinder } = api;
  const B = {
    foundation: 'minecraft:polished_deepslate',
    casing: 'minecraft:deepslate_bricks',
    trim: 'minecraft:polished_blackstone',
    glass: 'minecraft:cyan_stained_glass',
    glass2: 'minecraft:purple_stained_glass',
    metal: 'minecraft:iron_block',
    coil: 'minecraft:lightning_rod',
    light: 'minecraft:sea_lantern',
    pipe: 'minecraft:oxidized_copper',
    pipe2: 'minecraft:cut_copper',
    accent: 'minecraft:amethyst_block',
    hazard: 'minecraft:yellow_concrete',
    air: 'minecraft:air'
  };
  // Foundation and stepped base / 基础与阶梯式底座
  fill(s, [0,0,0], [24,0,24], B.foundation);
  hollowBox(s, [1,1,1], [23,4,23], B.casing);
  fill(s, [2,1,2], [22,1,22], B.trim);
  // Four service wings / 四向检修翼舱
  hollowBox(s, [1,5,8], [5,11,16], B.metal);
  hollowBox(s, [19,5,8], [23,11,16], B.metal);
  hollowBox(s, [8,5,1], [16,11,5], B.metal);
  hollowBox(s, [8,5,19], [16,11,23], B.metal);
  // Colored intake/output windows / 入口与出口观察窗
  fill(s, [1,7,10], [1,9,14], B.glass);
  fill(s, [23,7,10], [23,9,14], B.glass2);
  fill(s, [10,7,1], [14,9,1], B.glass);
  fill(s, [10,7,23], [14,9,23], B.glass2);
  // Central pressure vessel / 中央压力分馏塔
  hollowBox(s, [6,5,6], [18,23,18], B.casing);
  hollowBox(s, [8,7,8], [16,21,16], B.glass);
  fill(s, [9,8,9], [15,20,15], B.glass2);
  // Vertical reinforced ribs / 纵向加强肋
  for (const [x,z] of [[6,6],[18,6],[6,18],[18,18]]) {
    line(s, [x,5,z], [x,23,z], B.trim);
    setBlock(s, [x,24,z], B.accent);
  }
  // Internal fractionation columns / 内部多级分馏柱
  for (const x of [9,12,15]) {
    for (const z of [9,12,15]) {
      line(s, [x,8,z], [x,20,z], B.pipe);
      setBlock(s, [x,10,z], B.light);
      setBlock(s, [x,14,z], B.light);
      setBlock(s, [x,18,z], B.light);
    }
  }
  // Cross-flow manifolds / 交叉流体歧管
  for (const y of [9,13,17,21]) {
    line(s, [2,y,12], [22,y,12], B.pipe2);
    line(s, [12,y,2], [12,y,22], B.pipe2);
    setBlock(s, [12,y,12], B.accent);
  }
  // Top condenser crown / 顶部冷凝冠环
  hollowBox(s, [4,24,4], [20,27,20], B.trim);
  cylinder(s, [12,0,12], 9, [27,27], B.pipe2, { filled: false });
  cylinder(s, [12,0,12], 6, [28,28], B.accent, { filled: false });
  for (const [x,z] of [[12,3],[12,21],[3,12],[21,12]]) {
    line(s, [x,24,z], [x,28,z], B.coil);
    setBlock(s, [x,28,z], B.light);
  }
  // Radar-like central exhaust / 顶部排放与监测桅杆
  line(s, [12,25,12], [12,28,12], B.metal);
  setBlock(s, [12,28,12], B.light);
  // Side warning bands and access corridor / 警示条与检修通道
  for (const x of [2,22]) fill(s, [x,2,8], [x,2,16], B.hazard);
  for (const z of [2,22]) fill(s, [8,2,z], [16,2,z], B.hazard);
  // Keep four access corridors open / 保持四向检修通道贯通
  fill(s, [11,1,0], [13,4,5], B.air);
  fill(s, [11,1,19], [13,4,24], B.air);
  fill(s, [0,1,11], [5,4,13], B.air);
  fill(s, [19,1,11], [24,4,13], B.air);
  // Door frames / 门框
  for (const [a,b] of [
    [[11,1,5],[13,4,5]], [[11,1,19],[13,4,19]],
    [[5,1,11],[5,4,13]], [[19,1,11],[19,4,13]]
  ]) hollowBox(s, a, b, B.trim);
  return { structure: s, metadata: { name: 'hk3gtl-i03-liquid-fractionation-center', footprint: '25x29x25', controller: [12, 5, 12] } };
}

