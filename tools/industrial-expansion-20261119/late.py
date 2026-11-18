import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
DELIVERY = ROOT / 'deliveries/0003_40台工业内容补全_20261119'
RECIPES, ITEMS, FLUIDS, LINKS = [], {}, {}, []
ROLE, TIER, RESEARCH, FAMILY, COLOR = '', 0, '', '', ''


def configure(role, tier, research, family, color):
    global ROLE, TIER, RESEARCH, FAMILY, COLOR
    ROLE, TIER, RESEARCH, FAMILY, COLOR = role, tier, research, family, color


def entries(values, fluid=False):
    result = []
    for token in values.split():
        name, count = token.rsplit('@', 1)
        if ':' not in name:
            name = 'hk3gtl:' + name
        result.append({'id': name, 'amount' if fluid else 'count': int(count)})
    return result


def recipe(key, title, inputs='', outputs='', fluid_inputs='', fluid_outputs='', catalysts='', ticks=1200, purpose=''):
    item_inputs, item_outputs = entries(inputs), entries(outputs)
    fluid_in, fluid_out = entries(fluid_inputs, True), entries(fluid_outputs, True)
    RECIPES.append(dict(id='industrial_expansion_' + key, design_uid='EX-' + ROLE + '-' + key,
        title=title, role=ROLE, requirements=[RESEARCH], item_inputs=item_inputs, item_outputs=item_outputs,
        fluid_inputs=fluid_in, fluid_outputs=fluid_out, item_catalysts=entries(catalysts), ticks=ticks,
        energy_tier=TIER, stage_tier=TIER, energy_direction='input', input_eut=0, input_hw=0,
        facts=[], required_facts=[], experiment='', provisional=False, network_credit=0, circuit=0,
        industrial_purpose=purpose))


def part(key, name, inputs, fluids='', purpose='', shape='', count=4, waste='', fluid_waste='', catalysts='', ticks=1200):
    ITEMS[key] = dict(id=key, zh=name, en=key.replace('_', ' ').title(), family=FAMILY,
        purpose=purpose, appearance=f'原生64×64透明像素图，{COLOR}工业金属与崩坏能光路，{shape}，禁止文字、纯色块和缩放旧图',
        raw_materials=entries(inputs) + entries(fluids, True), downstream=[])
    recipe(key, name, inputs, f'{key}@{count} {waste}', fluids, fluid_waste, catalysts, ticks, purpose)


def liquid(key, name, color, inputs='', fluids='', purpose='', output=4000, waste='', temperature=300):
    FLUIDS[key] = dict(id=key, zh=name, en=key.replace('_', ' ').title(), color=color,
        temperature=temperature, purpose=purpose,
        appearance=f'原生64×64流动纹理，{COLOR}底色中的分层旋涡、反光与微粒，不使用纯色块',
        raw_materials=entries(inputs) + entries(fluids, True), downstream=[])
    recipe(key, name, inputs, waste, fluids, f'{key}@{output}', ticks=800, purpose=purpose)


def fluid_asset(key, name, color, purpose, temperature=300):
    FLUIDS[key] = dict(id=key, zh=name, en=key.replace('_', ' ').title(), color=color,
        temperature=temperature, purpose=purpose,
        appearance=f'原生64×64流动纹理，{COLOR}分层旋涡与{purpose}对应的悬浮颗粒，不使用纯色块',
        raw_materials=[], downstream=[])


def output_asset(key, name, purpose, shape):
    ITEMS[key] = dict(id=key, zh=name, en=key.replace('_', ' ').title(), family=FAMILY,
        purpose=purpose, appearance=f'原生64×64透明像素图，{COLOR}工业金属与崩坏能光路，{shape}，禁止文字、纯色块和缩放旧图',
        raw_materials=[], downstream=[])


def link(recipe_id, inputs='', fluids='', catalysts='', reason=''):
    LINKS.append(dict(recipe_id=recipe_id, item_inputs=entries(inputs), fluid_inputs=entries(fluids, True),
        item_catalysts=entries(catalysts), reason=reason))


def parts(rows):
    for key, name, inputs, fluids, purpose, shape in rows:
        part(key, name, inputs, fluids, purpose, shape)


def write():
    DELIVERY.mkdir(parents=True, exist_ok=True)
    base = ROOT / 'src/main/resources/data/hk3gtl/research'
    old = {}
    for name in ['industrial_processes.json', 'approved_industrial_processes.json']:
        old.update({row['id']: row for row in json.loads((base / name).read_text(encoding='utf-8'))['recipes']})
    for asset in list(ITEMS.values()) + list(FLUIDS.values()):
        source = [row for row in RECIPES if any(value['id'] == 'hk3gtl:' + asset['id']
            for field in ['item_outputs', 'fluid_outputs'] for value in row[field])]
        asset['source_recipes'] = [row['id'] for row in source]
        asset['source_machine'] = source[0]['role']
        asset['source_research'] = source[0]['requirements']
        if not asset['raw_materials']:
            asset['raw_materials'] = source[0]['item_inputs'] + source[0]['fluid_inputs']
    for source in RECIPES + LINKS:
        for field in ['item_inputs', 'item_catalysts', 'fluid_inputs']:
            for value in source.get(field, []):
                key = value['id'].removeprefix('hk3gtl:')
                target = ITEMS.get(key) or FLUIDS.get(key)
                if target:
                    target['downstream'].append(source.get('id', source.get('recipe_id')))
    additional = {}
    for source in LINKS:
        key = source['recipe_id']
        target = additional.setdefault(key, dict(item_inputs=[], fluid_inputs=[], item_catalysts=[]))
        for field in target:
            target[field].extend(source[field])
        source['before'] = {field: old[key][field] for field in target}
        source['after'] = {field: old[key][field] + additional[key][field] for field in target}
    files = {
        ROOT / 'src/main/resources/data/hk3gtl/research/industrial_expansion_late_processes.json': dict(schema=1, source='0003工业链内容补全20261119', recipes=RECIPES, additional_inputs=additional),
        DELIVERY / 'late-assets.json': dict(items=list(ITEMS.values()), fluids=list(FLUIDS.values())),
        DELIVERY / 'late-links.json': LINKS,
    }
    for path, data in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(recipes=dict(Counter(row['role'] for row in RECIPES)), items=len(ITEMS), fluids=len(FLUIDS), links=len(LINKS)), ensure_ascii=False))


configure('I34', 25, 'RN-IOP', 'imaginary_observation', '紫银与青蓝')
fluid_asset('spent_tree_optical_polish', '废虚数观测抛光悬液', '695978', '收集光窗磨屑后经分离恢复抛光液')
liquid('tree_optical_polish', '虚数观测抛光悬液', '9B73DC', 'gtceu:diamond_dust@64 gtceu:cerium_oxide_dust@128', 'gtceu:distilled_water@16000 soulium_process_solvent@4000', '在不损伤魂钢光窗的条件下去除亚表面缺陷', 16000)
part('tree_silica_blank', '观测级石英光坯', 'gtceu:quartzite_dust@256 gtceu:boron_dust@16', 'gtceu:argon@8000', '观测透镜与光纤的共同实体原料', '带磨削余量的六棱透明坯体', 16)
part('tree_window_substrate', '魂钢光窗基片', 'tree_silica_blank@8 soulium_data_substrate@8', 'tree_optical_polish@1000', '承受虚数侧压差并透过观测波段', '银框夹持的紫色椭圆光窗', 4, 'soulium_swarf@2', 'spent_tree_optical_polish@1000')
part('tree_dichroic_coating', '虚数双色介质膜', 'gtceu:titanium_dust@64 gtceu:silicon_dioxide_dust@128 gtceu:hafnium_dust@32', 'gtceu:oxygen@8000', '分开参考光与虚数观测光', '蓝紫交替的多层光学薄膜', 16)
part('tree_spectral_splitter', '树枝光谱分束棱镜', 'tree_silica_blank@4 tree_dichroic_coating@8 gtceu:osmium_foil@32', 'tree_optical_polish@1000', '将树枝投影拆为可测的波段', '带银色固定座的三角分光棱镜', 4)
part('tree_coherent_fiber', '相干观测光纤束', 'tree_silica_blank@8 gtceu:polyetheretherketone_foil@64 gtceu:graphene_foil@64', 'gtceu:helium@4000', '在远端探头和接收器之间保持相位', '弯曲束状青蓝光纤及金属端口', 8)
part('tree_athermal_spacer', '无热漂观测隔圈', 'material:soulium/plate@16 gtceu:invar_plate@64 gtceu:carbon_fiber_plate@32', 'soulium_protective_gas@4000', '抵消长时间曝光造成的光程漂移', '镂空蜂窝环及三点支承', 8, 'soulium_swarf@2')
part('tree_balanced_receiver', '平衡式虚数光接收器', 'tree_window_substrate@2 tree_spectral_splitter@2 soulium_data_substrate@8 circuit_encapsulation_part@8', 'gtceu:soldering_alloy@4608', '同时读取观测光和参考光并扣除共同噪声', '左右双光窗的对称接收头', 4)
part('tree_reference_laser', '观测参考激光头', 'tree_dichroic_coating@8 gtceu:diamond_lens@8 gtceu:niobium_titanium_single_wire@64 soulium_data_substrate@8', 'gtceu:soldering_alloy@4608', '为干涉测距提供已知频率', '银色圆筒带紫色激光窗口', 4)
part('tree_delay_spool', '可变光程延迟盘', 'tree_coherent_fiber@8 tree_athermal_spacer@2 gtceu:neutronium_ring@32', 'stable_transport_medium@1000', '将未知空间延迟转换为可测相位', '盘绕光纤和双侧步进支架', 4)
part('tree_phase_comparator', '树枝相位比较器', 'tree_balanced_receiver@2 tree_reference_laser@1 etched_circuit_layer@16 gtceu:gold_foil@128', 'gtceu:soldering_alloy@4608', '输出相对相位并驱动光程伺服', '带双输入插座的紫色电路盒', 4)
part('tree_aperture_rotor', '虚数视场选通转盘', 'material:soulium/plate@32 gtceu:neutronium_ring@32 gtceu:diamond_dust@64', 'tree_optical_polish@1000', '物理屏蔽相邻树枝的串光', '六孔转盘与蓝紫遮光刃口', 4, 'soulium_swarf@4')
part('tree_parallax_bench', '树枝视差测量基座', 'tree_athermal_spacer@4 tree_balanced_receiver@2 tree_aperture_rotor@2 soulium_anchor_component@4', 'gtceu:polyimide@4608', '固定两组探测器的空间基线', '成对光学滑台和长形基梁', 4)
part('tree_polarization_gate', '偏振隔离选通器', 'tree_spectral_splitter@2 tree_dichroic_coating@4 gtceu:magnetic_neodymium_rod@32', 'soulium_process_solvent@1000', '阻止虚数回波反射进入参考光源', '交叉晶片与磁极夹持环', 4)
part('tree_wavefront_actuator', '观测波前校正镜组', 'tree_window_substrate@4 tree_phase_comparator@2 gtceu:platinum_foil@64 gtceu:graphene_foil@64', 'gtceu:polyimide@2304', '补偿观测界面造成的波前弯曲', '多块六边形银镜组成的镜阵', 4)
part('tree_shot_noise_filter', '光子散粒噪声滤波板', 'soulium_data_substrate@16 etched_circuit_layer@16 gtceu:fine_niobium_titanium_wire@64', 'gtceu:soldering_alloy@4608', '将接收器输出变为可积分的测量信号', '分区屏蔽的双通道电路板', 4)
part('tree_clock_distributor', '观测同步时钟分配器', 'tree_phase_comparator@2 tree_shot_noise_filter@2 circuit_encapsulation_part@16 gtceu:niobium_titanium_single_wire@64', 'gtceu:soldering_alloy@4608', '让远端观测头共享同一采样时刻', '四面时钟插座和中央晶体', 4)
part('tree_aberration_cartridge', '树枝像差补偿镜筒', 'tree_wavefront_actuator@2 tree_polarization_gate@2 tree_delay_spool@2 tree_athermal_spacer@4', 'stable_transport_medium@1000', '以镜组和光程补偿代替逐次人工调节', '可拆卸长镜筒和补偿旋钮', 2)
part('tree_triangulation_head', '虚数三角测距探头', 'tree_parallax_bench@2 tree_reference_laser@2 tree_phase_comparator@4 spatial_probe@2', 'gtceu:polyimide@4608', '为跨界航路提供可追溯距离', '三角框架中的三枚测距镜头', 2)
part('tree_spectral_imager', '树枝多谱成像头', 'tree_balanced_receiver@4 tree_spectral_splitter@4 tree_shot_noise_filter@4 tree_aperture_rotor@2', 'soulium_protective_gas@2000', '识别不同树枝的稳定观测波段', '四波段排列的紧凑成像盒', 2)
part('tree_drift_compensator', '观测基线漂移补偿器', 'tree_clock_distributor@2 tree_delay_spool@2 tree_wavefront_actuator@2 spatial_calibration_module@2', 'gtceu:soldering_alloy@4608', '在长周期观测中实时调整参考光程', '环形光纤和侧置伺服电路', 2)
part('tree_observation_cassette', '虚数树观测光学匣', 'tree_aberration_cartridge@2 tree_spectral_imager@2 tree_drift_compensator@2 soulium_data_substrate@16', 'honkai_stabilization_medium@2000', '作为树观测实验消耗的完整光学匣', '抽屉式光学匣和三条观测窗口', 2)
part('tree_branch_locator', '树枝空间定位组件', 'tree_triangulation_head@2 tree_clock_distributor@2 tree_polarization_gate@4 circuit_encapsulation_part@16', 'stable_transport_medium@2000', '为世界泡和锚定提供独立空间坐标', '银色三叉定位头及紫色中心环', 2)
part('tree_remote_optical_bus', '虚数观测远端光总线', 'tree_coherent_fiber@16 tree_clock_distributor@4 tree_shot_noise_filter@4 gtceu:polyetheretherketone_foil@128', 'gtceu:polyimide@4608', '将观测数据送往跨界中继', '多端口光纤汇流排', 2)
part('tree_field_spectrometer', '树界面光谱测量组件', 'tree_spectral_imager@2 tree_aberration_cartridge@2 tree_branch_locator@1 tree_remote_optical_bus@2 spatial_probe@4', 'stable_transport_medium@2000', '为世界维系控制提供界面变化量', '带光谱条纹窗口的厚壁仪器匣', 2)
recipe('tree_repolish_windows', '磨损观测光窗再抛光', 'tree_observation_cassette@1 tree_silica_blank@2', 'tree_window_substrate@4 soulium_swarf@2', 'tree_optical_polish@2000', ticks=800, purpose='拆下服役光学匣，保留可用光窗并补回磨耗玻璃')
recipe('tree_recover_splitter', '报废成像头分光件拆解', 'tree_spectral_imager@1', 'tree_spectral_splitter@2 tree_aperture_rotor@1 soulium_swarf@4', 'soulium_process_solvent@1000', ticks=600, purpose='停役成像头回收有形光学组件，避免无限凭空复制')
recipe('tree_silver_refining', '观测镜组镀层回收', 'tree_wavefront_actuator@2', 'gtceu:platinum_dust@6 soulium_swarf@4', 'gtceu:nitric_acid@2000', ticks=600, purpose='损耗镜组回收贵金属，按箔片材料量折算后低于原生投入')
recipe('tree_bus_retermination', '远端光总线重新端接', 'tree_remote_optical_bus@1 gtceu:polyetheretherketone_foil@32', 'tree_coherent_fiber@8 circuit_encapsulation_part@4', 'soulium_process_solvent@1000', ticks=600, purpose='将长总线拆成可再用短光纤，独立拉丝路线保留首源')
recipe('tree_polish_regeneration', '观测抛光悬液离心再生', 'separation_filter@1 gtceu:diamond_dust@8', 'separation_residue@1', 'spent_tree_optical_polish@4000', 'tree_optical_polish@3500', ticks=600, purpose='补充磨粒并分离魂钢微屑，液体保留损耗')
link('industrial_imaginary_observation', 'tree_observation_cassette@2 tree_branch_locator@2', reason='真实光路与测距组件承担树枝观测，不再仅投入探针和数据基底')
link('industrial_imaginary_anchor', 'tree_branch_locator@2', reason='用树枝坐标为锚桩确定位置')
link('industrial_world_maintenance', 'tree_field_spectrometer@2', reason='界面光谱为世界维系提供实时测量')

