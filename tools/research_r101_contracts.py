"""Build the auditable beta5 execution data. Never registers machine structures."""
import json, pathlib, datetime
R=pathlib.Path(__file__).resolve().parents[1]
BASE=R/'src/main/resources'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
catalog=read(BASE/'data/hk3gtl/research/research_catalog.json')['topics']
approved={}
for p in sorted((R/'logs/research-migration-20260928').glob('s*-experiment-contracts-*.json')):
    for row in read(p)['rows']: approved[row['id']]=row
# Execution site, consumed physical precursor, required real process facts.
# A fact is a successful server operation, NEVER inventory possession or a recipe unlock.
rows='''
HED|I01-1|prototype_honkai_detector|
HSA|I02|honkai_analysis_sample|
LSE|I03|separation_filter|
LES|I04|honkai_crystal_seed|
BCE|I02|honkai_adapted_circuit_substrate|
DMT|I07|prototype_honkai_detector|
SMR|I05|separation_filter|
HFB|I06|fuel_matrix|
FRP|I02|fuel_encapsulation_test_specimen|
SRE|I02|honkai_fuel_rod_casing|
HLC|I02|fuel_encapsulation_part|reactor_load
SFR|I02|depleted_honkai_fuel_rod|reactor_spent_rod
RAT|I02|honkai_reference_sample|
SSP|I02|honkai_crystal_seed|
NBS|I02|soulium_microstructure_template|soulium_precursor
NRA|I02|nano_building_unit|nano_building
NSP|I02|unprogrammed_nanobot|nano_assembly
CBS|I02|controlled_nano_swarm|nano_control
HRC|I02|controlled_nano_swarm|nano_control
SPC|I02|coated_nano_swarm|nano_coating
SRA|I02|soulium_polymerization_residue|soulium_polymerization
SPM|I02|soulium_data_substrate|soulium_reconstruction
MCE|I02|honkai_adapted_circuit_substrate|substrate_growth,soulium_processing
ALE|S01|etched_circuit_layer|
OPR|S01|separation_filter|recovery_medium,recovery_heat,recovery_spent_rods
SSC|I02|soulium_data_substrate|liquid_collection
CCE|I02|honkai_crystal_seed|solid_collection
CFR|I17|fuel_matrix|
MRE|I02|fuel_encapsulation_part|reactor_load,recovery_heat,recovery_spent_rods
CPT|I02|etched_circuit_layer|circuit_etching
ERA|I02|soulium_anchor_component|anchor_basic
GSC|I02|soulium_anchor_component|liquid_collection,solid_collection
PCE|I02|gas_purification_filter|gas_collection
GPR|I02|spent_gas_purification_filter|gas_exhaust
FCA|I02|honkai_crystal_seed|crystal_growth
ICA|I02|honkai_crystal_seed|crystal_growth
RCA|I02|honkai_crystal_seed|crystal_growth,circuit_packaging
VCA|I02|honkai_crystal_seed|crystal_growth,anchor_enhanced
ECA|I02|honkai_crystal_seed|crystal_growth,circuit_packaging
GCA|I02|honkai_crystal_seed|crystal_growth
BCA|I02|honkai_crystal_seed|crystal_growth,anchor_enhanced
TCA|I02|honkai_crystal_seed|crystal_growth,circuit_packaging
WCA|I02|honkai_crystal_seed|crystal_growth,gas_collection
DKE|I02|circuit_encapsulation_part|circuit_packaging
VAK|I33|imitation_reason_core|divine_key_assembly
CJK|I33|imitation_void_core|divine_key_assembly
SEK|I33|imitation_rock_core|divine_key_assembly
JOK|I33|imitation_binding_core|divine_key_assembly
QOM|I44|spatial_calibration_module|
QLE|I24|spatial_probe|
SSQ|I02|soulium_data_substrate|soulium_polymerization,soulium_reconstruction,soulium_processing
CQS|I02|circuit_encapsulation_part|circuit_packaging,gas_collection
ERM|S02|imitation_corruption_core|
WCP|I24|spatial_probe|enhanced_beacon_signal,cocoon_authorization
UAA|I02|unprogrammed_nanobot|soulium_processing,circuit_packaging
UED|I11|spatial_probe|coordinate_solution,drone_assembly
LTA|I02|world_mining_legacy_record|first_mining_legacy
HBD|I32|ship_engineering_archive|ship_archive
HCC|I02|soulium_data_substrate|soulium_processing
HVI|I33|hyperion_navigation_module|ship_components
BCC|I33|failed_containment_shell|vessel_shell
WBC|I33|empty_bubble_containment_vessel|coordinate_solution
WTR|I33|spatial_calibration_module|real_capture
LRE|I02|fuel_encapsulation_part|medium_reactor_load,phase_conversion
SWC|I32|world_model_carrier|real_termination
SWS|I32|world_maintenance_specimen|simulation_created
SWR|I32|bubble_termination_charge|simulation_stabilized
VRC|I32|spatial_probe|distinct_mining_routes
IOP|I32|world_model_carrier|simulation_full_chain,distinct_mining_routes
ILE|I34|spatial_probe|
UPR|I11|worn_work_drone|drone_return
LTB|I32|world_mining_legacy_record|distinct_legacy_sources
IAA|I33|soulium_anchor_component|imaginary_observation
ESC|I33|soulium_data_substrate|liquid_collection,solid_collection,gas_collection,imaginary_anchor
HER|I33|soulium_data_substrate|energy_collection
CED|I32|soulium_data_substrate|hw_injection,hw_load
WME|I33|soulium_anchor_component|imaginary_anchor,anchor_enhanced,hw_injection,manual_dispatch
WMS|I32|world_maintenance_specimen|world_maintenance
WPF|I32|conducting_composite|composite_production
CEE|I32|world_maintenance_specimen|prefabrication
URE|I32|extreme_casting_material|large_reactor_load,composite_production
HCCO|I43|soulium_data_substrate|formal_communication
AIM|I43|etched_circuit_layer|soulium_processing,circuit_packaging
SEM|I43|polarized_electromagnetic_material|electromagnetic_test
IFF|I43|gas_purification_filter|flow_test,gas_purification,recovery_heat
CCF|I43|cryogenic_condensed_material|cryogenic_test
IAR|I43|soulium_anchor_component|imaginary_anchor,world_maintenance
MRA|I43|recovered_fuel_casing_material|recovery_medium,recovery_spent_rods,gas_purification
SFF|I43|extreme_casting_material|flame_test,ultra_reactor_load
GSF|I43|soulium_anchor_component|compression_test,simulation_created,simulation_stabilized
ECB|I43|imitation_binding_core|binding_test
CLE|I43|soulium_data_substrate|lab_four_interface,three_domains
ELC|I32|soulium_data_substrate|manual_dispatch_multiple
CKV|I43|world_model_carrier|contradiction_retest,three_domains
DIO|I43|industrial_work_drone|cross_machine_order
ASR|I43|imitation_corruption_core|bounded_computation
WCE|I43|world_model_carrier|simulation_full_chain
CAV|I43|soulium_data_substrate|wonder_W09,wonder_W11,wonder_W13,wonder_W14
TAA|I43|soulium_data_substrate|all_fourteen_wonders,ship_acceptance,cross_domain_report
DVC|I32|world_model_carrier|three_domain_difference
'''
specs={p[0]:p[1:] for p in (line.split('|') for line in rows.strip().splitlines())}
existing={'HED':'machine:liquid_collection','HSA':'industrial_initial_spectrum','LSE':'industrial_liquid_fractionation','LES':'industrial_liquid_stabilization','BCE':'industrial_circuit_adaptation_experiment','DMT':'industrial_prototype_detector_calibration','SMR':'industrial_stabilization_medium_recovery','HFB':'industrial_liquid_fuel_blending','FRP':'industrial_fuel_rod_isolation_experiment','CFR':'industrial_liquid_fuel_concentration','ALE':'LAB-ALE','OPR':'LAB-OPR','ERM':'LAB-ERM-AID'}
existing.update(QOM='industrial_beacon_calibration',QLE='industrial_quantum_observation',ILE='industrial_imaginary_observation',SWS='world:simulation_created',HBD='industrial_ship_blueprint_analysis')
unlocks={}
for fragment in '''HSA:I03 LSE:I04 BCE:I05,I06,I07 HFB:I17 FRP:I18 SRE:I19 RAT:I36 SSP:I09 NBS:I10 NRA:I11 NSP:I12 HRC:I13 SPC:I14 SRA:I15 SPM:I16 ALE:S02 SSC:I01-2 CCE:I08 MRE:I20 GSC:I01-3 PCE:I23 DKE:I33 CJK:I44,I45 QOM:I24 QLE:S03 WCP:I25 UED:I26 LTA:I32 HVI:H01 WBC:I27 WTR:I28 LRE:I21 SWC:I29 SWS:I30 SWR:I31 VRC:I39 IOP:I34 ILE:S04 IAA:I35 ESC:I01-4 HER:I38 CED:I41 WME:I37 WMS:I40 WPF:I42 CEE:I43 URE:I22 HCCO:W01 AIM:W02 SEM:W04 IFF:W05 CCF:W06 IAR:W03 MRA:W07 SFF:W08 GSF:W10 ECB:W12 CLE:S05 CKV:W09 DIO:W11 ASR:W13 WCE:W14 TAA:W15'''.split():
    k,v=fragment.split(':');unlocks[k]=v.split(',')
