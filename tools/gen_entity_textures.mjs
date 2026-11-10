/**
 * 生成空之律者·西琳的实体贴图和翅膀贴图。
 * - void_queen_sirin.png: 64x64 玩家皮肤格式，紫白配色
 * - sirin_wing.png: 32x32 翅膀贴图，左半为右翼，右半为左翼
 */
import sharp from 'sharp';
import fs from 'fs';

const OUT = 'src/main/resources/assets/hk3gtl/textures/entity';
fs.mkdirSync(OUT, { recursive: true });

function createBuf(w, h, fill = [0, 0, 0, 0]) {
  const buf = Buffer.alloc(w * h * 4);
  for (let i = 0; i < w * h; i++) {
    buf[i * 4]     = fill[0];
    buf[i * 4 + 1] = fill[1];
    buf[i * 4 + 2] = fill[2];
    buf[i * 4 + 3] = fill[3];
  }
  return buf;
}

function setPixel(buf, w, x, y, r, g, b, a = 255) {
  if (x < 0 || y < 0 || x >= w) return;
  const idx = (y * w + x) * 4;
  buf[idx] = r; buf[idx+1] = g; buf[idx+2] = b; buf[idx+3] = a;
}

function fillRect(buf, w, x1, y1, x2, y2, r, g, b, a = 255) {
  for (let y = y1; y < y2; y++)
    for (let x = x1; x < x2; x++)
      setPixel(buf, w, x, y, r, g, b, a);
}

// ═══════════════════════════════════════
//  1. 西琳皮肤 (64x64, 标准 MC 玩家皮肤格式)
// ═══════════════════════════════════════

function generateSirinSkin() {
  const W = 64, H = 64;
  const buf = createBuf(W, H);

  // 主要颜色 — 空之律者主题
  const white = [235, 230, 240];      // 白色基调
  const purple = [120, 60, 180];      // 紫色主色
  const darkPurple = [80, 30, 130];   // 深紫
  const gold = [220, 180, 60];        // 金色点缀
  const skin = [240, 210, 200];       // 肤色
  const hair = [200, 190, 220];       // 银白发色
  const eyePurple = [160, 80, 220];   // 紫眼

  // === HEAD (8x8 at 0,0 in UV space) ===
  // 头顶 (UV: 8,0 → 16,8 前面)
  // 标准皮肤UV映射:
  // 头部前面: (8,8)-(16,16)
  // 头部后面: (24,8)-(32,16)
  // 头部上面: (8,0)-(16,8)
  // 头部下面: (16,0)-(24,8)
  // 头部右面: (0,8)-(8,16)
  // 头部左面: (16,8)-(24,16)

  // 头部上方 — 银白发
  fillRect(buf, W, 8, 0, 16, 8, ...hair);

  // 头部下方
  fillRect(buf, W, 16, 0, 24, 8, ...darkPurple);

  // 头部右
  fillRect(buf, W, 0, 8, 8, 16, ...hair);

  // 头部前面 — 脸
  fillRect(buf, W, 8, 8, 16, 16, ...skin);
  // 发型（头顶2行）
  fillRect(buf, W, 8, 8, 16, 10, ...hair);
  // 眼睛
  setPixel(buf, W, 10, 12, ...eyePurple);
  setPixel(buf, W, 13, 12, ...eyePurple);

  // 头部左
  fillRect(buf, W, 16, 8, 24, 16, ...hair);

  // 头部后
  fillRect(buf, W, 24, 8, 32, 16, ...hair);

  // === BODY (8x12 ===)
  // 身体前面: (20,20)-(28,32)
  // 身体后面: (32,20)-(40,32)
  // 身体上面: (20,16)-(28,20)
  // 身体下面: (28,16)-(36,20)
  // 身体右: (16,20)-(20,32)
  // 身体左: (28,20)-(32,32)

  fillRect(buf, W, 20, 16, 28, 20, ...white);       // 上
  fillRect(buf, W, 28, 16, 36, 20, ...white);       // 下
  fillRect(buf, W, 16, 20, 20, 32, ...purple);      // 右
  fillRect(buf, W, 20, 20, 28, 32, ...white);       // 前
  fillRect(buf, W, 28, 20, 32, 32, ...purple);      // 左
  fillRect(buf, W, 32, 20, 40, 32, ...white);       // 后

  // 身体前面装饰：紫色十字
  fillRect(buf, W, 23, 20, 25, 32, ...purple);
  fillRect(buf, W, 20, 24, 28, 26, ...purple);
  // 金色中心
  setPixel(buf, W, 23, 24, ...gold);
  setPixel(buf, W, 24, 24, ...gold);
  setPixel(buf, W, 23, 25, ...gold);
  setPixel(buf, W, 24, 25, ...gold);

  // === RIGHT ARM (4x12) ===
  // 前面: (44,20)-(48,32)
  fillRect(buf, W, 40, 16, 44, 20, ...white);
  fillRect(buf, W, 44, 16, 48, 20, ...white);
  fillRect(buf, W, 40, 20, 44, 32, ...white);       // 右外侧
  fillRect(buf, W, 44, 20, 48, 32, ...white);       // 前面
  fillRect(buf, W, 48, 20, 52, 32, ...white);       // 左内侧
  fillRect(buf, W, 52, 20, 56, 32, ...white);       // 后面
  // 紫色袖口
  fillRect(buf, W, 44, 28, 48, 32, ...purple);

  // === RIGHT LEG (4x12) ===
  // UV: (0,16)-(16,32)
  fillRect(buf, W, 0, 16, 4, 20, ...darkPurple);
  fillRect(buf, W, 4, 16, 8, 20, ...darkPurple);
  fillRect(buf, W, 0, 20, 4, 32, ...darkPurple);
  fillRect(buf, W, 4, 20, 8, 32, ...darkPurple);
  fillRect(buf, W, 8, 20, 12, 32, ...darkPurple);
  fillRect(buf, W, 12, 20, 16, 32, ...darkPurple);

  // === LEFT LEG (4x12) - 1.8+ 格式在下半区 ===
  // UV: (16,48)-(32,64)
  fillRect(buf, W, 16, 48, 20, 52, ...darkPurple);
  fillRect(buf, W, 20, 48, 24, 52, ...darkPurple);
  fillRect(buf, W, 16, 52, 20, 64, ...darkPurple);
  fillRect(buf, W, 20, 52, 24, 64, ...darkPurple);
  fillRect(buf, W, 24, 52, 28, 64, ...darkPurple);
  fillRect(buf, W, 28, 52, 32, 64, ...darkPurple);

  // === LEFT ARM (4x12) - 1.8+ 格式在下半区 ===
  // UV: (32,48)-(48,64)
  fillRect(buf, W, 32, 48, 36, 52, ...white);
  fillRect(buf, W, 36, 48, 40, 52, ...white);
  fillRect(buf, W, 32, 52, 36, 64, ...white);
  fillRect(buf, W, 36, 52, 40, 64, ...white);
  fillRect(buf, W, 40, 52, 44, 64, ...white);
  fillRect(buf, W, 44, 52, 48, 64, ...white);
  fillRect(buf, W, 36, 60, 40, 64, ...purple);

  return buf;
}

