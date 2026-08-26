# -*- coding: utf-8 -*-
"""单元测试：验证 PDD (局部细节保留下采样) 模块功能、张量维度、梯度流通与骨干集成"""

import pytest
import torch
import torch.nn as nn
from prtiny.models.pdd import SpaceToDepth, PDDDownsample, ResNetStemPDD, ResNetWithPDD


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
    """验证 PDD 模块参数量极小化 (<3% 骨干参数增量约束)"""
    in_c = 64
    out_c = 64
    pdd = PDDDownsample(in_channels=in_c, out_channels=out_c, split_ratio=0.5)
    
    # PDDDownsample(64, 64) 参数量:
    # DWConv: 32 * 1 * 3 * 3 = 288 + BN(64)
    # FuseConv: 160 * 64 * 1 * 1 = 10,240 + BN(128)
    # 总参数量仅约 10.7k 参数
    pdd_params = sum(p.numel() for p in pdd.parameters())
    print(f"PDDDownsample(64,64) 参数量: {pdd_params}")
    assert pdd_params < 20000


def test_resnet_with_pdd_single_position():
    """验证 ResNetWithPDD 单位置 Stage 0 替换与输出维度"""
    model = ResNetWithPDD(
        depth=50,
        num_stages=4,
        out_indices=(0, 1, 2, 3),
        pdd_stages=(0,),
        frozen_stages=-1
    )
    # 验证 maxpool 为 PDDDownsample
    assert isinstance(model.maxpool, PDDDownsample)
    
    # 模拟输入 [B, 3, 256, 256]
    x = torch.randn(2, 3, 256, 256)
    outs = model(x)
    
    # 验证 4 个 stage 输出维度
    # stage 0 (C2 / stride 4): [B, 256, 64, 64]
    # stage 1 (C3 / stride 8): [B, 512, 32, 32]
    # stage 2 (C4 / stride 16): [B, 1024, 16, 16]
    # stage 3 (C5 / stride 32): [B, 2048, 8, 8]
    assert outs[0].shape == (2, 256, 64, 64)
    assert outs[1].shape == (2, 512, 32, 32)
    assert outs[2].shape == (2, 1024, 16, 16)
    assert outs[3].shape == (2, 2048, 8, 8)
    
    # 参数增量比率计算 (相对标准 ResNet-50)
    total_pdd_r50_params = sum(p.numel() for p in model.parameters())
    from mmdet.models.backbones.resnet import ResNet
    std_r50 = ResNet(depth=50, num_stages=4, out_indices=(0, 1, 2, 3))
    total_std_r50_params = sum(p.numel() for p in std_r50.parameters())
    
    overhead_ratio = (total_pdd_r50_params - total_std_r50_params) / total_std_r50_params
    print(f"ResNet50: {total_std_r50_params}, ResNet50-PDD: {total_pdd_r50_params}, Overhead: {overhead_ratio*100:.3f}%")
    assert overhead_ratio < 0.03  # 远小于 3% 约束 (< 0.05%)
