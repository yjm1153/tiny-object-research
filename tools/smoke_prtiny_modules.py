"""PRT-DEV-001: synthetic module checks only; no dataset or detector training."""

import argparse
import importlib.util
import json
from pathlib import Path
import platform
import subprocess
import sys

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from prtiny.models import PDDDownsample, P2RefinementAdapter, SpatialSpectralRefinement


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/prototypes/prtiny_modules.json")
    args = parser.parse_args()
    torch.set_num_threads(2)
    torch.manual_seed(37)
    config = json.loads(args.config.read_text(encoding="utf-8"))
    if config.get("formal_training_authorized") is not False:
        raise ValueError("This runner is synthetic-only")
    if args.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable; no fabricated GPU smoke")
    device = torch.device(args.device)
    pdd = PDDDownsample(**config["pdd"]).to(device)
    x = torch.randn(2, 64, 35, 37, device=device, requires_grad=True)
    pdd_out = pdd(x)
    pdd_out.square().mean().backward()
    assert pdd_out.shape == (2, 64, 18, 19)
    assert x.grad is not None and torch.isfinite(x.grad).all()
    mode_records = {}
    for mode in SpatialSpectralRefinement.MODES:
        kwargs = dict(config["ssr"], mode=mode)
        layer = SpatialSpectralRefinement(**kwargs).to(device)
        opt = torch.optim.SGD(layer.parameters(), lr=.1)
        sample = torch.randn(1, 256, 19, 21, device=device, requires_grad=True)
        before = layer.out.weight.detach().clone()
        result = layer(sample)
        (result - torch.randn_like(result)).square().mean().backward()
        all_finite = all(p.grad is not None and torch.isfinite(p.grad).all().item() for p in layer.parameters())
        opt.step()
        updated = not torch.equal(layer.out.weight, before)
        assert all_finite and updated and torch.isfinite(result).all()
        mode_records[mode] = {"parameters": sum(p.numel() for p in layer.parameters()),
                              "finite_gradients": all_finite, "optimizer_updated_output": updated}
    assert mode_records["full"]["parameters"] == mode_records["spatial_matched"]["parameters"]
    adapter = P2RefinementAdapter(**config["ssr"]).to(device)
    pyramid = tuple(torch.randn(1, 256, h, h, device=device) for h in (32, 16, 8, 4, 2))
    refined = adapter(pyramid)
    assert all(refined[i] is pyramid[i] for i in range(1, 5))
    report = {
        "task_id": "PRT-DEV-001", "status": "SMOKE_ONLY", "review_status": "READY_FOR_REVIEW",
        "run_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source_dirty": bool(subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT, text=True).strip()),
        "python": platform.python_version(), "torch": torch.__version__, "device": str(device),
        "gpu": torch.cuda.get_device_name(device) if device.type == "cuda" else None,
        "mmdet_installed": importlib.util.find_spec("mmdet") is not None,
        "config": config, "seed": 37, "pdd_output_shape": list(pdd_out.shape),
        "modes": mode_records, "p3_to_p6_unchanged": True,
        "detector_integration": "NOT_TESTED", "AP": "NOT_TESTED", "latency": "NOT_TESTED",
        "dataset_accessed": False, "formal_training_authorized": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, allow_nan=False)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
