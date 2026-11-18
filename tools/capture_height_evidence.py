# -*- coding: utf-8 -*-
"""只读采集明确指定的高度报告与启动依据，按旧档、新档和重启独立封存。

【变更记录 #1】2026-10-17 22:29:29（修订166）
- 删除：无。
- 新增：显式批次、报告、进程、部署和观察路径，原字节复制与SHA绑定、过滤后的存档条件证据。
- 修改：不自动寻找最新导出；批次已存在时只接受完全相同的原字节，拒绝覆盖证据。
- 用途：供check_height_runtime.py复核启动因果；不改实例、存档、游戏进程或业务资源，不输出种子和玩家数据。

【变更记录 #2】2026-10-17 22:32:19（修订166）
- 删除：无，原始报告字节仍完整保存。
- 新增：兼容实际PowerShell七位与Java九位小数的带时区ISO时间读取。
- 修改：仅比较时裁至Python微秒精度，回执与来源仍保存原始时间字符串，不改写源报告。
- 用途：让本机Python3.9处理真实导出格式，不把合法纳秒字符串误判为缺失证据。

【变更记录 #3】2026-10-17 22:34:10（修订166）
- 删除：服务端world_directory是绝对路径的错误假设。
- 新增：按实际审计输出的存档文件夹名严格核对，同时保留报告位于指定实例目录的检查。
- 修改：不修改游戏报告或放宽到任意存档名；用途：匹配本次已构建审计API的真实字段定义。

【变更记录 #4】2026-10-17 22:37:49（修订166）
- 删除：无；保留已封存旧档条件原字节，不回写历史证据。
- 新增：新档冻结合同的版本、上界与快照数量过滤摘要，启用合同缺少快照时拒绝采集。
- 修改：所有1至9位ISO小数统一填充或截至六位微秒；用途：完整兼容本机解析并证明首存合同已封存。

【变更记录 #5】2026-10-17 22:47:33（修订166）
- 删除：无，已封存旧档报告和回执保持原字节。
- 新增：新档与重启批次必须显式指定探针清单，核对135位置和报告创建时间后原字节封存。
- 修改：不执行探针、不自动寻找新报告，重启继续读取同一清单；用途：为实际持久化验收提供源清单身份。
"""

import argparse
import gzip
import hashlib
import io
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import nbtlib

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'logs/dimension-height-r166/runtime'
HK = timezone(timedelta(hours=8))
RULES = ('rules.md', '系统角色设定.md', '崩坏三-gtl (hk3gtl) 项目规则.md',
         'hk3gtl java文件变更备注规范.md', '当前多方块设计规则.md', '巨构提示词.txt')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load_json(raw):
    value = json.loads(raw.decode('utf-8-sig'))
    require(isinstance(value, dict), 'JSON根必须是对象')
    return value


def stable_read(path):
    path = Path(path).resolve(strict=True)
    require(path.is_file(), '输入不是文件：' + str(path))
    before = path.stat()
    raw = path.read_bytes()
    after = path.stat()
    require((before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns),
            '采集时输入仍在变化，请待该导出完成后重试：' + str(path))
    return path, raw, after


def instant(value):
    require(isinstance(value, str) and re.fullmatch(
        r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,9})?(?:Z|[+-]\d{2}:\d{2})', value),
        '时间必须是带时区的ISO格式，允许最多九位小数')
    normalized = re.sub(r'\.(\d{1,9})(?=Z|[+-]\d{2}:\d{2}$)',
                        lambda match: '.' + match.group(1)[:6].ljust(6, '0'), value)
    result = datetime.fromisoformat(normalized.replace('Z', '+00:00'))
    require(result.tzinfo is not None, '时间必须有时区')
    return result


