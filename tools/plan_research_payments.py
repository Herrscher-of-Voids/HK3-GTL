"""研究讨论用费用候选：复用已核对的物品来源，不写生产资源。
变更记录#1：实际执行时间写入输出；新增10项具体费用与迁移风险，删除无。
材料取得仅核对本项目源码，不宣称整包动态配方或游戏验收通过。
"""
from pathlib import Path
import datetime, json, html, re
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'logs/research-migration-20260928'
PLAN=ROOT/'doc/HK3GTL-内测5/09_测试发布/十二天重制计划与交付清单.html'

# 点数和时间是新增平衡候选；材料支付与实验证据独立，研究点路线仍要求相同实验。
ROWS=[
 ('HED',20,600,[('honkai_analysis_sample',2)],'industrial_honkai_sample_canning','已采液态崩坏能灌瓶；不要求研究完成。'),
 ('HSA',30,900,[('analyzed_honkai_sample',2)],'industrial_initial_spectrum','I02初始光谱产物；提交费用不代替本队实验。'),
 ('LSE',60,1200,[('separation_filter',4),('honkai_reference_sample',2)],'industrial_separation_filter,industrial_honkai_reference_sample','前级GT组装机；滤芯不依赖LSE解锁后的分离产物。'),
 ('LES',100,1800,[('honkai_crystal_seed',8),('directional_crystallization_matrix',2)],'industrial_honkai_crystal_seed,industrial_directional_crystallization_matrix','晶种来自LSE后可得粒子；不以稳定液作为材料费用前提。'),
 ('BCE',120,1800,[('honkai_adapted_circuit_substrate',2),('analyzed_honkai_sample',4)],'industrial_honkai_adapted_circuit_substrate,industrial_initial_spectrum','基板只要求已完成LES，不索要BCE之后的电子部件。'),
 ('DMT',160,2400,[('honkai_reference_sample',4),('analyzed_honkai_sample',4)],'industrial_honkai_reference_sample,industrial_initial_spectrum','不消费唯一校准报告或探测器；报告保留给正式探测器升级。'),
 ('SMR',160,2400,[('separation_filter',4),('separation_residue',8)],'industrial_separation_filter,industrial_liquid_fractionation','滤芯有独立制造来源，残渣来自前序分馏；不索要SMR改良产物。'),
 ('HFB',200,3000,[('fuel_matrix',4),('honkai_reference_sample',4)],'industrial_fuel_matrix,industrial_honkai_reference_sample','前级GT已能制造燃料基质，不消耗整台设备或探测器。'),
 ('FRP',240,3600,[('honkai_fuel_rod_casing',4),('fuel_encapsulation_part',8)],'industrial_fuel_rod_casing,industrial_fuel_encapsulation_part','两者仅要求HFB；不把可发电燃料棒当成封装研究费用。'),
 ('CFR',900,7200,[('fuel_matrix',16),('honkai_adapted_circuit_substrate',8)],'industrial_fuel_matrix,industrial_honkai_adapted_circuit_substrate','保留固态采集等研究前置；材料来自液态前序，不要求浓缩燃料棒。')
]

