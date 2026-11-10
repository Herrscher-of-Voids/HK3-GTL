/**
 * 综合资源修复脚本：
 * 1. 将所有子目录中的物品模型 JSON 复制到 models/item/ 扁平路径
 * 2. 为崩坏能稳定玻璃创建透明模型
 * 3. 为结构方块（线圈/冷却/通讯/数据柱）生成独特贴图
 * 4. 生成多方块控制器 overlay 贴图
 */
import sharp from 'sharp';
import fs from 'fs';
import path from 'path';

const ASSETS = 'src/main/resources/assets/hk3gtl';
const MODEL_DIR = `${ASSETS}/models/item`;
const TEX_DIR = `${ASSETS}/textures`;
const BLOCK_MODEL_DIR = `${ASSETS}/models/block`;

function ensureDir(dir) { fs.mkdirSync(dir, { recursive: true }); }

// ═══════════════════════════════════════════
//  1. 修复物品模型路径（子目录 → 扁平）
// ═══════════════════════════════════════════

function flattenItemModels() {
  console.log('\n=== 1. 修复物品模型路径 ===');
  const subdirs = ['abyss/components', 'abyss/circuits', 'abyss', 'honkai', 'soulium', 'research/permits'];
  let count = 0;

  for (const subdir of subdirs) {
    const dir = path.join(MODEL_DIR, subdir);
    if (!fs.existsSync(dir)) continue;

    const files = fs.readdirSync(dir).filter(f => f.endsWith('.json'));
    for (const file of files) {
      const srcPath = path.join(dir, file);
      const dstPath = path.join(MODEL_DIR, file);

      if (fs.existsSync(dstPath)) continue;

      let raw = fs.readFileSync(srcPath, 'utf-8');
      if (raw.charCodeAt(0) === 0xFEFF) raw = raw.slice(1);
      const content = JSON.parse(raw);
      fs.writeFileSync(dstPath, JSON.stringify(content, null, 2) + '\n');
      count++;
      console.log(`  复制: ${subdir}/${file} → item/${file}`);
    }
  }
  console.log(`  共复制 ${count} 个模型到扁平路径`);
}

// ═══════════════════════════════════════════
//  2. 玻璃方块透明模型
// ═══════════════════════════════════════════

function fixGlassModel() {
  console.log('\n=== 2. 修复玻璃模型（透明渲染） ===');
  const modelPath = path.join(BLOCK_MODEL_DIR, 'structure/glass_honkai_stabilized.json');
  const model = {
    parent: 'minecraft:block/cube_all',
    textures: {
      all: 'hk3gtl:block/casings/glass_honkai_stabilized'
    },
    render_type: 'minecraft:translucent'
  };
  fs.writeFileSync(modelPath, JSON.stringify(model, null, 2) + '\n');
  console.log('  已添加 render_type: translucent');
}

// ═══════════════════════════════════════════
//  3. 结构方块独特贴图
// ═══════════════════════════════════════════

async function generatePixelArt(dstPath, width, height, drawFn) {
  const pixels = Buffer.alloc(width * height * 4);
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const [r, g, b, a] = drawFn(x, y);
      const i = (y * width + x) * 4;
      pixels[i] = r; pixels[i+1] = g; pixels[i+2] = b; pixels[i+3] = a;
    }
  }
  ensureDir(path.dirname(dstPath));
  await sharp(pixels, { raw: { width, height, channels: 4 } }).png().toFile(dstPath);
}

