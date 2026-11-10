"""补齐研究讨论中的90项费用候选，保留首批10项和旧费用。
变更记录#1：输出记录实际执行时间；新增全目录候选、材料前置检查与风险，删除无。
物品注册、字符串引用、拟定解锁是不同证据，不把候选门槛当现役配方已实现。
"""
from pathlib import Path
import datetime, json, re, html, collections
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'logs/research-migration-20260928'
PLAN=ROOT/'doc/HK3GTL-内测5/09_测试发布/十二天重制计划与交付清单.html'
# 名称前#表示材料标签，其余为已注册HK3物品；时间单位分钟，均为新增候选。
DATA='''
SRE|300|4|honkai_fuel_rod_casing:8,fuel_encapsulation_part:16,#plates/tungsten_steel:16
HLC|320|4|separation_filter:8,#plates/silver:16,#plates/tungsten_steel:8
SFR|360|5|separation_filter:8,#plates/polytetrafluoroethylene:16,#dusts/carbon:32
RAT|300|4|directional_crystallization_matrix:4,honkai_reference_sample:8,#foils/platinum:16
SSP|400|5|honkai_reference_sample:8,separation_filter:8,#dusts/tungsten:16
NBS|450|5|honkai_reference_sample:8,#dusts/platinum:16,#dusts/silicon:32
NRA|500|6|nano_building_unit:16,honkai_adapted_circuit_substrate:4,#foils/polybenzimidazole:16
NSP|600|7|unprogrammed_nanobot:8,honkai_adapted_circuit_substrate:8,honkai_reference_sample:8
CBS|600|7|controlled_nano_swarm:8,honkai_adapted_circuit_substrate:8,#foils/polybenzimidazole:32
HRC|650|7|controlled_nano_swarm:16,separation_filter:8,#foils/polybenzimidazole:32
SPC|750|8|coated_nano_swarm:16,directional_crystallization_matrix:4,#plates/tungsten_steel:32
SRA|800|8|coated_nano_swarm:16,separation_filter:8,#foils/platinum:32
SPM|850|8|#ingots/soulium:16,#gems/diamond:16,#plates/tungsten_steel:16
MCE|900|9|honkai_adapted_circuit_substrate:16,#foils/platinum:32,#wires/fine/soulium:16
ALE|1200|12|#plates/soulium:32,etched_circuit_layer:16,directional_crystallization_matrix:8
OPR|450|5|separation_filter:8,fuel_encapsulation_part:8,#plates/silver:8
SSC|1400|10|#plates/soulium:24,directional_crystallization_matrix:8,honkai_reference_sample:16
CCE|1500|10|honkai_crystal_seed:32,directional_crystallization_matrix:8,#foils/platinum:32
MRE|1800|12|honkai_fuel_rod_casing:32,fuel_encapsulation_part:64,#plates/soulium:32
CPT|1600|10|etched_circuit_layer:16,#plates/soulium:16,#foils/polybenzimidazole:64
ERA|1600|10|directional_crystallization_matrix:16,#plates/soulium:32,honkai_reference_sample:16
GSC|1800|12|directional_crystallization_matrix:16,separation_filter:16,#plates/soulium:32
PCE|1800|12|separation_filter:16,#plates/silver:32,#plates/tungsten_steel:32
GPR|1600|10|separation_filter:32,#foils/polybenzimidazole:64,#dusts/carbon:64
FCA|1200|8|honkai_crystal_seed:32,#plates/tungsten_steel:32,#foils/platinum:16
ICA|1200|8|honkai_crystal_seed:32,#plates/silver:32,separation_filter:8
RCA|1400|10|honkai_crystal_seed:32,etched_circuit_layer:16,circuit_encapsulation_part:8
VCA|1600|10|honkai_crystal_seed:32,directional_crystallization_matrix:16,#plates/soulium:16
ECA|1400|10|honkai_crystal_seed:32,etched_circuit_layer:24,circuit_encapsulation_part:8
GCA|1400|10|honkai_crystal_seed:32,#plates/tungsten_steel:64,directional_crystallization_matrix:8
BCA|1600|10|honkai_crystal_seed:32,#foils/polybenzimidazole:64,directional_crystallization_matrix:16
TCA|1400|10|honkai_crystal_seed:32,etched_circuit_layer:8,#wires/fine/soulium:32
WCA|1600|10|honkai_crystal_seed:32,separation_filter:16,#plates/soulium:16
DKE|2000|12|#plates/soulium:48,circuit_encapsulation_part:16,etched_circuit_layer:16
VAK|2200|14|divine_key_housing:1,etched_circuit_layer:32,#foils/platinum:32
CJK|2400|15|divine_key_housing:1,directional_crystallization_matrix:24,#plates/soulium:32
SEK|2200|14|divine_key_housing:1,#plates/tungsten_steel:64,#plates/soulium:32
JOK|2200|14|divine_key_housing:1,#foils/polybenzimidazole:64,directional_crystallization_matrix:24
QOM|2400|15|directional_crystallization_matrix:24,etched_circuit_layer:24,honkai_reference_sample:16
QLE|3000|18|#plates/soulium:64,etched_circuit_layer:32,circuit_encapsulation_part:16
SSQ|1400|10|#ingots/soulium:32,honkai_reference_sample:16,separation_filter:16
CQS|2200|14|etched_circuit_layer:32,circuit_encapsulation_part:32,#foils/polybenzimidazole:64
ERM|2000|12|etched_circuit_layer:32,circuit_encapsulation_part:16,honkai_reference_sample:16
WCP|3000|15|etched_circuit_layer:32,directional_crystallization_matrix:24,#foils/platinum:32
UAA|3400|16|#plates/soulium:64,circuit_encapsulation_part:32,etched_circuit_layer:32
UED|3600|18|#plates/soulium:48,circuit_encapsulation_part:32,directional_crystallization_matrix:32
LTA|3600|18|honkai_reference_sample:32,etched_circuit_layer:32,#foils/platinum:64
HBD|4000|20|etched_circuit_layer:48,circuit_encapsulation_part:24,#plates/soulium:32
HCC|4500|22|#plates/soulium:96,circuit_encapsulation_part:32,#plates/tungsten_steel:64
HVI|5000|25|hyperion_keel_segment:4,hyperion_thruster_assembly:2,hyperion_navigation_module:2
BCC|4200|20|#plates/soulium:64,directional_crystallization_matrix:32,#foils/polybenzimidazole:64
WBC|4500|22|#plates/soulium:48,directional_crystallization_matrix:32,circuit_encapsulation_part:32
WTR|4800|24|directional_crystallization_matrix:48,#plates/soulium:48,separation_filter:32
LRE|5000|25|honkai_fuel_rod_casing:64,fuel_encapsulation_part:128,#plates/soulium:64
SWC|5200|25|#plates/soulium:64,etched_circuit_layer:64,directional_crystallization_matrix:48
SWS|4800|24|directional_crystallization_matrix:48,#foils/polybenzimidazole:128,circuit_encapsulation_part:32
SWR|5200|25|directional_crystallization_matrix:48,separation_filter:48,#plates/soulium:64
VRC|5500|26|#plates/soulium:64,etched_circuit_layer:64,circuit_encapsulation_part:48
IOP|6000|28|etched_circuit_layer:64,directional_crystallization_matrix:64,honkai_reference_sample:32
ILE|7200|30|#plates/soulium:128,etched_circuit_layer:96,circuit_encapsulation_part:64
UPR|3800|18|#plates/soulium:32,circuit_encapsulation_part:24,#foils/platinum:48
LTB|4000|20|etched_circuit_layer:48,honkai_reference_sample:32,#foils/platinum:64
IAA|7000|28|#plates/soulium:96,directional_crystallization_matrix:64,circuit_encapsulation_part:48
ESC|7500|30|soulium_anchor_component:16,directional_crystallization_matrix:64,#plates/soulium:64
HER|8000|30|soulium_anchor_component:16,etched_circuit_layer:64,#wires/fine/soulium:128
CED|8500|32|etched_circuit_layer:96,circuit_encapsulation_part:64,#wires/fine/soulium:128
WME|9000|32|soulium_anchor_component:32,directional_crystallization_matrix:64,#plates/soulium:96
WMS|9500|35|#plates/soulium:128,soulium_anchor_component:32,separation_filter:64
WPF|10000|35|conducting_composite:32,confining_composite:32,reconstructing_composite:32
CEE|10500|36|conducting_composite:32,confining_composite:32,etched_circuit_layer:96
URE|12000|40|confining_composite:64,conducting_composite:64,honkai_fuel_rod_casing:128
HCCO|11000|36|cognitive_composite:32,etched_circuit_layer:96,circuit_encapsulation_part:64
AIM|11500|38|reconstructing_composite:64,etched_circuit_layer:96,circuit_encapsulation_part:64
SEM|11500|38|conducting_composite:64,#wires/fine/soulium:128,etched_circuit_layer:64
IFF|11000|36|confining_composite:48,separation_filter:64,#plates/silver:64
CCF|11500|38|confining_composite:64,#plates/silver:96,#foils/platinum:64
IAR|12500|40|soulium_anchor_component:64,confining_composite:64,conducting_composite:32
MRA|12000|40|reconstructing_composite:64,separation_filter:96,circuit_encapsulation_part:64
SFF|13000|42|confining_composite:64,conducting_composite:64,#plates/tungsten_steel:128
GSF|13000|42|confining_composite:96,soulium_anchor_component:32,#plates/soulium:96
ECB|12500|40|confining_composite:96,directional_crystallization_matrix:64,#foils/polybenzimidazole:128
CLE|15000|45|cognitive_composite:64,reconstructing_composite:64,etched_circuit_layer:128
ELC|10000|35|#wires/fine/soulium:128,etched_circuit_layer:96,circuit_encapsulation_part:64
CKV|16000|45|cognitive_composite:96,reconstructing_composite:64,etched_circuit_layer:128
DIO|18000|48|conducting_composite:96,cognitive_composite:64,circuit_encapsulation_part:128
ASR|18000|48|cognitive_composite:128,etched_circuit_layer:128,reconstructing_composite:64
WCE|20000|50|confining_composite:128,reconstructing_composite:96,soulium_anchor_component:64
CAV|14000|40|cognitive_composite:64,etched_circuit_layer:96,honkai_reference_sample:64
TAA|24000|60|cognitive_composite:128,confining_composite:128,reconstructing_composite:128
DVC|12000|35|honkai_reference_sample:64,cognitive_composite:48,etched_circuit_layer:64
'''
# 仅作为新工艺方案的门槛断言，不伪装成现有配方已接线。
PROPOSED_GATES={
 'nano_building_unit':'RN-NBS','unprogrammed_nanobot':'RN-NRA','controlled_nano_swarm':'RN-NSP',
 'coated_nano_swarm':'RN-HRC','etched_circuit_layer':'RN-MCE','circuit_encapsulation_part':'RN-CPT',
 'divine_key_housing':'RN-DKE','hyperion_keel_segment':'RN-HCC','hyperion_thruster_assembly':'RN-HCC',
 'hyperion_navigation_module':'RN-HCC','soulium_anchor_component':'RN-IAA',
 'conducting_composite':'RN-WMS','confining_composite':'RN-WMS','reconstructing_composite':'RN-WMS','cognitive_composite':'RN-WMS'}
