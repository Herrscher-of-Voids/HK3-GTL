import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0003_40台工业内容补全_20261119'
RECIPES, ITEMS, FLUIDS, LINKS = [], {}, {}, []
TIERS = {'I17': 17, 'I18': 15, 'I23': 20, 'I24': 20, 'I25': 21, 'I26': 22, 'I27': 23, 'I28': 23, 'I29': 24, 'I30': 24, 'I31': 24, 'I32': 19, 'I33': 20}
RESEARCH = {'I17': 'RN-CFR', 'I18': 'RN-FRP', 'I23': 'RN-PCE', 'I24': 'RN-QOM', 'I25': 'RN-WCP', 'I26': 'RN-UED', 'I27': 'RN-WBC', 'I28': 'RN-WTR', 'I29': 'RN-SWC', 'I30': 'RN-SWS', 'I31': 'RN-SWR', 'I32': 'RN-LTA', 'I33': 'RN-DKE'}
PALETTE = {'I17': 0x42C7D4, 'I18': 0xE6C455, 'I23': 0x58DDF4, 'I24': 0x927DE0, 'I25': 0x63B8F1, 'I26': 0xE8A346, 'I27': 0x8F64D8, 'I28': 0xC578A6, 'I29': 0x53BBA1, 'I30': 0x639FE1, 'I31': 0x96A9BE, 'I32': 0xDCB956, 'I33': 0xD99EDD}
BASE = ['gtceu:neutronium_plate', 'gtceu:transcendentmetal_ring', 'gtceu:cosmic_foil', 'gtceu:shirabon_foil', 'gtceu:carbon_nanotubes_foil', 'gtceu:polyetheretherketone_foil', 'gtceu:polybenzimidazole_foil', 'gtceu:fine_cosmicneutronium_wire', 'gtceu:neutronium_screw', 'gtceu:graphene_foil', 'gtceu:platinum_foil', 'gtceu:zirconium_carbide_plate']
MATERIALS = {
    'ceramic': ['gtceu:zirconium_carbide_plate', 'gtceu:hafnium_oxide_dust', 'gtceu:silicon_dioxide_dust', 'gtceu:polybenzimidazole_foil'],
    'thermal': ['gtceu:graphene_foil', 'gtceu:carbon_nanotubes_foil', 'gtceu:platinum_foil', 'gtceu:neutronium_plate'],
    'mechanical': ['gtceu:neutronium_plate', 'gtceu:transcendentmetal_ring', 'gtceu:cosmic_foil', 'gtceu:neutronium_screw'],
    'polymer': ['gtceu:polyetheretherketone_foil', 'gtceu:polybenzimidazole_foil', 'gtceu:fullerene_polymer_matrix_pulp_foil', 'gtceu:carbon_fiber_mesh'],
    'optical': ['gtceu:silicon_dioxide_dust', 'gtceu:gold_foil', 'gtceu:silver_foil', 'gtceu:hafnium_oxide_dust'],
    'recording': ['hk3gtl:soulium_data_substrate', 'gtceu:graphene_foil', 'gtceu:gold_foil', 'gtceu:polyetheretherketone_foil'],
    'magnetic': ['gtceu:shirabon_foil', 'gtceu:cosmicneutronium_foil', 'gtceu:fine_shirabon_wire', 'gtceu:carbon_nanotubes_foil'],
    'adsorption': ['gtceu:silicon_dioxide_dust', 'gtceu:carbon_nanotubes_dust', 'gtceu:platinum_foil', 'gtceu:palladium_foil'],
}
PROFILES = {
    'I17': ['adsorption', 'polymer', 'ceramic', 'magnetic'],
    'I18': ['ceramic', 'polymer', 'thermal', 'mechanical', 'thermal', 'ceramic'],
    'I24': ['optical', 'optical', 'mechanical', 'magnetic', 'adsorption', 'optical'],
    'I25': ['recording', 'recording', 'optical', 'magnetic', 'optical', 'recording'],
    'I26': ['ceramic', 'adsorption', 'polymer', 'mechanical', 'thermal', 'optical'],
    'I27': ['magnetic', 'polymer', 'adsorption', 'mechanical', 'mechanical', 'magnetic'],
    'I28': ['magnetic', 'thermal', 'adsorption', 'ceramic', 'polymer', 'mechanical'],
    'I29': ['ceramic', 'polymer', 'adsorption', 'magnetic', 'magnetic', 'recording'],
    'I30': ['polymer', 'thermal', 'polymer', 'magnetic', 'ceramic', 'recording'],
    'I31': ['recording', 'adsorption', 'ceramic', 'magnetic', 'recording', 'mechanical'],
    'I32': ['optical', 'recording', 'optical', 'recording', 'optical', 'recording'],
    'I33': ['mechanical', 'optical', 'magnetic', 'magnetic', 'magnetic', 'magnetic'],
}
BRANCHES = {}
INCOMING = {
    ('I25', 'navigation_frame'): ['bubble_parallax_navigation_catalog', 'bubble_lensing_correction_catalog'],
    ('I25', 'ephemeris'): ['bubble_temporal_navigation_standard', 'bubble_parallax_navigation_catalog'],
    ('I25', 'collision'): ['bubble_lensing_correction_catalog', 'bubble_tidal_hazard_atlas'],
    ('I25', 'anchor'): ['bubble_tidal_hazard_atlas', 'bubble_temporal_navigation_standard'],
    ('I25', 'return'): ['bubble_spectral_identity_catalog', 'bubble_lensing_correction_catalog'],
    ('I25', 'uncertainty'): ['bubble_background_rejection_pack', 'bubble_parallax_navigation_catalog'],
    ('I26', 'drone_cutting'): ['route_collision_avoidance_cartridge'],
    ('I26', 'sample_sorting'): ['bubble_spectral_identity_catalog'],
    ('I26', 'cargo'): ['route_reentry_guidance_cartridge'],
    ('I26', 'maintenance'): ['route_uncertainty_compensator'],
    ('I26', 'thermal'): ['bubble_tidal_hazard_atlas'],
    ('I26', 'telemetry'): ['route_ephemeris_memory'],
    ('I27', 'capture_field'): ['route_anchor_lock_cartridge'],
    ('I27', 'boundary'): ['bubble_tidal_hazard_atlas'],
    ('I27', 'vacuum'): ['bubble_spectral_identity_catalog'],
    ('I27', 'anchor_load'): ['route_uncertainty_compensator'],
    ('I27', 'closure'): ['bubble_temporal_navigation_standard'],
    ('I27', 'handover'): ['route_coordinate_frame_cartridge'],
    ('I28', 'termination_front'): ['capture_field_coupling_pack'],
    ('I28', 'quench'): ['capture_boundary_cushion'],
    ('I28', 'gas_capture'): ['capture_vacuum_guard_pack'],
    ('I28', 'debris_sorting'): ['capture_anchor_equalization_pack'],
    ('I28', 'residue'): ['capture_closure_seal_pack'],
    ('I28', 'container_release'): ['capture_handover_transfer_pack'],
    ('I29', 'lithosphere'): ['archive_material_compatibility_pack'],
    ('I29', 'hydrosphere'): ['archive_material_compatibility_pack'],
    ('I29', 'atmosphere'): ['bubble_spectral_identity_catalog'],
    ('I29', 'geomagnetic'): ['bubble_background_rejection_pack'],
    ('I29', 'topology'): ['bubble_lensing_correction_catalog'],
    ('I29', 'matter_balance'): ['archive_metrology_transfer_pack'],
    ('I30', 'tidal_damping'): ['simulated_topology_seed_pack'],
    ('I30', 'thermal_balance'): ['simulated_lithosphere_seed_pack'],
    ('I30', 'pressure_balance'): ['simulated_hydrosphere_cycle_pack', 'simulated_atmosphere_seed_pack'],
    ('I30', 'time_lock'): ['bubble_temporal_navigation_standard'],
    ('I30', 'radiation_balance'): ['simulated_geomagnetic_boundary_pack'],
    ('I30', 'anchor_feedback'): ['simulated_mass_balance_pack'],
    ('I31', 'state_checkpoint'): ['simulated_time_lock_pack'],
    ('I31', 'seed_extraction'): ['simulated_tidal_stabilization_pack'],
    ('I31', 'matter_fractions'): ['simulated_pressure_balance_pack'],
    ('I31', 'field_release'): ['simulated_radiation_balance_pack'],
    ('I31', 'traceability'): ['simulated_anchor_feedback_pack'],
    ('I31', 'container_reset'): ['simulated_thermal_balance_pack'],
}


