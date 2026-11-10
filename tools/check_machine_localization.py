"""核对已注册机器名称、静态翻译引用及 approvedMachine 动态提示键。

【变更记录 #1】2026-10-26T21:50:54+08:00（修订178）
新增：38个实际注册机器的名称，以及静态Component和动态工业提示覆盖检查。
用途：阻止控制器名称或提示在游戏内退化为原始语言键。
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MACHINE_DIR = ROOT / "src/main/java/com/sirin/hk3gtl/common/machine"
JAVA_DIR = ROOT / "src/main/java"
LANG_DIR = ROOT / "src/main/resources/assets/hk3gtl/lang"


def read_lang(path: Path) -> dict:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"重复语言键：{path.name}: {key}")
            result[key] = value
        return result

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)


def check() -> dict:
    machine_source = "\n".join(p.read_text(encoding="utf-8") for p in MACHINE_DIR.rglob("*.java"))
    names = set()
    for pattern in (
        r'\.multiblock\("([a-z0-9_]+)"', r'\.machine\("([a-z0-9_]+)"',
        r'approvedMachine\("([a-z0-9_]+)"', r'register\("([a-z0-9_]+)"',
        r'collectionUpgrade\("([a-z0-9_]+)"', r'institute\("([a-z0-9_]+)"',
    ):
        names.update(re.findall(pattern, machine_source))
    required = {f"block.hk3gtl.{name}" for name in names}
    dynamic_names = set(re.findall(r'approvedMachine\("([a-z0-9_]+)"', machine_source))
    for name in dynamic_names:
        required.update(f"hk3gtl.machine.{name}.tooltip.{index}" for index in range(2))
    static_keys = set()
    for path in JAVA_DIR.rglob("*.java"):
        source = path.read_text(encoding="utf-8")
        for match in re.finditer(r'Component\.translatable\(\s*"([^"\n]+)"', source):
            if source[match.end():].lstrip().startswith("+"):
                continue  # 动态键由明确生成器单独覆盖。
            key = match.group(1)
            if key.startswith(("hk3gtl.", "block.hk3gtl.", "item.hk3gtl.", "gui.hk3gtl.", "message.hk3gtl.")):
                static_keys.add(key)
    required.update(static_keys)
    missing = {}
    for language in ("zh_cn", "en_us"):
        values = read_lang(LANG_DIR / f"{language}.json")
        missing[language] = sorted(key for key in required if not str(values.get(key, "")).strip())
    return {
        "status": "passed" if not any(missing.values()) else "failed",
        "registered_machines": len(names), "machine_ids": sorted(names),
        "static_keys": len(static_keys), "dynamic_approved_machine_names": sorted(dynamic_names),
        "required_keys_per_language": len(required), "missing": missing,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = check()
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
    print(output)
    raise SystemExit(0 if result["status"] == "passed" else 1)
