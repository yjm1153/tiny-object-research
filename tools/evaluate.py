# -*- coding: utf-8 -*-
"""MMDetection 模型评估与极小目标尺度诊断脚本"""

import argparse
import os
import os.path as osp
import json

from mmengine.config import Config, DictAction
from mmengine.runner import Runner
from mmengine.runner import set_random_seed


def parse_args():
    parser = argparse.ArgumentParser(description='Evaluate a detector')
    parser.add_argument('config', help='test config file path')
    parser.add_argument('--checkpoint', required=True, help='checkpoint file')
    parser.add_argument('--work-dir', help='the dir to save logs and eval results')
    parser.add_argument(
        '--cfg-options',
        nargs='+',
        action=DictAction,
        help='override some settings in the used config')
    parser.add_argument(
        '--launcher',
        choices=['none', 'pytorch', 'slurm', 'mpi'],
        default='none',
        help='job launcher')
    parser.add_argument('--local_rank', '--local-rank', type=int, default=0)
    args = parser.parse_args()
    if 'LOCAL_RANK' not in os.environ:
        os.environ['LOCAL_RANK'] = str(args.local_rank)
    return args


def main():
    args = parse_args()

    cfg = Config.fromfile(args.config)
    cfg.launcher = args.launcher
    if args.cfg_options is not None:
        cfg.merge_from_dict(args.cfg_options)

    if args.work_dir is not None:
        cfg.work_dir = args.work_dir
    else:
        cfg.work_dir = osp.dirname(args.checkpoint)

    cfg.load_from = args.checkpoint

    # 构建并运行评估
    runner = Runner.from_cfg(cfg)
    metrics = runner.test()
    print("==================================================")
    print("评估指标结果 (Evaluation Metrics):")
    print(metrics)
    print("==================================================")

    # 导出评估结果
    eval_out = osp.join(cfg.work_dir, "eval_results.json")
    with open(eval_out, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    print(f"评估指标已保存至: {eval_out}")


if __name__ == '__main__':
    main()
