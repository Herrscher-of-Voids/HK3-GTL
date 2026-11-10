/**
 * 生成西琳 3D 翅膀贴图（参考 GodCore 的尖角设计，改为紫白配色）。
 * - sirin_wing_right.png (32x32): 右翼
 * - sirin_wing_left.png  (32x32): 左翼（水平镜像）
 * - sirin_wing_core.png  (16x16): 发光核心
 */
import sharp from 'sharp';
import fs from 'fs';

const OUT = 'src/main/resources/assets/hk3gtl/textures/entity';
fs.mkdirSync(OUT, { recursive: true });

function createBuf(w, h) { return Buffer.alloc(w * h * 4); }

function setPixel(buf, w, x, y, r, g, b, a = 255) {
  if (x < 0 || y < 0 || x >= w || y >= 32) return;
  const idx = (y * w + x) * 4;
  buf[idx] = r; buf[idx+1] = g; buf[idx+2] = b; buf[idx+3] = a;
}

function getPixel(buf, w, x, y) {
  const idx = (y * w + x) * 4;
  return [buf[idx], buf[idx+1], buf[idx+2], buf[idx+3]];
}

function lerp(a, b, t) { return Math.round(a + (b - a) * Math.max(0, Math.min(1, t))); }

function lerpColor(c1, c2, t) {
  return [lerp(c1[0], c2[0], t), lerp(c1[1], c2[1], t),
          lerp(c1[2], c2[2], t), lerp(c1[3], c2[3], t)];
}

// 颜色 — 空之律者主题
const C_ROOT  = [90, 30, 140, 255];     // 深紫根部
const C_MID   = [140, 70, 200, 255];    // 中紫主体
const C_LIGHT = [190, 140, 235, 255];   // 浅紫过渡
const C_TIP   = [240, 225, 255, 255];   // 白紫尖端
const C_EDGE  = [210, 180, 245, 200];   // 边缘高光

/**
 * 沿折线绘制一根羽翼（渐变粗细和颜色）。
 */
function drawFeather(buf, W, points, maxThick) {
  const len = points.length;
  for (let i = 0; i < len; i++) {
    const [cx, cy] = points[i];
    const t = i / Math.max(len - 1, 1); // 0=根, 1=尖
    const thick = Math.max(0, Math.round(maxThick * (1 - t * 0.9)));
    const baseCol = lerpColor(C_ROOT, C_MID, t * 1.5);
    const tipCol = lerpColor(C_MID, C_TIP, (t - 0.3) * 2);
    const col = t < 0.4 ? baseCol : tipCol;

    for (let dy = -thick; dy <= thick; dy++) {
      const edgeT = thick > 0 ? Math.abs(dy) / thick : 0;
      const px = lerpColor(col, C_EDGE, edgeT * 0.4);
      setPixel(buf, W, cx, cy + dy, px[0], px[1], px[2], px[3]);
    }
  }
}

/**
 * 生成右翼（32x32）。设计参考 GodCore：3 根尖锐羽翼 + 短装饰翼。
 */
function generateRightWing() {
  const W = 32, H = 32;
  const buf = createBuf(W, H);

  // 羽翼 1（最长，向右上 45° 展开）
  drawFeather(buf, W, [
    [3,24],[4,23],[5,22],[6,21],[7,20],[8,19],[9,18],[10,17],
    [11,16],[12,15],[13,14],[14,13],[15,12],[16,11],[17,10],
    [18,9],[19,8],[20,7],[21,6],[22,5],[23,4],[24,3],[25,2],
  ], 4);

  // 羽翼 2（中等长度，稍平）
  drawFeather(buf, W, [
    [3,22],[4,21],[5,20],[6,19],[7,18],[8,17],[9,17],[10,16],
    [11,16],[12,15],[13,15],[14,14],[15,14],[16,13],[17,13],
    [18,12],[19,12],[20,11],[21,11],
  ], 3);

  // 羽翼 3（短，向右偏下展开）
  drawFeather(buf, W, [
    [3,26],[4,25],[5,25],[6,25],[7,24],[8,24],[9,24],[10,23],
    [11,23],[12,23],[13,22],[14,22],[15,22],[16,22],
  ], 2);

  // 装饰短翼（向下方）
  drawFeather(buf, W, [
    [3,27],[4,28],[5,28],[6,29],[7,29],[8,29],[9,30],
  ], 1);

  // 根部填充（连接各羽翼的粗根）
  for (let y = 20; y <= 28; y++) {
    for (let x = 1; x <= 5; x++) {
      const t = (y - 20) / 8;
      const col = lerpColor(C_ROOT, C_MID, t * 0.5);
      setPixel(buf, W, x, y, col[0], col[1], col[2], col[3]);
    }
  }

  return buf;
}

function mirrorHorizontal(srcBuf, W, H) {
  const dst = createBuf(W, H);
  for (let y = 0; y < H; y++)
    for (let x = 0; x < W; x++) {
      const [r, g, b, a] = getPixel(srcBuf, W, x, y);
      setPixel(dst, W, W - 1 - x, y, r, g, b, a);
    }
  return dst;
}

function generateCore() {
  const W = 16, H = 16;
  const buf = createBuf(W, H);
  const cx = 7.5, cy = 7.5, radius = 4;
  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      const d = Math.sqrt((x - cx) ** 2 + (y - cy) ** 2);
      if (d > radius + 1) continue;
      const t = Math.min(1, d / radius);
      const alpha = Math.round(255 * Math.max(0, 1 - t * t));
      const col = lerpColor([255, 240, 200, 255], [180, 100, 220, 0], t);
      setPixel(buf, W, x, y, col[0], col[1], col[2], alpha);
    }
  }
  return buf;
}

async function savePng(name, buf, w, h) {
  await sharp(buf, { raw: { width: w, height: h, channels: 4 } })
    .png().toFile(`${OUT}/${name}`);
  console.log(`  ✓ ${name} (${w}x${h})`);
}

async function main() {
  console.log('=== 生成西琳 3D 翅膀贴图 ===');

  const right = generateRightWing();
  await savePng('sirin_wing_right.png', right, 32, 32);

  const left = mirrorHorizontal(right, 32, 32);
  await savePng('sirin_wing_left.png', left, 32, 32);

  const core = generateCore();
  await savePng('sirin_wing_core.png', core, 16, 16);

  // 清理旧版
  const old = `${OUT}/sirin_wing.png`;
  if (fs.existsSync(old)) { fs.unlinkSync(old); console.log('  × 已删除旧版 sirin_wing.png'); }

  console.log('完成！');
}

main().catch(console.error);
