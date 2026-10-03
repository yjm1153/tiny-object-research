"""Synthetic-only SSR prototype, PRT-DEV-001. No detector training is approved.

The agreement rule is a hypothesis, not a calibrated probability. Spatial and
spectral branches share an input and are not statistically independent.
"""

import math

import torch
from torch import nn
from torch.nn import functional as F


def agreement_gate(spatial, spectral):
    """Inputs are sigmoid responses in [0, 1]; both-low is not strong evidence."""
    return spatial * spectral * (1.0 - (spatial - spectral).abs())


def shift_spectral_maps(descriptors):
    """Within-image deterministic misalignment; does not mix batch samples."""
    h, w = descriptors.shape[-2:]
    if h == 1 and w == 1:
        raise ValueError("A 1x1 map cannot provide a spatial misalignment control")
    return torch.roll(descriptors, shifts=(h // 2, w // 2), dims=(-2, -1))


class LocalBandEnergy(nn.Module):
    """4x4 orthonormal DCT, stride 2; three normalized per-channel band maps.

    Energy calculation remains FP32 under autocast. Padding is on the bottom
    and right only; interpolation is fixed and shared by all spectral modes.
    Output order is [all low channels, all mid channels, all high channels].
    """

    def __init__(self, eps=1e-6):
        super().__init__()
        if not math.isfinite(eps) or eps <= 0:
            raise ValueError("eps must be positive and finite")
        self.eps = eps
        n = torch.arange(4, dtype=torch.float32)
        u = torch.arange(4, dtype=torch.float32)[:, None]
        basis = torch.cos(math.pi * (2 * n + 1) * u / 8)
        basis[0] *= 0.5
        basis[1:] *= math.sqrt(0.5)
        filters = torch.einsum("ui,vj->uvij", basis, basis).reshape(16, 1, 4, 4)
        degree = (torch.arange(4)[:, None] + torch.arange(4)).flatten()
        bands = torch.stack((degree <= 1, (degree >= 2) & (degree <= 3), degree >= 4))
        self.register_buffer("filters", filters)
        self.register_buffer("band_weights", bands.float() / bands.sum(1, keepdim=True))

    def forward(self, x):
        if x.ndim != 4 or min(x.shape) < 1 or not x.is_floating_point():
            raise ValueError("Expected a nonempty floating BCHW tensor")
        b, c, h, w = x.shape
        # At least one valid 4x4 window, including each edge pixel.
        ph = max(4 - h, 0) + (h % 2 if h >= 4 else 0)
        pw = max(4 - w, 0) + (w % 2 if w >= 4 else 0)
        with torch.autocast(device_type=x.device.type, enabled=False):
            padded = F.pad(x.float(), (0, pw, 0, ph), mode="replicate")
            coeff = F.conv2d(padded, self.filters.float().repeat(c, 1, 1, 1),
                             stride=2, groups=c)
            coeff = coeff.reshape(b, c, 16, *coeff.shape[-2:])
            energy = torch.einsum("bcnhw,kn->bckhw", coeff.square(), self.band_weights.float())
            normalized = energy / (energy.sum(2, keepdim=True) + self.eps)
            maps = normalized.permute(0, 2, 1, 3, 4).reshape(b, 3 * c, *coeff.shape[-2:])
            maps = F.interpolate(maps, size=(h, w), mode="bilinear", align_corners=False)
        return maps.to(dtype=x.dtype)


class SpatialSpectralRefinement(nn.Module):
    MODES = ("full", "spatial_only", "spatial_matched", "frequency_only",
             "no_agreement", "shuffled_frequency")

    def __init__(self, channels=256, hidden_channels=16, mode="full",
                 layer_scale=1e-3, enabled=True):
        super().__init__()
        if channels < 1 or hidden_channels < 1:
            raise ValueError("Channel counts must be positive")
        if mode not in self.MODES or not math.isfinite(layer_scale):
            raise ValueError("Invalid mode or LayerScale")
        self.channels = channels
        self.mode = mode
        self.enabled = enabled
        d = hidden_channels
        self.project = nn.Conv2d(channels, d, 1)
        self.value = nn.Conv2d(d, d, 3, padding=1, groups=d)
        self.out = nn.Conv2d(d, channels, 1)
        self.alpha = nn.Parameter(torch.full((1, channels, 1, 1), float(layer_scale)))
        self.spatial = None if mode == "frequency_only" else nn.Sequential(
            nn.Conv2d(d, d, 3, padding=1, groups=d), nn.Conv2d(d, d, 1))
        self.spectral = None if mode == "spatial_only" else nn.Conv2d(3 * d, d, 1)
        self.bands = LocalBandEnergy() if mode not in ("spatial_only", "spatial_matched") else None

    def forward(self, x):
        if x.ndim != 4 or x.shape[1] != self.channels or min(x.shape) < 1:
            raise ValueError("Input must match configured nonempty BCHW shape")
        if not self.enabled:
            return x
        z = self.project(x)
        s = torch.sigmoid(self.spatial(z)) if self.spatial is not None else None
        f = None
        if self.spectral is not None:
            if self.mode == "spatial_matched":
                desc = torch.cat((z, F.avg_pool2d(z, 3, stride=1, padding=1),
                                  F.avg_pool2d(z, 5, stride=1, padding=2)), dim=1)
            else:
                desc = self.bands(z)
            if self.mode == "shuffled_frequency":
                desc = shift_spectral_maps(desc)
            f = torch.sigmoid(self.spectral(desc))
        if self.mode == "spatial_only":
            gate = s
        elif self.mode == "frequency_only":
            gate = f
        elif self.mode == "no_agreement":
            gate = 0.5 * (s + f)
        else:
            gate = agreement_gate(s, f)
        delta = self.out(gate * F.silu(self.value(z)))
        return x + self.alpha.to(delta.dtype) * delta


class P2RefinementAdapter(nn.Module):
    """Refine only P2 of an already-built P2..P6 tuple. No MMDet dependency."""

    def __init__(self, channels=256, **ssr_kwargs):
        super().__init__()
        self.channels = channels
        self.ssr = SpatialSpectralRefinement(channels=channels, **ssr_kwargs)

    def forward(self, features):
        if not isinstance(features, (tuple, list)) or len(features) != 5:
            raise ValueError("Expected five pyramid features P2 through P6")
        if features[0].ndim != 4:
            raise ValueError("Expected BCHW feature tensors")
        batch = features[0].shape[0]
        for feat in features:
            if feat.ndim != 4 or feat.shape[1] != self.channels or feat.shape[0] != batch:
                raise ValueError("Pyramid features must share batch and configured channels")
        return (self.ssr(features[0]), *features[1:])
