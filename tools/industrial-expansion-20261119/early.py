import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'src/main/resources/data/hk3gtl/research'
OUT = ROOT / 'deliveries/0003_40台工业内容补全_20261119'
recipes, items, fluids, links = [], [], [], []
plans = {}
approved = json.loads((DATA / 'approved_industrial_processes.json').read_text(encoding='utf-8'))
obsolete_originals = set(approved['superseded_ids']) | set(approved['replacement_ids'])
for name in ['industrial_processes', 'reactor_fuel_processes', 'industrial_support_processes']:
    for plan in json.loads((DATA / f'{name}.json').read_text(encoding='utf-8'))['recipes']:
        if plan['id'] not in obsolete_originals and not any(plan['id'].startswith(p) for p in approved.get('superseded_prefixes', [])):
            plans[plan['id']] = plan
plans.update((plan['id'], plan) for plan in approved['recipes'])


def ns(identifier):
    return identifier if ':' in identifier else 'hk3gtl:' + identifier


def quantities(text, key):
    return [dict(id=ns(token.split('*')[0]), **{key: int(token.split('*')[1])}) for token in text.split()]


def group(role, tier, research, family):
    global context
    context = role, tier, research.split(), family


def item(identifier, zh, en, appearance, purpose):
    items.append(dict(id=identifier, zh=zh, en=en, family=context[3], appearance=appearance, purpose=purpose))


def fluid(identifier, zh, en, color, purpose, temperature=300):
    fluids.append(dict(id=identifier, zh=zh, en=en, family=context[3], color=color, temperature=temperature,
                       appearance=f'{zh}采用有流动细纹与悬浮颗粒的独立像素液面，主色#{color:06x}。', purpose=purpose))


def r(slug, title, ii='', io='', fi='', fo='', tool='', ticks=1600, hw=0, tier=None, research=None):
    role, base_tier, requirements, family = context
    tier = base_tier if tier is None else tier
    recipes.append(dict(id='industrial_expansion_early_' + slug, title=title, role=role, requirements=requirements if research is None else research.split(),
                        design_uid='EXP-E:' + slug, item_inputs=quantities(ii, 'count'), item_outputs=quantities(io, 'count'),
                        fluid_inputs=quantities(fi, 'amount'), fluid_outputs=quantities(fo, 'amount'), item_catalysts=quantities(tool, 'count'),
                        ticks=ticks, energy_tier=tier, stage_tier=tier, energy_direction='input', input_eut=2013265920 * 4 ** (tier - 14),
                        input_hw=hw, facts=[], required_facts=[], experiment='', provisional=False, network_credit=0, circuit=0))


def link(identifier, ii='', fi='', tool='', reason=''):
    plan = plans[identifier]
    inputs = quantities(ii, 'count')
    liquids = quantities(fi, 'amount')
    tools = quantities(tool, 'count')
    links.append(dict(recipe_id=identifier, item_inputs=inputs, fluid_inputs=liquids, item_catalysts=tools, reason=reason,
                      before={key: plan.get(key, []) for key in ['item_inputs', 'fluid_inputs', 'item_catalysts']},
                      after={key: plan.get(key, []) + extra for key, extra in [('item_inputs', inputs), ('fluid_inputs', liquids), ('item_catalysts', tools)]}))


def link_output(identifier, ii='', fi='', tool='', reason=''):
    link(next(p['id'] for p in plans.values() if any(x['id'] == ns(identifier) for x in p.get('item_outputs', []))), ii, fi, tool, reason)


group('I01-1', 14, '', 'cryogenic_sampling')
item('air_drying_cartridge', '低温采气干燥筒', 'Cryogenic Air Dryer Cartridge', '银白网筒内填琥珀色颗粒，蓝色防霜端盖。', '除去采集空气的水分，防止低温流道结冰。')
item('wet_air_drying_cartridge', '吸湿采气干燥筒', 'Waterlogged Air Dryer Cartridge', '母型银白网筒内颗粒变深，底部有凝露。', '脱水后循环使用，凝露进入采样尾水处理。')
item('aerosol_capture_felt', '气溶胶捕集毡', 'Aerosol Capture Felt', '灰白折叠纤维毡上有铜色支撑网。', '捕捉空气中固体微粒，提供独立粉体分析原料。')
item('loaded_aerosol_felt', '载尘气溶胶捕集毡', 'Loaded Aerosol Capture Felt', '折叠毡褶缝内有紫灰色积尘。', '洗出崩坏痕量尘后回收纤维基材。')
item('cryosorption_pellet', '低温吸附颗粒', 'Cryosorption Pellet', '蓝灰多孔小圆柱，切面显示蜂窝孔。', '在吸附床内富集痕量崩坏能。')
item('loaded_cryosorption_pellet', '载能低温吸附颗粒', 'Charged Cryosorption Pellet', '蓝灰多孔颗粒孔口有稀疏青紫光点。', '解吸产生小流量浓缩采样气。')
item('cryogenic_column_pack', '低温采样填料盒', 'Cryogenic Sampling Column Pack', '矩形银白盒内为交错铂网，侧面蓝色锁扣。', '初始液态空气采集及富集柱均消耗的可更换填料。')
item('spent_cryogenic_column_pack', '失活低温采样填料盒', 'Spent Cryogenic Column Pack', '铂网表面呈灰紫斑，蓝扣保留。', '清洗回收铂和过滤残渣，避免无耗工装包办所有采集。')
item('cryogenic_frost_salt', '低温霜析沉积物', 'Cryogenic Frost Deposit', '灰白多孔碎片夹少量紫色凝霜，断面可见干燥剂颗粒。', '干燥筒再生时分出的硅铝干燥剂磨屑，融洗后有损回收。')
item('trace_honkai_aerosol', '痕量崩坏气溶胶尘', 'Trace Honkai Aerosol Dust', '暗灰粉堆内稀疏青色点。', '进入固相采集机分选，不能直接当作成品结晶。')
fluid('dried_sampling_air', '干燥采样空气', 'Dried Sampling Air', 0xAAC3D4, '除湿空气进入气溶胶过滤和低温冷凝。')
fluid('aerosol_free_air', '除尘采样空气', 'Aerosol Free Sampling Air', 0xC1D5E2, '无尘空气进入吸附与低温富集。')
fluid('honkai_enriched_air', '痕能富集空气', 'Trace Energy Enriched Air', 0x7992C7, '经吸附解吸得到的气相富集液化原料。')
fluid('cryogenic_sampling_condensate', '低温采样凝液', 'Cryogenic Sampling Condensate', 0x91BCD0, '分馏得到液态崩坏能及可回收空气组分。', 90)
fluid('sampling_wash_water', '采样清洗尾水', 'Sampling Wash Water', 0x7A899A, '清洗滤毡和填料的含尘废水，经分离回收水及尘。')
fluid('lean_sampling_air', '贫痕能采样空气', 'Lean Sampling Air', 0xBBC4CD, '已脱除崩坏痕量组分的空气，分离氮氧回收。')
fluid('sampling_frost_brine', '采样除霜悬液', 'Sampling Defrost Suspension', 0x829FA9, '霜析沉积物融洗所得悬液，脱水后回收硅铝磨屑。')
r('air_dryer_fill', '硅铝复合干燥剂装填低温采气干燥筒', 'gtceu:silicon_dioxide_dust*128 gtceu:alumina_dust*64 gtceu:stainless_steel_foil*64 gtceu:polyetheretherketone_foil*64', 'air_drying_cartridge*8', 'gtceu:distilled_water*16000', ticks=2400)
r('aerosol_felt_form', '折叠气溶胶捕集毡定形', 'gtceu:carbon_fiber_plate*32 gtceu:platinum_foil*32 gtceu:polybenzimidazole_foil*64', 'aerosol_capture_felt*8', 'gtceu:polybenzimidazole*4608')
r('cryosorption_pellet_form', '低温多孔吸附颗粒成形', 'gtceu:zeolite_dust*128 gtceu:alumina_dust*64 gtceu:graphene_dust*32', 'cryosorption_pellet*64', 'gtceu:distilled_water*8000')
r('cryogenic_column_form', '铂网低温采样柱填料装配', 'gtceu:platinum_foil*128 gtceu:stainless_steel_foil*128 cryosorption_pellet*16', 'cryogenic_column_pack*8', 'gtceu:polyimide*4608', ticks=3200)
r('sampling_air_dry', '百万升空气除湿预处理', 'air_drying_cartridge*1', 'wet_air_drying_cartridge*1', 'gtceu:air*1000000', 'dried_sampling_air*960000 gtceu:distilled_water*4000', ticks=2400)
r('sampling_air_dust', '干燥空气气溶胶截留', 'aerosol_capture_felt*1', 'loaded_aerosol_felt*1', 'dried_sampling_air*960000', 'aerosol_free_air*940000', ticks=1800)
r('sampling_air_adsorb', '无尘空气低温选择吸附', 'cryosorption_pellet*16', 'loaded_cryosorption_pellet*16', 'aerosol_free_air*940000', 'lean_sampling_air*900000', tool='prototype_honkai_detector*1', ticks=3200)
r('sampling_air_desorb', '载能颗粒真空解吸', 'loaded_cryosorption_pellet*16', 'cryosorption_pellet*14', 'gtceu:helium*16000', 'honkai_enriched_air*32000', ticks=1600)
r('sampling_air_condense', '富集空气低温冷凝', 'cryogenic_column_pack*1', 'spent_cryogenic_column_pack*1', 'honkai_enriched_air*32000 gtceu:liquid_hydrogen*16000', 'cryogenic_sampling_condensate*2000 gtceu:hydrogen*16000', ticks=2400)
r('sampling_condensate_fraction', '采样凝液痕能分馏', '', '', 'cryogenic_sampling_condensate*2000', 'liquid_honkai_energy*80 gtceu:liquid_air*1600', tool='prototype_honkai_detector*1', ticks=2400)
r('sampling_air_nitrogen', '贫痕能尾气氮组分回收', '', '', 'lean_sampling_air*900000', 'gtceu:nitrogen*540000 gtceu:oxygen*180000 gtceu:argon*8000', ticks=1800)
r('sampling_felt_rinse', '载尘滤毡逆流洗脱', 'loaded_aerosol_felt*8', 'aerosol_capture_felt*6 trace_honkai_aerosol*4', 'gtceu:distilled_water*16000', 'sampling_wash_water*16000')
r('sampling_dryer_regen', '吸湿干燥筒真空再生', 'wet_air_drying_cartridge*8', 'air_drying_cartridge*7 cryogenic_frost_salt*8', 'gtceu:nitrogen*32000', 'gtceu:distilled_water*8000')
r('sampling_column_strip', '失活填料酸洗退镀', 'spent_cryogenic_column_pack*8', 'gtceu:platinum_dust*32 separation_residue*8', 'gtceu:hydrochloric_acid*16000', 'sampling_wash_water*16000')
r('sampling_water_filter', '采样尾水微粒分离', 'separation_filter*1', 'separation_residue*4 trace_honkai_aerosol*2', 'sampling_wash_water*16000', 'gtceu:distilled_water*12000')
r('sampling_coldbox_defrost', '冷箱沉积物受控融洗', 'cryogenic_frost_salt*16', '', 'gtceu:distilled_water*16000', 'sampling_frost_brine*16000')
r('sampling_brine_recover', '除霜悬液脱水回收', '', 'cryogenic_frost_salt*12', 'sampling_frost_brine*16000', 'gtceu:distilled_water*12000')
r('sampling_salt_silica', '霜析沉积物硅铝粒径分级', 'cryogenic_frost_salt*32', 'gtceu:silicon_dioxide_dust*16 gtceu:alumina_dust*8', 'gtceu:distilled_water*4000', 'sampling_wash_water*4000')
r('sampling_capture_concentrate', '捕集尘湿法富集', 'trace_honkai_aerosol*16', 'concentrated_honkai_impurity*4 separation_residue*8', 'honkai_analysis_reagent*2000', 'spent_analysis_reagent*2000', research='RN-HSA')
r('sampling_column_resinter', '清洗填料补粉再烧结', 'spent_cryogenic_column_pack*4 gtceu:platinum_foil*32 cryosorption_pellet*16', 'cryogenic_column_pack*3', 'gtceu:hydrogen*8000')
r('sampling_pellet_recondition', '吸附颗粒孔道再开通', 'loaded_cryosorption_pellet*32 gtceu:alumina_dust*16', 'cryosorption_pellet*24 separation_residue*8', 'gtceu:hydrogen*16000', 'sampling_wash_water*4000')
r('sampling_dryer_scrap', '报废干燥筒拆解', 'wet_air_drying_cartridge*8', 'gtceu:stainless_steel_dust*16 gtceu:silicon_dioxide_dust*32', 'gtceu:distilled_water*4000', 'sampling_wash_water*4000')
r('sampling_felt_carbon_recover', '滤毡碳纤维回收', 'loaded_aerosol_felt*8', 'gtceu:carbon_dust*32 gtceu:platinum_dust*8', 'gtceu:nitrogen*16000')
r('sampling_condensate_polish', '采样凝液杂质抛光', 'separation_filter*1', 'concentrated_honkai_impurity*2', 'cryogenic_sampling_condensate*4000 honkai_analysis_reagent*1000', 'clarified_honkai_mother_liquor*200 spent_analysis_reagent*1000', research='RN-HSA')
r('sampling_splitflow_meter', '并行采样分流标定件制造', 'gtceu:neutronium_plate*64 gtceu:platinum_foil*64 gtceu:sapphire_lens*16', 'detector_calibration_split_mask*2', 'gtceu:helium*16000', ticks=2400)
r('sampling_burst_media', '瞬态采气泡沫消能', 'cryosorption_pellet*32 aerosol_capture_felt*2', 'loaded_cryosorption_pellet*24 loaded_aerosol_felt*2', 'honkai_enriched_air*64000', 'lean_sampling_air*48000', ticks=2000)
r('sampling_fraction_buffer', '浓缩样流分级缓释', 'cryogenic_column_pack*1', 'spent_cryogenic_column_pack*1', 'cryogenic_sampling_condensate*8000', 'honkai_mother_liquor*400 lean_sampling_air*4000', tool='prototype_honkai_detector*1', research='RN-HSA')
r('sampling_rinse_filter_make', '采样尾水分离滤芯压制', 'cryosorption_pellet*32 gtceu:polybenzimidazole_foil*64 gtceu:stainless_steel_foil*64', 'separation_filter*8', 'gtceu:reinforced_epoxy_resin*4608')
link('approved_hbv_r11', 'cryogenic_column_pack*1', reason='低温铂网填料提供痕量崩坏能富集表面；填料由独立MAX原料首制，初采不依赖HW。')


