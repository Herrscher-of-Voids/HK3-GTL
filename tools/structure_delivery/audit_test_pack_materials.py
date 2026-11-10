"""Inventory actual test-pack block resources without changing the instance."""
import collections
import json
import re
import zipfile
from pathlib import Path

from material_resources import Resources
from redesign69_geometry import ROOT


INSTANCE = Path.home() / 'AppData/Roaming/PrismLauncher/instances/GTL十一周目/minecraft'
OUT = ROOT / 'deliveries/测试包建材核对_GTL十一周目'


def main():
    mods = []
    blocks = {}
    for path in sorted((INSTANCE / 'mods').glob('*.jar')):
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            ids = []
            for name in names:
                match = re.fullmatch(r'assets/([^/]+)/blockstates/(.+)\.json', name)
                if match:
                    block = ':'.join(match.groups())
                    blocks[block] = str(path)
                    ids.append(block)
            mods.append({'jar': path.name, 'blockstate_resources': len(ids)})
    resources = Resources(instance=INSTANCE)
    candidates = []
    try:
        for block, source in sorted(blocks.items()):
            if not re.search(r'casing|glass|coil|containment|machine|panel|plating|pillar', block):
                continue
            row = {'block': block, 'source': source}
            try:
                material = resources.material(block)
                row.update({'resolved_cube': True, 'model': material['model'],
                            'transparent': material['transparent'], 'tinted': material['tinted'],
                            'animated': bool(material['animations'])})
            except (FileNotFoundError, ValueError, KeyError) as error:
                row.update({'resolved_cube': False, 'reason': str(error)})
            candidates.append(row)
    finally:
        resources.close()
    report = {'instance': str(INSTANCE), 'mods': mods, 'blockstate_sources': blocks,
              'candidates': candidates,
              'limits': ['Resource existence is not proof of runtime registration or recipe availability.',
                         'Non-cube, stateful and tinted models need additional preview handling.',
                         'Instance files were not modified.']}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / '资源与建材核对.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'mods': len(mods), 'blockstates': len(blocks),
                      'namespaces': dict(collections.Counter(b.split(':')[0] for b in blocks)),
                      'material_candidates': len(candidates),
                      'resolved_cube_candidates': sum(c['resolved_cube'] for c in candidates)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
