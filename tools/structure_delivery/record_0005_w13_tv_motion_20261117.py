# -*- coding: utf-8 -*-
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W13_侵蚀之律者电视山_T2_20261117'
LOG = ROOT / 'logs/0005-w13-tv-motion-20261117'


def digest(path):
    sha = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            sha.update(chunk)
    return sha.hexdigest()


def main():
    observation = json.loads((OUT / 'motion-preview.json').read_text('utf8'))
    active = observation['captures'][8]
    receipt = dict(machine='W13', revision='T2-M1',
        recorded_at=datetime.now(timezone(timedelta(hours=8))).isoformat(),
        request='眼珠转动，电线甩动', scope='网页运行预览',
        eye=active['eye'], cables=active['cables'], captures=len(observation['captures']),
        browser_errors=observation['errors'], failed_requests=observation['failed'],
        running_time=[observation['running'][key]['time'] for key in ['before', 'after']],
        paused_time=[observation['paused'][key]['time'] for key in ['before', 'after']],
        idle_time=[observation['idle'][key]['time'] for key in ['before', 'after']],
        appearance_approved=False, official_blueprint_connected=False, game_animation_connected=False,
        jar_built=False, installed=False, game_started=False,
        static_nbt_sha256=digest(OUT / 'W13-侵蚀之律者电视山-T2.nbt'),
        compressed_backups=['before-motion.zip', 'before-memory.zip'],
        visual_review=['眼珠0/3秒', '电缆0/8秒', '整机8秒', '主控8秒'],
        score_changed=False)
    shutil.copy2(Path(__file__), OUT / '生成脚本' / Path(__file__).name)
    manifest = json.loads((OUT / 'manifest.json').read_text('utf8'))
    manifest['motion_revision'] = 'T2-M1'
    manifest['motion'] = dict(scope='网页运行预览', game_connected=False,
        eye='屏幕内转动注视', cables='九缆分节错相甩动，主控缆两端固定',
        pause='定格当前姿态', idle='恢复T2静态', nbt='T2静态实体保持')
    for path in OUT.rglob('*'):
        if path.is_file() and path.name != 'manifest.json':
            relative = path.relative_to(OUT).as_posix()
            if relative not in manifest['files'] or relative in ['index.html', 'viewer.bundle.js'] or relative.startswith('生成脚本/'):
                manifest['files'][relative] = dict(bytes=path.stat().st_size, sha256=digest(path))
    for path, value in [(LOG / 'completion.json', receipt), (OUT / 'manifest.json', manifest)]:
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')
    print(json.dumps(dict(captures=receipt['captures'], eye_blocks=receipt['eye']['voxelCount'],
        cable_quads=receipt['cables']['renderedQuads'], browser_errors=receipt['browser_errors'],
        static_nbt_sha256=receipt['static_nbt_sha256']), ensure_ascii=True))


if __name__ == '__main__':
    main()
