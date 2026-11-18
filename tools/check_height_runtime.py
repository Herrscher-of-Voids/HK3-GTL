"""只读核验高度系统166的实际导出、外部启动身份回执和重启持久化证据。

【变更记录 #1】2026-10-17 21:59:17（修订166）
- 删除：无。
- 新增：旧档、新档及完整模式；45维度、47类型、135探针、客户端同步和重启身份严格核验。
- 修改：缺证据不能通过；不自动选最新文件，不运行游戏、不改实例或存档。
- 用途：供根任务核对真实导出；合成自测不作为游戏、光影、多人或内存验收。

【变更记录 #2】2026-10-17 22:07:02（修订166）
- 删除：无；保留首轮完整覆盖和外部回执绑定。
- 新增：JSON根类型、回执数值类型、未来窗口与旧新重启批次因果时序的严格拒绝。
- 修改：新进程启动前必须完成首次服务端和客户端导出；旧档基线必须先于新档导出。
- 用途：防止坏根节点、布尔伪整数、未来时间或交叉批次报告被误判为完整验收。

【变更记录 #3】2026-10-17 22:10:36（修订166）
- 删除：无。新增：Windows标准输出与错误输出统一UTF-8。
- 修改：帮助文本只显示职责首句；结果显式区分新世界与旧档的核验范围。
- 用途：避免终端默认代码页造成中文乱码，并防止局部模式被读成全阶段通过。

【变更记录 #4】2026-10-17 22:23:14（修订166）
- 删除：无。新增：输出与全部输入、基准清单、启动回执和已部署JAR的路径及硬链接互斥。
- 修改：先检查输出安全再核验；路径冲突时只打印失败，不写入任何摘要文件。
- 用途：防止核验器给出通过后反而覆盖证据；明确包来源与测试档条件须由外部验收取证。

【变更记录 #5】2026-10-17 22:34:50（修订166）
- 删除：无。新增：标准带时区ISO时间的1至9位小数支持及坏格式严格拒绝。
- 修改：兼容Python3.9，仅在比较时把7至9位小数截断为微秒；原报告字节与时间字符串不改写。
- 用途：读取PowerShell七位及Java九位真实时间；不宣称核验器具有纳秒级时序分辨率。
"""

import argparse
import hashlib
import json
import os
import re
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / 'logs/dimension-height-investigation-20261017/dimension-inventory.json'
INVENTORY_SHA = '27c18846286e68b15eb067064a736cd98ec4d28431982704dabca4434d3894d5'
PROBES = ((8, 768, 8, 'minecraft:glass'), (9, 1007, 8, 'minecraft:chest'),
          (10, 1023, 8, 'minecraft:sea_lantern'))
LIMITS = ['不证明远端多人通过', '不证明光影与12视距渲染通过', '不证明Ad Astra Y600降落通道安全',
          '不证明机器加工、性能或整包内存达标', 'PID及实例身份依赖提供的外部回执，不独立操作系统取证',
          '包SHA依赖可信部署回执，不独立证明来自本次构建', '不证明测试档同时满足超平坦、创造模式和允许作弊',
          '时间比较精度为微秒，7至9位小数仅比较时截断，原报告字节保留']
ISO_INSTANT = re.compile(r'(?P<seconds>[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2})'
                         r'(?:\.(?P<fraction>[0-9]{1,9}))?'
                         r'(?P<zone>Z|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])?')


class EvidenceError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise EvidenceError(message)


def integer(value, message):
    require(type(value) is int, message + '必须是整数')
    return value


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, 'JSON对象包含重复键：' + key)
        value[key] = item
    return value


def read_json(path):
    path = Path(path).resolve()
    require(path.is_file(), '证据文件缺失：' + str(path))
    result = json.loads(path.read_text(encoding='utf-8-sig'), object_pairs_hook=unique_object)
    require(isinstance(result, dict), '证据根节点必须是JSON对象：' + str(path))
    return result


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def same_path(left, right):
    left, right = Path(left).resolve(), Path(right).resolve()
    if os.path.normcase(str(left)) == os.path.normcase(str(right)):
        return True
    return left.exists() and right.exists() and os.path.samefile(left, right)


