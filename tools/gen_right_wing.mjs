/**
 * 右翼贴图 = 左翼水平翻转（文件级镜像，避免运行时 scale(-1,1,1) 导致背面剔除异常）。
 * 输出到 textures/entity 与 textures/item/wing，供 BakedModel 与资源引用一致。
 */
import sharp from 'sharp';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ASSET = path.join(__dirname, '..', 'src', 'main', 'resources', 'assets', 'hk3gtl', 'textures');
const ENTITY = path.join(ASSET, 'entity');
const ITEM_WING = path.join(ASSET, 'item', 'wing');

const entityPairs = [
    ['sirin_wing_left_body.png', 'sirin_wing_right_body.png'],
    ['sirin_wing_left_secondary.png', 'sirin_wing_right_secondary.png'],
    ['sirin_wing_core.png', 'sirin_wing_right_core.png'],
];

const itemPairs = [
    ['sirin_left_body.png', 'sirin_right_body.png'],
    ['sirin_left_secondary.png', 'sirin_right_secondary.png'],
    ['sirin_left_core.png', 'sirin_right_core.png'],
];

async function flopTo(srcDir, pairs) {
    for (const [src, dst] of pairs) {
        const srcPath = path.join(srcDir, src);
        const dstPath = path.join(srcDir, dst);
        await sharp(srcPath).flop().png({ compressionLevel: 6 }).toFile(dstPath);
        console.log(`${path.relative(ASSET, srcPath)} → ${path.relative(ASSET, dstPath)}`);
    }
}

await flopTo(ENTITY, entityPairs);
await flopTo(ITEM_WING, itemPairs);
console.log('右翼贴图（entity + item/wing）水平翻转完成。');
