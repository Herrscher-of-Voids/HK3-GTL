#!/usr/bin/env node
'use strict';
/**
 * 从单个 Litematica .litematic 文件解析休伯利安号结构并生成 GT 多方块 Pattern。
 *
 * 相对旧的 502 chunk NBT 方案的优势：
 *   1. 单一来源文件，无需合并 → 结构连续无散裂
 *   2. 包含所有 region/方块/方向元数据
 *   3. 跨 chunk 边界的飞船不会被切碎
 *
 * Litematic 格式要点：
 *   - 顶层 NBT (gzip 压缩)：{ Version, Metadata, Regions: { name: {...} } }
 *   - Regions[name].BlockStatePalette: BlockState 列表
 *   - Regions[name].BlockStates: long[]，跨边界紧凑打包索引
 *   - Regions[name].Position / Size: 整数三元组（Size 可能负数表示反向）
 *
 * 输出：
 *   src/main/java/com/sirin/hk3gtl/common/multiblock/hyperion/HyperionLayerPart*.java
 *   src/main/java/com/sirin/hk3gtl/common/multiblock/hyperion/HyperionPatternData.java
 *
 * 注意：休伯利安控制器与 ΩΨΦΣ 四舱位为手工补丁（见 HyperionPatternProviderImpl 体素换算）。
 * 重新运行本脚本会按 litematic 覆盖 Layer 文件，需按同一文档恢复布局。
 */

const fs   = require('fs');
const path = require('path');
const zlib = require('zlib');

// ── 常量 ────────────────────────────────────────────────────────────────────
const PROJECT_ROOT = path.join(__dirname, '..');
const LITEMATIC_PATH = process.argv[2]
  ? path.resolve(process.argv[2])
  : path.join(PROJECT_ROOT, '休伯利安号 .litematic');
if (!fs.existsSync(LITEMATIC_PATH)) {
  throw new Error('找不到休伯利安源文件，请通过第一个参数提供 .litematic 路径：' + LITEMATIC_PATH);
}
const PACKAGE   = 'com.sirin.hk3gtl.common.multiblock.hyperion';
const OUTPUT_DIR = path.join(
  __dirname, '..', 'src', 'main', 'java',
  'com', 'sirin', 'hk3gtl', 'common', 'multiblock', 'hyperion'
);
const LAYERS_PER_FILE = 10;

const SYM_AIR        = ' ';
const SYM_CONTROLLER = 'S';
const SYM_QUARTZ     = 'X'; // 原石英块位置 → gravity_stabilization_casing
const SYM_BLACK      = 'B'; // 原黑色混凝土位置 → extreme_density_casing
const QUARTZ_BLOCK   = 'minecraft:quartz_block';
const BLACK_CONCRETE = 'minecraft:black_concrete';

/**
 * minecraft 方块 → 替换为 GT 机壳。
 * 替换是 1:1 的：解析时遇到 key，输出 Pattern 时只匹配 value。
 * 半砖/楼梯在解析阶段已压成「同材质完整方块」，不再单独锁朝向。
 */
const BLOCK_REPLACE = new Map([
  [QUARTZ_BLOCK,                  'gtladditions:gravity_stabilization_casing'],
  [BLACK_CONCRETE,                'gtladditions:extreme_density_casing'],
  ['minecraft:yellow_concrete',   'gtceu:industrial_steam_casing'],
  ['minecraft:cyan_terracotta',   'gtlcore:ultimate_stellar_containment_casing'],
  ['minecraft:smooth_stone',      'gtlcore:fission_reactor_casing'],
  ['minecraft:polished_deepslate','gtlcore:antifreeze_heatproof_machine_casing'],
  ['minecraft:cyan_concrete',     'gtlcore:qft_coil'],
]);

/**
 * 半砖 / 楼梯 → 同材质完整方块 id（与 litematic 中 Name 同格式，含命名空间）。
 * 未收录的 minecraft 半砖楼梯在运行时打一次警告并保留原名（仍可能走活板门级逻辑若适用）。
 */
