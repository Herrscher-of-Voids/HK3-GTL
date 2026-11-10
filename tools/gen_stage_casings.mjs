/**
 * 为虚数/量子/终焉三阶段生成机壳贴图 + blockstate + model + mcmeta。
 * 以海渊机壳为模板，按阶段色彩方案重新映射亮度。
 */
import sharp from 'sharp';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');
const ASSETS = path.join(ROOT, 'src', 'main', 'resources', 'assets', 'hk3gtl');
const TEX_DIR = path.join(ASSETS, 'textures', 'block', 'casings');
const BS_DIR = path.join(ASSETS, 'blockstates');
const MODEL_DIR = path.join(ASSETS, 'models', 'block', 'casing');

fs.mkdirSync(TEX_DIR, { recursive: true });
fs.mkdirSync(BS_DIR, { recursive: true });
fs.mkdirSync(MODEL_DIR, { recursive: true });

function lerp(a, b, t) { return Math.round(a + (b - a) * t); }
function lerpColor(c1, c2, t) { return [lerp(c1[0], c2[0], t), lerp(c1[1], c2[1], t), lerp(c1[2], c2[2], t)]; }

function mapLuminanceToGradient(lum, gradient) {
    const t = lum / 255;
    const n = gradient.length - 1;
    const idx = t * n;
    const lo = Math.floor(idx);
    const hi = Math.min(lo + 1, n);
    const frac = idx - lo;
    return lerpColor(gradient[lo], gradient[hi], frac);
}

async function readRawPixels(filePath) {
    const { data, info } = await sharp(filePath).raw().toBuffer({ resolveWithObject: true });
    return { data, width: info.width, height: info.height, channels: info.channels };
}

function recolorPixels(src, gradient) {
    const dst = Buffer.alloc(src.data.length);
    const ch = src.channels;
    const total = src.width * src.height;
    for (let i = 0; i < total; i++) {
        const off = i * ch;
        const r = src.data[off], g = src.data[off + 1], b = src.data[off + 2];
        const a = ch === 4 ? src.data[off + 3] : 255;
        const lum = Math.round(0.299 * r + 0.587 * g + 0.114 * b);
        const [nr, ng, nb] = mapLuminanceToGradient(lum, gradient);
        dst[off] = nr; dst[off + 1] = ng; dst[off + 2] = nb;
        if (ch === 4) dst[off + 3] = a;
    }
    return dst;
}

async function recolorAndSave(templatePath, outputName, gradient) {
    const src = await readRawPixels(templatePath);
    const dst = recolorPixels(src, gradient);
    await sharp(dst, { raw: { width: src.width, height: src.height, channels: src.channels } })
        .png({ compressionLevel: 6 }).toFile(path.join(TEX_DIR, outputName));
}

function writeMcmeta(name) {
    const mcmeta = { ldlib: { connection: `hk3gtl:block/casings/${name}_ctm` } };
    fs.writeFileSync(path.join(TEX_DIR, `${name}.png.mcmeta`), JSON.stringify(mcmeta, null, 2));
}

function writeBlockstate(name) {
    const bs = { variants: { "": { model: `hk3gtl:block/casing/${name}` } } };
    fs.writeFileSync(path.join(BS_DIR, `${name}.json`), JSON.stringify(bs, null, 2));
}

function writeModel(name) {
    const model = { parent: "minecraft:block/cube_all", textures: { all: `hk3gtl:block/casings/${name}` } };
    fs.writeFileSync(path.join(MODEL_DIR, `${name}.json`), JSON.stringify(model, null, 2));
}

// 海渊模板：mechanical → 构造类, research → 科研类, energy → 能源类
const TEMPLATES = {
    construct: path.join(TEX_DIR, 'casing_abyss_mechanical.png'),
    construct_ctm: path.join(TEX_DIR, 'casing_abyss_mechanical_ctm.png'),
    research: path.join(TEX_DIR, 'casing_abyss_research.png'),
    research_ctm: path.join(TEX_DIR, 'casing_abyss_research_ctm.png'),
    energy: path.join(TEX_DIR, 'casing_abyss_energy.png'),
    energy_ctm: path.join(TEX_DIR, 'casing_abyss_energy_ctm.png'),
};

