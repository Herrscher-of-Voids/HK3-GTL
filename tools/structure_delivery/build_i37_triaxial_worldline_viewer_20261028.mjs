/** I37三轴世界线干涉测量台的MC材质评审页生成器。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
if (!process.argv[2]) throw new Error('缺少I37候选交付目录参数');
const output = path.resolve(process.argv[2]);
const sourcePath = path.join(root, 'tools/structure_delivery/build_i38_imaginary_rectifier_viewer_v1_20261027.mjs');
let source = await fs.readFile(sourcePath, 'utf8');
const replacements = [
  ['I38', 'I37'],
  ['i38', 'i37'],
  ['虚数能量整流中枢', '世界维系试验平台'],
  ['双极脉冲换流站', '三轴世界线干涉测量台'],
  ['阀组材质近景', '零位测量井材质近景'],
  ['阀列', '测量基线'],
  ['阀塔', '计量节点'],
  ['换流阀', '干涉测量头'],
  ['整流调节、合法结算与状态监测机柜', '三轴状态采集、参考态比对与维系记录机柜'],
  ['前端整流、合法结算与状态监测', '中轴计量、状态记录与维系工况监测'],
  ['维度传送', '维度传送'],
  ['能量态崩坏能采集结果与合同允许的回收能流', 'I35锚定结果、I36稳定场与I38供能合同允许的稳定介质'],
  ['承担整流、合法校验和幂等记账的建筑表达', '对参考态与扰动态进行世界维系试验并生成维系记录的建筑表达'],
  ['HKE或免费EU', '世界或免费EU'],
  ['整流、账户与去重结算', '维系工况、状态比对与报告输出'],
  ['供能合同、整流、账户与去重结算', 'I35锚定、I36稳定场、I38供能合同与I37维系工况'],
  ['I01-4负责能量态崩坏能采集，I38负责HKE整流和合法记账，I41负责文明负载调度，三者职责分开。', 'I35提供锚定能力，I36提供稳定场，I38按供能合同提供能量与稳定介质；I37只承担世界维系试验和维系记录，不能替代I35至I38其他机器职责。'],
  ['IWV · V12', 'WFV · V13'],
  ['IWV· V12', 'WFV · V13'],
  ['十二座分级绝缘计量节点构成双极换流测量基线，纵向基线承担锚定输入与记录采集，两条横向基线对照参考态和扰动态；居中测控室沿连续外墙集成主控与接口。', '开敞的三条正交测量基线汇入中央零位井：纵向基线承担锚定输入与记录，两条横向基线对照参考态和扰动态；主控、接口、滑台与计量框均嵌入同一承力轨床。'],
  ['接收I01-4能量态采集结果与合同允许的回收能流，对参考态与扰动态进行世界维系试验并生成维系记录的建筑表达。I01-4继续负责能量态采集，I41负责文明负载调度；本机不以外观预览代替HKE结算运行验收。', '承接I35锚定状态、I36稳定场与I38按供能合同允许的能量及稳定介质，对参考态和扰动态进行世界维系试验并形成维系报告的建筑表达。I37不替代I35至I38其他机器职责；实际工艺与维系报告仍须在游戏中验收。'],
  ['不能凭结构存在自动创造世界或免费EU；不把资料包当作能量，不自动解锁研究或文明。', '不能凭结构存在自动创造世界或免费EU；不以外观替代真实锚定、稳定、供能、维系工况或研究逻辑。'],
  ['后侧冷却与回流', '侧向计量基线'],
  ['V1 · MC材质三维评审', '白纸新构型 · MC材质三维评审'],
  ['主控接口', '主控定位'],
  ['定位主控', '定位主控'],
  ['东北', '斜上'],
  ['十六座分级绝缘阀塔构成双极换流阀列', '三条正交基线汇入中央零位井，形成开敞的世界线干涉测量台'],
  ['顶置脉冲母线连接前端变压器与后端散热机列', '纵向基线承担锚定输入与记录采集，两条横向基线对照参考态和扰动态'],
  ['控制室沿连续外墙集成主控与接口', '主控与接口嵌入正面设备梁，滑台和计量桥由连续轨床承力'],
  ['阀塔、母线和变压器仅作工程造型表达', '测量基线、试件和计量框仅作工程造型表达'],
  ['camera.position.set(500,115,95);controls.target.set(476,105,134);', 'camera.position.set(W*.78,H*.72,D*.78);controls.target.set(W/2,H*.42,D/2);'],
  ["if(data.key!=='i38'", "if(data.key!=='i37'"],
];
for (const [before, after] of replacements) source = source.replaceAll(before, after);
source = source.replaceAll(
  '十二座分级绝缘计量节点构成双极换流测量基线，顶置脉冲母线连接前端变压器与后端散热机列；居中测控室沿连续外墙集成主控与接口。',
  '开敞的三条正交测量基线汇入中央零位井：纵向基线承担锚定输入与记录，两条横向基线对照参考态和扰动态；主控、接口、滑台与计量框均嵌入同一承力轨床。');
source = source.replaceAll(
  '十二座分级绝缘计量节点构成双极换流测量基线，纵向基线承担锚定输入与记录采集，两条横向基线对照参考态和扰动态；居中测控室沿连续外墙集成主控与接口。',
  '开敞的三条正交测量基线汇入中央零位井：纵向基线承担锚定输入与记录，两条横向基线对照参考态和扰动态；主控、接口、滑台与计量框均嵌入同一承力轨床。');
source = source.replaceAll(
  '开敞T形三轴基线汇入中央零位测量井：横向对照参考态与扰动态，纵向承载锚定、介质输入和维系记录采集；高架正交计量框由同一轨床承力。',
  '开敞的三条正交测量基线汇入中央零位井：横向对照参考态与扰动态，纵向承载锚定输入和记录采集；高架计量框与滑台由同一轨床承力。');
source = source.replaceAll(
  '换流站计量节点、母线和变压器仅作工程造型表达',
  '三轴基线、零位井和计量框仅作工程造型表达');
source = source.replaceAll('三轴世界线干涉测量台V1-三维预览.png', '三轴世界线干涉测量台-三维预览.png');
source = source.replace("if(data.key!=='i37'||data.controller[0]!==Math.floor((data.size[0]-1)/2))",
  "if(data.key!=='i37'||data.controller[0]!==Math.floor((data.size[0]-1)/2))");
if (!source.includes("if(data.key!=='i37'") || !source.includes('三轴世界线干涉测量台') || source.includes('双极脉冲换流站')) {
  throw new Error('I37查看器文本或标识转换未完成');
}
const runner = path.join(path.dirname(fileURLToPath(import.meta.url)), '.i37_triaxial_viewer_runner.tmp.mjs');
await fs.writeFile(runner, source, 'utf8');
try {
  await import(pathToFileURL(runner).href + '?build=' + Date.now());
} finally {
  await fs.rm(runner, {force: true});
}
console.log(JSON.stringify({output, viewer: path.join(output, 'i37/三维评审.html'), candidate: true}));