const SLAB_STAIR_FULL = (() => {
  const m = new Map();
  const pair = (base, fullShort) => {
    m.set(`minecraft:${base}_slab`, `minecraft:${fullShort}`);
    m.set(`minecraft:${base}_stairs`, `minecraft:${fullShort}`);
  };
  const woods = ['oak', 'spruce', 'birch', 'jungle', 'acacia', 'dark_oak', 'mangrove', 'cherry', 'bamboo', 'crimson', 'warped'];
  for (const w of woods) pair(w, `${w}_planks`);
  pair('bamboo_mosaic', 'bamboo_mosaic');
  pair('quartz', 'quartz_block');
  pair('smooth_quartz', 'smooth_quartz');
  pair('purpur', 'purpur_block');
  pair('stone', 'stone');
  pair('smooth_stone', 'smooth_stone');
  pair('cobblestone', 'cobblestone');
  pair('stone_brick', 'stone_bricks');
  pair('mossy_stone_brick', 'mossy_stone_bricks');
  pair('andesite', 'andesite');
  pair('polished_andesite', 'polished_andesite');
  pair('diorite', 'diorite');
  pair('polished_diorite', 'polished_diorite');
  pair('granite', 'granite');
  pair('polished_granite', 'polished_granite');
  pair('brick', 'bricks');
  pair('mud_brick', 'mud_bricks');
  pair('sandstone', 'sandstone');
  pair('cut_sandstone', 'cut_sandstone');
  pair('smooth_sandstone', 'smooth_sandstone');
  pair('red_sandstone', 'red_sandstone');
  pair('cut_red_sandstone', 'cut_red_sandstone');
  pair('smooth_red_sandstone', 'smooth_red_sandstone');
  pair('prismarine', 'prismarine');
  pair('prismarine_brick', 'prismarine_bricks');
  pair('dark_prismarine', 'dark_prismarine');
  pair('nether_brick', 'nether_bricks');
  pair('red_nether_brick', 'red_nether_bricks');
  pair('blackstone', 'blackstone');
  pair('polished_blackstone', 'polished_blackstone');
  pair('polished_blackstone_brick', 'polished_blackstone_bricks');
  pair('cobbled_deepslate', 'cobbled_deepslate');
  pair('polished_deepslate', 'polished_deepslate');
  pair('deepslate_brick', 'deepslate_bricks');
  pair('deepslate_tile', 'deepslate_tiles');
  pair('end_stone_brick', 'end_stone_bricks');
  pair('cut_copper', 'cut_copper');
  pair('exposed_cut_copper', 'exposed_cut_copper');
  pair('weathered_cut_copper', 'weathered_cut_copper');
  pair('oxidized_cut_copper', 'oxidized_cut_copper');
  pair('waxed_cut_copper', 'waxed_cut_copper');
  pair('waxed_exposed_cut_copper', 'waxed_exposed_cut_copper');
  pair('waxed_weathered_cut_copper', 'waxed_weathered_cut_copper');
  pair('waxed_oxidized_cut_copper', 'waxed_oxidized_cut_copper');
  m.set('minecraft:petrified_oak_slab', 'minecraft:oak_planks');
  return m;
})();

let warnedUnknownSlabStair = false;
function slabOrStairsToFullBlock(blockId) {
  if (!blockId.endsWith('_slab') && !blockId.endsWith('_stairs')) return blockId;
  const hit = SLAB_STAIR_FULL.get(blockId);
  if (hit) return hit;
  if (!warnedUnknownSlabStair) {
    console.warn(`[hyperion_litematic_gen] 未映射的半砖/楼梯，保留原 id（请补 SLAB_STAIR_FULL）: ${blockId}`);
    warnedUnknownSlabStair = true;
  }
  return blockId;
}

/** 将 litematic 中的方块在读入时归一化：半砖/楼梯 → 完整方块（无 Properties）。 */
function normalizeLitematicState(state) {
  if (!state || !state.Name) return state;
  const name = state.Name;
  if (name.endsWith('_slab') || name.endsWith('_stairs')) {
    const full = slabOrStairsToFullBlock(name);
    return { Name: full, Properties: {} };
  }
  return state;
}

