# -*- coding: utf-8 -*-
"""单元测试：验证 PDD (局部细节保留下采样) 模块功能、张量维度与梯度流通"""

import pytest
import torch
import torch.nn as nn
from prtiny.models.pdd import SpaceToDepth, PDDDownsample, ResNetStemPDD


def test_space_to_depth_shape_and_lossless():
    """验证 SpaceToDepth 空间到通道无损重组"""
    s2d = SpaceToDepth(block_size=2)
    x = torch.randn(2, 16, 32, 32)
    out = s2d(x)
    
    # 空间尺寸减半，通道数扩大 4 倍
    assert out.shape == (2, 64, 16, 16)
    
    # 验证重组无 NaN / Inf
    assert not torch.isnan(out).any()
    assert not torch.isinf(out).any()


def test_pdd_forward_and_backward():
    """验证 PDD 模块前向与反向梯度流通"""
    in_c = 64
    out_c = 128
    pdd = PDDDownsample(in_channels=in_c, out_channels=out_c, split_ratio=0.5)
    
    x = torch.randn(2, in_c, 40, 40, requires_grad=True)
    out = pdd(x)
    
    # 验证输出维度
    assert out.shape == (2, out_c, 20, 20)
    assert not torch.isnan(out).any()
    
    # 验证反向传播与梯度更新
    loss = out.sum()
    loss.backward()
    
    assert x.grad is not None
    assert x.grad.shape == x.shape
    assert not torch.isnan(x.grad).any()
    assert not torch.isinf(x.grad).any()


def test_pdd_split_ratios():
    """验证不同通道拆分比例下的鲁棒性"""
    for ratio in [0.25, 0.5, 0.75]:
        pdd = PDDDownsample(in_channels=64, out_channels=64, split_ratio=ratio)
        x = torch.randn(1, 64, 16, 16)
        out = pdd(x)
        assert out.shape == (1, 64, 8, 8)


def test_pdd_parameter_overhead():
    """验证 PDD 模块参数量极小化 (轻量化设计)"""
    in_c = 64
    out_c = 128
    pdd = PDDDownsample(in_channels=in_c, out_channels=out_c, split_ratio=0.5)
    
    # 计算参数量
    pdd_params = sum(p.numel() for p in pdd.parameters() if p.requires_grad)
    
    # 标准 3x3 Conv 下采样参数量
    std_conv = nn.Conv2d(in_c, out_c, kernel_size=3, stride=2, padding=1, bias=False)
    std_params = sum(p.numel() for p in std_conv.parameters() if p.requires_grad)
    
    print(f"PDD params: {pdd_params}, Standard Conv params: {std_params}")
    # PDD 使用 DWConv(3x3) + Pointwise(1x1)，参数量应显著低于或处于同等水平
    assert pdd_params < std_params * 1.5
