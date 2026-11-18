# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import shutil
from zipfile import ZipFile, ZIP_DEFLATED

from package_0005_w13_tv_t2_20261117 import ROOT, OUT, LOG, NBT_FILE, digest, save


def main():
    geometry = json.loads((OUT / 'geometry.json').read_text('utf8'))
    preview = json.loads((OUT / '预览记录.json').read_text('utf8'))
    backup_path = LOG / 'before-memory.zip'
    targets = [ROOT / 'AGENTS.md', ROOT / 'rule/当前多方块设计规则.md']
    with ZipFile(backup_path, 'w', ZIP_DEFLATED, compresslevel=9) as archive:
        for path in targets:
            archive.write(path, path.relative_to(ROOT).as_posix())
    backup_files = {}
    with ZipFile(backup_path) as archive:
        for path in targets:
            name = path.relative_to(ROOT).as_posix()
            content = archive.read(name)
            info = archive.getinfo(name)
            backup_files[name] = dict(bytes=info.file_size, compressed_bytes=info.compress_size, sha256=digest(path),
                archive_content_matches=content == path.read_bytes())
    if any(not item['archive_content_matches'] for item in backup_files.values()):
        raise RuntimeError('规则文件在压缩期间发生变化，重新保存备份后再记录。')
    w, d, h = geometry['actual_size_wdh']
    entry = f'''\n\n## 2026-11-17 对话0005：W13中央电视山补全T2待审\n\n- 负责人指出原片巨眼电视下方也是电视山。官方42秒全景V01可见中央脚下连续小屏、深机壳与阶梯堆体，纳入W13整体；左右远景独立电视塔另行区分。V07至V11用于旧CRT细节与混合朝向，原R1/T1记录保留。\n- 当前入口为`deliveries/{OUT.name}/index.html`。T2用{geometry['television_count']}台大中小旧电视组成错层山体，包含圆角厚框、收窄后壳、鼓面屏、旋钮、按键、喇叭及格栅；混排黑屏、雪花、白青扫描、字符与彩条。中央顶簇抬高嵌入主机下方，机匣和电缆保留穿插；被遮挡的接触点、底部、背侧与尺寸属于方块建模补全。\n- 实际{w}×{d}×{h}（宽×深×高）、{geometry['blocks']:,}去重实体格、{len(geometry['components'])}分件、{geometry['unique_block_types']}种实际方块；全部真实整数格及GT/HK/原版原生像素贴图。完整NBT、整数格NPZ、原始分件、240台布局明细与来源随稿保存，T1历史候选保持。\n- 唯一主控沿用源坐标(0,16,472)的前方电缆检修端子，朝南且正面外露；其余全部实体格可自由换合法接口。网页运行仅演示主眼屏亮度与局部故障，电视山、主壳、机匣与电缆固定。\n- 18张网页截图覆盖全向、电视山、主机衔接、CRT细节、主眼屏、像素、主控和运行画面；浏览器错误及请求失败均为空。外观待负责人审核，CEV旧材料种类要求继续待确认，不继承W09/W11例外；正式蓝图接入、构建和安装另记，评分及批准数量保持，W07继续停止。回执`logs/{LOG.name}/completion.json`。\n'''
    for path in targets:
        with path.open('a', encoding='utf8', newline='') as stream:
            stream.write(entry)
    shutil.copy2(Path(__file__), OUT / '生成脚本' / Path(__file__).name)
    files = [path for path in OUT.rglob('*') if path.is_file() and path.name != 'manifest.json']
    save(OUT / 'manifest.json', dict(machine='W13', candidate='T2', actual_size_wdh=geometry['actual_size_wdh'],
        blocks=geometry['blocks'], television_count=geometry['television_count'], shape_selection_approved=True, appearance_approved=False,
        files={path.relative_to(OUT).as_posix(): dict(bytes=path.stat().st_size, sha256=digest(path)) for path in files}))
    completion = dict(machine='W13', candidate='T2', recorded_at=datetime.now(timezone(timedelta(hours=8))).isoformat(),
        request='我没记错的话，侵蝕之律者在那条影片下面的那个地方也是一座电视山啊',
        actual_size_wdh=geometry['actual_size_wdh'], blocks=geometry['blocks'], television_count=geometry['television_count'],
        unique_block_types=geometry['unique_block_types'], shape_selection_approved=True, appearance_approved=False,
        controller=geometry['controller'], scale_comparison=geometry['scale_comparison'],
        reviewed_images=['整体预览.png', '正面预览.png', '背面预览.png', '主机与电视山衔接.png', '旧电视近景.png', '主控近景.png', '像素近景.png'],
        screenshots=len(preview['captures']) + 1, browser_errors=preview['errors'], failed_requests=preview['failed'],
        backup=dict(path=backup_path.relative_to(ROOT).as_posix(), format='ZIP_DEFLATED', files=backup_files, archive_bytes=backup_path.stat().st_size),
        nbt=dict(path=(OUT / NBT_FILE).relative_to(ROOT).as_posix(), bytes=(OUT / NBT_FILE).stat().st_size, sha256=digest(OUT / NBT_FILE)),
        formal_blueprint_present=False, jar_built=False, installed=False, game_started=False, scores_changed=False)
    save(LOG / 'completion.json', completion)
    print(json.dumps({key: completion[key] for key in ['actual_size_wdh', 'blocks', 'television_count', 'screenshots', 'browser_errors', 'failed_requests']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
