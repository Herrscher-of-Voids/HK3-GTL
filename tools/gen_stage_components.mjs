/**
 * 基于用户提供的 18 张 GT 风格参考图，重建四阶段（海渊/虚数/量子/终焉）部件贴图。
 *
 * 设计目标：
 * 1. 不再以项目现有贴图为模板，完全以外部参考图为母版
 * 2. 保留 GT 原版式金属像素结构，只改主题色，不改轮廓
 * 3. 使用低阶母版 + 高阶母版混合，生成同一阶段 1~4 档的电压层次感
 *
 * 生成范围：
 * - 9 种部件 × 4 阶段 × 4 电压 = 144 张 PNG
 * - 1 种电路板 × 4 阶段 × 4 电压 = 16 张 PNG
 */
import sharp from 'sharp';
import fs from 'fs';
import os from 'os';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');
// 修订108：批准色卡已接管，历史生成器仅保留溯源。
if (fs.existsSync(path.join(ROOT, 'src/main/resources/data/hk3gtl/catalog/voltage_palette.json'))) {
    throw new Error('Approved palette active; use tools/apply_voltage_palette_r108.py');
}
const ASSETS = path.join(ROOT, 'src', 'main', 'resources', 'assets', 'hk3gtl');
const TEX_ITEM = path.join(ASSETS, 'textures', 'item');
const USER_HOME = process.env.USERPROFILE || os.homedir();

// 允许通过环境变量覆盖 Cursor 导出的参考图目录，避免脚本和本机路径强绑定。
const REFERENCE_ROOT = process.env.HK3GTL_REFERENCE_ROOT ||
    path.join(USER_HOME, '.cursor', 'projects', 'c-Users-OWNER-Desktop-hk3gtl', 'assets');

const VOLTAGE_KEYS = {"abyss": ["hbv", "hcv", "hrv", "hdv"], "imaginary": ["qsv", "qcv", "qev", "qav"], "quantum": ["imv", "icv", "irv", "iwv"], "finality": ["wfv", "wsv", "civ", "cev"]};

const COMPONENT_TYPES = [
    'conveyor_module',
    'electric_motor',
    'electric_piston',
    'electric_pump',
    'emitter',
    'field_generator',
    'fluid_regulator',
    'robot_arm',
    'sensor',
];

