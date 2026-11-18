"""核验器的合成负例自测；不读取真实游戏报告、不操作游戏或实例，不产生游戏通过证据。

【变更记录 #1】2026-10-17 22:03:35（修订166）
- 删除：无。新增：完整合成输入及缺失/重复/漂移/错误身份时序的拒绝回归。
- 修改：只在logs内的已核对临时目录写夹具，结束清理自建目录。
- 用途：直接执行生产核验器，确认不能靠汇总passed或重复探针冒充完整验收。

【变更记录 #2】2026-10-17 22:07:02（修订166）
- 删除：无；保留全部真实核验入口的合成负例。
- 新增：目标实例身份、包hash、报告hash、进程创建时序、未来窗口及布尔伪版本的负例。
- 修改：负例均校验具体拒绝原因，不把任意异常当作成功拒绝。
- 用途：验证证据归属和因果链；所有夹具仍明确属于合成自测。

【变更记录 #3】2026-10-17 22:23:14（修订166）
- 删除：无。新增：命令行输出覆盖报告、启动回执、基准清单及JAR的拒绝与原hash保持检查。
- 修改：直接调用真实main入口，验证错误摘要也不会破坏作为输入的原文件。
- 用途：复现并封住独立审查指出的自毁证据路径；仍仅为合成自测。

【变更记录 #4】2026-10-17 22:34:50（修订166）
- 删除：无。新增：PowerShell七位、Java九位及1至9位小数时间正例与坏格式负例。
- 修改：比较期望UTC微秒值，并明确验证截断不进位及输入字符串原样保留。
- 用途：使Python3.9读取真实报告时间，同时拒绝缺时区、过长小数或宽松非标准格式。
"""

import copy
import contextlib
import io
import json
import os
import tempfile
import unittest
import uuid
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

import check_height_runtime as checker

OUT = checker.ROOT / 'logs/dimension-height-r166/validator-selftest'


