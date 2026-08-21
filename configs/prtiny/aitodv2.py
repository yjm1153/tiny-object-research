# AI-TOD-v2 数据集基础配置与流水线
# 数据集来源: AI-TOD-v2 (https://chasel-tsui.github.io/AI-TOD-v2/)

dataset_type = 'AITODv2Dataset'
data_root = 'data/AI-TOD-v2/'

# AI-TOD-v2 官方 8 个目标类别
class_names = [
    'airplane',
    'bridge',
    'storage-tank',
    'ship',
    'swimming-pool',
    'vehicle',
    'person',
    'wind-mill'
]
num_classes = len(class_names)

# 输入尺度固定为 800x800，保持长宽比并 pad 到 32 的倍数
# 严格遵守 PRT-001 约束: 仅允许随机水平翻转 (p=0.5)，严禁 mosaic / mixup / copy-paste
input_size = (800, 800)

train_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(type='LoadAnnotations', with_bbox=True),
    dict(type='Resize', scale=input_size, keep_ratio=True),
    dict(type='RandomFlip', prob=0.5),
    dict(type='Pad', size_divisor=32),
    dict(type='PackDetInputs')
]

val_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(type='Resize', scale=input_size, keep_ratio=True),
    dict(type='Pad', size_divisor=32),
    dict(type='LoadAnnotations', with_bbox=True),
    dict(
        type='PackDetInputs',
        meta_keys=('img_id', 'img_path', 'ori_shape', 'img_shape', 'scale_factor')
    )
]

test_pipeline = val_pipeline

train_dataloader = dict(
    batch_size=2,
    num_workers=2,
    persistent_workers=True,
    sampler=dict(type='DefaultSampler', shuffle=True),
    batch_sampler=dict(type='AspectRatioBatchSampler'),
    dataset=dict(
        type=dataset_type,
        data_root=data_root,
        metainfo=dict(classes=class_names),
        ann_file='annotations/aitodv2_train.json',
        data_prefix=dict(img='train/'),
        filter_cfg=dict(filter_empty_gt=True, min_size=2),
        pipeline=train_pipeline
    )
)

val_dataloader = dict(
    batch_size=2,
    num_workers=2,
    persistent_workers=True,
    drop_last=False,
    sampler=dict(type='DefaultSampler', shuffle=False),
    dataset=dict(
        type=dataset_type,
        data_root=data_root,
        metainfo=dict(classes=class_names),
        ann_file='annotations/aitodv2_val.json',
        data_prefix=dict(img='val/'),
        test_mode=True,
        pipeline=val_pipeline
    )
)

# test split 严格隔离，开发阶段不得用于调参
test_dataloader = dict(
    batch_size=2,
    num_workers=2,
    persistent_workers=True,
    drop_last=False,
    sampler=dict(type='DefaultSampler', shuffle=False),
    dataset=dict(
        type=dataset_type,
        data_root=data_root,
        metainfo=dict(classes=class_names),
        ann_file='annotations/aitodv2_test.json',
        data_prefix=dict(img='test/'),
        test_mode=True,
        pipeline=test_pipeline
    )
)

val_evaluator = dict(
    type='TinyObjectEvaluator',
    ann_file=data_root + 'annotations/aitodv2_val.json',
    metric=['bbox'],
    format_only=False
)

test_evaluator = dict(
    type='TinyObjectEvaluator',
    ann_file=data_root + 'annotations/aitodv2_test.json',
    metric=['bbox'],
    format_only=False
)