configure('I35', 25, 'RN-IAA', 'imaginary_anchoring', '白金与深紫')
fluid_asset('spent_anchor_grout', '失活虚数锚定灌注液', '655674', '回收锚定期间捕获的应力颗粒')
liquid('anchor_grout', '虚数锚定灌注液', 'A67CDB', 'gtceu:zirconium_oxide_dust@128 gtceu:graphene_dust@64', 'honkai_stabilization_medium@8000 gtceu:reinforced_epoxy_resin@4000', '在锚桩与虚数边界之间形成应力传递层', 12000)
parts([
('anchor_preload_shim','锚桩预紧垫片','material:soulium/plate@32 gtceu:infinity_plate@16','soulium_protective_gas@2000','将装配预紧力分散到锚桩端面','堆叠的开槽环形垫片'),
('anchor_kinematic_cone','锚定位锥座','material:soulium/plate@32 gtceu:neutronium_plate@64','soulium_process_solvent@1000','以确定接触点约束六个刚体自由度','三角圆锥定位座'),
('anchor_tension_tendon','虚数抗拉索芯','gtceu:fine_shirabon_wire@128 gtceu:carbon_fiber_mesh@64','gtceu:polyimide@4608','跨界拉索承受轴向张力','绞合银紫钢索'),
('anchor_flexure_sleeve','锚桩柔顺衬套','gtceu:niobium_titanium_plate@128 gtceu:polyetheretherketone_foil@128','gtceu:helium@2000','容许热胀位移而传递锚定力','带轴向弹性槽的厚壁套筒'),
('anchor_piezo_stack','锚位压电微调堆','gtceu:quartzite_plate@128 gtceu:platinum_foil@64 soulium_data_substrate@4','gtceu:polyimide@2304','将电压转换为锚桩微小位移','多层紫晶与金属叠片'),
('anchor_displacement_pickup','锚位差动位移线圈','gtceu:fine_niobium_titanium_wire@128 gtceu:neutronium_ring@32','gtceu:reinforced_epoxy_resin@2304','读取锚桩相对基座的位置','双绕组线圈与伸缩磁芯'),
('anchor_strain_bridge','锚桩全桥应变片','gtceu:graphene_foil@128 gtceu:fine_platinum_wire@64 etched_circuit_layer@8','gtceu:polyimide@2304','用四臂电桥测量锚索受力','四向细纹应变箔'),
('anchor_axial_socket','锚索轴向承载接头','anchor_kinematic_cone@2 anchor_preload_shim@4 gtceu:neutronium_screw@64','gtceu:lubricant@1000','将抗拉索与锚桩连接并允许检修','带大螺纹的叉形接头'),
('anchor_radial_bearing','虚数锚径向导向座','anchor_flexure_sleeve@2 anchor_preload_shim@4 gtceu:transcendentmetal_ring@32','gtceu:lubricant@1000','限制侧移并保留轴向调节','八瓣径向导向环'),
('anchor_vacuum_bellows','锚位真空隔离波纹管','gtceu:neutronium_foil@128 gtceu:polybenzimidazole_foil@128','gtceu:helium@4000','隔开工艺介质与微调执行机构','伸缩银色波纹管'),
('anchor_damping_laminate','锚索剪切阻尼片','gtceu:carbon_fiber_mesh@128 gtceu:silicone_rubber_foil@128 anchor_preload_shim@2','gtceu:polyvinyl_butyral@4608','吸收高频锚索振动而保留静态刚度','黑白夹层矩形阻尼片'),
('anchor_phase_winding','虚数相位锁定绕组','gtceu:fine_shirabon_wire@256 gtceu:niobium_nitride_foil@128 soulium_anchor_component@4','honkai_stabilization_medium@2000','将锚桩相位锁定到同一边界','紫色环绕线圈'),
('anchor_force_manifold','锚定载荷均衡歧管','anchor_axial_socket@4 anchor_radial_bearing@4 anchor_damping_laminate@4','anchor_grout@1000','在多根锚索之间分配载荷','六支路机械均衡架'),
('anchor_servo_cartridge','锚位闭环微调匣','anchor_piezo_stack@4 anchor_displacement_pickup@2 anchor_strain_bridge@4 circuit_encapsulation_part@16','gtceu:soldering_alloy@4608','根据位移和应力同步调节锚桩','带伸缩杆的伺服匣'),
('anchor_sealed_feedthrough','锚位密封动力贯穿件','anchor_vacuum_bellows@2 anchor_axial_socket@2 gtceu:polybenzimidazole_plate@64','gtceu:helium@2000','在隔离边界传递受控机械位移','法兰夹持的密封拉杆'),
('anchor_safety_release','锚索过载卸荷器','anchor_strain_bridge@4 anchor_radial_bearing@2 gtceu:transcendentmetal_screw@64','gtceu:lubricant@1000','在不可逆结构破坏前释放局部过载','机械脱扣臂和弹簧盒'),
('anchor_damped_tendon','阻尼虚数锚索','anchor_tension_tendon@8 anchor_damping_laminate@4 anchor_axial_socket@4','anchor_grout@2000','提供有阻尼的跨界抗拉连接','两端带关节的粗壮钢索'),
('anchor_phase_servo','锚定相位跟踪模组','anchor_phase_winding@4 anchor_servo_cartridge@2 spatial_calibration_module@4','gtceu:soldering_alloy@4608','联合控制机械位置和虚数相位','中央线圈与双侧伺服盒'),
('anchor_grout_injector','锚桩定量灌注头','anchor_sealed_feedthrough@2 anchor_force_manifold@2 gtceu:neutronium_small_fluid_pipe@32','gtceu:polyimide@2304','将灌注液送入承载接触层','多孔喷嘴与压力接口'),
('anchor_isolation_foot','锚定隔振承载脚','anchor_kinematic_cone@4 anchor_radial_bearing@4 anchor_damping_laminate@4 anchor_safety_release@2','gtceu:reinforced_epoxy_resin@4608','将锚定载荷传到机器基础','宽底三层机械支脚'),
('anchor_load_node','虚数锚载荷节点','anchor_damped_tendon@4 anchor_force_manifold@2 anchor_sealed_feedthrough@2 soulium_anchor_component@8','anchor_grout@2000','将多束锚索并入原有锚组件','多向锚索汇接球节点'),
('anchor_feedback_harness','锚定反馈接线束','anchor_displacement_pickup@8 anchor_strain_bridge@8 anchor_servo_cartridge@2 gtceu:fine_shirabon_wire@128','gtceu:polyimide@4608','把受力和位移数据送到稳定控制器','带传感端子的编织线束'),
('anchor_boundary_clamp','虚数边界夹持组件','anchor_phase_servo@2 anchor_load_node@2 anchor_isolation_foot@4 anchor_grout_injector@2','anchor_grout@2000','在空间边界建立有载锚定连接','四爪夹具与中部紫色线圈'),
('anchor_field_transfer','锚定场力传递组件','anchor_phase_winding@8 anchor_feedback_harness@2 anchor_safety_release@4 soulium_anchor_component@8','anchor_grout@2000','将虚数锚定力传递到世界维系结构','环状场线圈与十字载荷支架')
])
recipe('anchor_grout_service','边界夹持件灌注维护','anchor_boundary_clamp@2','anchor_load_node@1 soulium_swarf@4','anchor_grout@4000','spent_anchor_grout@4000',ticks=1000,purpose='服役夹持件卸压后回收内部节点，旧灌注介质进入再生')
recipe('anchor_grout_regeneration','锚定灌注液应力颗粒分离','separation_filter@1 gtceu:zirconium_oxide_dust@16','separation_residue@2','spent_anchor_grout@4000 honkai_stabilization_medium@500','anchor_grout@4000',ticks=1000,purpose='补充失活载体并回用已分离的灌注介质')
recipe('anchor_tendon_restrand','退役锚索解股','anchor_damped_tendon@2','anchor_tension_tendon@3 anchor_axial_socket@1','soulium_process_solvent@2000',ticks=800,purpose='回收长索的内层钢丝，新增钢索仍有原生制造路径')
recipe('anchor_servo_salvage','锚位伺服匣拆修','anchor_servo_cartridge@2','anchor_piezo_stack@1 anchor_displacement_pickup@1 soulium_swarf@4','soulium_process_solvent@1000',ticks=800,purpose='以整匣损耗换回仍可使用的执行与测量部件')
link('industrial_imaginary_anchor','anchor_boundary_clamp@2 anchor_feedback_harness@2','anchor_grout@2000',reason='锚定位、承载与应力反馈分别由实体组件承担')
link('industrial_world_maintenance','anchor_field_transfer@2',reason='世界维系工艺使用虚数锚的场力传递组件')
link('industrial_prefabrication','anchor_isolation_foot@4',reason='预制奇观构件具备可承载的隔振基脚')
recipe('anchor_phase_coil_recovery','相位绕组绝缘剥离','anchor_phase_winding@2','gtceu:fine_shirabon_wire@96 gtceu:niobium_nitride_foil@32','soulium_process_solvent@2000',ticks=800,purpose='从退役绕组中回收导体和屏蔽箔，回收少于制造投入')