def same_path(left, right):
    return Path(left).resolve() == Path(right).resolve()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def save_once(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        require(path.read_bytes() == raw, '证据已存在且内容不同，拒绝覆盖：' + str(path))
    else:
        with path.open('xb') as stream:
            stream.write(raw)
    require(path.read_bytes() == raw, '封存字节复核失败：' + str(path))


def world_conditions(world, expected_enabled, checked_at):
    path, raw, stat = stable_read(world / 'level.dat')
    require(raw[:2] == b'\x1f\x8b', 'level.dat不是预期gzip格式')
    data = nbtlib.File.parse(io.BytesIO(gzip.decompress(raw)))['Data']
    game_type = int(data['GameType'])
    commands = int(data['allowCommands'])
    generator = str(data['WorldGenSettings']['dimensions']['minecraft:overworld']['generator']['type'])
    present = 'hk3gtl:height_contract' in data
    enabled = bool(int(data['hk3gtl:height_contract']['enabled'])) if present else False
    require(game_type == 1 and commands == 1 and generator == 'minecraft:flat',
            '指定测试存档必须同时满足创造、允许作弊、超平坦')
    require(present == expected_enabled and enabled == expected_enabled,
            '旧档应无合同；新档与重启应有已启用合同')
    contract = data['hk3gtl:height_contract'] if present else None
    version = int(contract['contractVersion']) if present else None
    top = int(contract['topExclusive']) if present else None
    snapshot_count = len(contract['dimensions']) if present else 0
    require(not present or version == 1 and top == 1024 and snapshot_count > 0,
            '本轮新档合同必须版本1、上界1024并已有非空冻结快照')
    return {'schema': 1, 'revision': 166, 'checked_at': checked_at,
            'world_directory': str(world), 'source_path': str(path), 'source_sha256': digest(raw),
            'source_bytes': len(raw), 'source_last_write_at': datetime.fromtimestamp(stat.st_mtime, HK).isoformat(),
            'game_type': game_type, 'allow_commands': commands, 'generator_type': generator,
            'height_contract_present': present, 'height_contract_enabled': enabled,
            'contract_version': version, 'top_exclusive': top, 'dimension_snapshot_count': snapshot_count,
            'passed': True, 'privacy_boundary': '仅读取并输出列明条件；未封存level.dat原文、种子或玩家数据'}


def capture(args):
    now = datetime.now(HK)
    recorded = now.isoformat(timespec='microseconds')
    deployment_path, deployment_raw, _ = stable_read(args.deployment)
    observation_path, observation_raw, _ = stable_read(args.launch_observation)
    deployment = load_json(deployment_raw)
    observation = load_json(observation_raw)
    require(deployment.get('revision') == 166 and observation.get('revision') == 166, '部署与观察必须属于修订166')
    require(observation.get('deployment_receipt_sha256') == digest(deployment_raw)
            and same_path(observation['deployment_receipt_path'], deployment_path), '观察没有绑定所给部署回执')
    game = Path(observation['game_directory']).resolve(strict=True)
    require(same_path(game, Path(deployment['instance']) / 'minecraft'), '部署与观察的实例目录不同')
    jar, jar_raw, _ = stable_read(deployment['target'])
    require(jar.parent == game / 'mods' and same_path(jar, observation['deployed_jar']), '模组不在所给实例mods内')
    expected_sha = deployment['sha256']
    require(digest(jar_raw) == expected_sha == observation.get('expected_jar_sha256')
            == observation.get('actual_jar_sha256') and observation.get('deployed_sha_matches') is True,
            '当前JAR与部署或观察身份不同')
    selected = [item for item in observation.get('processes', []) if type(item.get('process_id')) is int
                and item['process_id'] == args.process_id]
    require(len(selected) == 1, '必须在显式观察中找到唯一指定PID')
    process = selected[0]
    require(process.get('parent_process_name', '').lower() == 'prismlauncher.exe'
            and process.get('is_prism_entrypoint') is True, '所给进程不是观察确认的Prism入口')
    require(args.instance_evidence.strip(), '必须明确提供外部界面身份核对依据，不能只凭唯一Java进程')
    created = instant(process['created_at'])
    deployed = datetime.strptime(deployment['time'], '%Y%m%d_%H%M%S').replace(tzinfo=HK)
    require(deployed <= created <= now, '部署与进程创建时序错误')
    world = Path(args.world).resolve(strict=True)
    require(world.parent == game / 'saves', '只允许核读该实例saves直接子目录')
    expected_name = 'hk3gtl-industrial-r160-review' if args.label == 'old' else 'hk3gtl-height-r166-review'
    require(world.name == expected_name, '指定存档不是本批次约定的测试世界')
    reports = {}
    originals = {}
    report_values = {}
    captured = []
    label_directory = BASE / args.label
    for role in ('server', 'client'):
        path, raw, _ = stable_read(getattr(args, role))
        require(path.parent == game / 'logs/hk3gtl-height-audit', '报告不属于目标实例高度导出目录')
        value = load_json(raw)
        require(value.get('schema') == 1 and value.get('revision') == 166, '报告修订或格式不符')
        stamp = instant(value['captured_at'])
        require(created <= stamp <= now, '报告不属于所给进程之后的真实已完成时间')
        if role == 'server':
            require(value['world_directory'] == world.name, '服务端报告不属于所给测试世界')
            require(value['contract_enabled'] is (args.label != 'old'), '报告合同状态与批次不符')
        target = label_directory / path.name
        reports[role] = {'path': str(target.resolve()), 'sha256': digest(raw)}
        originals[role] = {'path': str(path), 'sha256': digest(raw), 'bytes': len(raw),
                           'captured_at': value['captured_at']}
        report_values[role] = value
        captured.append(stamp)
        save_once(target, raw)
    probe_binding = None
    if args.label == 'old':
        require(args.probe_manifest is None, '旧档批次不应指定或读取新档探针清单')
    else:
        require(args.probe_manifest is not None, '新档与重启必须显式指定原探针清单')
        probe_path, probe_raw, _ = stable_read(args.probe_manifest)
        require(probe_path == world / 'hk3gtl-height-probes.json', '探针清单不属于指定新测试世界')
        probes = load_json(probe_raw)
        require(probes.get('schema') == 1 and probes.get('revision') == 166
                and len(probes.get('positions', [])) == 135, '探针清单不是本修订135位置')
        require(probes.get('created_at') == report_values['server']['probe_verification'].get('created_at'),
                '原探针清单与服务端报告的创建身份不一致')
        probe_target = label_directory / probe_path.name
        save_once(probe_target, probe_raw)
        probe_binding = {'path': str(probe_target.resolve()), 'sha256': digest(probe_raw),
                         'source_path': str(probe_path), 'bytes': len(probe_raw),
                         'created_at': probes['created_at'], 'positions': 135}
    conditions = world_conditions(world, args.label != 'old', recorded)
    conditions_path = label_directory / 'world-conditions.json'
    require(not conditions_path.exists(), '此批次条件证据已存在；拒绝以较晚状态覆盖，请复用原批次')
    save_once(label_directory / deployment_path.name, deployment_raw)
    save_once(label_directory / observation_path.name, observation_raw)
    launch = {'label': args.label, 'process_id': args.process_id,
              'process_created_at': process['created_at'], 'instance_confirmed': True,
              'instance_evidence': args.instance_evidence.strip(),
              'export_started_at': min(captured).isoformat(), 'export_ended_at': max(captured).isoformat(),
              'export_window_basis': '两份已完成原报告的captured_at最小值至最大值；不伪造界面操作起止时间',
              'reports': reports, 'source_reports': originals,
              'launch_observation': {'path': str((label_directory / observation_path.name).resolve()),
                                     'sha256': digest(observation_raw)},
              'deployment_receipt': {'path': str((label_directory / deployment_path.name).resolve()),
                                     'sha256': digest(deployment_raw)},
              'world_conditions': {'path': str(conditions_path.resolve()),
                                   'sha256': digest(json_bytes(conditions))}, 'collected_at': recorded}
    if probe_binding is not None:
        launch['probe_manifest'] = probe_binding
    receipt_path = BASE / 'launch-receipt.json'
    if receipt_path.exists():
        prior_raw = receipt_path.read_bytes()
        receipt = load_json(prior_raw)
        require(receipt.get('revision') == 166 and same_path(receipt['game_directory'], game)
                and receipt['expected_jar_sha256'] == expected_sha, '现有回执属于不同部署，拒绝混用')
        require(all(item['label'] != args.label for item in receipt['launches']), '批次已登记，拒绝重复或替换')
        save_once(BASE / 'receipt-history' / (now.strftime('%Y%m%d-%H%M%S-%f') + '.json'), prior_raw)
    else:
        receipt = {'schema': 1, 'revision': 166, 'game_directory': str(game), 'deployed_jar': str(jar),
                   'expected_jar_sha256': expected_sha, 'deployed_at': deployed.isoformat(), 'launches': []}
    save_once(conditions_path, json_bytes(conditions))
    save_once(label_directory / 'capture-record.json', json_bytes(launch))
    receipt['launches'].append(launch)
    receipt['updated_at'] = recorded
    receipt['rules_read_identity'] = [{'path': str(ROOT / 'rule' / name),
                                      'sha256': digest((ROOT / 'rule' / name).read_bytes())} for name in RULES]
    receipt['change_record'] = {'number': len(receipt['launches']), 'recorded_at': recorded,
                               'delete': '无，保留旧回执快照和全部原始报告',
                               'add': args.label + '批次原字节、启动身份和过滤后存档条件',
                               'modify': '只增量追加明确批次，不重选最新报告',
                               'purpose': '绑定真实运行证据；不作为所有功能已通过的声明'}
    temporary = BASE / ('launch-receipt-' + now.strftime('%Y%m%d-%H%M%S-%f') + '.tmp')
    save_once(temporary, json_bytes(receipt))
    os.replace(temporary, receipt_path)
    print(json.dumps({'label': args.label, 'receipt': str(receipt_path),
                      'receipt_sha256': digest(receipt_path.read_bytes()), 'reports': reports,
                      'world_conditions_passed': conditions['passed']}, ensure_ascii=False))


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--label', choices=('old', 'new', 'restart'), required=True)
    parser.add_argument('--server', type=Path, required=True)
    parser.add_argument('--client', type=Path, required=True)
    parser.add_argument('--launch-observation', type=Path, required=True)
    parser.add_argument('--deployment', type=Path, required=True)
    parser.add_argument('--process-id', type=int, required=True)
    parser.add_argument('--instance-evidence', required=True)
    parser.add_argument('--world', type=Path, required=True)
    parser.add_argument('--probe-manifest', type=Path)
    try:
        capture(parser.parse_args())
    except (ValueError, OSError, KeyError, TypeError) as error:
        print('采集拒绝：' + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