out=[]
for t in catalog:
    k=t['id'][3:];a=approved[t['id']];role,precursor,facts=specs[k]
    parents=list(dict.fromkeys(a.get('experiment_recipe_requirements',t['prerequisites'])+a.get('facility_and_input_unlocks',[])))
    if k=='CFR': parents=['RN-HFB']
    if k=='HED': parents=[]
    assert t['id'] not in parents,(t['id'],parents)
    out.append(dict(id=t['id'],title=t['title'],lab=t['lab'],tier=t['tier'],executor=role,
        recipe=existing.get(k,'industrial_experiment_'+k.lower()),existing=k in existing,
        prerequisites=parents,facts=facts.split(',') if facts else [],
        specimen='research_specimen_'+k.lower(),precursor=precursor,
        ticks=800+400*(t['lab']-1)+40*t['tier'],energy_tier=max(14,13+t['tier']),
        provisional=k not in existing,unlocks=unlocks.get(k,[]),
        source=a['experiment_facility'],success=a['success'],inputs=a['inputs'],benefit=a['formal_unlock'],
        no_self_lock=a['no_self_lock']))
# 修订102：HBD采用已批准的特殊工艺，不能被通用样件公式覆盖。
for entry in out:
    if entry['id']=='RN-HBD':
        entry['ticks']=2400;entry['energy_tier']=19
        entry['no_self_lock']='I26真实任务20%提前发现、第5次成功保底；模拟与终止不计入。I32在LTA/UED后解析，先发证据再正常付款研究。'
assert len(out)==100 and len(specs)==100
write(BASE/'data/hk3gtl/research/research_execution.json',{'schema':1,'revision':101,'structure_approval':False,'topics':out})
write(R/'logs/research-mainline-r101/execution-plan.json',{'generated_at':datetime.datetime.now().isoformat(),'topics':out})
print('Wrote 100 explicit execution contracts; geometry not registered.')

# 变更记录 #2 · 2026-09-30 00:04:43 · 修订102：修正批准的HBD工艺值及已确认保底说明。

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
