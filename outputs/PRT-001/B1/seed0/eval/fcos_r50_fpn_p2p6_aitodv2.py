class_names = [
    'airplane',
    'bridge',
    'storage-tank',
    'ship',
    'swimming-pool',
    'vehicle',
    'person',
    'wind-mill',
]
data_root = 'data/AI-TOD-v2/'
dataset_type = 'CocoDataset'
default_hooks = dict(
    checkpoint=dict(
        interval=1, max_keep_ckpts=3, save_best='auto', type='CheckpointHook'),
    logger=dict(interval=50, type='LoggerHook'),
    param_scheduler=dict(type='ParamSchedulerHook'),
    sampler_seed=dict(type='DistSamplerSeedHook'),
    timer=dict(type='IterTimerHook'))
default_scope = 'mmdet'
input_size = (
    800,
    800,
)
launcher = 'none'
load_from = 'outputs/PRT-001/B1/seed0/best_coco_bbox_mAP_epoch_12.pth'
model = dict(
    backbone=dict(
        depth=50,
        frozen_stages=1,
        init_cfg=dict(
            checkpoint='data/pretrained/resnet50_msra-5891d200.pth',
            type='Pretrained'),
        norm_cfg=dict(requires_grad=True, type='BN'),
        norm_eval=True,
        num_stages=4,
        out_indices=(
            0,
            1,
            2,
            3,
        ),
        style='pytorch',
        type='ResNet'),
    bbox_head=dict(
        feat_channels=256,
        in_channels=256,
        loss_bbox=dict(loss_weight=1.0, type='GIoULoss'),
        loss_centerness=dict(
            loss_weight=1.0, type='CrossEntropyLoss', use_sigmoid=True),
        loss_cls=dict(
            alpha=0.25,
            gamma=2.0,
            loss_weight=1.0,
            type='FocalLoss',
            use_sigmoid=True),
        num_classes=8,
        regress_ranges=(
            (
                -1,
                32,
            ),
            (
                32,
                64,
            ),
            (
                64,
                128,
            ),
            (
                128,
                256,
            ),
            (
                256,
                100000000.0,
            ),
        ),
        stacked_convs=4,
        strides=[
            4,
            8,
            16,
            32,
            64,
        ],
        type='FCOSHead'),
    data_preprocessor=dict(
        bgr_to_rgb=True,
        mean=[
            123.675,
            116.28,
            103.53,
        ],
        pad_size_divisor=32,
        std=[
            58.395,
            57.12,
            57.375,
        ],
        type='DetDataPreprocessor'),
    neck=dict(
        add_extra_convs='on_output',
        in_channels=[
            256,
            512,
            1024,
            2048,
        ],
        num_outs=5,
        out_channels=256,
        relu_before_extra_convs=True,
        start_level=0,
        type='FPN'),
    test_cfg=dict(
        max_per_img=3000,
        min_bbox_size=0,
        nms=dict(iou_threshold=0.5, type='nms'),
        nms_pre=3000,
        score_thr=0.05),
    type='FCOS')
num_classes = 8
optim_wrapper = dict(
    clip_grad=dict(max_norm=35, norm_type=2),
    optimizer=dict(lr=0.005, momentum=0.9, type='SGD', weight_decay=0.0001),
    paramwise_cfg=dict(bias_decay_mult=0.0, bias_lr_mult=2.0),
    type='OptimWrapper')
param_scheduler = [
    dict(
        begin=0,
        by_epoch=False,
        end=250,
        start_factor=0.3333333333333333,
        type='LinearLR'),
    dict(
        begin=0,
        by_epoch=True,
        end=12,
        gamma=0.1,
        milestones=[
            8,
            11,
        ],
        type='MultiStepLR'),
]
test_cfg = dict(type='TestLoop')
test_dataloader = dict(
    batch_size=4,
    dataset=dict(
        ann_file='annotations/aitod_test_v1.json',
        data_prefix=dict(img='test/images/'),
        data_root='data/AI-TOD-v2/',
        metainfo=dict(classes=[
            'airplane',
            'bridge',
            'storage-tank',
            'ship',
            'swimming-pool',
            'vehicle',
            'person',
            'wind-mill',
        ]),
        pipeline=[
            dict(backend_args=None, type='LoadImageFromFile'),
            dict(keep_ratio=True, scale=(
                800,
                800,
            ), type='Resize'),
            dict(size_divisor=32, type='Pad'),
            dict(type='LoadAnnotations', with_bbox=True),
            dict(
                meta_keys=(
                    'img_id',
                    'img_path',
                    'ori_shape',
                    'img_shape',
                    'scale_factor',
                ),
                type='PackDetInputs'),
        ],
        test_mode=True,
        type='CocoDataset'),
    drop_last=False,
    num_workers=8,
    persistent_workers=True,
    pin_memory=True,
    sampler=dict(shuffle=False, type='DefaultSampler'))
