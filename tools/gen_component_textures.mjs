/**
 * 生成魂钢组件/电路 16x16 贴图与物品模型（Imaginary/Quantum/Finality 模型；全阶段贴图）。
 * 依赖：sharp（项目 devDependencies）
 * 运行：node tools/gen_component_textures.mjs（需在仓库根目录）
 */
import sharp from 'sharp';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const ASSETS = path.join(ROOT, 'src/main/resources/assets/hk3gtl');
const TEX_ITEM = path.join(ASSETS, 'textures/item');
const MODELS_ITEM = path.join(ASSETS, 'models/item');

const SIZE = 16;

const STAGES = [
  {
    key: 'abyss',
    dark: [60, 80, 180],
    bright: [120, 140, 220],
  },
  {
    key: 'imaginary',
    dark: [200, 170, 40],
    bright: [255, 220, 100],
  },
  {
    key: 'quantum',
    dark: [160, 120, 220],
    bright: [200, 170, 255],
  },
  {
    key: 'finality',
    dark: [220, 200, 50],
    bright: [255, 240, 160],
  },
];

const COMPONENT_TYPES = [
  'electric_motor',
  'electric_piston',
  'electric_pump',
  'conveyor_module',
  'robot_arm',
  'field_generator',
  'emitter',
  'sensor',
];

const MCMETA_ANIMATION = JSON.stringify({ animation: { frametime: 4 } });

function lerp(a, b, t) {
  return a + (b - a) * t;
}

function lerpRgb(c1, c2, t) {
  return [
    Math.round(lerp(c1[0], c2[0], t)),
    Math.round(lerp(c1[1], c2[1], t)),
    Math.round(lerp(c1[2], c2[2], t)),
  ];
}

/** tierInStage: 1..4 → 0..1 插值（1 最深/暗，4 最亮） */
function stageTierColor(stage, tierInStage) {
  const t = (tierInStage - 1) / 3;
  return lerpRgb(stage.dark, stage.bright, t);
}

function clampByte(n) {
  return Math.max(0, Math.min(255, n | 0));
}

function shadeRgb(rgb, mul) {
  return [
    clampByte(rgb[0] * mul),
    clampByte(rgb[1] * mul),
    clampByte(rgb[2] * mul),
  ];
}

function mixRgb(a, b, t) {
  return [
    clampByte(lerp(a[0], b[0], t)),
    clampByte(lerp(a[1], b[1], t)),
    clampByte(lerp(a[2], b[2], t)),
  ];
}

function createBuffer() {
  return Buffer.alloc(SIZE * SIZE * 4, 0);
}

function setPx(buf, x, y, rgba) {
  if (x < 0 || x >= SIZE || y < 0 || y >= SIZE) return;
  const i = (y * SIZE + x) * 4;
  buf[i] = rgba[0];
  buf[i + 1] = rgba[1];
  buf[i + 2] = rgba[2];
  buf[i + 3] = rgba[3];
}

function fillRect(buf, x0, y0, x1, y1, rgba) {
  for (let y = y0; y < y1; y++)
    for (let x = x0; x < x1; x++) setPx(buf, x, y, rgba);
}

function distSq(x1, y1, x2, y2) {
  const dx = x1 - x2;
  const dy = y1 - y2;
  return dx * dx + dy * dy;
}

function fillCircle(buf, cx, cy, r, rgba) {
  const r2 = r * r;
  for (let y = 0; y < SIZE; y++)
    for (let x = 0; x < SIZE; x++) {
      if (distSq(x, y, cx, cy) <= r2 + 0.25) setPx(buf, x, y, rgba);
    }
}

/** 环形：内半径外半径（像素近似） */
function ring(buf, cx, cy, rInner, rOuter, rgba) {
  for (let y = 0; y < SIZE; y++)
    for (let x = 0; x < SIZE; x++) {
      const d2 = distSq(x, y, cx, cy);
      if (d2 >= rInner * rInner - 0.1 && d2 <= rOuter * rOuter + 0.25) setPx(buf, x, y, rgba);
    }
}

