/**
 * 生成多方块控制器 overlay 贴图（GT 风格屏幕，完全不透明）。
 * overlay_front.png：深色面板 + 蓝色指示灯 + 绿色状态条
 * overlay_front_active.png：活跃态（指示灯更亮）
 * overlay_front_active_emissive.png：发光层（仅指示灯）
 * 其他面（back/top/bottom/side）：1x1 透明 PNG（让机壳纹理显示）
 */
import sharp from 'sharp';
import fs from 'fs';
import path from 'path';

const OUT = 'src/main/resources/assets/hk3gtl/textures/block/overlay/default';
fs.mkdirSync(OUT, { recursive: true });

const S = 16;

function rgba(r, g, b, a = 255) { return [r, g, b, a]; }

function createPixelBuffer(w, h, fill = [0, 0, 0, 0]) {
  const buf = Buffer.alloc(w * h * 4);
  for (let i = 0; i < w * h; i++) {
    buf[i * 4]     = fill[0];
    buf[i * 4 + 1] = fill[1];
    buf[i * 4 + 2] = fill[2];
    buf[i * 4 + 3] = fill[3];
  }
  return buf;
}

function setPixel(buf, w, x, y, color) {
  if (x < 0 || x >= w || y < 0 || y >= S) return;
  const idx = (y * w + x) * 4;
  buf[idx]     = color[0];
  buf[idx + 1] = color[1];
  buf[idx + 2] = color[2];
  buf[idx + 3] = color[3];
}

function fillRect(buf, w, x1, y1, x2, y2, color) {
  for (let y = y1; y < y2; y++)
    for (let x = x1; x < x2; x++)
      setPixel(buf, w, x, y, color);
}

// 颜色定义（参照 GT 风格控制器屏幕）
const C_FRAME_DARK  = rgba(35, 35, 40);
const C_FRAME_LIGHT = rgba(55, 55, 62);
const C_FRAME_EDGE  = rgba(70, 70, 78);
const C_SCREEN_BG   = rgba(15, 18, 28);
const C_SCREEN_DARK = rgba(10, 12, 20);
const C_INDICATOR   = rgba(40, 100, 180);
const C_INDICATOR_A = rgba(60, 140, 240);
const C_GREEN_BAR   = rgba(30, 160, 60);
const C_GREEN_BAR_A = rgba(50, 220, 80);
const C_AMBER       = rgba(180, 140, 30);
const C_AMBER_A     = rgba(240, 200, 50);

function drawFrontOverlay(active) {
  const buf = createPixelBuffer(S, S, C_FRAME_DARK);

  // 外框高光边
  fillRect(buf, S, 0, 0, S, 1, C_FRAME_EDGE);
  fillRect(buf, S, 0, 0, 1, S, C_FRAME_EDGE);
  fillRect(buf, S, 0, S - 1, S, S, rgba(20, 20, 25));
  fillRect(buf, S, S - 1, 0, S, S, rgba(20, 20, 25));

  // 内框
  fillRect(buf, S, 1, 1, S - 1, S - 1, C_FRAME_LIGHT);

  // 屏幕区域 (2,2) → (14,14)
  fillRect(buf, S, 2, 2, 14, 14, C_SCREEN_BG);
  fillRect(buf, S, 3, 3, 13, 13, C_SCREEN_DARK);

  // 屏幕内边框线
  fillRect(buf, S, 2, 2, 14, 3, rgba(25, 40, 70));
  fillRect(buf, S, 2, 2, 3, 14, rgba(25, 40, 70));

  const indColor = active ? C_INDICATOR_A : C_INDICATOR;
  const greenCol = active ? C_GREEN_BAR_A : C_GREEN_BAR;
  const amberCol = active ? C_AMBER_A : C_AMBER;

  // 6 个蓝色指示灯 (2行3列)
  const positions = [
    [4, 4], [7, 4], [10, 4],
    [4, 7], [7, 7], [10, 7],
  ];
  for (const [px, py] of positions) {
    fillRect(buf, S, px, py, px + 2, py + 2, indColor);
  }

  // 底部绿色状态条
  fillRect(buf, S, 4, 10, 9, 12, greenCol);

  // 底部琥珀指示灯
  fillRect(buf, S, 10, 10, 12, 12, amberCol);

  return buf;
}

function drawEmissive() {
  const buf = createPixelBuffer(S, S);

  const indColor = rgba(80, 160, 255, 200);
  const greenCol = rgba(80, 255, 120, 180);
  const amberCol = rgba(255, 220, 80, 180);

  const positions = [
    [4, 4], [7, 4], [10, 4],
    [4, 7], [7, 7], [10, 7],
  ];
  for (const [px, py] of positions) {
    fillRect(buf, S, px, py, px + 2, py + 2, indColor);
  }
  fillRect(buf, S, 4, 10, 9, 12, greenCol);
  fillRect(buf, S, 10, 10, 12, 12, amberCol);

  return buf;
}

async function savePng(name, buf, w = S, h = S) {
  const out = path.join(OUT, name);
  await sharp(buf, { raw: { width: w, height: h, channels: 4 } })
    .png()
    .toFile(out);
  console.log(`  ✓ ${out}`);
}

// 1x1 透明 PNG（非正面使用）
const TRANSPARENT_1x1 = createPixelBuffer(1, 1);

async function main() {
  console.log('=== 生成 overlay 贴图 ===');

  // 正面
  await savePng('overlay_front.png', drawFrontOverlay(false));
  await savePng('overlay_front_active.png', drawFrontOverlay(true));
  await savePng('overlay_front_active_emissive.png', drawEmissive());

  // 非正面（透明，让机壳纹理完全显示）
  const faces = ['back', 'top', 'bottom', 'side'];
  const states = ['', '_active'];
  for (const face of faces) {
    for (const state of states) {
      await savePng(`overlay_${face}${state}.png`, TRANSPARENT_1x1, 1, 1);
    }
  }

  console.log('\n完成！');
}

main().catch(console.error);
