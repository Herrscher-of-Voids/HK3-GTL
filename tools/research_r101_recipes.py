"""Explicit provisional process balances; no structures or trade are installed."""
import json,pathlib,re
R=pathlib.Path(__file__).resolve().parents[1];B=R/'src/main/resources'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
contracts=read(B/'data/hk3gtl/research/research_execution.json')['topics']
by={x['id']:x for x in contracts}
# These two names were descriptive, not actual registered IDs.
for c in contracts:
 c['precursor']={'gas_purification_filter':'process_gas_filter','spent_gas_purification_filter':'depleted_gas_filter','imitation_reason_core':'unencapsulated_reason_core'}.get(c['precursor'],c['precursor'])
write(B/'data/hk3gtl/research/research_execution.json',{'schema':1,'revision':101,'structure_approval':False,'topics':contracts})
recipes=[]
def parts(s):
 return [{'id':('hk3gtl:'+p.split('*')[0]) if ':' not in p.split('*')[0] else p.split('*')[0],'count':int(p.split('*')[1]) if '*' in p else 1} for p in s.split(',') if p]
def fluids(s):return [{'id':p.split('*')[0],'amount':int(p.split('*')[1])} for p in s.split(',') if p]
def add(id,role,gate,ins,outs,fi='',fo='',ticks=800,tier=14,facts='',experiment=''):
 recipes.append(dict(id=id,role=role,requirements=['RN-'+p for p in gate.split(',') if p],item_inputs=parts(ins),item_outputs=parts(outs),fluid_inputs=fluids(fi),fluid_outputs=fluids(fo),ticks=ticks,energy_tier=tier,facts=facts.split(',') if facts else [],experiment=experiment,provisional=True))
