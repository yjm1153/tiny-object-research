# Independent project rules

This repository is exclusively for the extremely tiny object detection side project.

## Research boundary

- Do not import research claims, experiment IDs, gates, or conclusions from any other repository.
- The current working problem is missed detection of extremely tiny objects, provisionally defined as objects with an effective size of 2–8 pixels.
- The current working model is PRTiny with at most two substantive model changes: PDD and SSR.
- P2, NWD, augmentation, or other known techniques must be treated as baselines or controls unless a task card explicitly promotes them into the method.
- Frequency evidence is a feature-reliability cue in this project; this project does not claim frequency-guided sparse acceleration or counterfactual compute utility.

## Experiment discipline

- Formal experiments require a task card under `experiment_handoffs/tasks/`.
- Results must be written under `experiment_handoffs/results/` and point to raw evidence in `outputs/`.
- Smoke tests prove only code connectivity and tensor shapes, never model effectiveness.
- Use the states `PLANNED`, `SMOKE_ONLY`, `RUNNING`, `MEASURED`, `FAILED`, `BLOCKED`, and `NOT_TESTED`.
- Report latency only when measured on the same GPU, input size, batch size, precision, and runtime protocol.
- Keep datasets, weights, checkpoints, and large logs out of Git.

## Git discipline

- `main` stores reviewed project state.
- Research design branches use `codex/research-<topic>`.
- Experiment branches use `codex/exp-<task-id>`.
- Do not force-push shared branches or commit datasets, weights, checkpoints, or local environments.