const REFERENCE_FILES = {
    conveyor_module: {
        low: 'c__Users_OWNER_AppData_Roaming_Cursor_User_workspaceStorage_980cbbac315a606c5f08cbfa0d147962_images_conveyor_module_abyss_1-bc122d5c-07dd-4fa2-afd3-1816866ea4ea.png',
        high: 'c__Users_OWNER_AppData_Roaming_Cursor_User_workspaceStorage_980cbbac315a606c5f08cbfa0d147962_images_ev_conveyor_module-2b9f4326-7f16-4acc-83a3-77db230ad5d3.png',
    },
    electric_motor: {
        low: 'c__Users_OWNER_AppData_Roaming_Cursor_User_workspaceStorage_980cbbac315a606c5f08cbfa0d147962_images_electric_motor_abyss_1-2950b0d5-4b5e-489e-ba86-55ac0c00d326.png',
        high: 'c__Users_OWNER_AppData_Roaming_Cursor_User_workspaceStorage_980cbbac315a606c5f08cbfa0d147962_images_ev_electric_motor-d7bb21e5-5bc3-4c8c-a7e7-715ed5ae78da.png',
    },
    electric_piston: {
        low: 'c__Users_OWNER_AppData_Roaming_Cursor_User_workspaceStorage_980cbbac315a606c5f08cbfa0d147962_images_electric_piston_abyss_1-6344660d-f468-4efc-8bc2-2453ee0f02c8.png',
        high: 'c__Users_OWNER_AppData_Roaming_Cursor_User_workspaceStorage_980cbbac315a606c5f08cbfa0d147962_images_ev_electric_piston-ebd0d603-0985-4019-98da-c80d01789949.png',
    },
    electric_pump: {
        low: 'c__Users_OWNER_AppData_Roaming_Cursor_User_workspaceStorage_980cbbac315a606c5f08cbfa0d147962_images_electric_pump_abyss_1-70557bdd-8468-4f10-8cff-e26fe576f984.png',
        high: 'c__Users_OWNER_AppData_Roaming_Cursor_User_workspaceStorage_980cbbac315a606c5f08cbfa0d147962_images_ev_electric_pump-b721d3af-099a-4f5e-a6d2-7a090cf33767.png',
    },
    emitter: {
        low: 'c__Users_OWNER_AppData_Roaming_Cursor_User_workspaceStorage_980cbbac315a606c5f08cbfa0d147962_images_emitter_abyss_1-3dda3e03-007c-4cce-bda3-8073f285ad7a.png',
        high: 'c__Users_OWNER_AppData_Roaming_Cursor_User_workspaceStorage_980cbbac315a606c5f08cbfa0d147962_images_ev_emitter-c241c02e-0729-4156-88c8-65dd3178252b.png',
    },
    field_generator: {
        low: 'c__Users_OWNER_AppData_Roaming_Cursor_User_workspaceStorage_980cbbac315a606c5f08cbfa0d147962_images_field_generator_abyss_1-4a4e3daa-746f-4718-97d7-1b9b256f7ac2.png',
        high: 'c__Users_OWNER_AppData_Roaming_Cursor_User_workspaceStorage_980cbbac315a606c5f08cbfa0d147962_images_ev_field_generator-2e994385-515f-4ec7-aebc-d1504df4e9ea.png',
    },
    fluid_regulator: {
        low: 'c__Users_OWNER_AppData_Roaming_Cursor_User_workspaceStorage_980cbbac315a606c5f08cbfa0d147962_images_fluid_regulator_abyss_1-c6906535-3e1c-447f-8af8-e2cf3c785e42.png',
        high: 'c__Users_OWNER_AppData_Roaming_Cursor_User_workspaceStorage_980cbbac315a606c5f08cbfa0d147962_images_ev_fluid_regulator-c24ba466-fa38-4406-93f0-7740fb5e0182.png',
    },
    robot_arm: {
        low: 'c__Users_OWNER_AppData_Roaming_Cursor_User_workspaceStorage_980cbbac315a606c5f08cbfa0d147962_images_robot_arm_abyss_1-565601e3-c2ac-4b0b-b446-2f272a806c26.png',
        high: 'c__Users_OWNER_AppData_Roaming_Cursor_User_workspaceStorage_980cbbac315a606c5f08cbfa0d147962_images_ev_robot_arm-4709a8df-ed85-4570-b3d3-1641f84b633c.png',
    },
    sensor: {
        low: 'c__Users_OWNER_AppData_Roaming_Cursor_User_workspaceStorage_980cbbac315a606c5f08cbfa0d147962_images_sensor_abyss_1-23224b8d-d39c-476b-8f2f-12fb29baf5c1.png',
        high: 'c__Users_OWNER_AppData_Roaming_Cursor_User_workspaceStorage_980cbbac315a606c5f08cbfa0d147962_images_ev_sensor-41d1ff10-4cf2-4155-bbaf-78a6213ba3d0.png',
    },
};

const CIRCUIT_REFERENCE_FILE =
    'c__Users_OWNER_AppData_Roaming_Cursor_User_workspaceStorage_980cbbac315a606c5f08cbfa0d147962_images________2026-04-15_080756-41551bc9-8238-4f57-9ca2-b21268f22a07.png';

const TIER_MIX = [0.0, 0.35, 0.7, 1.0];