group('I01-2', 19, 'RN-SSC', 'solid_capture')
item('capture_electrode_blank', '捕集电极坯', 'Capture Electrode Blank', '钨黑多孔环片嵌银色导流齿。', '极化后作为固相捕集盒的静电电极。')
item('poled_capture_electrode', '极化捕集电极', 'Poled Capture Electrode', '钨黑环片内圈有分段青色电极。', '形成分级电场，装入固相捕集盒。')
item('solid_capture_textile', '固相捕集织物', 'Solid Capture Textile', '白灰金属纤维织物呈折叠方片，铜线贯穿。', '拦截游离颗粒，使用后可洗脱。')
item('loaded_solid_capture_textile', '载尘固相捕集织物', 'Loaded Solid Capture Textile', '折叠织物中心附着深紫粉尘。', '洗脱后产出原始固相粉并回收织物。')
item('solid_capture_sieve', '梯度固相分级筛', 'Graded Solid Classification Sieve', '银色三层细网框，网眼逐级缩小。', '不消耗的颗粒粒径分选工装。')
item('solid_drift_aperture', '固相漂移准直孔板', 'Solid Drift Aperture', '黑银圆盘开同心扇形长孔，青色定位点。', '控制固相粒子轨迹，服务稳定捕集。')
item('solid_capture_cartridge', '固相捕集盒', 'Solid Capture Cartridge', '长方银壳露出折叠白织物与分段环电极。', '组装电极、织物、孔板的消耗式集成捕集件。')
item('spent_solid_capture_cartridge', '饱和固相捕集盒', 'Saturated Solid Capture Cartridge', '同型银盒窗口内为深紫积尘，角部琥珀警示。', '解体回收结构，洗出崩坏固体前驱。')
item('raw_solid_honkai_powder', '原始崩坏固相粉', 'Raw Solid Honkai Powder', '紫灰粗粉混银色颗粒。', '经湿法分散、磁选和电选后得到可稳定固相。')
item('magnetic_capture_fraction', '捕集磁性杂相', 'Magnetic Capture Fraction', '深铁灰细粉带少量红棕颗粒。', '还原回收铁镍，防止污染结晶。')
item('light_capture_fraction', '捕集轻质杂相', 'Light Capture Fraction', '灰白絮粉夹黑色碳点。', '分离回收硅碳组分。')
item('selected_honkai_solid', '分选崩坏固相', 'Classified Honkai Solid', '粒径均匀的紫色粗晶粒。', '浸出除去残余金属杂质。')
item('washed_honkai_solid', '净洗崩坏固相', 'Washed Honkai Solid', '青紫湿晶粒边缘有白色液膜。', '干燥、钝化后制稳定结晶或颗粒。')
item('dry_honkai_solid', '干燥崩坏固相', 'Dried Honkai Solid', '清晰棱角的蓝紫晶砂。', '制成晶种、压坯及封闭运输安瓿。')
item('solid_particle_preform', '崩坏微粒压坯', 'Honkai Particle Preform', '紫黑短圆柱，表面分层压纹。', '受控解聚制备原始崩坏微粒。')
item('solid_transport_ampoule', '固相运输安瓿', 'Solid Transport Ampoule', '透明银框瓶中为蓝紫晶砂，黑色双端盖。', '将干燥固相封闭转运到燃料／晶种制造。')
fluid('solid_capture_suspension', '固相捕集分散浆', 'Solid Capture Suspension', 0x8876AF, '原始固相粉的湿法分类载体。')
fluid('classified_solid_slurry', '分级固相浓浆', 'Classified Solid Slurry', 0x6A66B0, '磁选除轻杂质后的浓浆，离心获得固相。')
fluid('solid_capture_leachate', '固相除杂浸出液', 'Solid Capture Leachate', 0x88728A, '酸洗尾液，处理后回收酸与金属。')
r('capture_electrode_form', '多孔钨电极坯烧结', 'gtceu:tungsten_dust*256 gtceu:platinum_dust*64 gtceu:graphene_dust*64', 'capture_electrode_blank*8', 'gtceu:argon*64000', ticks=2400)
r('capture_electrode_pole', '捕集电极分区极化', 'capture_electrode_blank*8 gtceu:fine_cosmic_wire*128', 'poled_capture_electrode*8', 'gtceu:polyimide*9216')
r('capture_textile_weave', '金属纤维固相捕集织物织造', 'gtceu:stainless_steel_foil*128 gtceu:carbon_fiber_plate*64 gtceu:polybenzimidazole_foil*128', 'solid_capture_textile*16', 'gtceu:reinforced_epoxy_resin*9216')
r('capture_sieve_laminate', '梯度固相分级筛叠合', 'gtceu:neutronium_plate*128 gtceu:platinum_foil*128 gtceu:polyetheretherketone_foil*128', 'solid_capture_sieve*4', 'gtceu:soldering_alloy*36864')
r('capture_drift_align', '漂移准直孔板电场对中', 'gtceu:neutronium_plate*128 gtceu:graphene_foil*128 gtceu:sapphire_lens*32', 'solid_drift_aperture*8', 'gtceu:helium*32000', tool='detector_calibration_split_mask*1')
r('capture_cartridge_assemble', '电极织物一体固相捕集盒', 'poled_capture_electrode*2 solid_capture_textile*4 solid_drift_aperture*1 gtceu:polyetheretherketone_foil*64', 'solid_capture_cartridge*4', 'gtceu:polyimide*9216')
r('solid_field_collect', '定向电场固相痕能捕集', 'solid_capture_cartridge*1', 'spent_solid_capture_cartridge*1 raw_solid_honkai_powder*8', 'honkai_coolant*4000', 'hot_honkai_coolant*4000', tool='solid_honkai_detector*1 solid_capture_sieve*1', ticks=3200)
r('capture_cartridge_open', '饱和捕集盒拆洗', 'spent_solid_capture_cartridge*4', 'loaded_solid_capture_textile*12 capture_electrode_blank*4 raw_solid_honkai_powder*16', 'gtceu:distilled_water*16000', 'sampling_wash_water*16000')
r('capture_textile_wash', '固相织物超声洗脱', 'loaded_solid_capture_textile*8', 'solid_capture_textile*6 raw_solid_honkai_powder*8', 'gtceu:distilled_water*16000', 'sampling_wash_water*16000')
r('solid_powder_disperse', '原始固相超声分散', 'raw_solid_honkai_powder*32', '', 'soulium_process_solvent*8000 nano_surface_passivation_liquid*2000', 'solid_capture_suspension*10000')
r('solid_powder_magnetic', '固相分散浆梯度磁选', '', 'magnetic_capture_fraction*8', 'solid_capture_suspension*10000', 'classified_solid_slurry*8000', tool='poled_capture_electrode*1')
r('solid_powder_gravity', '固相浓浆沉降分级', '', 'light_capture_fraction*8 selected_honkai_solid*20', 'classified_solid_slurry*8000', 'spent_soulium_solvent*8000', tool='solid_capture_sieve*1')
r('solid_powder_electric', '分选固相介电分离', 'selected_honkai_solid*32', 'washed_honkai_solid*24 concentrated_honkai_impurity*4', 'honkai_analysis_reagent*4000', 'spent_analysis_reagent*4000', tool='solid_drift_aperture*1')
r('solid_powder_leach', '选矿固相选择浸出', 'selected_honkai_solid*32', 'washed_honkai_solid*28', 'gtceu:hydrochloric_acid*8000', 'solid_capture_leachate*8000')
r('solid_powder_dry', '净洗固相真空干燥', 'washed_honkai_solid*32', 'dry_honkai_solid*32', 'gtceu:argon*16000', 'gtceu:distilled_water*4000')
r('solid_powder_stabilize', '固相晶砂化学稳定', 'dry_honkai_solid*32 directional_crystallization_matrix*8', 'honkai_energy_crystal*16 separation_residue*4', 'honkai_stabilization_medium*4000', 'spent_honkai_stabilization_medium*4000', ticks=2400)
r('solid_leachate_strip', '固相浸出液酸金属分离', 'separation_filter*1', 'magnetic_capture_fraction*4', 'solid_capture_leachate*8000', 'gtceu:hydrochloric_acid*4000 unrecoverable_process_effluent*4000')
r('solid_textile_reclaim', '烧损织物金属纤维回收', 'loaded_solid_capture_textile*16', 'gtceu:stainless_steel_dust*32 gtceu:carbon_dust*32 separation_residue*8', 'gtceu:nitrogen*32000')
r('solid_sieve_clean', '阶梯筛分固相物理分级', 'raw_solid_honkai_powder*32', 'selected_honkai_solid*16 light_capture_fraction*8 separation_residue*4', 'gtceu:argon*32000', tool='solid_capture_sieve*1')
r('solid_aperture_reclaim', '漂移孔板退镀回收', 'solid_drift_aperture*8', 'gtceu:neutronium_dust*64 gtceu:graphene_dust*16', 'gtceu:hydrochloric_acid*8000', 'solid_capture_leachate*8000')
r('solid_light_fraction_recover', '轻质杂相硅碳回收', 'light_capture_fraction*32', 'gtceu:silicon_dioxide_dust*16 gtceu:carbon_dust*8 separation_residue*4', 'gtceu:argon*16000')
r('solid_magnetic_fraction_reduce', '磁性杂相还原回收', 'magnetic_capture_fraction*32', 'gtceu:iron_dust*16 gtceu:nickel_dust*8 separation_residue*4', 'gtceu:hydrogen*16000')
r('solid_seed_imprint', '固相晶砂定向晶种刻印', 'dry_honkai_solid*32 gtceu:platinum_foil*64', 'honkai_crystal_seed*16', 'resonance_growth_solution*4000', 'spent_resonance_growth_solution*4000', tool='solid_drift_aperture*1')
r('solid_aerosol_coalesce', '痕量气溶胶粉电凝聚', 'trace_honkai_aerosol*32', 'raw_solid_honkai_powder*8 light_capture_fraction*8', 'gtceu:argon*16000', tool='poled_capture_electrode*1')
r('solid_ampoule_seal', '干燥固相惰性封装', 'dry_honkai_solid*32 gtceu:borosilicate_glass_dust*64 gtceu:stainless_steel_foil*64', 'solid_transport_ampoule*8', 'gtceu:argon*16000')
r('solid_ampoule_release', '固相安瓿隔离释料', 'solid_transport_ampoule*8', 'dry_honkai_solid*28 gtceu:stainless_steel_dust*16', 'gtceu:argon*8000')
r('solid_particle_press', '崩坏固相微粒预压', 'dry_honkai_solid*32 gtceu:graphene_dust*16', 'solid_particle_preform*8', 'honkai_stabilization_medium*2000', 'spent_honkai_stabilization_medium*2000')
r('solid_particle_release', '固相压坯受控解聚', 'solid_particle_preform*8', 'raw_honkai_particle*32 separation_residue*4', 'honkai_coolant*4000', 'hot_honkai_coolant*4000')
r('solid_residue_rescan', '捕集杂相残能复选', 'concentrated_honkai_impurity*32', 'raw_honkai_particle*8 separation_residue*16', 'honkai_analysis_reagent*4000', 'spent_analysis_reagent*4000', tool='solid_honkai_detector*1')
r('solid_cartridge_remanufacture', '饱和捕集盒结构重制', 'spent_solid_capture_cartridge*8 solid_capture_textile*16 gtceu:platinum_foil*64', 'solid_capture_cartridge*6 raw_solid_honkai_powder*8', 'gtceu:polyimide*9216')


group('I01-3', 19, 'RN-GSC', 'gas_capture')
item('gas_getter_pellet', '气态崩坏能吸气剂颗粒', 'Honkai Gas Getter Pellet', '深灰多孔颗粒，截面银色金属点。', '吸附气态崩坏能杂质，填充净化筒。')
item('gas_getter_shell', '吸气剂净化筒壳', 'Getter Purifier Shell', '银灰长筒带穿孔内衬，黑色双端螺纹。', '封装吸气剂，拆洗可回收。')
item('activated_gas_getter', '活化吸气剂净化筒', 'Activated Getter Cartridge', '穿孔银筒内填蓝灰颗粒，端部青色标记。', '采气时反应消耗，产饱和净化筒。')
item('saturated_gas_getter', '饱和吸气剂净化筒', 'Saturated Getter Cartridge', '同型筒内颗粒呈暗紫色，端部橙点。', '氢气脱附或拆解回收金属。')
item('gas_phase_diaphragm', '气相分离隔膜', 'Gas Phase Separation Diaphragm', '圆形蓝灰微孔膜，银色辐条支撑。', '隔离载气与崩坏气体，净化过程消耗。')
item('fouled_gas_diaphragm', '污堵气相分离隔膜', 'Fouled Gas Separation Diaphragm', '膜面被深紫条纹堵塞，支撑辐条保留。', '溶剂清洗可恢复大部分隔膜。')
item('gas_baffle_pack', '气相折流除沫组件', 'Gas Demister Baffle Pack', '叠合银色折板，板间有蓝色陶瓷间隔。', '将夹带液滴从气相中分离。')
item('gas_ion_neutralizer', '气相离子中和栅', 'Gas Ion Neutralizer Grid', '金色细线构成双层方栅，黑色陶瓷边框。', '采气回路的可复用电荷中和工装。')
item('gas_sample_capsule', '气态崩坏能取样胶囊', 'Honkai Gas Sampling Capsule', '银色短管中央透明青紫窗口。', '用于定量转运气态能量，送检测及燃料工艺。')
item('gas_mist_capture_bead', '气相除沫吸附珠', 'Gas Mist Capture Bead', '半透明白珠内有灰蓝多孔核心。', '将微雾凝聚为可处理的夹带液。')
fluid('honkai_carrier_gas', '崩坏采气载气', 'Honkai Sampling Carrier Gas', 0xA6C1CB, '氦氩混合物，承担采气、吹扫和气相传质。')
fluid('raw_phase_honkai_gas', '原始相态崩坏气', 'Raw Phase Honkai Gas', 0x9283B9, '采集的含雾带电气，需除沫和中和。')
fluid('demisted_honkai_gas', '除雾崩坏气', 'Demisted Honkai Gas', 0x8E9AC7, '除去液滴，进入中和和膜分离。')
fluid('neutral_honkai_gas', '电中性崩坏气', 'Neutral Honkai Gas', 0x91AEC9, '稳定气相原料，适合压力摆动净化。')
fluid('gas_capture_mist', '采气夹带雾液', 'Gas Capture Mist Liquor', 0x87759E, '除沫副流，回收液态能量及滤芯污染物。')
fluid('depleted_carrier_gas', '失效采气载气', 'Spent Sampling Carrier Gas', 0x747C90, '含杂质的吹扫尾气，经分馏回收氦氩。')
fluid('gas_membrane_wash', '气相膜清洗液', 'Gas Membrane Wash Liquor', 0x796A8D, '清洗膜片产生的溶剂尾液。')
r('gas_getter_powder', '锆钛吸气剂颗粒烧结', 'gtceu:zirconium_dust*128 gtceu:titanium_dust*128 gtceu:graphene_dust*64', 'gas_getter_pellet*64', 'gtceu:argon*64000')
r('gas_getter_shell', '多孔吸气剂筒壳制备', 'gtceu:neutronium_plate*128 gtceu:stainless_steel_foil*128 gtceu:polyetheretherketone_foil*128', 'gas_getter_shell*16', 'gtceu:polyimide*9216')
r('gas_getter_activate', '吸气剂填充真空活化', 'gas_getter_shell*4 gas_getter_pellet*32 gtceu:platinum_foil*64', 'activated_gas_getter*4', 'gtceu:hydrogen*32000')
r('gas_diaphragm_form', '微孔气相隔膜定形', 'gtceu:polyetheretherketone_foil*128 gtceu:graphene_foil*128 gtceu:platinum_foil*64', 'gas_phase_diaphragm*16', 'gtceu:polyimide*9216')
r('gas_demister_form', '陶瓷间隔折流除沫组件', 'gtceu:neutronium_plate*128 nano_ceramic*32 gtceu:polybenzimidazole_foil*128', 'gas_baffle_pack*8', 'gtceu:soldering_alloy*36864')
r('gas_neutralizer_align', '双层离子中和栅对中', 'gtceu:fine_gold_wire*256 nano_ceramic*32 gtceu:graphene_foil*128', 'gas_ion_neutralizer*4', 'gtceu:polyimide*9216', tool='detector_calibration_split_mask*1')
r('gas_mist_bead_form', '多孔除沫吸附珠造粒', 'gtceu:alumina_dust*128 gtceu:silicon_dioxide_dust*128 gtceu:zeolite_dust*128', 'gas_mist_capture_bead*64', 'gtceu:distilled_water*16000')
r('gas_carrier_blend', '低杂质氦氩载气配制', '', '', 'gtceu:helium*64000 gtceu:argon*64000', 'honkai_carrier_gas*128000')
r('gas_field_capture', '载气驱动相态崩坏能采集', 'activated_gas_getter*1 process_gas_filter*1', 'saturated_gas_getter*1 depleted_gas_filter*1', 'honkai_carrier_gas*64000 honkai_coolant*8000', 'raw_phase_honkai_gas*16000 depleted_carrier_gas*48000 hot_honkai_coolant*8000', tool='gaseous_honkai_detector*1 soulium_anchor_component*2', ticks=3200)
r('gas_phase_demisting', '原始崩坏气折流除沫', 'gas_mist_capture_bead*16', 'separation_residue*8', 'raw_phase_honkai_gas*16000', 'demisted_honkai_gas*14000 gas_capture_mist*2000', tool='gas_baffle_pack*1')
r('gas_charge_neutralize', '除雾气相电荷中和', '', '', 'demisted_honkai_gas*14000 honkai_carrier_gas*16000', 'neutral_honkai_gas*12000 depleted_carrier_gas*18000', tool='gas_ion_neutralizer*1')
r('gas_membrane_separate', '电中性气相选择透膜', 'gas_phase_diaphragm*1', 'fouled_gas_diaphragm*1', 'neutral_honkai_gas*12000', 'gaseous_honkai_energy*2000 depleted_carrier_gas*10000', ticks=2400)
r('gas_swing_adsorb', '净化筒压力摆动气相富集', 'activated_gas_getter*1', 'saturated_gas_getter*1', 'neutral_honkai_gas*16000 honkai_carrier_gas*16000', 'gaseous_honkai_energy*4000 depleted_carrier_gas*28000', ticks=2400)
r('gas_mist_condense', '夹带雾液崩坏组分回收', 'separation_filter*1', 'concentrated_honkai_impurity*4', 'gas_capture_mist*8000', 'liquid_honkai_energy*1000 sampling_wash_water*6000')
r('gas_carrier_fractionate', '失效载气低温氦氩分离', 'process_gas_filter*1', 'depleted_gas_filter*1', 'depleted_carrier_gas*64000 gtceu:liquid_hydrogen*16000', 'gtceu:helium*24000 gtceu:argon*24000 gtceu:hydrogen*16000')
r('gas_getter_regenerate', '饱和净化筒氢气脱附', 'saturated_gas_getter*8 gas_getter_pellet*16', 'activated_gas_getter*6 concentrated_honkai_impurity*8', 'gtceu:hydrogen*32000', 'depleted_carrier_gas*16000')
r('gas_diaphragm_wash', '污堵气相隔膜溶剂复原', 'fouled_gas_diaphragm*16', 'gas_phase_diaphragm*12 separation_residue*8', 'soulium_process_solvent*16000', 'gas_membrane_wash*16000')
r('gas_membrane_solvent_recover', '膜清洗液溶剂分离', '', 'process_gas_impurity*8', 'gas_membrane_wash*16000', 'soulium_process_solvent*10000 unrecoverable_process_effluent*6000')
r('gas_getter_shell_recover', '饱和吸气筒金属分拆', 'saturated_gas_getter*8', 'gas_getter_shell*6 gtceu:zirconium_dust*16 gtceu:titanium_dust*16 separation_residue*8', 'gtceu:hydrochloric_acid*8000', 'solid_capture_leachate*8000')
r('gas_filter_deep_desorb', '废气滤芯真空深度解吸', 'depleted_gas_filter*16', 'process_gas_filter*10 process_gas_impurity*8', 'honkai_carrier_gas*32000', 'gas_capture_mist*2000 depleted_carrier_gas*30000')
r('gas_capsule_seal', '气态崩坏能定量封存', 'gas_getter_shell*8 gtceu:borosilicate_glass_dust*64 gtceu:polyetheretherketone_foil*64', 'gas_sample_capsule*8', 'gaseous_honkai_energy*8000')
r('gas_capsule_release', '气态取样胶囊隔离释放', 'gas_sample_capsule*8', 'gas_getter_shell*6', '', 'gaseous_honkai_energy*7200', tool='gas_baffle_pack*1')
r('gas_crystal_sublimation', '固相样品惰性载气升华', 'solid_transport_ampoule*8', 'gtceu:stainless_steel_dust*16', 'honkai_carrier_gas*32000', 'raw_phase_honkai_gas*16000 depleted_carrier_gas*16000', ticks=2400)
r('gas_trace_residue_capture', '采气杂质残余气相剥离', 'process_gas_impurity*32 gas_mist_capture_bead*16', 'concentrated_honkai_impurity*8 separation_residue*16', 'honkai_carrier_gas*32000', 'raw_phase_honkai_gas*4000 depleted_carrier_gas*28000')
r('gas_getter_water_guard', '低温载气水汽保护过滤', 'air_drying_cartridge*4', 'wet_air_drying_cartridge*4', 'honkai_carrier_gas*128000', 'gtceu:helium*60000 gtceu:argon*60000')
r('gas_membrane_metal_reclaim', '报废隔膜铂碳分离', 'fouled_gas_diaphragm*16', 'gtceu:platinum_dust*16 gtceu:carbon_dust*32', 'gtceu:hydrogen*16000', 'depleted_carrier_gas*8000')
r('gas_demister_mist_recovery', '折流板附着雾滴冲洗回收', 'gas_baffle_pack*1', 'gas_baffle_pack*1 separation_residue*2', 'gas_capture_mist*8000 gtceu:distilled_water*8000', 'sampling_wash_water*14000 liquid_honkai_energy*200')
r('gas_low_pressure_polish', '低分压气态崩坏能终端净化', 'activated_gas_getter*1 gas_phase_diaphragm*1', 'saturated_gas_getter*1 fouled_gas_diaphragm*1', 'raw_phase_honkai_gas*32000', 'gaseous_honkai_energy*3000 gas_capture_mist*4000 depleted_carrier_gas*25000', tool='gas_ion_neutralizer*1', ticks=3200)
link('industrial_gas_collection', 'activated_gas_getter*1', reason='活化吸气剂在采集时固定氧化和腐蚀杂质；筒体整合颗粒及密封，形成明确耗材支线。')


