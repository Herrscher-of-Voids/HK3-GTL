# -*- coding: utf-8 -*-
"""登记W05外观候选与W04材质迁移，不改变系统分数或批准数量。"""
from datetime import datetime
from pathlib import Path
import json
import shutil
import w05_wind_circuit_a1_20261112 as g


def load(path):
    return json.loads(path.read_text('utf8'))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def main():
    now = datetime.now().astimezone().isoformat()
    audit = g.ROOT / 'logs/beta5-completion-audit-20261030'
    history = g.LOG / ('audit-before-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
    history.mkdir()
    for name in ['index.html', 'current-summary.json']:
        shutil.copy2(audit / name, history / name)
    summary = load(history / 'current-summary.json')
    manifest = load(g.OUT / 'manifest.json')
    verification = load(g.OUT / 'verification.json')
    qa = load(g.LOG / 'viewer-qa.json')
    rel = g.OUT.relative_to(g.ROOT).as_posix()
    candidate = dict(
        id='W05', version='A1', title=manifest['title'], status='candidate_waiting_user_review',
        size_xyz=manifest['size'], blocks=manifest['blocks'], materials=len(g.STATES),
        components=len(manifest['component_bounds_blueprint']), preview=rel + '/index.html',
        interactive_preview=rel + '/三维评审.html', verification=rel + '/verification.json',
        viewer_qa='logs/w05-wind-circuit-a1-20261112/viewer-qa.json',
        animation_enabled=False, whole_integer_voxel=True, no_nominal_clipping=True,
        palette_identity=manifest['palette_identity'], controller_registered=False,
        approved=False, installed=False, game_verified=False, score_delta=0, updated_at=now,
        remaining='静态外观候选待评审；W05真实控制器、正式Pattern、配方、研究接入与运行仍未实现。')
    p4 = 'deliveries/W04_现存材质与通用接口_P4_20261112'
    p4_receipt = dict(
        preview=p4 + '/index.html', verification=p4 + '/verification.json',
        migration={'hk3gtl:wonder_thunder_casing': 'hk3gtl:voltage_machine_casing_hrv',
                   'hk3gtl:wonder_thunder_interface': 'hk3gtl:industrial_port_casing'},
        blocks=17440898, size_xyz=[941, 623, 1056], geometry_unchanged=True,
        remaining='保留三组交叠及14.083%龙首遮挡，巨手未制作，主控仍为红石块占位。',
        approved=False, installed=False, game_verified=False, score_delta=0)
    receipt = dict(
        updated_at=now, requested_work='继续后续多方块设计，实机测试交还负责人',
        candidate=candidate, w04_palette_migration=p4_receipt,
        structural_review=dict(
            method='源码坐标核对与七幅静态预览复核',
            controller_blueprint=manifest['controller_blueprint'], ports=manifest['ports'],
            fixes=['液压撑杆落在z±60的既有换热座上', '泵头补金属接套连接换向管',
                   '中央轴下接整流岛，底圈补转接环', '前庭阶梯置于控制器墙前'],
            flow_connection_radius=[198.204, 164.015],
            wind_eye_max_radius=110, airfoil_conservative_inner_x=182.858),
        export_readback=verification['readback'], rendered_quads=verification['viewer_rendered_quads'],
        viewer_qa=qa, audit_before=history.relative_to(g.ROOT).as_posix(),
        scores=dict(development=summary['development_metric']['overall_percent'],
                    acceptance=summary['overall_percent'], delta=0),
        game_desktop_instance_operations=False)
    save(g.LOG / 'design-delivery.json', receipt)
    system = next(x for x in summary['systems'] if x['id'] == 'multiblocks')
    system['previous_structure_design_candidate'] = system['structure_design_candidate']
    system['structure_design_candidate'] = candidate
    system['w05_wind_circuit_a1'] = candidate
    system['w04_palette_p4'] = p4_receipt
    system['updated_at'] = now
    summary['current_work']['previous_design_candidate'] = summary['current_work']['design_candidate']
    summary['current_work'].update(
        system='后续多方块外观设计', state='W05双层回流A1已导出真实方块静态预览；W04 P4完成现存材质迁移。',
        scope='仓库设计与离线导出；不操作游戏、桌面、活动实例或存档，不安装。',
        next_turn='继续未完成多方块的独立外观候选；负责人反馈后再修改对应建筑。',
        design_candidate=candidate)
    summary['wonder_design_delivery_receipt'] = 'logs/w05-wind-circuit-a1-20261112/design-delivery.json'
    summary['report_updated_at'] = now
    summary['updated_at'] = now
    save(audit / 'current-summary.json', summary)
    w, h, d = manifest['size']
    section = f'''<section id="w05-wind-circuit-current" class="notice"><h2>2026-11-12 · W05风之律者双层回流A1候选</h2>
<p>最新工作转回后续多方块设计；助手实机测试停止，验证交还负责人。W05采用HDV风息绿，运行目标WSV；双层闭合流道、中央扭转叶栅风眼、双侧上扬导流壳与四组回流泵组成{w}×{d}×{h}格候选，{manifest['blocks']:,}个真实方块，16构件，无动画。</p>
<p>NBT／Schematic逐格回读及7幅离线视图通过；预览只绘制整机最终归属表面，保留既有评审界面。主控红石块与八接口为位置示意，W05控制器、Pattern及正式工艺尚未实现，外观待批准。W04 P4仅迁移两种已删除材质；三组交叠、14.083%遮挡及巨手缺项保持。</p>
<p>研发{summary['development_metric']['overall_percent']:.5f}%、原验收{summary['overall_percent']:.5f}%，37域、原分母、原分数及批准数量不变。<a href="../../{rel}/index.html">W05候选</a> · <a href="../../{p4}/index.html">W04 P4</a> · <a href="../w05-wind-circuit-a1-20261112/design-delivery.json">交付回执</a></p></section>'''
    page = (history / 'index.html').read_text('utf8')
    (audit / 'index.html').write_text(page.replace('<body><main>', '<body><main>' + section, 1), 'utf8')
    note = f'''\n\n## 2026-11-12 后续多方块设计：W05双层回流A1与W04材质P4\n\n- 负责人要求停止助手实机、回到未完成多方块设计。本轮只生成仓库候选，不操作游戏、桌面、活动实例或存档，不安装。\n- W05「风之律者 · 长风·理想流体环流阵」首版独立候选：`{rel}/index.html`。实际宽{w}×深{d}×高{h}，{manifest['blocks']:,}实体、16构件；双层闭合回流、中央扭转叶栅、双侧上扬导流壳与四组泵。HDV风息绿身份，运行目标WSV；无动画，真实方块贴图，完整NBT/Schematic逐格回读与7幅离线视图通过。\n- W05控制器未注册；红石块明确占位，周围同面3×3八块工业接口嵌墙。外观未批准、未安装，Pattern、正式配方和研究接入未实现；不增加系统分数或批准数量。旧表289×321×97仅作参考，不裁切新候选。\n- W04 P4：`{p4}/index.html`，只将已删除的wonder_thunder_casing/interface换为现存HRV机壳/industrial_port_casing；17,440,898块、941×1056×623及原界面保持，P3历史不改。原三组交叠、14.083%遮挡、巨手缺项及主控占位继续保留。\n- 交付证据：`logs/w05-wind-circuit-a1-20261112/design-delivery.json`；固定审计已同步，37域研发及验收原分数保持。\n'''
    for target in [g.ROOT / 'AGENTS.md', g.ROOT / 'rule/当前多方块设计规则.md']:
        with target.open('a', encoding='utf8') as handle:
            handle.write(note)
    print(json.dumps(dict(candidate='W05 A1', size_xyz=manifest['size'], blocks=manifest['blocks'],
                          audit_score_delta=0, receipt='logs/w05-wind-circuit-a1-20261112/design-delivery.json')))


if __name__ == '__main__':
    main()
