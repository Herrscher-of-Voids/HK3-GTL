import hashlib
import json
import shutil

from prepare_watermelon_cipher_world_20261114 import ROOT, main, write_json


DELIVERY = ROOT / 'deliveries/西瓜ARG_完整籽海_玩家体验_R283_20261114'
WORLD = DELIVERY / '世界/西瓜来信_完整籽海'
INTRO = ('右键随身手机，打开「残页译码」。\n\n'
         '从第一张残页开始。规则与线索都在程序里，答案由你留下。\n\n'
         '纸笔和旅途用品已经备好。等信封展开后，再去读下一段来信。\n\n'
         '离开后，回到同一存档，仍可继续。')
SUPPLIES = (
    ('hk3gtl:personal_phone', 2, '{Charge:128000L}'),
    ('minecraft:oak_planks', 256, ''),
    ('minecraft:torch', 64, ''),
    ('minecraft:ladder', 64, ''),
    ('minecraft:iron_axe', 1, ''),
    ('minecraft:iron_pickaxe', 1, ''),
    ('minecraft:water_bucket', 1, ''),
    ('minecraft:white_bed', 1, ''),
    ('minecraft:oak_boat', 1, ''),
)


if __name__ == '__main__':
    manifest = main(WORLD, '西瓜来信 · 完整籽海', INTRO, SUPPLIES)
    manifest['候选修订'] = 'R283'
    manifest['所需模组'] = 'HK3GTL R283候选及增强版3.5现有依赖，由负责人自行安装后体验。'
    manifest['开局'] = '右键满电手机完成真实安装，再打开残页译码；五题解开后由服务端发放门桩。'
    manifest['状态边界'] = '仅首次领取场景与用品标记；未预发门桩，没有手机安装、谜题答案、ARG解锁或终点完成进度。'
    write_json(WORLD / '离线准备清单.json', manifest)
    archive = shutil.make_archive(str(DELIVERY / '西瓜来信_完整籽海'), 'zip', WORLD.parent, WORLD.name)
    receipt = dict(
        revision='R283', world=WORLD.relative_to(ROOT).as_posix(),
        archive=str((DELIVERY / '西瓜来信_完整籽海.zip').relative_to(ROOT).as_posix()),
        sha256=hashlib.sha256((DELIVERY / '西瓜来信_完整籽海.zip').read_bytes()).hexdigest(),
        preparation='仅离线生成；R282旧图保持，未改活动实例、现有存档或安装JAR。',
        entry='将ZIP内同名世界文件夹导入saves，使用R283候选进图后右键手机，打开残页译码。',
        player_acceptance='由负责人亲自解密，尚未执行。', supplies=manifest['额外探险补给'])
    write_json(DELIVERY / 'map-preparation.json', receipt)
    print(json.dumps(receipt, ensure_ascii=False))
