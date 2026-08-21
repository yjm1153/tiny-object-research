import pytest


def test_fcos_b0_config():
    """验证 B0 (标准 FCOS P3-P7) 金字塔配置参数"""
    # 模拟读取 B0 配置
    import configs.prtiny.fcos_r50_fpn_p3p7_aitodv2 as b0
    
    assert b0.model['type'] == 'FCOS'
    neck = b0.model['neck']
    assert neck['start_level'] == 1  # 从 P3 (Stage 1) 开始
    assert neck['num_outs'] == 5
    
    head = b0.model['bbox_head']
    assert head['strides'] == [8, 16, 32, 64, 128]
    assert head['regress_ranges'] == ((-1, 64), (64, 128), (128, 256), (256, 512), (512, 100000000.0))
    assert head['feat_channels'] == 256
    assert head['stacked_convs'] == 4


def test_fcos_b1_config():
    """验证 B1 (FCOS-P2 下移金字塔 P2-P6) 配置参数"""
    import configs.prtiny.fcos_r50_fpn_p2p6_aitodv2 as b1
    
    assert b1.model['type'] == 'FCOS'
    neck = b1.model['neck']
    assert neck['start_level'] == 0  # 下移至 P2 (Stage 0) 开始
    assert neck['num_outs'] == 5
    
    head = b1.model['bbox_head']
    assert head['strides'] == [4, 8, 16, 32, 64]  # 步长严格下移
    assert head['regress_ranges'] == ((-1, 32), (32, 64), (64, 128), (128, 256), (256, 100000000.0))
    assert head['feat_channels'] == 256
    assert head['stacked_convs'] == 4


def test_b0_b1_fairness_alignment():
    """验证 B0 与 B1 的结构容量、通道数、优化器与训练预算严格公平对齐"""
    import configs.prtiny.fcos_r50_fpn_p3p7_aitodv2 as b0
    import configs.prtiny.fcos_r50_fpn_p2p6_aitodv2 as b1
    
    # 骨干网络一致
    assert b0.model['backbone'] == b1.model['backbone']
    
    # 检测头深度与通道一致
    assert b0.model['bbox_head']['in_channels'] == b1.model['bbox_head']['in_channels']
    assert b0.model['bbox_head']['feat_channels'] == b1.model['bbox_head']['feat_channels']
    assert b0.model['bbox_head']['stacked_convs'] == b1.model['bbox_head']['stacked_convs']
    assert b0.model['bbox_head']['loss_cls'] == b1.model['bbox_head']['loss_cls']
    assert b0.model['bbox_head']['loss_bbox'] == b1.model['bbox_head']['loss_bbox']
    
    # 训练预算与优化器一致
    assert b0.optim_wrapper == b1.optim_wrapper
    assert b0.train_cfg == b1.train_cfg
    assert b0.param_scheduler == b1.param_scheduler