/** 仅活板门仍按完整 BlockState 锁定（休伯利安投影里多为 SKIP，可能无此项）。 */
function isDirectionalBlock(name) {
  return name.endsWith('_trapdoor');
}
const SKIP_BLOCKS = new Set([
  'minecraft:powered_rail',
  'minecraft:spruce_wall_sign',
  'minecraft:oak_button',
  'minecraft:heavy_weighted_pressure_plate',
  'minecraft:spruce_fence_gate',
  'minecraft:oak_slab',
  'minecraft:spruce_stairs',
  'minecraft:spruce_trapdoor',
  'minecraft:gray_carpet',
  'minecraft:white_carpet',
  'minecraft:light_blue_carpet',
  'minecraft:iron_bars',
]);
// 装饰符号池：先用 ASCII 可打印（去掉 S/X/B/空格/双引号/反斜杠/单引号），
// 不够再补 CJK 区。一个独立方块名占一个字符；不再锁定 BlockState 朝向。
const DECO_POOL = (() => {
  const out = [];
  for (let c = 0x21; c <= 0x7E; c++) {
    const ch = String.fromCharCode(c);
    if (ch === SYM_AIR || ch === SYM_CONTROLLER || ch === SYM_QUARTZ || ch === SYM_BLACK) continue;
    if (ch === '"' || ch === '\\' || ch === "'") continue;
    out.push(ch);
  }
  // 补充 CJK 兜底（如 ASCII 不够用）
  for (let c = 0x4E00; c <= 0x4F00; c++) out.push(String.fromCharCode(c));
  return out.join('');
})();

// ── NBT 解析器（支持 long 数组）────────────────────────────────────────────
class NbtParser {
  constructor(buf) { this.buf = buf; this.pos = 0; }
  readUByte()  { return this.buf.readUInt8(this.pos++); }
  readByte()   { return this.buf.readInt8(this.pos++); }
  readShort()  { const v = this.buf.readInt16BE(this.pos); this.pos += 2; return v; }
  readUShort() { const v = this.buf.readUInt16BE(this.pos); this.pos += 2; return v; }
  readInt()    { const v = this.buf.readInt32BE(this.pos); this.pos += 4; return v; }
  readLong()   { const v = this.buf.readBigInt64BE(this.pos); this.pos += 8; return v; }
  readFloat()  { const v = this.buf.readFloatBE(this.pos); this.pos += 4; return v; }
  readDouble() { const v = this.buf.readDoubleBE(this.pos); this.pos += 8; return v; }
  readString() {
    const len = this.readUShort();
    const str = this.buf.toString('utf8', this.pos, this.pos + len);
    this.pos += len; return str;
  }
  readPayload(type) {
    switch (type) {
      case 1: return this.readByte();
      case 2: return this.readShort();
      case 3: return this.readInt();
      case 4: return this.readLong();
      case 5: return this.readFloat();
      case 6: return this.readDouble();
      case 7: { const len = this.readInt(); const a = this.buf.slice(this.pos, this.pos + len); this.pos += len; return a; }
      case 8: return this.readString();
      case 9: { const et = this.readUByte(); const cnt = this.readInt(); const l = []; for(let i=0;i<cnt;i++) l.push(this.readPayload(et)); return l; }
      case 10: { const o = {}; while(true){ const t=this.readUByte(); if(t===0)break; const n=this.readString(); o[n]=this.readPayload(t); } return o; }
      case 11: { const len = this.readInt(); const a = new Int32Array(len); for(let i=0;i<len;i++) a[i] = this.readInt(); return a; }
      case 12: { const len = this.readInt(); const a = new BigInt64Array(len); for(let i=0;i<len;i++) a[i] = this.readLong(); return a; }
      default: throw new Error(`Unknown NBT type ${type}`);
    }
  }
  parseRoot() {
    const type = this.readUByte();
    this.readString();
    return this.readPayload(type);
  }
}

// ── Litematic packed BlockStates 解码（跨 long 边界紧凑打包） ──────────────
/**
 * 解码 Litematica 的 packed long array → 索引数组。
 *
 * <p><b>关键修复：BigInt 的 `>>` 是算术右移（符号扩展），但 Litematica 的 long
 * 数组应当按无符号解读。必须先 `& ULONG_MASK` 把每个 long 转成无符号 BigInt，
 * 否则当某个 long 的高位 bit 为 1 时，算术右移会把错误的 1 位塞进解码出的索引值，
 * 造成：超出 palette 范围 → 空洞；映射错位 → 错误方块（如黄色混凝土）。</b></p>
 *
 * @param {BigInt64Array} packed 输入打包数据
 * @param {number} count 体积（x*y*z 索引数量）
 * @param {number} bits  每索引占位数 = max(2, ceil(log2(palette.length)))
 * @returns {Uint32Array} 索引数组
 */
