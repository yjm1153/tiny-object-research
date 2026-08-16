# PRTiny research brief v0.1

- Status: `PLANNED / NOT_TESTED`
- Target: a model-improvement paper for extremely tiny object detection
- Compute: one RTX 4090D
- Primary failure: missed detection in the 2–8 pixel regime

## Research question

Can an efficient detector reduce extremely tiny object misses by preserving early spatial detail and refining shallow features only when spatial and multi-band spectral evidence are mutually reliable?

## Working model

### Partial Detail-Preserving Downsampling (PDD)

Split channels between a space-to-depth preservation path and a stride-2 depthwise-convolution path, then fuse and compress them. Apply PDD only at the early downsampling locations that feed P2/P3.

### Spatial–Spectral Reliable Refinement (SSR)

Use a lightweight spatial branch and a low/mid/high spectral branch. Construct an agreement gate from their responses and apply residual refinement to shallow high-resolution features. High-frequency response alone must not be treated as target evidence.

## Initial experimental frame

- Primary dataset: AI-TOD-v2.
- Generalization dataset: VisDrone; TinyPerson is optional.
- Development detector: FCOS-R50-FPN-P2.
- Transfer detector: RTMDet-s-P2.
- Primary metrics: AP, AP50, APvt, ARvt, and recall in 2–4, 4–6, 6–8, and 8–16 pixel bins.

## Required controls

1. original detector;
2. P2-only baseline;
3. PDD only;
4. spatial-only refinement;
5. frequency-only refinement;
6. spatial+frequency without agreement;
7. full SSR;
8. shuffled-frequency control;
9. PDD+SSR final model;
10. NWD applied consistently as a separate supervision control.

## Stop conditions

- Drop PDD if it has no stable benefit over a matched P2 baseline.
- Drop the frequency claim if SSR does not outperform a capacity-matched spatial-only module.
- Do not retain more than two substantive model changes in the final method.
- Do not claim generalization without gains on a second dataset or detector.
- Do not claim efficiency from FLOPs alone.
