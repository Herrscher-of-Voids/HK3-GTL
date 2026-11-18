"""保留R269原包，叠入AE兼容修正与本轮版本身份。"""
import json
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'logs/industrial-datagen-r269-20261113'
BASE = OUT / 'HK3GTL-r268-industrial-fix-r269.jar'
BUILT = ROOT / 'build/libs/hk3gtl-0.5.0.jar'
CLASSES = ['mixin/ae/Hk3ExactCpuProgramMixin']
RESOURCE = 'assets/hk3gtl/changelog.json'


def selected(name):
    return name == RESOURCE or name.endswith('.class') and any(
        name == 'com/sirin/hk3gtl/' + root + '.class'
        or name.startswith('com/sirin/hk3gtl/' + root + '$') for root in CLASSES)


def main():
    candidate = OUT / 'HK3GTL-r269-ae-compat-r270.jar'
    with ZipFile(BASE) as previous, ZipFile(BUILT) as current:
        replacements = {name: current.read(name) for name in current.namelist() if selected(name)}
        changed = []
        with ZipFile(candidate, 'w') as result:
            for entry in previous.infolist():
                data = previous.read(entry)
                updated = replacements.pop(entry.filename, data)
                if updated != data:
                    changed.append(entry.filename)
                result.writestr(entry, updated)
            for name, data in replacements.items():
                result.writestr(current.getinfo(name), data)
    receipt = dict(updated_at=datetime.now().astimezone().isoformat(), revision=270,
        candidate=candidate.relative_to(ROOT).as_posix(), bytes=candidate.stat().st_size,
        sha256=sha256(candidate.read_bytes()).hexdigest(),
        base=BASE.relative_to(ROOT).as_posix(), base_sha256=sha256(BASE.read_bytes()).hexdigest(),
        source_jar_sha256=sha256(BUILT.read_bytes()).hexdigest(), changed_entries=changed,
        source_classes=CLASSES, resources=[RESOURCE],
        source_sha256={name: sha256((ROOT / 'src/main/java/com/sirin/hk3gtl' / (name + '.java')).read_bytes()).hexdigest()
                       for name in CLASSES})
    (OUT / 'packaging-r270.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', 'utf8')
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == '__main__':
    main()
