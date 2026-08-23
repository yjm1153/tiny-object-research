# Model: FCOS-R50-PDD-P2 (PDD 局部细节保留下采样增强模型)
# 数据集: AI-TOD-v2
# 优化配置: batch_size=4 + lr=0.005 + num_workers=8 + val_interval=4 (FP32 数值极稳)

_base_ = ['./aitodv2.py']

custom_imports = dict(imports=['prtiny.models'], allow_failed_imports=False)

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
        type='ResNetWithPDD',
        depth=50,
        num_stages=4,
        out_indices=(0, 1, 2, 3),
        frozen_stages=1,
        norm_cfg=dict(type='BN', requires_grad=True),
        norm_eval=True,
        style='pytorch',
        init_cfg=dict(type='Pretrained', checkpoint='data/pretrained/resnet50_msra-5891d200.pth'),
        pdd_stages=(0, 1)
    ),
    neck=dict(
        type='FPN',
        in_channels=[256, 512, 1024, 2048],
        out_channels=256,
        start_level=0,  # 输出 P2, P3, P4, P5, P6
        add_extra_convs='on_output',
        num_outs=5,
        relu_before_extra_convs=True
    ),
    bbox_head=dict(
        type='FCOSHead',
        num_classes=8,
        in_channels=256,
        stacked_convs=4,
        feat_channels=256,
        strides=[4, 8, 16, 32, 64],
        regress_ranges=((-1, 32), (32, 64), (64, 128), (128, 256), (256, 100000000.0)),
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

# 满血训练优化器: FP32 严格数值稳定性 + lr=0.005 + 梯度裁剪
optim_wrapper = dict(
    type='OptimWrapper',
    optimizer=dict(type='SGD', lr=0.005, momentum=0.9, weight_decay=0.0001),
    paramwise_cfg=dict(bias_lr_mult=2.0, bias_decay_mult=0.0),
    clip_grad=dict(max_norm=35, norm_type=2)
)

param_scheduler = [
    dict(
        type='LinearLR',
        start_factor=1.0 / 3,
        by_epoch=False,
        begin=0,
        end=250
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

train_cfg = dict(type='EpochBasedTrainLoop', max_epochs=12, val_interval=4)
val_cfg = dict(type='ValLoop')
test_cfg = dict(type='TestLoop')

default_hooks = dict(
    timer=dict(type='IterTimerHook'),
    logger=dict(type='LoggerHook', interval=50),
    param_scheduler=dict(type='ParamSchedulerHook'),
    checkpoint=dict(type='CheckpointHook', interval=1, max_keep_ckpts=3, save_best='auto'),
    sampler_seed=dict(type='DistSamplerSeedHook')
)