configure('I36', 19, 'RN-RAT', 'reality_stability', '蓝白与金色')
fluid_asset('spent_reality_dielectric','失效现实场介电液','6A747E','收集场线圈绝缘降解产物并重新净化')
liquid('reality_dielectric','现实场介电浸渍液','75B7DE','gtceu:mica_dust@128 gtceu:alumina_dust@128','gtceu:silicone_rubber@8000 honkai_stabilization_medium@4000','填充现实稳定线圈绝缘层并抑制局部放电',12000)
parts([
('reality_ceramic_spool','现实场陶瓷绕线骨架','gtceu:alumina_dust@256 gtceu:zirconium_oxide_dust@128','gtceu:argon@4000','固定线圈间隙并绝缘相邻绕组','白色带法兰陶瓷线轴'),
('reality_flux_return','现实场闭合磁轭','gtceu:niobium_titanium_plate@128 gtceu:neutronium_plate@64','honkai_stabilization_medium@2000','为场线提供可控回流路径','四角闭合的厚重磁轭'),
('reality_gradient_winding','现实场梯度绕组','reality_ceramic_spool@4 gtceu:fine_niobium_titanium_wire@256 gtceu:polyetheretherketone_foil@128','reality_dielectric@1000','调节边界附近的场强梯度','双锥相向的蓝色绕组'),
('reality_trim_winding','现实场微调绕组','reality_ceramic_spool@4 gtceu:fine_gold_wire@256 gtceu:polyetheretherketone_foil@128','reality_dielectric@1000','补偿安装误差造成的剩余场','薄型分段小线圈'),
('reality_guard_electrode','现实场护环电极','gtceu:platinum_foil@128 gtceu:polybenzimidazole_plate@128','gtceu:reinforced_epoxy_resin@2304','阻挡绝缘边缘的泄漏电流','金色同心护环电极'),
('reality_hall_pickup','现实场霍尔拾取片','gtceu:gallium_arsenide_dust@64 gtceu:gold_foil@64 etched_circuit_layer@8','gtceu:soldering_alloy@2304','把局部场强转换为电反馈','四引脚小型蓝色测量片'),
('reality_resistive_bridge','现实场差动电阻桥','gtceu:graphene_foil@128 gtceu:fine_platinum_wire@128 etched_circuit_layer@8','gtceu:polyimide@2304','比较场边界两侧的传感器读数','四臂电桥与中央散热片'),
('reality_thermal_strap','现实场柔性导热带','gtceu:carbon_fiber_mesh@128 gtceu:graphene_foil@128 gtceu:neutronium_foil@64','gtceu:polyimide@2304','把线圈热点热量导向冷板','银黑编织导热扁带'),
('reality_cold_plate','现实场分区冷板','gtceu:neutronium_plate@128 gtceu:neutronium_small_fluid_pipe@64 reality_thermal_strap@4','gtceu:soldering_alloy@4608','将场线圈余热分区引出','带蛇形液道的金属冷板'),
('reality_ground_mesh','现实场等电位网','gtceu:fine_gold_wire@256 gtceu:niobium_nitride_foil@128','gtceu:polyimide@2304','让场端屏蔽壳保持相同电位','交叉编织金网与接地端'),
('reality_ceramic_feedthrough','现实场绝缘贯穿件','reality_ceramic_spool@2 reality_guard_electrode@2 gtceu:fine_niobium_titanium_wire@128','reality_dielectric@1000','把大电流引入屏蔽边界','白瓷法兰中穿过银色导杆'),
('reality_gate_driver','现实场功率驱动板','etched_circuit_layer@16 circuit_encapsulation_part@8 reality_guard_electrode@2 gtceu:gold_foil@128','gtceu:soldering_alloy@4608','按控制信号调节稳定线圈电流','金色栅极接线的蓝色电路板'),
('reality_sensor_ring','现实场多点测量环','reality_hall_pickup@8 reality_resistive_bridge@4 reality_ground_mesh@2','gtceu:polyimide@4608','对场边界进行多点差动采样','八枚测量片围成的环'),
('reality_coil_module','现实场屏蔽线圈模组','reality_gradient_winding@4 reality_trim_winding@4 reality_flux_return@2 reality_ceramic_feedthrough@4','reality_dielectric@2000','形成带独立微调与绝缘的稳定线圈','套装双层蓝白线圈'),
('reality_drift_integrator','现实场漂移积分器','reality_resistive_bridge@4 reality_gate_driver@2 circuit_encapsulation_part@16','gtceu:soldering_alloy@4608','累积低频场误差并控制补偿绕组','带大积分电容的电路盒'),
('reality_feedback_filter','现实场反馈抑振滤波器','reality_hall_pickup@4 reality_guard_electrode@4 gtceu:fine_niobium_titanium_wire@128 etched_circuit_layer@16','gtceu:polyimide@4608','过滤传感噪声并限制控制回路振荡','屏蔽罩中的电感电容滤波组'),
('reality_insulation_block','现实场真空绝缘块','reality_ground_mesh@4 reality_ceramic_feedthrough@4 gtceu:polybenzimidazole_plate@128','reality_dielectric@2000','把高场绝缘组合成便于更换的模块','透明蓝色灌封层中的陶瓷块'),
('reality_quench_switch','现实场失超泄放开关','reality_gate_driver@4 reality_thermal_strap@4 gtceu:neutronium_bolt@64 gtceu:nichrome_plate@128','gtceu:soldering_alloy@4608','在失超时把线圈能量引向电阻负载','带粗接线端的机械电力开关'),
('reality_compensation_yoke','现实场补偿磁路','reality_flux_return@4 reality_trim_winding@8 reality_sensor_ring@2','reality_dielectric@2000','抵消邻近机器引入的静态场偏差','可调四极蓝白磁路'),
('reality_boundary_driver','现实边界功率驱动匣','reality_gate_driver@4 reality_drift_integrator@2 reality_feedback_filter@2 reality_quench_switch@2','gtceu:soldering_alloy@4608','提供含闭环调节和泄放保护的驱动','侧面带大端子的功率匣'),
('reality_isolation_tile','现实稳定隔离瓦','reality_insulation_block@2 reality_cold_plate@2 reality_ground_mesh@4','reality_dielectric@1000','把现实稳定组件隔离于高能工艺室','蓝白叠层工业瓦片'),
('reality_field_cartridge','现实稳定场组件匣','reality_coil_module@4 reality_compensation_yoke@2 reality_boundary_driver@2 reality_sensor_ring@2','reality_dielectric@2000','提供可装入工业设施的完整稳定场单元','环形蓝色场组件与白色承载匣'),
('reality_sensor_harness','现实边界监测线束','reality_sensor_ring@4 reality_feedback_filter@4 reality_ceramic_feedthrough@4 gtceu:polyetheretherketone_foil@128','gtceu:polyimide@4608','向世界维系与预制工艺提供边界监测','多路传感插头和屏蔽编织线束'),
('reality_quench_bank','现实场泄放电阻组','reality_quench_switch@4 reality_cold_plate@4 reality_thermal_strap@8 gtceu:nichrome_plate@256','reality_dielectric@2000','消耗高能场切换时释放的剩余能量','带液冷接头的多片电阻架')
])
recipe('reality_dielectric_exchange','稳定场组件排液维护','reality_field_cartridge@1','reality_coil_module@1 soulium_swarf@4','reality_dielectric@4000','spent_reality_dielectric@4000',ticks=1000,purpose='维护退役场组件时回收线圈并产生真实废介电液')
recipe('reality_dielectric_regeneration','介电液真空脱气再生','process_gas_filter@1 gtceu:mica_dust@16','depleted_gas_filter@1','spent_reality_dielectric@4000','reality_dielectric@3500',ticks=1200,purpose='过滤导电颗粒并去除介电液中的气体')
recipe('reality_winding_recovery','失超绕组解绕回收','reality_gradient_winding@2','gtceu:fine_niobium_titanium_wire@96 reality_ceramic_spool@2','soulium_process_solvent@2000',ticks=800,purpose='退役梯度线圈按损耗回收导线与陶瓷骨架')
recipe('reality_sensor_rework','监测线束拆解维修','reality_sensor_harness@1','reality_sensor_ring@1 reality_ceramic_feedthrough@1','soulium_process_solvent@1000',ticks=800,purpose='短接线束拆回可直接使用的传感环和贯穿件')
recipe('reality_guard_refining','护环电极贵金属剥离','reality_guard_electrode@4','gtceu:platinum_dust@24','gtceu:hydrochloric_acid@4000',ticks=800,purpose='回收绝缘电极的铂镀层，箔片按四分之一锭折算后保留损耗')
link('industrial_world_maintenance','reality_field_cartridge@2 reality_sensor_harness@2',reason='维系世界边界需要实际稳定场与监测回路')
link('industrial_composite_confining','reality_isolation_tile@4 reality_quench_bank@2',reason='约束复合材料生产需要现实场隔离与失超泄放')
link('industrial_prefabrication','reality_isolation_tile@4',reason='预制件加入绝缘和边界隔离层')

configure('I37', 27, 'RN-WME', 'world_maintenance', '青绿与白银')
fluid_asset('spent_world_regeneration_bath','负载世界再生浴液','517467','吸收维系运行中的溶出物并进入资源回收')
liquid('world_regeneration_bath','世界维系再生浴液','68C9AE','gtceu:zirconium_oxide_dust@128 gtceu:carbon_dust@128 gtceu:alumina_dust@128','world_stabilization_medium@8000 gtceu:grade_16_purified_water@16000','在稳定世界边界内运输离子并固定溶出杂质',24000)
parts([
('world_membrane_support','世界维系多孔膜架','material:soulium/plate@64 gtceu:zirconium_carbide_dust@128','soulium_protective_gas@4000','承托再生膜并抵抗跨界压差','青白多孔圆盘及金属辐条'),
('world_selective_membrane','世界维系离子选择膜','gtceu:polybenzimidazole_foil@256 gtceu:graphene_foil@128 gtceu:zirconium_oxide_dust@64','world_regeneration_bath@1000','选择性通过维系介质中的有效离子','半透明绿色叠层薄膜'),
('world_catalytic_felt','维系反应催化毡','gtceu:carbon_fiber_mesh@128 gtceu:platinum_dust@64 gtceu:palladium_dust@64','soulium_process_solvent@2000','在低压差下提供反应表面','银色微粒覆盖的绿色纤维毡'),
('world_ion_exchange_bead','维系离子交换珠','gtceu:polytetrafluoroethylene_dust@256 gtceu:zirconium_oxide_dust@128','gtceu:hydrochloric_acid@4000','从循环维系液中固定离子杂质','成串半透明绿色树脂珠'),
('world_porous_diffuser','世界维系微孔扩散板','gtceu:silicon_carbide_plate@128 gtceu:neutronium_foil@128','gtceu:argon@4000','将供给介质均匀送入维系界面','青色微孔板与背部集流槽'),
('world_thermal_tile','世界维系温差缓冲瓦','gtceu:graphene_foil@256 gtceu:carbon_fiber_plate@128 gtceu:polybenzimidazole_plate@128','gtceu:polyimide@4608','平衡局部热流以减少世界边界应力','白色隔热层夹持绿色导热片'),
('world_strain_web','维系柔顺应力网','gtceu:fine_shirabon_wire@256 gtceu:carbon_fiber_mesh@128 material:soulium/plate@32','gtceu:polyimide@4608','把局部边界拉力分散到大面积','青银交织的立体索网'),
('world_osmotic_spacer','世界维系渗透隔网','gtceu:polyetheretherketone_foil@256 gtceu:carbon_fiber_mesh@128','world_regeneration_bath@1000','保持膜间流道并控制浓差','波浪折叠的绿色蜂窝隔网'),
('world_membrane_cassette','维系选择膜匣','world_membrane_support@4 world_selective_membrane@8 world_osmotic_spacer@4 gtceu:neutronium_screw@64','gtceu:polyimide@4608','在稳定边界中连续分离有效介质','堆叠膜片装入的方形匣'),
('world_redox_stack','维系氧化还原反应堆片','world_catalytic_felt@8 world_porous_diffuser@4 gtceu:platinum_foil@128','world_regeneration_bath@2000','通过定向界面反应处理反应性杂质','带进出液口的交替反应片'),
('world_sorbent_bed','维系再生吸附柱芯','world_ion_exchange_bead@16 gtceu:polybenzimidazole_plate@128 world_membrane_support@2','world_regeneration_bath@2000','将可回收离子集中到可更换柱芯','透明绿珠装填的短圆柱'),
('world_heat_spreader','维系平面热扩散组件','world_thermal_tile@8 gtceu:neutronium_small_fluid_pipe@64 gtceu:graphene_foil@128','gtceu:soldering_alloy@4608','让边界热量进入可控冷却回路','方形导热板及两侧液管'),
('world_load_transfer_web','世界边界载荷传递网','world_strain_web@8 soulium_anchor_component@8 gtceu:transcendentmetal_ring@64','world_regeneration_bath@2000','将边界力传到锚定结构','多个金属锚点连接的立体索网'),
('world_pressure_equalizer','世界维系压差均衡器','world_porous_diffuser@8 world_membrane_support@4 gtceu:neutronium_small_fluid_pipe@64','world_regeneration_bath@2000','缓慢均衡跨膜压力以避免结构撕裂','双腔压差调节器与旁通管'),
('world_chemical_probe','世界维系化学探头','world_selective_membrane@4 gtceu:platinum_foil@128 soulium_data_substrate@16','gtceu:polyimide@4608','测量维系液中离子负载与反应状态','带绿色隔膜的多电极探头'),
('world_edge_flux_sensor','世界边缘通量传感器','world_strain_web@4 world_thermal_tile@4 etched_circuit_layer@32 circuit_encapsulation_part@16','gtceu:soldering_alloy@4608','读取边界机械与热通量','三方向传感叶片与中心电路'),
('world_boundary_valve','维系边界分区阀','world_pressure_equalizer@2 gtceu:neutronium_ring@64 material:soulium/plate@64','world_regeneration_bath@2000','隔离故障分区并保持其他区继续维系','四路绿色液阀与旁通接口'),
('world_feedback_controller','世界维系反馈控制匣','world_chemical_probe@4 world_edge_flux_sensor@4 soulium_data_substrate@32 circuit_encapsulation_part@16','gtceu:soldering_alloy@9216','联合控制化学再生与边界载荷','带双排状态接口的绿色控制匣'),
('world_regeneration_train','世界维系介质再生组件','world_membrane_cassette@4 world_redox_stack@2 world_sorbent_bed@4 world_pressure_equalizer@2','world_regeneration_bath@4000','将分离、反应和吸附整合为维系液再生单元','串联三种反应匣的紧凑工艺组件'),
('world_boundary_heat_sink','世界边界热缓冲组件','world_heat_spreader@4 world_boundary_valve@4 world_thermal_tile@8','world_regeneration_bath@4000','储配维系时产生的温差与热流','环形冷却板与绿色缓冲腔'),
('world_load_balancer','世界维系载荷平衡组件','world_load_transfer_web@4 world_feedback_controller@2 world_edge_flux_sensor@4','world_regeneration_bath@4000','自动分配世界边界上的拉力','带中央控制核的八向机械网'),
('world_maintenance_service_pack','世界维系运行维护包','world_regeneration_train@2 world_boundary_heat_sink@2 world_feedback_controller@2 controlled_nano_swarm@16','world_regeneration_bath@4000','为现有世界维系试验提供实体维护介质与执行件','白绿工业箱中分隔的膜匣与阀组'),
('world_regeneration_interface','世界介质再生接口','world_regeneration_train@2 world_boundary_valve@4 world_chemical_probe@4','world_regeneration_bath@4000','让旧世界稳定介质接入新再生装置','双法兰绿色流体接口组件'),
('world_boundary_service_frame','世界边界维系承载架','world_load_balancer@2 world_boundary_heat_sink@2 world_load_transfer_web@4 soulium_anchor_component@16','world_regeneration_bath@4000','给奇观构件提供受控边界与承载结构','带绿色稳定节点的空间桁架')
])
recipe('world_service_reclaim','维系维护包服役拆解','world_maintenance_service_pack@4','world_membrane_support@2 inactive_nano_unit@8','world_regeneration_bath@4000','spent_world_regeneration_bath@4000',ticks=1600,purpose='服役维护包拆出可重复利用的实体框架并回收负载浴液')
recipe('world_bath_regeneration','世界再生浴液离子解吸','world_ion_exchange_bead@2','separation_residue@2','spent_world_regeneration_bath@8000 gtceu:grade_16_purified_water@1000','world_regeneration_bath@7500',ticks=1600,purpose='恢复维系浴液并把固定杂质移出循环')
recipe('world_membrane_rebuild','维系膜匣拆解','world_membrane_cassette@1','world_membrane_support@1 world_osmotic_spacer@1','soulium_process_solvent@2000',ticks=1000,purpose='退役膜匣拆回支撑与隔网，损耗膜片')
recipe('world_catalyst_recovery','维系催化毡贵金属回收','world_catalytic_felt@4','gtceu:platinum_dust@32 gtceu:palladium_dust@32','gtceu:hydrochloric_acid@4000',ticks=1200,purpose='退役催化层回收铂钯，纤维支撑和部分镀层损耗')
recipe('world_frame_disassembly','维系承载架卸载拆解','world_boundary_service_frame@1','world_load_transfer_web@1 soulium_anchor_component@4 soulium_swarf@8','soulium_process_solvent@2000',ticks=1000,purpose='停役承载架仅回收完整索网和部分锚点')
link('industrial_world_maintenance','world_maintenance_service_pack@2 world_load_balancer@2',reason='世界维系有消耗的维护包和实际载荷平衡器')
link('industrial_composite_reconstructing','world_regeneration_interface@2',reason='再构复材使用可再生介质接口保持反应边界')
link('industrial_prefabrication','world_boundary_service_frame@4',reason='奇观预制件有维系承载架')