function line(buf, x0, y0, x1, y1, rgba) {
  let dx = Math.abs(x1 - x0);
  let dy = -Math.abs(y1 - y0);
  let sx = x0 < x1 ? 1 : -1;
  let sy = y0 < y1 ? 1 : -1;
  let err = dx + dy;
  let x = x0;
  let y = y0;
  for (;;) {
    setPx(buf, x, y, rgba);
    if (x === x1 && y === y1) break;
    const e2 = 2 * err;
    if (e2 >= dy) {
      err += dy;
      x += sx;
    }
    if (e2 <= dx) {
      err += dx;
      y += sy;
    }
  }
}

function drawDiamondOutline(buf, cx, cy, rx, ry, rgba) {
  const pts = [
    [cx, cy - ry],
    [cx + rx, cy],
    [cx, cy + ry],
    [cx - rx, cy],
  ];
  for (let i = 0; i < 4; i++) {
    const a = pts[i];
    const b = pts[(i + 1) % 4];
    line(buf, a[0], a[1], b[0], b[1], rgba);
  }
}

const WHITE = [255, 255, 255, 255];
const BLACK = [0, 0, 0, 255];

/**
 * @param {string} type
 * @param {[number,number,number]} base
 */
function drawComponent(type, base) {
  const buf = createBuffer();
  const body = [...base, 255];
  const hi = [...mixRgb(base, [255, 255, 255], 0.45), 255];
  const lo = [...shadeRgb(base, 0.55), 255];
  const mid = [...mixRgb(base, [255, 255, 255], 0.2), 255];
  const accent = [...mixRgb(base, [100, 200, 255], 0.25), 255];

  if (type === 'electric_motor') {
    fillCircle(buf, 8, 8, 5, lo);
    ring(buf, 8, 8, 3.2, 5, body);
    fillCircle(buf, 8, 8, 2, [20, 22, 30, 255]);
    // 齿
    for (const [ax, ay] of [
      [8, 2],
      [13, 5],
      [14, 8],
      [13, 11],
      [8, 14],
      [3, 11],
      [2, 8],
      [3, 5],
    ]) {
      setPx(buf, ax, ay, hi);
      setPx(buf, ax + (ax === 8 ? 0 : ax > 8 ? -1 : 1), ay + (ay === 8 ? 0 : ay > 8 ? -1 : 1), mid);
    }
    // 线圈
    fillRect(buf, 1, 6, 3, 10, accent);
    fillRect(buf, 13, 6, 15, 10, accent);
    line(buf, 3, 7, 5, 7, hi);
    line(buf, 3, 9, 5, 9, hi);
    line(buf, 11, 7, 13, 7, hi);
    line(buf, 11, 9, 13, 9, hi);
  } else if (type === 'electric_piston') {
    fillRect(buf, 2, 5, 8, 11, body);
    fillRect(buf, 2, 4, 8, 5, lo);
    fillRect(buf, 2, 11, 8, 12, hi);
    fillRect(buf, 8, 7, 14, 9, mid);
    fillRect(buf, 14, 6, 16, 10, hi);
    line(buf, 14, 6, 14, 5, lo);
    line(buf, 14, 9, 14, 10, lo);
  } else if (type === 'electric_pump') {
    fillRect(buf, 1, 7, 15, 9, body);
    fillRect(buf, 7, 1, 9, 15, body);
    fillRect(buf, 1, 6, 15, 7, lo);
    fillRect(buf, 1, 9, 15, 10, hi);
    fillRect(buf, 6, 1, 7, 15, lo);
    fillRect(buf, 9, 1, 10, 15, hi);
    fillCircle(buf, 8, 8, 3, mid);
    fillCircle(buf, 8, 8, 1, [30, 30, 40, 255]);
    for (let a = 0; a < 4; a++) {
      const rad = (a * Math.PI) / 2;
      const x = Math.round(8 + Math.cos(rad) * 2);
      const y = Math.round(8 + Math.sin(rad) * 2);
      setPx(buf, x, y, hi);
    }
  } else if (type === 'conveyor_module') {
    fillRect(buf, 1, 9, 15, 13, lo);
    fillRect(buf, 1, 10, 15, 12, body);
    for (const cx of [4, 8, 12]) {
      fillCircle(buf, cx, 11, 2, mid);
      fillCircle(buf, cx, 11, 1, hi);
    }
    fillRect(buf, 1, 9, 15, 10, hi);
    fillRect(buf, 1, 12, 15, 13, shadeRgb(base, 0.45).concat(255));
    line(buf, 2, 11, 14, 11, mixRgb(base, [255, 255, 255], 0.35).concat(255));
  } else if (type === 'robot_arm') {
    fillRect(buf, 10, 11, 15, 15, lo);
    fillRect(buf, 11, 4, 13, 12, body);
    fillRect(buf, 4, 4, 12, 6, mid);
    fillRect(buf, 4, 4, 6, 6, hi);
    fillRect(buf, 2, 3, 5, 5, lo);
    fillRect(buf, 1, 4, 3, 6, hi);
    fillRect(buf, 2, 5, 4, 5, accent);
  } else if (type === 'field_generator') {
    drawDiamondOutline(buf, 8, 8, 6, 6, lo);
    drawDiamondOutline(buf, 8, 8, 5, 5, body);
    fillRect(buf, 6, 6, 10, 10, [0, 0, 0, 0]);
    drawDiamondOutline(buf, 8, 8, 4, 4, mid);
    // 中心高亮（配合 mcmeta 动画观感）
    fillCircle(buf, 8, 8, 2, hi);
    setPx(buf, 8, 7, WHITE);
    setPx(buf, 7, 8, mixRgb(base, [200, 255, 255], 0.5).concat(255));
    setPx(buf, 9, 8, mixRgb(base, [200, 255, 255], 0.5).concat(255));
    setPx(buf, 8, 9, mixRgb(base, [255, 200, 255], 0.4).concat(255));
  } else if (type === 'emitter') {
    // 碟形弧
    for (let x = 3; x <= 13; x++) {
      const yy = 11 - Math.round(Math.sqrt(Math.max(0, 25 - (x - 8) * (x - 8))) * 0.65);
      setPx(buf, x, yy, body);
      setPx(buf, x, yy + 1, mid);
    }
    fillRect(buf, 6, 10, 10, 13, lo);
    triangleTop(buf, 8, 5, 3, hi);
    for (let y = 2; y <= 5; y++) line(buf, 8, 6, 8, y, mixRgb(base, [180, 220, 255], 0.35).concat(255));
    line(buf, 6, 3, 8, 1, accent);
    line(buf, 10, 3, 8, 1, accent);
  } else if (type === 'sensor') {
    fillCircle(buf, 8, 9, 4, lo);
    fillCircle(buf, 8, 9, 3, body);
    fillCircle(buf, 8, 9, 2, [10, 14, 22, 255]);
    setPx(buf, 8, 9, mixRgb(base, [150, 220, 255], 0.55).concat(255));
    fillRect(buf, 4, 5, 5, 6, hi);
    fillRect(buf, 11, 5, 12, 6, hi);
    for (let x = 1; x < 15; x += 2) if (x < 4 || x > 11) setPx(buf, x, 7, mid);
    line(buf, 2, 8, 0, 8, lo);
    line(buf, 14, 8, 15, 8, lo);
  } else {
    // 未知类型兜底
    fillRect(buf, 3, 3, 13, 13, body);
  }

  return buf;
}