// ═══════════════════════════════════════
//  2. 翅膀贴图 (32x32)
//  左半 (0-15, 0-31) = 右翼
//  右半 (16-31, 0-31) = 左翼
// ═══════════════════════════════════════

function generateWingTexture() {
  const W = 32, H = 32;
  const buf = createBuf(W, H);

  // 翅膀配色 — 淡紫/白，半透明发光效果
  const wingEdge  = [180, 140, 220, 200];
  const wingMid   = [220, 200, 245, 180];
  const wingCore  = [255, 240, 255, 220];
  const wingGlow  = [200, 160, 255, 160];

  // 右翼 (左半部分, x: 0-15)
  drawWingSide(buf, W, 0, false, wingEdge, wingMid, wingCore, wingGlow);

  // 左翼 (右半部分, x: 16-31) — 水平镜像
  drawWingSide(buf, W, 16, true, wingEdge, wingMid, wingCore, wingGlow);

  return buf;
}

function drawWingSide(buf, W, offsetX, mirror, edge, mid, core, glow) {
  // 翅膀形状 — 羽翼轮廓（每行的宽度）
  const shape = [
    [7, 1],    // y=2: 起始窄
    [6, 2],    // y=3
    [5, 4],    // y=4
    [4, 6],    // y=5
    [3, 8],    // y=6
    [2, 10],   // y=7
    [2, 11],   // y=8
    [1, 12],   // y=9
    [1, 13],   // y=10
    [0, 14],   // y=11
    [0, 14],   // y=12
    [0, 15],   // y=13: 最宽
    [0, 15],   // y=14
    [0, 14],   // y=15
    [1, 13],   // y=16
    [1, 13],   // y=17
    [2, 12],   // y=18
    [2, 11],   // y=19
    [3, 10],   // y=20
    [3, 9],    // y=21
    [4, 8],    // y=22
    [4, 7],    // y=23
    [5, 6],    // y=24
    [5, 5],    // y=25
    [6, 4],    // y=26
    [7, 3],    // y=27
    [8, 2],    // y=28
    [9, 1],    // y=29
  ];

  for (let i = 0; i < shape.length; i++) {
    const y = i + 2;
    const [start, width] = shape[i];

    for (let j = 0; j < width; j++) {
      const x = mirror ? (15 - start - j) + offsetX : start + j + offsetX;

      // 越靠内越亮（核心发光）
      let color;
      const ratio = width > 1 ? j / (width - 1) : 0.5;
      if (ratio < 0.15 || ratio > 0.85) {
        color = edge;
      } else if (ratio < 0.3 || ratio > 0.7) {
        color = mid;
      } else {
        color = i % 4 === 0 ? glow : core;
      }

      setPixel(buf, W, x, y, color[0], color[1], color[2], color[3]);
    }
  }
}

async function main() {
  console.log('=== 生成实体贴图 ===');

  const skin = generateSirinSkin();
  await sharp(skin, { raw: { width: 64, height: 64, channels: 4 } })
    .png().toFile(`${OUT}/void_queen_sirin.png`);
  console.log('  ✓ void_queen_sirin.png (64x64 皮肤)');

  const wing = generateWingTexture();
  await sharp(wing, { raw: { width: 32, height: 32, channels: 4 } })
    .png().toFile(`${OUT}/sirin_wing.png`);
  console.log('  ✓ sirin_wing.png (32x32 翅膀)');

  console.log('\n完成！');
}

main().catch(console.error);
