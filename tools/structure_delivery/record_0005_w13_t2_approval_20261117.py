from datetime import datetime
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / 'logs/0005-w13-t2-production-20261117'
FILES = ['AGENTS.md', 'rule/当前多方块设计规则.md']
TEXT = '''

## 2026-11-17 对话0005：W13电视山T2-M1正式实装批准

- 负责人批准“可以，没问题，但是你控制器打算放哪，实装一下”，并明确“原样实装，允许 W13 专项例外（推荐）”。W13采用T2电视山与M1眼珠、电缆动画，20种实际方块作为本机专项例外，沿用当前造型与配色。
- 正式结构宽1207×深1042×高1213，共55,059,317格实体。完整HK3P/2蓝图为`src/main/resources/data/hk3gtl/structures/w13_candidate.bin.gz`，11,167,028条游程，SHA-256为`c034a38d6b53a10197ba6bfb57b130c7a846f75234420058a4323a099db00443`；沿用完整建造与GTL原生逐批判定，需要可容纳1213格高度的维度。
- 唯一主控位于正面中央电缆末端检修盒，源坐标(0,16,472)、归一化坐标(623,542,1020)，朝南且正面外露。除主控外，全部实体格可自由替换合法通用接口，不额外预留接口区域。
- 正式研究母机保留研究、支付、退款与原UI，制造、实际研究扣电或创造调试运行状态驱动眼珠转向与九根粗缆摆动。第三根连接主控的电缆两端固定，中段轻摆；待机恢复T2静态。动态遮罩含1,546,420格，接口继续原生显示。
- 正式身份、完整JEI及终端全景、1213层截面、普通渲染、Embeddium与远景路由均已接入。批准、源码、完整构建、交付、安装与游戏事实分别记录于`logs/0005-w13-t2-production-20261117/`，本条记录批准及源码状态，构建结果另记；原评分与分母保持，W07继续停止。
'''


def main():
    backup = LOG / 'before-memory.zip'
    with ZipFile(backup, 'x', ZIP_DEFLATED, compresslevel=6) as archive:
        for name in FILES:
            archive.write(ROOT / name, name)
    with ZipFile(backup) as archive:
        for name in FILES:
            if archive.read(name) != (ROOT / name).read_bytes():
                raise ValueError('记忆压缩备份核对失败：' + name)
    for name in FILES:
        with (ROOT / name).open('a', encoding='utf8') as stream:
            stream.write(TEXT)
    record = dict(recorded_at=datetime.now().astimezone().isoformat(), conversation='0005',
        conversation_id='01a1e02a-4d20-7d81-bdab-70404f66086d',
        approval_quote='可以，没问题，但是你控制器打算放哪，实装一下',
        material_exception_approval_quote='原样实装，允许 W13 专项例外（推荐）',
        approved=True, actual_material_types=20, controller_source_xyz=[0,16,472],
        controller_blueprint_xyz=[623,542,1020], controller_facing='south',
        backup=str(backup), backup_sha256=hashlib.sha256(backup.read_bytes()).hexdigest(),
        backup_original_bytes=sum(len(ZipFile(backup).read(name)) for name in FILES),
        backup_compressed_bytes=backup.stat().st_size, memory_files=FILES,
        installed=False, game_started=False, game_verified=False)
    (LOG / 'approval.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', 'utf8')
    print('W13外观、动画与20种方块专项例外已写入两处既有记忆。')


if __name__ == '__main__':
    main()