const ULONG_MASK = (1n << 64n) - 1n;
function unpackLitematicaIndices(packed, count, bits) {
  const out = new Uint32Array(count);
  const mask = (1n << BigInt(bits)) - 1n;

  for (let i = 0; i < count; i++) {
    const startBit = i * bits;
    const startLong = (startBit >>> 6);                  // i*bits / 64
    const startBitInLong = BigInt(startBit & 0x3F);      // i*bits % 64
    const endBit = startBit + bits - 1;
    const endLong = (endBit >>> 6);

    // 取出 long 并强制按无符号解读（屏蔽 BigInt 的算术右移问题）
    let v;
    const lo = packed[startLong] & ULONG_MASK;
    if (startLong === endLong) {
      v = (lo >> startBitInLong) & mask;
    } else {
      const hi = packed[endLong] & ULONG_MASK;
      const bitsInLo = 64n - startBitInLong;
      v = ((lo >> startBitInLong) | (hi << bitsInLo)) & mask;
    }
    out[i] = Number(v);
  }
  return out;
}

// ── 1. 读取 .litematic ──────────────────────────────────────────────────────
if (!fs.existsSync(LITEMATIC_PATH)) {
  console.error(`Litematic file not found: ${LITEMATIC_PATH}`);
  process.exit(1);
}
console.log(`Reading: ${LITEMATIC_PATH}`);
const raw = fs.readFileSync(LITEMATIC_PATH);
const decompressed = zlib.gunzipSync(raw);
const root = new NbtParser(decompressed).parseRoot();

const meta = root.Metadata || {};
console.log(`  Version: ${root.Version}, DataVersion: ${root.MinecraftDataVersion}`);
console.log(`  Name: ${meta.Name}, Author: ${meta.Author}`);
console.log(`  TotalBlocks: ${meta.TotalBlocks}, TotalVolume: ${meta.TotalVolume}`);
console.log(`  EnclosingSize: ${meta.EnclosingSize?.x} × ${meta.EnclosingSize?.y} × ${meta.EnclosingSize?.z}`);

const regions = root.Regions || {};
const regionNames = Object.keys(regions);
console.log(`  Regions: ${regionNames.length}`);

// ── 2. 解码所有 region 的方块到统一坐标系 ──────────────────────────────────
// 输出：blockAt(x,y,z) -> stateKey
// stateKey：普通方块为 "minecraft:xxx"；半砖/楼梯在读入时已压成完整方块名；
// 活板门仍为 "id|prop=val,..."（若有）。
const allBlocks = new Map(); // key "x,y,z" -> stateKey
const stateInfo = new Map(); // stateKey -> { name, properties: { ... } }
let minX=Infinity,minY=Infinity,minZ=Infinity,maxX=-Infinity,maxY=-Infinity,maxZ=-Infinity;

function stateKeyOf(state) {
  const name = state.Name;
  if (!isDirectionalBlock(name)) return name;
  const props = state.Properties || {};
  const keys = Object.keys(props).sort();
  if (keys.length === 0) return name;
  return name + '|' + keys.map(k => `${k}=${props[k]}`).join(',');
}

function registerState(state) {
  const key = stateKeyOf(state);
  if (!stateInfo.has(key)) {
    const props = {};
    if (isDirectionalBlock(state.Name) && state.Properties && typeof state.Properties === 'object') {
      for (const k of Object.keys(state.Properties).sort()) {
        props[k] = String(state.Properties[k]);
      }
    }
    stateInfo.set(key, { name: state.Name, properties: props });
  }
  return key;
}

