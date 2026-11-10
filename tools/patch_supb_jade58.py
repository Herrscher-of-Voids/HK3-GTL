# -*- coding: utf-8 -*-
"""#1 2026-09-23 03:53:00 / revision58。
将GTLSupb的Jade注入参数从Accessor修正为目标实际要求的BlockAccessor。
Match the Jade injection descriptor to the actual BlockAccessor target.
只改一个常量，保留原机器逻辑、instanceof检查和全部资源；先备份再部署。
Change one constant, preserve machine logic/checks/resources, back up before deployment.
限定原始3.5哈希，未知包拒绝；--apply才替换libs与用户指定实例的对应包。
Pin the original 3.5 hash; --apply updates only matching libs and instance packages.
"""
import argparse
from datetime import datetime
import json
import shutil
import subprocess
import zipfile
from patch_advanced_hatch57 import ROOT, MODS, digest, patch_class

EXPECTED = '73e701d0ade17e17118b346b3a75436979baff421f180cf6979d2006a420eb08'
ENTRY = 'com/gtlsupb/gtlsupb/mixin/gtceu/integration/ParallelProviderMixin.class'
OLD = b'(Lnet/minecraft/nbt/CompoundTag;Lsnownee/jade/api/Accessor;Lorg/spongepowered/asm/mixin/injection/callback/CallbackInfo;)V'
NEW = OLD.replace(b'api/Accessor;', b'api/BlockAccessor;')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    sources = [ROOT / 'libs/GTLsupb-3.5.jar', MODS / 'GTLsupb-3.5.jar']
    assert all(digest(p) == EXPECTED for p in sources)
    folder = ROOT / '.dbg/supb-jade58'
    folder.mkdir(parents=True, exist_ok=True)
    candidate = folder / sources[0].name
    with zipfile.ZipFile(sources[0]) as original, zipfile.ZipFile(candidate, 'w') as patched:
        assert not any(n.upper().endswith(('.SF', '.RSA', '.DSA')) for n in original.namelist())
        patched.comment = original.comment
        for info in original.infolist():
            content = original.read(info.filename)
            patched.writestr(info, patch_class(content, OLD, NEW) if info.filename == ENTRY else content)
    with zipfile.ZipFile(sources[0]) as original, zipfile.ZipFile(candidate) as patched:
        assert original.namelist() == patched.namelist()
        assert patched.testzip() is None
        assert [n for n in original.namelist() if original.read(n) != patched.read(n)] == [ENTRY]
    disassembly = subprocess.check_output(
        ['javap', '-p', '-c', '-classpath', str(candidate), ENTRY[:-6].replace('/', '.')], text=True)
    assert 'gtlSupb$appendServerData(net.minecraft.nbt.CompoundTag, snownee.jade.api.BlockAccessor,' in disassembly
    (folder / 'patched-javap.txt').write_text(disassembly, encoding='utf-8')
    print('Verified one descriptor change:', digest(candidate))
    if args.apply:
        stamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        backups = [ROOT / 'archive' / ('supb-jade58-' + stamp),
                   MODS.parent / 'hk3gtl-mod-backups' / ('supb-jade58-' + stamp)]
        for source, backup in zip(sources, backups):
            backup.mkdir(parents=True)
            shutil.copy2(source, backup / source.name)
            assert digest(backup / source.name) == EXPECTED
        # 实例优先：若游戏占用则libs也不改。Instance first: locks leave libs untouched.
        for source in reversed(sources):
            assert digest(source) == EXPECTED
            stage = source.with_suffix('.jar.hk3patch.tmp')
            shutil.copy2(candidate, stage)
            stage.replace(source)
            assert digest(source) == digest(candidate)
        manifest = dict(time=stamp, original_sha256=EXPECTED, patched_sha256=digest(candidate),
                        changed_entry=ENTRY, backups=[str(p) for p in backups])
        for backup in backups:
            (backup / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