def item(id, count=1):
    return {'id': id if ':' in id else 'hk3gtl:' + id, 'count': count}


def fluid(id, amount=1000):
    return {'id': id if ':' in id else 'hk3gtl:' + id, 'amount': amount}


def plan(role, id, title, ins, outs, fins=(), fouts=(), catalysts=(), research=(), ticks=1200, tier=None, power=None, purpose='', circuit=0):
    tier = TIERS[role] if tier is None else tier
    recipe = {'id': 'industrial_expansion_' + id, 'design_uid': 'EXP-WORLD:' + id, 'title': title, 'role': role,
              'requirements': list(research or [RESEARCH[role]]), 'item_inputs': list(ins), 'item_outputs': list(outs),
              'fluid_inputs': list(fins), 'fluid_outputs': list(fouts), 'item_catalysts': list(catalysts),
              'ticks': ticks, 'energy_tier': tier, 'stage_tier': tier, 'energy_direction': 'output' if role == 'I23' else 'input',
              'facts': [], 'required_facts': [], 'experiment': '', 'provisional': False, 'input_hw': 0,
              'network_credit': 0, 'circuit': circuit, 'purpose': purpose,
              'material_rule': '采用MAX以上原料和专用功能部件；后续整合件承接散件功能，非同产物材料替换配方。'}
    for key, quantity in [('item_inputs', 'count'), ('item_outputs', 'count'), ('item_catalysts', 'count'), ('fluid_inputs', 'amount'), ('fluid_outputs', 'amount')]:
        merged = {}
        for entry in recipe[key]:
            merged[entry['id']] = merged.get(entry['id'], 0) + entry[quantity]
        recipe[key] = [{'id': code, quantity: amount} for code, amount in merged.items()]
    recipe['output_eut' if role == 'I23' else 'input_eut'] = power or 30 * 4 ** (tier - 1)
    RECIPES.append(recipe)
    return recipe['id']


def asset(role, code, zh, purpose, liquid=False):
    en = code.replace('_', ' ').title()
    if liquid:
        color, temperature = PALETTE[role], 320
        for word, tone, heat in [('melt', 0xC78743, 1100), ('quench', 0x7DC7DA, 285), ('thermal', 0x669FD2, 360), ('resin', 0xBF9348, 335), ('sealant', 0xCBAD75, 330), ('lubricant', 0x817347, 305), ('ink', 0x465880, 300), ('recording', 0x738CC7, 300), ('wash', 0x66BBA9, 310), ('slurry', 0x829A9F, 325), ('sol', 0xA19BC2, 315), ('gel', 0x7FABBC, 310)]:
            if word in code:
                color, temperature = tone, heat
                break
        FLUIDS[code] = {'id': code, 'zh': zh, 'en': en, 'color': color, 'temperature': temperature, 'gas': False,
                        'purpose': purpose, 'appearance': '透明流体底纹，悬浮晶粒、层流条带和发光微粒分别绘制，使用' + zh + '对应的工业流体动画。'}
    else:
        shape = '多层薄片与边缘接触点' if any(t in code for t in ['foil', 'film', 'plate', 'mask', 'grating']) else '透明窗口内的晶体与金属封边' if any(t in code for t in ['lens', 'crystal', 'window', 'optical']) else '带插接头、固定螺钉及功能内芯的工业组件'
        ITEMS[code] = {'id': code, 'zh': zh, 'en': en, 'family': role, 'purpose': purpose,
                       'appearance': zh + '采用' + shape + '；以原生64×64像素表现实体结构，保留透明背景，功能内芯使用该机器支线配色。'}
    return code


def link(recipe, ids, reason, liquids=()):
    LINKS.append({'recipe_id': recipe, 'item_inputs': [item(id, 2) for id in ids],
                  'fluid_inputs': [fluid(id, 2000) for id in liquids], 'item_catalysts': [], 'reason': reason})