for (const regionName of regionNames) {
  const r = regions[regionName];
  const palette = r.BlockStatePalette;
  const packed  = r.BlockStates;
  const pos     = r.Position;
  const size    = r.Size;

  // 计算实际方向（Size 任意分量可能负数，表示从 Position 向负方向延伸）
  const sx = size.x, sy = size.y, sz = size.z;
  const absX = Math.abs(sx), absY = Math.abs(sy), absZ = Math.abs(sz);
  const dirX = sx >= 0 ? 1 : -1;
  const dirY = sy >= 0 ? 1 : -1;
  const dirZ = sz >= 0 ? 1 : -1;

  // 真正的 region 起点（左下后角）
  const baseX = pos.x + (sx < 0 ? sx + 1 : 0);
  const baseY = pos.y + (sy < 0 ? sy + 1 : 0);
  const baseZ = pos.z + (sz < 0 ? sz + 1 : 0);

  // 计算 bits/count
  const count = absX * absY * absZ;
  const bits  = Math.max(2, Math.ceil(Math.log2(palette.length)));

  console.log(`  Region "${regionName}": ${absX}×${absY}×${absZ} = ${count} cells, ${palette.length} palette, ${bits} bits/cell, packed.length=${packed.length}`);

  const indices = unpackLitematicaIndices(packed, count, bits);

  // 遍历每个 cell，存到全局坐标
  // Litematica 在 region 内顺序：y-major, z-mid, x-fast (x++ 先，再 z++，再 y++)
  // 公式：i = (y * z_size + z) * x_size + x
  let i = 0;
  for (let ly = 0; ly < absY; ly++) {
    for (let lz = 0; lz < absZ; lz++) {
      for (let lx = 0; lx < absX; lx++) {
        const idx = indices[i++];
        const raw = palette[idx];
        if (!raw) continue;
        if (!raw.Name || raw.Name === 'minecraft:air') continue;
        // SKIP 列表按投影「原始」方块 id 匹配；归一成 planks 后会与全船木板冲突，故跳过项直接视为石英位材质链
        const state = SKIP_BLOCKS.has(raw.Name)
          ? { Name: QUARTZ_BLOCK, Properties: {} }
          : normalizeLitematicState(raw);
        const wx = baseX + lx;
        const wy = baseY + ly;
        const wz = baseZ + lz;
        const key = registerState(state);
        allBlocks.set(`${wx},${wy},${wz}`, key);
        if (wx < minX) minX = wx;
        if (wy < minY) minY = wy;
        if (wz < minZ) minZ = wz;
        if (wx > maxX) maxX = wx;
        if (wy > maxY) maxY = wy;
        if (wz > maxZ) maxZ = wz;
      }
    }
  }
}

console.log(`Total non-air blocks: ${allBlocks.size}`);
console.log(`Bounds X[${minX},${maxX}] Y[${minY},${maxY}] Z[${minZ},${maxZ}]`);
const W = maxX - minX + 1;
const H = maxY - minY + 1;
const D = maxZ - minZ + 1;
console.log(`Dimensions: ${W}W × ${H}H × ${D}D`);

// ── 3. 统计方块类型 ────────────────────────────────────────────────────────
const stateCount = new Map();
for (const key of allBlocks.values()) {
  stateCount.set(key, (stateCount.get(key) || 0) + 1);
}
console.log(`\nTop 20 state keys (by usage):`);
[...stateCount.entries()].sort((a,b)=>b[1]-a[1]).slice(0, 20).forEach(([k,c])=>{
  console.log(`  ${String(c).padStart(7)} × ${k}`);
});
console.log(`Total unique state keys: ${stateCount.size}`);

// 按"方块名"统计（楼梯/台阶按 name 归并显示一次）
const nameCount = new Map();
for (const key of allBlocks.values()) {
  const info = stateInfo.get(key);
  const name = info ? info.name : key;
  nameCount.set(name, (nameCount.get(name) || 0) + 1);
}
console.log(`Total unique block names: ${nameCount.size}`);

// ── 4. 装饰符号分配 ─────────────────────────────────────────────────────────
// 'X' 谓词：原石英位置 → gravity_stabilization_casing
// 'B' 谓词：原黑色混凝土位置 → extreme_density_casing
// SKIP_BLOCKS 位置并入 'X'（不再要求杂项装饰）
// 其余 stateKey 各占一个字符：方块名 → Predicates.blocks（半砖/楼梯已合并为完整方块）
const decoSet = new Set();
for (const key of stateCount.keys()) {
  const info = stateInfo.get(key);
  const name = info ? info.name : key;
  if (name === QUARTZ_BLOCK) continue;
  if (name === BLACK_CONCRETE) continue;
  if (SKIP_BLOCKS.has(name)) continue;
  if (name === 'minecraft:air') continue;
  decoSet.add(key);
}
const decoList = [...decoSet].sort();
const decoSym = new Map();
{
  let poolIdx = 0;
  for (const key of decoList) {
    if (poolIdx >= DECO_POOL.length) {
      throw new Error(`Too many state keys: ${decoList.length} > ${DECO_POOL.length}`);
    }
    decoSym.set(key, DECO_POOL[poolIdx++]);
  }
}
console.log(`Symbols: 'S' + 'X' + 'B' + ${decoList.length} deco state keys + ' '`);

// ── 5. 定位控制器（正面中心石英方块） ───────────────────────────────────────
const targetCX = Math.round((minX + maxX) / 2);
const targetCY = Math.round((minY + maxY) / 2);