group('I01-4', 26, 'RN-ESC', 'energy_capture')
item('energy_capture_lining', '能态捕获衬层', 'Energy Capture Lining', '紫黑层叠片内有银色细网，外沿淡青刻线。', '提供捕获笼的能态吸收和电荷泄放表面。')
item('energy_capture_cage', '能态捕获笼', 'Energy Capture Cage', '银黑八棱短笼，分段青色束环包围空腔。', '把散逸能态约束为可转移束流，采集后充能。')
item('charged_energy_capture_cage', '充能能态捕获笼', 'Charged Energy Capture Cage', '同型笼腔中有青紫细束，分段束环点亮。', '分级泄放出相干能态束流。')
item('spent_energy_capture_cage', '退能捕获笼', 'Discharged Energy Capture Cage', '同型笼内衬出现浅灰冲蚀痕，束环暗淡。', '补衬后再造，或拆回结构材料。')
item('energy_absorber_foil', '能态吸收箔', 'Energy Absorber Foil', '紫黑卷箔表面为青银微格纹。', '收集偏离主束的能量，避免直接丢弃散射副流。')
item('charged_energy_absorber_foil', '充能能态吸收箔', 'Charged Energy Absorber Foil', '母型卷箔微格内有青紫光点。', '受控放电回收原始崩坏微粒。')
item('energy_phase_grating', '能态相位栅', 'Energy Phase Grating', '银色薄框内平行紫色细栅，边缘黑色绝缘条。', '将相干主束和散射副束按相位分开。')
item('energy_capture_tile', '能态捕集耦合片', 'Energy Capture Coupling Tile', '方形银黑集成片，青色交叉导路与紫色中心孔。', '整合相位栅和衬层，成为能态采集的消耗式耦合件。')
item('energy_waveguide', '能态约束波导', 'Confined Energy Waveguide', '银黑弯管，内壁紫色衬线，三段青色箍环。', '作为束流输送、注入与放电工装。')
item('energy_quench_sleeve', '能态淬熄套筒', 'Energy Quench Sleeve', '黑银厚壁筒开有蓝色螺旋冷却槽。', '把失配束流转为可沉降的淬熄液。')
item('energy_spectrum_reference', '能态谱线实体基准', 'Energy Spectrum Reference', '小型透明晶板内封装三条青紫谱线，银色框。', '用于能态探测与空间标定的可复用物理参照。')
item('field_energy_contact', '场能耦合触点', 'Field Energy Contact', '银色三叉触点，紫黑陶瓷根部，青色顶端。', '以实体导路承接相干束流。')
item('charged_field_contact', '充能场能耦合触点', 'Charged Field Contact', '三叉银触点顶端有青紫放电点。', '与聚焦内衬制成功能性场能嵌件。')
item('energy_focus_insert', '场能聚焦嵌件', 'Field Energy Focusing Insert', '六角银壳内嵌紫色晶体，三叉触点环绕。', '增强反应堆稳定器的场能整形。')
item('energy_quench_glass', '淬熄含能玻璃', 'Energy Quench Glass', '灰紫玻璃碎块内封存稀疏青点。', '淬熄尾流的固体副产，解离回收能量和硅料。')
fluid('coherent_energy_stream', '相干能态束流', 'Coherent Energy Stream', 0x82BEDB, '捕获后可控的能态主流，冷凝、谱分或充能使用。')
fluid('divergent_energy_stream', '散射能态尾流', 'Scattered Energy Tail Stream', 0x9164C0, '谱分得到的非相干副流，吸收或淬熄回收。')
fluid('energy_quench_liquor', '能态淬熄液', 'Energy Quench Liquor', 0x6F719E, '淬熄套筒产生的含能尾液，沉降回收玻璃状残渣。')
r('energy_lining_laminate', '场能吸收衬层多层复合', 'gtceu:neutronium_plate*256 gtceu:graphene_foil*512 gtceu:cosmic_foil*256 gtceu:shirabon_foil*256', 'energy_capture_lining*32', 'gtceu:spacetime*147456 gtceu:polyimide*73728', ticks=3200)
r('energy_cage_form', '八向约束捕获笼封装', 'energy_capture_lining*16 soulium_anchor_component*8 gtceu:neutronium_plate*256 gtceu:cosmic_foil*256', 'energy_capture_cage*8', 'gtceu:infinity*18432 gtceu:super_mutated_living_solder*147456', ticks=3200)
r('energy_absorber_form', '能态吸收微格箔压合', 'gtceu:graphene_foil*512 gtceu:platinum_foil*256 gtceu:cosmic_foil*256', 'energy_absorber_foil*64', 'gtceu:polyimide*73728')
r('energy_grating_align', '能态相位栅对中', 'gtceu:cosmic_foil*256 gtceu:fine_cosmic_wire*256 gtceu:sapphire_lens*64', 'energy_phase_grating*16', 'gtceu:spacetime*73728', tool='detector_calibration_split_mask*1')
r('energy_waveguide_form', '能态波导衬管成形', 'energy_capture_lining*8 gtceu:neutronium_plate*256 gtceu:polyetheretherketone_foil*512', 'energy_waveguide*4', 'gtceu:infinity*18432')
r('energy_quench_sleeve_form', '螺旋冷道淬熄套筒封接', 'gtceu:neutronium_plate*256 nano_ceramic*128 gtceu:graphene_foil*256', 'energy_quench_sleeve*4', 'gtceu:polyimide*73728 gtceu:soldering_alloy*294912')
r('energy_capture_tile_assemble', '采集耦合片工艺集成', 'energy_capture_lining*8 energy_phase_grating*4 gtceu:cosmic_foil*128 gtceu:shirabon_foil*128', 'energy_capture_tile*16', 'gtceu:spacetime*73728')
r('energy_contact_form', '三叉场能触点绝缘封接', 'gtceu:cosmic_foil*256 gtceu:fine_cosmic_wire*256 nano_ceramic*64', 'field_energy_contact*32', 'gtceu:infinity*18432 gtceu:polyimide*36864')
r('energy_cage_capture', '分段束环场能捕获', 'energy_capture_cage*4 energy_capture_tile*8 process_gas_filter*8', 'charged_energy_capture_cage*4 depleted_gas_filter*8', 'honkai_coolant*64000', 'hot_honkai_coolant*64000', tool='energy_honkai_detector*1 soulium_anchor_component*8', ticks=4800)
r('energy_cage_bleed', '捕获笼相干主束分级泄放', 'charged_energy_capture_cage*4', 'spent_energy_capture_cage*4', '', 'coherent_energy_stream*16000', tool='energy_waveguide*1', ticks=3200)
r('energy_phase_sort', '相干束流相位谱分', '', '', 'coherent_energy_stream*16000', 'gaseous_honkai_energy*4000 divergent_energy_stream*8000', tool='energy_phase_grating*1 energy_spectrum_reference*1')
r('energy_stream_condense', '相干能态束流实体冷凝', 'directional_crystallization_matrix*32', 'compressed_honkai_core*16', 'coherent_energy_stream*16000 honkai_coolant*32000', 'hot_honkai_coolant*32000', tool='energy_waveguide*1', ticks=3200)
r('energy_scatter_absorb', '散射尾流微格吸收', 'energy_absorber_foil*16', 'charged_energy_absorber_foil*16', 'divergent_energy_stream*16000', '', tool='energy_waveguide*1')
r('energy_foil_discharge', '吸收箔脉冲解吸回收', 'charged_energy_absorber_foil*16', 'energy_absorber_foil*12 raw_honkai_particle*32', 'honkai_coolant*16000', 'hot_honkai_coolant*16000', tool='energy_waveguide*1')
r('energy_scatter_quench', '失配能态尾流淬熄', '', '', 'divergent_energy_stream*16000 gtceu:grade_16_purified_water*16000', 'energy_quench_liquor*24000', tool='energy_quench_sleeve*1')
r('energy_quench_settle', '淬熄液玻璃态沉降', 'gtceu:silicon_dioxide_dust*64', 'energy_quench_glass*32', 'energy_quench_liquor*24000', 'unrecoverable_process_effluent*16000')
r('energy_cage_reline', '退能捕获笼补衬再造', 'spent_energy_capture_cage*8 energy_capture_lining*16 gtceu:cosmic_foil*128', 'energy_capture_cage*6 separation_residue*16', 'gtceu:polyimide*73728')
r('energy_cage_dismantle', '退能捕获笼结构分拆', 'spent_energy_capture_cage*8', 'gtceu:neutronium_dust*128 gtceu:cosmic_dust*64 soulium_swarf*64', 'gtceu:hydrochloric_acid*32000', 'unrecoverable_process_effluent*32000')
r('energy_foil_strip', '报废吸收箔金属退镀', 'charged_energy_absorber_foil*32', 'gtceu:platinum_dust*64 gtceu:carbon_dust*128 concentrated_honkai_impurity*16', 'gtceu:hydrogen*64000')
r('energy_spectrum_reference_make', '能态谱线物理基准封存', 'compressed_honkai_core*8 energy_phase_grating*4 gtceu:sapphire_lens*32 gtceu:cosmic_foil*128', 'energy_spectrum_reference*4', 'gtceu:polyimide*36864', tool='energy_waveguide*1')
r('energy_contact_charge', '场能触点受控充能', 'field_energy_contact*16', 'charged_field_contact*16', 'coherent_energy_stream*8000 honkai_coolant*16000', 'hot_honkai_coolant*16000', tool='energy_waveguide*1')
r('energy_focus_insert_make', '场能聚焦触点嵌件总装', 'charged_field_contact*8 energy_capture_lining*8 energy_phase_grating*2 gtceu:sapphire_lens*16', 'energy_focus_insert*4', 'gtceu:infinity*9216 gtceu:polyimide*36864')
r('energy_reactor_stabilizer', '聚焦嵌件反应堆稳定器整合', 'energy_focus_insert*4 soulium_anchor_component*8 gtceu:neutronium_plate*128 gtceu:cosmic_foil*128', 'reactor_stabilizer*4', 'gtceu:super_mutated_living_solder*147456 honkai_coolant*16000', 'hot_honkai_coolant*16000', ticks=2400)
r('energy_cage_gas_release', '捕获笼气相安全释能', 'charged_energy_capture_cage*4 gas_phase_diaphragm*4', 'spent_energy_capture_cage*4 fouled_gas_diaphragm*4', 'honkai_carrier_gas*64000', 'gaseous_honkai_energy*8000 depleted_carrier_gas*56000', tool='gas_baffle_pack*1')
r('energy_glass_break', '含能玻璃选择解离', 'energy_quench_glass*32', 'raw_honkai_particle*16 gtceu:silicon_dioxide_dust*32 separation_residue*8', 'honkai_analysis_reagent*8000', 'spent_analysis_reagent*8000')
r('energy_gas_collimate', '气态崩坏能定向能态化', '', '', 'gaseous_honkai_energy*16000 honkai_coolant*32000', 'coherent_energy_stream*8000 hot_honkai_coolant*32000', tool='energy_waveguide*1 energy_phase_grating*1')
r('energy_particle_ionize', '崩坏微粒电离散射', 'raw_honkai_particle*64 energy_absorber_foil*4', 'charged_energy_absorber_foil*4', 'honkai_carrier_gas*32000', 'divergent_energy_stream*8000 depleted_carrier_gas*24000')
r('energy_waveguide_reclaim', '能态波导材料分离', 'energy_waveguide*4', 'gtceu:neutronium_dust*128 gtceu:carbon_dust*64 soulium_swarf*32', 'gtceu:hydrochloric_acid*16000', 'unrecoverable_process_effluent*16000')
r('energy_spatial_reference', '实体谱线空间标定模组', 'energy_spectrum_reference*4 energy_focus_insert*4 soulium_anchor_component*8 gtceu:cosmic_foil*256', 'spatial_calibration_module*4', 'gtceu:spacetime*147456 gtceu:super_mutated_living_solder*147456', tool='energy_waveguide*1', ticks=3200)
link('industrial_energy_collection', 'energy_capture_tile*2', tool='energy_spectrum_reference*1', reason='耦合片负责捕集主束，实体谱线校准采集频带；谱线基准可由独立新采集支线取得，避免主配方自身首源循环。')


group('I04', 14, 'RN-LSE', 'liquid_stabilization')
item('stabilization_buffer_pellet', '稳定化缓冲颗粒', 'Stabilization Buffer Pellet', '白色多孔小柱外缘有浅蓝包衣。', '控制稳定化液的局部酸度和离子强度，消耗形成废缓冲盐。')
item('spent_stabilization_buffer', '耗尽稳定化缓冲盐', 'Spent Stabilization Buffer Salt', '灰蓝结块，有紫色杂质细点。', '酸洗分离后补料回收缓冲颗粒。')
item('stabilizer_chelation_bead', '稳定化螯合树脂珠', 'Stabilization Chelation Bead', '琥珀色透明小珠，内层为蓝色微孔网。', '螯合杂质金属，防止液态能量不受控成核。')
item('loaded_stabilizer_chelation_bead', '载杂稳定化螯合珠', 'Loaded Stabilization Chelation Bead', '树脂珠核心变暗紫色，保留琥珀外缘。', '酸洗脱附回收树脂和杂相。')
item('stabilization_redox_mesh', '稳定化氧化还原网', 'Stabilization Redox Mesh', '银铂双层细网，铜色边框与蓝色端子。', '均衡液相电荷状态，定期再活化。')
item('passivated_stabilization_mesh', '钝化稳定化还原网', 'Passivated Stabilization Mesh', '银网表面覆灰紫薄膜。', '氢还原恢复活性，薄膜进入残渣处理。')
item('stabilization_seed_mantle', '稳定化晶种包覆料', 'Stabilization Seed Mantle', '细小白蓝鳞片混合银色薄粒。', '限制晶体生长速度，作为稳定结晶的消耗投入。')
item('stabilization_pulse_capsule', '液相脉冲阻尼胶囊', 'Liquid Pulse Damping Capsule', '银白胶囊带蓝色柔性环和黑色轴心。', '平抑液相脉冲，组装成条件化柱。')
item('liquid_conditioning_cartridge', '液态崩坏能条件化柱', 'Liquid Honkai Conditioning Cartridge', '竖直银柱内分层白颗粒、琥珀树脂和铂网。', '整合缓冲、螯合和电荷均衡功能，减少后期散件输入。')
item('spent_liquid_conditioning_cartridge', '耗尽液态条件化柱', 'Spent Liquid Conditioning Cartridge', '银柱内填料层变暗紫，末端橙色锁扣。', '拆分取回螯合珠、还原网及杂质。')
item('stability_transport_ampoule', '稳定液定量安瓿', 'Stabilized Liquid Metering Ampoule', '透明银框长瓶装蓝色液体，黑色量程刻度。', '定量封存稳定液，服务晶体及燃料装载。')
item('stabilization_filter_cake', '稳定化杂相滤饼', 'Stabilization Impurity Filter Cake', '扁平灰紫多孔滤饼，断面有银粒。', '由除杂产生，回收贵金属与残余崩坏组分。')
item('bubbleless_stabilization_nozzle', '无泡稳定液灌注嘴', 'Bubble Free Stabilization Nozzle', '细长银色双套管，蓝色尖端和侧面回流口。', '为稳定化总工艺提供不消耗的脱泡灌注接口。')
fluid('stabilization_buffer_solution', '稳定化缓冲液', 'Stabilization Buffer Solution', 0x88B6CF, '以无机缓冲颗粒配制的独立新鲜液相调理剂。')
fluid('buffered_honkai_liquor', '缓冲崩坏液', 'Buffered Honkai Liquor', 0x8A8EC5, '完成酸度调节，进入金属杂质螯合。')
fluid('chelated_honkai_liquor', '螯合净化崩坏液', 'Chelated Honkai Liquor', 0x779CC6, '已去除杂质金属，进入氧化还原均衡。')
fluid('redox_balanced_honkai_liquor', '电荷均衡崩坏液', 'Redox Balanced Honkai Liquor', 0x69A4C5, '完成电荷调整，继续脱气和热调理。')
fluid('deaerated_honkai_liquor', '脱气崩坏调理液', 'Deaerated Honkai Conditioning Liquor', 0x66ADC4, '去除气核，减少后续局部沸腾及失稳。')
fluid('conditioned_honkai_liquor', '条件化崩坏液', 'Conditioned Honkai Liquor', 0x63BDD1, '完成温度和电荷调理的稳定化前驱液。')
fluid('stabilization_buffer_tail', '稳定化缓冲尾液', 'Stabilization Buffer Tail Liquor', 0x7D849E, '缓冲盐和杂质回收的侧流。')
fluid('stabilizer_bead_wash', '螯合珠洗脱液', 'Chelation Bead Eluate', 0x917A9F, '树脂再生时释放的杂质与酸液。')
r('stabilization_buffer_form', '无机稳定化缓冲颗粒造粒', 'gtceu:alumina_dust*128 gtceu:silicon_dioxide_dust*128 gtceu:zeolite_dust*128', 'stabilization_buffer_pellet*64', 'gtceu:grade_16_purified_water*16000')
r('stabilizer_chelation_form', '多孔螯合树脂珠固化', 'gtceu:polybenzimidazole_foil*128 gtceu:graphene_dust*64 gtceu:platinum_dust*32', 'stabilizer_chelation_bead*64', 'gtceu:reinforced_epoxy_resin*18432 gtceu:ethanol*16000')
r('stabilization_mesh_form', '铂银氧化还原网编织', 'gtceu:platinum_foil*128 gtceu:silver_foil*128 gtceu:fine_gold_wire*128', 'stabilization_redox_mesh*16', 'gtceu:polyimide*9216')
r('stabilization_seed_mantle_form', '受控成核晶种包覆料制备', 'gtceu:silicon_dioxide_dust*128 gtceu:alumina_dust*64 gtceu:platinum_foil*64', 'stabilization_seed_mantle*64', 'gtceu:polybenzimidazole*9216')
r('stabilization_pulse_form', '液相脉冲阻尼胶囊封装', 'gtceu:neutronium_plate*64 gtceu:polyetheretherketone_foil*128 gtceu:graphene_foil*64', 'stabilization_pulse_capsule*16', 'gtceu:silicone_rubber*9216')
r('stabilization_column_assemble', '多层液态条件化柱总装', 'stabilization_buffer_pellet*16 stabilizer_chelation_bead*16 stabilization_redox_mesh*4 stabilization_pulse_capsule*4 gtceu:neutronium_plate*64', 'liquid_conditioning_cartridge*4', 'gtceu:polyimide*18432')
r('stabilization_buffer_dissolve', '新鲜稳定化缓冲液配制', 'stabilization_buffer_pellet*16', '', 'gtceu:grade_16_purified_water*16000 gtceu:ethyleneglycol*8000', 'stabilization_buffer_solution*24000')
r('stabilization_liquor_buffer', '粗崩坏液缓冲调理', 'stabilization_buffer_pellet*8', 'spent_stabilization_buffer*8', 'crude_honkai_energy*16000 stabilization_buffer_solution*8000', 'buffered_honkai_liquor*16000 stabilization_buffer_tail*8000')
r('stabilization_liquor_chelate', '缓冲崩坏液杂质螯合', 'stabilizer_chelation_bead*16', 'loaded_stabilizer_chelation_bead*16', 'buffered_honkai_liquor*16000', 'chelated_honkai_liquor*14000 stabilization_buffer_tail*2000')
r('stabilization_liquor_redox', '崩坏液氧化还原均衡', 'stabilization_redox_mesh*4', 'passivated_stabilization_mesh*4', 'chelated_honkai_liquor*14000', 'redox_balanced_honkai_liquor*14000')
r('stabilization_liquor_degas', '均衡崩坏液膜式脱气', 'gas_phase_diaphragm*1', 'fouled_gas_diaphragm*1', 'redox_balanced_honkai_liquor*14000 gtceu:helium*16000', 'deaerated_honkai_liquor*12000 depleted_carrier_gas*18000', research='RN-LSE RN-GSC', tier=19)
r('stabilization_liquor_vacuum', '均衡崩坏液真空脱气', 'stabilization_pulse_capsule*2', 'separation_residue*2', 'redox_balanced_honkai_liquor*14000 honkai_coolant*8000', 'deaerated_honkai_liquor*10000 hot_honkai_coolant*8000', tool='stabilization_static_mixer*1')
r('stabilization_liquor_condition', '脱气崩坏液等温条件化', 'liquid_conditioning_cartridge*1', 'spent_liquid_conditioning_cartridge*1', 'deaerated_honkai_liquor*12000 honkai_stabilization_medium*4000', 'conditioned_honkai_liquor*12000 spent_honkai_stabilization_medium*4000')
r('stabilization_liquor_finish', '条件化崩坏液限域稳定', 'stabilization_seed_mantle*16 directional_crystallization_matrix*16 honkai_crystal_seed*8', 'honkai_energy_crystal*64 stabilization_filter_cake*8', 'conditioned_honkai_liquor*12000 honkai_coolant*8000', 'stabilized_liquid_honkai_energy*2400 crystallization_residual_liquid*4000 hot_honkai_coolant*8000', tool='bubbleless_stabilization_nozzle*1', ticks=3200)
r('stabilization_mother_polish', '结晶母液残余杂相抛光', 'stabilizer_chelation_bead*8', 'loaded_stabilizer_chelation_bead*8 stabilization_filter_cake*4', 'honkai_mother_liquor*8000', 'clarified_honkai_mother_liquor*6000 stabilization_buffer_tail*2000')
r('stabilization_buffer_recover', '耗尽缓冲盐补料再生', 'spent_stabilization_buffer*32 gtceu:alumina_dust*16', 'stabilization_buffer_pellet*24 stabilization_filter_cake*8', 'gtceu:grade_16_purified_water*8000', 'stabilization_buffer_tail*8000')
r('stabilizer_bead_regenerate', '载杂螯合树脂酸洗再生', 'loaded_stabilizer_chelation_bead*32', 'stabilizer_chelation_bead*24 stabilization_filter_cake*4', 'gtceu:hydrochloric_acid*8000', 'stabilizer_bead_wash*8000')
r('stabilization_mesh_reactivate', '钝化还原网氢气活化', 'passivated_stabilization_mesh*8 gtceu:platinum_foil*16', 'stabilization_redox_mesh*6 stabilization_filter_cake*4', 'gtceu:hydrogen*16000')
r('stabilization_column_strip', '条件化柱分层解体', 'spent_liquid_conditioning_cartridge*4', 'loaded_stabilizer_chelation_bead*12 passivated_stabilization_mesh*4 spent_stabilization_buffer*12 stabilization_filter_cake*8', 'gtceu:distilled_water*8000', 'stabilization_buffer_tail*8000')
r('stability_ampoule_fill', '稳定崩坏液定量安瓿灌封', 'gtceu:borosilicate_glass_dust*128 gtceu:neutronium_plate*64 gtceu:polyetheretherketone_foil*64', 'stability_transport_ampoule*8', 'stabilized_liquid_honkai_energy*8000', tool='bubbleless_stabilization_nozzle*1')
r('stability_ampoule_drain', '稳定液安瓿隔离卸料', 'stability_transport_ampoule*8', 'gtceu:neutronium_dust*16', '', 'stabilized_liquid_honkai_energy*7200', tool='bubbleless_stabilization_nozzle*1')
r('stabilization_seed_crust_break', '结晶包覆滤饼选择解聚', 'stabilization_filter_cake*32', 'concentrated_honkai_impurity*8 gtceu:silicon_dioxide_dust*16', 'honkai_analysis_reagent*4000', 'spent_analysis_reagent*4000')
r('stabilization_buffer_tail_recover', '缓冲尾液盐水分离', '', 'spent_stabilization_buffer*16 stabilization_filter_cake*4', 'stabilization_buffer_tail*16000', 'gtceu:distilled_water*8000 unrecoverable_process_effluent*8000')
r('stabilizer_bead_wash_recover', '螯合洗脱液贵金属回收', 'separation_filter*1', 'gtceu:platinum_dust*8 concentrated_honkai_impurity*4', 'stabilizer_bead_wash*8000', 'gtceu:hydrochloric_acid*4000 unrecoverable_process_effluent*4000')
r('stabilization_mesh_metal_recover', '腐蚀还原网贵金属分离', 'passivated_stabilization_mesh*16', 'gtceu:platinum_dust*32 gtceu:silver_dust*32 stabilization_filter_cake*8', 'gtceu:hydrochloric_acid*8000', 'stabilizer_bead_wash*8000')
r('stabilization_nozzle_form', '同轴无泡灌注嘴对中', 'gtceu:neutronium_plate*128 gtceu:platinum_foil*64 gtceu:polyetheretherketone_foil*128 gtceu:sapphire_lens*16', 'bubbleless_stabilization_nozzle*4', 'gtceu:helium*16000 gtceu:polyimide*9216', tool='detector_calibration_split_mask*1')
r('stabilization_column_compact', '条件化柱短程集成稳定', 'liquid_conditioning_cartridge*2 stabilization_seed_mantle*16 honkai_crystal_seed*16', 'spent_liquid_conditioning_cartridge*2 honkai_energy_crystal*32 stabilization_filter_cake*8', 'crude_honkai_energy*16000 honkai_stabilization_medium*4000 honkai_coolant*8000', 'stabilized_liquid_honkai_energy*1800 spent_honkai_stabilization_medium*4000 hot_honkai_coolant*8000', tool='bubbleless_stabilization_nozzle*1', ticks=2400)
r('stabilization_column_repack', '耗尽条件化柱结构补料重装', 'spent_liquid_conditioning_cartridge*4 stabilization_buffer_pellet*16 stabilizer_chelation_bead*16 stabilization_redox_mesh*4', 'liquid_conditioning_cartridge*3 stabilization_filter_cake*8', 'gtceu:polyimide*9216')
r('stabilization_precipitate_recover', '含能杂相缓冲浸出', 'concentrated_honkai_impurity*32 stabilization_buffer_pellet*8', 'spent_stabilization_buffer*8 stabilization_filter_cake*16', 'stabilization_buffer_solution*8000', 'crude_honkai_energy*1000 stabilization_buffer_tail*7000')
link('approved_hbv_r18', 'stabilization_buffer_pellet*16 stabilization_seed_mantle*16', tool='bubbleless_stabilization_nozzle*1', reason='无机缓冲控制局部反应，包覆料限制成核，灌注嘴去除气泡；三项都能由MAX常规物料首制，不依赖RN-LES完成。')


