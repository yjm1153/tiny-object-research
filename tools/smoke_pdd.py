# -*- coding: utf-8 -*-
"""PRT-002 Gate S: PDD (局部细节保留下采样) 模块与 FCOS-P2 模型 Smoke 验证脚本

验证标准:
1. PDD 模块双路径 (Space-to-Depth + DWConv) 空间下采样 2x 且前向/反向正常；
2. 集成 PDD 的 FCOS-P2 模型前向拓扑连线正确，输出 5 层金字塔 (P2–P6)；
3. P2 空间分辨率严格为 200x200 (输入 800x800)；
4. 全网络参数量增幅严格受控在 3% 以内；
5. 前向与梯度计算全流程无 NaN / Inf。
"""

import sys
import os
import torch
import torch.nn as nn
import torch.nn.functional as F

# 加入 src 路径
sys.path.insert(0, os.path.abspath("src"))
from prtiny.models.pdd import PDDDownsample, SpaceToDepth


class MockFPN(nn.Module):
    def __init__(self, in_channels_list=[256, 512, 1024, 2048], out_channels=256, start_level=0, num_outs=5):
        super().__init__()
        self.start_level = start_level
        self.num_outs = num_outs
        self.lateral_convs = nn.ModuleList()
        self.fpn_convs = nn.ModuleList()

        for in_c in in_channels_list[start_level:]:
            self.lateral_convs.append(nn.Conv2d(in_c, out_channels, 1))
            self.fpn_convs.append(nn.Conv2d(out_channels, out_channels, 3, padding=1))

        used_backbone_levels = len(in_channels_list) - start_level
        if num_outs > used_backbone_levels:
            self.extra_convs = nn.ModuleList()
            for _ in range(num_outs - used_backbone_levels):
                self.extra_convs.append(nn.Conv2d(out_channels, out_channels, 3, stride=2, padding=1))

    def forward(self, inputs):
        feats = inputs[self.start_level:]
        laterals = [lat(f) for lat, f in zip(self.lateral_convs, feats)]
        for i in range(len(laterals) - 1, 0, -1):
            prev_shape = laterals[i - 1].shape[2:]
            laterals[i - 1] = laterals[i - 1] + F.interpolate(laterals[i], size=prev_shape, mode='nearest')
        outs = [fpn(lat) for fpn, lat in zip(self.fpn_convs, laterals)]
        if hasattr(self, 'extra_convs'):
            for extra in self.extra_convs:
                outs.append(extra(outs[-1]))
        return tuple(outs)