test_evaluator = dict(
    ann_file='data/AI-TOD-v2/annotations/aitod_test_v1.json',
    format_only=False,
    metric='bbox',
    type='CocoMetric')
test_pipeline = [
    dict(backend_args=None, type='LoadImageFromFile'),
    dict(keep_ratio=True, scale=(
        800,
        800,
    ), type='Resize'),
    dict(size_divisor=32, type='Pad'),
    dict(type='LoadAnnotations', with_bbox=True),
    dict(
        meta_keys=(
            'img_id',
            'img_path',
            'ori_shape',
            'img_shape',
            'scale_factor',
        ),
        type='PackDetInputs'),
]
train_cfg = dict(max_epochs=12, type='EpochBasedTrainLoop', val_interval=4)
train_dataloader = dict(
    batch_sampler=dict(type='AspectRatioBatchSampler'),
    batch_size=4,
    dataset=dict(
        ann_file='annotations/aitod_train_v1.json',
        data_prefix=dict(img='train/images/'),
        data_root='data/AI-TOD-v2/',
        filter_cfg=dict(filter_empty_gt=True, min_size=2),
        metainfo=dict(classes=[
            'airplane',
            'bridge',
            'storage-tank',
            'ship',
            'swimming-pool',
            'vehicle',
            'person',
            'wind-mill',
        ]),
        pipeline=[
            dict(backend_args=None, type='LoadImageFromFile'),
            dict(type='LoadAnnotations', with_bbox=True),
            dict(keep_ratio=True, scale=(
                800,
                800,
            ), type='Resize'),
            dict(prob=0.5, type='RandomFlip'),
            dict(size_divisor=32, type='Pad'),
            dict(type='PackDetInputs'),
        ],
        type='CocoDataset'),
    num_workers=8,
    persistent_workers=True,
    pin_memory=True,
    sampler=dict(shuffle=True, type='DefaultSampler'))
train_pipeline = [
    dict(backend_args=None, type='LoadImageFromFile'),
    dict(type='LoadAnnotations', with_bbox=True),
    dict(keep_ratio=True, scale=(
        800,
        800,
    ), type='Resize'),
    dict(prob=0.5, type='RandomFlip'),
    dict(size_divisor=32, type='Pad'),
    dict(type='PackDetInputs'),
]
val_cfg = dict(type='ValLoop')
val_dataloader = dict(
    batch_size=4,
    dataset=dict(
        ann_file='annotations/aitod_val_v1.json',
        data_prefix=dict(img='val/images/'),
        data_root='data/AI-TOD-v2/',
        metainfo=dict(classes=[
            'airplane',
            'bridge',
            'storage-tank',
            'ship',
            'swimming-pool',
            'vehicle',
            'person',
            'wind-mill',
        ]),
        pipeline=[
            dict(backend_args=None, type='LoadImageFromFile'),
            dict(keep_ratio=True, scale=(
                800,
                800,
            ), type='Resize'),
            dict(size_divisor=32, type='Pad'),
            dict(type='LoadAnnotations', with_bbox=True),
            dict(
                meta_keys=(
                    'img_id',
                    'img_path',
                    'ori_shape',
                    'img_shape',
                    'scale_factor',
                ),
                type='PackDetInputs'),
        ],
        test_mode=True,
        type='CocoDataset'),
    drop_last=False,
    num_workers=8,
    persistent_workers=True,
    pin_memory=True,
    sampler=dict(shuffle=False, type='DefaultSampler'))
val_evaluator = dict(
    ann_file='data/AI-TOD-v2/annotations/aitod_val_v1.json',
    format_only=False,
    metric='bbox',
    type='CocoMetric')
val_pipeline = [
    dict(backend_args=None, type='LoadImageFromFile'),
    dict(keep_ratio=True, scale=(
        800,
        800,
    ), type='Resize'),
    dict(size_divisor=32, type='Pad'),
    dict(type='LoadAnnotations', with_bbox=True),
    dict(
        meta_keys=(
            'img_id',
            'img_path',
            'ori_shape',
            'img_shape',
            'scale_factor',
        ),
        type='PackDetInputs'),
]
work_dir = 'outputs/PRT-001/B1/seed0/eval'