group('I06', 14, 'RN-FRP', 'fuel_loading')
item('fuel_capillary_wick', '燃料毛细分布芯', 'Fuel Capillary Distribution Wick', '银黑多孔条带中有平行蓝色细槽。', '在载体内均匀分配液态燃料，减少未浸润孔。')
item('fuel_pore_opening_granule', '燃料载体开孔颗粒', 'Fuel Carrier Pore Opening Granule', '白灰细粒混银色针状碎屑。', '温和开启载体孔道，消耗形成含能清孔残渣。')
item('fuel_loading_pressure_shoe', '燃料载入压差夹块', 'Fuel Loading Pressure Shoe', '银色双瓣夹块，黑色软面与蓝色密封圈。', '压差浸渍工装，制备预压实燃料包。')
item('fuel_metering_injector', '燃料定量浸注头', 'Fuel Metering Impregnation Injector', '四管银色注头，琥珀量窗与黑色定位座。', '燃料装载不消耗工装，控制每份载量。')
item('prewetted_fuel_carrier', '预润湿燃料载体', 'Prewetted Fuel Carrier', '深灰多孔块表面有均匀蓝色湿润膜。', '用预润湿代替额外燃料冲洗，实现连续低损耗浸注。')
item('opened_fuel_carrier', '清孔燃料载体', 'Pore Opened Fuel Carrier', '深灰多孔块，贯通孔口带浅灰磨痕。', '完成清孔后进入底液预润湿，提供贯通毛细通道。')
item('fuel_distribution_laminate', '燃料分布层片', 'Fuel Distribution Laminate', '银黑网芯夹在两片青灰陶瓷薄层之间。', '将燃料棒内载荷均匀分区，供封装使用。')
item('degassed_fuel_charge', '脱气燃料载荷', 'Degassed Fuel Charge', '青色多孔燃料颗粒压成规整短块。', '去除载荷气核，制备稳定包芯料。')
item('pressed_fuel_loading_pack', '预压实燃料包芯料', 'Precompacted Fuel Loading Pack', '银网包覆青色燃料颗粒，侧面层片清晰。', '整合脱气载荷与分布芯，接入既有燃料棒封装。')
item('fuel_pore_cleaning_sludge', '燃料清孔残渣', 'Fuel Pore Cleaning Sludge', '灰紫湿粉内含少量青色碎点。', '清孔和浸注的固定副产，回收残能及碳料。')
fluid('fuel_prewetting_primer', '燃料预润湿底液', 'Fuel Prewetting Primer', 0x6C9FB3, '新鲜溶剂与稳定介质配制，降低燃料浸润阻力。')
fluid('spent_fuel_prewetting_primer', '失效燃料预润湿液', 'Spent Fuel Prewetting Primer', 0x717A96, '浸润后尾液，回收溶剂及燃料残余。')
r('fuel_capillary_wick_form', '多孔燃料毛细分布芯烧结', 'gtceu:graphene_foil*128 gtceu:platinum_foil*64 gtceu:stainless_steel_foil*128', 'fuel_capillary_wick*32', 'gtceu:polybenzimidazole*9216')
r('fuel_pore_granule_form', '燃料载体温和开孔颗粒制备', 'gtceu:alumina_dust*128 gtceu:zeolite_dust*128 gtceu:silicon_dioxide_dust*128', 'fuel_pore_opening_granule*64', 'gtceu:distilled_water*16000')
r('fuel_loading_shoe_form', '压差夹块耐蚀封接', 'gtceu:neutronium_plate*128 gtceu:polyetheretherketone_foil*128 gtceu:platinum_foil*64', 'fuel_loading_pressure_shoe*4', 'gtceu:silicone_rubber*18432')
r('fuel_metering_head_form', '四通道定量浸注头标定', 'gtceu:neutronium_plate*128 gtceu:platinum_foil*128 gtceu:sapphire_lens*32 gtceu:fine_gold_wire*128', 'fuel_metering_injector*4', 'gtceu:helium*16000 gtceu:polyimide*18432', tool='detector_calibration_split_mask*1')
r('fuel_primer_blend', '燃料预润湿底液配制', '', '', 'soulium_process_solvent*16000 honkai_stabilization_medium*8000 gtceu:ethyleneglycol*8000', 'fuel_prewetting_primer*32000')
r('fuel_carrier_prewet', '清孔燃料载体孔道预润湿', 'opened_fuel_carrier*16', 'prewetted_fuel_carrier*16 fuel_pore_cleaning_sludge*8', 'fuel_prewetting_primer*8000', 'spent_fuel_prewetting_primer*8000')
r('fuel_capillary_impregnate', '预润湿载体连续毛细浸注', 'prewetted_fuel_carrier*16 fuel_capillary_wick*4', 'honkai_carbon_charge*16 fuel_pore_cleaning_sludge*4', 'liquid_honkai_fuel*14000', '', tool='fuel_metering_injector*1', ticks=2400)
r('fuel_distribution_laminate_form', '燃料分布层片热压封边', 'fuel_capillary_wick*16 nano_ceramic*32 gtceu:polybenzimidazole_foil*128', 'fuel_distribution_laminate*32', 'gtceu:polyimide*18432')
r('fuel_charge_degas', '浸注燃料载荷真空脱气', 'honkai_carbon_charge*16 fuel_capillary_wick*4', 'degassed_fuel_charge*16', 'honkai_coolant*8000', 'hot_honkai_coolant*8000', tool='fuel_loading_pressure_shoe*1')
r('fuel_loading_pack_press', '燃料包芯料分区预压实', 'degassed_fuel_charge*16 fuel_distribution_laminate*16 gtceu:graphene_foil*128', 'pressed_fuel_loading_pack*16', 'honkai_stabilization_medium*4000', 'spent_honkai_stabilization_medium*4000', tool='fuel_loading_pressure_shoe*1')
r('fuel_primer_regenerate', '失效预润湿液真空分馏', '', 'fuel_pore_cleaning_sludge*8', 'spent_fuel_prewetting_primer*16000', 'soulium_process_solvent*8000 honkai_stabilization_medium*2000 unrecoverable_process_effluent*6000')
r('fuel_wick_reclaim', '载荷毛细芯选择脱载', 'degassed_fuel_charge*16', 'fuel_capillary_wick*2 inactive_fuel_residue*8', 'fuel_waste_processing_fluid*8000', 'fuel_refining_residual*8000')
r('fuel_pore_sludge_recover', '燃料清孔残渣湿法残能回收', 'fuel_pore_cleaning_sludge*32', 'inactive_fuel_residue*8 gtceu:carbon_dust*16 separation_residue*8', 'honkai_analysis_reagent*4000', 'spent_analysis_reagent*4000')
r('fuel_pack_rework', '燃料包芯料破包返工', 'pressed_fuel_loading_pack*16', 'degassed_fuel_charge*12 fuel_distribution_laminate*8 fuel_pore_cleaning_sludge*8', 'soulium_process_solvent*4000', 'spent_soulium_solvent*4000')
r('fuel_carrier_open_pore', '碳载体脉冲清孔', 'honkai_carbon_carrier*16 fuel_pore_opening_granule*16', 'opened_fuel_carrier*16 fuel_pore_cleaning_sludge*8', 'gtceu:hydrogen*16000', tool='fuel_loading_pressure_shoe*1')
link('industrial_honkai_carbon_loading', 'fuel_capillary_wick*1', tool='fuel_metering_injector*1', reason='毛细芯分配燃料，定量浸注头约束载量，替代单纯浸泡的工艺假设。')
link('approved_hdv_p09', 'pressed_fuel_loading_pack*8 fuel_distribution_laminate*32', reason='包芯料及分布层片承担棒内燃料固定和孔隙控制，接入既有燃料棒封装阵列。')


group('I07', 14, '', 'precision_metrology')
for identifier, zh, en, appearance, purpose in [
    ('metrology_quartz_blank', '计量石英谐振坯', 'Metrology Quartz Resonator Blank', '透明六边薄片，银色电极尚未修调。', '频率基准的压电前驱。'),
    ('metrology_clock_reference', '实体频率基准', 'Physical Frequency Reference', '透明六边晶片带金色双电极和黑色封边。', '检测器与时序节点的实际频率参照。'),
    ('metrology_optical_flat', '计量光学平晶', 'Metrology Optical Flat', '青白透明圆盘，边缘有细银色镀层。', '提供精密干涉面的基底。'),
    ('metrology_path_reference', '干涉光程基准', 'Interferometric Path Reference', '两块平晶以黑银间隔框固定，中心微蓝。', '形成已知光程，供差分和相位测量。'),
    ('metrology_resistor_blank', '精密电阻网络坯', 'Precision Resistor Network Blank', '白色陶瓷片上四条深灰折线，端点裸银。', '热修调前的电阻网络。'),
    ('metrology_resistance_reference', '实体电阻基准', 'Physical Resistance Reference', '白陶瓷片上等长灰线，四角金色Kelvin端子。', '测量桥和增益校准的精密电阻。'),
    ('metrology_shunt_blank', '低漂移分流器坯', 'Low Drift Shunt Blank', '银铜厚条中部开狭槽，四点测量端。', '大电流四端采样前驱。'),
    ('metrology_current_reference', '实体电流基准', 'Physical Current Reference', '银铜分流片嵌黑陶瓷座，青色四端连线。', '提供差分采样及电流测量参照。'),
    ('metrology_pressure_diaphragm', '计量压力膜片', 'Metrology Pressure Diaphragm', '银色圆膜刻三圈波纹，中央小凸点。', '制备温补压力基准。'),
    ('metrology_pressure_reference', '温补压力基准', 'Temperature Compensated Pressure Reference', '银色圆膜封入蓝灰方座，金色电桥端子。', '校准采样腔和液态探测器压力。'),
    ('metrology_leak_blank', '微孔漏率件坯', 'Microleak Standard Blank', '黑银短柱中有细长毛细孔。', '几何修整形成可溯源微漏。'),
    ('metrology_leak_reference', '实体漏率基准', 'Physical Leak Rate Reference', '黑银短柱有金色锁定环与蓝色孔口。', '检漏仪和密封结构的流导参照。'),
    ('metrology_thermopile_blank', '计量热电堆坯', 'Metrology Thermopile Blank', '银金交错U形导片排在白色陶瓷上。', '成对热电偶的装配前驱。'),
    ('metrology_thermal_reference', '实体温差基准', 'Physical Temperature Difference Reference', '蓝红双端的小型热电堆，银色散热面。', '温度差分测量及液体测量头的补偿。'),
    ('metrology_field_coil', '计量磁场线圈坯', 'Metrology Field Coil Blank', '铜色双线圈绕在黑色方框两端。', '磁场基准的对称线圈。'),
    ('metrology_field_reference', '实体磁场基准', 'Physical Magnetic Field Reference', '铜色双线圈中央有银色定位块，青色端子。', '磁性测量和工艺电场的参照。'),
    ('metrology_dielectric_blank', '计量介质叠层坯', 'Metrology Dielectric Stack Blank', '灰白陶瓷薄片与银箔层层交替。', '制备低损耗电容基准。'),
    ('metrology_capacitance_reference', '实体电容基准', 'Physical Capacitance Reference', '白银叠片封入蓝灰壳，金色双端引脚。', '电桥相位及阻抗测量的参照。'),
    ('metrology_gain_card', '探测增益修调卡', 'Detector Gain Trim Card', '墨绿卡上有四个金色可调电阻岛。', '固化探测器模拟前端的增益参数。'),
    ('metrology_dark_noise_card', '暗噪声补偿卡', 'Dark Noise Compensation Card', '黑色遮光盖封住白色参考电桥，金边卡。', '隔离外部信号获得电路本底补偿。'),
    ('metrology_impedance_bridge', '计量阻抗桥', 'Metrology Impedance Bridge', '银黑方架内四臂分别为白蓝电阻电容。', '整合电流、电阻和电容参照的实体桥。'),
    ('metrology_scattering_reference', '实体散射基准', 'Physical Scattering Reference', '磨砂蓝宝石方片有三种刻蚀网格。', '固相探测与光学仪器的散射参照。'),
    ('metrology_liquid_cell', '计量液相标准池', 'Metrology Liquid Reference Cell', '透明蓝色方池由银框封装，左右铂电极。', '液相测量头中提供稳定光程和电极几何。'),
    ('metrology_solid_angle_aperture', '计量立体角孔板', 'Metrology Solid Angle Aperture', '银黑圆片刻多个不同孔径的同心孔阵。', '定义固体与粒子探测接收范围。'),
    ('metrology_phase_reference', '实体相位基准片', 'Physical Phase Reference Tile', '青白双平晶夹住金色谐振片，黑色方框。', '为差分、气相及能态探测提供相位参照。'),
    ('integrated_metrology_standard', '集成计量基准组', 'Integrated Metrology Standard', '银黑抽屉盒内分别封装白电阻、蓝电容及透明晶片。', '把独立基准合成可复用工装，用于液相探测器升级和群控校时。'),
    ('detector_alignment_cartridge', '探测前端对准组件', 'Detector Front End Alignment Cartridge', '银框内含金边双卡和青色光路。', '整合增益、本底与相位补偿，进入探测器总装。'),
    ('metrology_alignment_socket', '计量对准转接座', 'Metrology Alignment Socket', '银色十字基座配黑色三点运动学定位块。', '探测器升级时用于固定液相测量头的三点转接座。'),
    ('liquid_reference_measurement_head', '液相基准测量头', 'Liquid Reference Measurement Head', '蓝色透明测量池外置银色压力膜和红蓝温补片。', '液态探测器集成温度、压力及光程测量头。'),
]:
    item(identifier, zh, en, appearance, purpose)