def chain(role, family, names, purpose, sink, mode='fabrication'):
    entries = [entry.split('=') for entry in names.split('|')]
    a, b, c, d, e = [asset(role, code, zh, purpose, index == 1) for index, (code, zh) in enumerate(entries)]
    branch = BRANCHES.get(role, 0)
    BRANCHES[role] = branch + 1
    process = PROFILES[role][branch]
    profile = MATERIALS[process]
    upstream = [item(code, 2) for code in INCOMING.get((role, family), [])]
    if mode == 'survey':
        upstream.append(item('world_mining_legacy_record' if role == 'I32' else 'spatial_probe', 1))
    description = purpose + '。'
    solid_feed = [item(raw, 256 if index == 0 else 128) for index, raw in enumerate(profile)]
    solid_feed += [item(code, 64) for code in ['gtceu:neutronium_screw', 'gtceu:transcendentmetal_ring', 'gtceu:fine_cosmicneutronium_wire'] if code not in profile]
    first_op = {'ceramic': '热压成形', 'thermal': '展热结构成形', 'mechanical': '精密结构成形', 'polymer': '层合成形', 'optical': '光学基准制造', 'recording': '基准存储器制造', 'magnetic': '磁路定向成形', 'adsorption': '孔径分级成形'}[process]
    plan(role, a, entries[0][1] + '：' + first_op, solid_feed, [item(a, 32)],
         [fluid('gtceu:soldering_alloy', 147456), fluid('gtceu:super_mutated_living_solder', 73728), fluid('gtceu:polyimide', 9216), fluid('gtceu:argon', 32000)], purpose=description, circuit=branch + 1)
    chemistry = [item(profile[1], 128), item(profile[2], 128), item('gtceu:carbon_nanotubes_dust', 128), item('hk3gtl:honkai_energy_crystal', 64)]
    plan(role, b, entries[1][1] + '：定向调制', chemistry, [],
         [fluid('hk3gtl:stabilized_liquid_honkai_energy', 16000), fluid('hk3gtl:soulium_process_solvent', 16000), fluid('hk3gtl:honkai_stabilization_medium', 8000), fluid('gtceu:helium', 32000)], [fluid(b, 32000)], [item(a)], purpose=description + '该支线专用基准件作为不消耗工装，控制孔径、表面结构或场域方向。')
    joining = [fluid('gtceu:soldering_alloy', 147456), fluid('gtceu:super_mutated_living_solder', 73728), fluid('gtceu:polyimide', 18432)]
    wiring = [item('gtceu:fine_cosmicneutronium_wire', 128), item('gtceu:polybenzimidazole_foil', 128), item('gtceu:neutronium_screw', 64)]
    if mode == 'survey':
        operation = {'I24': '多次观测曝光', 'I25': '航路约束映射', 'I31': '状态存储器写入', 'I32': '遗留实物光学解析'}[role]
        plan(role, c, entries[2][1] + '：' + operation,
             [item('hk3gtl:soulium_data_substrate', 32), item(profile[2], 128)] + upstream, [item(c, 16)],
             [fluid(b, 8000), fluid('hk3gtl:honkai_analysis_reagent', 4000), fluid('hk3gtl:honkai_coolant', 8000)],
             [fluid('hk3gtl:spent_analysis_reagent', 4000), fluid('hk3gtl:hot_honkai_coolant', 8000)], [item(a)], ticks=2400, purpose=description + '原始记录来自实际探针或遗留资料；读头与参考件重复使用。')
        plan(role, d, entries[3][1] + '：约束求解', [item(c, 16), item('hk3gtl:soulium_data_substrate', 16)] + wiring,
             [item(d, 8)], [fluid(b, 4000), fluid('hk3gtl:honkai_coolant', 4000)], [fluid('hk3gtl:hot_honkai_coolant', 4000)], [item(a)], ticks=3200, purpose=description + '对原始记录进行相位、误差和边界约束求解，输出后续可直接使用的索引。')
        plan(role, e, entries[4][1] + '：索引封装', [item(d, 8), item('hk3gtl:soulium_data_substrate', 16), item('gtceu:cosmic_foil', 128)] + wiring,
             [item(e, 8)], joining, [], [item(a)], ticks=2000, purpose=description + '封装已完成求解的索引，观测与读取仪器保留。')
    else:
        ctool = process in ['adsorption', 'magnetic']
        forming = {'ceramic': '浸渗烧结', 'thermal': '毛细浸润', 'mechanical': '精密结合', 'polymer': '界面涂覆', 'optical': '介电层沉积', 'recording': '存储层写入', 'magnetic': '场形印刻', 'adsorption': '选择吸附活化'}[process]
        cins = [item(profile[0], 64), item(profile[2], 128), item(profile[3], 128)] + upstream + ([] if ctool else [item(a, 8)])
        plan(role, c, entries[2][1] + '：' + forming, cins, [item(c, 16)],
             [fluid(b, 8000), fluid('gtceu:argon', 32000), fluid('hk3gtl:honkai_coolant', 8000)], [fluid('hk3gtl:hot_honkai_coolant', 8000)], [item(a)] if ctool else [], ticks=1600, purpose=description)
        dinputs = [item(c, 16), item(profile[1], 64)] + wiring
        if process in ['magnetic', 'adsorption', 'mechanical']:
            dinputs.append(item(a, 8))
        dfluids = [fluid(b, 8000)] + (joining if process in ['mechanical', 'magnetic', 'optical', 'recording'] else [fluid('hk3gtl:soulium_process_solvent', 16000), fluid('gtceu:argon', 32000)])
        dop = {'ceramic': '致密化连接', 'thermal': '热通道连通', 'mechanical': '承力预装', 'polymer': '受压共固化', 'optical': '光路对准', 'recording': '总线整合', 'magnetic': '回路对准', 'adsorption': '分级装填'}[process]
        plan(role, d, entries[3][1] + '：' + dop, dinputs, [item(d, 8)], dfluids,
             [], [item(a)] if process in ['ceramic', 'thermal', 'polymer', 'optical', 'recording'] else [], ticks=2000, purpose=description)
        eins = [item(d, 8), item('gtceu:transcendentmetal_ring', 64), item('gtceu:cosmic_foil', 128)] + wiring
        if process in ['thermal', 'polymer', 'ceramic', 'optical', 'recording']:
            eins.append(item(a, 4))
        plan(role, e, entries[4][1] + '：功能总装', eins, [item(e, 8)],
             [fluid(b, 4000)] + joining, [], [item(a)] if process in ['magnetic', 'adsorption'] else [], ticks=2400, purpose=description)
    if sink:
        link(sink, [e], purpose)
    return e


