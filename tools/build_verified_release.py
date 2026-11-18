"""【变更记录 #1】2026-10-26 21:55:20（修订178）
删除：无；新增：逐修订完整构建与源码指纹收据；修改：复用现有部署工具的路径及摘要函数。
用途：构建完成后源码仍须一致，禁止以旧包或局部编译成功冒充本轮完整产物。
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import deploy_late_industrial_20261026 as release


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--revision", type=int, required=True)
    parser.add_argument("--log-dir", type=Path, required=True)
    parser.add_argument("--keep-build-outputs", action="store_true",
                        help="复用生产源码指纹未变的产物，仍运行完整build及check")
    args = parser.parse_args()
    log = args.log_dir.resolve()
    release.require(log.is_relative_to((release.ROOT / "logs").resolve()), "构建收据必须位于项目logs目录")
    log.mkdir(parents=True, exist_ok=True)
    release.LOG = log
    before = release.source_inputs()
    release.save("build-source-inputs.json", before)
    env = dict(os.environ)
    env["JAVA_HOME"] = "C:/Program Files/Java/jdk-17"
    started = datetime.now(timezone.utc).isoformat()
    with (log / "clean-build.log").open("w", encoding="utf-8") as output:
        tasks = (["build"] if args.keep_build_outputs else ["clean", "build"])
        result = subprocess.run(["cmd.exe", "/d", "/c", "gradlew.bat", *tasks, "--offline", "--no-daemon", "--console=plain"],
                                cwd=release.ROOT, env=env, stdout=output, stderr=subprocess.STDOUT)
    after = release.source_inputs()
    same = before == after
    passed = result.returncode == 0 and same and release.base.SOURCE.is_file()
    receipt = {"status": "passed" if passed else "failed", "revision": args.revision,
               "started_at_utc": started, "finished_at_utc": datetime.now(timezone.utc).isoformat(),
               "exit_code": result.returncode, "source_inputs_unchanged": same,
               "clean": not args.keep_build_outputs, "gradle_tasks": tasks,
               "jar_sha256": release.sha(release.base.SOURCE) if release.base.SOURCE.is_file() else None,
               "changed_source_files": [key for key in before.keys() | after.keys() if before.get(key) != after.get(key)]}
    release.save("clean-build.json", receipt)
    print(json.dumps(receipt, ensure_ascii=True))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