r('metrology_quartz_polish', '压电石英计量坯精抛', 'gtceu:quartzite_dust*128 gtceu:platinum_foil*64 gtceu:graphene_foil*64', 'metrology_quartz_blank*16', ticks=2400)
r('metrology_frequency_trim', '压电晶片频率修调', 'metrology_quartz_blank*16 gtceu:gold_foil*64 gtceu:polybenzimidazole_foil*128', 'metrology_clock_reference*8')
r('metrology_optical_flat_lap', '蓝宝石平晶差分研抛', 'gtceu:sapphire_lens*32 gtceu:diamond_dust*32 gtceu:platinum_foil*64', 'metrology_optical_flat*16')
r('metrology_path_pair', '双平晶已知光程配对', 'metrology_optical_flat*16 gtceu:neutronium_plate*64 gtceu:polyetheretherketone_foil*128', 'metrology_path_reference*8')
r('metrology_resistor_deposit', '陶瓷精密电阻网络沉积', 'gtceu:alumina_dust*128 gtceu:graphene_foil*128 gtceu:platinum_foil*64', 'metrology_resistor_blank*16')
r('metrology_resistor_trim', '四端电阻桥热修调', 'metrology_resistor_blank*16 gtceu:gold_foil*64 gtceu:polybenzimidazole_foil*128', 'metrology_resistance_reference*8')
r('metrology_shunt_mill', '四端低漂移分流器加工', 'gtceu:copper_plate*128 gtceu:manganese_dust*64 gtceu:nickel_dust*64', 'metrology_shunt_blank*16')
r('metrology_shunt_certify', '分流器等电位端修整', 'metrology_shunt_blank*16 gtceu:alumina_dust*128 gtceu:gold_foil*64', 'metrology_current_reference*8')
r('metrology_diaphragm_shape', '波纹压力膜片应力定形', 'gtceu:neutronium_plate*128 gtceu:platinum_foil*64 gtceu:polyetheretherketone_foil*64', 'metrology_pressure_diaphragm*16')
r('metrology_pressure_bridge', '温补压力电桥封装', 'metrology_pressure_diaphragm*16 metrology_resistance_reference*4 gtceu:gold_foil*64', 'metrology_pressure_reference*8')
r('metrology_microleak_drill', '计量微漏毛细孔加工', 'gtceu:neutronium_plate*128 gtceu:polyetheretherketone_foil*64 gtceu:diamond_dust*32', 'metrology_leak_blank*16')
r('metrology_microleak_trim', '毛细孔流导修整', 'metrology_leak_blank*16 metrology_optical_flat*4 gtceu:gold_foil*64', 'metrology_leak_reference*8')
r('metrology_thermopile_join', '成对热电偶计量堆焊接', 'gtceu:platinum_foil*128 gtceu:gold_foil*128 gtceu:alumina_dust*128', 'metrology_thermopile_blank*16')
r('metrology_thermal_pair', '热电堆温差配对封装', 'metrology_thermopile_blank*16 metrology_resistance_reference*4 gtceu:polybenzimidazole_foil*128', 'metrology_thermal_reference*8')
r('metrology_field_coil_wind', '对称计量磁场线圈绕制', 'gtceu:fine_copper_wire*256 gtceu:graphene_foil*128 gtceu:alumina_dust*128', 'metrology_field_coil*16')
r('metrology_field_balance', '双线圈磁场均匀区对准', 'metrology_field_coil*16 metrology_current_reference*4 gtceu:neutronium_plate*64', 'metrology_field_reference*8')
r('metrology_dielectric_stack', '低损耗计量介质叠片', 'gtceu:alumina_dust*128 gtceu:platinum_foil*128 gtceu:polyetheretherketone_foil*128', 'metrology_dielectric_blank*16')
r('metrology_capacitor_trim', '叠片电容边缘补偿修调', 'metrology_dielectric_blank*16 gtceu:gold_foil*64 gtceu:graphene_foil*64', 'metrology_capacitance_reference*8')
r('metrology_gain_card_program', '探测增益电阻组修调', 'metrology_resistance_reference*8 gtceu:gold_foil*128 kubejs:optical_ram_chip*32', 'metrology_gain_card*8')
r('metrology_noise_card_shield', '暗噪声参考电桥屏蔽封装', 'metrology_resistance_reference*8 metrology_current_reference*4 gtceu:graphene_foil*128', 'metrology_dark_noise_card*8')
r('metrology_impedance_bridge_assemble', '三基准阻抗电桥装配', 'metrology_resistance_reference*4 metrology_current_reference*4 metrology_capacitance_reference*4 gtceu:neutronium_plate*128', 'metrology_impedance_bridge*4')
r('metrology_scattering_etch', '多尺度散射基准刻蚀', 'metrology_optical_flat*16 gtceu:diamond_dust*32 gtceu:graphene_foil*64', 'metrology_scattering_reference*8')
r('metrology_liquid_cell_seal', '铂电极液相标准池封装', 'stability_transport_ampoule*4 metrology_optical_flat*8 gtceu:platinum_foil*128 gtceu:polyetheretherketone_foil*128', 'metrology_liquid_cell*4', research='RN-LSE')
r('metrology_solid_aperture_trim', '粒子探测立体角孔板修调', 'gtceu:neutronium_plate*128 gtceu:platinum_foil*128 metrology_scattering_reference*4', 'metrology_solid_angle_aperture*8')
r('metrology_phase_plate', '谐振频率与干涉相位联合基准', 'metrology_clock_reference*8 metrology_path_reference*8 gtceu:gold_foil*128', 'metrology_phase_reference*8')
r('metrology_standard_integrate', '四种实体计量基准集成', 'metrology_clock_reference*4 metrology_path_reference*4 metrology_resistance_reference*4 metrology_capacitance_reference*4 gtceu:neutronium_plate*128 gtceu:polyetheretherketone_foil*128', 'integrated_metrology_standard*4', ticks=2400)
r('metrology_detector_alignment', '探测前端本底增益相位集成', 'metrology_gain_card*4 metrology_dark_noise_card*4 metrology_phase_reference*4 gtceu:neutronium_plate*128', 'detector_alignment_cartridge*4')
r('metrology_alignment_socket_make', '运动学三点对准转接座制造', 'metrology_solid_angle_aperture*4 metrology_field_reference*4 metrology_impedance_bridge*4 gtceu:neutronium_plate*128', 'metrology_alignment_socket*4')
r('metrology_liquid_head_integrate', '液相光程温压基准测量头集成', 'metrology_liquid_cell*4 metrology_pressure_reference*4 metrology_thermal_reference*4 metrology_leak_reference*4 detector_alignment_cartridge*8 metrology_alignment_socket*4 gtceu:neutronium_plate*128', 'liquid_reference_measurement_head*4', tool='integrated_metrology_standard*1', research='RN-LSE')
link('approved_hcv_d01', 'liquid_reference_measurement_head*2', reason='液态探测器增加集成光程、温度、压力测量头，减少用通用高阶材料代表全部测量能力。')


group('I02', 14, '', 'analytical_instrumentation')
for identifier, zh, en, appearance, purpose in [
    ('analytical_quartz_window', '分析级石英窗', 'Analytical Quartz Window', '透明方片四边磨砂，角部银色定位缺口。', '比色池、光学过滤和单色仪共同的实际光学基底。'),
    ('analytical_optical_cuvette', '分析级定程比色池', 'Analytical Fixed Path Cuvette', '透明细长方池，黑色遮光侧壁和银底。', '取代敞口样品，约束分析光程。'),
    ('analytical_reference_disc', '光谱反射参照片', 'Spectral Reflectance Reference Disc', '白色磨砂圆片分为三档灰色反射区。', '对分析光源的反射与亮度进行参照。'),
    ('analytical_exchange_powder', '分析离子交换粉', 'Analytical Ion Exchange Powder', '淡米色细粉，夹少量琥珀色颗粒。', '制备分析吸附剂及新鲜分析试剂。'),
    ('analytical_preconditioned_sorbent', '预处理分析吸附剂', 'Preconditioned Analytical Sorbent', '琥珀小颗粒均匀包浅蓝薄膜。', '装入固相微萃取筒，稳定捕获痕量组分。'),
    ('analytical_extraction_cartridge', '分析固相微萃取筒', 'Analytical Solid Phase Extraction Cartridge', '透明细管内为琥珀吸附层，两端银白过滤塞。', '分析前富集液态痕量组分，作为通用分析耗材。'),
    ('loaded_analytical_extraction_cartridge', '载样分析微萃取筒', 'Loaded Analytical Extraction Cartridge', '微萃取管内吸附层呈紫蓝色。', '洗脱释放样品，回收筒体和部分吸附剂。'),
    ('analytical_sample_microgrid', '分析样品微栅', 'Analytical Sample Microgrid', '铜金细网固定在黑色方形框内。', '支撑固体样品、截面制样和电子束分析。'),
    ('analytical_polishing_puck', '金刚石精抛块', 'Diamond Fine Polishing Puck', '深灰圆块表面为颗粒状蓝灰抛光面。', '截面精抛消耗件，磨屑参与回收。'),
    ('analytical_embedded_sample', '分析镶嵌样', 'Embedded Analytical Specimen', '透明琥珀树脂小圆饼内嵌紫色微粒。', '固定已取得样品，供截面形貌分析。'),
    ('analytical_polished_section', '精抛分析截面', 'Polished Analytical Cross Section', '琥珀圆饼切面露出银紫分层结构。', '作为材料再制造与纳米工艺的物理参照。'),
    ('analytical_spectral_filter', '窄带分析滤光片', 'Narrowband Analytical Filter', '青紫渐变薄片镶入银色方框。', '屏蔽分析光谱中的离带干扰。'),
    ('analytical_diffraction_slit', '光谱精密狭缝', 'Precision Spectral Slit', '黑银双刀口片，中央一条细亮缝。', '定义单色仪入射光束。'),
    ('analytical_spectrum_grating', '分析光谱刻线光栅', 'Analytical Ruled Spectral Grating', '银色镜片表面为细密青紫平行纹。', '将复合光谱分成可测量波段。'),
    ('analytical_monochromator', '分析级单色器', 'Analytical Monochromator', '银黑小盒开有青紫双光口，侧面金色微调轮。', '整合狭缝、光栅和滤光片，实际选择分析波段。'),
    ('analytical_reference_cell', '分析光学参照池', 'Analytical Optical Reference Cell', '黑银框内有透明短池，背面白色参照片。', '比较主样品和空白光路，减少基线漂移。'),
    ('analytical_lamp_cathode', '分析灯空心阴极', 'Analytical Lamp Hollow Cathode', '银色筒形电极中有凹下的金属靶。', '产生材料特征谱线的实体光源部件。'),
    ('analytical_line_source', '特征谱线分析光源', 'Characteristic Line Analytical Source', '透明短灯管内为银色空心阴极，紫蓝电极端。', '支持分析光谱仪及分析级测量头。'),
    ('analytical_ion_source', '微束分析离子源', 'Microbeam Analytical Ion Source', '银黑细管装金色环电极，中心青蓝小孔。', '用于受控剖析与离子交换颗粒活化。'),
    ('analytical_balance_pan', '微量分析称量舟', 'Microanalytical Weighing Boat', '银白窄舟两端抬起，底部金色细线。', '微量固体分析样品的实际承载件。'),
    ('analytical_microbalance_head', '微量分析称量头', 'Microanalytical Balance Head', '银色小舟悬在黑色弹性梁和金色电桥上。', '为粉体和包覆工艺提供定量材料参照。'),
    ('analytical_filter_cake', '分析富集滤饼', 'Analytical Concentration Filter Cake', '灰紫薄饼内有细小琥珀颗粒。', '分析和萃取的固定副产，回收离子交换粉及残能。'),
    ('analytical_porosity_probe', '分析微孔探针', 'Analytical Porosity Probe', '银色细针连黑色陶瓷座，尖端三条微孔。', '对燃料载体及陶瓷流道提供孔隙参照。'),
    ('analytical_thermal_probe', '分析量热探头', 'Analytical Calorimetric Probe', '银色圆盘夹红蓝热电丝，黑色外环。', '为稳定化和退火工艺提供真实量热部件。'),
    ('analytical_spectrograph_head', '集成分析光谱头', 'Integrated Analytical Spectrograph Head', '银黑长盒集成紫色灯管、青色光口与双参照池。', '把光源、单色器和参照池整合，接入既有样品分析。'),
]:
    item(identifier, zh, en, appearance, purpose)
fluid('analytical_optical_couplant', '分析光学耦合液', 'Analytical Optical Couplant', 0xB1BBCF, '匹配分析窗与样品折射率，独立新鲜合成。')
fluid('spent_analytical_couplant', '失效分析耦合液', 'Spent Analytical Couplant', 0x827A97, '截面制样及光学耦合后的含样尾液。')
r('analysis_window_polish', '分析石英窗超精研抛', 'gtceu:quartzite_dust*128 gtceu:diamond_dust*32 gtceu:platinum_foil*64', 'analytical_quartz_window*32', 'gtceu:grade_16_purified_water*16000')
r('analysis_cuvette_bond', '定程比色池精密粘接', 'analytical_quartz_window*32 gtceu:graphene_foil*64 gtceu:polyetheretherketone_foil*128', 'analytical_optical_cuvette*8', 'gtceu:polyimide*9216')
r('analysis_reflectance_disc', '反射参照片梯度烧结', 'gtceu:alumina_dust*128 gtceu:silicon_dioxide_dust*128 gtceu:platinum_dust*32', 'analytical_reference_disc*16', 'gtceu:argon*16000')
r('analysis_exchange_powder', '微孔离子交换粉功能化', 'gtceu:zeolite_dust*128 gtceu:silicon_dioxide_dust*128 gtceu:graphene_dust*64', 'analytical_exchange_powder*64', 'gtceu:hydrochloric_acid*8000 gtceu:grade_16_purified_water*8000')
r('analysis_sorbent_condition', '分析吸附剂新鲜预处理', 'analytical_exchange_powder*32 gtceu:polybenzimidazole_foil*64', 'analytical_preconditioned_sorbent*32', 'gtceu:ethanol*8000 gtceu:grade_16_purified_water*8000')
r('analysis_cartridge_fill', '固相微萃取筒分层装填', 'analytical_preconditioned_sorbent*32 analytical_quartz_window*16 gtceu:platinum_foil*64 gtceu:polyetheretherketone_foil*64', 'analytical_extraction_cartridge*16', 'gtceu:polyimide*9216')
r('analysis_trace_extract', '液态崩坏痕量固相富集', 'analytical_extraction_cartridge*8', 'loaded_analytical_extraction_cartridge*8', 'liquid_honkai_energy*800 honkai_analysis_reagent*4000', 'spent_analysis_reagent*4000', research='RN-HSA')
r('analysis_cartridge_elute', '载样微萃取筒选择洗脱', 'loaded_analytical_extraction_cartridge*8', 'analytical_preconditioned_sorbent*12 concentrated_honkai_impurity*4 analytical_filter_cake*4', 'gtceu:ethanol*8000', 'spent_analytical_couplant*8000', research='RN-HSA')
r('analysis_sample_grid_weave', '固体分析样品微栅织造', 'gtceu:fine_copper_wire*256 gtceu:gold_foil*64 gtceu:polyetheretherketone_foil*128', 'analytical_sample_microgrid*32', 'gtceu:polyimide*9216')
r('analysis_polishing_puck', '金刚石精抛块结合剂固化', 'gtceu:diamond_dust*64 gtceu:carbon_dust*128 gtceu:stainless_steel_foil*128', 'analytical_polishing_puck*16', 'gtceu:reinforced_epoxy_resin*18432')
r('analysis_sample_embed', '既有样品截面树脂镶嵌', 'analyzed_honkai_sample*8 analytical_sample_microgrid*8', 'analytical_embedded_sample*8', 'gtceu:reinforced_epoxy_resin*9216 analytical_optical_couplant*4000', 'spent_analytical_couplant*4000', research='RN-HSA')
r('analysis_section_polish', '镶嵌样截面逐级精抛', 'analytical_embedded_sample*8 analytical_polishing_puck*2', 'analytical_polished_section*8 analytical_filter_cake*4', 'gtceu:grade_16_purified_water*8000', 'spent_analytical_couplant*8000', research='RN-HSA')
r('analysis_filter_deposit', '分析滤光片窄带膜沉积', 'analytical_quartz_window*16 gtceu:platinum_foil*64 gtceu:graphene_foil*128', 'analytical_spectral_filter*16', 'gtceu:argon*16000')
r('analysis_slit_lap', '光谱双刀口精密狭缝研合', 'gtceu:neutronium_plate*128 gtceu:graphene_foil*128 gtceu:diamond_dust*32', 'analytical_diffraction_slit*16', 'gtceu:grade_16_purified_water*8000')
r('analysis_grating_rule', '光谱光栅纳米刻线', 'analytical_quartz_window*16 gtceu:platinum_foil*128 gtceu:gold_foil*64', 'analytical_spectrum_grating*8', 'gtceu:argon*16000', tool='analytical_diffraction_slit*1')
r('analysis_monochromator_integrate', '狭缝光栅单色器集成', 'analytical_diffraction_slit*8 analytical_spectrum_grating*8 analytical_spectral_filter*8 gtceu:neutronium_plate*128', 'analytical_monochromator*4', 'gtceu:polyimide*18432')
r('analysis_reference_cell_assemble', '空白光学参照池装配', 'analytical_optical_cuvette*8 analytical_reference_disc*8 gtceu:graphene_foil*128', 'analytical_reference_cell*8', 'analytical_optical_couplant*4000')
r('analysis_lamp_cathode', '特征谱线空心阴极制作', 'gtceu:platinum_dust*64 gtceu:gold_dust*64 gtceu:neutronium_plate*128', 'analytical_lamp_cathode*16', 'gtceu:argon*16000')
r('analysis_line_source_seal', '特征谱线光源惰性充气封装', 'analytical_lamp_cathode*8 analytical_quartz_window*16 gtceu:polyetheretherketone_foil*64', 'analytical_line_source*8', 'gtceu:argon*16000 gtceu:helium*8000')
r('analysis_ion_source_align', '微束离子源电极对中', 'analytical_diffraction_slit*8 gtceu:gold_foil*128 gtceu:neutronium_plate*128 gtceu:graphene_foil*128', 'analytical_ion_source*4', 'gtceu:helium*16000')
r('analysis_balance_pan_form', '微量分析称量舟成形', 'gtceu:platinum_foil*128 gtceu:gold_foil*64 gtceu:neutronium_plate*64', 'analytical_balance_pan*16', 'gtceu:argon*16000')
r('analysis_microbalance_assemble', '称量舟柔性电桥集成', 'analytical_balance_pan*8 metrology_resistance_reference*4 gtceu:graphene_foil*128 gtceu:polybenzimidazole_foil*128', 'analytical_microbalance_head*4', 'gtceu:polyimide*9216')
r('analysis_porosity_probe_form', '载体孔隙分析探针修调', 'analytical_diffraction_slit*4 gtceu:neutronium_plate*128 gtceu:platinum_foil*128 analytical_quartz_window*8', 'analytical_porosity_probe*4', 'gtceu:helium*16000')
r('analysis_thermal_probe_form', '分析量热探头热电配对', 'gtceu:copper_foil*128 analytical_reference_disc*8 gtceu:platinum_foil*128 gtceu:graphene_foil*128', 'analytical_thermal_probe*4', 'gtceu:polyimide*18432')
r('analysis_spectrograph_integrate', '双路光谱分析头集成', 'analytical_line_source*4 analytical_monochromator*4 analytical_reference_cell*8 gtceu:neutronium_plate*128 gtceu:polyetheretherketone_foil*128', 'analytical_spectrograph_head*4', 'gtceu:polyimide*18432', ticks=2400)
r('analysis_couplant_fresh', '新鲜光学耦合液均化', '', '', 'gtceu:ethyleneglycol*16000 gtceu:silicone_rubber*4608 gtceu:grade_16_purified_water*8000', 'analytical_optical_couplant*24000')
r('analysis_couplant_recover', '失效耦合液滤饼及溶剂分离', 'separation_filter*1', 'analytical_filter_cake*8', 'spent_analytical_couplant*16000', 'gtceu:ethyleneglycol*8000 unrecoverable_process_effluent*8000')
r('analysis_filter_cake_recover', '分析富集滤饼离子交换料回收', 'analytical_filter_cake*32', 'analytical_exchange_powder*16 concentrated_honkai_impurity*4 separation_residue*8', 'gtceu:hydrochloric_acid*8000', 'spent_analysis_reagent*8000', research='RN-HSA')
r('analysis_reagent_reconstitute', '交换粉新鲜分析试剂配制', 'analytical_exchange_powder*32 gtceu:platinum_dust*32', '', 'gtceu:hydrochloric_acid*8000 gtceu:grade_16_purified_water*16000', 'honkai_analysis_reagent*24000', tool='analytical_ion_source*1')
link('approved_hbv_r13', 'analytical_extraction_cartridge*2 analytical_optical_cuvette*2', tool='analytical_spectrograph_head*1', reason='正常样品分析使用真实萃取耗材和固定光程比色池，光谱头控制波段；全部可在首份HW前由MAX常规原料首制。')
link('industrial_failed_package_section_analysis', 'analytical_polishing_puck*1', tool='analytical_polished_section*1', reason='已产生的失败封装做截面分析，精抛耗材和既有标准截面承担制样与形貌比较，不增加研究凭据。')
link('industrial_honkai_carbon_loading', tool='analytical_porosity_probe*1', reason='以微孔探针约束碳载体孔道，定量燃料浸注依据实际孔隙。')
link('approved_hbv_r18', tool='analytical_thermal_probe*1', reason='稳定化塔以量热探头测量反应热，探头来源为独立常规材料。')


