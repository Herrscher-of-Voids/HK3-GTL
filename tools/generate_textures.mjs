/**
 * 贴图生成脚本：基于 GT 原版机壳样式，生成本模组所有机壳 + 结构方块 + 控制器覆盖层贴图。
 * 使用 sharp 库处理 16x16 PNG。
 *
 * 用法: node tools/generate_textures.mjs
 */
import sharp from 'sharp';
import path from 'path';
import fs from 'fs';

const TEX_DIR = 'src/main/resources/assets/hk3gtl/textures/block';
const CASINGS_DIR = path.join(TEX_DIR, 'casings');

fs.mkdirSync(CASINGS_DIR, { recursive: true });
fs.mkdirSync(path.join(TEX_DIR, 'overlay'), { recursive: true });

const REF_BASE = 'C:/Users/OWNER/.cursor/projects/c-Users-OWNER-Desktop-hk3gtl/assets/c__Users_OWNER_AppData_Roaming_Cursor_User_workspaceStorage_980cbbac315a606c5f08cbfa0d147962_images_aluminium_bronze_casing-f639c574-1eb7-4275-85ef-f6feadd100f3.png';
const REF_CTM = 'C:/Users/OWNER/.cursor/projects/c-Users-OWNER-Desktop-hk3gtl/assets/c__Users_OWNER_AppData_Roaming_Cursor_User_workspaceStorage_980cbbac315a606c5f08cbfa0d147962_images_aluminium_bronze_casing_ctm-a681fb97-1681-428f-8546-7a5a5ae10330.png';

// 每种机壳的色调偏移 (hue rotation in degrees)
// 参考图的铝青铜色大约 hue=50 (暖黄色)
// 我们通过 tint 方法实现：先转灰度，再叠加目标色
const CASINGS = [
  { name: 'casing_soulium',             r: 120, g: 70,  b: 180 }, // 暗紫
  { name: 'casing_reinforced_soulium',  r: 160, g: 95,  b: 210 }, // 亮紫
  { name: 'casing_abyss_mechanical',    r: 60,  g: 80,  b: 160 }, // 深蓝
  { name: 'casing_abyss_research',      r: 40,  g: 190, b: 170 }, // 青色
  { name: 'casing_abyss_energy',        r: 220, g: 170, b: 40  }, // 橙金
];

const STRUCTURES = [
  { name: 'coil_abyss_flux',              r: 60,  g: 100, b: 220 }, // 蓝色线圈
  { name: 'structure_abyss_cooling_unit',  r: 140, g: 200, b: 240 }, // 蓝白
  { name: 'structure_communication_array', r: 100, g: 180, b: 120 }, // 绿色科技
  { name: 'structure_data_pillar',         r: 80,  g: 140, b: 200 }, // 数据蓝
];

/**
 * 读取参考图 -> 转灰度 -> 叠加目标颜色 -> 保存
 */
async function tintTexture(srcPath, dstPath, r, g, b) {
  const img = sharp(srcPath);
  const meta = await img.metadata();
  const { data, info } = await img.raw().toBuffer({ resolveWithObject: true });
  const channels = info.channels;
  const pixels = Buffer.alloc(info.width * info.height * 4);

  for (let i = 0; i < info.width * info.height; i++) {
    const si = i * channels;
    const sr = data[si], sg = data[si + 1], sb = data[si + 2];
    const sa = channels === 4 ? data[si + 3] : 255;

    // 灰度亮度
    const luma = 0.299 * sr + 0.587 * sg + 0.114 * sb;
    const factor = luma / 255;

    const di = i * 4;
    pixels[di]     = Math.min(255, Math.round(r * factor));
    pixels[di + 1] = Math.min(255, Math.round(g * factor));
    pixels[di + 2] = Math.min(255, Math.round(b * factor));
    pixels[di + 3] = sa;
  }

  await sharp(pixels, { raw: { width: info.width, height: info.height, channels: 4 } })
    .png()
    .toFile(dstPath);
}

/**
 * 生成 16x16 的控制器正面屏幕覆盖层
 * 模仿 GT 控制器正面：外框灰色金属 + 中央黑色屏幕 + 小指示灯
 */
