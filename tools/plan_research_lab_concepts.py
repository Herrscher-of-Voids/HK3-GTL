# -*- coding: utf-8 -*-
"""研究所概念记录，非批准结构；新增方案及参考链接，不修改生产Pattern。
变更记录#1：输出实际时间，保留原计划；仅列尺寸/轮廓候选，材料预览另行审批。
"""
from pathlib import Path
import json,datetime,html,math
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'logs/research-migration-20260928'
ROWS=[
 ('S02','高级材料研究所',[35,23,31],2,'中央精密检测腔、左侧样件制备翼、右侧数据与冷却翼、后侧双散热柱。管路连接明确端点，检修通道绕设备行走，不切断检测腔。',['advanced_integrated_ore_processor','component_assembly_line']),
 ('S03','量子研究所',[45,39,45],4,'中央观测核与两道交叉约束环、四组落地支撑，前方控制台与后方数据模块；环下设置连续检修步道，不以悬浮碎块代替设备细节。',['advanced_sps_crafting','dimensional_focus_engraving_array']),
 ('S04','虚数研究所',[55,55,49],8,'竖直锚定柱与错层约束框，左右分别布置能流调理和稳定记录模块；中轴通道到核心维护区，避免同尺寸圆环重复堆叠。',['nano_core','gravitation_shockburst']),
 ('S05','文明认知穹顶',[65,45,65],16,'中央分段穹顶与三领域档案翼，外围三组计算阵列和贯通环廊，前方中轴入口；宽阔展开，不继续机械加高，不与W09合并。',['mage_assembler','star_ultimate_material_forge_factory','qft'])]

def main():
 now=datetime.datetime.now().astimezone().isoformat()
 data={'time':now,'status':'概念尺寸候选，未审批、未生成正式结构','constraints':['主控正面水平居中，后方中轴平分左右宽度','保留白色外框，框内除主控均为接口候选位，最多两层','地板整齐统一白色，不散放MAX机壳碎块','端口数量与实际能力在预览设计时核对','完整建材需核对双底包，不使用动态方块实体作装饰'],'rows':[{'id':i,'name':n,'size_xyz':s,'slots':c,'concept':d,'references':r,'bounding_cells':math.prod(s)} for i,n,s,c,d,r in ROWS],'limits':['尚未核对全部实际材质及完整形体','正投影为真实布局深度图，并非材质预览或游戏截图','候选包围盒较小不代表手机性能已验证']}
 with (OUT/'research-labs-concept-proposal.json').open('x',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2)
 p=ROOT/'doc/HK3GTL-内测5/09_测试发布/十二天重制计划与交付清单.html';s=p.read_text(encoding='utf-8');assert 'id="research-labs-concept-proposal"' not in s
 section=f'<section class="panel" id="research-labs-concept-proposal"><h2>S02–S05轮廓与尺寸候选 · 尚未审批</h2><p>变更记录#1 · {now}。新增概念与参考链接，删除无，保留历史内容。不是已批准结构或正式预览。</p><p><a href="../../../logs/research-migration-20260928/enhanced-28-shape-projections.png">查看28项增强版真实布局正投影</a>：灰度代表深度，不是材质或游戏截图，各图独立缩放。</p>'
 for row in data['rows']:
  section+=f'<h3>{row["id"]} {row["name"]}</h3><p>候选尺寸X/Y/Z：{row["size_xyz"]}；包围盒{row["bounding_cells"]}格；并行{row["slots"]}项。</p><p>{row["concept"]}</p><p>参考：{html.escape(", ".join(row["references"]))}</p>'
 section+='<p>共同约束：'+'；'.join(data['constraints'])+'。</p><p>后续生成材质明确的结构预览再审批，不将本概念直接接入Pattern。</p></section>'
 with (OUT/'plan-before-lab-concepts.html').open('x',encoding='utf-8') as f:f.write(s)
 i=s.lower().rfind('</body>');assert i>=0;p.write_text(s[:i]+section+'\n'+s[i:],encoding='utf-8')
 assert p.read_text(encoding='utf-8').replace(section+'\n','',1)==s
 assert (p.parent/'../../../logs/research-migration-20260928/enhanced-28-shape-projections.png').resolve().is_file()
 print(json.dumps({'concepts':4,'bounding_cells':[r['bounding_cells'] for r in data['rows']],'reference_image_exists':True,'production_changed':False},ensure_ascii=False))
if __name__=='__main__':main()