group('I10', 15, 'RN-NBS', 'nano_functional_parts')
for identifier, zh, en, appearance, purpose in [
    ('nano_forming_mandrel', '纳米构型芯模', 'Nano Forming Mandrel', '银色细针阵列固定于黑色方台，尖端青点。', '限定纳米构筑件的实际尺度与连接位。'),
    ('nano_sacrificial_pore_template', '纳米牺牲孔道模板', 'Nano Sacrificial Pore Template', '白色多孔方片，孔道以灰色细线交叉。', '为沉积空心支撑与微流道提供可溶出模板。'),
    ('nano_hollow_strut', '纳米空心支撑柱', 'Nano Hollow Strut', '银色短柱截面中空，外壁金色加固点。', '提供纳米阀、能量单元与执行器的轻量支撑。'),
    ('nano_manifold_blank', '纳米歧管沉积坯', 'Nano Manifold Deposition Blank', '灰白小板内嵌银色分叉细管。', '溶出模板后成为真实连通微流道。'),
    ('nano_microfluidic_manifold', '纳米微流道歧管', 'Nano Microfluidic Manifold', '黑银薄板上青色树枝状流道清晰。', '向纳米构筑单元分配工作介质。'),
    ('nano_valve_blank', '纳米阀芯坯', 'Nano Valve Core Blank', '银色小锥阀连短细杆，紫灰底托。', '研配阀座后控制微流道开闭。'),
    ('nano_valve_seat', '纳米研配阀座', 'Nano Lapped Valve Seat', '黑陶瓷环内有银色锥面。', '与阀芯及微歧管形成定量输送单元。'),
    ('nano_dielectric_flexure', '纳米介质柔性铰', 'Nano Dielectric Flexure', '白蓝薄带中段呈弯折弹性桥，银色两端。', '隔离纳米关节并承担柔性运动。'),
    ('nano_piezo_drive_film', '纳米压电驱动膜', 'Nano Piezoelectric Drive Film', '白色薄膜双面金电极，中央蓝色压电纹。', '将电信号转成执行器位移。'),
    ('nano_magnetoresistive_pickup', '纳米磁阻拾取单元', 'Nano Magnetoresistive Pickup', '金边黑色方片中为四条青蓝折线。', '读取微执行器位置，不以通用电路代替位置检测。'),
    ('nano_energy_buffer', '纳米脉冲储能单元', 'Nano Pulse Energy Buffer', '黑银小柱由蓝白介电层交替叠成。', '吸收驱动脉冲并为纳米动作提供局部能量。'),
    ('nano_joint_flexure', '纳米关节弹性节', 'Nano Joint Flexure', '银色双叉由白蓝弹性膜相连。', '作为纳米驱动节的无间隙连接件。'),
    ('nano_bearing_shell', '纳米轴承座', 'Nano Bearing Shell', '银黑小环，内侧白色陶瓷滚道。', '容纳滚珠，支撑纳米驱动转子。'),
    ('nano_bearing_ball', '纳米陶瓷滚珠', 'Nano Ceramic Bearing Ball', '数颗白灰球珠，边缘有淡蓝高光。', '纳米轴承的实际滚动接触件。'),
    ('nano_bearing_pack', '纳米轴承组件', 'Nano Bearing Pack', '黑银环内排列白色小球，金色保持架。', '整合座、滚珠和保持架。'),
    ('nano_drive_stator', '纳米驱动定子', 'Nano Drive Stator', '金色细绕组嵌银黑环，中心青色磁面。', '纳米驱动执行器的固定磁路。'),
    ('nano_drive_rotor', '纳米驱动转子', 'Nano Drive Rotor', '银色细轴两端金色磁极，中央黑色转鼓。', '与定子、轴承配合输出受控运动。'),
    ('nano_drive_cartridge', '纳米驱动集成芯', 'Nano Drive Cartridge', '黑银短筒开窗显示金色定子和白色轴承。', '把运动部件整合，服务构筑单元和机械装配。'),
    ('nano_molecular_delivery_tip', '纳米分子输送尖端', 'Nano Molecular Delivery Tip', '银色细锥阵列从青色微流板伸出。', '在微流道末端定量沉积工作物。'),
    ('nano_surface_receptor_film', '纳米表面受体膜', 'Nano Surface Receptor Film', '灰蓝薄片上有细小金色受体点阵。', '接收界面化学信号，补足纳米单元感测功能。'),
    ('nano_functional_tile', '纳米功能集成片', 'Nano Functional Tile', '银黑方片集成青色流道、金色执行器与白色储能柱。', '整合传感、执行、输送和局部供能，接入既有纳米构筑单元。'),
    ('spent_nano_pore_template', '溶出纳米模板残料', 'Dissolved Nano Template Residue', '灰白破碎孔架覆少量银色细膜。', '回收模板无机材料与金属沉积损失。'),
]:
    item(identifier, zh, en, appearance, purpose)
fluid('nano_piezo_precursor_slurry', '纳米压电前驱浆', 'Nano Piezoelectric Precursor Slurry', 0xA8AFCC, '钛酸盐前驱分散浆，成膜后提供实际压电驱动。')
r('nano_mandrel_form', '纳米构型芯模尖端精整', 'gtceu:neutronium_plate*128 gtceu:diamond_dust*64 gtceu:platinum_foil*128', 'nano_forming_mandrel*4', 'gtceu:argon*32000')
r('nano_pore_template_form', '纳米牺牲孔道模板成形', 'gtceu:silicon_dioxide_dust*256 gtceu:alumina_dust*128 gtceu:polybenzimidazole_foil*128', 'nano_sacrificial_pore_template*32', 'gtceu:polyvinyl_butyral*18432')
r('nano_hollow_strut_deposit', '模板表面空心支撑沉积', 'nano_sacrificial_pore_template*16 gtceu:platinum_foil*128 gtceu:graphene_foil*128', 'nano_hollow_strut*32 spent_nano_pore_template*8', 'soulium_precursor_fluid*8000', 'nano_reaction_tail_liquid*8000', tool='nano_forming_mandrel*1')
r('nano_manifold_deposit', '歧管分叉流道共形沉积', 'nano_sacrificial_pore_template*16 nano_hollow_strut*16 gtceu:graphene_foil*128', 'nano_manifold_blank*16', 'soulium_precursor_fluid*8000', 'nano_reaction_tail_liquid*8000', tool='nano_deposition_stencil*1')
r('nano_manifold_release', '微流道模板选择溶出', 'nano_manifold_blank*16', 'nano_microfluidic_manifold*16 spent_nano_pore_template*8', 'honkai_circuit_etchant*8000', 'spent_honkai_etchant*8000')
r('nano_valve_core_form', '纳米阀芯圆锥面精整', 'nano_hollow_strut*16 gtceu:neutronium_plate*128 gtceu:diamond_dust*32', 'nano_valve_blank*32', 'nano_surface_passivation_liquid*4000', 'spent_nano_passivation_liquid*4000')
r('nano_valve_seat_lap', '陶瓷阀座锥面研配', 'nano_ceramic*128 gtceu:diamond_dust*32 nano_hollow_strut*16', 'nano_valve_seat*32', 'gtceu:grade_16_purified_water*8000')
r('nano_dielectric_flexure_form', '纳米介质弹性桥成膜', 'nano_ceramic*64 gtceu:polybenzimidazole_foil*256 gtceu:graphene_foil*128', 'nano_dielectric_flexure*32', 'gtceu:polyimide*18432')
r('nano_piezo_slurry_blend', '钛酸盐压电前驱浆配制', 'gtceu:barium_dust*128 gtceu:titanium_dust*128 gtceu:zirconium_oxide_dust*64', '', 'soulium_process_solvent*16000 nano_surface_passivation_liquid*4000', 'nano_piezo_precursor_slurry*20000')
r('nano_piezo_film_cast', '压电驱动膜电极成形', 'gtceu:gold_foil*128 nano_dielectric_flexure*16', 'nano_piezo_drive_film*32', 'nano_piezo_precursor_slurry*16000', 'nano_reaction_tail_liquid*8000', tool='nano_deposition_stencil*1')
r('nano_pickup_bridge_form', '四臂纳米磁阻拾取桥沉积', 'gtceu:nickel_dust*128 gtceu:iron_dust*128 gtceu:gold_foil*128 nano_ceramic*64', 'nano_magnetoresistive_pickup*32', 'nano_surface_passivation_liquid*4000', 'spent_nano_passivation_liquid*4000')
r('nano_energy_buffer_stack', '纳米脉冲储能介电叠层', 'nano_ceramic*128 gtceu:graphene_foil*256 gtceu:platinum_foil*128', 'nano_energy_buffer*32', 'gtceu:polyimide*18432')
r('nano_joint_flexure_assemble', '无间隙纳米关节弹性节装配', 'nano_dielectric_flexure*32 nano_hollow_strut*32 gtceu:gold_foil*128', 'nano_joint_flexure*32', 'gtceu:soldering_alloy*73728')
r('nano_bearing_shell_form', '纳米轴承座陶瓷滚道成形', 'nano_ceramic*128 gtceu:neutronium_plate*128 gtceu:graphene_foil*128', 'nano_bearing_shell*32', 'nano_surface_passivation_liquid*4000', 'spent_nano_passivation_liquid*4000')
r('nano_bearing_ball_lap', '纳米陶瓷滚珠级配研磨', 'nano_ceramic*128 gtceu:diamond_dust*32', 'nano_bearing_ball*128', 'gtceu:grade_16_purified_water*16000', tool='nano_forming_mandrel*1')
r('nano_bearing_pack_assemble', '纳米滚动轴承保持架装配', 'nano_bearing_shell*32 nano_bearing_ball*128 gtceu:gold_foil*128', 'nano_bearing_pack*32', 'gtceu:lubricant*4000')
r('nano_drive_stator_wind', '纳米驱动定子磁路绕制', 'nano_hollow_strut*32 gtceu:fine_cosmic_wire*256 gtceu:graphene_foil*128', 'nano_drive_stator*32', 'gtceu:polyimide*18432')
r('nano_drive_rotor_form', '纳米转子磁极定向成形', 'nano_hollow_strut*32 gtceu:nickel_dust*128 gtceu:iron_dust*128', 'nano_drive_rotor*32', 'soulium_precursor_fluid*8000', 'nano_reaction_tail_liquid*8000')
r('nano_drive_cartridge_integrate', '纳米驱动定转子闭环集成', 'nano_drive_stator*16 nano_drive_rotor*16 nano_bearing_pack*32 nano_joint_flexure*16 nano_magnetoresistive_pickup*16', 'nano_drive_cartridge*16', 'gtceu:lubricant*4000 gtceu:super_mutated_living_solder*73728', tool='nano_forming_mandrel*1')
r('nano_delivery_tip_assemble', '分子输送尖端阀路集成', 'nano_microfluidic_manifold*16 nano_valve_blank*32 nano_valve_seat*32 nano_hollow_strut*32', 'nano_molecular_delivery_tip*16', 'nano_surface_passivation_liquid*4000', 'spent_nano_passivation_liquid*4000')
r('nano_receptor_film_form', '纳米表面化学受体膜沉积', 'nano_dielectric_flexure*16 gtceu:gold_foil*128 gtceu:graphene_foil*128', 'nano_surface_receptor_film*32', 'honkai_interface_priming_liquid*8000', 'spent_honkai_interface_carrier*8000')
r('nano_functional_tile_integrate', '感测执行供能输送四功能集成', 'nano_drive_cartridge*8 nano_molecular_delivery_tip*8 nano_energy_buffer*16 nano_surface_receptor_film*16 nano_piezo_drive_film*16 gtceu:cosmic_foil*128', 'nano_functional_tile*8', 'gtceu:super_mutated_living_solder*147456 nano_surface_passivation_liquid*8000', 'spent_nano_passivation_liquid*8000', ticks=3200)
r('nano_template_reclaim', '溶出模板无机骨架分离', 'spent_nano_pore_template*32', 'gtceu:silicon_dioxide_dust*64 gtceu:alumina_dust*32 gtceu:platinum_dust*8', 'gtceu:hydrochloric_acid*8000', 'unrecoverable_process_effluent*8000')
link('approved_hcv_p16', 'nano_functional_tile*4', tool='nano_forming_mandrel*1', reason='构筑单元增加具有感测、执行、局部供能、分子输送功能的集成片；集成片从常规材料首制，未使用构筑单元本身。')
link('approved_x_n03', 'nano_joint_flexure*8 nano_bearing_pack*8', reason='纳米驱动节实际消耗弹性关节与陶瓷轴承，连接新构型与旧驱动件。')
link('approved_x_s01', tool='analytical_microbalance_head*1', reason='成核颗粒的固体配比采用微量称量头，分析设备的实体产物服务旧材料工艺。')


group('I11', 15, 'RN-NRA', 'robotic_subassemblies')
for identifier, zh, en, appearance, purpose in [
    ('nanobot_joint_gaiter', '纳米机器人关节护套', 'Nanobot Joint Gaiter', '黑色折叠软套两端银环，青色密封唇。', '保护关节流道和轴承，接入换装腕及功能组件。'),
    ('nanobot_microgripper', '纳米机器人微夹爪', 'Nanobot Microgripper', '两片银色弯指连黑色弹性根部。', '承担实体抓取，防止机械臂只有通用电路。'),
    ('nanobot_inertial_pickup', '纳米机器人惯性拾取件', 'Nanobot Inertial Pickup', '金色框内十字悬臂托住银色小质量块。', '提供运动闭环中的惯性读数。'),
    ('nanobot_adhesion_sole', '纳米机器人附着足垫', 'Nanobot Adhesion Sole', '灰黑分瓣圆垫，底面青色微沟纹。', '支撑攀附和位置固定。'),
    ('nanobot_optical_encoder', '纳米机器人光学编码器', 'Nanobot Optical Encoder', '黑银小盘刻金色码道，侧面青色光口。', '测量关节转角，结合惯性件形成闭环。'),
    ('nanobot_microfluidic_pump', '纳米机器人微流泵', 'Nanobot Microfluidic Pump', '银色小泵体露出青色双腔及金色压电膜。', '为纳米机器人工作介质循环供压。'),
    ('nanobot_recirculation_block', '纳米机器人循环歧管', 'Nanobot Recirculation Block', '黑银方块中为青色闭合流道，四侧小接口。', '把泵、阀、分子输送接口整合。'),
    ('nanobot_tool_coupler', '纳米机器人快换接头', 'Nanobot Quick Change Coupler', '银黑三爪圆座内有金色触点和蓝色流体密封圈。', '允许同一机体装配不同实体工具。'),
    ('nanobot_contact_bumper', '纳米机器人接触缓冲垫', 'Nanobot Contact Bumper', '灰蓝弧形垫内嵌金色网格。', '保护微夹爪和附着足免受硬碰撞。'),
    ('nanobot_telemetry_bank', '纳米机器人遥测存储块', 'Nanobot Telemetry Bank', '黑色微型存储堆有金色边脚与青色状态窗。', '记录位移、工具和流量反馈，供控制核使用。'),
    ('nanobot_toolchange_wrist', '纳米机器人快换腕', 'Nanobot Tool Change Wrist', '银色转腕前端三爪接头，后部黑色护套。', '将夹爪、足垫及快换接口集成。'),
    ('nanobot_power_distributor', '纳米机器人局部配电板', 'Nanobot Local Power Distribution Board', '黑银板连接蓝白储能柱，金色分流路径。', '隔离各执行器脉冲，服务机器人功能总成。'),
    ('nanobot_functional_cartridge', '纳米机器人功能总成', 'Nanobot Functional Cartridge', '银色微型机体露出金色编码盘、青色流道及双腕。', '未编程机器人总装的传感、执行、工具与流体功能包。'),
    ('robotic_closedloop_servo_pod', '机器人闭环伺服舱', 'Robotic Closed Loop Servo Pod', '黑银短舱有金色编码盘与青色惯性小窗。', '将多源反馈闭环做成可复用高阶伺服部件。'),
]:
    item(identifier, zh, en, appearance, purpose)
r('nanobot_gaiter_seal', '机器人关节折叠护套封边', 'nano_dielectric_flexure*32 gtceu:polybenzimidazole_foil*256 gtceu:neutronium_plate*128', 'nanobot_joint_gaiter*32', 'gtceu:silicone_rubber*18432')
r('nanobot_gripper_assemble', '弹性节微夹爪装配', 'nano_joint_flexure*32 nano_piezo_drive_film*32 gtceu:neutronium_plate*128', 'nanobot_microgripper*32', 'gtceu:super_mutated_living_solder*73728', tool='actuator_preload_gauge*1')
r('nanobot_inertial_assemble', '悬臂质量块惯性拾取件装配', 'nano_joint_flexure*32 nano_magnetoresistive_pickup*32 gtceu:gold_foil*128 gtceu:neutronium_plate*128', 'nanobot_inertial_pickup*32', 'gtceu:polyimide*18432')
r('nanobot_sole_form', '微沟附着足垫复合', 'nano_surface_receptor_film*32 nano_dielectric_flexure*32 gtceu:graphene_foil*256', 'nanobot_adhesion_sole*32', 'gtceu:silicone_rubber*18432')
r('nanobot_encoder_align', '光学编码盘与读头对准', 'metrology_optical_flat*16 nano_magnetoresistive_pickup*16 gtceu:gold_foil*128 gtceu:sapphire_lens*32', 'nanobot_optical_encoder*16', 'gtceu:polyimide*18432', tool='metrology_phase_reference*1')
r('nanobot_pump_assemble', '双腔压电微流泵装配', 'nano_microfluidic_manifold*16 nano_piezo_drive_film*32 nano_valve_blank*32 nano_valve_seat*32', 'nanobot_microfluidic_pump*16', 'gtceu:polyimide*18432')
r('nanobot_recirculation_assemble', '机器人闭式工作介质流路装配', 'nanobot_microfluidic_pump*16 nano_microfluidic_manifold*16 nano_molecular_delivery_tip*16 gtceu:graphene_foil*128', 'nanobot_recirculation_block*16', 'nano_surface_passivation_liquid*8000', 'spent_nano_passivation_liquid*8000')
r('nanobot_tool_coupler_assemble', '电流体双路快换接头装配', 'nano_joint_flexure*32 nano_valve_seat*32 gtceu:gold_foil*128 gtceu:neutronium_plate*128', 'nanobot_tool_coupler*32', 'gtceu:silicone_rubber*18432')
r('nanobot_bumper_form', '接触缓冲垫层间封接', 'nano_surface_receptor_film*32 gtceu:graphene_foil*256 gtceu:polybenzimidazole_foil*256', 'nanobot_contact_bumper*32', 'gtceu:silicone_rubber*18432')
r('nanobot_telemetry_assemble', '多源反馈遥测存储块装配', 'kubejs:optical_ram_chip*128 nano_energy_buffer*32 gtceu:gold_foil*128 gtceu:cosmic_foil*128', 'nanobot_telemetry_bank*16', 'gtceu:super_mutated_living_solder*147456')
r('nanobot_wrist_integrate', '抓附快换腕功能集成', 'nanobot_tool_coupler*16 nanobot_microgripper*16 nanobot_adhesion_sole*16 nanobot_joint_gaiter*16 nano_drive_cartridge*16', 'nanobot_toolchange_wrist*16', 'gtceu:lubricant*8000 gtceu:super_mutated_living_solder*147456', tool='actuator_preload_gauge*1')
r('nanobot_power_distribution', '局部储能与分流配电板装配', 'nano_energy_buffer*32 metrology_current_reference*8 gtceu:gold_foil*256 gtceu:cosmic_foil*128', 'nanobot_power_distributor*16', 'gtceu:polyimide*18432')
r('nanobot_functional_integrate', '机器人感知执行工具流路总成', 'nanobot_toolchange_wrist*16 nanobot_recirculation_block*8 nanobot_optical_encoder*16 nanobot_inertial_pickup*8 nanobot_telemetry_bank*8 nanobot_power_distributor*8 nanobot_contact_bumper*16', 'nanobot_functional_cartridge*8', 'gtceu:super_mutated_living_solder*294912 nano_surface_passivation_liquid*16000', 'spent_nano_passivation_liquid*16000', ticks=3200)
r('nanobot_scrap_salvage', '纳米装配废料分组解离', 'nano_assembly_scrap*32', 'nano_hollow_strut*8 gtceu:gold_dust*16 inactive_nano_unit*8', 'fuel_waste_processing_fluid*8000', 'nano_reaction_tail_liquid*8000')
r('nanobot_servo_pod_integrate', '光学惯性磁阻闭环伺服舱', 'nano_drive_cartridge*16 nanobot_optical_encoder*16 nanobot_inertial_pickup*16 nano_magnetoresistive_pickup*16 nanobot_telemetry_bank*8', 'robotic_closedloop_servo_pod*8', 'gtceu:super_mutated_living_solder*147456 gtceu:lubricant*8000', tool='actuator_preload_gauge*1', ticks=2400)
r('nanobot_wrist_remanufacture', '快换腕可拆执行部件回收', 'nanobot_toolchange_wrist*16', 'nanobot_tool_coupler*8 nano_drive_cartridge*8 nano_joint_flexure*8 nano_assembly_scrap*8', 'soulium_process_solvent*8000', 'spent_soulium_solvent*8000')
link('approved_hcv_p18', 'nanobot_functional_cartridge*2', reason='未编程机器人以真实传感、执行、工具、流路功能总成组装，编程之前就具有实体工作部件。')
link('approved_qsv_e06', 'robotic_closedloop_servo_pod*4', reason='四象限伺服模块采用包含光学、惯性和磁阻反馈的闭环伺服舱。')


