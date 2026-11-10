import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const output = path.resolve(process.argv[2] ?? '');
if (!process.argv[2]) throw new Error('缺少I37交付根目录参数');
const view = path.join(output, 'i37');
let builder = await fs.readFile(path.join(root, 'tools/structure_delivery/build_i38_imaginary_rectifier_viewer_v1_20261027.mjs'), 'utf8');

function replaceOne(from, to) {
  const at = builder.indexOf(from);
  if (at < 0 || builder.indexOf(from, at + from.length) >= 0) throw new Error(`查看器适配锚点数量不符: ${from}`);
  builder = builder.slice(0, at) + to + builder.slice(at + from.length);
}

replaceOne("const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');", `const root=${JSON.stringify(root)};`);
builder = builder.replaceAll("'i38'", "'i37'").replaceAll('i38', 'i37').replaceAll('I38', 'I37');
builder = builder.replaceAll('IWV', 'WFV').replaceAll('V12', 'V13').replaceAll('tier26', 'tier27')
  .replaceAll('虚数能量整流中枢', '世界维系试验平台').replaceAll('双极脉冲换流站', '双腔差分场试验场')
  .replaceAll('阀组材质近景', '双腔机壳材质近景').replaceAll('阀组', '环腔').replaceAll('阀塔', '测量腔')
  .replaceAll('阀列', '双腔').replaceAll('冷却与回流', '环形检修廊').replaceAll('换流站', '试验场');
builder = builder.replaceAll(' V1 ·', ' ·');
builder = builder.replace(/<div class="candidate-note">[\s\S]*?<\/div>/,
  '<div class="candidate-note">本轮是全新建筑候选，尚未批准、尚未接入实例。两座同构环腔分别作为稳定参考态与局部扰动态；中轴差分计量颈部、三轴测量框和闭合冠梁组成连通承力体系。</div>');
builder = builder.replace(
  '接收I01-4能量态采集结果与合同允许的回收能流，承担整流、合法校验和幂等记账的建筑表达。I01-4继续负责能量态采集，I41负责文明负载调度；本机不以外观预览代替HKE结算运行验收。',
  '以I35锚定能力、I36稳定场和I37供能/稳定介质合同作为试验前提，比较稳定参考态与局部扰动态，输出维系记录、试验样件和失败分析。研究与运行输入仍以正式文档为准，本页不代表配方、传送、免费能源或玩家世界操作已经实现。');
builder = builder.replace('不能凭结构存在自动创造HKE或免费EU；不把资料包当作能量，不自动解锁研究或文明。正式供能合同、整流、账户与去重结算均须另行核验。',
  '本设计仅表达建筑布局；研究门槛、配方、维系场与供能行为须由正式规则和游戏验收确认。结构摆放不会自动制造世界、稳定场、能源或传送能力。');
builder = builder.replace('换流站测量腔、母线和变压器仅作工程造型表达', '环形承力壳、计量框与冠梁仅作建筑表达');
builder = builder.replace('I35锚定能力、I36稳定场和I37供能/稳定介质合同', 'I35锚定能力、I36稳定场和I38供能/稳定介质合同');
builder = builder.replace("camera.position.set(500,115,95);controls.target.set(476,105,134);", "camera.position.set(114,140,112);controls.target.set(142,136,160);");
builder = builder.replace('i37-surface-runs-v1', 'i37-dual-field-runs-v1');

if (!builder.includes('稳定参考态与局部扰动态') || !builder.includes("data.key!=='i37'") || builder.includes('阀塔'))
  throw new Error('I37查看器仍包含错误机器文案或编号');
await import('data:text/javascript;base64,' + Buffer.from(builder).toString('base64'));
