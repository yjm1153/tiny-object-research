# PRT-DEV-001 module prototype

This directory has no detector training config. The original PDD is unchanged;
SSR is a synthetic-only candidate under the versioned task card. The main control
is `spatial_matched` (equal trainable parameter count), not `spatial_only`.

From this worktree, with PyTorch and pytest available:

```powershell
python -m pytest tests/test_ssr.py tests/test_handoff_diagnostics.py tests/test_pdd.py -q
python tools/smoke_prtiny_modules.py --device cpu --output outputs/PRT-DEV-001/smoke_cpu.json
python tools/audit_prt002_handoff.py --ref origin/codex/exp-prt-002-a1 --output outputs/PRT-DEV-001/handoff_screen.json
```

The audit exits 2 if evidence conflicts are found (expected for the current
PRT-002-A1 handoff). It never emits a research release. Output files are created
exclusively; choose a new name for reruns rather than overwrite evidence.

`P2RefinementAdapter` accepts a synthetic or already-computed five-level feature
tuple. It is not registered into an MMDetection FPN yet. Detector integration,
AP, generalization and latency remain NOT_TESTED. No pretrained weights or data
are required; smoke must not be interpreted as detection evidence.