group('I12', 15, 'RN-NSP', 'bounded_swarm_control')
for identifier, zh, en, appearance, purpose in [
    ('swarm_quorum_latch_blank', '群体仲裁锁存坯', 'Swarm Quorum Latch Blank', '黑色方片上三组金色交叉触点尚未封闭。', '制备有限节点仲裁锁存器。'),
    ('swarm_quorum_latch', '群体仲裁锁存器', 'Swarm Quorum Latch', '黑色方片中三组金色触点围绕青色中心。', '保证群控命令一次获得明确多数。'),
    ('swarm_clock_ring_blank', '群体时钟环坯', 'Swarm Clock Ring Blank', '银黑环上等距金色节点未接桥。', '建立环形时序传播结构。'),
    ('swarm_synchronized_clock_ring', '群体同步时钟环', 'Swarm Synchronized Clock Ring', '金色节点以青色同心线相连的黑银环。', '为分布式节点提供相同时间基准。'),
    ('swarm_watchdog_cutout', '群体看门狗断离器', 'Swarm Watchdog Cutout', '银黑小盒中央有红色机械断路片和金色触点。', '失去有效心跳时断开执行通道。'),
    ('swarm_reservation_matrix', '群体资源预约矩阵', 'Swarm Resource Reservation Matrix', '黑色矩阵板上金色分区格与青色互锁线。', '调度有限工具、流路和动作空间，避免冲突。'),
    ('swarm_fault_isolator', '群体故障隔离节点', 'Swarm Fault Isolation Node', '黑银四端节点中央白色隔离环。', '将故障成员从群控信号链断离。'),
    ('swarm_sensor_bus', '群体传感汇集总线', 'Swarm Sensor Aggregation Bus', '金色树枝状线束压在灰蓝薄板上。', '把位置、惯性和介质信号送到融合节点。'),
    ('swarm_clock_fanout', '群体时钟扇出器', 'Swarm Clock Fanout', '青色中心晶片向金色八端放射连线。', '向多成员分发同步脉冲。'),
    ('swarm_sensor_fusion_tile', '群体传感融合片', 'Swarm Sensor Fusion Tile', '银黑方片上蓝色交叉线连接三个金色拾取区。', '联合位置、惯性与接触输入形成动作反馈。'),
    ('swarm_trajectory_tile', '群体轨迹约束片', 'Swarm Trajectory Constraint Tile', '黑色板面刻青色三维路径和金色边界点。', '把动作限制在有限工作空间。'),
    ('swarm_tool_scheduler', '群体工具调度片', 'Swarm Tool Scheduler', '黑金板上四个工具端口经青色开关相连。', '协调快换腕、夹爪和输送尖端。'),
    ('swarm_gradient_decoder', '群体介质梯度解码片', 'Swarm Medium Gradient Decoder', '灰蓝膜片金色点阵逐级加密，侧边青色梳齿。', '解码表面化学梯度和介质流向。'),
    ('swarm_motion_protocol', '群体运动协议芯片', 'Swarm Motion Protocol Chip', '黑银小芯片上有青色关节路径和金色触点。', '把闭环反馈转换成实际运动时序。'),
    ('swarm_fluid_protocol', '群体微流协议芯片', 'Swarm Microfluidic Protocol Chip', '黑银小芯片上青色分叉流道与阀门点阵。', '定义泵、阀与分子尖端的定量输送行为。'),
    ('swarm_fabrication_protocol', '群体构筑协议芯片', 'Swarm Fabrication Protocol Chip', '黑银小芯片上为金色逐层构筑网格。', '定义有限模板内的沉积和装配顺序。'),
    ('swarm_boundary_mask_blank', '群体工作边界掩膜坯', 'Swarm Work Boundary Mask Blank', '灰银薄板表面未完成的黑色网格。', '提供不可越过的物理工作区域模板。'),
    ('swarm_boundary_mask', '群体工作边界掩膜', 'Swarm Work Boundary Mask', '银色掩膜上青色工作区被黑色双框包围。', '限定群体可工作的范围，供安全控制核和生长模板使用。'),
    ('nanobot_firmware_tile', '纳米机器人执行固件片', 'Nanobot Execution Firmware Tile', '黑色金边存储片上有青色闭合回路线。', '从未编程机器人固化为具体有限行为，独立于正式研究完成记录。'),
    ('bounded_swarm_firmware', '受限群体协作固件', 'Bounded Swarm Cooperation Firmware', '银黑模块内三颗协议芯和青色时钟环。', '整合仲裁、同步和三种动作协议。'),
    ('swarm_admitted_worker_group', '受限纳米工作编组', 'Bounded Nano Worker Group', '透明银框盒内几枚带金色工具腕的青黑微体。', '由实体机器人配置成有限工作编组，接入涂层工艺。'),
    ('swarm_safety_interlock_core', '群体安全互锁核', 'Swarm Safety Interlock Core', '黑银立方核中央白环，四角红色断路点。', '把故障隔离、看门狗和边界保护整合进群控核心。'),
    ('circuit_directional_growth_template', '电路定向生长控制模板', 'Circuit Directional Growth Control Template', '金边透明板内为青色定向线路和黑色边界掩膜。', '限定适配基板的线路生长方向与可达区域。'),
    ('swarm_task_router', '群体工序路由核', 'Swarm Process Routing Core', '银黑六端核心上有青色箭头连三块金色协议片。', '调度实体编组的运动、流体与构筑工序。'),
]:
    item(identifier, zh, en, appearance, purpose)
r('swarm_quorum_blank', '有限节点仲裁锁存阵列制作', 'kubejs:optical_ram_chip*128 gtceu:gold_foil*256 gtceu:cosmic_foil*128', 'swarm_quorum_latch_blank*32', 'gtceu:super_mutated_living_solder*147456')
r('swarm_quorum_close', '仲裁锁存反馈环闭合', 'swarm_quorum_latch_blank*32 metrology_gain_card*8 gtceu:fine_cosmic_wire*256', 'swarm_quorum_latch*32', 'gtceu:polyimide*18432', tool='nano_swarm_quorum_encoder*1')
r('swarm_clock_ring_form', '环形群体时钟互连制作', 'nano_swarm_timing_node*32 gtceu:gold_foil*256 gtceu:graphene_foil*128', 'swarm_clock_ring_blank*32', 'gtceu:super_mutated_living_solder*147456')
r('swarm_clock_ring_sync', '群体时钟环相位同步', 'swarm_clock_ring_blank*32 metrology_clock_reference*8 gtceu:fine_cosmic_wire*256', 'swarm_synchronized_clock_ring*32', 'gtceu:polyimide*18432', tool='integrated_metrology_standard*1')
r('swarm_watchdog_assemble', '失联断离机械电互锁装配', 'nano_joint_flexure*32 nanobot_power_distributor*16 gtceu:neutronium_plate*128 gtceu:gold_foil*128', 'swarm_watchdog_cutout*32', 'gtceu:super_mutated_living_solder*73728')
r('swarm_reservation_assemble', '工具流道动作空间预约矩阵', 'swarm_quorum_latch*32 nanobot_telemetry_bank*16 gtceu:cosmic_foil*256', 'swarm_reservation_matrix*16', 'gtceu:super_mutated_living_solder*147456')
r('swarm_fault_isolate_assemble', '群成员信号故障隔离节点', 'swarm_watchdog_cutout*16 nano_joint_isolation_membrane*64 gtceu:gold_foil*128 gtceu:graphene_foil*256', 'swarm_fault_isolator*32', 'gtceu:polyimide*18432')
r('swarm_sensor_bus_assemble', '位置惯性接触信号汇集总线', 'nanobot_optical_encoder*16 nanobot_inertial_pickup*16 nano_surface_receptor_film*32 gtceu:fine_cosmic_wire*256', 'swarm_sensor_bus*16', 'gtceu:polyimide*18432')
r('swarm_clock_fanout_assemble', '同步脉冲多端扇出器装配', 'swarm_synchronized_clock_ring*16 nano_energy_buffer*32 gtceu:gold_foil*256', 'swarm_clock_fanout*32', 'gtceu:super_mutated_living_solder*147456')
r('swarm_sensor_fusion', '多源传感融合片配置', 'swarm_sensor_bus*16 nanobot_telemetry_bank*16 metrology_gain_card*16', 'swarm_sensor_fusion_tile*16', 'gtceu:polyimide*18432')
r('swarm_trajectory_configure', '有限轨迹约束片配置', 'swarm_reservation_matrix*16 swarm_sensor_fusion_tile*16 kubejs:optical_ram_chip*128', 'swarm_trajectory_tile*16', 'gtceu:super_mutated_living_solder*147456')
r('swarm_tool_schedule', '快换工具时序调度片配置', 'swarm_reservation_matrix*16 swarm_clock_fanout*16 nanobot_tool_coupler*32', 'swarm_tool_scheduler*16', 'gtceu:polyimide*18432')
r('swarm_gradient_decode', '表面介质梯度解码片配置', 'nano_surface_receptor_film*32 nano_magnetoresistive_pickup*16 nanobot_telemetry_bank*16', 'swarm_gradient_decoder*16', 'honkai_interface_priming_liquid*8000', 'spent_honkai_interface_carrier*8000')
r('swarm_motion_protocol_compile', '闭环关节运动协议固化', 'swarm_trajectory_tile*16 swarm_sensor_fusion_tile*16 swarm_tool_scheduler*16 gtceu:cosmic_foil*256', 'swarm_motion_protocol*16', 'gtceu:super_mutated_living_solder*147456')
r('swarm_fluid_protocol_compile', '微泵阀组定量输送协议固化', 'swarm_gradient_decoder*16 nanobot_recirculation_block*16 swarm_clock_fanout*16 gtceu:cosmic_foil*256', 'swarm_fluid_protocol*16', 'gtceu:super_mutated_living_solder*147456')
r('swarm_fabrication_protocol_compile', '有限模板构筑顺序固化', 'swarm_tool_scheduler*16 nano_forming_mandrel*4 swarm_reservation_matrix*16 gtceu:cosmic_foil*256', 'swarm_fabrication_protocol*16', 'gtceu:super_mutated_living_solder*147456')
r('swarm_boundary_blank', '工作边界双层掩膜沉积', 'gtceu:neutronium_plate*128 gtceu:graphene_foil*256 gtceu:gold_foil*128', 'swarm_boundary_mask_blank*32', 'gtceu:polyimide*18432')
r('swarm_boundary_configure', '有限工作区边界模板刻写', 'swarm_boundary_mask_blank*32 metrology_solid_angle_aperture*8 gtceu:cosmic_foil*128', 'swarm_boundary_mask*32', 'honkai_circuit_etchant*8000', 'spent_honkai_etchant*8000')
r('nanobot_firmware_compile', '单成员执行固件校时写入', 'swarm_clock_fanout*16 swarm_fault_isolator*16 kubejs:optical_ram_chip*256 gtceu:gold_foil*256', 'nanobot_firmware_tile*32', 'gtceu:super_mutated_living_solder*147456')
r('bounded_swarm_firmware_integrate', '仲裁时序三协议协作固件整合', 'swarm_motion_protocol*16 swarm_fluid_protocol*16 swarm_fabrication_protocol*16 swarm_quorum_latch*16 swarm_synchronized_clock_ring*16 nanobot_firmware_tile*32', 'bounded_swarm_firmware*16', 'gtceu:super_mutated_living_solder*294912', ticks=3200)
r('swarm_worker_admission', '实体纳米机器人有限编组', 'unprogrammed_nanobot*16 bounded_swarm_firmware*8 swarm_boundary_mask*16', 'swarm_admitted_worker_group*8 inactive_nano_unit*4', 'soulium_process_solvent*8000', 'spent_soulium_solvent*8000')
r('swarm_safety_interlock_integrate', '故障失联工作边界三重互锁整合', 'swarm_fault_isolator*16 swarm_watchdog_cutout*16 swarm_boundary_mask*16 nanobot_power_distributor*16', 'swarm_safety_interlock_core*8', 'gtceu:super_mutated_living_solder*147456')
r('circuit_growth_template_configure', '电路定向生长有限区域模板', 'swarm_boundary_mask*16 swarm_fabrication_protocol*16 analytical_polished_section*8 gtceu:cosmic_foil*256', 'circuit_directional_growth_template*8', 'circuit_growth_medium*8000', 'spent_circuit_growth_medium*8000')
r('swarm_task_router_integrate', '运动流体构筑三工序路由核', 'swarm_motion_protocol*8 swarm_fluid_protocol*8 swarm_fabrication_protocol*8 swarm_tool_scheduler*8 nanobot_telemetry_bank*8 swarm_safety_interlock_core*8', 'swarm_task_router*8', 'gtceu:super_mutated_living_solder*147456')
r('swarm_worker_refresh', '失活纳米单元清洗与执行固件重装', 'inactive_nano_unit*32 nanobot_firmware_tile*16 nano_drive_cartridge*8', 'unprogrammed_nanobot*8 nano_assembly_scrap*16', 'soulium_process_solvent*16000 nano_surface_passivation_liquid*8000', 'spent_soulium_solvent*16000 spent_nano_passivation_liquid*8000')
r('swarm_control_tile_reclaim', '协作固件存储及金属分离', 'bounded_swarm_firmware*16', 'kubejs:optical_ram_chip*64 gtceu:gold_dust*32 nano_assembly_scrap*16', 'fuel_waste_processing_fluid*8000', 'nano_reaction_tail_liquid*8000')
link('approved_hcv_p21', 'bounded_swarm_firmware*2 swarm_safety_interlock_core*1', reason='受控纳米群增加实际协作固件及故障互锁，正式研究与机器编组分开；两件首源均不使用受控纳米群。')
link('approved_x_n08', 'swarm_task_router*1', reason='有限群控核心消费三工序路由核，负责具体工具及介质调度。')
link('approved_hrv_e18', tool='circuit_directional_growth_template*1', reason='适配基板生长采用有物理边界和定向线路的模板，提供可复用高阶工装。')
link('approved_hrv_s04', 'swarm_admitted_worker_group*4', reason='抗侵蚀涂层增加带真实动作固件的纳米工作编组，执行表面覆盖。')


group('I13', 16, 'RN-HRC', 'functional_interface_coating')
for identifier, zh, en, appearance, purpose in [
    ('plasma_activated_anchor_mesh', '等离子活化锚固网', 'Plasma Activated Anchor Mesh', '黑银纤维网边缘呈均匀青蓝光泽。', '活化表面后与界面底胶形成可靠连接。'),
    ('graded_interface_bondfilm', '梯度界面粘接膜', 'Graded Interface Bond Film', '青灰薄膜与黑银纤维交错，截面层次递变。', '平缓陶瓷、金属与聚合物界面的应力差。'),
    ('coating_edge_barrier_gasket', '涂层端面阻隔垫', 'Coating Edge Barrier Gasket', '黑银长条垫中间为蓝白陶瓷夹层。', '封闭涂层端面，接入纳米群涂层和旧基板工艺。'),
    ('peelable_coating_mask', '可剥离涂层遮蔽膜', 'Peelable Coating Mask', '半透明灰蓝折片带琥珀色剥离边。', '保护接口区域，完成涂覆后移除。'),
    ('masked_barrier_patch', '遮蔽多层阻隔贴片', 'Masked Multilayer Barrier Patch', '蓝白层片覆半透明膜，金色边界标记。', '完成共形沉积但接口仍受遮蔽保护的工艺中间件。'),
    ('conformal_barrier_patch', '共形多层阻隔贴片', 'Conformal Multilayer Barrier Patch', '蓝白多层片露出整齐金色接口，黑银加强边。', '整合梯度底层与耐蚀阻隔层，供旧纳米涂层消费。'),
]:
    item(identifier, zh, en, appearance, purpose)
fluid('surface_activation_plasma_gas', '界面活化等离子工艺气', 'Interface Activation Plasma Process Gas', 0x7B9FD0, '氮氩低污染表面活化气，形成可润湿界面。')
fluid('ceramic_interface_bond_primer', '陶瓷界面粘接底胶', 'Ceramic Interface Bonding Primer', 0x99A7B9, '含无机纳米颗粒与聚合物链的独立新鲜底胶。')
r('surface_plasma_gas_blend', '氮氩界面活化工艺气配制', '', '', 'gtceu:nitrogen*64000 gtceu:argon*64000', 'surface_activation_plasma_gas*128000')
r('interface_primer_fresh', '陶瓷聚合物界面底胶分散', 'gtceu:silicon_dioxide_dust*128 gtceu:alumina_dust*128 gtceu:graphene_dust*64', '', 'gtceu:ethanol*16000 gtceu:polyimide*18432 honkai_interface_priming_liquid*8000', 'ceramic_interface_bond_primer*32000')
r('interface_mesh_plasma_activate', '锚固纤维网等离子表面活化', 'carbon_nanotube_anchoring_mesh*32', 'plasma_activated_anchor_mesh*32', 'surface_activation_plasma_gas*64000')
r('interface_gradient_bondfilm', '活化网梯度界面粘接成膜', 'plasma_activated_anchor_mesh*32 ceramic_interface_reinforced_fiber_sheet*32 gtceu:polybenzimidazole_foil*256', 'graded_interface_bondfilm*32', 'ceramic_interface_bond_primer*16000', 'spent_honkai_interface_carrier*8000')
r('coating_edge_gasket_press', '阻隔涂层端面垫热压', 'graded_interface_bondfilm*16 nano_joint_isolation_membrane*32 nano_ceramic*64', 'coating_edge_barrier_gasket*32', 'honkai_resistant_coating*8000', 'spent_resistant_coating*8000')
r('coating_mask_cast', '可剥离接口遮蔽膜流延', 'gtceu:polyetheretherketone_foil*256 gtceu:graphene_foil*128', 'peelable_coating_mask*32', 'gtceu:polyvinyl_butyral*18432 gtceu:ethanol*16000')
r('coating_masked_patch_deposit', '遮蔽多层阻隔贴片共形沉积', 'graded_interface_bondfilm*32 peelable_coating_mask*32', 'masked_barrier_patch*32', 'nano_barrier_ceramic_dispersion*16000 honkai_resistant_coating*8000', 'spent_resistant_coating*8000', tool='nano_barrier_spray_header*1')
r('coating_patch_unmask', '多层阻隔贴片接口去遮蔽', 'masked_barrier_patch*32', 'conformal_barrier_patch*32 nano_assembly_scrap*8', 'soulium_process_solvent*8000', 'spent_soulium_solvent*8000')
r('coating_patch_refurbish', '共形阻隔贴片分层回收', 'conformal_barrier_patch*32', 'plasma_activated_anchor_mesh*16 nano_ceramic*16 separation_residue*8', 'fuel_waste_processing_fluid*8000', 'nano_reaction_tail_liquid*8000')
link('approved_hrv_s04', 'conformal_barrier_patch*16 coating_edge_barrier_gasket*16', reason='多层贴片整合底胶、梯度过渡与阻隔涂层；端面垫封闭薄弱边缘，形成真实纳米涂层部件支线。')
link('approved_hdv_e01', 'graded_interface_bondfilm*16', reason='把梯度界面膜夹在压电谐振基片与金属骨架之间。这一步在 I13 的涂层研究后开放。')


