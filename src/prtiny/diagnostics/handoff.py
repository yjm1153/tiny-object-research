"""Strict numerical screening of PRT-002-A1, not a replacement for review.

Consumes a bundle of remote-visible JSON. Reported hashes are checked for form
only: actual dataset/checkpoint/prediction bytes are not loaded by this tool.
"""

import math
import re


PRIMARY = ("AP", "APvt_official_1500", "ARvt_2_8_3000")


def screen_handoff(bundle):
    issues = []
    warnings = ["Artifact bytes/logs/predictions were not reevaluated; hash syntax is not verification."]
    means = None
    seed2_required = False
    numeric_pass = False
    if bundle.get("load_errors"):
        issues.extend(bundle["load_errors"])
    manifest = bundle.get("manifest", {})
    expected = {"train": (11214, 650471), "val": (2804, 70424)}
    # The frozen card's conflicting count must not silently be rewritten here.
    legacy = bundle.get("legacy_manifest", {})
    for split, (images, instances) in expected.items():
        row = manifest.get("splits", {}).get(split, {})
        if row.get("image_count") != images or row.get("instance_count") != instances:
            issues.append(f"DATA_COUNT_CONFLICT:{split}")
        if row.get("conforms_to_prt001_a1_spec") is not True:
            issues.append(f"DATA_SPEC_NOT_CONFIRMED:{split}")
        sha = row.get("annotation_sha256")
        old = legacy.get("file_hashes", {}).get(split, {}).get("sha256")
        if not isinstance(sha, str) or not re.fullmatch(r"[a-fA-F0-9]{64}", sha) or sha != old:
            issues.append(f"DATA_HASH_UNCONFIRMED:{split}")
    if manifest.get("audit_passed") is not True:
        issues.append("AUDIT_NOT_PASSED")

    audited = bundle.get("parameter_audit", {})
    for name in ("B1-F1", "PDD-F1", "B1-U", "PDD-U"):
        if name not in audited:
            issues.append(f"PARAMETER_CONFIG_MISSING:{name}")
    warnings.append("Stem audits require exact module paths and the actual training optimizer/loss.")

    runs = bundle.get("runs", {})
    b_runs, p_runs = runs.get("B1-U", {}), runs.get("PDD-U", {})
    if set(b_runs) != set(p_runs):
        issues.append("UNPAIRED_SEEDS")
    seeds = sorted(set(b_runs) & set(p_runs))
    if seeds not in ([0, 1], [0, 1, 2]):
        issues.append("INCOMPLETE_OR_UNEXPECTED_SEEDS")
    deltas = []
    for seed in seeds:
        values = []
        for name, records in (("B1-U", b_runs), ("PDD-U", p_runs)):
            row = records[seed]
            if row.get("task_id") != "PRT-002-A1" or row.get("model") != name or row.get("seed") != seed:
                issues.append(f"RUN_IDENTITY_INVALID:{name}:seed{seed}")
            for field in ("checkpoint_sha256", "prediction_json_sha256", "config_sha256"):
                sha = row.get(field)
                if not isinstance(sha, str) or not re.fullmatch(r"[a-fA-F0-9]{64}", sha):
                    issues.append(f"HASH_INVALID:{name}:seed{seed}:{field}")
            m = row.get("metrics", {})
            vals = [m.get(key) for key in PRIMARY]
            valid = all(isinstance(v, (int, float)) and not isinstance(v, bool)
                        and math.isfinite(v) and 0 <= v <= 1 for v in vals)
            if not valid:
                issues.append(f"METRIC_MISSING_OR_INVALID:{name}:seed{seed}")
                values.append(None)
                continue
            if vals[0] == 0 or (vals[1] == 0 and vals[2] == 0):
                issues.append(f"DEGENERATE_RUN_REQUIRES_DIAGNOSIS:{name}:seed{seed}")
            values.append(vals)
        if all(v is not None for v in values):
            deltas.append([p - b for b, p in zip(values[0], values[1])])

    if seeds and len(deltas) == len(seeds):
        means = dict(zip(PRIMARY, [sum(row[i] for row in deltas) / len(deltas) for i in range(3)]))
        n = len(seeds)
        positives = [sum(row[i] > 0 for row in deltas) for i in range(3)]
        # Frozen card: OR, two-seed all positive; three-seed at least 2/3.
        min_positive = 2
        numeric_pass = n >= 2 and means["AP"] >= -0.002 and (
            (means[PRIMARY[1]] >= 0.005 and positives[1] >= min_positive)
            or (means[PRIMARY[2]] >= 0.010 and positives[2] >= min_positive))
        if n == 2:
            conflicting = any(deltas[0][i] * deltas[1][i] < 0 for i in (1, 2))
            gray = ((0 < means[PRIMARY[1]] < 0.007) or (0 < means[PRIMARY[2]] < 0.012))
            clear_failure = (means["AP"] < -0.005 or
                             (means[PRIMARY[1]] <= 0 and means[PRIMARY[2]] <= 0))
            seed2_required = conflicting or (gray and not clear_failure)
            if seed2_required:
                issues.append("SEED2_REQUIRED_BEFORE_CONCLUSION")
        if not numeric_pass:
            issues.append("NUMERIC_KEEP_CRITERION_NOT_MET")
    submitted = bundle.get("gate_report", {})
    gate_pass = submitted.get("gate_checks", {}).get("Gate_B_two_seed_decision", {}).get("passed")
    if gate_pass and issues:
        warnings.append("Submitted Gate B pass does not close the prerequisite/seed conflicts.")
    return {
        "task_id": "PRT-DEV-001",
        "screened_task_id": "PRT-002-A1",
        "source_commit": bundle.get("source_commit"),
        "status": "BLOCKED" if issues else "NUMERIC_SCREEN_ONLY",
        "formal_release_authorized": False,
        "issues": sorted(set(issues)), "warnings": warnings,
        "paired_seeds": seeds, "mean_deltas": means,
        "numeric_keep_criterion_met": numeric_pass,
        "seed2_required": seed2_required,
    }