configure('I38', 26, 'RN-HER', 'imaginary_rectification', '紫黑与亮金')
fluid_asset('spent_rectifier_passivation','负载整流钝化液','736476','去除功率半导体边缘金属离子后进入再生')
liquid('rectifier_passivation','虚数整流界面钝化液','B185D8','gtceu:sodium_fluoride_dust@128 gtceu:boron_dust@64','gtceu:grade_16_purified_water@16000 soulium_process_solvent@4000','清洁整流界面并控制表面漏电',20000)
parts([
('rectifier_carbide_wafer','虚数整流碳化硅晶片','gtceu:silicon_carbide_dust@256 gtceu:boron_dust@64','gtceu:argon@8000','承受高电场的功率半导体衬底','深紫色方形晶片'),
('rectifier_gate_oxide','整流栅极绝缘膜','gtceu:hafnium_oxide_dust@128 gtceu:alumina_dust@128 gtceu:platinum_foil@64','rectifier_passivation@1000','控制半导体表面电场并隔离栅极','金属边框中的紫色薄膜'),
('rectifier_copper_interposer','整流低感导电底板','gtceu:gold_foil@256 gtceu:carbon_fiber_plate@128 gtceu:neutronium_plate@64','gtceu:soldering_alloy@4608','将功率器件直接接到大电流端口','金色宽导流片与深色基底'),
('rectifier_sinter_paste_pad','整流烧结银连接片','gtceu:silver_dust@256 gtceu:platinum_dust@64','soulium_process_solvent@2000','用烧结连接替代高热阻焊点','银色多孔连接薄片'),
('rectifier_guard_ring','整流电场均压环','gtceu:niobium_nitride_foil@256 gtceu:polybenzimidazole_plate@128','rectifier_passivation@1000','降低功率晶片边缘电场集中','多层黑金同心护环'),
('rectifier_kelvin_terminal','整流四端测量端子','gtceu:fine_gold_wire@256 gtceu:neutronium_bolt@64 gtceu:alumina_dust@128','gtceu:polyimide@4608','分离主电流和栅极参考电位','四支粗细不同的接线端子'),
('rectifier_schottky_die','虚数整流肖特基芯片','passivated_rectifier_wafer@4 rectifier_sinter_paste_pad@4 gtceu:platinum_foil@128','rectifier_passivation@2000','在低反向恢复损耗下整流','带银色接触面的紫色小晶片'),
('rectifier_switch_die','虚数整流开关芯片','passivated_rectifier_wafer@4 rectifier_gate_oxide@8 rectifier_guard_ring@4','rectifier_passivation@2000','在受控时刻切换虚数能量电流','金色栅极网络覆盖的晶片'),
('rectifier_diode_tile','虚数整流二极管瓦','rectifier_schottky_die@8 rectifier_copper_interposer@4 rectifier_kelvin_terminal@4','gtceu:polyimide@4608','以低电感封装形成二极管支路','黑色陶瓷瓦上并列的二极管芯片'),
('rectifier_switch_tile','虚数整流有源开关瓦','rectifier_switch_die@8 rectifier_sinter_paste_pad@8 rectifier_copper_interposer@4 rectifier_kelvin_terminal@4','gtceu:polyimide@4608','为同步整流提供可独立驱动的开关支路','金色导流片覆盖的紫黑功率瓦'),
('rectifier_gate_transformer','整流隔离栅极变压器','gtceu:fine_niobium_titanium_wire@256 gtceu:niobium_nitride_foil@128 gtceu:polyetheretherketone_foil@128','gtceu:reinforced_epoxy_resin@4608','把栅极控制信号隔离到高电位','双隔离骨架与金色绕组'),
('rectifier_deadtime_board','整流死区控制板','etched_circuit_layer@32 circuit_encapsulation_part@16 gtceu:gold_foil@128','gtceu:soldering_alloy@9216','避免半桥上下开关同时导通','对称双驱动接口电路板'),
('rectifier_desaturation_sensor','整流饱和异常检测器','rectifier_kelvin_terminal@4 rectifier_schottky_die@4 soulium_data_substrate@16','gtceu:soldering_alloy@4608','检测开关过流并快速关断','金色探针夹持的传感电路盒'),
('rectifier_snubber_capacitor','整流缓冲吸收电容','gtceu:polybenzimidazole_foil@256 gtceu:aluminium_foil@256 rectifier_guard_ring@4','reality_dielectric@2000','吸收开关瞬态尖峰电压','扁平紫色电容和宽接线片'),
('rectifier_laminated_busbar','整流叠层直流母排','rectifier_copper_interposer@8 gtceu:polybenzimidazole_foil@256 gtceu:gold_foil@128','gtceu:polyimide@4608','让去回电流靠近以减少寄生电感','金黑交替的多层扁母排'),
('rectifier_ceramic_coldplate','整流绝缘微流道冷板','gtceu:alumina_dust@256 gtceu:neutronium_small_fluid_pipe@128 gtceu:graphene_foil@128','gtceu:soldering_alloy@9216','在绝缘条件下冷却功率晶片','白瓷微流道冷板与双金属液口'),
('rectifier_isolated_driver','虚数整流隔离驱动器','rectifier_gate_transformer@4 rectifier_deadtime_board@4 rectifier_desaturation_sensor@4 circuit_encapsulation_part@16','gtceu:soldering_alloy@9216','组合隔离驱动与故障关断','四路隔离接口的紫色功率板'),
('rectifier_half_bridge','虚数整流半桥模块','rectifier_switch_tile@8 rectifier_snubber_capacitor@4 rectifier_laminated_busbar@4 rectifier_ceramic_coldplate@2','gtceu:polyimide@9216','构成有源整流的功率桥臂','上下对称功率瓦与中间母排'),
('rectifier_diode_bridge','虚数整流无源桥模块','rectifier_diode_tile@8 rectifier_laminated_busbar@4 rectifier_ceramic_coldplate@2','gtceu:polyimide@9216','给启动和旁路回路提供固定极性','六枚二极管围绕直流母排'),
('rectifier_precharge_unit','整流直流预充电组件','rectifier_diode_tile@4 rectifier_snubber_capacitor@4 rectifier_desaturation_sensor@2 gtceu:nichrome_plate@128','gtceu:soldering_alloy@9216','限制直流母线首次充电冲击','功率电阻与二极管组成的紧凑匣'),
('rectifier_active_power_stack','虚数有源整流功率堆','rectifier_half_bridge@6 rectifier_isolated_driver@6 rectifier_laminated_busbar@8 rectifier_ceramic_coldplate@4','honkai_coolant@4000','承担现行虚数能量整流的实体功率级','多层紫黑桥臂与金色母排堆叠'),
('rectifier_fault_bypass','虚数整流故障旁路组件','rectifier_diode_bridge@4 rectifier_precharge_unit@2 rectifier_desaturation_sensor@4 gtceu:neutronium_bolt@128','gtceu:polyimide@9216','让故障支路被隔离后维持其余回路','双粗端子与旁路功率桥'),
('rectifier_power_interface','文明电网整流接口','rectifier_active_power_stack@2 rectifier_fault_bypass@2 rectifier_precharge_unit@2 soulium_data_substrate@32','gtceu:soldering_alloy@18432','把虚数整流级接入文明电网母线','带三组金色接线口的整流柜芯'),
('rectifier_grid_chopper','文明电网制动斩波组件','rectifier_half_bridge@4 rectifier_isolated_driver@4 rectifier_snubber_capacitor@8 gtceu:nichrome_plate@256','honkai_coolant@4000','处理电网调度期间的负载突变和回馈过压','带水冷电阻片的紫黑功率模块')
])
output_asset('passivated_rectifier_wafer','已钝化虚数整流晶片','去除边缘缺陷并稳定表面电场后才能形成有源整流芯片','紫黑晶片边缘可见金白钝化环')
recipe('rectifier_surface_clean','整流晶片边缘清洗与钝化','rectifier_carbide_wafer@4','passivated_rectifier_wafer@4 separation_residue@1','rectifier_passivation@2000','spent_rectifier_passivation@2000',ticks=800,purpose='固定产出表面已钝化的下一工序晶片，钝化液带走界面杂质')
recipe('rectifier_bath_recovery','整流钝化液过滤再生','separation_filter@1 gtceu:sodium_fluoride_dust@16','separation_residue@2','spent_rectifier_passivation@4000','rectifier_passivation@3500',ticks=1000,purpose='去除金属离子并补充氟化组分')
recipe('rectifier_bridge_teardown','退役半桥拆出功率瓦','rectifier_half_bridge@2','rectifier_switch_tile@3 rectifier_ceramic_coldplate@1 composite_offcut@4','soulium_process_solvent@2000',ticks=1000,purpose='半桥退役后保留部分可用功率瓦和冷板')
recipe('rectifier_silver_recovery','烧结银连接层回收','rectifier_sinter_paste_pad@4','gtceu:silver_dust@160 gtceu:platinum_dust@32','gtceu:hydrochloric_acid@4000',ticks=1000,purpose='剥离退役连接片中的银和铂，保持材料损耗')
recipe('rectifier_busbar_recovery','叠层母排剥层回收','rectifier_laminated_busbar@2','rectifier_copper_interposer@3 gtceu:gold_dust@24','soulium_process_solvent@2000',ticks=1000,purpose='大母排拆回部分导电底板及镀层，金箔按材料量折算')
link('industrial_energy_rectification_gas','rectifier_active_power_stack@2 rectifier_fault_bypass@2',reason='气态崩坏能整流使用真实功率堆和故障隔离支路')
link('industrial_energy_rectification_core','rectifier_active_power_stack@4 rectifier_precharge_unit@2',reason='核心高能脉冲整流需要预充电与有源开关桥')
link('industrial_dispatch_conductor','rectifier_power_interface@2 rectifier_grid_chopper@2',reason='文明电网接收整流功率并处理负载回馈')

configure('I39', 24, 'RN-VRC', 'cross_boundary_relay', '深蓝与青紫')
fluid_asset('spent_relay_immersion','负载跨界总线浸没液','4E647A','带走总线介质中的游离杂质后过滤再生')
liquid('relay_immersion','跨界总线浸没液','678ECE','gtceu:zirconium_oxide_dust@64 gtceu:graphene_dust@64','stable_transport_medium@8000 gtceu:perfluorobenzene@8000','浸没高速数据总线并稳定跨界接口介电常数',16000)
parts([
('relay_silica_waveguide','跨界中继石英波导','gtceu:fine_borosilicate_glass_wire@256 gtceu:polyetheretherketone_foil@128','gtceu:polyimide@4608','把高速光信号引到中继接口','蓝色柔性光波导束'),
('relay_optical_coupler','跨界中继光耦合器','gtceu:sapphire_lens@16 gtceu:gold_foil@128 material:soulium/plate@32','stable_transport_medium@2000','将发射光束耦合到波导','双端蓝色透镜连接头'),
('relay_differential_pair','跨界差分传输线对','gtceu:fine_gold_wire@256 gtceu:polybenzimidazole_foil@128','gtceu:polyimide@4608','抑制跨界电连接的共同模式干扰','两条并行金色屏蔽传输线'),
('relay_balun_core','跨界中继平衡变换磁芯','gtceu:magnetic_steel_plate@128 gtceu:niobium_nitride_foil@128','gtceu:reinforced_epoxy_resin@4608','变换平衡与非平衡信号阻抗','双孔深蓝磁芯'),
('relay_impedance_coupon','跨界阻抗匹配片','gtceu:graphene_foil@128 gtceu:gold_foil@128 etched_circuit_layer@16','gtceu:polyimide@4608','给总线端点提供实体匹配网络','带蛇形微带的蓝色小板'),
('relay_clock_oscillator','跨界中继稳频振荡器','gtceu:quartzite_plate@128 gtceu:platinum_foil@64 soulium_data_substrate@8','gtceu:soldering_alloy@4608','提供可由远端对时的本地时钟','金属壳中的紫色石英片'),
('relay_photonic_transmitter','跨界光发射组件','relay_optical_coupler@4 relay_silica_waveguide@4 gtceu:gallium_arsenide_dust@64','gtceu:soldering_alloy@4608','把数字信号转为跨界光脉冲','带青色出光口的银蓝发射头'),
('relay_photonic_receiver','跨界光接收组件','relay_optical_coupler@4 relay_silica_waveguide@4 gtceu:indium_gallium_phosphide_dust@64','gtceu:soldering_alloy@4608','把跨界光脉冲恢复为电信号','带深蓝遮光罩的接收头'),
('relay_line_transformer','跨界传输隔离变压器','relay_balun_core@4 relay_differential_pair@8 gtceu:polyetheretherketone_foil@128','relay_immersion@1000','隔断地电位差并匹配传输阻抗','屏蔽壳中的双线绕组'),
('relay_equalizer_board','跨界通道均衡板','relay_impedance_coupon@8 etched_circuit_layer@32 circuit_encapsulation_part@16','gtceu:soldering_alloy@9216','补偿跨界链路的频率选择性衰减','多级微带与可调元件电路板'),
('relay_clock_recovery','跨界时钟恢复电路','relay_clock_oscillator@4 relay_differential_pair@4 circuit_encapsulation_part@16','gtceu:soldering_alloy@9216','从接收数据恢复同步时钟','带锁相环和时钟晶体的电路盒'),
('relay_crc_engine','跨界差错校验处理板','soulium_data_substrate@16 etched_circuit_layer@32 circuit_encapsulation_part@16 gtceu:gold_foil@128','gtceu:soldering_alloy@9216','检测和纠正链路传输误码','并排校验芯片与蓝色总线'),
('relay_packet_memory','跨界分组缓冲存储片','soulium_data_substrate@32 gtceu:niobium_nitride_foil@128 gtceu:polybenzimidazole_foil@128','relay_immersion@2000','缓冲时延变化期间的数据分组','多层蓝紫存储阵列'),
('relay_isolation_backplane','跨界中继隔离背板','relay_line_transformer@4 relay_impedance_coupon@8 gtceu:neutronium_plate@64','gtceu:polyimide@9216','为不同空间侧的总线提供隔离安装位','多插槽深蓝背板'),
('relay_duplex_optical_head','跨界双工光通信头','relay_photonic_transmitter@4 relay_photonic_receiver@4 relay_equalizer_board@2','relay_immersion@2000','在单个接口同时收发两路跨界光信号','双出光口蓝银通信头'),
('relay_timestamp_unit','跨界硬件时间戳单元','relay_clock_recovery@4 relay_crc_engine@2 relay_clock_oscillator@4','gtceu:soldering_alloy@9216','在实体接口处记录真实收发时刻','晶振围绕的计时电路盒'),
('relay_store_forward','跨界存储转发组件','relay_packet_memory@8 relay_crc_engine@4 relay_equalizer_board@4','relay_immersion@2000','在空间路径暂时中断时保留有效分组','多层存储板与转发接口匣'),
('relay_link_watchdog','跨界航路失联监测器','relay_timestamp_unit@2 relay_clock_recovery@2 relay_isolation_backplane@2','gtceu:soldering_alloy@9216','识别链路时延越限并通知航路调度','带独立时钟的双接口监测盒'),
('relay_clock_boundary','跨界时钟边界转换器','relay_timestamp_unit@4 relay_isolation_backplane@2 relay_line_transformer@4','relay_immersion@2000','在两个独立时钟域之间转交数据','分隔双时钟域的桥接板'),
('relay_optical_switch','跨界光路切换组件','relay_duplex_optical_head@4 relay_silica_waveguide@16 relay_clock_boundary@2','stable_transport_medium@4000','选择已校准的跨界光路','四支路光纤切换匣'),
('relay_route_bus','无人跨界航路总线','relay_store_forward@4 relay_duplex_optical_head@4 relay_isolation_backplane@4 soulium_data_substrate@32','relay_immersion@4000','把旧航路中继模组接到完整通信总线','多接口深蓝工业总线匣'),
('relay_navigation_link','跨界导航同步组件','relay_clock_boundary@4 relay_link_watchdog@4 relay_optical_switch@2 spatial_calibration_module@4','stable_transport_medium@4000','向千界列车提供校时与导航数据','双频导航接口和光纤盘'),
('relay_beacon_link','跨界信标通信组件','relay_optical_switch@2 relay_timestamp_unit@4 relay_crc_engine@4','relay_immersion@4000','将千界信标观测数据传回中继','带环形天线的蓝色光通信匣'),
('relay_maintenance_bus','世界维系远程控制总线','relay_route_bus@2 relay_link_watchdog@4 relay_store_forward@4 relay_navigation_link@2 circuit_encapsulation_part@32','relay_immersion@4000','在有时延的航路上传输维系控制和反馈','带隔离插头的多层控制匣')
])
recipe('relay_bus_fluid_exchange','跨界总线浸没维护','relay_route_bus@1','relay_isolation_backplane@1 circuit_encapsulation_part@4','relay_immersion@4000','spent_relay_immersion@4000',ticks=1000,purpose='退役总线取出背板并回收浸没介质')
recipe('relay_immersion_regeneration','跨界浸没液吸附再生','process_gas_filter@1 separation_filter@1','depleted_gas_filter@1 separation_residue@1','spent_relay_immersion@4000','relay_immersion@3500',ticks=1200,purpose='去除绝缘介质游离杂质并保留过滤损耗')
recipe('relay_optical_salvage','双工光头拆出光耦','relay_duplex_optical_head@2','relay_optical_coupler@8 relay_silica_waveguide@4','soulium_process_solvent@2000',ticks=800,purpose='退役双工光头回收机械耦合和短光纤')
recipe('relay_memory_reclaim','转发组件存储片回收','relay_store_forward@2','relay_packet_memory@3 soulium_data_substrate@4','soulium_process_solvent@2000',ticks=800,purpose='退役转发组件保留部分可用存储器')
recipe('relay_transformer_rewind','隔离变压器解绕','relay_line_transformer@2','relay_balun_core@1 relay_differential_pair@3','soulium_process_solvent@1000',ticks=800,purpose='拆解隔离变压器回收磁芯和部分传输线')
link('industrial_route_relay_module','relay_route_bus@2 relay_clock_boundary@2 relay_beacon_link@2',reason='航路中继包含实体数据总线、时钟域转换和信标通信接口')
link('industrial_world_maintenance','relay_maintenance_bus@2',reason='远端世界维系具备隔离控制和反馈总线')