group('I14', 16, 'RN-SPC', 'pressure_forming')
for identifier, zh, en, appearance, purpose in [
    ('hotpress_vent_insert', '热压排气流道镶件', 'Hot Press Vent Channel Insert', '银灰厚片中有树枝状黑色排气槽。', '成型工装，排出聚合及热压产生的气体。'),
    ('hotpress_deformable_capsule', '可变形热压包套', 'Deformable Hot Press Capsule', '银白薄壁盒有外翻边，侧面细密波纹。', '在热压中传递压力并隔绝污染。'),
    ('hotpress_vacuum_collar', '热压抽气封口环', 'Hot Press Vacuum Sealing Collar', '银色双层环带细长抽气支管与黑色密封边。', '封接包套及真空管路。'),
    ('hotpress_pressure_pack', '热压密闭传压包', 'Hermetic Hot Press Pressure Pack', '银白波纹方包带抽气支管，黑色排气镶件可见。', '整合包套、封口、排气与传压介质，接入旧压铸。'),
    ('hotpress_pressure_granule', '热压柔性传压颗粒', 'Hot Press Compliant Pressure Granule', '灰白细小圆柱颗粒，表面疏松。', '均匀传递压力，成型后回收无机粉料。'),
    ('forming_expansion_shim', '差胀补偿层片', 'Differential Expansion Compensation Shim', '铜银交替的薄弧片，边缘蓝色隔离线。', '缓冲模具与工件的热膨胀差。'),
    ('forming_load_balance_pad', '成型均载垫', 'Forming Load Equalization Pad', '黑银方垫内嵌蓝白弹性陶瓷网。', '降低局部过压，服务端盖和换热壳成型。'),
    ('ceramic_mold_release_paper', '陶瓷脱模隔离纸', 'Ceramic Mold Release Paper', '灰白柔性薄片上有蓝灰陶瓷细点。', '隔开模壁和工件，避免粘模。'),
    ('soulium_polymer_charge_cassette', '魂钢聚合装料匣', 'Soulium Polymerization Charge Cassette', '黑银分区盒内排列深灰粉坯和紫色颗粒。', '把定量混料、隔离和载荷分配集成为实际装料。'),
    ('pressure_coupling_blank', '等压耦合连接坯', 'Isostatic Coupling Connection Blank', '银黑厚块内有金色缓冲层和青色三叉接口。', '作为高载荷微歧管和承力节点的成型前驱。'),
    ('pressure_thermal_shell_blank', '均载换热壳坯', 'Load Balanced Thermal Shell Blank', '银白弧壳内为黑色分流槽和蓝白隔层。', '供旧电路冷板制造消耗的换热结构坯。'),
    ('forming_multiport_pressure_cap', '多口成型密封端盖', 'Multiport Forming Pressure Cap', '银色圆盖上多组金色接口，边沿黑色密封槽。', '集成端面承力和流路密封，接入压力设备组件。'),
]:
    item(identifier, zh, en, appearance, purpose)
r('hotpress_vent_insert_form', '热压排气树枝流道镶件成形', 'gtceu:neutronium_plate*256 gtceu:graphene_foil*256 nano_ceramic*128', 'hotpress_vent_insert*8', 'gtceu:polyimide*36864', tool='soulium_hotpress_porous_die*1')
r('hotpress_capsule_fold', '热压薄壁包套波纹成形', 'gtceu:stainless_steel_foil*512 gtceu:neutronium_plate*128 gtceu:polybenzimidazole_foil*256', 'hotpress_deformable_capsule*16', 'gtceu:polyimide*36864')
r('hotpress_vacuum_collar_join', '热压抽气支管与封口环封接', 'gtceu:neutronium_plate*256 gtceu:platinum_foil*128 gtceu:graphene_foil*128', 'hotpress_vacuum_collar*16', 'gtceu:super_mutated_living_solder*147456')
r('hotpress_pressure_granule_form', '无机柔性传压颗粒烧结', 'gtceu:alumina_dust*256 gtceu:zirconium_oxide_dust*128 gtceu:silicon_dioxide_dust*128', 'hotpress_pressure_granule*128', 'gtceu:polyvinyl_butyral*18432')
r('forming_expansion_shim_laminate', '金属差胀补偿层片复合', 'gtceu:copper_plate*256 gtceu:neutronium_plate*128 gtceu:graphene_foil*256', 'forming_expansion_shim*64', 'gtceu:polyimide*36864')
r('forming_equalization_pad_press', '柔性陶瓷均载垫热压', 'forming_expansion_shim*32 nano_joint_isolation_membrane*64 nano_ceramic*128', 'forming_load_balance_pad*32', 'gtceu:polybenzimidazole*18432')
r('forming_release_paper_cast', '陶瓷脱模隔离纸流延', 'gtceu:alumina_dust*128 gtceu:silicon_dioxide_dust*128 gtceu:graphene_foil*256', 'ceramic_mold_release_paper*64', 'gtceu:polyvinyl_butyral*18432')
r('hotpress_pressure_pack_assemble', '密闭排气传压包总装', 'hotpress_deformable_capsule*16 hotpress_vacuum_collar*16 hotpress_vent_insert*8 hotpress_pressure_granule*128 ceramic_mold_release_paper*32', 'hotpress_pressure_pack*16', 'gtceu:argon*64000')
r('soulium_charge_cassette_pack', '魂钢聚合分区定量装料', 'coated_nano_swarm*32 gtceu:tungsten_steel_dust*512 gtceu:neutronium_dust*256 soulium_grain_boundary_inoculant*64 ceramic_mold_release_paper*32 forming_expansion_shim*32', 'soulium_polymer_charge_cassette*16', 'soulium_precursor_fluid*16000', 'nano_reaction_tail_liquid*8000', ticks=3200)
r('forming_coupling_blank_press', '三叉接口等压耦合坯成形', 'soulium_structural_preform*32 hotpress_pressure_pack*8 forming_load_balance_pad*16 gtceu:cosmic_foil*256', 'pressure_coupling_blank*16', 'gtceu:argon*64000', tool='soulium_hotpress_porous_die*1', ticks=3200)
r('forming_thermal_shell_press', '均载冷道换热壳热压', 'soulium_structural_preform*32 hotpress_pressure_pack*8 forming_load_balance_pad*16 graded_interface_bondfilm*32 gtceu:graphene_foil*256', 'pressure_thermal_shell_blank*16', 'gtceu:argon*64000', tool='hotpress_vent_insert*1', ticks=3200)
r('forming_multiport_cap_press', '多口端面密封盖均载成形', 'pressure_coupling_blank*16 forming_expansion_shim*32 ceramic_mold_release_paper*32 gtceu:platinum_foil*128', 'forming_multiport_pressure_cap*16', 'gtceu:polyimide*36864')
r('hotpress_pack_dismantle', '密闭传压包分层拆解回收', 'hotpress_pressure_pack*16', 'hotpress_vacuum_collar*8 hotpress_vent_insert*4 gtceu:alumina_dust*32 gtceu:stainless_steel_dust*64', 'soulium_process_solvent*8000', 'spent_soulium_solvent*8000')
r('hotpress_capsule_metal_reclaim', '薄壁包套材料分离', 'hotpress_deformable_capsule*16', 'gtceu:stainless_steel_dust*128 gtceu:neutronium_dust*32 separation_residue*16', 'gtceu:hydrochloric_acid*16000', 'unrecoverable_process_effluent*16000')
link('approved_hrv_s09', 'soulium_polymer_charge_cassette*8 hotpress_pressure_pack*8', reason='聚合压铸增加已定量分区装料匣与密闭传压包，承担装料、脱气、隔离与均压；不依赖魂钢原始团块产物。')
link_output('quadrisystem_thermal_exchange_hub', 'pressure_thermal_shell_blank*8 forming_multiport_pressure_cap*8', reason='四系统换热枢纽实际消耗经过均载成型的换热壳及端盖，连接专用压铸支线。')


group('I15', 16, 'RN-SRA', 'reconstruction_heat_treatment')
for identifier, zh, en, appearance, purpose in [
    ('anneal_kinematic_holder', '退火运动学承托架', 'Annealing Kinematic Holder', '黑银三点承托框架，蓝白陶瓷接触垫。', '热处理期间支撑工件并允许可控膨胀。'),
    ('anneal_slip_shim', '退火滑移补偿片', 'Annealing Slip Compensation Shim', '银灰薄片夹黑色石墨滑移层。', '减少夹具约束引起的残余应力。'),
    ('anneal_getter_tray', '退火活性吸气托盘', 'Annealing Reactive Getter Tray', '银色浅盘内铺灰黑锆钛小颗粒，金色边框。', '捕捉炉内残余氧和腐蚀气体，使用后饱和。'),
    ('spent_anneal_getter_tray', '饱和退火吸气托盘', 'Saturated Annealing Getter Tray', '银浅盘中的颗粒变成灰白，边角紫黑。', '再生或拆解回收锆钛。'),
    ('anneal_temperature_witness', '退火温度见证片', 'Annealing Temperature Witness', '银色薄片有三条红蓝热敏带。', '实际热敏测量部件，和量热探头组成温度参照。'),
    ('anneal_gradient_guard', '退火温度梯度护罩', 'Annealing Thermal Gradient Guard', '银黑弧形罩内蓝白隔热层呈阶梯厚度。', '均衡工件表面热流，减少温差。'),
    ('vacuum_dried_soulium_charge', '真空脱挥魂钢料', 'Vacuum Devolatilized Soulium Charge', '紫灰金属块表面已无树脂光泽，有均匀细孔。', '预脱挥后进入分级退火，不替代旧稳定团块。'),
    ('homogenized_soulium_charge', '扩散均化魂钢料', 'Diffusion Homogenized Soulium Charge', '银紫金属块中不同相条带细化。', '经过扩散均化，继续应力松弛和组织调整。'),
    ('relaxed_soulium_charge', '应力松弛魂钢料', 'Stress Relaxed Soulium Charge', '银紫金属块表面为平滑均匀条纹。', '解除压铸内应力后控制析出与织构。'),
    ('aged_soulium_charge', '时效调理魂钢料', 'Age Conditioned Soulium Charge', '银灰块体内有规则细紫点。', '通过受控时效形成稳定微结构。'),
    ('textured_soulium_charge', '定向织构魂钢料', 'Textured Soulium Charge', '银紫块体截面呈整齐方向性层纹。', '为各向异性构件提供可制造的定向晶格。'),
    ('annealed_interface_blank', '退火界面连接坯', 'Annealed Interface Connection Blank', '银黑双层连接片由渐变紫纹界面结合。', '把热处理材料与金属连接位结合，接入后期承力组件。'),
    ('creep_conditioned_anchor', '蠕变调理锚固件', 'Creep Conditioned Anchor', '黑银短锚两端金属耳，中央紫色加强层。', '经载荷时效抑制长期蠕变，服务承力节点。'),
    ('anneal_quench_baffle', '退火冷却流整流板', 'Annealing Cooling Flow Baffle', '银色扇形板开渐变长孔，边缘蓝色温标。', '控制退火末段冷却流分配，避免热冲击。'),
]:
    item(identifier, zh, en, appearance, purpose)
fluid('anneal_thermal_contact_paste', '退火热接触浆', 'Annealing Thermal Contact Paste', 0x7F8D9D, '新鲜陶瓷和石墨热接触浆，降低夹具接触温差。')
fluid('spent_anneal_contact_paste', '失效退火热接触浆', 'Spent Annealing Thermal Contact Paste', 0x766B82, '热处理后夹带金属颗粒的接触浆，回收无机组分。')
fluid('anneal_clean_protective_gas', '退火净化保护气', 'Purified Annealing Protective Gas', 0xA0B8C7, '由吸气托盘净化的氩氢保护气，供分级热处理。')
r('anneal_holder_form', '三点运动学退火承托架制作', 'gtceu:neutronium_plate*256 nano_ceramic*128 gtceu:graphene_foil*256', 'anneal_kinematic_holder*8', 'gtceu:polyimide*36864', tool='soulium_anneal_expansion_mount*1')
r('anneal_slip_shim_form', '石墨滑移补偿片层合', 'gtceu:graphene_foil*512 gtceu:neutronium_plate*128 gtceu:platinum_foil*128', 'anneal_slip_shim*64', 'gtceu:polybenzimidazole*18432')
r('anneal_getter_tray_fill', '锆钛活性退火吸气托盘装填', 'gtceu:zirconium_dust*256 gtceu:titanium_dust*256 gtceu:neutronium_plate*128', 'anneal_getter_tray*16', 'gtceu:hydrogen*64000')
r('anneal_witness_form', '退火温度见证片热敏配对', 'metrology_thermal_reference*16 analytical_thermal_probe*8 gtceu:platinum_foil*128', 'anneal_temperature_witness*32', 'gtceu:polyimide*18432')
r('anneal_gradient_guard_form', '渐变隔热退火护罩制作', 'nano_ceramic*256 gtceu:neutronium_plate*256 gtceu:graphene_foil*256', 'anneal_gradient_guard*16', 'gtceu:polybenzimidazole*36864')
r('anneal_contact_paste_fresh', '新鲜退火热接触浆分散', 'gtceu:alumina_dust*256 gtceu:graphene_dust*128 gtceu:zirconium_oxide_dust*128', '', 'gtceu:ethyleneglycol*16000 gtceu:grade_16_purified_water*16000', 'anneal_thermal_contact_paste*32000')
r('anneal_gas_purify', '氩氢退火气吸气净化', 'anneal_getter_tray*4', 'spent_anneal_getter_tray*4', 'gtceu:argon*128000 gtceu:hydrogen*32000', 'anneal_clean_protective_gas*160000')
r('anneal_charge_vacuum_dry', '魂钢聚合料真空脱挥', 'soulium_proto_mass*32 anneal_slip_shim*16', 'vacuum_dried_soulium_charge*32 separation_residue*8', 'anneal_clean_protective_gas*64000', 'hot_soulium_exhaust*32000', tool='anneal_kinematic_holder*1')
r('anneal_charge_homogenize', '脱挥魂钢料扩散均化', 'vacuum_dried_soulium_charge*32 anneal_temperature_witness*8', 'homogenized_soulium_charge*32', 'anneal_clean_protective_gas*64000 anneal_thermal_contact_paste*8000', 'spent_anneal_contact_paste*8000', tool='anneal_gradient_guard*1', ticks=3200)
r('anneal_charge_relax', '均化魂钢料约束应力松弛', 'homogenized_soulium_charge*32 anneal_slip_shim*16', 'relaxed_soulium_charge*32', 'stress_relief_conditioning_bath*16000', 'spent_stress_relief_conditioning_bath*16000', tool='anneal_kinematic_holder*1', ticks=3200, research='RN-SRA RN-SPM')
r('anneal_charge_age', '魂钢料控制析出时效', 'relaxed_soulium_charge*32 anneal_temperature_witness*8', 'aged_soulium_charge*32', 'anneal_clean_protective_gas*64000', '', tool='anneal_gradient_guard*1', ticks=3200)
r('anneal_charge_texture', '时效料晶格织构定向', 'aged_soulium_charge*32 resonance_texture_seed*16', 'textured_soulium_charge*32', 'resonance_growth_solution*16000', 'spent_resonance_growth_solution*16000', tool='anneal_kinematic_holder*1', ticks=3200, research='RN-SRA RN-SPM')
r('anneal_interface_diffusion_bond', '定向织构料界面扩散连接', 'textured_soulium_charge*32 soulium_diffusion_bonding_interlayer*32 graded_interface_bondfilm*32 gtceu:cosmic_foil*256', 'annealed_interface_blank*16', 'anneal_clean_protective_gas*64000 anneal_thermal_contact_paste*16000', 'spent_anneal_contact_paste*16000', tool='anneal_kinematic_holder*1', ticks=3200)
r('anneal_anchor_creep_condition', '锚固连接件载荷蠕变调理', 'annealed_interface_blank*16 forming_expansion_shim*32 gtceu:neutronium_plate*256', 'creep_conditioned_anchor*16', 'anneal_clean_protective_gas*64000 honkai_coolant*16000', 'hot_honkai_coolant*16000', tool='anneal_gradient_guard*1', ticks=4000)
r('anneal_quench_baffle_form', '渐变冷却流整流板热定形', 'gtceu:neutronium_plate*256 gtceu:graphene_foil*256 nano_ceramic*128', 'anneal_quench_baffle*16', 'anneal_clean_protective_gas*64000')
r('anneal_interface_controlled_cool', '连接坯分区缓冷定型', 'annealed_interface_blank*16 anneal_quench_baffle*4', 'soulium_structural_preform*16', 'honkai_coolant*32000', 'hot_honkai_coolant*32000', tool='anneal_kinematic_holder*1', ticks=2400)
r('anneal_getter_regenerate', '饱和吸气托盘氢气补活', 'spent_anneal_getter_tray*16 gtceu:zirconium_dust*64 gtceu:titanium_dust*64', 'anneal_getter_tray*12 separation_residue*16', 'gtceu:hydrogen*64000')
r('anneal_getter_metal_reclaim', '饱和托盘金属组分回收', 'spent_anneal_getter_tray*16', 'gtceu:zirconium_dust*64 gtceu:titanium_dust*64 gtceu:neutronium_dust*32', 'gtceu:hydrochloric_acid*16000', 'unrecoverable_process_effluent*16000')
r('anneal_contact_paste_recover', '接触浆无机相分离', '', 'gtceu:alumina_dust*64 gtceu:carbon_dust*32 soulium_swarf*16', 'spent_anneal_contact_paste*16000', 'gtceu:ethyleneglycol*8000 unrecoverable_process_effluent*8000')
r('anneal_reconstruction_stabilizer', '退火热流与差胀组件集成', 'anneal_temperature_witness*16 anneal_slip_shim*32 anneal_gradient_guard*8 anneal_quench_baffle*8 gtceu:neutronium_plate*256', 'reactor_stabilizer*8', 'gtceu:super_mutated_living_solder*147456 anneal_thermal_contact_paste*8000', 'spent_anneal_contact_paste*8000', tool='anneal_kinematic_holder*1')
r('anneal_interface_reclaim', '扩散连接坯界面退层回收', 'annealed_interface_blank*16', 'soulium_swarf*64 nano_ceramic*16 gtceu:cosmic_dust*32', 'fuel_waste_processing_fluid*16000', 'nano_reaction_tail_liquid*16000')
r('anneal_creep_anchor_rework', '蠕变调理锚固件高温返修', 'creep_conditioned_anchor*16 anneal_slip_shim*16', 'annealed_interface_blank*12 soulium_swarf*16', 'anneal_clean_protective_gas*64000', '', tool='anneal_kinematic_holder*1', ticks=3200)
link('approved_hrv_s12', 'anneal_slip_shim*16 anneal_temperature_witness*8', tool='anneal_kinematic_holder*1 anneal_gradient_guard*1', reason='魂钢首轮重构退火增加差胀滑移、温度参照和均热承托；这些工装由普通MAX材料及早期纳米陶瓷制造，不使用稳定魂钢产物。')
link('approved_wfv_f01', 'creep_conditioned_anchor*8 pressure_coupling_blank*8', reason='结构传力节点采用经过蠕变调理和均压成形的实体锚固件。')
link_output('symmetric_multichip_interconnect_bridge', 'annealed_interface_blank*4', reason='多芯片互连桥通过退火扩散界面连接承载和电连接层。')


def write():
    OUT.mkdir(parents=True, exist_ok=True)
    (DATA / 'industrial_expansion_early_processes.json').write_text(json.dumps(dict(schema=1, recipes=recipes), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for asset in items + fluids:
        identifier = ns(asset['id'])
        asset['sources'] = [p['id'] for p in recipes if any(x['id'] == identifier for key in ['item_outputs', 'fluid_outputs'] for x in p[key])]
        asset['source_inputs'] = [dict(recipe_id=p['id'], title=p['title'], role=p['role'], item_inputs=p['item_inputs'], fluid_inputs=p['fluid_inputs'], item_catalysts=p['item_catalysts']) for p in recipes if p['id'] in asset['sources']]
        asset['uses'] = [p['id'] for p in recipes if any(x['id'] == identifier for key in ['item_inputs', 'fluid_inputs', 'item_catalysts'] for x in p[key])]
        asset['uses'] += [p['recipe_id'] for p in links if any(x['id'] == identifier for key in ['item_inputs', 'fluid_inputs', 'item_catalysts'] for x in p[key])]
    for entry in links:
        original = plans[entry['recipe_id']]
        entry['after'] = {key: original.get(key, []) + [x for candidate in links if candidate['recipe_id'] == entry['recipe_id'] for x in candidate[key]] for key in ['item_inputs', 'fluid_inputs', 'item_catalysts']}
    (OUT / 'early-assets.json').write_text(json.dumps(dict(items=items, fluids=fluids), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (OUT / 'early-links.json').write_text(json.dumps(links, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(recipes=len(recipes), items=len(items), fluids=len(fluids), roles=Counter(p['role'] for p in recipes)), ensure_ascii=False))


if __name__ == '__main__':
    write()