# Real intermediate production; dedicated role types do not register or approve controllers.
add('industrial_soulium_precursor','I09','SSP','soulium_microstructure_template,gtceu:titanium_dust*8,gtceu:platinum_dust*2','soulium_microstructure_template,soulium_polymerization_residue','stabilized_liquid_honkai_energy*200,soulium_process_solvent*1000','soulium_precursor_fluid*800,spent_soulium_solvent*900',1200,facts='soulium_precursor')
add('industrial_soulium_template','GT_ASSEMBLER','LES','gtceu:platinum_foil*4,gtceu:tungsten_steel_plate*2,honkai_crystal_seed*2','soulium_microstructure_template*2',ticks=600)
add('industrial_process_solvent','GT_MIXER','LES','gtceu:carbon_dust*4','', 'gtceu:distilled_water*1000,honkai_analysis_reagent*100','soulium_process_solvent*1000,unrecoverable_process_effluent*100',600)
add('industrial_nano_building','I10','NBS','soulium_microstructure_template*2,gtceu:silicon_dust*4','nano_building_unit*16,inactive_nano_unit*2','soulium_precursor_fluid*400','nano_reaction_tail_liquid*300',1000,facts='nano_building')
add('industrial_nano_assembly','I11','NRA','nano_building_unit*8,gtceu:gold_foil*4,honkai_adapted_circuit_substrate','unprogrammed_nanobot*4,nano_assembly_scrap*2','gtceu:soldering_alloy*144','',1000,facts='nano_assembly')
add('industrial_rule_carrier','GT_ASSEMBLER','NRA','honkai_adapted_circuit_substrate*2,gtceu:platinum_foil*4','reconstruction_rule_carrier',ticks=600)
add('industrial_nano_control','I12','NSP','unprogrammed_nanobot*4,reconstruction_rule_carrier','controlled_nano_swarm*3,inactive_nano_unit','soulium_process_solvent*250','spent_soulium_solvent*250',1200,facts='nano_control')
add('industrial_resistant_coating','GT_MIXER','NSP','gtceu:polytetrafluoroethylene_dust*4,gtceu:carbon_dust*2','','soulium_process_solvent*500','honkai_resistant_coating*500',600)
add('industrial_nano_coating','I13','HRC','controlled_nano_swarm*3','coated_nano_swarm*2,inactive_nano_unit','honkai_resistant_coating*250','spent_resistant_coating*200',1000,facts='nano_coating')
add('industrial_soulium_polymerization','I14','SPC','coated_nano_swarm*2,gtceu:tungsten_steel_dust*16','soulium_polymerization_residue*8','soulium_precursor_fluid*500','nano_reaction_tail_liquid*400',1600,facts='soulium_polymerization')
add('industrial_soulium_reconstruction','I15','SRA','soulium_polymerization_residue*8,reconstruction_rule_carrier','soulium_data_substrate*4,soulium_swarf*2','honkai_stabilization_medium*200','spent_honkai_stabilization_medium*200',1600,facts='soulium_reconstruction')
add('industrial_soulium_processing','I16','SPM','soulium_data_substrate*4','material:soulium/plate*4,material:soulium/fine_wire*8,soulium_swarf*2','honkai_coolant*250','hot_honkai_coolant*250',1200,facts='soulium_processing')
add('industrial_growth_medium','GT_MIXER','CBS','gtceu:silicon_dust*8,gtceu:phosphorus_dust*2','','honkai_analysis_reagent*250,gtceu:distilled_water*1000','circuit_growth_medium*1000,unrecoverable_process_effluent*250',600)
add('industrial_substrate_growth','I12','CBS','controlled_nano_swarm,gtceu:silicon_plate*4','honkai_adapted_circuit_substrate*4,defective_circuit_substrate','circuit_growth_medium*500','spent_circuit_growth_medium*500',1200,facts='substrate_growth')
add('industrial_lithography_mask','GT_ASSEMBLER','CBS,SPM','gtceu:soulium_plate*2,gtceu:platinum_foil*4','circuit_lithography_mask',ticks=800)
add('industrial_etchant','GT_MIXER','CBS','gtceu:carbon_dust*2','','honkai_analysis_reagent*500,gtceu:distilled_water*500','honkai_circuit_etchant*1000',600)
add('industrial_circuit_etching','I16','MCE','honkai_adapted_circuit_substrate*4,circuit_lithography_mask,gtceu:soulium_fine_wire*8','etched_circuit_layer*4,failed_circuit_layer','honkai_circuit_etchant*500','spent_honkai_etchant*500',1400,facts='circuit_etching')
add('industrial_circuit_packaging','I16','CPT','etched_circuit_layer*4,gtceu:polytetrafluoroethylene_plate*4,gtceu:gold_foil*8','circuit_encapsulation_part*4,rejected_circuit_package','gtceu:soldering_alloy*288','',1200,18,'circuit_packaging')
add('industrial_heat_exchange','I05','HLC','separation_filter','', 'hot_honkai_coolant*1000','honkai_coolant*900,lost_coolant_residue*100',600)
add('industrial_spent_rod_reprocessing','I05','SFR','depleted_honkai_fuel_rod','recovered_fuel_casing_material*2,inactive_fuel_residue*2','honkai_analysis_reagent*500','fuel_waste_processing_fluid*500',1800)
add('industrial_optimized_medium_recovery','I05','OPR','separation_filter*2,gtceu:carbon_dust*4','','spent_honkai_stabilization_medium*1000','honkai_stabilization_medium*850,unrecoverable_process_effluent*150',1200)
add('industrial_optimized_heat_exchange','I05','OPR','separation_filter','','hot_honkai_coolant*1000','honkai_coolant*950,lost_coolant_residue*50',500)
add('industrial_optimized_spent_rods','I05','OPR','depleted_honkai_fuel_rod*2','recovered_fuel_casing_material*5,inactive_fuel_residue*3','honkai_analysis_reagent*800','fuel_waste_processing_fluid*800',2800)
add('industrial_process_gas_filter','GT_ASSEMBLER','GSC','separation_filter*2,gtceu:carbon_dust*4,gtceu:platinum_foil*2','process_gas_filter*2',ticks=600)
add('industrial_gas_purification','I05','GPR','process_gas_filter','depleted_gas_filter,process_gas_impurity*2','spent_soulium_process_gas*1000','soulium_protective_gas*800,hot_soulium_exhaust*200',800,19,'gas_purification')
add('industrial_vessel_shell','I16','BCC','gtceu:soulium_plate*16,circuit_encapsulation_part*4','failed_containment_shell','honkai_coolant*500','hot_honkai_coolant*500',1800,22,'vessel_shell')
# The FIRST shell is permitted by existing SPM, not by its own BCC research.
recipes[-1]['requirements']=['RN-SPM','RN-JOK']
add('industrial_vessel_calibration','I33','BCC','failed_containment_shell,spatial_calibration_module,imitation_binding_core','empty_bubble_containment_vessel','honkai_stabilization_medium*1000','spent_honkai_stabilization_medium*1000',2400,22)
add('industrial_drone_assembly','I11','UAA','soulium_data_substrate*8,circuit_encapsulation_part*4,controlled_nano_swarm*2','industrial_work_drone','gtceu:soldering_alloy*576','',2000,21,'drone_assembly')
add('industrial_spatial_probe','I11','CJK','soulium_data_substrate*4,circuit_encapsulation_part*2,imitation_void_core','spatial_probe',ticks=1200,tier=19)
add('industrial_drone_repair','I11','UPR','worn_work_drone,nano_building_unit*8,circuit_encapsulation_part*2','industrial_work_drone,drone_disassembly_scrap','gtceu:soldering_alloy*288','',1600,22)
# 修订104：原版实际注册表证明终止组件没有首件制造路线；不要求SWR/I31，不输出研究证据。
add('industrial_bubble_termination_component','I16','WTR,SPM','soulium_data_substrate*2,spatial_calibration_module,circuit_encapsulation_part*2','bubble_termination_charge','gtceu:soldering_alloy*288,honkai_coolant*250','hot_honkai_coolant*250',1200,22)
add('industrial_anchor_component','GT_ASSEMBLER','RAT','gtceu:tungsten_steel_plate*8,gtceu:platinum_foil*4,honkai_adapted_circuit_substrate*2','soulium_anchor_component',ticks=1000,tier=14)
add('industrial_spatial_module','I33','VCA','soulium_data_substrate*4,unencapsulated_void_core,circuit_encapsulation_part*2','spatial_calibration_module',ticks=1200,tier=18)
add('industrial_key_housing','I33','DKE','soulium_data_substrate*8,circuit_encapsulation_part*2','divine_key_housing',ticks=1400,tier=19,facts='divine_key_assembly')
for core,topic in [('flame','FCA'),('ice','ICA'),('reason','RCA'),('void','VCA'),('corruption','ECA'),('rock','GCA'),('binding','BCA'),('thunder','TCA'),('wind','WCA')]:
 add('industrial_core_'+core,'I08',topic,'honkai_crystal_seed*16,directional_crystallization_matrix*4','unencapsulated_'+core+'_core','stabilized_liquid_honkai_energy*500','crystallization_residual_liquid*500',2400,18)
 # Core encapsulation must not require DKE (DKE evidence itself precedes I33).
 if core!='reason':add('industrial_encapsulate_'+core,'I16',topic+',CPT','unencapsulated_'+core+'_core,circuit_encapsulation_part*4','imitation_'+core+'_core',ticks=1600,tier=18)
