"""项目搬迁路径回归：历史证据、仓库相对路径和外部实例必须分开处理。"""
from pathlib import Path
import json
import unittest

from project_paths import LEGACY_ROOTS, ROOT, project_path


class ProjectPathTests(unittest.TestCase):
    def test_legacy_roots_preserve_chinese_and_spaces(self):
        for old in LEGACY_ROOTS:
            with self.subTest(old=old):
                self.assertEqual(project_path(old / 'deliveries/确认档案/测试 01.nbt'),
                                 ROOT / 'deliveries/确认档案/测试 01.nbt')

    def test_case_and_slash_variants(self):
        old = 'c:/users/owner/desktop/PROGREM/complate progrem/hk3gtl/src/main'
        self.assertEqual(project_path(old), ROOT / 'src/main')

    def test_current_and_relative_paths(self):
        for value in ('src/main/java', Path('src/main/java'), ROOT / 'src/main/java'):
            self.assertEqual(project_path(value), ROOT / 'src/main/java')

    def test_external_paths_are_unchanged(self):
        for value in ('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/目标实例',
                      'E:/Other/HK3GTL/file.json', 'C:/Users/OWNER/Desktop/hk3gtl-other/file.json'):
            self.assertEqual(project_path(value), Path(value))

    def test_legacy_parent_traversal_is_rejected(self):
        with self.assertRaises(ValueError):
            project_path(LEGACY_ROOTS[0] / '../other/file.json')

    def test_resource_relative_resolution(self):
        from i40_voltage_progression_20261028 import resolve
        self.assertEqual(resolve('data/hk3gtl/structures/approved/i44.json'),
                         ROOT / 'src/main/resources/data/hk3gtl/structures/approved/i44.json')

    def test_current_approval_and_formal_sources_exist(self):
        index = ROOT / 'deliveries/多方块确认归档/当前归档索引.json'
        rows = json.loads(index.read_text(encoding='utf-8'))['entries']
        rows += [json.loads(path.read_text(encoding='utf-8')) for path in
                 (ROOT / 'src/main/resources/data/hk3gtl/structures/approved').glob('*.json')]
        for row in rows:
            for key in ('archive', 'archive_zip', 'approval_manifest', 'approved_nbt',
                        'source_snapshot', 'source_metadata', 'source_nbt'):
                if row.get(key):
                    with self.subTest(machine=row.get('id', row.get('key')), key=key):
                        self.assertTrue(project_path(row[key]).exists(), row[key])


if __name__ == '__main__':
    unittest.main()