let ctrlPos = null, bestDist = Infinity;
// 在最前面 5 层石英方块中找离中心最近的（石英方块无 properties，stateKey 即方块名）
for (const [posKey, stateKey] of allBlocks) {
  if (stateKey !== QUARTZ_BLOCK) continue;
  const [bx,by,bz] = posKey.split(',').map(Number);
  if (bz < maxZ - 5) continue;
  const d = Math.abs(bx-targetCX) + Math.abs(by-targetCY) + (maxZ - bz) * 3;
  if (d < bestDist) { bestDist = d; ctrlPos = [bx,by,bz]; }
}
if (!ctrlPos) {
  for (const [posKey] of allBlocks) {
    const [bx,by,bz] = posKey.split(',').map(Number);
    if (bz < maxZ - 5) continue;
    const d = Math.abs(bx-targetCX) + Math.abs(by-targetCY);
    if (d < bestDist) { bestDist = d; ctrlPos = [bx,by,bz]; }
  }
}
console.log(`Controller world pos: (${ctrlPos.join(',')})`);
console.log(`Controller local pos (origin-zeroed, bottom-up Y): (${ctrlPos[0]-minX}, ${ctrlPos[1]-minY}, ${ctrlPos[2]-minZ})`);
const ctrlKey = ctrlPos.join(',');

// ── 6. 构建三维字符网格 ────────────────────────────────────────────────────
// GTCEu FactoryBlockPattern.start() 默认 stringDir = UP，
// 即每个 aisle 的字符串数组：index 0 = Y 最低（底部），index H-1 = Y 最高（顶部）
console.log('\nBuilding character grid (bottom-up Y order)...');
const layers = new Array(D);
for (let z = 0; z < D; z++) {
  const layer = new Array(H);
  for (let yi = 0; yi < H; yi++) {
    const wy = minY + yi; // ← 底→顶，与 GT 的 stringDir=UP 一致
    const row = new Array(W);
    for (let x = 0; x < W; x++) {
      const wx = minX + x;
      const wz = minZ + z;
      const key = `${wx},${wy},${wz}`;
      if (key === ctrlKey) {
        row[x] = SYM_CONTROLLER;
      } else if (allBlocks.has(key)) {
        const stateKey = allBlocks.get(key);
        const info = stateInfo.get(stateKey);
        const name = info ? info.name : stateKey;
        if (name === QUARTZ_BLOCK || SKIP_BLOCKS.has(name)) {
          row[x] = SYM_QUARTZ;
        } else if (name === BLACK_CONCRETE) {
          row[x] = SYM_BLACK;
        } else {
          row[x] = decoSym.get(stateKey);
        }
      } else {
        row[x] = SYM_AIR;
      }
    }
    layer[yi] = row.join('');
  }
  layers[z] = layer;
  if (z % 20 === 0) process.stdout.write(`  Z ${z}/${D}\r`);
}
console.log('\nGrid built.');

// ── 7. 清空旧的 HyperionLayerPart*.java、HyperionEmbeddedNbtData.java ─────
fs.mkdirSync(OUTPUT_DIR, { recursive: true });
for (const f of fs.readdirSync(OUTPUT_DIR)) {
  if (/^HyperionLayerPart\d+\.java$/.test(f) || f === 'HyperionEmbeddedNbtData.java') {
    fs.unlinkSync(path.join(OUTPUT_DIR, f));
  }
}

// ── 8. 写 HyperionLayerPart*.java ──────────────────────────────────────────
const numParts = Math.ceil(D / LAYERS_PER_FILE);
for (let pi = 0; pi < numParts; pi++) {
  const startZ = pi * LAYERS_PER_FILE;
  const endZ   = Math.min(startZ + LAYERS_PER_FILE, D);
  const cn = `HyperionLayerPart${pi + 1}`;
  const lines = [
    `package ${PACKAGE};`,
    '',
    `/** Auto-generated from .litematic. Part ${pi + 1}/${numParts}. */`,
    `public final class ${cn} {`,
    `    private ${cn}() {}`,
    '',
  ];
  for (let z = startZ; z < endZ; z++) {
    const layerNum = String(z - startZ + 1).padStart(3, '0');
    const rows = layers[z].map(r => `        "${r.replace(/\\/g,'\\\\').replace(/"/g,'\\"')}"`);
    lines.push(`    public static final String[] LAYER_${layerNum} = {`);
    lines.push(rows.join(',\n'));
    lines.push('    };');
    lines.push('');
  }
  lines.push('}');
  fs.writeFileSync(path.join(OUTPUT_DIR, `${cn}.java`), lines.join('\n'), 'utf8');
}
console.log(`Written ${numParts} Part files.`);