for item,topic,core in [('imitation_void_archives','VAK','reason'),('imitation_cosmic_juggernaut','CJK','void'),('imitation_star_of_eden','SEK','rock'),('imitation_oath_of_judah','JOK','binding')]:
 add('industrial_'+item,'I33',topic,'divine_key_housing,unencapsulated_'+core+'_core,circuit_encapsulation_part*4',item,ticks=2400,tier=19)
add('industrial_ship_components','I16','HCC','soulium_data_substrate*16,circuit_encapsulation_part*8,coated_nano_swarm*4','hyperion_keel_segment*2,hyperion_navigation_module,hyperion_thruster_assembly,hyperion_bridge_module','honkai_coolant*1000','hot_honkai_coolant*1000',3200,22,'ship_components')
# 修订101：补全已批准职责的实际耗料工况，仍不注册任何新结构。
add('industrial_fuel_rod_encapsulation','I18','FRP','honkai_fuel_rod_casing,fuel_encapsulation_part*2','honkai_fuel_rod','liquid_honkai_fuel*1000,honkai_coolant*250','hot_honkai_coolant*250',1000,14)
add('industrial_dense_rod_encapsulation','I18','FRP,CFR','honkai_fuel_rod_casing,fuel_encapsulation_part*4','dense_honkai_fuel_rod','concentrated_liquid_honkai_fuel*1000,honkai_coolant*500','hot_honkai_coolant*500',1400,16)
for role,gate,rod,n,tier,fact in [('I19','SRE','honkai_fuel_rod',1,14,'reactor_load,reactor_spent_rod'),('I20','MRE','dense_honkai_fuel_rod',2,17,'medium_reactor_load'),('I21','LRE','dense_honkai_fuel_rod',4,23,'large_reactor_load'),('I22','URE','dense_honkai_fuel_rod',8,26,'ultra_reactor_load')]:
 add('industrial_reactor_'+role.lower(),role,gate,rod+'*'+str(n),('depleted_honkai_fuel_rod' if n==1 else 'depleted_dense_honkai_fuel_rod')+'*'+str(n), 'honkai_coolant*'+str(1000*n),'hot_honkai_coolant*'+str(1000*n),3600,tier,fact)
