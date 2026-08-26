# Tiny Object Research

Independent research repository for extremely tiny object detection.

## Current direction

Working model: **PRTiny — Detail-Preserving Downsampling and Spatial–Spectral Reliable Refinement**.

The project targets missed detections of extremely tiny objects, especially the 2–8 pixel regime. The current model hypothesis combines:

1. partial detail-preserving downsampling (PDD) to reduce irreversible early information loss;
2. spatial–spectral reliable refinement (SSR) on shallow high-resolution features;
3. systematic per-size evaluation and matched-compute controls.

Research status: `PLANNED / NOT_TESTED`.

> This line records the original brief status. For the current reviewed state,
> use `docs/memory/CURRENT_STATE.md` or the generated dashboard below.

## Research progress dashboard

Open `dashboard/index.html` for a repository-native view of the roadmap,
reviewed metrics, evidence boundaries, blockers, next actions, and Git handoff
state. Refresh it from authoritative repository files with:

```powershell
python tools/build_research_dashboard.py --fetch
```

The dashboard is read-only and does not turn an experiment-agent report into a
research conclusion. See `dashboard/README.md` for its source and drift rules.

## Independence boundary

This repository is independent from the frequency-routing mainline project. It does not inherit that project's datasets, model constraints, task IDs, gates, utility targets, experimental conclusions, or Git history.

## Repository layout

- `docs/`: research brief, paper lineage, and decisions;
- `docs/memory/`: versioned project context, evidence ledger, and new-Codex bootstrap;
- `governance/`: research-agent and experiment-agent authority, handoff, and Git rules;
- `research/reviews/`: immutable design and result review records from the research agent;
- `experiment_handoffs/tasks/`: approved experiment task cards;
- `experiment_handoffs/results/`: evidence-backed result reports;
- `configs/`: model, dataset, and training configurations;
- `src/`: implementation code;
- `tests/`: unit and smoke tests;
- `data/`: local dataset links or instructions only;
- `outputs/`: local logs, checkpoints, metrics, and figures.

## Immediate next step

Review and merge the role-separated governance branch, then rebase the PRT-001 experiment branch onto the governed `main`. PDD and SSR remain locked until PRT-001 is formally reviewed and passed.

## New Codex project

Open `D:\研究\tiny-object-research` as the workspace and begin with `docs/memory/START_HERE.md`. Repository files are authoritative over old chats or global memory.