// ── 9. 写 HyperionPatternData.java ─────────────────────────────────────────
function blockRef(blockName) {
  const [ns, bp] = blockName.split(':');
  return `BuiltInRegistries.BLOCK.get(new ResourceLocation("${ns}", "${bp}"))`;
}

/** 把 sym 转为 Java 安全字段名后缀 */
function symToFieldId(sym) {
  if (/^[A-Za-z0-9]$/.test(sym)) return sym;
  return 'x' + sym.charCodeAt(0).toString(16);
}

const QUARTZ_REPLACE = BLOCK_REPLACE.get(QUARTZ_BLOCK);
const BLACK_REPLACE  = BLOCK_REPLACE.get(BLACK_CONCRETE);

const patLines = [
  `package ${PACKAGE};`,
  '',
  'import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;',
  'import com.gregtechceu.gtceu.api.pattern.BlockPattern;',
  'import com.gregtechceu.gtceu.api.pattern.FactoryBlockPattern;',
  'import com.gregtechceu.gtceu.api.pattern.Predicates;',
  'import net.minecraft.core.registries.BuiltInRegistries;',
  'import net.minecraft.nbt.CompoundTag;',
  'import net.minecraft.nbt.NbtUtils;',
  'import net.minecraft.resources.ResourceLocation;',
  'import net.minecraft.world.level.block.Blocks;',
  'import net.minecraft.world.level.block.state.BlockState;',
  'import java.util.concurrent.atomic.AtomicBoolean;',
  '',
  '/**',
  ' * 休伯利安号旗舰多方块 Pattern。',
  ` * 由 tools/hyperion_litematic_gen.js 从单一 .litematic 投影生成。`,
  ` * 维度: ${W}W × ${H}H × ${D}D，总方块: ${allBlocks.size}。`,
  ` * 控制器位置(归零本地坐标，底向上 Y): (${ctrlPos[0]-minX}, ${ctrlPos[1]-minY}, ${ctrlPos[2]-minZ})`,
  ' *',
  " * 'S' = 控制器",
  ` * 'X' = ${QUARTZ_REPLACE}（原石英块位置）`,
  ` * 'B' = ${BLACK_REPLACE}（原黑色混凝土位置）`,
  " * ' ' = 空气",
  ' * 其余字符 = 各自方块（半砖/楼梯已换成同材质完整方块，仅 Predicates.blocks）。',
  ' * 活板门若有则仍按完整 BlockState 锁朝向。',
  ' */',
  'public final class HyperionPatternData {',
  '',
  '    private static final AtomicBoolean BUILT = new AtomicBoolean(false);',
  '    private static BlockPattern cachedPattern;',
  '',
  '    /**',
  '     * 把 Name + Properties 还原成 BlockState。',
  '     * 借助 NbtUtils.readBlockState 实现，失败回退 AIR，避免初始化抛异常。',
  '     */',
  '    private static BlockState parseState(String name, java.util.function.Consumer<CompoundTag> propsBuilder) {',
  '        try {',
  '            CompoundTag root = new CompoundTag();',
  '            root.putString("Name", name);',
  '            CompoundTag props = new CompoundTag();',
  '            if (propsBuilder != null) propsBuilder.accept(props);',
  '            if (!props.isEmpty()) root.put("Properties", props);',
  '            BlockState state = NbtUtils.readBlockState(BuiltInRegistries.BLOCK.asLookup(), root);',
  '            return state == null ? Blocks.AIR.defaultBlockState() : state;',
  '        } catch (Exception e) {',
  '            return Blocks.AIR.defaultBlockState();',
  '        }',
  '    }',
  '',
];