configure('I40', 27, 'RN-WMS', 'wonder_materials', '银白、靛紫与四种功能色')
fluid_asset('spent_composite_infiltrant','失效奇观复材浸渗液','685D79','带出复材孔隙中的残余颗粒后进入再生')
liquid('composite_infiltrant','奇观复材真空浸渗液','B59ADD','gtceu:fullerene_dust@128 gtceu:zirconium_oxide_dust@128','gtceu:fullerene_polymer_matrix_pulp@8000 world_stabilization_medium@8000','填充复材微孔并将不同功能相连接到载荷骨架',16000)
parts([
('composite_braided_preform','奇观复材三维编织预制体','gtceu:carbon_fiber_mesh@256 gtceu:fine_shirabon_wire@256','gtceu:polyimide@9216','为四类功能复材提供三向连续承载骨架','立体银紫纤维编织块'),
('composite_soulium_whisker','魂钢定向增强晶须','material:soulium/plate@128 gtceu:carbon_nanotubes_dust@128','soulium_protective_gas@8000','以细晶须桥接复材裂纹','成束银白短晶须'),
('composite_interface_veil','复材裂纹偏转界面毡','gtceu:niobium_nitride_foil@256 gtceu:graphene_foil@256','composite_infiltrant@2000','令裂纹沿可替换界面偏转并保留主结构','半透明紫色薄毡'),
('composite_ceramic_lattice','奇观复材陶瓷微桁架','gtceu:zirconium_carbide_dust@256 gtceu:silicon_carbide_dust@256','gtceu:argon@8000','在高温下保持复材内部通道形状','白色多孔立体微桁架'),
('composite_conductive_roving','复材超导导电束','gtceu:fine_shirabon_wire@512 gtceu:niobium_nitride_foil@256','composite_infiltrant@2000','在承载纤维间建立连续低损耗电流路径','缠绕紫色绝缘膜的银色导电束'),
('composite_dielectric_interleaf','复材高场介电夹层','gtceu:hafnium_oxide_dust@256 gtceu:polybenzimidazole_foil@256','reality_dielectric@4000','把约束复材中的强电场分层隔开','白紫交替的绝缘叠层'),
('composite_healing_capsule','复材自修复微胶囊','gtceu:fullerene_dust@128 gtceu:graphene_dust@128 controlled_nano_swarm@16','soulium_precursor_fluid@4000','在局部裂纹处释放有限的再构材料','绿色核心包裹的微小胶囊簇'),
('composite_synaptic_grain','复材可编程极化晶粒','gtceu:lanthanum_embedded_fullerene_dust@128 gtceu:gallium_arsenide_dust@128','honkai_stabilization_medium@4000','让认知复材的局部极化状态可写入和读取','紫蓝晶粒围绕银色电极'),
('composite_conductive_tape','奇观导电复材带','composite_conductive_roving@8 composite_interface_veil@4 composite_soulium_whisker@4','composite_infiltrant@4000','形成带载荷支撑的连续导电层','卷绕的银蓝导电宽带'),
('composite_confinement_ply','奇观约束复材层板','composite_dielectric_interleaf@8 composite_ceramic_lattice@4 composite_interface_veil@4','composite_infiltrant@4000','把电场隔离和热承载组合到同一层板','黑白多层约束板'),
('composite_rebuild_mesh','奇观再构复材网','composite_healing_capsule@8 infiltrated_composite_preform@4 composite_soulium_whisker@4','composite_infiltrant@4000','使再构介质沿裂纹可达通道分布','含绿色胶囊的银色网架'),
('composite_cognitive_film','奇观认知复材薄膜','composite_synaptic_grain@8 gtceu:gold_foil@256 composite_interface_veil@4','composite_infiltrant@4000','为认知复材提供可寻址状态层','带金色寻址网的紫色薄膜'),
('composite_current_spreader','奇观复材电流扩散层','composite_conductive_tape@8 gtceu:graphene_foil@256 composite_ceramic_lattice@4','gtceu:soldering_alloy@9216','均匀注入电流以避免局部过热','放射状导流纹的银蓝平板'),
('composite_field_grading','奇观复材场强分级层','composite_confinement_ply@8 composite_dielectric_interleaf@4 gtceu:niobium_nitride_foil@256','reality_dielectric@4000','让强场逐级分布到多层约束结构','同心梯度色的紫白层板'),
('composite_microvascular_panel','奇观再构微血管板','composite_rebuild_mesh@8 gtceu:neutronium_small_fluid_pipe@128 composite_interface_veil@4','soulium_precursor_fluid@4000','向受损位置输送可消耗的修复材料','绿色细通道覆盖的银色层板'),
('composite_cognitive_addressor','奇观认知复材寻址网','composite_cognitive_film@8 soulium_data_substrate@32 gtceu:fine_gold_wire@256','gtceu:soldering_alloy@9216','单独访问认知晶粒的状态','金色细线交叉的紫色薄网'),
('composite_pultrusion_die','奇观复材定向拉挤模芯','composite_ceramic_lattice@8 material:soulium/plate@128 gtceu:diamond_dust@128','soulium_process_solvent@4000','保证连续增强纤维沿载荷方向成型','带不同截面孔的厚重模芯'),
('composite_vacuum_bag','奇观复材真空封装袋','gtceu:polybenzimidazole_foil@512 gtceu:polyetheretherketone_foil@256 composite_interface_veil@4','gtceu:polyvinyl_butyral@9216','在固化时形成可密封的真空边界','折叠紫色袋体和抽气接头'),
('composite_co_cured_joint','奇观复材共固化接头','infiltrated_composite_preform@8 composite_soulium_whisker@8 composite_pultrusion_die@2','composite_infiltrant@4000','将不同功能层连接到同一承力接头','叉形复材接头与连续缠绕纹'),
('composite_conduction_insert','奇观导电功能嵌件','composite_current_spreader@8 composite_co_cured_joint@4 composite_vacuum_bag@2','composite_infiltrant@4000','作为现有导电复材的功能主材','蓝银层叠嵌件'),
('composite_confinement_insert','奇观约束功能嵌件','composite_field_grading@8 composite_co_cured_joint@4 composite_vacuum_bag@2','composite_infiltrant@4000','作为现有约束复材的功能主材','白紫分级绝缘嵌件'),
('composite_reconstruction_insert','奇观再构功能嵌件','composite_microvascular_panel@8 composite_co_cured_joint@4 composite_vacuum_bag@2','soulium_precursor_fluid@4000','作为现有再构复材的可补料结构主材','含绿色流道的银色嵌件'),
('composite_cognition_insert','奇观认知功能嵌件','composite_cognitive_addressor@8 composite_co_cured_joint@4 composite_vacuum_bag@2','composite_infiltrant@4000','作为现有认知复材的寻址功能主材','金紫网格覆盖的嵌件'),
('composite_multifunction_seam','奇观异质复材过渡接缝','composite_conductive_tape@4 composite_confinement_ply@4 composite_rebuild_mesh@4 composite_cognitive_film@4','composite_infiltrant@4000','连接四类复材而不在接口集中应力','四种功能色在银白接缝中渐变')
])
output_asset('infiltrated_composite_preform','已浸渗奇观复材预制体','把多孔编织骨架变成可共固化的连续承载复材','银紫编织骨架的孔隙填满半透明金色基体')
recipe('composite_vacuum_infusion','复材预制体真空浸渗','composite_braided_preform@4 composite_vacuum_bag@1','infiltrated_composite_preform@4 composite_offcut@2','composite_infiltrant@4000','spent_composite_infiltrant@4000',ticks=1600,purpose='排出孔隙残留物并固定产出已浸渗预制体，后续共固化直接消耗该物料')
recipe('composite_infiltrant_regeneration','复材浸渗液过滤补充','separation_filter@1 gtceu:fullerene_dust@16','separation_residue@2','spent_composite_infiltrant@4000','composite_infiltrant@3500',ticks=1400,purpose='从负载液中去除孔隙排出物并补充界面聚合物')
recipe('composite_carbon_recovery','复材边角料热解分离','composite_offcut@32','gtceu:carbon_fibers@24 gtceu:zirconium_oxide_dust@16 soulium_swarf@4','gtceu:nitrogen@4000',ticks=1600,purpose='将旧复材边角料分成纤维、氧化物与魂钢屑，原生材料路线仍可首次生产')
recipe('composite_joint_salvage','共固化接头有损拆解','composite_co_cured_joint@2','composite_soulium_whisker@3 composite_interface_veil@1 composite_offcut@4','soulium_process_solvent@4000',ticks=1200,purpose='退役接头回收增强相，主要承载结构在拆解中损耗')
recipe('composite_conductive_strip','导电嵌件剥层回收','composite_conduction_insert@1','composite_current_spreader@1 composite_offcut@4','soulium_process_solvent@2000',ticks=1000,purpose='拆回一半电流扩散层，保留原生功能嵌件制造路径')
link('industrial_composite_conducting','composite_conduction_insert@4',reason='导电复材使用专用导流嵌件')
link('industrial_composite_confining','composite_confinement_insert@4',reason='约束复材使用高场绝缘嵌件')
link('industrial_composite_reconstructing','composite_reconstruction_insert@4',reason='再构复材具有可补料微血管结构')
link('industrial_composite_cognitive','composite_cognition_insert@4',reason='认知复材具有可寻址晶粒和状态网络')
link('industrial_prefabrication','composite_multifunction_seam@8',reason='异质功能复材用过渡接缝连接')