function triangleTop(buf, cx, topY, halfW, rgba) {
  for (let row = 0; row < 4; row++) {
    const w = halfW - row;
    if (w < 0) break;
    fillRect(buf, cx - w, topY + row, cx + w + 1, topY + row + 1, rgba);
  }
}

function drawCircuit(base) {
  const buf = createBuffer();
  const body = [...base, 255];
  const hi = [...mixRgb(base, [255, 255, 255], 0.5), 255];
  const trace = [...mixRgb(base, [80, 220, 120], 0.35), 255];
  const dark = [...shadeRgb(base, 0.5), 255];
  fillRect(buf, 3, 4, 13, 12, dark);
  fillRect(buf, 4, 5, 12, 11, body);
  // 引脚
  for (let y = 6; y <= 10; y += 2) {
    setPx(buf, 2, y, hi);
    setPx(buf, 13, y, hi);
  }
  // 走线
  line(buf, 5, 6, 10, 6, trace);
  line(buf, 6, 8, 11, 8, trace);
  line(buf, 5, 10, 9, 10, trace);
  line(buf, 9, 6, 9, 9, trace);
  fillRect(buf, 7, 7, 9, 9, hi);
  setPx(buf, 8, 8, BLACK);
  return buf;
}

async function writePng(buf, outPath) {
  await sharp(buf, { raw: { width: SIZE, height: SIZE, channels: 4 } })
    .png()
    .toFile(outPath);
}