// 为活板门等方向敏感方块生成 BlockState 静态字段（半砖/楼梯已改为完整方块，不需要）
for (const [stateKey, sym] of decoSym) {
  const info = stateInfo.get(stateKey);
  if (!info || !isDirectionalBlock(info.name)) continue;
  const propEntries = Object.entries(info.properties || {});
  const fname = `S_${symToFieldId(sym)}`;
  if (propEntries.length === 0) {
    patLines.push(`    private static final BlockState ${fname} = parseState("${info.name}", null); // ${stateKey}`);
  } else {
    patLines.push(`    private static final BlockState ${fname} = parseState("${info.name}", p -> {`);
    for (const [k, v] of propEntries) {
      patLines.push(`        p.putString("${k}", "${v}");`);
    }
    patLines.push(`    }); // ${stateKey}`);
  }
}
patLines.push('');

patLines.push('    private HyperionPatternData() {}');
patLines.push('');
patLines.push('    public static BlockPattern createPattern(MultiblockMachineDefinition definition) {');
patLines.push('        if (BUILT.get() && cachedPattern != null) return cachedPattern;');
patLines.push('        synchronized (BUILT) {');
patLines.push('            if (BUILT.get() && cachedPattern != null) return cachedPattern;');
patLines.push('            cachedPattern = build(definition);');
patLines.push('            BUILT.set(true);');
patLines.push('            return cachedPattern;');
patLines.push('        }');
patLines.push('    }');
patLines.push('');
patLines.push('    private static BlockPattern build(MultiblockMachineDefinition definition) {');
patLines.push('        FactoryBlockPattern pat = FactoryBlockPattern.start()');

for (let pi = 0; pi < numParts; pi++) {
  const startZ = pi * LAYERS_PER_FILE;
  const endZ   = Math.min(startZ + LAYERS_PER_FILE, D);
  const cn = `HyperionLayerPart${pi + 1}`;
  for (let z = startZ; z < endZ; z++) {
    const layerNum = String(z - startZ + 1).padStart(3, '0');
    patLines.push(`                .aisle(${cn}.LAYER_${layerNum})`);
  }
}
patLines[patLines.length - 1] += ';';
patLines.push('');

patLines.push(`        pat = pat.where('S', Predicates.controller(Predicates.blocks(definition.getBlock())));`);
patLines.push('');
patLines.push(`        // 'X' = 原石英块位置 → ${QUARTZ_REPLACE}`);
patLines.push(`        pat = pat.where('X', Predicates.blocks(${blockRef(QUARTZ_REPLACE)}));`);
patLines.push('');
patLines.push(`        // 'B' = 原黑色混凝土位置 → ${BLACK_REPLACE}`);
patLines.push(`        pat = pat.where('B', Predicates.blocks(${blockRef(BLACK_REPLACE)}));`);
patLines.push('');
// 每个 deco state → Predicates.blocks(替换后方块) 或 Predicates.states(STATE)
for (const [stateKey, sym] of decoSym) {
  const info = stateInfo.get(stateKey);
  const name = info ? info.name : stateKey;
  const esc = sym.replace(/\\/g,'\\\\').replace(/'/g,"\\'");
  if (info && isDirectionalBlock(info.name)) {
    const fname = `S_${symToFieldId(sym)}`;
    patLines.push(`        pat = pat.where('${esc}', Predicates.states(${fname})); // ${stateKey}`);
  } else {
    const targetName = BLOCK_REPLACE.get(name) || name;
    if (BLOCK_REPLACE.has(name)) {
      patLines.push(`        pat = pat.where('${esc}', Predicates.blocks(${blockRef(targetName)})); // ${name} → ${targetName}`);
    } else {
      patLines.push(`        pat = pat.where('${esc}', Predicates.blocks(${blockRef(targetName)})); // ${name}`);
    }
  }
}
patLines.push('');
patLines.push(`        pat = pat.where(' ', Predicates.air());`);
patLines.push('');
patLines.push('        return pat.build();');
patLines.push('    }');
patLines.push('}');

fs.writeFileSync(path.join(OUTPUT_DIR, 'HyperionPatternData.java'), patLines.join('\n'), 'utf8');
console.log('Written HyperionPatternData.java');

console.log('\n=== Generation complete ===');
console.log(`Source: ${LITEMATIC_PATH}`);
console.log(`Dimensions: ${W} × ${H} × ${D} = ${W*H*D} cells (${allBlocks.size} non-air)`);
console.log(`Parts: ${numParts}, deco symbols: ${decoList.length}`);

// 【变更记录 #1】2026-10-23 23:41:24（内测5名称统一维护）：删除旧项目名引用；新增本条维护记录；修改项目路径、启动标识或纹理目录为 HK3GTL 对应名称；用途为统一工具与构建引用，保留原有业务逻辑。
