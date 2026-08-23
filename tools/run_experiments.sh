#!/usr/bin/env bash
set -e

# ==============================================================================
# PRTiny 矩阵训练与自动关机下机流水线 (AutoDL 零空转计费保障)
# ==============================================================================

echo "=================================================================="
echo "PRTiny 矩阵实验流程状态检查与断点续训"
echo "=================================================================="

# 1. 检查 B0 是否已完成
if [ -f "outputs/PRT-001/B0/seed0/best_coco_bbox_mAP_epoch_12.pth" ]; then
    echo "✅ [1/3] B0 基线 (FCOS-P3P7) 已 100% 完成，跳过训练。"
else
    echo "🚀 正在训练 B0 基线..."
    python tools/train.py configs/prtiny/fcos_r50_fpn_p3p7_aitodv2.py \
        --work-dir outputs/PRT-001/B0/seed0 \
        --resume \
        --seed 0
fi

# 2. 检查 B1 是否已完成
if [ -f "outputs/PRT-001/B1/seed0/best_coco_bbox_mAP_epoch_12.pth" ]; then
    echo "✅ [2/3] B1 基线 (FCOS-P2P6) 已 100% 完成，跳过训练。"
else
    echo "🚀 正在训练 B1 基线..."
    python tools/train.py configs/prtiny/fcos_r50_fpn_p2p6_aitodv2.py \
        --work-dir outputs/PRT-001/B1/seed0 \
        --resume \
        --seed 0
fi

# 3. 运行 / 断点续训 PRT-002 PDD (从 Epoch 3 恢复继续完成 4~12 轮)
echo "=================================================================="
echo "🚀 [3/3] 正在从 Checkpoint 自动续训 PRT-002 PDD 模型 (Epoch 4~12)..."
echo "=================================================================="
python tools/train.py configs/prtiny/fcos_r50_pdd_p2p6_aitodv2.py \
    --work-dir outputs/PRT-002/PDD/seed0 \
    --resume \
    --seed 0

echo "=================================================================="
echo "🎉 全矩阵 3 大模型全部 12 轮训练与评测已 100% 圆满完成！"
echo "=================================================================="

# 生成最终指标快照
python tools/track_progress.py
python -c "from tools.monitor_daemon import update_dashboard; update_dashboard()"

echo "=================================================================="
echo "💤 正在触发 AutoDL 自动下机关机指令，彻底避免 GPU 空转计费..."
echo "=================================================================="
sync
sleep 5
/usr/bin/shutdown || shutdown -h now || poweroff