async function generateStructureTextures() {
  console.log('\n=== 3. 生成结构方块独特贴图 ===');

  // 崩坏能稳定玻璃（半透明青色）
  console.log('  玻璃: glass_honkai_stabilized');
  await generatePixelArt(
    path.join(TEX_DIR, 'block/casings/glass_honkai_stabilized.png'), 16, 16,
    (x, y) => {
      const edge = x === 0 || x === 15 || y === 0 || y === 15;
      const inner = x >= 2 && x <= 13 && y >= 2 && y <= 13;
      if (edge) return [20, 60, 80, 200];
      if (inner) {
        const glow = ((x + y) % 4 === 0) ? 20 : 0;
        return [40 + glow, 180 + glow, 200 + glow, 140];
      }
      return [30, 120, 150, 170];
    }
  );

  // 海渊磁束线圈（铜橙色螺旋线圈纹理）
  console.log('  线圈: coil_abyss_flux');
  await generatePixelArt(
    path.join(TEX_DIR, 'block/casings/coil_abyss_flux.png'), 16, 16,
    (x, y) => {
      const diagonal = (x + y) % 4;
      const isCoil = diagonal === 0 || diagonal === 1;
      const border = x === 0 || x === 15 || y === 0 || y === 15;
      if (border) return [40, 25, 15, 255];
      if (isCoil) {
        const bright = ((x * 3 + y * 7) % 5 === 0) ? 30 : 0;
        return [200 + bright, 120 + bright, 40, 255];
      }
      const dark = ((x ^ y) % 3 === 0) ? 10 : 0;
      return [30 + dark, 20 + dark, 35 + dark, 255];
    }
  );
  // 移除线圈的 CTM mcmeta（线圈不需要连接纹理）
  const coilMcmeta = path.join(TEX_DIR, 'block/casings/coil_abyss_flux.png.mcmeta');
  if (fs.existsSync(coilMcmeta)) fs.unlinkSync(coilMcmeta);
  const coilCtm = path.join(TEX_DIR, 'block/casings/coil_abyss_flux_ctm.png');
  if (fs.existsSync(coilCtm)) fs.unlinkSync(coilCtm);

  // 海渊冷却构件（冰蓝色散热片纹理）
  console.log('  冷却: structure_abyss_cooling_unit');
  await generatePixelArt(
    path.join(TEX_DIR, 'block/casings/structure_abyss_cooling_unit.png'), 16, 16,
    (x, y) => {
      const border = x === 0 || x === 15 || y === 0 || y === 15;
      if (border) return [20, 30, 50, 255];
      // 水平散热片纹理
      const fin = y % 3 === 0;
      const vent = (x >= 6 && x <= 9 && y >= 6 && y <= 9);
      if (vent) return [100, 200, 240, 255];
      if (fin) {
        const shimmer = ((x * 5) % 7 === 0) ? 15 : 0;
        return [60 + shimmer, 140 + shimmer, 200 + shimmer, 255];
      }
      return [35, 55, 80, 255];
    }
  );
  // 移除冷却构件的 CTM
  const coolMcmeta = path.join(TEX_DIR, 'block/casings/structure_abyss_cooling_unit.png.mcmeta');
  if (fs.existsSync(coolMcmeta)) fs.unlinkSync(coolMcmeta);
  const coolCtm = path.join(TEX_DIR, 'block/casings/structure_abyss_cooling_unit_ctm.png');
  if (fs.existsSync(coolCtm)) fs.unlinkSync(coolCtm);

  // 通讯阵列块（绿色电路板纹理 + 信号天线图案）
  console.log('  通讯: structure_communication_array');
  await generatePixelArt(
    path.join(TEX_DIR, 'block/casings/structure_communication_array.png'), 16, 16,
    (x, y) => {
      const border = x === 0 || x === 15 || y === 0 || y === 15;
      if (border) return [15, 40, 20, 255];
      // 电路板走线
      const trace = (x % 4 === 2) || (y % 4 === 2);
      // 中心天线图案
      const antenna = (x === 7 || x === 8) && y >= 2 && y <= 8;
      const dish = y === 3 && x >= 5 && x <= 10;
      if (antenna || dish) return [40, 220, 120, 255];
      if (trace) {
        const glow = ((x + y) % 6 === 0) ? 20 : 0;
        return [30 + glow, 160 + glow, 80 + glow, 255];
      }
      return [20, 50, 30, 255];
    }
  );
  // 移除通讯阵列的 CTM
  const commMcmeta = path.join(TEX_DIR, 'block/casings/structure_communication_array.png.mcmeta');
  if (fs.existsSync(commMcmeta)) fs.unlinkSync(commMcmeta);
  const commCtm = path.join(TEX_DIR, 'block/casings/structure_communication_array_ctm.png');
  if (fs.existsSync(commCtm)) fs.unlinkSync(commCtm);

  // 数据柱（深蓝色数据流纹理 + 垂直光柱）
  console.log('  数据: structure_data_pillar');
  await generatePixelArt(
    path.join(TEX_DIR, 'block/casings/structure_data_pillar.png'), 16, 16,
    (x, y) => {
      const border = x === 0 || x === 15 || y === 0 || y === 15;
      if (border) return [10, 15, 40, 255];
      // 垂直数据流光柱
      const pillar1 = x === 4 || x === 11;
      const pillar2 = x === 7 || x === 8;
      // 水平数据节点
      const node = (y % 5 === 0) && (x >= 3 && x <= 12);
      if (node) return [80, 140, 255, 255];
      if (pillar2) {
        const pulse = ((y * 3) % 5 === 0) ? 40 : 0;
        return [40 + pulse, 80 + pulse, 200 + pulse, 255];
      }
      if (pillar1) return [30, 60, 150, 255];
      const noise = ((x * 7 + y * 13) % 11 === 0) ? 8 : 0;
      return [15 + noise, 20 + noise, 50 + noise, 255];
    }
  );
  // 移除数据柱的 CTM
  const dataMcmeta = path.join(TEX_DIR, 'block/casings/structure_data_pillar.png.mcmeta');
  if (fs.existsSync(dataMcmeta)) fs.unlinkSync(dataMcmeta);
  const dataCtm = path.join(TEX_DIR, 'block/casings/structure_data_pillar_ctm.png');
  if (fs.existsSync(dataCtm)) fs.unlinkSync(dataCtm);

  // 更新结构方块模型为 cube_all（不用 CTM）
  const structBlocks = ['coil_abyss_flux', 'structure_abyss_cooling_unit',
    'structure_communication_array', 'structure_data_pillar'];
  for (const name of structBlocks) {
    const modelPath = path.join(BLOCK_MODEL_DIR, `structure/${name}.json`);
    const model = {
      parent: 'minecraft:block/cube_all',
      textures: { all: `hk3gtl:block/casings/${name}` }
    };
    fs.writeFileSync(modelPath, JSON.stringify(model, null, 2) + '\n');
  }
}