FORBIDDEN={'imitation_hyperion_blueprint','sealed_real_world_bubble','stable_simulated_world_bubble',
 'unstable_simulated_world_bubble','honkai_detector_calibration_report','imitation_void_archives',
 'imitation_cosmic_juggernaut','imitation_star_of_eden','imitation_oath_of_judah'}

def main():
 now=datetime.datetime.now().astimezone().isoformat()
 topics=json.loads((ROOT/'src/main/resources/data/hk3gtl/research/research_catalog.json').read_text(encoding='utf-8'))['topics']
 catalog={t['id']:t for t in topics}
 def ancestors(k):
  r=set(catalog[k]['prerequisites'])
  for p in list(r):r.update(ancestors(p))
  return r
 registration=(ROOT/'src/main/java/com/sirin/hk3gtl/common/registration/Hk3IndustrialContent.java').read_text(encoding='utf-8')
 registered=set(re.findall(r'item\("([a-z0-9_]+)",',registration))
 recipe_sources={p:p.read_text(encoding='utf-8') for p in (ROOT/'src/main/java/com/sirin/hk3gtl/common/recipe').rglob('*.java')}
 first=json.loads((OUT/'payment-proposal-first10.json').read_text(encoding='utf-8'))['rows']
 rows={r['id']:r for r in first};gaps=[]
 for line in DATA.strip().splitlines():
  key,points,minutes,raw=line.split('|');key='RN-'+key;assert key not in rows and key in catalog
  mats=[]
  for token in raw.split(','):
   name,count=token.rsplit(':',1);count=int(count);assert count>0
   if name.startswith('#'):
    m={'tag':'forge:'+name[1:],'count':count,'status':'GT材料标签候选，需核对双底包运行时标签及前级制造来源'}
    if name.endswith('/soulium'):
     assert 'RN-SRA' in ancestors(key),(key,name)
     m['proposed_gate']='RN-SRA或RN-SPM，按锭/加工形态分别核对'
   else:
    assert name in registered,(key,name)
    assert name not in FORBIDDEN and not name.startswith('imitation_'),name
    gate=PROPOSED_GATES.get(name)
    if gate:assert gate in ancestors(key),(key,name,gate)
    refs=[]
    for p,s in recipe_sources.items():
     for i,l in enumerate(s.splitlines(),1):
      if '"'+name+'"' in l:refs.append({'path':str(p.relative_to(ROOT)).replace('\\','/'),'line':i,'text':l.strip()[:260]})
    m={'item':'hk3gtl:'+name,'count':count,'registered':True,'proposed_gate':gate,'recipe_literal_references':refs,
       'status':'发现配方字面量引用，仍须判定输入/输出及完整来源' if refs else '已注册但未找到该物品的配方字面量引用；来源待补，不能据此宣称可支付'}
    if not refs:gaps.append({'topic':key,'item':name})
   mats.append(m)
  rows[key]={'id':key,'title':catalog[key]['title'],'points':int(points),'ticks':int(minutes)*1200,'materials':mats,'status':'助手提出的费用候选，不改生产数据；来源缺口不以点数路线掩盖'}
 assert set(rows)==set(catalog) and len(rows)==100
 ordered=[rows[t['id']] for t in topics]
 stats=[]
 for lab in range(1,6):
  rs=[rows[t['id']] for t in topics if t['lab']==lab]
  stats.append({'lab':lab,'topics':len(rs),'points_range':[min(r['points'] for r in rs),max(r['points'] for r in rs)],'seconds_range':[min(r['ticks']/20 for r in rs),max(r['ticks']/20 for r in rs)]})
 notes=[
  '已有10项候选原样合并；本次补90项，总100项。材料费用不替代实验证据。',
  '新工艺材料门槛仅为设计约束，已检查属于课题祖先；不能据此推断当前配方和电压已闭合。',
  'ELC不依赖WMS，故不应要求导能复合材料；采用前序魂钢导体替代。',
  'BCE后的试制蚀刻必须继续存在；RN-MCE开放正式工艺，不能反锁首批电路。',
  '将四种高维复合材料统一放到WMS可能与更早电子平台冲突；本表只用于支付可达性规划，七条电路材料支线仍未定稿。',
  '基底材料数量偏小还是偏大需结合生产批量校准，尚未声称与研究点经济价值等价。',
  '研究功率仍由当前MAX+tier决定；拟定费用和时间没有修改电压，前级供电自锁需单独核对。']
 result={'time':now,'status':'100项费用讨论候选，非实施或全部物料闭合','rows':ordered,'stage_summary':stats,'missing_literal_sources':gaps,'notes':notes}
 p=OUT/'payment-proposal-100.json';assert not p.exists()
 p.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 original=PLAN.read_text(encoding='utf-8');assert 'id="research-payment-complete-proposal"' not in original
 esc=lambda x:html.escape(str(x),quote=True)
 chunks=[f'<section class="panel" id="research-payment-complete-proposal"><h2>100课题完整费用候选（非生产数据）</h2><p>变更记录#1 · {esc(now)}。新增余下90项并合并首批10项；删除无。保留旧费用与历史计划，生产代码未修改。</p>']
 chunks+=['<p>'+esc(n)+'</p>' for n in notes]
 for stage in stats:
  lab=stage['lab'];chunks.append(f'<details><summary>S0{lab} · {stage["topics"]}项 · {stage["points_range"][0]}–{stage["points_range"][1]}点</summary>')
  for t in topics:
   if t['lab']!=lab:continue
   r=rows[t['id']];chunks.append(f'<h3>{esc(r["id"])} · {esc(r["title"])}</h3><p>{r["points"]}点或以下材料；基础{r["ticks"]/20:g}秒，实际仍受供电、在线条件及既定加减速影响。</p><ul>')
   for m in r['materials']:
    chunks.append('<li>'+esc(m.get('item',m.get('tag')))+' × '+str(m['count'])+'；'+esc(m.get('status','首批已核对HK3源码制造入口，未验收整包动态配方'))+'</li>')
   chunks.append('</ul>')
  chunks.append('</details>')
 chunks.append('<p>检查通过：100项覆盖、数量与点数/时间正值、HK3具体物品注册、明确新材料门槛属于祖先课题、不消耗图纸/世界泡身份/神之键/校准报告。尚未通过：全部现役配方可达性、双底包运行时标签、全部电压链和游戏验收。</p></section>')
 section='\n'.join(chunks);pos=original.lower().rfind('</body>');assert pos>=0
 with (OUT/'plan-before-payments-100.html').open('x',encoding='utf-8') as f:f.write(original)
 PLAN.write_text(original[:pos]+section+'\n'+original[pos:],encoding='utf-8')
 assert PLAN.read_text(encoding='utf-8').replace(section+'\n','',1)==original
 print(json.dumps({'coverage':100,'stages':stats,'missing_source_items':sorted({g['item'] for g in gaps}),'game_modified':False},ensure_ascii=False))
if __name__=='__main__':main()

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
