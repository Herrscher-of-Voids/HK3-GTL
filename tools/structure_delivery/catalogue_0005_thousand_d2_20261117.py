from pathlib import Path
import json
import os


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'deliveries/0005_千人人偶_原作重建_D2_20261117'
OLD = ROOT/'deliveries/0005_千人人偶_独立像素模型_D1_20261117/references/design'


def relative(path):
    return os.path.relpath(path, OUT).replace('\\', '/')


def main():
    game = json.loads((OUT/'references/game/sources.json').read_text('utf8'))
    animation = json.loads((OUT/'references/animation/references.json').read_text('utf8'))
    old = json.loads((OLD/'observations.json').read_text('utf8'))
    rows = []
    study = json.loads((OUT/'references/game/study.json').read_text('utf8'))
    priority = ['S01', 'S02', *study['main_references']]
    for record in sorted(game['references'], key=lambda r: priority.index(r['id']) if r['id'] in priority else len(priority)):
        r = dict(record)
        r.update(family='game', file=relative(OUT/'references/game'/record['file']),
                 selected=record.get('accepted', record.get('selected', True)),
                 source_url=record.get('source_url', record.get('page_url', '')),
                 note=record.get('use', record.get('description', '')))
        rows.append(r)
    for r in old['references']:
        if r.get('file') in ['official-jp-va.jpg', 'steam-port-preview.jpg', 'gmod-port-01.jpg',
                             'gmod-port-02.jpg', 'gmod-port-04.jpg', 'gmod-port-05.jpg',
                             'gmod-port-06.jpg', 'gmod-port-07.jpg']:
            rows.append(dict(r, id='D-'+r['file'].replace('.jpg', ''), family='design',
                             file=relative(OLD/r['file']), source_url=r['page_url'],
                             selected=True, note=r['use'], angle=r['use']))
    for r in animation['references']:
        rows.append(dict(r, family='animation', file=relative(OUT/'references/animation'/r['file']),
                         note='；'.join(r.get('visible_parts', []))+'。'+r.get('obstruction', r['excluded_reason'])))
    payload = dict(rows=rows, animation=animation['counting_note'],
                   game_notes=game.get('counting_note', '游戏原帧和社区移植图按逐项清单计数。'),
                   counts=dict(game=sum(r['selected'] for r in rows if r['family']=='game'),
                               design=sum(r['selected'] for r in rows if r['family']=='design'),
                               animation=animation['selected_count'],
                               animation_reviewed=animation['reviewed_count']))
    template = Path(__file__).with_name('thousand_d2_catalogue.html').read_text('utf8')
    (OUT/'参考图册.html').write_text(template.replace('CATALOGUE_PAYLOAD', json.dumps(payload, ensure_ascii=False).replace('</', '<\\/')), 'utf8')
    (OUT/'references/catalogue.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), 'utf8')
    print(json.dumps(payload['counts'], ensure_ascii=False))


if __name__ == '__main__':
    main()