const STAGE_STYLES = {
    abyss: {
        tiers: [
            {
                accent: [[8, 18, 42], [18, 54, 110], [38, 104, 188], [116, 188, 255]],
                neutralTint: [74, 110, 168],
                neutralStrength: 0.10,
                accentBoost: 0.84,
            },
            {
                accent: [[6, 28, 40], [16, 78, 112], [34, 150, 196], [118, 228, 255]],
                neutralTint: [78, 132, 172],
                neutralStrength: 0.14,
                accentBoost: 0.92,
            },
            {
                accent: [[8, 24, 34], [20, 92, 120], [42, 176, 186], [160, 250, 236]],
                neutralTint: [86, 144, 150],
                neutralStrength: 0.17,
                accentBoost: 1.00,
            },
            {
                accent: [[14, 28, 38], [46, 110, 130], [110, 196, 220], [226, 250, 255]],
                neutralTint: [138, 170, 188],
                neutralStrength: 0.20,
                accentBoost: 1.06,
            },
        ],
    },
    imaginary: {
        tiers: [
            {
                accent: [[16, 12, 8], [82, 58, 18], [150, 108, 34], [230, 186, 92]],
                neutralTint: [142, 110, 66],
                neutralStrength: 0.14,
                accentBoost: 0.94,
            },
            {
                accent: [[18, 14, 6], [98, 70, 20], [182, 132, 38], [255, 214, 110]],
                neutralTint: [172, 136, 74],
                neutralStrength: 0.18,
                accentBoost: 1.00,
            },
            {
                accent: [[20, 16, 10], [112, 84, 28], [204, 162, 62], [255, 232, 156]],
                neutralTint: [196, 164, 106],
                neutralStrength: 0.22,
                accentBoost: 1.06,
            },
            {
                accent: [[10, 10, 10], [72, 60, 28], [156, 126, 58], [255, 242, 184]],
                neutralTint: [182, 160, 118],
                neutralStrength: 0.25,
                accentBoost: 1.10,
            },
        ],
    },
    quantum: {
        tiers: [
            {
                accent: [[28, 20, 44], [88, 62, 132], [160, 132, 218], [232, 222, 255]],
                neutralTint: [184, 172, 224],
                neutralStrength: 0.14,
                accentBoost: 0.94,
            },
            {
                accent: [[36, 22, 54], [108, 74, 162], [186, 156, 234], [248, 240, 255]],
                neutralTint: [208, 194, 236],
                neutralStrength: 0.18,
                accentBoost: 1.00,
            },
            {
                accent: [[40, 26, 60], [126, 86, 176], [206, 172, 242], [255, 246, 255]],
                neutralTint: [220, 204, 242],
                neutralStrength: 0.21,
                accentBoost: 1.04,
            },
            {
                accent: [[30, 24, 48], [142, 108, 184], [222, 196, 248], [255, 255, 255]],
                neutralTint: [234, 226, 248],
                neutralStrength: 0.24,
                accentBoost: 1.08,
            },
        ],
    },
    finality: {
        tiers: [
            {
                accent: [[8, 8, 8], [74, 58, 24], [152, 122, 50], [244, 228, 196]],
                neutralTint: [188, 178, 156],
                neutralStrength: 0.16,
                accentBoost: 0.96,
            },
            {
                accent: [[12, 10, 8], [92, 72, 28], [182, 146, 58], [255, 238, 214]],
                neutralTint: [210, 198, 176],
                neutralStrength: 0.20,
                accentBoost: 1.02,
            },
            {
                accent: [[14, 12, 10], [108, 84, 34], [206, 170, 74], [255, 246, 230]],
                neutralTint: [226, 214, 192],
                neutralStrength: 0.23,
                accentBoost: 1.06,
            },
            {
                accent: [[6, 6, 6], [96, 82, 42], [220, 190, 96], [255, 255, 244]],
                neutralTint: [238, 232, 220],
                neutralStrength: 0.28,
                accentBoost: 1.12,
            },
        ],
    },
};

function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
}

function lerp(a, b, t) {
    return Math.round(a + (b - a) * t);
}

function lerpColor(c1, c2, t) {
    return [lerp(c1[0], c2[0], t), lerp(c1[1], c2[1], t), lerp(c1[2], c2[2], t)];
}

function mixColors(rgbA, rgbB, t) {
    return [
        lerp(rgbA[0], rgbB[0], t),
        lerp(rgbA[1], rgbB[1], t),
        lerp(rgbA[2], rgbB[2], t),
    ];
}

function luminance(r, g, b) {
    return Math.round(0.299 * r + 0.587 * g + 0.114 * b);
}

function saturation(r, g, b) {
    return Math.max(r, g, b) - Math.min(r, g, b);
}

