from datetime import datetime
from pathlib import Path
import hashlib
import json
import shutil

import nbtlib as nbt

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/0005_万象天枢_三位一体取形_A1_20261114'
LOG = ROOT / 'logs/0005-ae-nexus-integration-a1-20261114'
RESOURCE = ROOT / 'src/main/resources/data/hk3gtl/structures/ae_nexus_a1.nbt'
ARCHIVE = ROOT / 'deliveries/多方块确认归档/20261114_0005_万象天枢_A1_外观确认'


def main():
    LOG.mkdir(parents=True, exist_ok=True)
    ARCHIVE.mkdir(parents=True)
    for name in ('manifest.json', '0005-ae-nexus-trinity-a1.nbt', '0005-ae-nexus-trinity-a1.schem', '前右预览.png'):
        shutil.copy2(SOURCE / name, ARCHIVE / name)
    template = nbt.load(SOURCE / '0005-ae-nexus-trinity-a1.nbt')
    template['palette'][-1]['Properties'] = nbt.Compound({'facing': nbt.String('north')})
    template['blocks'] = nbt.List[nbt.Compound](sorted(
        (block for block in template['blocks'] if int(block['state']) != 0),
        key=lambda block: tuple(map(int, block['pos']))))
    template.save(RESOURCE)
    record = dict(created_at=datetime.now().astimezone().isoformat(timespec='seconds'),
        conversation='0005', conversation_id='01a1d6b8-bd81-79d3-a6f4-4f590806cc8e',
        approval_quote='没事，就用这个吧，把它接入到万象天枢里吧',
        approved_design='万象天枢 · 三位一体取形 A1', appearance_approved=True,
        archive=str(ARCHIVE.relative_to(ROOT)), resource=str(RESOURCE.relative_to(ROOT)),
        source_sha256=hashlib.sha256((SOURCE / '0005-ae-nexus-trinity-a1.nbt').read_bytes()).hexdigest(),
        resource_sha256=hashlib.sha256(RESOURCE.read_bytes()).hexdigest(),
        resource_conversion='保留全部实体坐标与材料；移除空气记录，由正式Pattern空域规则检查；主控显式朝北；按XYZ排序供现有稀疏建造器使用',
        size_wdh=[35, 35, 33], blocks=6733, controller_xyz=[17, 3, 2],
        game_verified=False, installed=False)
    text = json.dumps(record, ensure_ascii=False, indent=2) + '\n'
    (LOG / 'geometry-integration.json').write_text(text, 'utf8')
    (ARCHIVE / 'approval.json').write_text(text, 'utf8')
    print(json.dumps(record, ensure_ascii=True))


if __name__ == '__main__':
    main()