def main():
    # 每条支线均输出可接入既有生产的实际部件；观测支线使用仪器、耗材、记录和解算的不同执行方式。
    chain('I17', 'selective_fuel', 'fuel_pore_ceramic=燃料分级微孔陶瓷|fuel_selective_wash=燃料选择洗脱液|fuel_adsorption_pellet=燃料选择吸附颗粒|fuel_grade_equalizer=燃料品位均化芯|fuel_grade_conditioner=燃料分级调理包', '按吸附孔径分离燃料杂质，稳定高压燃料的品位与裂变活性', 'approved_energy_f02')
    chain('I17', 'volatile_control', 'fuel_vapor_baffle=燃料挥发隔板|fuel_devolatilizing_solution=燃料脱挥工作液|fuel_low_volatile_granule=低挥发燃料粒|fuel_gel_scaffold=燃料凝胶骨架|fuel_low_volatile_gel=低挥发燃料凝胶包', '脱除燃料中的挥发夹杂，减少高温相变时的气蚀和供料波动', 'approved_energy_f03')
    chain('I17', 'carbide_seed', 'fuel_carbide_seed_plate=燃料碳化成核板|fuel_carbidizing_sol=燃料碳化溶胶|fuel_carbide_kernel=碳化燃料微核|fuel_sintering_aid=燃料烧结助剂|fuel_carbide_precursor_pack=碳化燃料前驱包', '制备可烧结燃料微核，形成耐高热流的陶瓷燃料前驱', 'approved_energy_f04')
    chain('I17', 'phase_nucleation', 'fuel_phase_nucleation_mesh=燃料相成核网|fuel_phase_seeding_suspension=燃料相晶种悬液|fuel_phase_seed_crystal=燃料相晶种|fuel_phase_ordering_matrix=燃料相序基体|fuel_phase_lattice_seeding_pack=燃料相晶格播种包', '预置相变成核中心，使燃料能够按预定压力窗口释放能量', None)
    energy_lanes = [
        ('helium_brayton', '氦载崩坏布雷顿', 'gtceu:helium', 'hk3gtl:gaseous_honkai_energy', 'hk3gtl:spent_phase_modulation_medium', 1),
        ('argon_ion', '氩离子崩坏', 'gtceu:argon', 'hk3gtl:stabilized_liquid_honkai_energy', 'hk3gtl:spent_soulium_process_gas', 2),
        ('nitrogen_flash', '氮载闪蒸崩坏', 'gtceu:nitrogen', 'hk3gtl:liquid_honkai_fuel', 'hk3gtl:spent_honkai_stabilization_medium', 3),
        ('carbon_supercritical', '二氧化碳超临界崩坏', 'gtceu:carbon_dioxide', 'hk3gtl:supercritical_honkai_fuel', 'hk3gtl:fuel_refining_residual', 4),
        ('steam_honkai', '水蒸汽携能崩坏', 'gtceu:distilled_water', 'hk3gtl:concentrated_liquid_honkai_fuel', 'hk3gtl:spent_phase_modulation_medium', 2),
        ('hydrogen_resonant', '氢载谐振崩坏', 'gtceu:hydrogen', 'hk3gtl:resonance_activated_honkai_fuel', 'hk3gtl:spent_honkai_stabilization_medium', 4),
        ('helium_imaginary', '氦载虚数耦合', 'gtceu:helium', 'hk3gtl:imaginary_coupled_honkai_fuel', 'hk3gtl:spent_phase_modulation_medium', 6),
        ('argon_continuity', '氩载连续约束', 'gtceu:argon', 'hk3gtl:continuity_confined_honkai_fuel', 'hk3gtl:spent_world_stabilization_medium', 8),
        ('nitrogen_crystal', '氮载结晶升华', 'gtceu:nitrogen', 'hk3gtl:stabilized_liquid_honkai_energy', 'hk3gtl:crystallization_residual_liquid', 3),
        ('carbon_mixedphase', '二氧化碳混相分离', 'gtceu:carbon_dioxide', 'hk3gtl:concentrated_liquid_honkai_fuel', 'hk3gtl:fuel_refining_residual', 5),
    ]
    conditioners = ['fuel_grade_conditioner', 'fuel_low_volatile_gel', 'fuel_carbide_precursor_pack', 'fuel_phase_lattice_seeding_pack']
    for index, (code, zh, carrier, fuel, waste, grade) in enumerate(energy_lanes):
        feed = asset('I17', code + '_charged_working_medium', zh + '高压载能介质', 'I23高压膨胀的固定燃料首源；崩坏燃料和调理剂不可回收', True)
        expanded = asset('I23', code + '_expanded_stream', zh + '膨胀热流', '高压膨胀后继续驱动I23显热回收段', True)
        recuperated = asset('I23', code + '_recuperated_stream', zh + '回热湿流', '显热回收后进入I23冷凝回收段', True)
        lane_colors = [0x75DDE3, 0x9679DB, 0x6AA8D5, 0xA88D78, 0xBDD8E8, 0x80C9CF, 0xB18AE3, 0xCCAC6C, 0x8EC5C2, 0x87929C]
        for target, temperature in [(feed, 1600 + grade * 100), (expanded, 1200 + grade * 70), (recuperated, 850 + grade * 20)]:
            FLUIDS[target].update(color=lane_colors[index], temperature=temperature, gas=target != feed or code not in ['nitrogen_flash', 'carbon_supercritical', 'steam_honkai', 'carbon_mixedphase'])
            FLUIDS[target]['appearance'] = zh + '的独立动画材质；' + ('高压载能相显示密集相域与收缩的流动条纹。' if target == feed else '膨胀相显示沿流向拉长的细密粒子与疏密过渡。' if target == expanded else '回热湿流显示悬浮液滴和温差条带。') + '静止与流动分别绘制，避免复用同一底纹换色。'
        lane_research = ['RN-CFR', 'RN-PCE'] + (['RN-MRE'] if grade >= 4 else []) + (['RN-LRE', 'RN-SSQ'] if grade >= 6 else []) + (['RN-URE'] if grade >= 8 else [])
        plan('I17', feed, zh + '载能介质配制', [item(conditioners[index % 4], 8), item('hk3gtl:honkai_energy_crystal', 128 * grade), item('gtceu:carbon_nanotubes_dust', 128), item('gtceu:hafnium_oxide_dust', 128)], [],
             [fluid(carrier, 16000), fluid(fuel, 4000 * grade), fluid('hk3gtl:honkai_stabilization_medium', 8000), fluid('hk3gtl:soulium_process_solvent', 8000)], [fluid(feed, 16000)], ticks=2400,
             research=lane_research, purpose='消耗崩坏燃料注入能量，载气回收无法恢复燃料或结晶。')
        power = 128849018880 * grade
        plan('I23', code + '_pressure_expansion', zh + '高压膨胀发电', [], [], [fluid(feed, 16000)], [fluid(expanded, 16000)], research=lane_research, ticks=1600, power=power * 4, purpose='提取压力功；固定输出热流继续回收显热。')
        plan('I23', code + '_sensible_heat_recovery', zh + '显热回收发电', [], [], [fluid(expanded, 16000), fluid('hk3gtl:secondary_heat_transfer_medium', 8000)], [fluid(recuperated, 16000), fluid('hk3gtl:warm_secondary_heat_transfer_medium', 8000)], research=lane_research, ticks=1600, power=power, purpose='温差转换发电并向次级热回路传热；输出可继续冷凝的湿流。')
        plan('I23', code + '_condensation_recovery', zh + '冷凝回收发电', [item('hk3gtl:process_gas_filter', 1)], [item('hk3gtl:depleted_gas_filter', 1)], [fluid(recuperated, 16000), fluid('hk3gtl:honkai_coolant', 4000)],
             [fluid(carrier, 12000), fluid(waste, 4000), fluid('hk3gtl:hot_honkai_coolant', 4000)], research=lane_research, ticks=1600, power=power // 4, purpose='利用末端冷凝压差发电；只回收75%载气，崩坏燃料变为乏化介质。')

    chain('I18', 'cladding', 'fuel_cladding_billet=燃料包壳复合坯|fuel_cladding_bonding_sol=燃料包壳结合溶胶|fuel_diffusion_barrier_tube=燃料扩散阻挡管|fuel_cladding_laminate=燃料层压包壳|fuel_hermetic_cladding=燃料气密包壳总成', '阻止燃料向包壳迁移，并承担棒体内外压差', 'approved_hdv_p09')
    chain('I18', 'end_seal', 'fuel_endcap_seat=燃料端盖密封座|fuel_glass_ceramic_sealant=燃料玻璃陶瓷密封剂|fuel_welded_endcap=燃料焊封端盖|fuel_expansion_joint=燃料热胀补偿接头|fuel_sealed_endplug=燃料气密端塞', '端面封闭、热胀补偿及冷却通道隔离', 'industrial_dense_rod_encapsulation')
    chain('I18', 'heat_interface', 'fuel_heat_spreader_foil=燃料展热箔|fuel_thermal_contact_slurry=燃料热接触浆料|fuel_bonded_heat_sleeve=燃料结合展热套|fuel_radial_heat_bridge=燃料径向导热桥|fuel_heat_transfer_insert=燃料热传递内衬', '降低燃料芯与包壳之间的热阻，使棒体传热与燃料发热匹配', 'approved_hdv_p09')
    chain('I18', 'bundle_grid', 'fuel_bundle_grid_blank=燃料束架格栅坯|fuel_grid_infiltration_sol=燃料格栅浸渗溶胶|fuel_stiffened_grid=燃料增强格栅|fuel_bundle_crossbrace=燃料束架横撑|fuel_bundle_support_grid=燃料束定位格栅', '维持4连、8连和16连棒束间距并承受流致振动', 'approved_hdv_p09')
    chain('I18', 'flow_channel', 'fuel_flow_splitter_blank=燃料分流芯坯|fuel_flow_lining_slurry=燃料流道衬覆浆料|fuel_isolated_flow_channel=燃料隔离流道|fuel_axial_flow_header=燃料轴向流量汇管|fuel_coolant_distribution_insert=燃料冷却分配内件', '把冷却剂均匀分配至各燃料棒，保持束芯与束边的流动通道', 'industrial_dense_rod_encapsulation')
    chain('I18', 'neutron_shield', 'fuel_shield_ceramic_plate=燃料屏蔽陶瓷板|fuel_absorber_infiltration_medium=燃料吸收体浸渗液|fuel_neutron_absorber_tile=燃料中子吸收片|fuel_guard_cage=燃料外围护笼|fuel_guarded_encapsulation_pack=燃料封装防护包', '在封装与搬运中隔开燃料单元，减少外部辐射与机械冲击', 'industrial_dense_rod_encapsulation')

    chain('I24', 'stellar_parallax', 'bubble_stellar_baseline_rail=世界泡测距基线轨|bubble_parallax_recording_emulsion=世界泡视差记录乳液|bubble_parallax_interferogram=世界泡视差干涉片|bubble_parallax_baseline_solution=世界泡视差基线解|bubble_parallax_navigation_catalog=世界泡视差导航星表', '以重复视差观测约束世界泡距离和相对运动，供坐标解算使用', 'industrial_coordinate_solution', 'survey')
    chain('I24', 'spectral', 'bubble_spectral_reference_grating=世界泡光谱基准栅|bubble_spectral_recording_medium=世界泡光谱记录液|bubble_spectral_fingerprint_plate=世界泡光谱指纹片|bubble_spectral_discrimination_map=世界泡光谱辨识图|bubble_spectral_identity_catalog=世界泡光谱身份目录', '区分外观相近但物质组成不同的世界泡，防止航路误匹配', 'industrial_coordinate_solution', 'survey')
    chain('I24', 'tidal', 'bubble_tidal_differential_frame=世界泡潮汐差分架|bubble_tidal_tracing_medium=世界泡潮汐示踪液|bubble_tidal_strain_record=世界泡潮汐应变记录|bubble_tidal_boundary_map=世界泡潮汐边界图|bubble_tidal_hazard_atlas=世界泡潮汐危险图谱', '测量边界潮汐，提前标出探针和收容器需要避开的危险区', 'industrial_world_bubble_capture', 'survey')
    chain('I24', 'temporal', 'bubble_temporal_reference_cavity=世界泡时标参考腔|bubble_temporal_recording_medium=世界泡时差记录液|bubble_temporal_drift_record=世界泡时标漂移记录|bubble_temporal_correction_table=世界泡时标修正表|bubble_temporal_navigation_standard=世界泡航行时标基准', '把不同世界泡的观测时标换算为同一导航基准', 'industrial_coordinate_solution', 'survey')
    chain('I24', 'background', 'bubble_background_nulling_mesh=世界泡本底抵消网|bubble_background_capture_medium=世界泡本底捕获液|bubble_background_noise_record=世界泡本底噪声记录|bubble_background_subtraction_mask=世界泡本底扣除掩膜|bubble_background_rejection_pack=世界泡本底抑制包', '排除量子背景伪信号，减少坐标分析中的无效运算', 'industrial_coordinate_solution', 'survey')
    chain('I24', 'lensing', 'bubble_lensing_reference_array=世界泡透镜基准阵列|bubble_lensing_imprint_solution=世界泡透镜印迹液|bubble_lensing_distortion_plate=世界泡透镜畸变片|bubble_lensing_inverse_map=世界泡透镜逆映射|bubble_lensing_correction_catalog=世界泡透镜校正目录', '还原观测路径的空间畸变，提供可信的边界位置', 'industrial_coordinate_solution', 'survey')

    chain('I25', 'navigation_frame', 'route_orthogonal_reference_frame=航路正交参考架|route_coordinate_transfer_ink=航路坐标转移墨液|route_reference_grid_plate=航路参考网格片|route_frame_transform_matrix=航路参考系转换矩阵|route_coordinate_frame_cartridge=航路坐标参考匣', '把观测坐标转换成调度台和收容机共享的参考系', 'industrial_coordinate_solution', 'survey')
    chain('I25', 'ephemeris', 'route_orbit_reference_wheel=航路轨迹参考轮|route_ephemeris_recording_medium=航路星历记录液|route_orbit_fit_record=航路轨迹拟合记录|route_predictive_ephemeris=航路预测星历|route_ephemeris_memory=航路星历存储器', '预测世界泡在发射和抵达之间的位移，给无人载荷提供提前量', 'industrial_unmanned_mining_dispatch', 'survey')
    chain('I25', 'collision', 'route_clearance_reference_array=航路净空基准阵列|route_obstacle_mapping_medium=航路障碍测绘液|route_obstacle_voxel_record=航路障碍体素记录|route_clearance_corridor_map=航路净空走廊图|route_collision_avoidance_cartridge=航路避碰解算匣', '对航路净空和返航路径作空间约束，避免载荷在边界碰撞', 'industrial_unmanned_mining_dispatch', 'survey')
    chain('I25', 'anchor', 'route_anchor_alignment_cage=航路锚点对准笼|route_anchor_phase_ink=航路锚点相位墨液|route_anchor_interference_map=航路锚点干涉图|route_anchor_lock_solution=航路锚点锁定解|route_anchor_lock_cartridge=航路锚点锁定匣', '把收容器的锚点同步到目标边界，减少捕获时的相位偏差', 'industrial_world_bubble_capture', 'survey')
    chain('I25', 'return', 'route_reentry_reference_ring=航路重入参考环|route_reentry_trace_medium=航路重入示踪液|route_reentry_envelope_record=航路重入包络记录|route_reentry_window_map=航路重入窗口图|route_reentry_guidance_cartridge=航路重入制导匣', '保存可执行返航窗口与进入角，保证无人载荷可重复往返', 'industrial_unmanned_mining_dispatch', 'survey')
    chain('I25', 'uncertainty', 'route_covariance_reference_grid=航路协方差基准格|route_covariance_recording_medium=航路协方差记录液|route_error_distribution_plate=航路误差分布片|route_uncertainty_budget=航路不确定度预算表|route_uncertainty_compensator=航路误差补偿器', '把测量误差传播为可执行的修正量，限制各级锚点的误差累积', 'industrial_coordinate_solution', 'survey')

    chain('I26', 'drone_cutting', 'drone_cutter_carbide_blank=无人采掘碳化刀坯|drone_cutter_bonding_slurry=无人采掘刀具结合浆料|drone_cutter_diamond_edge=无人采掘金刚石刃|drone_cutter_balanced_head=无人采掘平衡刀头|drone_cutting_tool_cartridge=无人采掘切削刀匣', '在真正采掘前备齐钻切消耗件，采掘过程持续消耗刀匣', 'industrial_unmanned_mining_dispatch')
    chain('I26', 'sample_sorting', 'drone_sorter_microchannel_plate=无人分选微流道板|drone_sorter_separation_medium=无人分选介质|drone_sorter_polarized_mesh=无人分选极化筛|drone_sorter_density_stage=无人分选密度级联件|drone_mineral_sorting_pack=无人物料分选包', '对采得物作密度与电性分选，将混合矿物流整理成资源包', 'industrial_unmanned_mining_dispatch')
    chain('I26', 'cargo', 'drone_cargo_cell_frame=无人货舱隔室框|drone_cargo_sealant=无人货舱封装胶|drone_cargo_lined_cell=无人货舱衬覆隔室|drone_cargo_manifold=无人货舱集流件|drone_sealed_cargo_cassette=无人密封货运匣', '独立封装大量物品与流体，避免采掘载荷混装污染', 'industrial_unmanned_mining_dispatch')
    chain('I26', 'maintenance', 'drone_service_contact_board=无人维护接触板|drone_service_lubricant=无人维护润滑液|drone_service_actuator_sleeve=无人维护执行器护套|drone_service_repair_head=无人维护修复头|drone_field_maintenance_pack=无人现场维护包', '在采掘期间修复载荷接点与运动部件，消耗维护包承担磨损', 'industrial_unmanned_mining_dispatch')
    chain('I26', 'thermal', 'drone_thermal_spreader_grid=无人展热格栅|drone_thermal_interface_gel=无人热接触凝胶|drone_thermal_wick_plate=无人导热毛细板|drone_thermal_phase_reservoir=无人热缓冲储罐|drone_thermal_buffer_pack=无人热缓冲包', '吸收采掘切削与航行的短时热峰，把热量转交外部冷却回路', 'industrial_unmanned_mining_dispatch')
    chain('I26', 'telemetry', 'drone_telemetry_antenna_blank=无人遥测天线坯|drone_telemetry_dielectric_sol=无人遥测介电溶胶|drone_telemetry_patch_array=无人遥测贴片阵列|drone_telemetry_error_encoder=无人遥测纠错编码器|drone_navigation_telemetry_pack=无人导航遥测包', '在世界泡边界维持定位、资源识别及返航遥测数据', 'industrial_unmanned_mining_dispatch')

    chain('I27', 'capture_field', 'capture_field_return_yoke=世界泡捕获回磁轭|capture_field_imprint_medium=世界泡捕获场印刻液|capture_field_imprinted_laminate=世界泡捕获场层片|capture_field_flux_balancer=世界泡捕获磁通平衡器|capture_field_coupling_pack=世界泡捕获场耦合包', '将大型收容场耦合到可拆卸容器，抑制捕获瞬间的场强尖峰', 'industrial_world_bubble_capture')
    chain('I27', 'boundary', 'capture_boundary_reference_cage=世界泡边界参考笼|capture_boundary_wetting_medium=世界泡边界润湿液|capture_boundary_contact_film=世界泡边界接触膜|capture_boundary_transition_ring=世界泡边界过渡环|capture_boundary_cushion=世界泡捕获边界缓冲器', '让收容场缓慢贴合真实边界，避免对世界泡产生瞬间剪切', 'industrial_world_bubble_capture')
    chain('I27', 'vacuum', 'capture_vacuum_molecular_sieve=世界泡收容分子筛|capture_vacuum_getter_solution=世界泡收容吸气液|capture_vacuum_getter_panel=世界泡收容吸气板|capture_vacuum_isolation_valve=世界泡收容真空隔离阀|capture_vacuum_guard_pack=世界泡收容真空保护包', '捕集收容边界释放的杂质气体并分隔各真空段', 'industrial_world_bubble_capture')
    chain('I27', 'anchor_load', 'capture_anchor_tension_blank=世界泡锚点受拉坯|capture_anchor_infiltration_resin=世界泡锚点浸渗树脂|capture_anchor_composite_tendon=世界泡复合锚索|capture_anchor_load_splitter=世界泡锚点载荷分配器|capture_anchor_equalization_pack=世界泡锚点均载包', '让多根锚点分担不同方向的潮汐载荷，防止单点过载', 'industrial_world_bubble_capture')
    chain('I27', 'closure', 'capture_closure_iris_blank=世界泡收容光阑坯|capture_closure_boundary_gel=世界泡收口边界凝胶|capture_closure_segment=世界泡分瓣收口片|capture_closure_synchronizer=世界泡收口同步器|capture_closure_seal_pack=世界泡同步收口密封包', '在最后一段捕获中同步合拢容器开口并保留独立泄压通道', 'industrial_world_bubble_capture')
    chain('I27', 'handover', 'capture_handover_contact_ring=世界泡交接接触环|capture_handover_phase_medium=世界泡交接相位液|capture_handover_isolation_plate=世界泡交接隔离板|capture_handover_phase_lock=世界泡交接锁相件|capture_handover_transfer_pack=世界泡密封交接包', '把已收容世界泡从捕获场安全转移至终止回收或存储工位', 'industrial_world_bubble_capture')

    chain('I28', 'termination_front', 'real_termination_waveguide_blank=真实泡终止波导坯|real_termination_impedance_medium=真实泡终止阻抗液|real_termination_matched_waveguide=真实泡阻抗匹配波导|real_termination_pulse_distributor=真实泡终止脉冲分配器|real_termination_wavefront_pack=真实泡终止波前包', '把终止脉冲沿既定边界分配，避免局部过早坍缩', 'industrial_world_bubble_termination')
    chain('I28', 'quench', 'real_recovery_quench_mesh=真实泡回收急冷网|real_recovery_quench_sol=真实泡回收急冷溶胶|real_recovery_quench_tile=真实泡回收急冷片|real_recovery_quench_header=真实泡回收急冷汇管|real_recovery_quench_pack=真实泡终止急冷包', '在终止后吸收热峰，保护可回收容器和魂钢部件', 'industrial_world_bubble_termination')
    chain('I28', 'gas_capture', 'real_recovery_gas_separator_blank=真实泡回收气体分离坯|real_recovery_gas_trap_solution=真实泡回收捕气液|real_recovery_gas_sorbent=真实泡回收气体吸附芯|real_recovery_gas_manifold=真实泡回收气体汇管|real_recovery_gas_capture_pack=真实泡终止气体捕集包', '隔离终止放出的不同气体并接入既有废气处理', 'industrial_world_bubble_termination')
    chain('I28', 'debris_sorting', 'real_recovery_debris_screen_blank=真实泡回收碎片筛坯|real_recovery_density_medium=真实泡回收密度液|real_recovery_debris_classifier=真实泡回收碎片分类盘|real_recovery_debris_gate=真实泡回收碎片分流闸|real_recovery_debris_sorting_pack=真实泡终止碎片分选包', '按尺寸与密度分类容器残片，减少后续魂钢回收的杂质', 'industrial_world_bubble_termination')
    chain('I28', 'residue', 'real_recovery_residue_trap=真实泡回收残留捕集座|real_recovery_residue_binding_sol=真实泡回收残留结合液|real_recovery_residue_filter=真实泡回收残留滤片|real_recovery_residue_canister=真实泡回收残留封罐|real_recovery_residue_isolation_pack=真实泡终止残留隔离包', '固定不可回收残留，阻止其污染冷却剂和可回用结构件', 'industrial_world_bubble_termination')
    chain('I28', 'container_release', 'real_recovery_release_wedge=真实泡回收解锁楔|real_recovery_release_medium=真实泡回收脱模液|real_recovery_release_liner=真实泡回收脱模衬片|real_recovery_release_fixture=真实泡容器解锁夹具|real_recovery_container_release_pack=真实泡容器卸载包', '按顺序卸除容器内应力，使残骸能够进入无源拆解和材料回收', 'industrial_world_bubble_termination')

    chain('I29', 'lithosphere', 'simulated_lithosphere_seed_mesh=模拟世界岩层晶种网|simulated_lithosphere_nutrient_melt=模拟世界岩层营养熔液|simulated_lithosphere_growth_tile=模拟世界岩层生长片|simulated_lithosphere_layer_cartridge=模拟世界分层地壳匣|simulated_lithosphere_seed_pack=模拟世界岩层播种包', '为模拟世界配置具有层次和物质守恒的岩层底材', 'industrial_simulated_world_construction')
    chain('I29', 'hydrosphere', 'simulated_hydrosphere_osmotic_mesh=模拟世界水圈渗透网|simulated_hydrosphere_buffer_solution=模拟世界水圈缓冲液|simulated_hydrosphere_reservoir_cell=模拟世界水圈蓄液格|simulated_hydrosphere_circulation_node=模拟世界水圈循环节点|simulated_hydrosphere_cycle_pack=模拟世界水圈循环包', '预置水量、盐度和相变条件，形成可维持的水循环', 'industrial_simulated_world_construction')
    chain('I29', 'atmosphere', 'simulated_atmosphere_exchange_lattice=模拟世界大气交换格|simulated_atmosphere_precursor_mix=模拟世界大气前驱混合液|simulated_atmosphere_gas_exchange_film=模拟世界大气交换膜|simulated_atmosphere_composition_node=模拟世界大气组分节点|simulated_atmosphere_seed_pack=模拟世界大气播种包', '给模拟世界设置可计算的大气组分及边界交换条件', 'industrial_simulated_world_construction')
    chain('I29', 'geomagnetic', 'simulated_geomagnetic_seed_yoke=模拟世界磁场晶种轭|simulated_geomagnetic_domain_sol=模拟世界磁畴溶胶|simulated_geomagnetic_ordered_tile=模拟世界磁畴有序片|simulated_geomagnetic_return_core=模拟世界磁通回路芯|simulated_geomagnetic_boundary_pack=模拟世界磁场边界包', '构造闭合磁通及辐射屏蔽边界，降低后续稳定负担', 'industrial_simulated_world_construction')
    chain('I29', 'topology', 'simulated_topology_reference_mesh=模拟世界拓扑参考网|simulated_topology_imprint_medium=模拟世界拓扑印刻液|simulated_topology_mapped_plate=模拟世界拓扑映射板|simulated_topology_boundary_stitch=模拟世界边界缝合件|simulated_topology_seed_pack=模拟世界拓扑播种包', '规定内部连通关系与外界边界，避免生成彼此重叠的空间', 'industrial_simulated_world_construction')
    chain('I29', 'matter_balance', 'simulated_mass_reference_cell=模拟世界质量基准格|simulated_mass_buffer_suspension=模拟世界质量缓冲悬液|simulated_mass_balancing_pellet=模拟世界质量平衡粒|simulated_mass_budget_register=模拟世界质量预算寄存器|simulated_mass_balance_pack=模拟世界质量平衡包', '记录并限制初始物质投入，给后续终止回收保留完整质量预算', 'industrial_simulated_world_construction')

    chain('I30', 'tidal_damping', 'simulated_tidal_damper_blank=模拟世界潮汐阻尼坯|simulated_tidal_damping_gel=模拟世界潮汐阻尼凝胶|simulated_tidal_shear_pad=模拟世界潮汐剪切垫|simulated_tidal_damper_array=模拟世界潮汐阻尼阵列|simulated_tidal_stabilization_pack=模拟世界潮汐稳定包', '衰减边界剪切与周期潮汐，减少锚点疲劳', 'industrial_simulated_world_stabilization')
    chain('I30', 'thermal_balance', 'simulated_thermal_reference_lattice=模拟世界热基准格|simulated_thermal_phase_buffer=模拟世界热相缓冲液|simulated_thermal_capillary_panel=模拟世界热毛细板|simulated_thermal_equalizer=模拟世界温差均衡器|simulated_thermal_balance_pack=模拟世界热平衡包', '在边界上搬运热量，平衡模拟世界不同区域的热负荷', 'industrial_simulated_world_stabilization')
    chain('I30', 'pressure_balance', 'simulated_pressure_reference_cell=模拟世界压力基准格|simulated_pressure_transfer_medium=模拟世界压力传递液|simulated_pressure_compensation_film=模拟世界压力补偿膜|simulated_pressure_equalizer=模拟世界压力均衡器|simulated_pressure_balance_pack=模拟世界压差平衡包', '控制内部气液压差，避免水圈与大气圈互相失稳', 'industrial_simulated_world_stabilization')
    chain('I30', 'time_lock', 'simulated_time_reference_cavity=模拟世界时标参考腔|simulated_time_phase_recording_medium=模拟世界时标相位液|simulated_time_drift_plate=模拟世界时标漂移板|simulated_time_feedback_oscillator=模拟世界时标反馈振荡器|simulated_time_lock_pack=模拟世界时标锁定包', '把局部演化时标锁定到主控时间，保证停止与回收可预测', 'industrial_simulated_world_stabilization')
    chain('I30', 'radiation_balance', 'simulated_radiation_absorber_blank=模拟世界辐射吸收坯|simulated_radiation_trapping_sol=模拟世界辐射俘获溶胶|simulated_radiation_shield_tile=模拟世界辐射屏蔽片|simulated_radiation_return_array=模拟世界辐射回流阵列|simulated_radiation_balance_pack=模拟世界辐射平衡包', '限制边界辐射泄漏，并把吸收的能量送回热管理回路', 'industrial_simulated_world_stabilization')
    chain('I30', 'anchor_feedback', 'simulated_anchor_feedback_frame=模拟世界锚点反馈框|simulated_anchor_response_medium=模拟世界锚点响应液|simulated_anchor_strain_sensor=模拟世界锚点应变传感片|simulated_anchor_feedback_controller=模拟世界锚点反馈控制器|simulated_anchor_feedback_pack=模拟世界锚点反馈包', '根据真实边界应变调节各锚点的相位与受力', 'industrial_simulated_world_stabilization')

    chain('I31', 'state_checkpoint', 'simulated_state_checkpoint_substrate=模拟世界状态检查点基底|simulated_state_recording_medium=模拟世界状态记录液|simulated_state_snapshot_plate=模拟世界状态快照片|simulated_state_index_memory=模拟世界状态索引器|simulated_state_checkpoint_pack=模拟世界状态保存包', '终止前保存物质分布和边界状态，供工程分析和下一次播种使用', 'industrial_simulated_world_termination', 'survey')
    chain('I31', 'seed_extraction', 'simulated_seed_extraction_screen=模拟世界晶种提取筛|simulated_seed_separation_medium=模拟世界晶种分离液|simulated_seed_capture_cell=模拟世界晶种捕获格|simulated_seed_identity_register=模拟世界晶种身份寄存器|simulated_seed_recovery_pack=模拟世界晶种回收包', '从终止物质中隔离可回用晶种，同时记录晶种来源', 'industrial_simulated_world_termination')
    chain('I31', 'matter_fractions', 'simulated_matter_fractionation_plate=模拟世界物质分馏板|simulated_matter_partition_medium=模拟世界物质分配液|simulated_matter_fractionation_cell=模拟世界物质分馏格|simulated_matter_classification_node=模拟世界物质分类节点|simulated_matter_recovery_pack=模拟世界物质回收包', '依照构造时的质量预算分类返还物质，控制混合残留', 'industrial_simulated_world_termination')
    chain('I31', 'field_release', 'simulated_field_release_yoke=模拟世界释场轭|simulated_field_quench_medium=模拟世界释场急冷液|simulated_field_release_coil=模拟世界释场线圈|simulated_field_energy_bleeder=模拟世界场能释放器|simulated_field_release_pack=模拟世界释场控制包', '按可控顺序卸去边界场，防止残余场能冲击主机', 'industrial_simulated_world_termination')
    chain('I31', 'traceability', 'simulated_recovery_provenance_substrate=模拟世界回收溯源基底|simulated_recovery_labeling_ink=模拟世界回收标记墨液|simulated_recovery_provenance_plate=模拟世界回收溯源片|simulated_recovery_mass_register=模拟世界回收质量寄存器|simulated_recovery_traceability_pack=模拟世界回收溯源包', '逐批比对构造投入和终止产出，让同一晶种的再利用保持可追溯', 'industrial_simulated_world_termination', 'survey')
    chain('I31', 'container_reset', 'simulated_container_reset_fixture=模拟世界容器复位夹具|simulated_container_cleaning_medium=模拟世界容器清洗液|simulated_container_reset_liner=模拟世界容器复位衬片|simulated_container_stress_equalizer=模拟世界容器应力均衡器|simulated_container_reset_pack=模拟世界容器复位包', '卸除容器剩余应力并清除上次世界的残留，供既有材料回收线拆解', 'industrial_simulated_world_termination')

    chain('I32', 'ship_archive', 'ship_archive_optical_reader=舰船档案光学读头|ship_archive_development_medium=舰船档案显影液|ship_archive_structural_record=舰船结构记录片|ship_archive_assembly_index=舰船总装索引|ship_archive_reconstruction_pack=舰船档案重建包', '把真实采掘遗留工程资料转换为可复制的舰船图纸索引', 'industrial_ship_blueprint_copy', 'survey')
    chain('I32', 'metrology_archive', 'archive_metrology_reference_plate=工程档案计量基准片|archive_metrology_recording_medium=工程档案计量记录液|archive_metrology_trace_plate=工程档案计量溯源片|archive_metrology_tolerance_atlas=工程档案公差图谱|archive_metrology_transfer_pack=工程计量传递包', '为遗留实物的逆向解析保存计量基准与装配公差', 'industrial_reverse_engineering_specimen', 'survey')
    chain('I32', 'material_archive', 'archive_material_diffraction_holder=工程档案材料衍射座|archive_material_development_medium=工程档案材料显影液|archive_material_diffraction_plate=工程档案材料衍射片|archive_material_phase_atlas=工程档案材料相图|archive_material_compatibility_pack=工程材料相容性档案包', '记录高阶材料的晶相、扩散和热胀相容性，服务高阶总装', 'industrial_reverse_engineering_specimen', 'survey')
    chain('I32', 'process_archive', 'archive_process_trace_reader=工程档案工艺轨迹读头|archive_process_trace_ink=工程档案工艺轨迹墨液|archive_process_trace_plate=工程档案工艺轨迹片|archive_process_dependency_index=工程档案工艺依赖索引|archive_process_transfer_pack=工程工艺转移档案包', '把多步前驱生产的装配关系整理为可重用的工艺档案', 'industrial_reverse_engineering_specimen', 'survey')
    chain('I32', 'spatial_archive', 'archive_spatial_reference_reader=工程档案空间基准读头|archive_spatial_mapping_medium=工程档案空间映射液|archive_spatial_boundary_record=工程档案空间边界记录|archive_spatial_interface_index=工程档案空间接口索引|archive_spatial_interface_pack=工程空间接口档案包', '统一遗留技术三域差分分析中的空间接口与观测基准', 'industrial_three_domain_difference', 'survey')
    chain('I32', 'containment_archive', 'archive_containment_trace_reader=工程档案收容轨迹读头|archive_containment_recording_medium=工程档案收容记录液|archive_containment_boundary_plate=工程档案收容边界片|archive_containment_load_atlas=工程档案收容载荷图谱|archive_containment_design_pack=工程收容设计档案包', '把实际边界观测与结构载荷合并，用于矛盾源取样的收容校准', 'industrial_contradictory_source_sampling', 'survey')

    chain('I33', 'key_shell', 'divine_key_shell_blank=仿制神之键壳坯|divine_key_shell_bonding_sol=仿制神之键壳体结合液|divine_key_shell_laminate=仿制神之键层合壳片|divine_key_shell_stress_frame=仿制神之键应力框|divine_key_integrated_shell_pack=仿制神之键壳体总成包', '将高阶层片与承力框组合成能够容纳仿制核心的封闭壳体', 'industrial_key_housing')
    chain('I33', 'void_archive', 'void_archive_prism_blank=虚空档案棱镜坯|void_archive_phase_writing_medium=虚空档案相位写入液|void_archive_encoded_prism=虚空档案编码棱镜|void_archive_index_cage=虚空档案索引笼|void_archive_indexing_pack=虚空万藏索引总成包', '完成仿制虚空万藏的编码载体、索引及外部读取接口', 'industrial_imitation_void_archives')
    chain('I33', 'eden_gravity', 'eden_gravity_return_yoke=伊甸重力回路轭|eden_gravity_imprint_medium=伊甸重力印刻液|eden_gravity_pole_segment=伊甸重力极段|eden_gravity_balancing_cage=伊甸重力平衡笼|eden_gravity_focus_pack=伊甸重力聚焦总成包', '把岩之仿制核心的输出约束到可控焦点，服务仿制伊甸之星', 'industrial_imitation_star_of_eden')
    chain('I33', 'judah_binding', 'judah_binding_chain_blank=犹大约束链坯|judah_binding_domain_medium=犹大约束域介质|judah_binding_anchor_link=犹大约束锚链节|judah_binding_field_cage=犹大约束场笼|judah_binding_domain_pack=犹大约束域总成包', '将约束作用分布到多个锚点，使仿制犹大的誓约能够形成稳定作用域', 'industrial_imitation_oath_of_judah')
    chain('I33', 'spatial_interface', 'divine_spatial_interface_blank=神之键空间接口坯|divine_spatial_interface_imprint_medium=神之键空间接口印刻液|divine_spatial_interface_window=神之键空间接口窗|divine_spatial_phase_aligner=神之键空间相位对准器|divine_spatial_interface_pack=神之键空间接口总成包', '对齐空间模块与仿制核心的相位边界，接入世界泡收容容器', 'approved_imv_g04')
    chain('I33', 'termination_charge', 'bubble_charge_pulse_liner=世界泡终止药包脉冲衬片|bubble_charge_phase_binding_medium=世界泡终止药包相位结合液|bubble_charge_shaped_waveguide=世界泡终止药包成形波导|bubble_charge_synchronized_trigger=世界泡终止药包同步触发器|bubble_charge_pulse_control_pack=世界泡终止药包脉冲控制包', '使终止药包按设计波前触发，保留可控的脉冲宽度与分配顺序', 'approved_imv_g06')

    OUT.mkdir(parents=True, exist_ok=True)
    additional = {}
    for entry in LINKS:
        inputs = additional.setdefault(entry['recipe_id'], {'item_inputs': [], 'fluid_inputs': [], 'item_catalysts': []})
        for key in inputs:
            inputs[key].extend(entry[key])
    (ROOT / 'src/main/resources/data/hk3gtl/research/industrial_expansion_world_processes.json').write_text(json.dumps({'schema': 1, 'revision': '2026-11-19', 'recipes': RECIPES, 'additional_inputs': additional}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (OUT / 'world-assets.json').write_text(json.dumps({'items': list(ITEMS.values()), 'fluids': list(FLUIDS.values())}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (OUT / 'world-links.json').write_text(json.dumps(LINKS, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'recipes': len(RECIPES), 'items': len(ITEMS), 'fluids': len(FLUIDS), 'links': len(LINKS)}))


if __name__ == '__main__':
    main()