function mapLuminanceToGradient(lum, gradient) {
    const t = lum / 255;
    const n = gradient.length - 1;
    const idx = t * n;
    const lo = Math.floor(idx);
    const hi = Math.min(lo + 1, n);
    return lerpColor(gradient[lo], gradient[hi], idx - lo);
}

async function readRawPixels(filePath) {
    const { data, info } = await sharp(filePath).raw().ensureAlpha().toBuffer({ resolveWithObject: true });
    return { data, width: info.width, height: info.height, channels: info.channels };
}

async function loadReferencePair(componentType) {
    const config = REFERENCE_FILES[componentType];
    if (!config) {
        throw new Error(`未配置参考图: ${componentType}`);
    }

    const lowPath = path.join(REFERENCE_ROOT, config.low);
    const highPath = path.join(REFERENCE_ROOT, config.high);
    if (!fs.existsSync(lowPath)) {
        throw new Error(`低阶参考图不存在: ${lowPath}`);
    }
    if (!fs.existsSync(highPath)) {
        throw new Error(`高阶参考图不存在: ${highPath}`);
    }

    const low = await readRawPixels(lowPath);
    let high = await readRawPixels(highPath);
    if (low.width !== high.width || low.height !== high.height) {
        const { data, info } = await sharp(highPath)
            .resize(low.width, low.height, { kernel: sharp.kernel.nearest })
            .raw()
            .ensureAlpha()
            .toBuffer({ resolveWithObject: true });
        high = { data, width: info.width, height: info.height, channels: info.channels };
    }
    return { low, high };
}

function blendSourcePixels(low, high, mix) {
    const dst = Buffer.alloc(low.data.length);
    const total = low.width * low.height;
    const ch = low.channels;
    for (let i = 0; i < total; i++) {
        const off = i * ch;
        const lowA = ch >= 4 ? low.data[off + 3] : 255;
        const highA = ch >= 4 ? high.data[off + 3] : 255;
        const alpha = lerp(lowA, highA, mix);

        if (alpha === 0) {
            dst[off] = 0;
            dst[off + 1] = 0;
            dst[off + 2] = 0;
            if (ch >= 4) dst[off + 3] = 0;
            continue;
        }

        dst[off] = lerp(low.data[off], high.data[off], mix);
        dst[off + 1] = lerp(low.data[off + 1], high.data[off + 1], mix);
        dst[off + 2] = lerp(low.data[off + 2], high.data[off + 2], mix);
        if (ch >= 4) dst[off + 3] = alpha;
    }
    return { data: dst, width: low.width, height: low.height, channels: low.channels };
}

function removeNearWhiteBackground(src) {
    const dst = Buffer.from(src.data);
    const total = src.width * src.height;
    const ch = src.channels;

    for (let i = 0; i < total; i++) {
        const off = i * ch;
        const r = dst[off];
        const g = dst[off + 1];
        const b = dst[off + 2];
        const a = ch >= 4 ? dst[off + 3] : 255;

        if (a === 0) {
            continue;
        }

        // 模板截图背景是纯白/近白，直接转透明，同时保留板边缘的灰色抗锯齿像素。
        if (r >= 248 && g >= 248 && b >= 248) {
            dst[off] = 0;
            dst[off + 1] = 0;
            dst[off + 2] = 0;
            if (ch >= 4) {
                dst[off + 3] = 0;
            }
        }
    }

    return { data: dst, width: src.width, height: src.height, channels: src.channels };
}

function recolorPixel(r, g, b, tierStyle) {
    const lum = luminance(r, g, b);
    const sat = saturation(r, g, b);

    // 近灰阶像素保留金属关系，只做轻度金属染色。
    if (sat < 26) {
        const metalBase = mixColors([r, g, b], tierStyle.neutralTint, tierStyle.neutralStrength);

        // 亮部稍微提亮，保持 GT 金属高光。
        if (lum > 210) {
            return mixColors(metalBase, [255, 255, 255], 0.28 + tierStyle.neutralStrength * 0.6);
        }
        // 深色边线压回黑色，避免轮廓发灰。
        if (lum < 42) {
            return mixColors(metalBase, [8, 8, 8], 0.35);
        }
        return metalBase;
    }

    // 彩色区域才按阶段主题色重映射，最大限度保留原版零件材质感。
    const mapped = mapLuminanceToGradient(clamp(lum * tierStyle.accentBoost, 0, 255), tierStyle.accent);
    const strength = clamp(0.78 + sat / 255 * 0.24 + tierStyle.neutralStrength * 0.25, 0.78, 1);
    return mixColors([r, g, b], mapped, strength);
}

