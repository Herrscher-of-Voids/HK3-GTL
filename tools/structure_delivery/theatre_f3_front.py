import base64
import gzip
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT/'deliveries/0005_支配剧场_外置巨像操偶_F2_20261117'


def build_theatre(out):
    out = Path(out)
    encoded = json.loads((SOURCE/'theatre.js').read_text('utf8').split('=', 1)[1].strip().removesuffix(';'))
    payload = json.loads(gzip.decompress(base64.b64decode(encoded)))
    removed = [part for part in payload['parts'] if part['modelId'] == 'front']
    parts = [part for part in payload['parts'] if part['modelId'] != 'front']
    blocks = sum(part['blocks'] for part in parts)
    lower = [min(part['origin'][axis] for part in parts) for axis in range(3)]
    upper = [max(part['origin'][axis]+part['size'][axis]-1 for part in parts) for axis in range(3)]
    bounds = dict(min=lower, max=upper)
    data = payload['data']
    data.update(title='支配剧场 · 正面敞开巨像操偶 F3', candidate='F3', total_blocks=blocks,
                bounds=bounds, sizeXYZ=[b-a+1 for a, b in zip(lower, upper)], front_removed=True)
    data['models'] = [model for model in data['models'] if model['id'] != 'front']
    data['design'] = [*data['design'], '前厅整面围护、门面与前端二层横廊实体已删除，正面敞开；沿用F2实体屋顶开口。']
    payload['parts'] = parts
    encoded = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode(), compresslevel=6)).decode()
    (out/'theatre.js').write_text('window.THEATRE_PAYLOAD='+json.dumps(encoded)+';\n', 'utf8')
    info = dict(blocks=blocks, parts=len(parts), front_removed=True, roof_opening=data['roof_opening'],
                removed_front_parts=len(removed), removed_front_blocks=sum(part['blocks'] for part in removed))
    deleted = [dict(id=part['id'], label=part['label'], blocks=part['blocks'],
                    bounds=dict(min=part['origin'],
                                max=[a+b-1 for a, b in zip(part['origin'], part['size'])])) for part in removed]
    record = dict(source=str(SOURCE/'theatre.js'), **info, bounds=bounds, removed_components=deleted,
                  note='直接从建筑数据删除全部front构件；大厅地面、内部柱和楼梯沿用F2。')
    (out/'建筑改造.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', 'utf8')
    return info