async function generateOverlay(dstPath) {
  const W = 16, H = 16;
  const pixels = Buffer.alloc(W * H * 4, 0);

  function setPixel(x, y, r, g, b, a = 255) {
    if (x < 0 || x >= W || y < 0 || y >= H) return;
    const i = (y * W + x) * 4;
    pixels[i] = r; pixels[i+1] = g; pixels[i+2] = b; pixels[i+3] = a;
  }

  // 外框: 浅灰金属边 (2px边距)
  for (let x = 2; x < 14; x++) {
    for (let y = 2; y < 14; y++) {
      setPixel(x, y, 45, 48, 55, 255); // 深灰屏幕背景
    }
  }
  // 上下边框线
  for (let x = 2; x < 14; x++) {
    setPixel(x, 2, 160, 165, 175, 255);
    setPixel(x, 13, 100, 105, 115, 255);
  }
  // 左右边框线
  for (let y = 2; y < 14; y++) {
    setPixel(2, y, 150, 155, 165, 255);
    setPixel(13, y, 110, 115, 125, 255);
  }

  // 屏幕内容区 (4,4 to 11,11)
  for (let x = 4; x < 12; x++) {
    for (let y = 4; y < 10; y++) {
      setPixel(x, y, 20, 25, 35, 255); // 纯黑屏幕
    }
  }

  // 屏幕网格线 (模拟 HUD)
  for (let x = 5; x < 11; x += 2) {
    for (let y = 5; y < 9; y += 2) {
      setPixel(x, y, 50, 120, 200, 255); // 蓝色像素点
    }
  }

  // 指示灯条 (底部)
  setPixel(5, 11, 50, 200, 80, 255);  // 绿灯
  setPixel(6, 11, 50, 200, 80, 200);
  setPixel(8, 11, 200, 180, 50, 255); // 黄灯
  setPixel(10, 11, 80, 160, 220, 255); // 蓝灯

  // 进度条 (屏幕底部)
  for (let x = 4; x < 9; x++) {
    setPixel(x, 10, 40, 100, 180, 255);
  }

  await sharp(pixels, { raw: { width: W, height: H, channels: 4 } })
    .png()
    .toFile(dstPath);
}

/**
 * 生成半透明玻璃贴图
 */
async function generateGlass(dstPath, r, g, b) {
  const W = 16, H = 16;
  const pixels = Buffer.alloc(W * H * 4, 0);

  function setPixel(x, y, pr, pg, pb, a) {
    const i = (y * W + x) * 4;
    pixels[i] = pr; pixels[i+1] = pg; pixels[i+2] = pb; pixels[i+3] = a;
  }

  // 半透明填充
  for (let x = 0; x < W; x++) {
    for (let y = 0; y < H; y++) {
      setPixel(x, y, r, g, b, 100);
    }
  }

  // 边框 (不透明)
  for (let x = 0; x < W; x++) {
    setPixel(x, 0, r+30, g+30, b+30, 200);
    setPixel(x, 15, r-20, g-20, b-20, 200);
  }
  for (let y = 0; y < H; y++) {
    setPixel(0, y, r+30, g+30, b+30, 200);
    setPixel(15, y, r-20, g-20, b-20, 200);
  }

  // 对角高光
  for (let i = 2; i < 6; i++) {
    setPixel(i, i, 255, 255, 255, 60);
  }

  await sharp(pixels, { raw: { width: W, height: H, channels: 4 } })
    .png()
    .toFile(dstPath);
}

async function main() {
  console.log('=== HK3GTL 贴图生成器 ===');

  // 1. 机壳贴图 (base + CTM)
  for (const c of CASINGS) {
    console.log(`  机壳: ${c.name}`);
    await tintTexture(REF_BASE, path.join(CASINGS_DIR, `${c.name}.png`), c.r, c.g, c.b);
    await tintTexture(REF_CTM, path.join(CASINGS_DIR, `${c.name}_ctm.png`), c.r, c.g, c.b);

    // 写入 LDLib CTM 元数据
    const mcmeta = { ldlib: { connection: `hk3gtl:block/casings/${c.name}_ctm` } };
    fs.writeFileSync(
      path.join(CASINGS_DIR, `${c.name}.png.mcmeta`),
      JSON.stringify(mcmeta, null, 2)
    );
  }

  // 2. 结构方块贴图 (base + CTM)
  for (const s of STRUCTURES) {
    console.log(`  结构: ${s.name}`);
    await tintTexture(REF_BASE, path.join(CASINGS_DIR, `${s.name}.png`), s.r, s.g, s.b);
    await tintTexture(REF_CTM, path.join(CASINGS_DIR, `${s.name}_ctm.png`), s.r, s.g, s.b);

    const mcmeta = { ldlib: { connection: `hk3gtl:block/casings/${s.name}_ctm` } };
    fs.writeFileSync(
      path.join(CASINGS_DIR, `${s.name}.png.mcmeta`),
      JSON.stringify(mcmeta, null, 2)
    );
  }

  // 3. 玻璃贴图
  console.log('  玻璃: glass_honkai_stabilized');
  await generateGlass(path.join(CASINGS_DIR, 'glass_honkai_stabilized.png'), 40, 200, 200);

  // 4. 控制器屏幕覆盖层
  console.log('  覆盖层: machine_overlay_front');
  await generateOverlay(path.join(TEX_DIR, 'overlay', 'machine_overlay_front.png'));

  console.log('=== 贴图生成完成 ===');
}

main().catch(console.error);