// ═══════════════════════════════════════════
//  4. 多方块控制器 overlay 贴图
// ═══════════════════════════════════════════

async function generateControllerOverlays() {
  console.log('\n=== 4. 生成多方块控制器 overlay ===');

  const overlayDir = path.join(TEX_DIR, 'block/overlay/default');
  ensureDir(overlayDir);

  // 正面 overlay（屏幕，透明背景让机壳透出）
  console.log('  overlay_front.png');
  await generatePixelArt(
    path.join(overlayDir, 'overlay_front.png'), 16, 16,
    (x, y) => {
      // 屏幕区域: 3-12, 2-10
      const screenX = x >= 3 && x <= 12;
      const screenY = y >= 2 && y <= 10;
      const screenBorder = screenX && screenY &&
        (x === 3 || x === 12 || y === 2 || y === 10);
      const screenInner = screenX && screenY && !screenBorder;

      if (screenBorder) return [60, 70, 80, 220];
      if (screenInner) {
        // 屏幕内容：深色背景 + 小图标
        const statusBar = y === 4 && x >= 5 && x <= 10;
        const dataLine1 = y === 6 && x >= 5 && x <= 9;
        const dataLine2 = y === 8 && x >= 5 && x <= 8;
        const indicator = x === 10 && y >= 6 && y <= 8;
        if (statusBar) return [40, 200, 120, 200];
        if (dataLine1 || dataLine2) return [80, 160, 220, 180];
        if (indicator) return [220, 180, 40, 200];
        return [15, 20, 35, 180];
      }
      // 屏幕外完全透明（让机壳贴图显示）
      return [0, 0, 0, 0];
    }
  );

  // 正面 active overlay
  console.log('  overlay_front_active.png');
  await generatePixelArt(
    path.join(overlayDir, 'overlay_front_active.png'), 16, 16,
    (x, y) => {
      const screenX = x >= 3 && x <= 12;
      const screenY = y >= 2 && y <= 10;
      const screenBorder = screenX && screenY &&
        (x === 3 || x === 12 || y === 2 || y === 10);
      const screenInner = screenX && screenY && !screenBorder;

      if (screenBorder) return [40, 180, 100, 230];
      if (screenInner) {
        const statusBar = y === 4 && x >= 5 && x <= 10;
        const progressBar = y === 6 && x >= 5 && x <= 9;
        const arrow = y === 8 && x >= 6 && x <= 9;
        const indicator = x === 10 && y >= 6 && y <= 8;
        if (statusBar) return [40, 255, 120, 220];
        if (progressBar) return [100, 200, 255, 200];
        if (arrow) return [200, 220, 60, 200];
        if (indicator) return [60, 255, 100, 220];
        return [10, 25, 40, 190];
      }
      return [0, 0, 0, 0];
    }
  );

  // 正面 active emissive（发光层）
  console.log('  overlay_front_active_emissive.png');
  await generatePixelArt(
    path.join(overlayDir, 'overlay_front_active_emissive.png'), 16, 16,
    (x, y) => {
      const screenX = x >= 3 && x <= 12;
      const screenY = y >= 2 && y <= 10;
      const screenInner = screenX && screenY &&
        !(x === 3 || x === 12 || y === 2 || y === 10);

      if (screenInner) {
        const statusBar = y === 4 && x >= 5 && x <= 10;
        const indicator = x === 10 && y >= 6 && y <= 8;
        if (statusBar || indicator) return [80, 255, 160, 180];
        return [0, 0, 0, 0];
      }
      return [0, 0, 0, 0];
    }
  );

  // 其他面的 overlay 全透明（不需要额外装饰）
  for (const face of ['overlay_back', 'overlay_top', 'overlay_bottom', 'overlay_side',
                        'overlay_back_active', 'overlay_top_active', 'overlay_bottom_active', 'overlay_side_active']) {
    const fPath = path.join(overlayDir, `${face}.png`);
    if (!fs.existsSync(fPath)) {
      await generatePixelArt(fPath, 16, 16, () => [0, 0, 0, 0]);
    }
  }

  console.log('  overlay 生成完成');
}

// ═══════════════════════════════════════════
//  主函数
// ═══════════════════════════════════════════

async function main() {
  console.log('==============================');
  console.log('  HK3GTL 资源综合修复脚本');
  console.log('==============================');

  flattenItemModels();
  fixGlassModel();
  await generateStructureTextures();
  await generateControllerOverlays();

  console.log('\n=== 全部完成 ===');
}

main().catch(console.error);