configure('I41', 26, 'RN-CED', 'civilization_grid', '蓝金与深灰')
fluid_asset('spent_grid_arc_medium','负载文明电网灭弧液','697779','含触头烧蚀微粒的灭弧介质过滤后再用')
liquid('grid_arc_medium','文明电网灭弧介质','90B8BF','gtceu:alumina_dust@128 gtceu:zirconium_oxide_dust@128','gtceu:perfluorobenzene@8000 honkai_coolant@8000','在电流分断时冷却电弧并隔绝触头间隙',16000)
parts([
('grid_contact_blank','文明电网耐弧触头坯','gtceu:tungsten_carbide_dust@256 gtceu:silver_dust@256 gtceu:platinum_dust@128','gtceu:argon@8000','耐受文明电网大电流开断时的烧蚀','银色圆触头与深灰基座'),
('grid_arc_chute','文明电网分层灭弧栅','gtceu:alumina_dust@256 gtceu:neutronium_plate@128','grid_arc_medium@2000','将开断电弧分成多个冷却段','交错银白栅片组成的灭弧室'),
('grid_saturable_core','文明电网饱和电抗磁芯','gtceu:magnetic_steel_plate@256 gtceu:niobium_nitride_foil@128','gtceu:reinforced_epoxy_resin@9216','限制短路电流上升速度','双柱灰色磁芯及金色锁扣'),
('grid_insulator_stack','文明电网支柱绝缘堆','gtceu:zirconium_oxide_dust@256 gtceu:polybenzimidazole_plate@256','reality_dielectric@4000','承托高电位母线并延长爬电路径','层叠蓝白伞裙绝缘柱'),
('grid_flexible_bus','文明电网柔性母线带','gtceu:fine_shirabon_wire@512 gtceu:gold_foil@256 gtceu:polyetheretherketone_foil@128','gtceu:polyimide@9216','吸收热胀和安装位移而传输大电流','多层金色柔性编织带'),
('grid_rogowski_coil','文明电网罗氏测流线圈','gtceu:fine_gold_wire@512 gtceu:polyetheretherketone_foil@256 soulium_data_substrate@16','gtceu:polyimide@9216','在无铁芯饱和的条件下测量电流变化','蓝色开口式环形线圈'),
('grid_voltage_divider','文明电网分布电压分压器','gtceu:graphene_foil@256 gtceu:polybenzimidazole_foil@256 gtceu:platinum_foil@128','reality_dielectric@4000','把总线电压按固定比例传给控制电路','长形多段电阻电容柱'),
('grid_grounding_braid','文明电网接地等电位编带','gtceu:fine_gold_wire@512 gtceu:niobium_nitride_foil@256','gtceu:polyimide@4608','把故障返回电流引到指定导体','宽扁金色接地编织带'),
('grid_vacuum_interrupter','文明电网真空分断管','grid_contact_blank@8 grid_arc_chute@4 grid_insulator_stack@4 gtceu:neutronium_ring@64','gtceu:helium@4000','在低气压封装内分断主回路电流','透明蓝色真空管与双银触头'),
('grid_current_limiter','文明电网限流电抗器','grid_saturable_core@4 grid_flexible_bus@8 grid_insulator_stack@4','grid_arc_medium@4000','在保护动作前限制故障电流','双绕组蓝金电抗组件'),
('grid_measurement_frontend','文明电网同步测量前端','grid_rogowski_coil@4 grid_voltage_divider@4 soulium_data_substrate@32 circuit_encapsulation_part@32','gtceu:soldering_alloy@9216','同步采样电流和电压以计算负载状态','带环形测流头的测量板'),
('grid_protection_relay','文明电网差动保护继电器','grid_measurement_frontend@4 etched_circuit_layer@64 circuit_encapsulation_part@32','gtceu:soldering_alloy@18432','比较不同端口的电流并发出分断命令','双端测量插座的保护匣'),
('grid_precharge_resistor','文明电网预充电电阻柱','gtceu:nichrome_plate@256 grid_insulator_stack@4 grid_thermal_bus@2','grid_arc_medium@2000','限制大电容或高能网络接入冲击','多片灰色电阻与蓝色端座'),
('grid_thermal_bus','文明电网液冷导热母座','gtceu:neutronium_plate@256 gtceu:neutronium_small_fluid_pipe@128 gtceu:graphene_foil@256','gtceu:soldering_alloy@9216','将大电流连接处热量送入冷却液','带冷却通道的粗金属母座'),
('grid_earthing_switch','文明电网检修接地开关','grid_contact_blank@8 grid_grounding_braid@8 grid_insulator_stack@4','gtceu:lubricant@2000','在检修时把隔离段可靠接地','金色开合刀闸与接地带'),
('grid_bus_coupler','文明电网分段母联','grid_flexible_bus@8 grid_vacuum_interrupter@4 grid_current_limiter@2 grid_thermal_bus@4','grid_arc_medium@4000','让独立母线分段受控并联','两组金色母排之间的开关桥'),
('grid_transfer_switch','文明电网无扰切换组件','grid_bus_coupler@2 grid_protection_relay@4 grid_precharge_resistor@4','grid_arc_medium@4000','在稳定测量和预充电后切换供电通道','三路功率接口的蓝金切换组件'),
('grid_load_scheduler','文明电网负载调度板','grid_protection_relay@4 grid_measurement_frontend@4 soulium_data_substrate@64 circuit_encapsulation_part@32','gtceu:soldering_alloy@18432','按实测负载分配可用电网容量','多测量接口和中央调度电路'),
('grid_power_quality_filter','文明电网谐波滤波组','grid_saturable_core@8 grid_voltage_divider@4 grid_thermal_bus@4 gtceu:polybenzimidazole_foil@256','grid_arc_medium@4000','降低开关负载引起的谐波和尖峰','电抗器与电容并排的滤波架'),
('grid_fault_locator','文明电网故障区段定位器','grid_measurement_frontend@4 grid_protection_relay@4 grid_load_scheduler@2','gtceu:soldering_alloy@18432','用两端测量定位应隔离的电网区段','多端测量线连接的定位匣'),
('grid_dispatch_cabinet_core','文明能源调度柜芯','grid_load_scheduler@4 grid_transfer_switch@4 grid_fault_locator@2 grid_earthing_switch@4 grid_regenerative_buffer@2','grid_arc_medium@4000','作为现行文明能源调度工艺的实际电力控制核心','蓝金分区柜芯与粗母线端口'),
('grid_polarization_feeder','电磁材料脉冲馈电组件','grid_bus_coupler@4 grid_current_limiter@4 grid_power_quality_filter@2 grid_thermal_bus@4','grid_arc_medium@4000','给电磁材料极化提供受控电流脉冲','环形馈电母排与液冷底座'),
('grid_wonder_bus_interface','奇观工程电网接口','grid_dispatch_cabinet_core@2 grid_power_quality_filter@4 grid_earthing_switch@4','grid_arc_medium@4000','让奇观预制件接入受保护的文明电网','四向金色总线与蓝色绝缘座'),
('grid_regenerative_buffer','文明电网回馈缓冲组件','grid_precharge_resistor@4 grid_transfer_switch@4 grid_voltage_divider@8 grid_thermal_bus@4','grid_arc_medium@4000','缓冲工业设备停机时返还的电磁能','液冷缓冲电阻与分段开关匣')
])
recipe('grid_arc_chamber_service','分断管退役排液拆检','grid_vacuum_interrupter@2','grid_arc_chute@1 grid_insulator_stack@1','grid_arc_medium@4000','spent_grid_arc_medium@4000',ticks=1400,purpose='实际服役分断管拆检产生含触头金属的灭弧液')
recipe('grid_arc_medium_regeneration','灭弧介质金属微粒分离','separation_filter@1 process_gas_filter@1','separation_residue@2 depleted_gas_filter@1','spent_grid_arc_medium@4000','grid_arc_medium@3500',ticks=1400,purpose='去除烧蚀导电颗粒使灭弧介质可再次使用')
recipe('grid_contact_metals','耐弧触头金属回收','grid_contact_blank@4','gtceu:silver_dust@160 gtceu:tungsten_carbide_dust@160 gtceu:platinum_dust@64','gtceu:hydrochloric_acid@4000',ticks=1200,purpose='触头退役回收贵金属与碳化物，保持烧蚀损耗')
recipe('grid_reactor_rewind','限流电抗器解绕','grid_current_limiter@2','grid_saturable_core@1 grid_flexible_bus@3','soulium_process_solvent@2000',ticks=1200,purpose='退役电抗器拆回磁芯和部分柔性母线')
recipe('grid_cabinet_salvage','调度柜芯模块拆回','grid_dispatch_cabinet_core@1','grid_protection_relay@2 grid_measurement_frontend@2 circuit_encapsulation_part@8','soulium_process_solvent@2000',ticks=1200,purpose='柜芯替换后保留部分仍可用的保护与计量模块')
link('industrial_dispatch_conductor','grid_dispatch_cabinet_core@2 grid_polarization_feeder@2',reason='电磁极化使用有测量、限流和保护的调度功率链')
link('industrial_prefabrication','grid_wonder_bus_interface@4',reason='奇观预制件包含受保护的电网接口')

configure('I42', 27, 'RN-WPF', 'wonder_prefabrication', '白银与琥珀金')
fluid_asset('spent_prefab_bonding_bath','负载奇观接合活化液','80705A','收集接合表面的氧化物并回收活化介质')
liquid('prefab_bonding_bath','奇观接合界面活化液','D9B76C','gtceu:sodium_hydroxide_dust@128 gtceu:zirconium_oxide_dust@128','soulium_process_solvent@8000 gtceu:grade_16_purified_water@16000','清除异质复材接合面的弱界面层并活化后续灌注',24000)
parts([
('prefab_truss_web','奇观预制桁架腹板','conducting_composite@16 reconstructing_composite@16 material:soulium/plate@128','soulium_protective_gas@8000','把奇观载荷分到桁架梁的腹板结构','带三角孔的白银腹板'),
('prefab_multiaxis_node','奇观多轴桁架节点','confining_composite@16 reconstructing_composite@16 gtceu:neutronium_screw@128','prefab_bonding_bath@2000','用独立可拆接口汇合多个承力方向','八向伸出的银色桁架球节点'),
('prefab_service_duct','奇观分舱维护导槽','material:soulium/plate@128 gtceu:polybenzimidazole_plate@256 gtceu:neutronium_ring@64','gtceu:polyimide@9216','让维护线路与高能工艺空间分舱通过','带多格隔板的金属导槽'),
('prefab_cooling_header','奇观液冷分配总管','gtceu:neutronium_large_fluid_pipe@64 gtceu:neutronium_small_fluid_pipe@128 confining_composite@16','gtceu:soldering_alloy@18432','把冷却介质按支路分给预制模块','宽体银色总管与多个液口'),
('prefab_radiation_laminate','奇观辐射屏蔽层板','gtceu:neutronium_plate@256 confining_composite@16 gtceu:polybenzimidazole_foil@256','prefab_bonding_bath@2000','在可拆层板中分级吸收高能辐射','白金多层厚重屏蔽板'),
('prefab_kinematic_foot','奇观可调运动学支座','gtceu:transcendentmetal_ring@128 gtceu:neutronium_bolt@128 reconstructing_composite@16','gtceu:lubricant@4000','在固定重载的同时提供确定安装基准','三点金色球头支座'),
('prefab_robot_service_rail','奇观维护机械导轨','gtceu:transcendentmetal_rod@128 gtceu:small_transcendentmetal_gear@128 material:soulium/plate@128','gtceu:lubricant@4000','让维修执行器在奇观模块之间通行','两根银色导轨与齿条'),
('prefab_power_bus_section','奇观预制供能母线段','conducting_composite@32 gtceu:fine_shirabon_wire@512 confining_composite@16','gtceu:polyimide@18432','把导电与绝缘复材组合成可拼接供能段','金色粗母线与白色绝缘支架'),
('prefab_optical_bus_section','奇观预制光总线段','cognitive_composite@16 gtceu:fine_borosilicate_glass_wire@512 gtceu:polyetheretherketone_foil@256','gtceu:polyimide@9216','将认知层与实体光纤接到统一数据接口','金白端口间的青色光纤束'),
('prefab_utility_cassette','奇观公用工程接口匣','prefab_service_duct@4 prefab_cooling_header@4 prefab_power_bus_section@4 prefab_optical_bus_section@4','prefab_bonding_bath@4000','把电力、流体和数据接口集中到可替换单元','三色接口并排的银白工业匣'),
('prefab_field_mount','奇观约束场安装座','confining_composite@32 prefab_multiaxis_node@4 gtceu:transcendentmetal_ring@128','reality_dielectric@4000','在承力结构中固定强场组件','白色圆环与多向金属支撑'),
('prefab_vacuum_joint','奇观真空分舱密封环','gtceu:polybenzimidazole_foil@512 gtceu:neutronium_ring@128 prefab_radiation_laminate@4','gtceu:helium@8000','让可拆模块连接后仍保持真空边界','厚重银环夹持多道白色密封唇'),
('prefab_lifting_lug','奇观模块吊装耳','material:soulium/plate@128 gtceu:neutronium_bolt@128 prefab_multiaxis_node@4','prefab_bonding_bath@2000','把吊装载荷传到主体桁架节点','双孔银白承载吊耳'),
('prefab_repair_sleeve','奇观再构接合套','reconstructing_composite@32 activated_prefab_truss_web@4 gtceu:neutronium_small_fluid_pipe@128','soulium_precursor_fluid@4000','给接缝保留可补充的修复材料通道','带绿色细流道的对开连接套'),
('prefab_thermal_break','奇观结构断热连接件','gtceu:zirconium_carbide_plate@256 prefab_kinematic_foot@4 confining_composite@16','prefab_bonding_bath@2000','在传递载荷时隔开不同温区','白色陶瓷芯连接的金属双头接件'),
('prefab_instrument_panel','奇观分区仪控面板','cognitive_composite@32 soulium_data_substrate@64 circuit_encapsulation_part@64','gtceu:soldering_alloy@18432','让模块传感与执行接口接入文明控制','多排琥珀色接口的仪控板'),
('prefab_alignment_prism','奇观安装测量基准棱镜','gtceu:sapphire_lens@32 material:soulium/plate@64 gtceu:platinum_foil@128','prefab_bonding_bath@2000','在大型安装时提供可复测的光学基准','三面金色固定座中的透明棱镜'),
('prefab_installation_sled','奇观模块装配滑台','prefab_robot_service_rail@8 prefab_kinematic_foot@8 prefab_lifting_lug@4 prefab_alignment_prism@4','gtceu:lubricant@8000','把重型模块平稳移入并对准安装位置','双轨银色滑台与金色定位点'),
('prefab_pipe_quick_coupler','奇观流体双截止接头','prefab_cooling_header@4 prefab_vacuum_joint@4 gtceu:neutronium_small_fluid_pipe@128','prefab_bonding_bath@4000','拆换模块时关闭两侧流路减少介质损失','双阀短管与对接法兰'),
('prefab_load_spreader','奇观基础载荷分散板','activated_prefab_truss_web@8 prefab_multiaxis_node@8 prefab_thermal_break@4','prefab_bonding_bath@4000','把上部奇观集中载荷扩散到基础','交叉银色肋梁的厚底板'),
('prefab_structural_carrier','奇观预制结构载体','prefab_load_spreader@4 prefab_repair_sleeve@8 prefab_field_mount@4 prefab_radiation_laminate@8','prefab_bonding_bath@4000','承托供能、场约束与维护接口模块','白金三维空间桁架载体'),
('prefab_service_module','奇观预制公用工程模块','prefab_utility_cassette@4 prefab_pipe_quick_coupler@8 prefab_instrument_panel@4 prefab_service_duct@8','prefab_bonding_bath@4000','为现行奇观预制件提供完整运行接口','带多色工程端口的分舱模块'),
('prefab_installation_pack','奇观模块安装工装组','prefab_installation_sled@2 prefab_alignment_prism@8 prefab_lifting_lug@8 prefab_robot_service_rail@8','gtceu:lubricant@8000','作为首座奇观控制器制造的可消耗安装工装','金白工具架中的滑台和定位棱镜'),
('prefab_foundation_interface','奇观基础综合接口','prefab_structural_carrier@2 prefab_service_module@2 prefab_vacuum_joint@8 prefab_kinematic_foot@8','prefab_bonding_bath@8000','将奇观承载、分舱和公用工程统一接入','宽底白银基础模块和金色接口')
])
output_asset('activated_prefab_truss_web','界面已活化的奇观桁架腹板','去除弱界面层后才能与载荷板和再构套形成连续接合','白银腹板的接合边缘可见琥珀色活化层')
recipe('prefab_surface_activation','预制桁架接合面活化','prefab_truss_web@4','activated_prefab_truss_web@4 soulium_swarf@8','prefab_bonding_bath@4000','spent_prefab_bonding_bath@4000',ticks=1600,purpose='固定产出界面已活化腹板供承载接合使用，弱表层移出活化浴液')
recipe('prefab_bath_regeneration','奇观接合活化液再生','separation_filter@2 gtceu:sodium_hydroxide_dust@16','separation_residue@4','spent_prefab_bonding_bath@8000','prefab_bonding_bath@7000',ticks=1600,purpose='过滤氧化物并补充活化剂，循环路线降低溶剂投入')
recipe('prefab_carrier_teardown','预制结构载体退役拆解','prefab_structural_carrier@1','prefab_multiaxis_node@2 prefab_repair_sleeve@1 composite_offcut@8','soulium_process_solvent@4000',ticks=1400,purpose='大型载体拆回可用连接节点及接合套')
recipe('prefab_utility_reclaim','公用工程模块接口回收','prefab_service_module@1','prefab_cooling_header@2 prefab_instrument_panel@1 prefab_optical_bus_section@1','soulium_process_solvent@4000',ticks=1400,purpose='退役公用工程模块回收尚可用的液路和仪控部分')
recipe('prefab_joint_remanufacture','分舱密封环金属件回收','prefab_vacuum_joint@4','gtceu:neutronium_ring@80 composite_offcut@4','soulium_process_solvent@4000',ticks=1200,purpose='损耗密封聚合物并回收部分中子素环')
link('industrial_prefabrication','prefab_structural_carrier@4 prefab_service_module@4',reason='现行奇观预制件包含实际结构载体与公用工程模块')
link('approved_wonder_k01','prefab_installation_pack@32 prefab_foundation_interface@64',reason='首座奇观控制器包含安装工装和综合基础，制造首源全部位于I42内')

