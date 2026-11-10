"""修订75资源维护：100个课题使用解锁成果图标，修改按钮与功率提示。

变更记录 #1：执行时间写入资源备注；保留历史记录、备份覆盖文件。
输入：研究目录和已有注册资产；输出：独立图标目录、中英文本及修订日志。
"""
from pathlib import Path
from datetime import datetime
import json
import shutil

ROOT=Path(__file__).resolve().parents[1]
RES=ROOT/'src/main/resources'
LOG=ROOT/'logs/revision75'
STAMP=datetime.now().astimezone()


def write_json(path,data):
    if path.exists():
        backup=LOG/'backup'/path.relative_to(ROOT)
        if not backup.exists():
            backup.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(path,backup)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    pairs='''HED honkai_analysis_sample
HSA analyzed_honkai_sample
LSE separation_filter
LES honkai_energy_crystal
BCE honkai_adapted_circuit_substrate
DMT liquid_honkai_detector
SMR separation_filter
HFB honkai_fuel_rod
FRP honkai_fuel_rod
SRE small_honkai_reactor_vessel
HLC honkai_heat_exchanger
SFR recovered_fuel_casing_material
RAT soulium_anchor_component
SSP soulium_microstructure_template
NBS nano_building_unit
NRA unprogrammed_nanobot
NSP controlled_nano_swarm
CBS honkai_adapted_circuit_substrate
HRC coated_nano_swarm
SPC soulium_proto_mass
SRA stabilized_soulium_proto_mass
SPM soulium_data_substrate
MCE etched_circuit_layer
ALE advanced_research_casing
OPR separation_filter
SSC solid_honkai_detector
CCE honkai_crystal_seed
CFR dense_honkai_fuel_rod
MRE medium_honkai_reactor_vessel
CPT circuit_encapsulation_part
ERA soulium_anchor_component
GSC gaseous_honkai_detector
PCE honkai_heat_exchanger
GPR process_gas_filter
FCA imitation_flame_core
ICA imitation_ice_core
RCA imitation_reason_core
VCA imitation_void_core
ECA imitation_corruption_core
GCA imitation_rock_core
BCA imitation_binding_core
TCA imitation_thunder_core
WCA imitation_wind_core
DKE divine_key_housing
VAK imitation_void_archives
CJK imitation_cosmic_juggernaut
SEK imitation_star_of_eden
JOK imitation_oath_of_judah
QOM spatial_probe
QLE quantum_research_casing
SSQ soulium_data_substrate
CQS circuit_encapsulation_part
ERM research_point_computer
WCP spatial_calibration_module
UAA industrial_work_drone
UED unmanned_resource_probe
LTA reverse_engineering_specimen
HBD imitation_hyperion_blueprint
HCC hyperion_keel_segment
HVI hyperion_navigation_module
BCC empty_bubble_containment_vessel
WBC sealed_real_world_bubble
WTR world_matter_seed
LRE large_honkai_reactor_vessel
SWC unstable_simulated_world_bubble
SWS stable_simulated_world_bubble
SWR world_model_carrier
VRC spatial_probe
IOP spatial_calibration_module
ILE imaginary_research_casing
UPR industrial_work_drone
LTB reverse_engineering_specimen
IAA soulium_anchor_component
ESC energy_honkai_detector
HER conducting_composite
CED high_dimensional_energy_conduit
WME world_maintenance_specimen
WMS civilization_singularity
WPF extreme_casting_material
CEE world_maintenance_specimen
URE ultimate_honkai_reactor_vessel
HCCO wonder_origin_core_mount
AIM wonder_reason_core_mount
SEM polarized_electromagnetic_material
IFF conducting_composite
CCF cryogenic_condensed_material
IAR wonder_void_core_mount
MRA reconstructing_composite
SFF extreme_casting_material
GSF civilization_singularity
ECB confining_composite
CLE civilization_computing_array
ELC high_dimensional_energy_conduit
CKV cognitive_composite
DIO civilization_computing_array
ASR research_point_computer
WCE stable_simulated_world_bubble
CAV world_maintenance_specimen
TAA wonder_tree_sea_core_mount
DVC cognitive_composite'''
    icons={'RN-'+line.split()[0]:'hk3gtl:'+line.split()[1] for line in pairs.splitlines()}
    # GTRegistrate研究计算机使用GT命名空间；以语言和既有模型进一步核对。
    icons['RN-ERM']=icons['RN-ASR']='hk3gtl:research_point_computer'
    catalog=json.loads((RES/'data/hk3gtl/research/research_catalog.json').read_text('utf-8'))
    assert set(icons)=={t['id'] for t in catalog['topics']}
    for topic,identifier in icons.items():
        ns,item=identifier.split(':')
        assert (RES/f'assets/{ns}/models/item/{item}.json').exists() or (
            item=='research_point_computer' and (RES/f'assets/{ns}/models/block/{item}.json').exists()),(topic,identifier)
    write_json(RES/'data/hk3gtl/research/research_icons.json',{'schema':1,
        '_comment':f'变更记录 #1 {STAMP.isoformat(timespec="seconds")} 修订75：100课题图标改用成果或解锁相关部件；不从支付材料取图标，不授予成果。', 'icons':icons})
    for language in ['zh_cn','en_us']:
        path=RES/f'assets/hk3gtl/lang/{language}.json'
        data=json.loads(path.read_text('utf-8'))
        zh=language=='zh_cn'
        for prefix in ['hk3gtl.research.terminal.','hk3gtl.research.lab.']:
            if prefix.endswith('terminal.'):
                data[prefix+'pointsButton']='使用研究点开始研究' if zh else 'Start With Points'
                data[prefix+'materialsButton']='使用材料开始研究' if zh else 'Start With Materials'
            else:
                data[prefix+'pay_points']='使用研究点开始研究' if zh else 'Start With Research Points'
                data[prefix+'pay_materials']='使用材料开始研究' if zh else 'Start With Materials'
        data['hk3gtl.research.terminal.time']='基础耗时：%s 秒   功率：%s' if zh else 'Base Time: %s s   Power: %s'
        data['hk3gtl.research.terminal.powerExact']='完整耗电量：%s EU/t' if zh else 'Exact Consumption: %s EU/t'
        data['hk3gtl.research.terminal.block.lab']='研究所阶级不足，请搭建“%s”阶研究所进行研究' if zh else 'Laboratory tier too low. Build a %s-tier laboratory to research this topic.'
        for i,label in enumerate(['一','二','三','四','五'],1):
            data['hk3gtl.research.lab.grade.'+str(i)]=label if zh else str(i)
        data['_comment_revision75']=f'变更记录 #1 {STAMP.isoformat(timespec="seconds")}：按钮使用开始研究；研究所不足带阶级参数；功率完整值移至悬停提示。'
        write_json(path,data)
    path=RES/'assets/hk3gtl/changelog.json'
    data=json.loads(path.read_text('utf-8'))
    data['entries'].insert(0,{'version':'0.5.0','revision':75,'codename':'HK3GTL-内测5',
        'date':STAMP.strftime('%Y-%m-%d'),'time':STAMP.strftime('%H:%M:%S'),
        'reason':'负责人要求研究UI功率摘要、具体阶级提示、按钮措辞和解锁成果图标。',
        'changes':['功率显示安培与电压缩写，完整EU/t仅悬停显示；不修改扣能数值。',
                   '阶级不足显示所需中文阶级，研究点与材料按钮改为开始研究。',
                   '100个课题接入独立成果图标目录，燃料调配图标为崩坏能燃料棒。',
                   '电路等级逐级交叠和动态tooltip方案正在按负责人确认讨论，尚不宣称已完成。']})
    write_json(path,data)
    print('100个图标覆盖与模型存在核对通过，中英文本更新完成。')


if __name__=='__main__':main()

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
