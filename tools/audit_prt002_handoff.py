"""Read an immutable Git tree; never touch the dataset or old result files."""

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from prtiny.diagnostics.handoff import screen_handoff


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref", default="origin/codex/exp-prt-002-a1")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sha = git("rev-parse", "--verify", "--end-of-options", args.ref + "^{commit}").strip()
    prefix = "outputs/PRT-002-A1/"
    bundle = {"source_commit": sha, "load_errors": [], "runs": {"B1-U": {}, "PDD-U": {}}}

    def read_json(path):
        try:
            return json.loads(git("show", f"{sha}:{path}"))
        except (subprocess.CalledProcessError, json.JSONDecodeError) as exc:
            bundle["load_errors"].append(f"INVALID_OR_MISSING_JSON:{path}:{type(exc).__name__}")
            return {}

    for key, path in {
        "manifest": prefix + "audit/dataset_manifest.json",
        "legacy_manifest": "outputs/PRT-001/data_manifest.json",
        "parameter_audit": prefix + "audit/parameter_update_audit.json",
        "gate_report": prefix + "gate_report.json",
    }.items():
        bundle[key] = read_json(path)
    for path in git("ls-tree", "-r", "--name-only", sha, prefix).splitlines():
        match = re.fullmatch(re.escape(prefix) + r"(B1-U|PDD-U)/seed(\d+)/metrics\.json", path)
        if match:
            bundle["runs"][match[1]][int(match[2])] = read_json(path)
    report = screen_handoff(bundle)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Refuse to overwrite: each screening remains traceable.
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False, allow_nan=False)
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 2 if report["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
