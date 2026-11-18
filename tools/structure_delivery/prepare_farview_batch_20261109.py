# -*- coding: utf-8 -*-
"""记录客户端发现的批次数瓶颈及对应修复；不宣称复测通过。"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]


def main():
    path = ROOT / 'src/main/resources/assets/hk3gtl/changelog.json'
    data = json.loads(path.read_text(encoding='utf8'))
    assert data['entries'][0]['revision'] == 226
    data['entries'].insert(0, dict(revision=227, date='2026-11-09', timezone='Asia/Hong_Kong',
        reason='依据客户端采样合并精确远景绘制批次', changes=[
            '客户端实测发现远景缓存补全后同一视角提交约1780批，额外CPU开销明显；保存原始性能包。',
            '保留16格精确缓存与真实静态面，将相邻分区合并为64格GPU绘制批次；分帧准备、单工作线程和显存上限保留。',
            '完全处于已加载近景与三维遮罩内的批次提前跳过；近远交接仍使用统一投影与真实深度。',
            '新增立即生效的/hk3farview on与off客户端开关，用于同视角性能对照；配置文件外部改动不视为已热重载。',
            '构建、停机安装与客户端复测分别记录，完整控制器成型和工程运行验收另计。']))
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    path = ROOT / 'src/main/java/com/sirin/hk3gtl/client/farview/Hk3FarTileMesh.java'
    source = path.read_text(encoding='utf8')
    start = source.index('                var section=piece.section();')
    end = source.index('                }\n                var rendered', start)
    source = source[:start] + ''.join('    ' + line if line.strip() else line
                                    for line in source[start:end].splitlines(keepends=True)) + source[end:]
    path.write_text(source, encoding='utf8')


if __name__ == '__main__':
    main()