class RuntimeCheckerTest(unittest.TestCase):
    checks = 0

    def setUp(self):
        OUT.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix='synthetic-', dir=OUT)
        self.directory = Path(self.temporary.name).resolve()
        self.assertEqual(self.directory.parent, OUT.resolve())
        inventory, self.dimensions, self.types = checker.baseline(checker.INVENTORY)
        self.inventory = copy.deepcopy(inventory)
        self.inventory['instance'] = str(self.directory / 'instance')
        jar = Path(self.inventory['instance']) / 'mods/hk3gtl-fixture.jar'
        jar.parent.mkdir(parents=True)
        jar.write_bytes(b'not a game package; validator synthetic fixture only')
        self.reports = {}
        self.paths = {}
        self.receipt = {'schema': 1, 'revision': 166, 'game_directory': self.inventory['instance'],
                        'deployed_jar': str(jar), 'expected_jar_sha256': checker.sha(jar),
                        'deployed_at': '2026-10-17T00:00:00Z', 'launches': []}
        for label, captured, enabled, pid, process, start, end in (
            ('old', '2026-10-17T01:05:00Z', False, 100, '2026-10-17T00:30:00Z', '2026-10-17T01:00:00Z', '2026-10-17T01:10:00Z'),
            ('new', '2026-10-17T02:05:00Z', True, 100, '2026-10-17T00:30:00Z', '2026-10-17T02:00:00Z', '2026-10-17T02:10:00Z'),
            ('restart', '2026-10-17T03:05:00Z', True, 200, '2026-10-17T02:30:00Z', '2026-10-17T03:00:00Z', '2026-10-17T03:10:00Z')):
            prefix = '' if label == 'new' else label + '_'
            server, client = self.make_reports(enabled, captured)
            self.reports[prefix + 'server'] = server
            self.reports[prefix + 'client'] = client
            self.receipt['launches'].append({'label': label, 'process_id': pid, 'process_created_at': process,
                'instance_confirmed': True, 'instance_evidence': '合成测试输入，不是实际实例身份',
                'export_started_at': start, 'export_ended_at': end, 'reports': {}})
        self.args = Namespace(mode='full', inventory=checker.INVENTORY, top_exclusive=1024,
                              expected_world='hk3gtl-height-r166-review', old_world=None,
                              launch_receipt=self.directory / 'receipt.json')
        self.persist()

    def tearDown(self):
        self.assertEqual(self.directory.parent, OUT.resolve())
        self.temporary.cleanup()

    def make_reports(self, enabled, captured):
        rows, contracts, checks = [], [], []
        for key, (min_y, height, logical) in self.types.items():
            new_height = max(min_y + height, 1024) - min_y
            contracts.append({'id': key, 'original_min_y': min_y, 'original_height': height,
                              'logical_height': logical, 'new_height': new_height,
                              'new_top_exclusive': min_y + new_height})
        for key, type_id in self.dimensions.items():
            min_y, height, logical = self.types[type_id]
            if enabled:
                height = max(min_y + height, 1024) - min_y
            rows.append({'id': key, 'type': type_id, 'min_y': min_y, 'height': height,
                'top_exclusive': min_y + height, 'logical_height': logical, 'sections': height // 16,
                'first_section': min_y // 16, 'last_section_exclusive': (min_y + height) // 16,
                'below_rejected': True, 'top_rejected': True, 'last_allowed': True,
                'last_coordinate_roundtrip': True, 'last_section_byte_roundtrip': True})
            for x, y, z, block in checker.PROBES:
                row = {'dimension': key, 'x': x, 'y': y, 'z': z, 'block': block, 'block_matches': True,
                       'chunk_sections_match_level': True, 'heightmap_top_block_y': y, 'heightmap_matches_probe': True}
                if block == 'minecraft:chest':
                    row['chest_name_persisted'] = True
                checks.append(row)
        server = {'schema': 1, 'revision': 166, 'captured_at': captured, 'contract_enabled': enabled,
                  'world_directory': 'hk3gtl-height-r166-review' if enabled else
                  Path(self.inventory['active_save_metadata_source']['path']).parent.name,
                  'dimensions': rows, 'probe_verification': {'present': False}}
        if enabled:
            server.update({'world_id': '42d5217c-e034-4ced-819f-7dd293ea9c23', 'contract_version': 1,
                           'contract_top_exclusive': 1024, 'dimension_type_contracts': contracts,
                           'probe_verification': {'present': True, 'passed': True,
                            'created_at': '2026-10-17T02:01:00Z', 'checks': checks}})
        client = {'schema': 1, 'revision': 166, 'captured_at': captured, 'dimension': rows[0]['id'],
                  'synced_dimension_types': [{'id': key, 'min_y': minimum, 'height':
                    max(minimum + height, 1024) - minimum if enabled else height, 'logical_height': logical}
                    for key, (minimum, height, logical) in self.types.items()]}
        client.update({key: rows[0][key] for key in ('min_y', 'height', 'top_exclusive', 'sections')})
        return server, client

    def persist(self):
        for role, value in self.reports.items():
            path = self.directory / (role + '.json')
            path.write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')
            setattr(self.args, role, path)
            self.paths[role] = path
        for launch in self.receipt['launches']:
            prefix = '' if launch['label'] == 'new' else launch['label'] + '_'
            launch['reports'] = {kind: {'path': str(self.paths[prefix + kind]),
                                      'sha256': checker.sha(self.paths[prefix + kind])}
                                 for kind in ('server', 'client')}
        self.args.launch_receipt.write_text(json.dumps(self.receipt, ensure_ascii=False), encoding='utf-8')

    def verify(self):
        with patch.object(checker, 'baseline', return_value=(self.inventory, self.dimensions, self.types)):
            return checker.verify(self.args)

    def test_complete_synthetic_fixture(self):
        self.assertEqual(self.verify()['status'], 'PASS')
        RuntimeCheckerTest.checks += 1

    def test_rejections(self):
        cases = [
            ('server', lambda r: r.update(revision=165), '修订166'),
            ('server', lambda r: r.update(contract_enabled=False), '启用状态'),
            ('server', lambda r: r.update(world_directory='another-world'), '世界目录'),
            ('server', lambda r: r['dimensions'].pop(), '45个'),
            ('server', lambda r: r['dimensions'].append(copy.deepcopy(r['dimensions'][0])), '重复ID'),
            ('server', lambda r: r['dimensions'][0].update(min_y=0), '实际高度'),
            ('server', lambda r: r['dimensions'][0].update(logical_height=1024), '实际高度'),
            ('server', lambda r: r['dimensions'][0].update(sections=24), '实际高度'),
            ('server', lambda r: r['dimensions'][0].update(last_section_byte_roundtrip=False), '序列化失败'),
            ('server', lambda r: r['dimension_type_contracts'].pop(), '47种'),
            ('server', lambda r: r['dimension_type_contracts'][0].update(original_height=16), '冻结快照'),
            ('server', lambda r: r['probe_verification']['checks'].pop(), '135个'),
            ('server', lambda r: r['probe_verification']['checks'].__setitem__(1, copy.deepcopy(r['probe_verification']['checks'][0])), '重复或意外'),
            ('server', lambda r: r['probe_verification']['checks'][0].update(heightmap_top_block_y=767), '精确Y'),
            ('server', lambda r: r['probe_verification']['checks'][0].update(block_matches=1), '实物'),
            ('server', lambda r: r['probe_verification']['checks'][1].update(chest_name_persisted=False), '自定义名称'),
            ('client', lambda r: r['synced_dimension_types'].pop(), '全部47'),
            ('client', lambda r: r['synced_dimension_types'][0].update(height=384), '不一致'),
            ('client', lambda r: r.update(sections=24), '客户端实际世界边界'),
            ('restart_server', lambda r: r.update(world_id=str(uuid.uuid4())), 'UUID改变'),
            ('restart_server', lambda r: r['probe_verification'].update(created_at='2026-10-17T02:02:00Z'), '同一份'),
            ('old_server', lambda r: r.update(contract_enabled=True), '启用状态'),
            ('old_server', lambda r: r['dimensions'][0].update(height=1024), '实际高度'),
            ('server', lambda r: r.update(captured_at='2026-10-17T02:20:00Z'), '导出窗口'),
        ]
        original = copy.deepcopy(self.reports)
        for role, mutate, expected in cases:
            with self.subTest(role=role, expected=expected):
                self.reports = copy.deepcopy(original)
                mutate(self.reports[role])
                self.persist()
                with self.assertRaisesRegex(checker.EvidenceError, expected):
                    self.verify()
                RuntimeCheckerTest.checks += 1
        self.reports = original
        self.persist()
        self.receipt['launches'][2]['process_id'] = 100
        self.args.launch_receipt.write_text(json.dumps(self.receipt), encoding='utf-8')
        with self.assertRaisesRegex(checker.EvidenceError, '同一PID'):
            self.verify()
        RuntimeCheckerTest.checks += 1

    def test_receipt_rejections(self):
        original = copy.deepcopy(self.receipt)
        cases = [
            (lambda r: r.update(schema=True), '版本错误'),
            (lambda r: r.update(game_directory=str(self.directory / 'other-instance')), '实例目录'),
            (lambda r: r.update(expected_jar_sha256='0' * 64), '模组SHA'),
            (lambda r: r['launches'][0].update(instance_confirmed=False), '身份核对'),
            (lambda r: r['launches'][0].update(instance_evidence=''), '身份核对'),
            (lambda r: r['launches'][0].update(process_id=True), '必须是整数'),
            (lambda r: r['launches'][0].update(process_created_at='2026-10-16T23:00:00Z'), '时序矛盾'),
            (lambda r: r['launches'][0].update(export_started_at='2026-10-17T01:00:00'), '缺少时区'),
            (lambda r: r['launches'][0].update(export_ended_at='2099-01-01T00:00:00Z'), '未来'),
            (lambda r: r['launches'][0]['reports']['server'].update(sha256='0' * 64), '报告SHA'),
            (lambda r: r['launches'][0]['reports']['server'].update(path=str(self.paths['server'])), '报告路径'),
        ]
        for mutate, expected in cases:
            with self.subTest(expected=expected):
                receipt = copy.deepcopy(original)
                mutate(receipt)
                self.args.launch_receipt.write_text(json.dumps(receipt), encoding='utf-8')
                with self.assertRaisesRegex(checker.EvidenceError, expected):
                    self.verify()
                RuntimeCheckerTest.checks += 1

    def test_output_never_overwrites_inputs(self):
        inventory = self.directory / 'inventory.json'
        inventory.write_bytes(checker.INVENTORY.read_bytes())
        inputs = [*self.paths.values(), self.args.launch_receipt, inventory,
                  Path(self.receipt['deployed_jar'])]
        alias = self.directory / 'jar-hardlink.json'
        os.link(inputs[-1], alias)
        inputs.append(alias)
        argv = ['--launch-receipt', str(self.args.launch_receipt), '--inventory', str(inventory)]
        for role, path in self.paths.items():
            argv.extend(['--' + role.replace('_', '-'), str(path)])
        for path in inputs:
            with self.subTest(path=str(path)):
                previous_hash = checker.sha(path)
                with contextlib.redirect_stdout(io.StringIO()) as captured:
                    self.assertEqual(checker.main([*argv, '--output', str(path)]), 1)
                self.assertIn('输出路径不得覆盖', captured.getvalue())
                self.assertEqual(checker.sha(path), previous_hash)
                RuntimeCheckerTest.checks += 1

    def test_iso_timestamp_precision(self):
        cases = [
            ('2026-10-17T22:01:19.7418540+08:00', '2026-10-17T14:01:19.741854+00:00'),
            ('2026-10-17T22:01:19.274401600+08:00', '2026-10-17T14:01:19.274401+00:00'),
            ('2026-10-17T22:01:19.999999999+08:00', '2026-10-17T14:01:19.999999+00:00'),
            ('2026-10-17T22:01:19-03:30', '2026-10-18T01:31:19+00:00'),
            ('2026-10-17T22:01:19Z', '2026-10-17T22:01:19+00:00'),
        ]
        for length in range(1, 10):
            fraction = '123456789'[:length]
            expected = fraction[:6].ljust(6, '0')
            cases.append(('2026-10-17T22:01:19.' + fraction + 'Z',
                          '2026-10-17T22:01:19.' + expected + '+00:00'))
        for value, expected in cases:
            with self.subTest(value=value):
                original = value
                self.assertEqual(checker.instant(value).isoformat(), expected)
                self.assertEqual(value, original)
                RuntimeCheckerTest.checks += 1
        for value in ('2026-10-17T22:01:19.1234567890Z', '2026-10-17T22:01:19.Z',
                      '2026-10-17T22:01:19,123Z', '2026-10-17 22:01:19Z',
                      '2026-10-17T22:01:19z', '2026-10-17T22:01:19+0800',
                      '2026-10-17T22:01:19+08:60', '2026-10-17T22:01:19+24:00',
                      '2026-10-17T22:01:19.123456', '2026-02-30T22:01:19Z',
                      '2026-10-17T22:01:60Z', '2026-10-17T22:01:19Z trailing'):
            with self.subTest(value=value):
                with self.assertRaises(checker.EvidenceError):
                    checker.instant(value)
                RuntimeCheckerTest.checks += 1


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(RuntimeCheckerTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'result.json').write_text(json.dumps({'schema': 1, 'revision': 166,
        'synthetic_validator_selftest_only': True, 'cases_checked': RuntimeCheckerTest.checks,
        'passed': result.wasSuccessful(), 'runtime_height_contract_verified': False,
        'boundary': '只证明核验器行为；没有实际Minecraft运行、实例身份或高空方块持久化通过证据'},
        ensure_ascii=False, indent=2), encoding='utf-8')
    raise SystemExit(0 if result.wasSuccessful() else 1)
