/**
 * 候选89：将同源逐格JSON交给既有Minecraft Builder导出NBT。
 * 变更记录 #1：新增候选专用适配；不改正式资源、不写游戏实例。
 * 禁止默认回落到正式目录；调用方必须显式传入候选文件。
 */
import fs from 'node:fs';
export default function build(api) {
  const source=process.env.HK3_REVIEW_BLUEPRINT;
  if(!source)throw new Error('缺少候选蓝图路径');
  const data=JSON.parse(fs.readFileSync(source,'utf8'));
  const structure=api.createStructure(data.size);
  for(const block of data.blocks)api.setBlock(structure,block.pos,block.state);
  return {structure,metadata:{name:data.name}};
}