def check_output_destination(args):
    if args.output is None:
        return
    inputs = [args.inventory, args.launch_receipt]
    inputs.extend(getattr(args, role, None) for role in
                  ('server', 'client', 'restart_server', 'restart_client', 'old_server', 'old_client'))
    for path in inputs:
        require(path is None or not same_path(args.output, path), '输出路径不得覆盖输入证据：' + str(path))
    receipt = read_json(args.launch_receipt)
    jar = receipt.get('deployed_jar')
    if isinstance(jar, str) and jar:
        require(not same_path(args.output, jar), '输出路径不得覆盖已部署JAR：' + jar)


def instant(value):
    require(isinstance(value, str), '时间必须包含时区的ISO字符串')
    match = ISO_INSTANT.fullmatch(value)
    require(match is not None, '时间格式损坏：' + value)
    require(match['zone'] is not None, '时间缺少时区：' + value)
    fraction = match['fraction']
    normalized = match['seconds'] + ('.' + fraction[:6].ljust(6, '0') if fraction else '')
    normalized += '+00:00' if match['zone'] == 'Z' else match['zone']
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as failure:
        raise EvidenceError('时间格式损坏：' + value) from failure
    return parsed.astimezone(timezone.utc)


def by_id(rows, field, label):
    require(isinstance(rows, list), label + '必须是数组')
    result = {}
    for row in rows:
        require(isinstance(row, dict) and isinstance(row.get(field), str), label + '缺少ID')
        key = row[field]
        require(key not in result, label + '存在重复ID：' + key)
        result[key] = row
    return result


def baseline(path):
    require(sha(path) == INVENTORY_SHA, '基准清单SHA与本次已确认的只读调查不一致')
    data = read_json(path)
    dimensions = {row['dimension_id']: row['dimension_type_reference'] for row in data['dimensions']
                  if row.get('observed_in_current_runtime_log') is True}
    types = {}
    for row in data['dimension_and_noise_resources']:
        if row['kind'] != 'dimension_type':
            continue
        fields = tuple(row['json'][key] for key in ('min_y', 'height', 'logical_height'))
        require(row['resource_id'] not in types or types[row['resource_id']] == fields,
                '基准维度类型定义冲突：' + row['resource_id'])
        types[row['resource_id']] = fields
    require(len(dimensions) == 45 and len(types) == 47, '基准必须包含45个运行维度和47种维度类型')
    require(all(key in types for key in dimensions.values()), '基准维度绑定存在未知类型')
    return data, dimensions, types


def header(report):
    require(type(report.get('schema')) is int and report['schema'] == 1, '导出schema不支持')
    require(type(report.get('revision')) is int and report['revision'] == 166, '导出不是修订166')
    return instant(report.get('captured_at'))