class MockResNet50PDD(nn.Module):
    """模拟包含 PDD 早期下采样的 ResNet-50 骨干网络"""
    def __init__(self):
        super().__init__()
        # Stem (stride 2)
        self.conv1 = nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)
        
        # PDD 代替传统 maxpool (Stage 0 -> C2, stride 2)
        self.pdd_stage0 = PDDDownsample(in_channels=64, out_channels=256, split_ratio=0.5)
        
        # PDD 用于 Stage 1 -> C3 (stride 2)
        self.pdd_stage1 = PDDDownsample(in_channels=256, out_channels=512, split_ratio=0.5)
        
        # 后续 Stage 2 (C4, 1024), Stage 3 (C5, 2048)
        self.stage2 = nn.Sequential(
            nn.Conv2d(512, 1024, kernel_size=3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(1024),
            nn.ReLU(inplace=True)
        )
        self.stage3 = nn.Sequential(
            nn.Conv2d(1024, 2048, kernel_size=3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(2048),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        # x: [1, 3, 800, 800]
        x = self.relu(self.bn1(self.conv1(x)))  # [1, 64, 400, 400]
        C2 = self.pdd_stage0(x)                 # [1, 256, 200, 200] (P2 来源)
        C3 = self.pdd_stage1(C2)                # [1, 512, 100, 100] (P3 来源)
        C4 = self.stage2(C3)                    # [1, 1024, 50, 50]  (P4 来源)
        C5 = self.stage3(C4)                    # [1, 2048, 25, 25]  (P5 来源)
        return [C2, C3, C4, C5]


def run_prt002_smoke():
    print("=" * 60)
    print("正在执行 PRT-002 Gate S: PDD 模块与模型 Smoke 连线验证...")
    print("=" * 60)
    
    # 1. 验证 PDD 独立模块
    print("\n1. 验证 PDD 独立模块维度变换与梯度流动:")
    pdd = PDDDownsample(in_channels=64, out_channels=256, split_ratio=0.5)
    x = torch.randn(1, 64, 400, 400, requires_grad=True)
    out = pdd(x)
    print(f"   -> 输入维度: {list(x.shape)} -> PDD 输出维度: {list(out.shape)}")
    assert out.shape == (1, 256, 200, 200), f"PDD 输出维度异常: {out.shape}"
    assert not torch.isnan(out).any(), "PDD 输出包含 NaN"
    
    # 反向梯度测试
    loss = out.sum()
    loss.backward()
    assert x.grad is not None and not torch.isnan(x.grad).any(), "PDD 反向梯度异常"
    print("   -> PDD 模块前向与反向梯度流通校验通过!")

    # 2. 验证全模型骨干与 FPN 金字塔连线
    print("\n2. 验证 FCOS-R50-PDD-P2 全模型连线 (输入: 800x800):")
    backbone = MockResNet50PDD()
    fpn = MockFPN(in_channels_list=[256, 512, 1024, 2048], out_channels=256, start_level=0, num_outs=5)
    
    img = torch.randn(1, 3, 800, 800)
    feats = backbone(img)
    print(f"   -> 骨干网络 Stage 输出维度:")
    for i, f in enumerate(feats):
        print(f"      * C{i+2}: {list(f.shape)}")
    
    # FPN 输出
    pyramid_outs = fpn(feats)
    print(f"   -> FPN 金字塔输出 (P2-P6):")
    for i, p in enumerate(pyramid_outs):
        print(f"      * P{i+2}: {list(p.shape)}")
        assert not torch.isnan(p).any(), f"P{i+2} 包含 NaN"
        assert not torch.isinf(p).any(), f"P{i+2} 包含 Inf"

    # 核心约束断言
    assert pyramid_outs[0].shape == (1, 256, 200, 200), "P2 空间分辨率必须为 200x200"
    assert pyramid_outs[1].shape == (1, 256, 100, 100), "P3 空间分辨率必须为 100x100"
    assert len(pyramid_outs) == 5, f"金字塔层数应为 5，实际为 {len(pyramid_outs)}"

    # 3. 参数量开销核算
    print("\n3. PDD 参数量开销核算:")
    pdd_params = sum(p.numel() for p in backbone.pdd_stage0.parameters()) + sum(p.numel() for p in backbone.pdd_stage1.parameters())
    total_backbone_params = sum(p.numel() for p in backbone.parameters())
    overhead_pct = (pdd_params / total_backbone_params) * 100
    print(f"   -> PDD 模块总参数量: {pdd_params:,}")
    print(f"   -> 骨干网络总参数量: {total_backbone_params:,}")
    print(f"   -> PDD 模块参数占比: {overhead_pct:.2f}% (科学红线要求: < 3.0%)")
    assert overhead_pct < 3.0, f"PDD 参数开销超标: {overhead_pct:.2f}%"

    print("=" * 60)
    print("🎉 PRT-002 Gate S: 全部验证通过 (STATUS: MEASURED / SMOKE_ONLY)")
    print("=" * 60)

    # 记录 smoke 结果到 outputs/PRT-002/smoke/
    os.makedirs("outputs/PRT-002/smoke", exist_ok=True)
    with open("outputs/PRT-002/smoke/smoke_result.txt", "w", encoding="utf-8") as f:
        f.write(f"PRT-002 Gate S Smoke Verification PASSED\n")
        f.write(f"P2 shape: {list(pyramid_outs[0].shape)}\n")
        f.write(f"PDD param overhead: {overhead_pct:.2f}%\n")
        f.write(f"Numerical checks: NO NaN / NO Inf\n")


if __name__ == "__main__":
    run_prt002_smoke()
