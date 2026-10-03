import io

import pytest
import torch

from prtiny.models.ssr import (LocalBandEnergy, P2RefinementAdapter,
                               SpatialSpectralRefinement, agreement_gate,
                               shift_spectral_maps)


def test_dct_orthonormal_and_frequency_fixtures():
    bands = LocalBandEnergy()
    basis = bands.filters.reshape(16, 16)
    torch.testing.assert_close(basis @ basis.T, torch.eye(16), atol=1e-6, rtol=1e-6)
    dc = bands(torch.ones(1, 1, 8, 8))
    assert dc[:, 0].min() > 0.999
    assert dc[:, 1:].abs().max() < 1e-8
    high_patch = bands.filters[15, 0].reshape(1, 1, 4, 4)
    assert bands(high_patch)[:, 2].min() > 0.999
    assert torch.equal(bands(torch.zeros(1, 2, 5, 7)), torch.zeros(1, 6, 5, 7))


def test_hand_computed_gate_and_both_low_rejection():
    a = torch.tensor([1.0, 1.0, 0.0, 0.2, 0.8])
    b = torch.tensor([1.0, 0.0, 0.0, 0.2, 0.5])
    torch.testing.assert_close(agreement_gate(a, b), torch.tensor([1., 0., 0., .04, .28]))


@pytest.mark.parametrize("shape", [(1, 8, 1, 1), (1, 8, 2, 3), (2, 8, 9, 11), (2, 8, 16, 16)])
@pytest.mark.parametrize("mode", SpatialSpectralRefinement.MODES)
def test_shapes_finite_gradients_and_actual_update(shape, mode):
    torch.manual_seed(19)
    layer = SpatialSpectralRefinement(8, 4, mode=mode)
    x = torch.randn(shape, requires_grad=True)
    if mode == "shuffled_frequency" and shape[-2:] == (1, 1):
        with pytest.raises(ValueError, match="1x1"):
            layer(x)
        return
    before = layer.out.weight.detach().clone()
    opt = torch.optim.SGD(layer.parameters(), lr=0.1)
    y = layer(x)
    assert y.shape == x.shape and torch.isfinite(y).all()
    (y - torch.randn_like(y)).square().mean().backward()
    assert torch.isfinite(x.grad).all()
    for name, p in layer.named_parameters():
        assert p.grad is not None, name
        assert torch.isfinite(p.grad).all(), name
    opt.step()
    assert not torch.equal(before, layer.out.weight)


def test_disabled_identity_and_zero_scale_identity():
    x = torch.randn(2, 8, 9, 11)
    assert SpatialSpectralRefinement(8, enabled=False)(x) is x
    y = SpatialSpectralRefinement(8, layer_scale=0)(x)
    assert torch.equal(x, y)


def test_spatial_matched_capacity_and_active_parameters():
    full = SpatialSpectralRefinement(8, 4, mode="full")
    matched = SpatialSpectralRefinement(8, 4, mode="spatial_matched")
    assert sum(p.numel() for p in full.parameters()) == sum(p.numel() for p in matched.parameters())
    assert full is not matched
    for module in (full, matched):
        module(torch.randn(2, 8, 9, 11)).square().mean().backward()
        assert all(p.grad is not None and p.grad.abs().sum() > 0 for p in module.parameters())


def test_shuffle_preserves_values_and_changes_correspondence_single_image():
    x = torch.arange(105.).reshape(1, 3, 5, 7)
    shifted = shift_spectral_maps(x)
    assert not torch.equal(x, shifted)
    torch.testing.assert_close(x.flatten().sort().values, shifted.flatten().sort().values)
    torch.manual_seed(123)
    full = SpatialSpectralRefinement(8, 4, layer_scale=1)
    control = SpatialSpectralRefinement(8, 4, mode="shuffled_frequency", layer_scale=1)
    control.load_state_dict(full.state_dict())
    sample = torch.randn(1, 8, 15, 17)
    assert (full(sample) - control(sample)).abs().max() > 1e-6


def test_pyramid_passthrough_and_serialization():
    module = P2RefinementAdapter(8, hidden_channels=4)
    feats = tuple(torch.randn(2, 8, h, h) for h in (32, 16, 8, 4, 2))
    out = module(feats)
    assert all(out[i] is feats[i] for i in range(1, 5))
    assert out[0].shape == feats[0].shape
    stream = io.BytesIO()
    torch.save(module.state_dict(), stream)
    stream.seek(0)
    independent = P2RefinementAdapter(8, hidden_channels=4)
    independent.load_state_dict(torch.load(stream, weights_only=True))
    torch.testing.assert_close(independent(feats)[0], out[0], atol=0, rtol=0)
    with pytest.raises(ValueError):
        module(feats[:4])


def test_cpu_autocast_preserves_finite_band_gradients():
    module = SpatialSpectralRefinement(8, 4)
    x = torch.randn(1, 8, 9, 11, requires_grad=True)
    with torch.autocast("cpu", dtype=torch.bfloat16):
        y = module(x)
    y.square().mean().backward()
    assert torch.isfinite(y).all() and torch.isfinite(x.grad).all()


def test_constructor_rejects_invalid_mode():
    with pytest.raises(ValueError):
        SpatialSpectralRefinement(mode="unknown")
    with pytest.raises(ValueError):
        LocalBandEnergy(eps=0)
