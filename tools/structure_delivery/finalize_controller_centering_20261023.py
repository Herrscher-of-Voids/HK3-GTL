# -*- coding: utf-8 -*-
"""核验实际部署收据后更新当前索引、审计追加状态与本轮讨论记录。

【变更记录 #1】2026-10-23 13:49:32（内测5修订175）
- 删除：当前索引中本轮仍待接入的失效状态，原字节及旧归档保留。
- 新增：正式来源、实例文件身份、batch-06完成记录和未实机验收边界。
- 修改：只在构建、包与实例SHA一致后更新部署状态；其他系统分值不变。
- 用途：区分用户批准、代码接入、文件部署与游戏验收，防止接续误读。
"""
from __future__ import annotations

import datetime as dt
import hashlib
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / 'logs/controller-centering-install-20261023'
INDEX = ROOT / 'deliveries/多方块确认归档/当前归档索引.json'
DATA = ROOT / 'src/main/resources/data/hk3gtl'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    final_path = LOG / 'install-final-check.json'
    if final_path.exists():
        raise ValueError('已有最终登记，禁止重复推进批次。')
    package = read(LOG / 'package-verification.json')
    deployment = read(LOG / 'deployment.json')
    approval = read(LOG / 'approval-archive.json')
    assert package['status'] == 'passed' and package['revision'] == deployment['revision'] == 175
    assert package['sha256'] == deployment['sha256'] == sha(Path(deployment['target']))
    assert deployment['third_party_jars_unchanged']
    assert deployment['formal_structure_forms'] == 26 and deployment['schematic_forms'] == 21
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    raw = INDEX.read_bytes()
    (LOG / 'current-index-before-finalization.json').open('xb').write(raw)
    index = json.loads(raw.decode('utf-8-sig'))
    assert index['pending_batch']['id'] == 'batch-06' and index['pending_batch']['count'] == 5
    formal_keys = sorted(package['resources'])
    assert len(formal_keys) == 78
    keys = {r['key'] for r in package['structures']} | {f's{i:02}' for i in range(1, 6)}
    for entry in index['entries']:
        if entry['key'] not in {r['key'] for r in package['structures']}:
            continue
        meta_path = DATA / f'structures/approved/{entry["key"]}.json'
        meta = read(meta_path)
        entry.update(status='approved_formal_deployed_game_unverified', formal_resource_present=True,
                     formal_metadata=str(meta_path), formal_metadata_sha256=sha(meta_path),
                     game_files_installed=True, game_verified=False, deployment_revision=175,
                     deployment_jar_sha256=deployment['sha256'], deployed_at=deployment['recorded_at'],
                     deployment_receipt=str(LOG / 'deployment.json'), required_abilities=meta['required_abilities'])
        if 'target_voltage' in meta:
            entry['target_voltage'] = meta['target_voltage']
        if entry['key'] in {'i14', 'i15', 'i16', 'i18'}:
            entry['recipe_execution_scope'] = '现有暂定工艺保持执行关闭，控制器生存获取尚未开放。'
        else:
            entry['recipe_execution_scope'] = '保留既有已接配方和运行校验；本轮未进行游戏内验收。'
    completed = dict(index['pending_batch'], status='structure_files_deployed_game_unverified',
                     completed_at=deployment['recorded_at'], revision=175, deployment_receipt=str(LOG / 'deployment.json'),
                     zip_sha256=approval['zip_sha256'], target_instance=deployment['target_instance']['game'])
    index.setdefault('completed_batches', []).append(completed)
    index.update(updated_at=now.isoformat(), formal_keys=sorted(keys), formal_structure_forms=26,
                 approved_structure_forms=26, snapshot=approval['snapshot'], zip=approval['zip'], zip_sha256=approval['zip_sha256'],
                 target_instance=deployment['target_instance']['game'], target_pack_version='2.9',
                 scope='I01四阶与I02–I18共21个V2形态已归档、正式接入并停机部署修订175；S01–S05保留，游戏成型和生存闭环未验收。',
                 batch_rule='每累计5台明确批准后接入；batch-06结构文件已部署，I01–I13修订不重复计入新机器批次。',
                 pending_batch={'id': 'batch-07', 'approved_machine_ids': [], 'count': 0, 'required': 5,
                                'deployment_eligible': False, 'deployment_blockers': ['尚无新的五台明确批准。']},
                 latest_deployment={'revision': 175, 'sha256': deployment['sha256'], 'receipt': str(LOG / 'deployment.json'),
                                    'game_verified': False})
    index.setdefault('_change_records', []).append({'record': len(index.get('_change_records', [])) + 1,
        'time': now.isoformat(), 'reason': '完整构建及实际停机部署收据已通过',
        'deleted': '当前待接入状态；旧索引原字节和历史归档保留',
        'added': '21形态正式资源和实例身份，batch-06完成与batch-07空批次',
        'modified': '正式总数由21推进至26，不重算既有机器修订为新机器',
        'purpose': '准确登记结构文件实装；不把未开放工艺或未实机验收记为闭环'})
    assert INDEX.read_bytes() == raw
    write(INDEX, index)
    discussion = ROOT / 'doc/HK3GTL-内测5/讨论记录' / (now.strftime('%Y-%m-%d_%H-%M-%S_') + 'I01-I18居中融合V2正式实装修订175.html')
    content = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>I01–I18居中融合V2实装</title>