function writeModelJson(relTexturePath, outFile) {
  const obj = {
    parent: 'minecraft:item/generated',
    textures: { layer0: relTexturePath },
  };
  fs.mkdirSync(path.dirname(outFile), { recursive: true });
  fs.writeFileSync(outFile, JSON.stringify(obj), 'utf8');
}

function tierKey(stageKey, n) {
  return `${stageKey}_${n}`;
}

async function main() {
  let textures = 0;
  let models = 0;
  let mcmetas = 0;

  for (const stage of STAGES) {
    for (let n = 1; n <= 4; n++) {
      const tk = tierKey(stage.key, n);
      const base = stageTierColor(stage, n);

      const compDir = path.join(TEX_ITEM, stage.key, 'components');
      const cirDir = path.join(TEX_ITEM, stage.key, 'circuits');
      fs.mkdirSync(compDir, { recursive: true });
      fs.mkdirSync(cirDir, { recursive: true });

      for (const ctype of COMPONENT_TYPES) {
        const name = `${ctype}_${tk}`;
        const pngPath = path.join(compDir, `${name}.png`);
        const buf = drawComponent(ctype, base);
        await writePng(buf, pngPath);
        textures++;

        if (ctype === 'field_generator') {
          const metaPath = `${pngPath}.mcmeta`;
          fs.writeFileSync(metaPath, MCMETA_ANIMATION, 'utf8');
          mcmetas++;
        }
      }

      const cbuf = drawCircuit(base);
      const cPng = path.join(cirDir, `circuit_${tk}.png`);
      await writePng(cbuf, cPng);
      textures++;

      // 模型：跳过 abyss（已存在）
      if (stage.key !== 'abyss') {
        for (const ctype of COMPONENT_TYPES) {
          const modelName = `${ctype}_${tk}.json`;
          const texRef = `hk3gtl:item/${stage.key}/components/${ctype}_${tk}`;
          writeModelJson(texRef, path.join(MODELS_ITEM, modelName));
          models++;
        }
        writeModelJson(
          `hk3gtl:item/${stage.key}/circuits/circuit_${tk}`,
          path.join(MODELS_ITEM, `circuit_${tk}.json`),
        );
        models++;
      }
    }
  }

  console.log('gen_component_textures.mjs 完成');
  console.log(`  贴图 PNG: ${textures}`);
  console.log(`  物品模型 JSON: ${models}（已跳过 abyss 已有模型）`);
  console.log(`  field_generator .png.mcmeta: ${mcmetas}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