// 虚数：金色 + 黑色
const IMAGINARY_GRADIENTS = {
    tree:    [[12, 10, 5], [50, 42, 15], [140, 115, 30], [200, 168, 45], [255, 215, 0]],
    lattice: [[15, 12, 8], [55, 48, 20], [130, 108, 35], [190, 160, 50], [245, 210, 10]],
    core:    [[10, 8, 3],  [45, 38, 12], [150, 125, 28], [210, 178, 40], [255, 225, 20]],
    anchor:  [[18, 14, 6], [60, 50, 18], [135, 112, 32], [195, 162, 48], [250, 208, 5]],
    weave:   [[14, 11, 4], [48, 40, 14], [145, 120, 26], [205, 172, 42], [255, 220, 15]],
};

// 量子：浅紫色 + 白色
const QUANTUM_GRADIENTS = {
    sea:       [[30, 22, 50], [80, 60, 120], [140, 110, 185], [190, 170, 230], [240, 235, 255]],
    bubble:    [[25, 18, 45], [75, 55, 115], [135, 105, 180], [185, 165, 225], [235, 230, 250]],
    flux:      [[35, 25, 55], [85, 65, 125], [145, 115, 190], [195, 175, 235], [245, 240, 255]],
    entangle:  [[28, 20, 48], [78, 58, 118], [138, 108, 183], [188, 168, 228], [238, 233, 253]],
    shipboard: [[32, 24, 52], [82, 62, 122], [142, 112, 188], [192, 172, 232], [242, 238, 255]],
};

// 终焉（空之律者）：金色 + 白色 + 黑色
const FINALITY_GRADIENTS = {
    void:     [[5, 4, 2],   [30, 25, 10], [120, 100, 35], [210, 195, 120], [255, 248, 230]],
    sanctum:  [[8, 6, 3],   [35, 30, 15], [130, 110, 40], [220, 205, 130], [255, 250, 240]],
    dominion: [[3, 2, 1],   [25, 20, 8],  [110, 92, 30],  [200, 180, 100], [255, 240, 200]],
    hyperion: [[6, 5, 2],   [32, 28, 12], [125, 105, 38], [215, 200, 125], [255, 245, 235]],
    wonder:   [[10, 8, 4],  [40, 34, 18], [135, 115, 42], [225, 210, 135], [255, 252, 245]],
};

// 机壳定义：[name, templateType, gradient]
const CASINGS = [
    // 虚数
    ['casing_imaginary_tree',    'construct', IMAGINARY_GRADIENTS.tree],
    ['casing_imaginary_lattice', 'research',  IMAGINARY_GRADIENTS.lattice],
    ['casing_imaginary_core',    'energy',    IMAGINARY_GRADIENTS.core],
    ['casing_imaginary_anchor',  'construct', IMAGINARY_GRADIENTS.anchor],
    ['casing_imaginary_weave',   'energy',    IMAGINARY_GRADIENTS.weave],
    // 量子
    ['casing_quantum_sea',       'construct', QUANTUM_GRADIENTS.sea],
    ['casing_quantum_bubble',    'research',  QUANTUM_GRADIENTS.bubble],
    ['casing_quantum_flux',      'energy',    QUANTUM_GRADIENTS.flux],
    ['casing_quantum_entangle',  'construct', QUANTUM_GRADIENTS.entangle],
    ['casing_quantum_shipboard', 'energy',    QUANTUM_GRADIENTS.shipboard],
    // 终焉
    ['casing_finality_void',     'construct', FINALITY_GRADIENTS.void],
    ['casing_finality_sanctum',  'research',  FINALITY_GRADIENTS.sanctum],
    ['casing_finality_dominion', 'energy',    FINALITY_GRADIENTS.dominion],
    ['casing_finality_hyperion', 'construct', FINALITY_GRADIENTS.hyperion],
    ['casing_finality_wonder',   'research',  FINALITY_GRADIENTS.wonder],
];

async function main() {
    console.log('=== 生成虚数/量子/终焉阶段机壳贴图 ===\n');

    for (const [name, tmplType, gradient] of CASINGS) {
        const mainTmpl = TEMPLATES[tmplType];
        const ctmTmpl = TEMPLATES[tmplType + '_ctm'];

        await recolorAndSave(mainTmpl, `${name}.png`, gradient);
        await recolorAndSave(ctmTmpl, `${name}_ctm.png`, gradient);
        writeMcmeta(name);
        writeBlockstate(name);
        writeModel(name);

        console.log(`  ✓ ${name}`);
    }

    console.log(`\n共生成 ${CASINGS.length} 套机壳资源（贴图+CTM+mcmeta+blockstate+model）。`);
}

main().catch(console.error);
