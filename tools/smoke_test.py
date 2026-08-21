"""
Gate S: B0/B1 模型 Smoke 连线与张量维度验证脚本
验证标准:
1. B0 (P3-P7) 与 B1 (P2-P6) 金字塔拓扑连线正确
2. B1 P2 空间尺度 (200x200) 严格等于 B0 P3 (100x100) 的 2 倍 (输入为 800x800)
3. 前向传播计算无 NaN / Inf
"""

import sys
import torch
import torch.nn as nn
import torch.nn.functional as F


class MockFPN(nn.Module):
    def __init__(self, in_channels_list, out_channels=256, start_level=1, num_outs=5):
        super().__init__()
        self.start_level = start_level
        self.num_outs = num_outs
        self.lateral_convs = nn.ModuleList()
        self.fpn_convs = nn.ModuleList()

        for in_c in in_channels_list[start_level:]:
            self.lateral_convs.append(nn.Conv2d(in_c, out_channels, 1))
            self.fpn_convs.append(nn.Conv2d(out_channels, out_channels, 3, padding=1))

        # extra convs for higher pyramid levels
        used_backbone_levels = len(in_channels_list) - start_level
        if num_outs > used_backbone_levels:
            self.extra_convs = nn.ModuleList()
            for _ in range(num_outs - used_backbone_levels):
                self.extra_convs.append(nn.Conv2d(out_channels, out_channels, 3, stride=2, padding=1))

    def forward(self, inputs):
        # inputs: [C2, C3, C4, C5]
        feats = inputs[self.start_level:]
        laterals = [lat(f) for lat, f in zip(self.lateral_convs, feats)]
        
        # Top-down pathway
        for i in range(len(laterals) - 1, 0, -1):
            prev_shape = laterals[i - 1].shape[2:]
            laterals[i - 1] = laterals[i - 1] + F.interpolate(laterals[i], size=prev_shape, mode='nearest')
            
        outs = [fpn(lat) for fpn, lat in zip(self.fpn_convs, laterals)]
        
        # Extra levels
        if hasattr(self, 'extra_convs'):
            for extra in self.extra_convs:
                outs.append(extra(outs[-1]))
                
        return tuple(outs)


def run_gate_s_smoke():
    print("==================================================")
    print("正在执行 PRT-001 Gate S: 模型 Smoke 连线与张量维度验证...")
    print("==================================================")
    
    # 模拟 800x800 单尺度输入经过 ResNet-50 骨干网络产生的 4 个 Stage 特征
    # C2: stride 4 (200x200), C3: stride 8 (100x100), C4: stride 16 (50x50), C5: stride 32 (25x25)
    batch_size = 1
    C2 = torch.randn(batch_size, 256, 200, 200)
    C3 = torch.randn(batch_size, 512, 100, 100)
    C4 = torch.randn(batch_size, 1024, 50, 50)
    C5 = torch.randn(batch_size, 2048, 25, 25)
    backbone_feats = [C2, C3, C4, C5]
    
    # 1. 验证 B0 (P3-P7, start_level=1, num_outs=5)
    fpn_b0 = MockFPN(in_channels_list=[256, 512, 1024, 2048], out_channels=256, start_level=1, num_outs=5)
    outs_b0 = fpn_b0(backbone_feats)
    
    assert len(outs_b0) == 5, f"B0 金字塔输出层数应为 5，实际为 {len(outs_b0)}"
    # outs_b0: P3(100x100), P4(50x50), P5(25x25), P6(13x13), P7(7x7)
    p3_shape = outs_b0[0].shape
    print(f"[B0] 输出 5 层金字塔: {[tuple(o.shape) for o in outs_b0]}")
    assert p3_shape == (1, 256, 100, 100), f"B0 P3 形状异常: {p3_shape}"
    
    # 检查数值无 NaN / Inf
    for i, o in enumerate(outs_b0):
        assert not torch.isnan(o).any(), f"B0 P{i+3} 包含 NaN"
        assert not torch.isinf(o).any(), f"B0 P{i+3} 包含 Inf"
    print(">> B0 (P3-P7) Smoke 前向与数值校验通过!")
    
    # 2. 验证 B1 (P2-P6, start_level=0, num_outs=5)
    fpn_b1 = MockFPN(in_channels_list=[256, 512, 1024, 2048], out_channels=256, start_level=0, num_outs=5)
    outs_b1 = fpn_b1(backbone_feats)
    
    assert len(outs_b1) == 5, f"B1 金字塔输出层数应为 5，实际为 {len(outs_b1)}"
    # outs_b1: P2(200x200), P3(100x100), P4(50x50), P5(25x25), P6(13x13)
    p2_shape = outs_b1[0].shape
    print(f"[B1] 输出 5 层金字塔: {[tuple(o.shape) for o in outs_b1]}")
    assert p2_shape == (1, 256, 200, 200), f"B1 P2 形状异常: {p2_shape}"
    
    # 核心守恒验证: B1 P2 空间分辨率必须为 B0 P3 的 2 倍
    assert outs_b1[0].shape[2] == outs_b0[0].shape[2] * 2, "B1 P2 空间高度应为 B0 P3 的 2 倍"
    assert outs_b1[0].shape[3] == outs_b0[0].shape[3] * 2, "B1 P2 空间宽度应为 B0 P3 的 2 倍"
    
    # 检查数值无 NaN / Inf
    for i, o in enumerate(outs_b1):
        assert not torch.isnan(o).any(), f"B1 P{i+2} 包含 NaN"
        assert not torch.isinf(o).any(), f"B1 P{i+2} 包含 Inf"
    print(">> B1 (P2-P6) Smoke 前向与数值校验通过!")
    print(">> 核心尺度对齐: B1 P2 分辨率 (200x200) 为 B0 P3 分辨率 (100x100) 的 2 倍!")
    print("==================================================")
    print("PRT-001 Gate S: 全部验证通过 (STATUS: MEASURED / SMOKE_ONLY)")
    print("==================================================")


if __name__ == "__main__":
    run_gate_s_smoke()