add('industrial_dense_spent_rod_reprocessing','I05','SFR','depleted_dense_honkai_fuel_rod','recovered_fuel_casing_material*4,inactive_fuel_residue*4','honkai_analysis_reagent*800','fuel_waste_processing_fluid*800',2200,17)
add('industrial_solid_collection','I01-2','SSC','soulium_anchor_component,separation_filter*2','honkai_crystal_seed*8,concentrated_honkai_impurity*2','honkai_coolant*500','hot_honkai_coolant*500',1200,15,'solid_collection')
add('industrial_gas_collection','I01-3','GSC','soulium_anchor_component,process_gas_filter','depleted_gas_filter','honkai_coolant*500','gaseous_honkai_energy*1000,hot_honkai_coolant*500',1600,19,'gas_collection')
add('industrial_crystal_growth','I08','CCE','honkai_crystal_seed*4,directional_crystallization_matrix','honkai_crystal_seed*8,concentrated_honkai_impurity','stabilized_liquid_honkai_energy*500,honkai_coolant*500','crystallization_residual_liquid*450,hot_honkai_coolant*500',1600,16,'crystal_growth')
add('industrial_anchor_baseline','I36','RAT','soulium_anchor_component,honkai_reference_sample','failed_engineering_specimen','honkai_stabilization_medium*250','spent_honkai_stabilization_medium*250',1200,14,'anchor_basic')
add('industrial_anchor_enhanced','I36','ERA','soulium_anchor_component*2,honkai_crystal_seed*4','failed_engineering_specimen','honkai_stabilization_medium*500','spent_honkai_stabilization_medium*500',1600,17,'anchor_enhanced')
add('industrial_fresh_protective_gas','I23','PCE','process_gas_filter','depleted_gas_filter','gaseous_honkai_energy*1000','soulium_protective_gas*800,spent_soulium_process_gas*200',1200,19,'phase_conversion,gas_exhaust')
add('industrial_beacon_calibration','I44','CJK','spatial_calibration_module,honkai_reference_sample','failed_engineering_specimen',ticks=1800,tier=19,experiment='RN-QOM')
add('industrial_quantum_observation','I24','QOM','spatial_probe,honkai_reference_sample','world_model_carrier',ticks=2400,tier=19,experiment='RN-QLE')
add('industrial_enhanced_beacon_signal','I44','QLE','spatial_calibration_module*2,imitation_cosmic_juggernaut','failed_engineering_specimen',ticks=1800,tier=20,facts='enhanced_beacon_signal')
add('industrial_coordinate_solution','I25','WCP','world_model_carrier,spatial_probe','world_model_carrier',ticks=2400,tier=21,facts='coordinate_solution')
add('industrial_imaginary_observation','I34','IOP','spatial_probe,world_model_carrier','world_model_carrier',ticks=3200,tier=23,facts='imaginary_observation',experiment='RN-ILE')
add('industrial_imaginary_anchor','I35','IAA','soulium_anchor_component*4,spatial_calibration_module*2','failed_engineering_specimen','honkai_stabilization_medium*1000','spent_honkai_stabilization_medium*1000',3200,23,'imaginary_anchor')
add('industrial_world_maintenance','I37','WME','soulium_anchor_component*4,world_model_carrier','world_maintenance_specimen*4','world_stabilization_medium*1000','spent_world_stabilization_medium*1000',3600,24,'world_maintenance')
add('industrial_world_medium','GT_MIXER','SWS','honkai_crystal_seed*4','','honkai_stabilization_medium*1000,soulium_process_solvent*500','world_stabilization_medium*1000,spent_soulium_solvent*500',1000,22)
for name,gate,core,fact in [('electromagnetic','TCA','thunder','electromagnetic_test'),('cryogenic','ICA','ice','cryogenic_test'),('flame','FCA','flame','flame_test'),('compression','SEK','rock','compression_test'),('binding','JOK','binding','binding_test'),('flow','WCA','wind','flow_test')]:
 out={'electromagnetic':'polarized_electromagnetic_material','cryogenic':'cryogenic_condensed_material','flame':'extreme_casting_material'}.get(name,'failed_engineering_specimen')
 add('industrial_'+name+'_worktest','I33',gate+',DKE','imitation_'+core+'_core,soulium_data_substrate*2',out,'honkai_coolant*500','hot_honkai_coolant*500',1800,20,fact)