<style>body{{max-width:1050px;margin:30px auto;font:16px/1.8 "Microsoft YaHei",sans-serif;color:#243b49}}section{{padding:18px;border:1px solid #bdd1d2;margin:15px 0}}code{{overflow-wrap:anywhere}}</style>
<h1>I01–I18居中融合V2正式实装 · 修订175</h1><p>实际记录时间：{now.isoformat()}，Asia/Hong_Kong。用户原消息精确时间未知。</p>
<section><h2>用户已确认</h2><p>负责人在当前V2评审上下文明确说“实装这一些吧”，批准I01四阶及I02–I18共21形态归档、正式接入、构建与唯一实例部署。此前“继续下一步”实际是要求主控沿宽度居中，并非批准；本次明确实装决定覆盖此前仍待审的当前状态。</p><p>主控沿整机宽度中轴，宽35对应从1计数第18格；控制器及接口继续自然融合。没有重新改色、缩小建筑或恢复独立面板。</p></section>
<section><h2>已实施与已验证</h2><p>21份V2原件按原字节归档并核对ZIP全部文件；正式布局、放置NBT与元数据采用对应批准几何。I01四阶逐格累积继承通过，S01–S05正式资源保持原字节。I14/I15/I16/I18新增正式控制器与Pattern，I17保留原ID和浓缩工艺，六口按四项真实能力布置，流体进出使用4槽仓。控制器与新设备可经注册表、创造页剩余物品收集和GT JEI全机器枚举找到；此为静态接线核查。</p><p>clean build成功，83项任务全部执行；构建前后4144份输入身份保持。83任务包含26形态模板/能力/四向与继承检查、新扩展暂定工单守卫检查。最终JAR的78份正式资源与源码匹配，21批准形态普通方块与原件逐格一致。</p><p>已停机备份并部署唯一增强版2.9实例（MC1.20.1 / Forge47.4.16）：<code>{html.escape(deployment['target_instance']['game'])}</code>。实例JAR SHA256：<code>{deployment['sha256']}</code>；旧包备份：<code>{html.escape(deployment['backup'])}</code>。21份批准Sponge已复制至实例独立目录，第三方JAR身份保持。</p></section>
<section><h2>未开放与未验收</h2><p>I14/I15/I16/I18当前32项暂定工艺仍不可执行，原计划注册和数值未改；四个新控制器未新增生存制作配方。结构批准不代替工艺定阶、研究和首建获取闭环，I14/I15映射、I16最迟HDV首建及I17最低档建造依赖仍需后续核验。本次没有启动游戏或加载世界，不宣称实机成型、流体IO、配方运行或生存可达通过。整包内存优化继续后置。</p><p>batch-06的I14–I18五台结构文件已部署，开始空的batch-07；既有I01–I13修订不重复计数。后续以指定实例进行实机验收，普通建材与控制器获取缺口在工艺定稿时处理，不用创造获取冒充生存链。</p></section>
<p><a href="2026-10-23_11-48-08_I01-I18主控制器宽度轴置中V2.html">上轮V2决定</a> · <a href="../../../logs/controller-centering-install-20261023/approval-archive.json">批准归档收据</a> · <a href="../../../logs/controller-centering-install-20261023/build-verification.json">构建收据</a> · <a href="../../../logs/controller-centering-install-20261023/package-verification.json">包身份核验</a> · <a href="../../../logs/controller-centering-install-20261023/deployment.json">实际部署</a></p>
<p>【变更记录 #1】{now.isoformat()}：删除当前未接入状态但保留旧记录；新增明确批准、正式接入及停机部署证据；修改正式总数为26；用途为保留实装事实与未验收边界。</p></html>'''
    with discussion.open('x', encoding='utf-8') as output:
        output.write(content + '\n')
    section = f'''<section id="controller-centering-r175" style="padding:20px;margin:20px;border:2px solid #537f8b"><h2>修订175 · I01–I18居中融合V2已实装</h2><p>{now.isoformat()}（香港时间）：负责人明确要求实装后，21形态已不可变归档、正式接入并停机部署增强版2.9。主控居中及普通几何、I01继承、S01–S05原件保持与最终78份结构资源核对通过；clean build为83/83任务。</p><p>I14/I15/I16/I18四台控制器已注册，32项暂定工单保持执行关闭，生存制作未开放；I17保留原ID与既有工艺，并采用多槽流体仓。没有启动游戏，成型、IO、配方与生存首建均未实机验收。其他系统原分母、评分和历史正文不改。</p><p><a href="../../../logs/controller-centering-install-20261023/install-final-check.json">本轮完整实装核验</a> · <a href="../../../logs/controller-centering-install-20261023/deployment.json">实例部署收据</a></p><small>变更记录#175：删除当前待接入结论；新增本轮结构和部署事实；历史原字节先保存后追加，未重新评分。</small></section>'''
    for relative in ['doc/崩坏三-GTL/00_项目总览/模组全面系统性分析报告.html',
                     'doc/HK3GTL-内测5/09_测试发布/内测5全库逐份代码文档对照审计_20261017.html']:
        path = ROOT / relative
        original = path.read_bytes()
        (LOG / ('before-r175-' + path.name)).open('xb').write(original)
        assert b'id="controller-centering-r175"' not in original
        match = re.search(br'<body\b[^>]*>', original, re.I)
        assert match is not None
        path.write_bytes(original[:match.end()] + section.encode('utf-8') + original[match.end():])
    result = {'status': 'passed', 'revision': 175, 'recorded_at': now.isoformat(), 'approved_forms': 21,
              'formal_forms': 26, 'formal_resource_files': 78, 'gradle_tasks': 83,
              'jar_sha256': deployment['sha256'], 'archive_zip_sha256': approval['zip_sha256'],
              'instance': deployment['target_instance']['game'], 'backup': deployment['backup'],
              'discussion': str(discussion), 'current_index_sha256': sha(INDEX),
              'batch06_structure_files_deployed': True, 'game_verified': False,
              'provisional_recipes_closed': 32, 'new_controller_survival_recipes': 0}
    write(final_path, result)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
