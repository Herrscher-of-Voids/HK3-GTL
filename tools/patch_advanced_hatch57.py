# -*- coding: utf-8 -*-
"""#1 2026-09-23 03:47:00 / 内测5修订57。
修复已核实旧版附属的单个显示接口引用；不增加或删除模组。
Patch one verified display reference; do not add or remove mods.
默认只生成并验证候选包，--apply 先核对原包哈希并备份再替换。
Dry run produces a checked candidate; --apply backs up before replacement.
输入仅允许指定 SHA256 的 fix2；未知版本拒绝处理，避免误改其他字节码。
Only the pinned fix2 SHA256 is accepted; unknown versions fail closed.
"""
import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
import shutil
import struct
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MODS = Path(r'C:\Users\OWNER\AppData\Roaming\PrismLauncher\instances\GregTech-Leisure-1.4.5.2\minecraft\mods')
NAME = 'GTMAdvancedHatch-1.20.1-0.1.10 fix2.jar'
EXPECTED = 'e5351799eac5ab70a61696e073557293e6e3921c2e3eb9253d33791c40701a68'
ENTRY = 'com/xingmot/gtmadvancedhatch/mixin/gtm/GTRecipeWidgetMixin.class'
OLD = b'com/gtladd/gtladditions/utils/CommonUtils'
NEW = b'org/gtlcore/gtlcore/utils/NumberUtils'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def patch_class(data, old=OLD, new=NEW):
    """仅重写常量池 UTF8 的类路径及其长度，保持索引和方法字节码。
    Rewrite only a constant-pool UTF8 owner and length; preserve all indices/code.
    JVM long/double 占两个槽；未知标签立即失败。Long/double occupy two slots.
    """
    assert data[:4] == b'\xca\xfe\xba\xbe'
    count = struct.unpack_from('>H', data, 8)[0]
    pos, index, changed = 10, 1, 0
    output = bytearray(data[:10])
    sizes = {3: 4, 4: 4, 5: 8, 6: 8, 7: 2, 8: 2, 9: 4, 10: 4,
             11: 4, 12: 4, 15: 3, 16: 2, 17: 4, 18: 4, 19: 2, 20: 2}
    while index < count:
        start, tag = pos, data[pos]
        pos += 1
        if tag == 1:
            size = struct.unpack_from('>H', data, pos)[0]
            value = data[pos + 2:pos + 2 + size]
            pos += 2 + size
            if value == old:
                output.extend(b'\x01' + struct.pack('>H', len(new)) + new)
                changed += 1
            else:
                output.extend(data[start:pos])
        else:
            pos += sizes[tag]
            output.extend(data[start:pos])
            if tag in (5, 6):
                index += 1
        index += 1
    assert changed == 1, changed
    output.extend(data[pos:])
    assert old not in output
    return bytes(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    source = MODS / NAME
    assert digest(source) == EXPECTED, 'Unexpected source JAR; inspect before patching.'
    target_api = subprocess.check_output(
        ['javap', '-p', '-classpath', str(ROOT / 'libs/gtlcore-1.2.3.2-fix2.jar'),
         NEW.decode().replace('/', '.')], text=True)
    assert 'public static java.lang.String formatDouble(double);' in target_api
    output_dir = ROOT / '.dbg/advanced-hatch57'
    output_dir.mkdir(parents=True, exist_ok=True)
    candidate = output_dir / NAME
    with zipfile.ZipFile(source) as original, zipfile.ZipFile(candidate, 'w') as patched:
        assert not any(n.upper().endswith(('.SF', '.RSA', '.DSA')) for n in original.namelist())
        patched.comment = original.comment
        for info in original.infolist():
            content = original.read(info.filename)
            patched.writestr(info, patch_class(content) if info.filename == ENTRY else content)
    with zipfile.ZipFile(source) as original, zipfile.ZipFile(candidate) as patched:
        assert original.namelist() == patched.namelist()
        assert patched.testzip() is None
        differences = [n for n in original.namelist() if original.read(n) != patched.read(n)]
        assert differences == [ENTRY], differences
        assert not any(OLD in patched.read(n) for n in patched.namelist() if n.endswith('.class'))
    disassembly = subprocess.check_output(
        ['javap', '-p', '-c', '-classpath', str(candidate), ENTRY[:-6].replace('/', '.')], text=True)
    assert NEW.decode() + '.formatDouble:(D)Ljava/lang/String;' in disassembly
    assert OLD.decode() not in disassembly
    (output_dir / 'patched-javap.txt').write_text(disassembly, encoding='utf-8')
    print('Verified: exactly one class changed; replacement static API resolves.')
    print('Candidate SHA256:', digest(candidate))
    if args.apply:
        stamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        backup = MODS.parent / 'hk3gtl-mod-backups' / ('advanced-hatch57-' + stamp)
        backup.mkdir(parents=True)
        shutil.copy2(source, backup / NAME)
        assert digest(backup / NAME) == EXPECTED
        assert digest(source) == EXPECTED
        # 同目录临时文件原子替换；占用失败时保留原包和备份，不强杀游戏。
        # Atomic replacement; on file-lock failure retain original/backup, never kill the game.
        staged = MODS / (NAME + '.hk3patch.tmp')
        shutil.copy2(candidate, staged)
        staged.replace(source)
        assert digest(source) == digest(candidate)
        report = dict(time=stamp, source_sha256=EXPECTED, patched_sha256=digest(source),
                      changed_entry=ENTRY, old_owner=OLD.decode(), new_owner=NEW.decode(),
                      backup=str(backup), runtime_validation='pending restart')
        (backup / 'manifest.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        (output_dir / 'deployment.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        print('Deployed:', source)
        print('Backup:', backup)


if __name__ == '__main__':
    main()

# #2 2026-09-23 03:53:00 / revision58: 允许传入精确UTF8常量供Jade签名补丁复用。
# Accept an exact UTF8 pair for the Jade descriptor patch; defaults preserve revision57.