function recolorPixels(src, tierStyle) {
    const dst = Buffer.alloc(src.data.length);
    const total = src.width * src.height;
    const ch = src.channels;
    for (let i = 0; i < total; i++) {
        const off = i * ch;
        const a = ch >= 4 ? src.data[off + 3] : 255;
        if (a === 0) {
            dst[off] = 0;
            dst[off + 1] = 0;
            dst[off + 2] = 0;
            if (ch >= 4) dst[off + 3] = 0;
            continue;
        }

        const [nr, ng, nb] = recolorPixel(
            src.data[off],
            src.data[off + 1],
            src.data[off + 2],
            tierStyle,
        );
        dst[off] = nr;
        dst[off + 1] = ng;
        dst[off + 2] = nb;
        if (ch >= 4) dst[off + 3] = a;
    }
    return dst;
}

async function writePng(rawImage, outputPath, tierStyle) {
    const dir = path.dirname(outputPath);
    fs.mkdirSync(dir, { recursive: true });

    const recolored = recolorPixels(rawImage, tierStyle);
    await sharp(recolored, {
        raw: {
            width: rawImage.width,
            height: rawImage.height,
            channels: rawImage.channels,
        },
    }).png({ compressionLevel: 6 }).toFile(outputPath);
}

function writeFieldGeneratorMcmeta(outputPath) {
    fs.writeFileSync(outputPath + '.mcmeta', JSON.stringify({ animation: { frametime: 4 } }));
}

async function loadCircuitReference() {
    const circuitPath = path.join(REFERENCE_ROOT, CIRCUIT_REFERENCE_FILE);
    if (!fs.existsSync(circuitPath)) {
        throw new Error(`电路板参考图不存在: ${circuitPath}`);
    }
    const circuit = await readRawPixels(circuitPath);
    return removeNearWhiteBackground(circuit);
}

async function main() {
    let count = 0;
    console.log('=== 基于参考图重建四阶段部件与电路贴图 ===');
    console.log(`参考图目录: ${REFERENCE_ROOT}\n`);

    const referenceCache = new Map();
    for (const componentType of COMPONENT_TYPES) {
        referenceCache.set(componentType, await loadReferencePair(componentType));
    }
    const circuitReference = await loadCircuitReference();

    for (const [stageName, stageStyle] of Object.entries(STAGE_STYLES)) {
        const stageDir = path.join(TEX_ITEM, stageName, 'components');
        const circuitDir = path.join(TEX_ITEM, stageName, 'circuits');
        fs.mkdirSync(stageDir, { recursive: true });
        fs.mkdirSync(circuitDir, { recursive: true });

        for (let tier = 1; tier <= 4; tier++) {
            const mix = TIER_MIX[tier - 1];
            const tierStyle = stageStyle.tiers[tier - 1];
            for (const componentType of COMPONENT_TYPES) {
                const refs = referenceCache.get(componentType);
                const blended = blendSourcePixels(refs.low, refs.high, mix);
                const outputFile = `${componentType}_${VOLTAGE_KEYS[stageName][tier-1]}.png`;
                const outputPath = path.join(stageDir, outputFile);
                await writePng(blended, outputPath, tierStyle);

                if (componentType === 'field_generator') {
                    writeFieldGeneratorMcmeta(outputPath);
                }
                count++;
            }

            const circuitOutputFile = `circuit_${VOLTAGE_KEYS[stageName][tier-1]}.png`;
            const circuitOutputPath = path.join(circuitDir, circuitOutputFile);
            await writePng(circuitReference, circuitOutputPath, tierStyle);
            count++;
        }
        console.log(`  ✓ ${stageName} 阶段完成`);
    }

    console.log(`\n共生成 ${count} 张贴图。`);
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});

// 变更记录 #107 · 2026-09-30 02:20:26 · 修订107：同步正式电压键及检查，旧历史保留。