def main():
 now=datetime.datetime.now().astimezone().isoformat()
 catalog={x['id']:x for x in json.loads((ROOT/'src/main/resources/data/hk3gtl/research/research_catalog.json').read_text(encoding='utf-8'))['topics']}
 registered=(ROOT/'src/main/java/com/sirin/hk3gtl/common/registration/Hk3IndustrialContent.java').read_text(encoding='utf-8')
 sources=list((ROOT/'src/main/java/com/sirin/hk3gtl/common/recipe').rglob('*.java'))
 text={p:p.read_text(encoding='utf-8') for p in sources}
 rows=[]
 for short,points,ticks,materials,recipes,boundary in ROWS:
  key='RN-'+short; assert key in catalog
  for item,count in materials:assert re.search(r'item\("'+item+r'",',registered) and count>0
  refs=[]
  for recipe in recipes.split(','):
   found=[{'recipe':recipe,'path':str(p.relative_to(ROOT)).replace('\\','/'),'line':s[:s.index('"'+recipe+'"')].count('\n')+1} for p,s in text.items() if '"'+recipe+'"' in s]
   assert found,recipe
   refs.extend(found)
  rows.append({'id':key,'title':catalog[key]['title'],'points':points,'ticks':ticks,'materials':[{'item':'hk3gtl:'+i,'count':n} for i,n in materials],'source_references':refs,'boundary':boundary,'status':'候选，未修改生产费用；整包动态来源未验收'})
 findings=[
  {'title':'旧魂钢路线仍注册','source':'src/main/java/com/sirin/hk3gtl/common/recipe/Hk3RecipeAdderImpl.java:147','detail':'SouliumRecipes.addSouliumSmeltingRecipes仍调用，bootstrap_soulium_ingot可从旧前驱体直接产出魂钢锭。新八段路线接通时必须迁移旧生产门槛与产物，不能仅改显示名。保留材料与有用加工代码，不在讨论阶段删除。'},
  {'title':'后续电子平台仍引用旧研究','source':'src/main/java/com/sirin/hk3gtl/common/recipe/Hk3ElectronicRecipes.java:63','detail':'平台门槛仍有R-AB-022、R-IM-004、R-QT-011；必须按蚀刻、封装、高阶工况用途迁移，不能把旧ID批量映射为同一新课题。'},
  {'title':'付款当前仅支持标签','source':'src/main/java/com/sirin/hk3gtl/common/research/Hk3ResearchPlans.java','detail':'Material仅有tag/count。拟扩展明确物品匹配，并在需要时核对物品数据；扣费仍保留实际ItemStack凭据，全额退款按原物品而非按标签重造。'},
  {'title':'其余90项费用不能凭注册存在定稿','source':'src/main/java/com/sirin/hk3gtl/common/registration/Hk3IndustrialContent.java','detail':'纳米群、世界泡容器、复合材料、舰体件已有注册不等于新研究前来源闭合。余下课题费用待具体工序接线核对；不把这10项候选报告为100项全部定稿。'}]
 out={'time':now,'status':'首批10项材料支付候选，非实现','rows':rows,'findings':findings,'limits':['现有HK3注册与源码配方引用已核对','未完成两个底包的运行时配方、全部材料成本及电压可达性验证','点数与材料是两种不同资源路径，未声称经济价值完全等价','研究电压沿目录现有值，此处只拟定点数、基础耗时和材料费用']}
 target=OUT/'payment-proposal-first10.json';assert not target.exists()
 original=PLAN.read_text(encoding='utf-8');assert 'id="research-payments-first10"' not in original
 esc=lambda x:html.escape(str(x),quote=True)
 chunks=[f'<section class="panel" id="research-payments-first10"><h2>首批10课题材料支付候选与旧工艺迁移风险</h2><p>变更记录#1 · {esc(now)}。新增讨论方案；删除无；保留历史内容。不修改生产费用、游戏代码或实例。</p><p>这些物品已核对本项目注册与配方源码，但未验证整包最终配方。实验证据、研究点付款或材料付款三者不能混用。余下90项费用尚未定稿。</p>']
 for row in rows:
  chunks.append(f'<h3>{esc(row["id"])} · {esc(row["title"])}</h3><p>候选：{row["points"]}研究点，或 '+ '、'.join(f'{esc(m["item"])} × {m["count"]}' for m in row['materials'])+f'。基础耗时{row["ticks"]/20:g}秒。{esc(row["boundary"])}</p><p>来源：'+ '；'.join(esc(r['recipe'])+' — '+esc(r['path'])+':'+str(r['line']) for r in row['source_references'])+'</p>')
 chunks.append('<h3>迁移时必须处理的实际代码问题</h3>')
 for f in findings:chunks.append(f'<p><b>{esc(f["title"])}：</b>{esc(f["detail"])} <code>{esc(f["source"])}</code></p>')
 chunks.append('</section>');section='\n'.join(chunks)
 marker=original.lower().rfind('</body>');assert marker>=0
 with (OUT/'plan-before-payment-first10.html').open('x',encoding='utf-8') as f:f.write(original)
 target.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
 revised=original[:marker]+section+'\n'+original[marker:]
 PLAN.write_text(revised,encoding='utf-8');assert PLAN.read_text(encoding='utf-8').replace(section+'\n','',1)==original
 print(json.dumps({'count':len(rows),'registered_items_checked':True,'recipe_literals_found':True,'previous_plan_preserved':True,'game_modified':False},ensure_ascii=False))
if __name__=='__main__':main()

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
