# Baseline B1: FCOS-R50-FPN-P2 下移五层金字塔 (P2-P6, stride 4-64)
# 数据集: AI-TOD-v2
# 约束说明: 保持与 B0 严格相同的 Head 深度 (4 convs)、通道数 (256)、优化器与 12 epochs 预算，仅下移 FPN 提取层级与回归范围

_base_ = ['./aitodv2.py']

model = dict(
    type='FCOS',
    data_preprocessor=dict(
        type='DetDataPreprocessor',
        mean=[123.675, 116.28, 103.53],
        std=[58.395, 57.12, 57.375],
        bgr_to_rgb=True,
        pad_size_divisor=32
    ),
    backbone=dict(
        type='ResNet',
        depth=50,
        num_stages=4,
        out_indices=(0, 1, 2, 3),
        frozen_stages=1,
        norm_cfg=dict(type='BN', requires_grad=True),
        norm_eval=True,
        style='pytorch',
        init_cfg=dict(type='Pretrained', checkpoint='torchvision://resnet50')
    ),
    neck=dict(
        type='FPN',
        in_channels=[256, 512, 1024, 2048],
        out_channels=256,
        start_level=0,  # 下移至 Stage 0 (res2 输出，即 P2 来源)
        add_extra_convs='on_output',
        num_outs=5,     # 输出 P2, P3, P4, P5, P6 (保持 5 层金字塔)
        relu_before_extra_convs=True
    ),
    bbox_head=dict(
        type='FCOSHead',
        num_classes=8,
        in_channels=256,
        stacked_convs=4,
        feat_channels=256,
        strides=[4, 8, 16, 32, 64],  # 金字塔 stride 同步下移
        regress_ranges=((-1, 32), (32, 64), (64, 128), (128, 256), (256, 100000000.0)),  # 回归范围对齐下移
        loss_cls=dict(
            type='FocalLoss',
            use_sigmoid=True,
            gamma=2.0,
            alpha=0.25,
            loss_weight=1.0
        ),
        loss_bbox=dict(type='GIoULoss', loss_weight=1.0),
        loss_centerness=dict(
            type='CrossEntropyLoss',
            use_sigmoid=True,
            loss_weight=1.0
        )
    ),
    test_cfg=dict(
        nms_pre=3000,
        min_bbox_size=0,
        score_thr=0.05,
        nms=dict(type='nms', iou_threshold=0.5),
        max_per_img=3000
    )
)

# 训练与优化器设置 (与 B0 完全一致: 12 epochs, 单卡 batch_size=2, lr=0.0025, 8/11 epoch 衰减)
optim_wrapper = dict(
    type='OptimWrapper',
    optimizer=dict(type='SGD', lr=0.0025, momentum=0.9, weight_decay=0.0001),
    paramwise_cfg=dict(bias_lr_mult=2.0, bias_decay_mult=0.0),
    clip_grad=dict(max_norm=35, norm_type=2)
)

param_scheduler = [
    dict(
        type='LinearLR',
        start_factor=1.0 / 3,
        by_epoch=False,
        begin=0,
        end=500
    ),
    dict(
        type='MultiStepLR',
        begin=0,
        end=12,
        by_epoch=True,
        milestones=[8, 11],
        gamma=0.1
    )
]

train_cfg = dict(type='EpochBasedTrainLoop', max_epochs=12, val_interval=1)
val_cfg = dict(type='ValLoop')
test_cfg = dict(type='TestLoop')

default_hooks = dict(
    timer=dict(type='IterTimerHook'),
    logger=dict(type='LoggerHook', interval=50),
    param_scheduler=dict(type='ParamSchedulerHook'),
    checkpoint=dict(type='CheckpointHook', interval=1, max_keep_ckpts=3, save_best='auto'),
    sampler_seed=dict(type='DistSamplerSeedHook')
)