configure('I43', 29, 'RN-CEE', 'engineering_metrology', '铂银与青紫')
fluid_asset('spent_metrology_couplant','负载工程超声耦合液','647586','清除无损检测接触界面带入的微粒后回收')
liquid('metrology_couplant','工程级超声耦合液','8CC9DD','gtceu:alumina_dust@64 gtceu:zirconium_oxide_dust@64','gtceu:ethyleneglycol@16000 gtceu:grade_16_purified_water@16000','排除探头与工件间空气使超声能量传入实体内部',32000)
parts([
('metrology_gauge_block','魂钢量块坯件','material:soulium/plate@128 gtceu:diamond_dust@128','soulium_process_solvent@4000','为精密长度基准提供保留研合余量的尺寸坯件','带平行磨削纹的银白长方体坯件'),
('interferometer_optical_reference_flat','工程级干涉光学平晶','gtceu:quartzite_plate@256 gtceu:cerium_oxide_dust@128','gtceu:grade_16_purified_water@16000','用干涉条纹检查大平面形状','带银色护框的透明圆平晶'),
('metrology_acoustic_wedge','无损检测折射楔块','gtceu:polyetheretherketone_plate@256 gtceu:sapphire_lens@16','metrology_couplant@2000','把纵向超声按确定角度耦合进工件','青色透明斜楔与定位刻面'),
('metrology_piezo_array','工程相控压电晶片阵列','gtceu:quartzite_plate@256 gtceu:platinum_foil@256 soulium_data_substrate@32','gtceu:polyimide@9216','独立激励多个声束以扫描工件内部','整齐排列的紫色小晶片阵列'),
('metrology_scintillator_tile','工程射线闪烁探测片','gtceu:alumina_dust@256 gtceu:zirconium_oxide_dust@256 gtceu:europium_plate@64','gtceu:argon@8000','将透过工件的高能射线变为可读光信号','淡紫发光晶片与银色边框'),
('metrology_collimator_grid','工程射线准直栅','gtceu:neutronium_plate@256 gtceu:neutronium_foil@256','soulium_protective_gas@8000','限制检测射线角度以减少散射假像','深银色密集准直孔栅'),
('metrology_eddy_probe','工程涡流检测线圈','gtceu:fine_platinum_wire@512 gtceu:zirconium_oxide_dust@128 etched_circuit_layer@32','gtceu:polyimide@9216','读取导电材料表面裂纹造成的阻抗变化','扁平双线圈与陶瓷探头'),
('metrology_flux_pickup','工程漏磁拾取阵列','gtceu:magnetic_neodymium_rod@128 gtceu:fine_gold_wire@256 soulium_data_substrate@32','gtceu:polyimide@9216','检测铁磁构件缺陷附近的磁通泄漏','白色探头上并列的磁极与传感片'),
('metrology_load_cell','工程载荷测量单元','material:soulium/plate@128 gtceu:graphene_foil@256 gtceu:fine_platinum_wire@256','gtceu:polyimide@9216','把实体构件变形变成可计量载荷','银白剪切梁与青色应变桥'),
('metrology_reference_resistor','工程四端参考电阻','gtceu:graphene_foil@256 gtceu:platinum_foil@256 gtceu:polybenzimidazole_plate@256','reality_dielectric@4000','作为大电流四线法测量的可重复参考','四只金属端子的陶瓷电阻块'),
('cryogenic_metrology_reference','工程低温温差参考模块','gtceu:platinum_foil@256 gtceu:fine_platinum_wire@256 gtceu:zirconium_carbide_plate@128','gtceu:polyimide@9216','为低温多点测量提供共同温差参考端','隔热白瓷座中的铂线束'),
('metrology_autocollimator','工程自准直测角头','interferometer_optical_reference_flat@4 gtceu:sapphire_lens@32 soulium_data_substrate@32','gtceu:soldering_alloy@18432','通过反射光测量大型结构角度偏差','长形银色光学镜筒和青色窗口'),
('metrology_ultrasonic_array','工程相控阵超声探头','metrology_piezo_array@8 metrology_acoustic_wedge@4 circuit_encapsulation_part@32','metrology_couplant@4000','以多角度声束检查复材层间和焊缝','多通道青紫超声探头'),
('metrology_radiography_head','工程射线成像探测头','metrology_scintillator_tile@8 metrology_collimator_grid@4 soulium_data_substrate@64','gtceu:polyimide@18432','按实体透射强度重建内部密度分布','带银色准直栅的面阵探测盒'),
('metrology_electromagnetic_head','工程电磁缺陷检测头','metrology_eddy_probe@8 metrology_flux_pickup@4 circuit_encapsulation_part@32','gtceu:soldering_alloy@18432','联合检测导体表面裂纹和磁性构件内部变化','并排线圈与磁极的检测头'),
('metrology_synchronous_digitizer','工程同步采样仪板','soulium_data_substrate@64 etched_circuit_layer@64 circuit_encapsulation_part@64 gtceu:gold_foil@256','gtceu:soldering_alloy@18432','让不同传感器的检测波形共享采样时刻','多路青紫采样输入与中央时钟板'),
('metrology_acoustic_beamformer','工程声束合成处理器','metrology_synchronous_digitizer@4 metrology_piezo_array@4 soulium_data_substrate@64','gtceu:soldering_alloy@18432','对多个超声通道做实体探头延时控制','带多路相位输出的银紫处理板'),
('metrology_fourwire_meter','工程四线功率测量匣','metrology_reference_resistor@8 metrology_synchronous_digitizer@4 cryogenic_metrology_reference@4','gtceu:soldering_alloy@18432','用独立电压引线排除大电流接触电阻影响','粗电流端与细测量端分置的测量匣'),
('metrology_interferometer','大型工程激光干涉仪','metrology_autocollimator@4 interferometer_optical_reference_flat@8 metrology_synchronous_digitizer@4 metrology_lapped_gauge_block@8','stable_transport_medium@4000','将大尺度装配长度与角度变成可复测量','双臂光路与银白基座'),
('metrology_structural_test_rig','工程载荷闭环试验组件','metrology_load_cell@8 metrology_lapped_gauge_block@8 metrology_synchronous_digitizer@4','gtceu:soldering_alloy@18432','用实体载荷和位移同时测量结构刚度','四向加载梁和中部测力块'),
('metrology_ndt_cartridge','文明工程无损检测仪匣','metrology_ultrasonic_array@4 metrology_radiography_head@4 metrology_electromagnetic_head@4 metrology_acoustic_beamformer@2','metrology_couplant@8000','作为旧四接口分析使用的可重复无损检测仪器','分舱容纳三种检测头的银色仪器匣'),
('metrology_geometry_reference','文明工程空间计量组件','metrology_interferometer@2 metrology_structural_test_rig@2 metrology_lapped_gauge_block@16','stable_transport_medium@4000','给边界结果验证提供真实空间与结构基准','激光镜组和载荷基准围成的框架'),
('metrology_energy_reference','文明工程能流计量组件','metrology_fourwire_meter@4 cryogenic_metrology_reference@8 metrology_synchronous_digitizer@4','honkai_coolant@4000','为矛盾复核提供相互独立的电能与热量测量','水冷测量母座与青紫采样板'),
('metrology_order_recorder','文明工程同步时序记录器','metrology_synchronous_digitizer@8 metrology_acoustic_beamformer@4 soulium_data_substrate@128 circuit_encapsulation_part@64','gtceu:soldering_alloy@36864','从机器实体传感器记录操作与响应的先后顺序','多通道时间输入与分层存储匣')
])
recipe('metrology_couplant_service','无损检测仪匣耦合液维护','metrology_ndt_cartridge@1','metrology_ultrasonic_array@1 circuit_encapsulation_part@8','metrology_couplant@8000','spent_metrology_couplant@8000',ticks=1600,purpose='服役检测仪匣拆检回收探头，同时产生带界面杂质的实际废液')
recipe('metrology_couplant_regeneration','工程超声耦合液过滤脱气','separation_filter@2 process_gas_filter@1','separation_residue@2 depleted_gas_filter@1','spent_metrology_couplant@8000','metrology_couplant@7000',ticks=1600,purpose='移出检测界面微粒和气泡，回收大部分耦合液')
output_asset('metrology_lapped_gauge_block','已研合魂钢精密量块','经定向研合获得平行工作面，作为精密仪器的实体长度基准','银白长方体两端为清晰平整镜面并带青紫护套')
recipe('metrology_gauge_relap','魂钢量块定向精密研合','metrology_gauge_block@4 gtceu:diamond_dust@16','metrology_lapped_gauge_block@3 soulium_swarf@4','soulium_process_solvent@2000',ticks=1200,purpose='从尺寸坯件固定产出带平行研合面的精密量块，精加工有实际材料损耗')
recipe('metrology_optics_salvage','干涉仪光学件拆检','metrology_interferometer@1','interferometer_optical_reference_flat@2 metrology_gauge_block@2 soulium_data_substrate@8','soulium_process_solvent@2000',ticks=1200,purpose='退役光学计量仪保留平晶和长度基准')
recipe('metrology_platinum_reclaim','参考温差组件铂回收','cryogenic_metrology_reference@4','gtceu:platinum_dust@72 gtceu:zirconium_carbide_dust@64','gtceu:hydrochloric_acid@4000',ticks=1200,purpose='回收铂引线和陶瓷支撑，箔片与细线按材料量折算后保留损耗')
link('industrial_lab_four_interface_analysis',catalysts='metrology_ndt_cartridge@1',reason='四接口分析实际使用可复用的超声、射线与电磁无损检测仪匣')
link('industrial_bounded_result_verification',catalysts='metrology_geometry_reference@1',reason='有界结果验证使用实体空间和载荷计量基准')
link('industrial_contradiction_review',catalysts='metrology_energy_reference@1',reason='矛盾复核通过独立电能与热量计量排查能流差异')
link('industrial_cross_machine_order_verification',catalysts='metrology_order_recorder@1',reason='跨机器顺序验证需要真实多通道时序记录器')

