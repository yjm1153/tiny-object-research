import copy
import pytest

from prtiny.diagnostics.handoff import screen_handoff


def bundle():
    sha = "a" * 64
    data = {
        "manifest": {"audit_passed": True, "splits": {
            "train": {"image_count": 11214, "instance_count": 650471,
                      "conforms_to_prt001_a1_spec": True, "annotation_sha256": sha},
            "val": {"image_count": 2804, "instance_count": 70424,
                    "conforms_to_prt001_a1_spec": True, "annotation_sha256": sha}}},
        "legacy_manifest": {"file_hashes": {s: {"sha256": sha} for s in ("train", "val")}},
        "parameter_audit": {n: {} for n in ("B1-F1", "PDD-F1", "B1-U", "PDD-U")},
        "runs": {"B1-U": {}, "PDD-U": {}},
    }
    for name in data["runs"]:
        for seed in (0, 1):
            delta = 0.02 if name == "PDD-U" else 0
            data["runs"][name][seed] = {
                "task_id": "PRT-002-A1", "model": name, "seed": seed,
                "checkpoint_sha256": sha, "prediction_json_sha256": sha, "config_sha256": sha,
                "metrics": {k: .1 + delta for k in ("AP", "APvt_official_1500", "ARvt_2_8_3000")},
            }
    return data


def test_clean_synthetic_evidence_is_never_formal_release():
    report = screen_handoff(bundle())
    assert report["status"] == "NUMERIC_SCREEN_ONLY"
    assert report["numeric_keep_criterion_met"]
    assert not report["formal_release_authorized"]


@pytest.mark.parametrize("value", [None, float("nan"), float("inf"), -1, True, "0.12"])
def test_invalid_metrics_are_not_default_zero(value):
    b = bundle()
    b["runs"]["B1-U"][0]["metrics"]["AP"] = value
    report = screen_handoff(b)
    assert report["status"] == "BLOCKED"
    assert any("METRIC_MISSING_OR_INVALID" in issue for issue in report["issues"])
    assert report["mean_deltas"] is None


def test_real_failure_pattern_blocks_despite_positive_deltas():
    b = bundle()
    b["manifest"]["splits"]["train"]["instance_count"] = 282580
    b["manifest"]["splits"]["train"]["conforms_to_prt001_a1_spec"] = False
    b["parameter_audit"].pop("PDD-F1")
    for seed, apvt in ((0, .0097), (1, .0027)):
        b["runs"]["B1-U"][seed]["metrics"] = {"AP": 7e-7, "APvt_official_1500": 0., "ARvt_2_8_3000": 0.}
        b["runs"]["PDD-U"][seed]["metrics"] = {"AP": .03, "APvt_official_1500": apvt, "ARvt_2_8_3000": .005}
        b["runs"]["B1-U"][seed]["task_id"] = "PRT-001-A1"
    report = screen_handoff(b)
    assert report["numeric_keep_criterion_met"]  # OR criterion, not AND.
    assert report["seed2_required"]
    assert report["status"] == "BLOCKED"
    for tag in ("DATA_COUNT_CONFLICT", "DATA_SPEC_NOT_CONFIRMED", "PARAMETER_CONFIG_MISSING",
                "RUN_IDENTITY_INVALID", "DEGENERATE_RUN", "SEED2_REQUIRED"):
        assert any(tag in issue for issue in report["issues"])


def test_three_seeds_use_two_of_three_not_all_positive():
    b = bundle()
    for name in b["runs"]:
        b["runs"][name][2] = copy.deepcopy(b["runs"][name][0])
        b["runs"][name][2]["seed"] = 2
    b["runs"]["PDD-U"][2]["metrics"] = {"AP": .1, "APvt_official_1500": .09, "ARvt_2_8_3000": .1}
    report = screen_handoff(b)
    assert report["numeric_keep_criterion_met"]
    assert not report["seed2_required"]


def test_empty_or_unpaired_evidence_blocks():
    assert screen_handoff({})["status"] == "BLOCKED"
    b = bundle()
    del b["runs"]["PDD-U"][1]
    assert "UNPAIRED_SEEDS" in screen_handoff(b)["issues"]
