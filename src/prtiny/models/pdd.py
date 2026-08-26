# -*- coding: utf-8 -*-
"""PDD: Partial Detail-Preserving Downsampling (局部细节保留下采样) 模块

设计动机：
极小目标 (2–8 px) 在标准 ResNet 早期下采样 (如 stride-2 卷积或 max-pooling) 中极易发生亚像素级几何空间排布丢失与高频衰减。
PDD 在向 P2/P3 供给浅层特征的早期阶段：
1. 将输入通道按比例拆分 (默认 1:1)；
2. 路径 1 (Space-to-Depth 分支): 使用无损 space-to-depth 变换将 2x2 邻域像素排布重组至通道维，保留极小目标微观空间排列；
3. 路径 2 (Learnable DWConv 分支): 使用 3x3 Stride-2 Depthwise 卷积提取局部下采样语义特征；
4. 拼接后通过 1x1 卷积完成通道融合与压缩，严格对齐输出通道数与空间分辨率 (H/2, W/2)。
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

try:
    from mmdet.registry import MODELS
    from mmdet.models.backbones.resnet import ResNet
    MMDET_AVAILABLE = True
except ImportError:
    MMDET_AVAILABLE = False


class SpaceToDepth(nn.Module):
    """Space-to-Depth (Pixel Unshuffle) 变换: [B, C, H, W] -> [B, 4C, H/2, W/2]"""
    def __init__(self, block_size=2):
        super().__init__()
        self.block_size = block_size

    def forward(self, x):
        b, c, h, w = x.shape
        bs = self.block_size
        if h % bs != 0 or w % bs != 0:
            pad_h = (bs - h % bs) % bs
            pad_w = (bs - w % bs) % bs
            x = F.pad(x, (0, pad_w, 0, pad_h), mode='reflect')
            _, _, h, w = x.shape
            
        # Reshape & Permute 构造无损空间-通道重排
        x = x.view(b, c, h // bs, bs, w // bs, bs)
        x = x.permute(0, 3, 5, 1, 2, 4).contiguous()
        x = x.view(b, c * (bs ** 2), h // bs, w // bs)
        return x


class PDDDownsample(nn.Module):
    """Partial Detail-Preserving Downsampling 模块

    Args:
        in_channels (int): 输入特征通道数
        out_channels (int): 输出目标通道数
        split_ratio (float): Space-to-Depth 路径分配的通道比例，默认 0.5
        norm_cfg (bool): 是否使用批归一化
    """
    def __init__(self, in_channels, out_channels, split_ratio=0.5, norm_cfg=True):
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.split_ratio = split_ratio
        
        self.c1 = int(in_channels * split_ratio)
        self.c2 = in_channels - self.c1
        assert self.c1 > 0 and self.c2 > 0, "拆分通道数必须大于 0"

        # 路径 1: 无损 Space-to-Depth (输出通道数 = 4 * c1)
        self.s2d = SpaceToDepth(block_size=2)
        
        # 路径 2: 可学习 Stride-2 Depthwise 卷积 (输出通道数 = c2)
        self.dw_conv = nn.Conv2d(
            self.c2, self.c2, kernel_size=3, stride=2, padding=1, groups=self.c2, bias=False
        )
        self.bn_dw = nn.BatchNorm2d(self.c2) if norm_cfg else nn.Identity()
        self.act_dw = nn.ReLU(inplace=True)

        # 融合与通道压缩 1x1 Conv: 输入通道 (4*c1 + c2) -> 输出通道 out_channels
        fused_channels = 4 * self.c1 + self.c2
        self.fuse_conv = nn.Sequential(
            nn.Conv2d(fused_channels, out_channels, kernel_size=1, bias=False),
            nn.BatchNorm2d(out_channels) if norm_cfg else nn.Identity(),
            nn.ReLU(inplace=True)
        )
        self.init_weights()

    def init_weights(self):
        """权重保真与数值稳定初始化"""
        if isinstance(self.dw_conv, nn.Conv2d):
            nn.init.kaiming_normal_(self.dw_conv.weight, mode='fan_out', nonlinearity='relu')
        if isinstance(self.bn_dw, nn.BatchNorm2d):
            nn.init.constant_(self.bn_dw.weight, 1.0)
            nn.init.constant_(self.bn_dw.bias, 0.0)
        for m in self.fuse_conv.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1.0)
                nn.init.constant_(m.bias, 0.0)

    def forward(self, x):
        # 1. 通道拆分
        x1 = x[:, :self.c1, :, :]
        x2 = x[:, self.c1:, :, :]

        # 2. 双路径下采样
        out_s2d = self.s2d(x1)                     # [B, 4*c1, H/2, W/2]
        out_dw = self.act_dw(self.bn_dw(self.dw_conv(x2)))  # [B, c2, H/2, W/2]

        # 3. 拼接与融合压缩
        out_fused = torch.cat([out_s2d, out_dw], dim=1)
        out = self.fuse_conv(out_fused)            # [B, out_channels, H/2, W/2]
        return out


class ResNetStemPDD(nn.Module):
    """带 PDD 下采样的 ResNet 骨干适配 Stem (用于早期 Stage 0/1 特征过渡)"""
    def __init__(self, in_channels=3, stem_channels=64, out_channels=256):
        super().__init__()
        self.conv1 = nn.Sequential(
            nn.Conv2d(in_channels, stem_channels, kernel_size=3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(stem_channels),
            nn.ReLU(inplace=True)
        )
        self.pdd_down = PDDDownsample(
            in_channels=stem_channels,
            out_channels=stem_channels,
            split_ratio=0.5
        )

    def forward(self, x):
        x = self.conv1(x)
        x = self.pdd_down(x)
        return x


if MMDET_AVAILABLE:
    @MODELS.register_module()
    class ResNetWithPDD(ResNet):
        """MMDetection 兼容的 ResNetWithPDD 骨干网络"""
        def __init__(self, pdd_stages=(0, 1), *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.pdd_stages = pdd_stages
            if 0 in pdd_stages:
                # 替换传统 maxpool 为 PDDDownsample (64 -> 64)
                self.maxpool = PDDDownsample(in_channels=64, out_channels=64, split_ratio=0.5)

        def init_weights(self):
            super().init_weights()
            if hasattr(self, 'maxpool') and isinstance(self.maxpool, PDDDownsample):
                self.maxpool.init_weights()

        def forward(self, x):
            return super().forward(x)
else:
    class ResNetWithPDD(nn.Module):
        pass
