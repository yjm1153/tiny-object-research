#!/usr/bin/env bash
# ==============================================================================
# PRT-001-A1 极小目标基准实验全自动执行与下机看门狗脚本
# 遵循实验执行 Agent 自主闭环流程：
# 1. 训练与评估 B0 seed 1 (FCOS-R50 P3-P7)
# 2. 训练与评估 B1 seed 1 (FCOS-R50 P2-P6)
# 3. 运行汇总统计并计算 Gate B 判定
# 4. 若触发条件成立则自适应运行 seed 2
# 5. 生成结果报告并安全同步磁盘，触发自动关机下机保护
# ==============================================================================

set -e
PROJECT_ROOT="/root/tiny-object-research"
cd "${PROJECT_ROOT}"

echo "======================================================================"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 启动 PRT-001-A1 实验流水线 (PID: $$)..."
echo "======================================================================"

mkdir -p outputs/PRT-001-A1/B0/seed1 outputs/PRT-001-A1/B1/seed1 outputs/PRT-001-A1/logs

# ------------------------------------------------------------------------------
# 阶段 1: B0 seed 1 (FCOS-R50 P3-P7, seed 1) 训练与评估
# ------------------------------------------------------------------------------
echo "[$(date '+%Y-%m-%d %H:%M:%S')] [1/4] 启动 B0 seed 1 训练 (12 epochs, seed=1)..."
python tools/train.py configs/prtiny/fcos_r50_fpn_p3p7_aitodv2.py \
    --work-dir outputs/PRT-001-A1/B0/seed1 \
    --seed 1 2>&1 | tee outputs/PRT-001-A1/logs/train_b0_seed1.log

echo "[$(date '+%Y-%m-%d %H:%M:%S')] [1/4] 正在对 B0 seed 1 最佳权重进行极小目标全量评测..."
B0_S1_CKPT=$(find outputs/PRT-001-A1/B0/seed1/ -name "best_*.pth" | head -n 1)
if [ -z "${B0_S1_CKPT}" ]; then
    B0_S1_CKPT="outputs/PRT-001-A1/B0/seed1/epoch_12.pth"
fi
python tools/evaluate.py configs/prtiny/fcos_r50_fpn_p3p7_aitodv2.py \
    --checkpoint "${B0_S1_CKPT}" \
    --work-dir outputs/PRT-001-A1/B0/seed1 2>&1 | tee outputs/PRT-001-A1/logs/eval_b0_seed1.log

# ------------------------------------------------------------------------------
# 阶段 2: B1 seed 1 (FCOS-R50 P2-P6, seed 1) 训练与评估
# ------------------------------------------------------------------------------
echo "[$(date '+%Y-%m-%d %H:%M:%S')] [2/4] 启动 B1 seed 1 训练 (12 epochs, seed=1)..."
python tools/train.py configs/prtiny/fcos_r50_fpn_p2p6_aitodv2.py \
    --work-dir outputs/PRT-001-A1/B1/seed1 \
    --seed 1 2>&1 | tee outputs/PRT-001-A1/logs/train_b1_seed1.log

echo "[$(date '+%Y-%m-%d %H:%M:%S')] [2/4] 正在对 B1 seed 1 最佳权重进行极小目标全量评测..."
B1_S1_CKPT=$(find outputs/PRT-001-A1/B1/seed1/ -name "best_*.pth" | head -n 1)
if [ -z "${B1_S1_CKPT}" ]; then
    B1_S1_CKPT="outputs/PRT-001-A1/B1/seed1/epoch_12.pth"
fi
python tools/evaluate.py configs/prtiny/fcos_r50_fpn_p2p6_aitodv2.py \
    --checkpoint "${B1_S1_CKPT}" \
    --work-dir outputs/PRT-001-A1/B1/seed1 2>&1 | tee outputs/PRT-001-A1/logs/eval_b1_seed1.log

# ------------------------------------------------------------------------------
# 阶段 3: 汇总生成 summary.csv 与 gate_report.json
# ------------------------------------------------------------------------------
echo "[$(date '+%Y-%m-%d %H:%M:%S')] [3/4] 运行 PRT-001-A1 指标汇总与 Gate B 判定..."
python tools/summarize_prt001_a1.py --root outputs/PRT-001-A1 --output-dir outputs/PRT-001-A1

# 检查是否触发 seed 2
NEED_SEED2=$(python -c "import json; data=json.load(open('outputs/PRT-001-A1/gate_report.json')); print(data.get('gate_checks', {}).get('seed2_trigger_condition', {}).get('triggered', False))")

if [ "${NEED_SEED2}" = "True" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 检测到触发条件成立，自适应启动 seed 2 补充验证..."
    
    mkdir -p outputs/PRT-001-A1/B0/seed2 outputs/PRT-001-A1/B1/seed2
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 运行 B0 seed 2..."
    python tools/train.py configs/prtiny/fcos_r50_fpn_p3p7_aitodv2.py \
        --work-dir outputs/PRT-001-A1/B0/seed2 \
        --seed 2 2>&1 | tee outputs/PRT-001-A1/logs/train_b0_seed2.log
    B0_S2_CKPT=$(find outputs/PRT-001-A1/B0/seed2/ -name "best_*.pth" | head -n 1)
    if [ -z "${B0_S2_CKPT}" ]; then
        B0_S2_CKPT="outputs/PRT-001-A1/B0/seed2/epoch_12.pth"
    fi
    python tools/evaluate.py configs/prtiny/fcos_r50_fpn_p3p7_aitodv2.py \
        --checkpoint "${B0_S2_CKPT}" \
        --work-dir outputs/PRT-001-A1/B0/seed2 2>&1 | tee outputs/PRT-001-A1/logs/eval_b0_seed2.log
        
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 运行 B1 seed 2..."
    python tools/train.py configs/prtiny/fcos_r50_fpn_p2p6_aitodv2.py \
        --work-dir outputs/PRT-001-A1/B1/seed2 \
        --seed 2 2>&1 | tee outputs/PRT-001-A1/logs/train_b1_seed2.log
    B1_S2_CKPT=$(find outputs/PRT-001-A1/B1/seed2/ -name "best_*.pth" | head -n 1)
    if [ -z "${B1_S2_CKPT}" ]; then
        B1_S2_CKPT="outputs/PRT-001-A1/B1/seed2/epoch_12.pth"
    fi
    python tools/evaluate.py configs/prtiny/fcos_r50_fpn_p2p6_aitodv2.py \
        --checkpoint "${B1_S2_CKPT}" \
        --work-dir outputs/PRT-001-A1/B1/seed2 2>&1 | tee outputs/PRT-001-A1/logs/eval_b1_seed2.log

    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 重新生成包含 seed 2 的汇总报告..."
    python tools/summarize_prt001_a1.py --root outputs/PRT-001-A1 --output-dir outputs/PRT-001-A1
fi

echo "======================================================================"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] [4/4] 实验流水线执行完毕！正在同步磁盘数据..."
echo "======================================================================"
sync
sleep 5

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 触发 AutoDL 关机下机保护，防止 GPU 空转计费..."
/usr/bin/shutdown || shutdown -h now || /usr/sbin/poweroff || true