add('industrial_composite_production','I40','WMS','soulium_data_substrate*8,world_maintenance_specimen','conducting_composite*2,confining_composite*2,reconstructing_composite*2,cognitive_composite*2,composite_offcut*2','world_stabilization_medium*500','spent_world_stabilization_medium*500',3200,25,'composite_production')
add('industrial_prefabrication','I42','WPF','conducting_composite*2,confining_composite*2,reconstructing_composite*2,cognitive_composite*2','world_maintenance_specimen*4,composite_offcut*2','honkai_coolant*1000','hot_honkai_coolant*1000',3200,25,'prefabrication')
add('industrial_ship_blueprint_analysis','I32','LTA,UED','ship_engineering_archive,soulium_data_substrate*2,minecraft:paper*4','imitation_hyperion_blueprint','honkai_analysis_reagent*250','spent_analysis_reagent*250',ticks=2400,tier=19,experiment='RN-HBD')
# 可复制图纸只用于制造；不能回写档案或实验完成记录。
add('industrial_ship_blueprint_copy','I32','HBD','soulium_data_substrate*2,minecraft:paper*4','imitation_hyperion_blueprint','honkai_analysis_reagent*250','spent_analysis_reagent*250',ticks=1200,tier=19)
recipes[-1]['item_catalysts']=parts('imitation_hyperion_blueprint')
# Individual specimen manufacture is a physical GT operation. The subsequent test
# additionally demands specific upstream server receipts. No specimen itself grants evidence.
registered=set(re.findall(r'item\("([a-z0-9_]+)"',(R/'src/main/java/com/sirin/hk3gtl/common/registration/Hk3IndustrialContent.java').read_text(encoding='utf-8')))
for c in contracts:
 if c['existing'] or c['id']=='RN-HBD':continue
 assert c['precursor'] in registered,c['precursor']
 prep='GT_ASSEMBLER' if c['lab']<=2 else ('I16' if c['executor'] in ['I33','I11','I02'] else 'I32')
 # WCP位于I32解锁前，起步观测样件必须由既有装配工艺准备。
 if c['id']=='RN-WCP':prep='GT_ASSEMBLER'
 add('industrial_prepare_'+c['id'][3:].lower(),prep,','.join(p[3:] for p in c['prerequisites']),c['precursor']+',gtceu:platinum_foil*2,gtceu:tungsten_steel_plate*2',c['specimen'],ticks=max(400,c['ticks']//2),tier=c['energy_tier'])
 add(c['recipe'],c['executor'],','.join(p[3:] for p in c['prerequisites']),c['specimen']+',honkai_reference_sample,minecraft:paper*2','failed_engineering_specimen',ticks=c['ticks'],tier=c['energy_tier'],experiment=c['id'])
# Production samples must obey known physical fluid requirements.
for r in recipes:
 r['energy_direction']='output' if r['role'] in ['I19','I20','I21','I22'] else 'input'
 for entry in r['item_inputs']+r['item_outputs']:
  entry['id']={'gtceu:soulium_plate':'material:soulium/plate','gtceu:soulium_fine_wire':'material:soulium/fine_wire'}.get(entry['id'],entry['id'])
 if r['id']=='industrial_prepare_hlc':r['fluid_inputs']=fluids('hot_honkai_coolant*250');r['fluid_outputs']=fluids('lost_coolant_residue*250')
 if r['id']=='industrial_prepare_ssp':r['fluid_inputs']=fluids('stabilized_liquid_honkai_energy*100');r['fluid_outputs']=fluids('spent_soulium_solvent*100')
 if r['id'] in ['industrial_prepare_hlc','industrial_prepare_ssp']:r['role']='I04'
 # GT搅拌机只有一个流体输出槽；带尾液的化学配制改用既有化学反应釜。
 if r['role']=='GT_MIXER' and len(r['fluid_outputs'])>1:r['role']='GT_CHEMICAL'
 if r['id']=='industrial_prepare_sre':r['item_inputs']+=parts('fuel_encapsulation_test_specimen')
 # Future experiments only read real-world/world-bubble receipts. Their physical
 # test does not capture, terminate, clone or create a world by recipe output.
ids=[r['id'] for r in recipes];assert len(set(ids))==len(ids)
write(B/'data/hk3gtl/research/industrial_processes.json',{'schema':1,'revision':101,'provisional':True,'recipes':recipes})
write(R/'logs/research-mainline-r101/provisional-recipes.json',{'recipes':recipes})
# Model reuse is explicit, not a newly approved texture design.
for c in contracts:
 if not c['existing']:write(B/('assets/hk3gtl/models/item/'+c['specimen']+'.json'),{'parent':'minecraft:item/generated','textures':{'layer0':'hk3gtl:item/failed_engineering_specimen'}})
for lang in ['zh_cn','en_us']:
 p=B/('assets/hk3gtl/lang/'+lang+'.json');d=read(p)
 for c in contracts:
  if not c['existing']:d['item.hk3gtl.'+c['specimen']]=(c['title']+'专用试验样件（不能作为正式产物）') if lang=='zh_cn' else c['id']+' Dedicated Test Specimen (Not a Production Component)'
 for item,title in [('world_mining_legacy_record','真实采掘遗留资料'),('ship_engineering_archive','舰船工程档案')]:
  d['item.hk3gtl.'+item]=title if lang=='zh_cn' else item.replace('_',' ').title()
 write(p,d)
for item in ['world_mining_legacy_record','ship_engineering_archive']:
 write(B/('assets/hk3gtl/models/item/'+item+'.json'),{'parent':'minecraft:item/generated','textures':{'layer0':'minecraft:item/paper'}})
print(len(recipes),'provisional recipes; 100 contracts; structures untouched')

# 变更记录 #2 · 2026-09-30 00:03:08 · 修订102：同步已批准图纸成本与非消耗模板，避免重新生成后回退。

# 变更记录 #3 · 2026-09-30 01:17:37 · 修订104。删除：无；新增：终止组件首件路线；修改：与正式工艺表同源数值；用途：再生成不丢失修复。

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