configure('I44', 20, 'RN-CJK', 'thousand_realms_beacon', '紫金与月白')
fluid_asset('spent_beacon_phase_bath','失活千界相位调谐液','706378','收集调谐期间界面脱落物并回收稳定介质')
liquid('beacon_phase_bath','千界相位调谐液','B9A1E1','gtceu:zirconium_oxide_dust@128 gtceu:hafnium_oxide_dust@128','stable_transport_medium@8000 honkai_stabilization_medium@8000','为信标共振腔提供可控介电界面并稳定发射相位',16000)
parts([
('beacon_quartz_reference','千界信标晶体频率基准','gtceu:quartzite_plate@128 gtceu:platinum_foil@128','gtceu:grade_16_purified_water@8000','为信标发射与测距提供稳定频率','金色支架中的月白晶体'),
('beacon_slot_waveguide','千界信标缝隙波导','gtceu:niobium_nitride_foil@256 gtceu:gold_foil@128 material:soulium/plate@32','beacon_phase_bath@1000','沿确定的几何路径输送信标激励波','带均匀狭缝的紫金长波导'),
('beacon_horn_element','千界信标喇叭馈源','material:soulium/plate@64 gtceu:gold_foil@128 gtceu:neutronium_ring@32','beacon_phase_bath@1000','将波导内的激励波变为定向空间波束','金色扩口锥形馈源'),
('beacon_lens_stack','千界信标介质透镜组','gtceu:sapphire_lens@32 gtceu:hafnium_oxide_dust@128 gtceu:quartzite_plate@128','beacon_phase_bath@2000','按波前需求整形信标波束','多层月白弧面透镜'),
('beacon_phase_shifter','千界信标移相单元','gtceu:niobium_nitride_foil@256 gtceu:graphene_foil@128 etched_circuit_layer@16','beacon_phase_bath@2000','对单个阵元施加可调相位延迟','带紫色分段微带的金色电路片'),
('beacon_impedance_bridge','千界信标阻抗测量桥','gtceu:fine_platinum_wire@256 gtceu:graphene_foil@128 soulium_data_substrate@16','gtceu:soldering_alloy@4608','读取馈源阻抗并识别腔体失谐','四端金色测量桥'),
('beacon_cryogenic_plate','千界信标低温热基板','gtceu:neutronium_plate@128 gtceu:neutronium_small_fluid_pipe@64 gtceu:graphene_foil@128','gtceu:soldering_alloy@9216','降低接收前端热噪声并引出腔体热量','银白冷板与紫色温度传感点'),
('beacon_magnetic_lens','千界信标束流磁透镜','gtceu:magnetic_neodymium_rod@128 gtceu:fine_niobium_titanium_wire@256 gtceu:niobium_nitride_foil@128','beacon_phase_bath@2000','用受控磁场约束激励能流方向','金色极靴围成的紫色磁透镜'),
('beacon_timing_board','千界信标同步触发板','beacon_quartz_reference@4 etched_circuit_layer@32 circuit_encapsulation_part@16','gtceu:soldering_alloy@9216','令所有信标阵元在相同时刻更新相位','中央晶体向四周扇出的金色触发板'),
('beacon_resonant_cavity','千界信标高稳共振腔','beacon_slot_waveguide@4 beacon_horn_element@4 beacon_cryogenic_plate@2 gtceu:neutronium_ring@64','beacon_phase_bath@2000','在可控几何腔内积累稳定发射波','紫色圆腔与金色馈源端口'),
('beacon_phased_array','千界信标相控阵面','beacon_horn_element@8 beacon_phase_shifter@8 beacon_slot_waveguide@4 beacon_lens_stack@4','beacon_phase_bath@4000','通过阵元相位改变信标波束方向','金色喇叭阵元排列的紫白阵面'),
('beacon_focus_servo','千界信标聚焦伺服器','beacon_magnetic_lens@4 beacon_impedance_bridge@4 beacon_timing_board@2','gtceu:soldering_alloy@9216','按阻抗与回波修正聚焦能流','金色线圈与双侧控制匣'),
('beacon_echo_receiver','千界信标低噪回波接收器','beacon_cryogenic_plate@4 beacon_lens_stack@4 soulium_data_substrate@32 circuit_encapsulation_part@16','gtceu:polyimide@9216','读取跨界返回信号并控制热噪声','深紫遮光口与月白冷却外壳'),
('beacon_signal_correlator','千界信标相关测距电路','beacon_timing_board@4 beacon_echo_receiver@2 etched_circuit_layer@32 soulium_data_substrate@32','gtceu:soldering_alloy@9216','比较发射序列和回波序列得到传播时延','双通道金色数据线的紫色电路板'),
('beacon_address_memory','千界信标航路地址存储器','soulium_data_substrate@32 circuit_encapsulation_part@32 gtceu:niobium_nitride_foil@256','gtceu:soldering_alloy@9216','保存已解析航路坐标供实体设备调用','带多层紫色存储芯片的金色底板'),
('beacon_angle_encoder','千界信标方位编码环','material:soulium/plate@64 gtceu:platinum_foil@128 beacon_impedance_bridge@4','beacon_phase_bath@2000','将波束扫描方位反馈到控制器','银白刻槽环与金色拾取头'),
('beacon_kinematic_mount','千界信标精密安装基座','material:soulium/plate@128 gtceu:transcendentmetal_ring@64 gtceu:neutronium_screw@64','gtceu:lubricant@2000','给光学、共振腔和阵面提供共同基准','三点调节的紫金安装架'),
('beacon_isolation_enclosure','千界信标双层隔离罩','gtceu:polybenzimidazole_plate@256 gtceu:niobium_nitride_foil@256 beacon_cryogenic_plate@2','gtceu:helium@4000','隔开高能发射级与低噪接收级','月白双层金属罩和紫色隔离环'),
('beacon_emission_core','千界信标定向发射组件','tuned_beacon_cavity@4 beacon_phased_array@4 beacon_focus_servo@2 beacon_kinematic_mount@4','beacon_phase_bath@4000','把共振、整形与相位控制组合为实体发射级','紫金共振腔连接金色阵面'),
('beacon_scan_head','千界信标全向扫描头','beacon_phased_array@4 beacon_angle_encoder@4 beacon_kinematic_mount@4 beacon_isolation_enclosure@2','beacon_phase_bath@4000','对未确认方位逐步搜索有效回波','多面紫金阵列围绕月白转轴'),
('beacon_tracking_head','千界信标锁定跟踪组件','beacon_emission_core@2 beacon_scan_head@2 beacon_signal_correlator@4 beacon_echo_receiver@4','beacon_phase_bath@4000','为原强化信标工艺提供真正的扫描与锁定前端','双层阵面围绕紫色跟踪核心'),
('beacon_reference_rack','千界信标相位参考架','beacon_quartz_reference@8 beacon_impedance_bridge@4 beacon_timing_board@4 beacon_kinematic_mount@4','beacon_phase_bath@4000','在信标工艺中反复使用的相位与几何参考','金色支架中的晶体与测量桥'),
('beacon_navigation_transponder','千界导航应答组件','beacon_signal_correlator@4 beacon_address_memory@8 beacon_echo_receiver@4 circuit_encapsulation_part@32','gtceu:soldering_alloy@18432','让列车根据已登记航路发射询问并取得测距回执','月白收发窗口与紫金存储匣'),
('beacon_timing_distributor','千界航路同步分配组件','beacon_timing_board@8 beacon_address_memory@4 beacon_slot_waveguide@8','gtceu:soldering_alloy@18432','向航路中继分发统一的信标时基与地址','多个金色波导端口与紫色同步核心')
])
output_asset('tuned_beacon_cavity','已调谐千界信标共振腔','将共振频率锁定到信标基准后才可组成定向发射组件','紫金圆腔中嵌入金白调谐片和闭合相位环')
recipe('beacon_cavity_tuning','千界共振腔湿式调谐','beacon_resonant_cavity@4','tuned_beacon_cavity@4 soulium_swarf@4','beacon_phase_bath@4000','spent_beacon_phase_bath@4000',ticks=1600,purpose='固定产出已完成频率调谐的共振腔供发射级装配，微调接触层进入废液')
recipe('beacon_phase_bath_regeneration','千界相位调谐液过滤再生','separation_filter@1 gtceu:zirconium_oxide_dust@16','separation_residue@2','spent_beacon_phase_bath@4000','beacon_phase_bath@3500',ticks=1400,purpose='去除界面颗粒并补充介电组分，循环路线节省稳定介质')
recipe('beacon_array_salvage','信标相控阵面拆解','beacon_phased_array@2','beacon_horn_element@3 beacon_phase_shifter@3 beacon_lens_stack@1','soulium_process_solvent@2000',ticks=1000,purpose='退役阵面拆出部分馈源和移相器，原生阵面制造提供首次来源')
recipe('beacon_reference_crystal_salvage','信标参考架回收晶体','beacon_reference_rack@1','beacon_quartz_reference@1 beacon_kinematic_mount@1','soulium_process_solvent@2000',ticks=1000,purpose='停役参考架保留频率晶体和机械安装基准')
recipe('beacon_waveguide_gold_recovery','千界波导镀层回收','beacon_slot_waveguide@4','gtceu:gold_dust@24 gtceu:niobium_nitride_foil@128 soulium_swarf@4','gtceu:hydrochloric_acid@4000',ticks=1200,purpose='拆解退役波导回收镀金和部分屏蔽箔，金箔按材料量折算')
link('industrial_enhanced_beacon_signal','beacon_tracking_head@2',catalysts='beacon_reference_rack@1',reason='强化信标有真实的波束跟踪前端和可重复使用的相位基准')
link('industrial_train_navigation_module','beacon_navigation_transponder@2',reason='列车通过实体信标应答器获取航路距离和地址')
link('industrial_route_relay_module','beacon_timing_distributor@2',reason='中继直接接收千界信标的同步时基')

configure('I45', 20, 'RN-CJK', 'thousand_realms_train', '月白、金色与深紫')
fluid_asset('spent_train_damping_fluid','失效千界悬置阻尼液','756C85','收集跨界悬置服役中的磨粒并进入过滤回收')
liquid('train_damping_fluid','千界跨界悬置阻尼液','C4B0DA','gtceu:zirconium_oxide_dust@128 gtceu:graphene_dust@128','gtceu:lubricant@16000 stable_transport_medium@8000','让跨界车载悬置吸收姿态扰动并将热量送至冷却支路',24000)
parts([
('train_inertial_proofmass','千界列车惯性测量质量块','gtceu:neutronium_plate@128 gtceu:platinum_foil@128','soulium_protective_gas@4000','为加速度测量提供确定的惯性质量','银色中心质量块与紫金框架'),
('train_gyro_ring','千界列车光纤陀螺环','gtceu:fine_borosilicate_glass_wire@512 gtceu:polyetheretherketone_foil@256 gtceu:gold_foil@128','gtceu:polyimide@9216','通过双向光程差读取车体角速度','月白环架中的青紫光纤线圈'),
('train_flexure_pivot','千界列车柔性悬置铰','material:soulium/plate@64 gtceu:niobium_titanium_plate@128','train_damping_fluid@2000','在没有滑动间隙的条件下允许小角度摆动','交叉薄片组成的金属柔性铰'),
('train_damper_piston','千界列车阻尼活塞','gtceu:neutronium_rod@128 gtceu:polybenzimidazole_foil@256 gtceu:neutronium_ring@64','gtceu:lubricant@4000','通过可控节流把悬置振动转成热量','紫金活塞与银白节流孔盘'),
('train_electromagnetic_shoe','千界列车电磁导向靴','gtceu:fine_niobium_titanium_wire@512 gtceu:niobium_nitride_foil@256 gtceu:magnetic_steel_plate@128','gtceu:reinforced_epoxy_resin@9216','对车体产生小幅可控横向导向力','月白靴形磁路与紫色线圈'),
('train_thermal_strap','千界列车柔性热桥','gtceu:graphene_foil@256 gtceu:carbon_fiber_mesh@256 gtceu:neutronium_foil@128','gtceu:polyimide@9216','跨过活动悬置导出车载仪器余热','银黑编织的弯曲宽热带'),
('train_hermetic_socket','千界列车密封舱接口','gtceu:neutronium_ring@128 gtceu:polybenzimidazole_plate@256 gtceu:neutronium_screw@128','gtceu:helium@8000','在车载分舱间传输介质并维持隔离','金色密封法兰与白色绝缘端口'),
('train_shielded_data_harness','千界列车屏蔽数据线束','gtceu:fine_gold_wire@512 gtceu:niobium_nitride_foil@256 gtceu:polyetheretherketone_foil@256','gtceu:polyimide@9216','防止导向线圈对导航数据线产生干扰','紫白编织线束和金色多针插头'),
('train_accelerometer','千界列车三轴加速度计','train_inertial_proofmass@4 train_flexure_pivot@8 soulium_data_substrate@32','gtceu:soldering_alloy@9216','读取车体在三方向的实际加速度','三轴银色敏感块与紫色电路盒'),
('train_inertial_unit','千界列车惯性测量单元','train_accelerometer@4 train_gyro_ring@4 train_shielded_data_harness@4 circuit_encapsulation_part@32','gtceu:soldering_alloy@18432','在信标暂时遮挡时维持相对姿态与速度测量','三环陀螺围绕中央惯性质量'),
('train_suspension_cylinder','千界列车跨界悬置筒','train_damper_piston@4 train_flexure_pivot@4 gtceu:neutronium_small_fluid_pipe@128','train_damping_fluid@4000','让跨界姿态扰动经过受控阻尼传到车体','月白密封筒与紫金活塞杆'),
('train_guidance_actuator','千界列车姿态导向器','train_electromagnetic_shoe@4 train_inertial_unit@2 soulium_data_substrate@32','train_damping_fluid@2000','根据惯性反馈调整横向导向磁场','双磁靴与中央导航控制盒'),
('train_thermal_panel','千界列车分舱热管理板','train_thermal_strap@8 gtceu:neutronium_small_fluid_pipe@128 train_hermetic_socket@4','gtceu:soldering_alloy@9216','把导航与货舱的热量送到独立液冷回路','白色微流道板及紫金密封端口'),
('train_cargo_isolator','千界列车货舱隔离座','train_suspension_cylinder@4 train_flexure_pivot@8 gtceu:polybenzimidazole_plate@256','train_damping_fluid@4000','将运输振动和边界扰动隔离于精密货物','四角阻尼支承的月白货舱底座'),
('train_route_computer','千界列车航路计算单元','train_inertial_unit@4 soulium_data_substrate@64 circuit_encapsulation_part@64 gtceu:niobium_nitride_foil@256','gtceu:soldering_alloy@18432','把惯性测量与已知航路坐标组合为导航解','紫色多层处理板与金色数据端口'),
('train_dead_reckoning_board','千界列车推算定位板','train_route_computer@2 train_accelerometer@4 train_gyro_ring@4','gtceu:soldering_alloy@18432','对短时信标遮挡期间的位置变化积分','并列惯性接口与紫金计算板'),
('train_position_fusion','千界列车组合定位器','train_dead_reckoning_board@2 train_route_computer@2 spatial_calibration_module@4','stable_transport_medium@4000','将相对惯性位置与外部空间坐标融合','三路定位输入的金色导航盒'),
('train_safety_brake','千界列车紧急磁制动器','train_electromagnetic_shoe@8 train_suspension_cylinder@4 train_thermal_panel@4','train_damping_fluid@4000','将导向系统的剩余运动能转换到可冷却负载','双侧磁靴和银色水冷制动盘'),
('train_escape_power_bus','千界列车应急供能总线','gtceu:fine_niobium_titanium_wire@512 train_hermetic_socket@8 train_shielded_data_harness@4','gtceu:polyimide@18432','为导航与安全执行器保留独立接线通道','分隔紫金母线与白色绝缘套'),
('train_motion_controller','千界列车姿态稳定控制器','train_guidance_actuator@4 train_position_fusion@2 train_safety_brake@2 train_escape_power_bus@4','gtceu:soldering_alloy@18432','联合处理导航误差、导向和安全制动','紫金控制匣与多组粗功率接口'),
('train_navigation_platform','千界列车组合导航平台','train_inertial_unit@4 train_position_fusion@4 train_motion_controller@2 train_thermal_panel@4','stable_transport_medium@8000','给现行列车导航模组提供完整姿态与位置平台','月白惯性平台围绕金色导航核心'),
('train_boundary_isolation','千界列车跨界隔离组件','train_cargo_isolator@4 train_hermetic_socket@8 train_thermal_panel@4 train_suspension_cylinder@4','train_damping_fluid@8000','使导航设备在边界扰动下保持几何与热稳定','四角悬置支撑的紫白封闭框'),
('train_emergency_controller','千界列车应急回路组件','train_safety_brake@4 train_escape_power_bus@8 train_motion_controller@2 train_shielded_data_harness@8','gtceu:soldering_alloy@18432','在主导航切换时保持安全执行器的独立控制','金色双母线与月白安全控制匣'),
('train_precision_cargo_cradle','千界列车精密工务载架','train_cargo_isolator@8 train_boundary_isolation@2 train_thermal_panel@4 material:soulium/plate@128','train_damping_fluid@8000','为奇观精密预制件提供跨界运输与安装载架','带液冷和四角悬置的月白载货框')
])
recipe('train_suspension_service','千界列车悬置排液维护','train_suspension_cylinder@4','train_damper_piston@3 train_flexure_pivot@2','train_damping_fluid@8000','spent_train_damping_fluid@8000',ticks=1600,purpose='对服役悬置拆检时回收活塞和含磨粒的阻尼液')
recipe('train_damping_fluid_regeneration','千界阻尼液磨粒过滤再生','separation_filter@2 gtceu:graphene_dust@16','separation_residue@4','spent_train_damping_fluid@8000','train_damping_fluid@7000',ticks=1600,purpose='去除悬置磨粒并补充导热润滑组分')
recipe('train_navigation_teardown','组合导航平台退役拆解','train_navigation_platform@1','train_inertial_unit@2 train_thermal_panel@1 circuit_encapsulation_part@8','soulium_process_solvent@2000',ticks=1400,purpose='退役导航平台回收惯性单元与热管理部分')
recipe('train_magnetic_shoe_recovery','电磁导向靴解绕回收','train_electromagnetic_shoe@4','gtceu:fine_niobium_titanium_wire@320 gtceu:magnetic_steel_plate@80','soulium_process_solvent@2000',ticks=1200,purpose='保留导向靴的部分绕组和磁路材料')
recipe('train_cargo_cradle_salvage','精密工务载架卸载拆解','train_precision_cargo_cradle@1','train_cargo_isolator@2 train_hermetic_socket@2 soulium_swarf@16','soulium_process_solvent@4000',ticks=1400,purpose='载架停役后回收部分隔离座和密封接口，结构主体损耗')
link('industrial_train_navigation_module','train_navigation_platform@2 train_boundary_isolation@2 train_emergency_controller@2',reason='列车导航含组合定位、跨界隔离和独立安全回路')
link('industrial_prefabrication','train_precision_cargo_cradle@4',reason='奇观预制件配套可跨界运输的精密工务载架')

if __name__ == '__main__':
    write()
