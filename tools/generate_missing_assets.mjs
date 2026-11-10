/**
 * 批量创建缺失的 item model JSON 和贴图。
 * 同时为海渊 II/III/IV 部件和电路生成改色贴图。
 */
import sharp from 'sharp';
import fs from 'fs';
import path from 'path';

const MODEL_DIR = 'src/main/resources/assets/hk3gtl/models/item';
const TEX_DIR = 'src/main/resources/assets/hk3gtl/textures/item';

function ensureDir(dir) { fs.mkdirSync(dir, { recursive: true }); }

function writeModel(modelPath, texturePath) {
  ensureDir(path.dirname(modelPath));
  fs.writeFileSync(modelPath, JSON.stringify({
    parent: 'minecraft:item/generated',
    textures: { layer0: texturePath }
  }, null, 2) + '\n');
}

async function tintTexture(srcPath, dstPath, r, g, b) {
  const img = sharp(srcPath);
  const { data, info } = await img.raw().toBuffer({ resolveWithObject: true });
  const channels = info.channels;
  const pixels = Buffer.alloc(info.width * info.height * 4);
  for (let i = 0; i < info.width * info.height; i++) {
    const si = i * channels;
    const sr = data[si], sg = data[si + 1], sb = data[si + 2];
    const sa = channels === 4 ? data[si + 3] : 255;
    const luma = 0.299 * sr + 0.587 * sg + 0.114 * sb;
    const f = luma / 255;
    const di = i * 4;
    pixels[di]     = Math.min(255, Math.round(r * f));
    pixels[di + 1] = Math.min(255, Math.round(g * f));
    pixels[di + 2] = Math.min(255, Math.round(b * f));
    pixels[di + 3] = sa;
  }
  ensureDir(path.dirname(dstPath));
  await sharp(pixels, { raw: { width: info.width, height: info.height, channels: 4 } })
    .png().toFile(dstPath);
}

// 生成16x16占位贴图
async function generatePlaceholder(dstPath, r, g, b) {
  const W = 16, H = 16;
  const pixels = Buffer.alloc(W * H * 4);
  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      const i = (y * W + x) * 4;
      const edge = x === 0 || x === 15 || y === 0 || y === 15;
      const inner = x >= 4 && x <= 11 && y >= 4 && y <= 11;
      pixels[i]     = edge ? Math.min(255, r+40) : inner ? Math.min(255, r+20) : r;
      pixels[i + 1] = edge ? Math.min(255, g+40) : inner ? Math.min(255, g+20) : g;
      pixels[i + 2] = edge ? Math.min(255, b+40) : inner ? Math.min(255, b+20) : b;
      pixels[i + 3] = 255;
    }
  }
  ensureDir(path.dirname(dstPath));
  await sharp(pixels, { raw: { width: W, height: H, channels: 4 } })
    .png().toFile(dstPath);
}

