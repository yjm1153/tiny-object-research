# Paper-to-method lineage v0.1

This document records technical migration rather than ownership of the original methods.

| Problem node | Source line | Transfer into PRTiny | Boundary |
|---|---|---|---|
| Early information loss | SPD-Conv; QueryDet | partial detail-preserving downsampling near P2/P3 | no wholesale architecture replacement |
| Background spectral interference | SET | spatial–spectral agreement instead of high-frequency thresholding | no claim that high frequency equals tiny objects |
| Scale-dependent spectrum | SFDNet | low/mid/high spectral descriptors | no dense spectrum-disentanglement stack by default |
| Spatial/frequency selection | SFS-DETR; FcaNet | lightweight spatial branch and spectral descriptor | matched spatial-only control is mandatory |
| Coarse-to-fine recovery | QueryDet; SEF-DETR; UHR-DETR | optional local recheck extension after the base model is validated | not part of v0.1 core model |
| Routing stability | YOLO-Master; SPAR-Det | optional soft-to-hard selection and reliability statistics | no sparse-acceleration claim |
| Tiny-box supervision | NWD-RKA | common loss/assignment control | not counted as a model contribution |
| Efficiency evidence | YOLO-ULM | same-hardware latency and memory protocol | published latency numbers are not directly comparable |

## Main narrative

PRTiny follows a preserve-then-refine paradigm: preserve weak evidence before it is irreversibly destroyed, then enhance shallow features only when complementary spatial and spectral cues agree.
