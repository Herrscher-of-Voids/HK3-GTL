# -*- coding: utf-8 -*-
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / 'logs/textures-redraw-0002-r3-20261114/art-review.json'
SOURCE = 'deliveries/0002贴图材质_审定重绘_R4_20261114/manifest.json'
REDO = {'imitation_star_of_eden', 'imitation_oath_of_judah'}


def main():
    review = json.loads(REVIEW.read_text(encoding='utf-8'))
    manifest = json.loads((ROOT / SOURCE).read_text(encoding='utf-8'))
    accepted = [x for x in manifest['items'] if x['id'] not in REDO]
    additions = [{k: x[k] for k in ('id', 'name', 'sha256')} | {'source_revision': 'R4'}
                 for x in accepted if x['id'] not in review['accepted_ids']]
    accepted_assets = review['accepted_assets'] + additions
    accepted_ids = [x['id'] for x in accepted_assets]
    pending = [x for x in review['pending_redraw_ids'] if x not in accepted_ids]
    review.update({
        'revision': 'R4', 'review_date': '2026-11-14',
        'updated_at': datetime.now().astimezone().isoformat(timespec='seconds'),
        'source_manifest': SOURCE, 'newly_accepted_ids': [x['id'] for x in accepted],
        'newly_accepted_count': len(accepted), 'accepted_count': len(accepted_assets),
        'accepted_assets': accepted_assets, 'accepted_ids': accepted_ids,
        'pending_redraw_ids': pending, 'pending_redraw_count': len(pending),
        'active_nonfuel_redraw_ids': sorted(REDO),
        'r4_reviewed_ids': [x['id'] for x in manifest['items']],
        'r4_accepted_ids': [x['id'] for x in accepted], 'r4_redo_ids': sorted(REDO),
        'r4_accepted_count': len(accepted), 'r4_redo_count': len(REDO),
        'accepted_policy': f'累计{len(accepted_assets)}张锁定精确PNG；未经负责人新指示不重画。R4其余两张待重做。',
        'next_candidate': {'revision': 'R4', 'nonfuel_candidate_count': 28,
            'accepted_count': len(accepted), 'redraw_count': len(REDO),
            'gallery': 'deliveries/0002贴图材质_审定重绘_R4_20261114/index.html',
            'fuel_paused': False, 'art_approved': False},
    })
    REVIEW.write_text(json.dumps(review, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'newly_accepted': len(additions), 'accepted_total': len(accepted_assets),
                      'r4_redo': sorted(REDO), 'pending_total': len(pending)}))


if __name__ == '__main__':
    main()