async function main() {
  console.log('=== 缺失资产生成 ===');

  // ─── 1. AbyssFunctionalItems: model + placeholder texture ───
  const functionalItems = [
    'artifact_void_archives', 'data_precivilization_fragment',
    'abyss_energy_modulator', 'abyss_data_core', 'abyss_stable_frame',
    'abyss_reactor_core', 'abyss_measurement_array', 'reactor_stabilizer'
  ];
  const funcColors = [
    [60,40,120], [80,120,200], [200,160,40], [40,180,180],
    [100,100,160], [200,80,60], [60,160,120], [140,140,160]
  ];

  for (let i = 0; i < functionalItems.length; i++) {
    const name = functionalItems[i];
    const [r,g,b] = funcColors[i];
    console.log(`  功能件: ${name}`);
    writeModel(
      path.join(MODEL_DIR, 'abyss', `${name}.json`),
      `hk3gtl:item/abyss/${name}`
    );
    await generatePlaceholder(path.join(TEX_DIR, 'abyss', `${name}.png`), r, g, b);
  }

  // ─── 2. data_research_package / world_bubble_sample ───
  const honkaiExtra = ['data_research_package', 'world_bubble_sample'];
  const honkaiColors = [[80,140,200], [120,200,220]];
  for (let i = 0; i < honkaiExtra.length; i++) {
    const name = honkaiExtra[i];
    if (!fs.existsSync(path.join(MODEL_DIR, 'honkai', `${name}.json`))) {
      console.log(`  崩坏件: ${name}`);
      writeModel(path.join(MODEL_DIR, 'honkai', `${name}.json`), `hk3gtl:item/honkai/${name}`);
      await generatePlaceholder(path.join(TEX_DIR, 'honkai', `${name}.png`), ...honkaiColors[i]);
    }
  }

  // ─── 3. 海渊 II/III/IV 部件: 改色贴图 ───
  const componentTypes = [
    'electric_motor', 'electric_piston', 'electric_pump', 'conveyor_module',
    'robot_arm', 'field_generator', 'emitter', 'sensor'
  ];
  // 每级颜色: II=蓝紫, III=红橙, IV=金白
  const tierTints = {
    2: { r: 100, g: 80, b: 220 },
    3: { r: 220, g: 100, b: 60 },
    4: { r: 240, g: 220, b: 140 }
  };

  for (const tier of [2, 3, 4]) {
    const { r, g, b } = tierTints[tier];
    for (const comp of componentTypes) {
      const name = `${comp}_${["hbv","hcv","hrv","hdv"][tier-1]}`;
      const srcTex = path.join(TEX_DIR, 'abyss', 'components', `${comp}_hbv.png`);
      const dstTex = path.join(TEX_DIR, 'abyss', 'components', `${name}.png`);
      const modelPath = path.join(MODEL_DIR, 'abyss', 'components', `${name}.json`);

      if (!fs.existsSync(modelPath)) {
        console.log(`  部件: ${name}`);
        writeModel(modelPath, `hk3gtl:item/abyss/components/${name}`);
      }
      if (!fs.existsSync(dstTex) && fs.existsSync(srcTex)) {
        await tintTexture(srcTex, dstTex, r, g, b);
      }
    }
  }

  // ─── 4. 海渊 II/III/IV 电路: 改色贴图 ───
  // 电路 2/3/4 已有贴图和模型，但我们也添加 fluid_regulator 的模型
  const fluidRegItems = ['fluid_regulator_hcv', 'fluid_regulator_hrv', 'fluid_regulator_hdv'];
  // fluid_regulator 不在 componentTypes 里，单独处理
  for (const tier of [2, 3, 4]) {
    const name = `fluid_regulator_${["hbv","hcv","hrv","hdv"][tier-1]}`;
    const srcTex = path.join(TEX_DIR, 'abyss', 'components', 'fluid_regulator_hbv.png');
    const dstTex = path.join(TEX_DIR, 'abyss', 'components', `${name}.png`);
    const modelPath = path.join(MODEL_DIR, 'abyss', 'components', `${name}.json`);
    const { r, g, b } = tierTints[tier];
    if (!fs.existsSync(modelPath)) {
      console.log(`  流体调节: ${name}`);
      writeModel(modelPath, `hk3gtl:item/abyss/components/${name}`);
    }
    if (!fs.existsSync(dstTex) && fs.existsSync(srcTex)) {
      await tintTexture(srcTex, dstTex, r, g, b);
    }
  }

  // ─── 5. Structure block item models ───
  const structBlocks = [
    'glass_honkai_stabilized', 'coil_abyss_flux',
    'structure_abyss_cooling_unit', 'structure_communication_array', 'structure_data_pillar'
  ];
  for (const name of structBlocks) {
    const modelPath = path.join(MODEL_DIR, `${name}.json`);
    if (!fs.existsSync(modelPath)) {
      console.log(`  结构方块: ${name}`);
      ensureDir(path.dirname(modelPath));
      fs.writeFileSync(modelPath, JSON.stringify({
        parent: `hk3gtl:block/structure/${name}`
      }, null, 2) + '\n');
    }
  }

  console.log('=== 完成 ===');
}

main().catch(console.error);

// 变更记录 #107 · 2026-09-30 02:20:26 · 修订107：同步正式电压键及检查，旧历史保留。