def server_check(report, dimension_types, types, enabled, top, world):
    captured = header(report)
    require(report.get('world_directory') == world, '服务端导出世界目录不符')
    require(report.get('contract_enabled') is enabled, '世界合同启用状态不符')
    contracts = {}
    if enabled:
        require(type(report.get('contract_version')) is int and report['contract_version'] == 1,
                '世界合同版本错误')
        require(integer(report.get('contract_top_exclusive'), '合同上界') == top, '冻结合同上界不符')
        try:
            identity = str(uuid.UUID(report.get('world_id', '')))
        except (ValueError, TypeError, AttributeError) as failure:
            raise EvidenceError('世界合同UUID损坏') from failure
        require(identity == report['world_id'], '世界UUID必须为规范格式')
        contracts = by_id(report.get('dimension_type_contracts'), 'id', '冻结类型快照')
        require(set(contracts) == set(types), '冻结类型快照必须完整且精确覆盖47种类型')
        for key, (min_y, height, logical) in types.items():
            row = contracts[key]
            expected = {'original_min_y': min_y, 'original_height': height, 'logical_height': logical,
                        'new_height': max(min_y + height, top) - min_y,
                        'new_top_exclusive': max(min_y + height, top)}
            for field, value in expected.items():
                require(integer(row.get(field), key + '/' + field) == value,
                        '冻结快照与已调查原资源或扩展公式不符：' + key + '/' + field)
    else:
        require(not any(key in report for key in ('world_id', 'contract_version', 'contract_top_exclusive',
                                                'dimension_type_contracts')), '无合同旧档不能携带伪装禁用的合同字段')
    rows = by_id(report.get('dimensions'), 'id', '服务器维度')
    require(set(rows) == set(dimension_types), '实际ServerLevel必须精确覆盖45个基准维度')
    for key, type_id in dimension_types.items():
        row = rows[key]
        min_y, original_height, logical = types[type_id]
        height = max(min_y + original_height, top) - min_y if enabled else original_height
        expected = {'min_y': min_y, 'height': height, 'top_exclusive': min_y + height,
                    'logical_height': logical, 'sections': height // 16, 'first_section': min_y // 16,
                    'last_section_exclusive': (min_y + height) // 16}
        require(row.get('type') == type_id, '维度类型绑定漂移：' + key)
        for field, value in expected.items():
            require(integer(row.get(field), key + '/' + field) == value, '实际高度或区段不符：' + key + '/' + field)
        for field in ('below_rejected', 'top_rejected', 'last_allowed', 'last_coordinate_roundtrip',
                      'last_section_byte_roundtrip'):
            require(row.get(field) is True, '实际边界或坐标序列化失败：' + key + '/' + field)
    probes = report.get('probe_verification')
    require(isinstance(probes, dict), '缺少探针状态')
    if not enabled:
        require(probes.get('present') is False, '旧玩家世界不应执行本次高空写入探针')
        return {'captured_at': captured, 'rows': rows, 'contracts': contracts, 'probe_created_at': None}
    require(probes.get('present') is True and probes.get('passed') is True and 'refused' not in probes,
            '探针缺失、拒绝或报告未通过')
    created = instant(probes.get('created_at'))
    require(created <= captured, '探针创建时间晚于核验导出')
    checks = probes.get('checks')
    require(isinstance(checks, list) and len(checks) == 135, '必须具有135个探针检查')
    expected_keys = {(key, *probe) for key in dimension_types for probe in PROBES}
    actual_keys = set()
    for row in checks:
        require(isinstance(row, dict), '探针行格式损坏')
        for field in ('x', 'y', 'z', 'heightmap_top_block_y'):
            integer(row.get(field), '探针/' + field)
        key = (row.get('dimension'), row['x'], row['y'], row['z'], row.get('block'))
        require(key not in actual_keys and key in expected_keys, '重复或意外探针：' + str(key))
        actual_keys.add(key)
        for field in ('block_matches', 'chunk_sections_match_level', 'heightmap_matches_probe'):
            require(row.get(field) is True, '探针实物、区段或高度图失败：' + str(key) + '/' + field)
        require(row['heightmap_top_block_y'] == row['y'], '探针高度图精确Y不符：' + str(key))
        if row['block'] == 'minecraft:chest':
            require(row.get('chest_name_persisted') is True, '高区段方块实体自定义名称丢失：' + str(key))
    require(actual_keys == expected_keys, '探针覆盖不是全部45维度各3种位置')
    return {'captured_at': captured, 'rows': rows, 'contracts': contracts, 'probe_created_at': created}


def client_check(report, server, types, enabled, top):
    captured = header(report)
    synced = by_id(report.get('synced_dimension_types'), 'id', '客户端同步类型')
    require(set(synced) == set(types), '客户端必须同步全部47种类型')
    for key, (min_y, original_height, logical) in types.items():
        expected = {'min_y': min_y, 'logical_height': logical,
                    'height': max(min_y + original_height, top) - min_y if enabled else original_height}
        for field, value in expected.items():
            require(integer(synced[key].get(field), '客户端/' + key + '/' + field) == value,
                    '客户端注册类型与服务器合同不一致：' + key + '/' + field)
    dimension = report.get('dimension')
    require(dimension in server['rows'], '客户端当前维度不在当前ServerLevel列表')
    for field in ('min_y', 'height', 'top_exclusive', 'sections'):
        require(integer(report.get(field), '客户端实际世界/' + field) == server['rows'][dimension][field],
                '客户端实际世界边界与服务器不同：' + field)
    return captured


def receipt_check(receipt, artifacts, reports, instance):
    require(type(receipt.get('schema')) is int and receipt['schema'] == 1
            and type(receipt.get('revision')) is int and receipt['revision'] == 166, '外部启动回执版本错误')
    require(same_path(receipt.get('game_directory', ''), instance), '启动回执实例目录不符')
    jar = Path(receipt.get('deployed_jar', ''))
    require(jar.is_file() and same_path(jar.parent, Path(instance) / 'mods'), '已部署模组路径不属于目标实例mods')
    require(sha(jar) == receipt.get('expected_jar_sha256'), '当前已部署模组SHA与启动回执不同')
    deployed = instant(receipt.get('deployed_at'))
    launches = by_id(receipt.get('launches'), 'label', '启动批次')
    roles = {'old': ('old_server', 'old_client'), 'new': ('server', 'client'),
             'restart': ('restart_server', 'restart_client')}
    selected = {}
    for label, pair in roles.items():
        if pair[0] not in reports:
            continue
        require(label in launches, '缺少启动批次：' + label)
        launch = launches[label]
        pid = integer(launch.get('process_id'), '进程PID')
        require(pid > 0, '进程PID无效')
        require(launch.get('instance_confirmed') is True and isinstance(launch.get('instance_evidence'), str)
                and launch['instance_evidence'].strip(), '缺少外部目标实例身份核对说明')
        started = instant(launch.get('process_created_at'))
        window_start = instant(launch.get('export_started_at'))
        window_end = instant(launch.get('export_ended_at'))
        require(deployed <= started <= window_start <= window_end, '部署、进程或导出窗口时序矛盾')
        require(window_end <= datetime.now(timezone.utc) + timedelta(seconds=30), '导出窗口在未来，不能作为已运行证据')
        bindings = launch.get('reports')
        require(isinstance(bindings, dict), '启动批次缺少报告hash绑定')
        for role, binding_key in zip(pair, ('server', 'client')):
            binding = bindings.get(binding_key)
            require(isinstance(binding, dict), '缺少服务端或客户端报告绑定：' + label)
            require(same_path(binding.get('path', ''), artifacts[role]), '报告路径未绑定本次启动：' + role)
            require(binding.get('sha256') == sha(artifacts[role]), '绑定报告SHA不符：' + role)
            captured = header(reports[role])
            require(window_start <= captured <= window_end, '报告时间不在对应启动导出窗口：' + role)
        selected[label] = (pid, started)
    if 'new' in selected and 'restart' in selected:
        require(selected['new'][0] != selected['restart'][0] and selected['new'][1] < selected['restart'][1],
                '持久化验收必须有真实后续新进程重启，不能复用同一PID冒充')
        require(max(header(reports['server']), header(reports['client'])) < selected['restart'][1],
                '重启进程早于首次服务端或客户端导出')
        require(instant(reports['server']['probe_verification']['created_at']) >= selected['new'][1],
                '首次探针不是在新进程启动后创建')
    if 'old' in selected and 'new' in selected:
        require(max(header(reports['old_server']), header(reports['old_client']))
                < min(header(reports['server']), header(reports['client'])),
                '旧档基线导出必须先于新世界导出')
    return {'deployed_jar': str(jar.resolve()), 'jar_sha256': sha(jar), 'launch_labels': sorted(selected)}


def verify(args):
    inventory, dimension_types, types = baseline(args.inventory)
    require(528 <= args.top_exclusive <= 2032 and args.top_exclusive % 16 == 0, '目标上界非法')
    roles = ('old_server', 'old_client') if args.mode == 'old' else ('server', 'client', 'restart_server', 'restart_client')
    if args.mode == 'full':
        roles += ('old_server', 'old_client')
    missing = [role for role in roles if getattr(args, role, None) is None]
    require(not missing, '缺少明确指定的报告：' + ','.join(missing))
    artifacts = {role: Path(getattr(args, role)).resolve() for role in roles}
    require(len(set(artifacts.values())) == len(artifacts), '不同阶段不得重复使用同一报告文件')
    reports = {role: read_json(path) for role, path in artifacts.items()}
    old_world = args.old_world or Path(inventory['active_save_metadata_source']['path']).parent.name
    checked = {}
    for prefix, enabled, world in (('old_', False, old_world), ('', True, args.expected_world),
                                    ('restart_', True, args.expected_world)):
        role = prefix + 'server'
        if role not in reports:
            continue
        checked[role] = server_check(reports[role], dimension_types, types, enabled, args.top_exclusive, world)
        client_check(reports[prefix + 'client'], checked[role], types, enabled, args.top_exclusive)
    if 'restart_server' in reports:
        before, after = reports['server'], reports['restart_server']
        require(before['world_id'] == after['world_id'], '重启后世界合同UUID改变')
        require(checked['server']['contracts'] == checked['restart_server']['contracts'], '重启后冻结类型合同改变')
        require(checked['server']['rows'] == checked['restart_server']['rows'], '重启后实际维度边界改变')
        require(checked['server']['probe_created_at'] == checked['restart_server']['probe_created_at'],
                '重启后不是同一份既有探针清单')
    identity = receipt_check(read_json(args.launch_receipt), artifacts, reports,
                             inventory['instance']['minecraft_directory'] if isinstance(inventory['instance'], dict)
                             else inventory['instance'])
    return {'schema': 1, 'revision': 166, 'validator_revision': 1, 'status': 'PASS', 'mode': args.mode,
            'captured_at': datetime.now(timezone.utc).isoformat(), 'runtime_height_contract_verified': True,
            'baseline_inventory_sha256': sha(args.inventory), 'identity': identity,
            'reports': {role: {'path': str(path), 'sha256': sha(path)} for role, path in artifacts.items()},
            'checks': {'dimensions_per_server': 45, 'synced_types_per_client': 47,
                       'probes_per_new_server': 135 if args.mode != 'old' else 0,
                       'restart_verified': args.mode != 'old', 'new_world_verified': args.mode != 'old',
                       'old_world_unchanged_verified': args.mode != 'new'},
            'multiplayer_verified': False, 'shader_verified': False, 'memory_verified': False, 'limits': LIMITS}


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--mode', choices=('old', 'new', 'full'), default='full')
    parser.add_argument('--inventory', type=Path, default=INVENTORY)
    for role in ('server', 'client', 'restart_server', 'restart_client', 'old_server', 'old_client'):
        parser.add_argument('--' + role.replace('_', '-'), type=Path)
    parser.add_argument('--launch-receipt', type=Path, required=True)
    parser.add_argument('--top-exclusive', type=int, default=1024)
    parser.add_argument('--expected-world', default='hk3gtl-height-r166-review')
    parser.add_argument('--old-world')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    output_safe = False
    try:
        check_output_destination(args)
        output_safe = True
        result, code = verify(args), 0
    except (EvidenceError, OSError, ValueError, KeyError, TypeError) as failure:
        result = {'schema': 1, 'revision': 166, 'validator_revision': 1, 'status': 'FAIL',
                  'runtime_height_contract_verified': False, 'error': str(failure), 'limits': LIMITS}
        code = 1
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output and output_safe:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + '\n', encoding='utf-8')
    print(rendered)
    return code


if __name__ == '__main__':
    sys.exit(main())
