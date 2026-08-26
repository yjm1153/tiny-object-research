#!/usr/bin/env bash
# ==============================================================================
# PRT-002-A1 PDD 因果诊断与最小可行性复核 全自动执行与下机看门狗脚本
# 遵循实验执行 Agent 自主闭环流程：
# 1. 运行 B1-U seed 0 (FCOS-R50 P2-P6 unfrozen) 训练与评估
# 2. 运行 PDD-U seed 0 (FCOS-R50 PDD P2-P6 unfrozen) 训练与评估
# 3. 运行汇总统计并计算 Gate V 判定 (Seed 0 可行性)
# 4. 若 Gate V 允许进入 Seed 1，自适应运行 B1-U/PDD-U seed 1
# 5. 重新汇总并判定 Gate B (两 Seed 决策)
# 6. 生成结果报告并安全同步磁盘，触发自动关机下机保护
# ==============================================================================

set -e
PROJECT_ROOT="/root/tiny-object-research"
cd "${PROJECT_ROOT}"

echo "======================================================================"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 启动 PRT-002-A1 实验流水线 (PID: $$)..."
echo "======================================================================"

mkdir -p outputs/PRT-002-A1/B1-U/seed0 outputs/PRT-002-A1/PDD-U/seed0 outputs/PRT-002-A1/logs

# ------------------------------------------------------------------------------
# 阶段 1: B1-U seed 0 (FCOS-R50 P2-P6 unfrozen, seed 0)
# ------------------------------------------------------------------------------
echo "[$(date '+%Y-%m-%d %H:%M:%S')] [1/5] 启动 B1-U seed 0 训练 (12 epochs, seed=0)..."
python tools/train.py configs/prtiny/fcos_r50_fpn_p2p6_unfrozen_aitodv2.py \
    --work-dir outputs/PRT-002-A1/B1-U/seed0 \
    --seed 0 2>&1 | tee outputs/PRT-002-A1/logs/train_b1u_seed0.log

echo "[$(date '+%Y-%m-%d %H:%M:%S')] [1/5] 正在对 B1-U seed 0 最佳权重进行极小目标全量评测..."
B1U_S0_CKPT=$(find outputs/PRT-002-A1/B1-U/seed0/ -name "best_*.pth" | head -n 1)
if [ -z "${B1U_S0_CKPT}" ]; then
    B1U_S0_CKPT="outputs/PRT-002-A1/B1-U/seed0/epoch_12.pth"
fi
python tools/evaluate.py configs/prtiny/fcos_r50_fpn_p2p6_unfrozen_aitodv2.py \
    --checkpoint "${B1U_S0_CKPT}" \
    --work-dir outputs/PRT-002-A1/B1-U/seed0 2>&1 | tee outputs/PRT-002-A1/logs/eval_b1u_seed0.log

# ------------------------------------------------------------------------------
# 阶段 2: PDD-U seed 0 (FCOS-R50 PDD P2-P6 unfrozen, seed 0)
# ------------------------------------------------------------------------------
echo "[$(date '+%Y-%m-%d %H:%M:%S')] [2/5] 启动 PDD-U seed 0 训练 (12 epochs, seed=0)..."
python tools/train.py configs/prtiny/fcos_r50_pdd_p2p6_aitodv2.py \
    --work-dir outputs/PRT-002-A1/PDD-U/seed0 \
    --seed 0 2>&1 | tee outputs/PRT-002-A1/logs/train_pddu_seed0.log

echo "[$(date '+%Y-%m-%d %H:%M:%S')] [2/5] 正在对 PDD-U seed 0 最佳权重进行极小目标全量评测..."
PDDU_S0_CKPT=$(find outputs/PRT-002-A1/PDD-U/seed0/ -name "best_*.pth" | head -n 1)
if [ -z "${PDDU_S0_CKPT}" ]; then
    PDDU_S0_CKPT="outputs/PRT-002-A1/PDD-U/seed0/epoch_12.pth"
fi
python tools/evaluate.py configs/prtiny/fcos_r50_pdd_p2p6_aitodv2.py \
    --checkpoint "${PDDU_S0_CKPT}" \
    --work-dir outputs/PRT-002-A1/PDD-U/seed0 2>&1 | tee outputs/PRT-002-A1/logs/eval_pddu_seed0.log

# ------------------------------------------------------------------------------
# 阶段 3: Gate V 判定 (Seed 0 可行性)
# ------------------------------------------------------------------------------
echo "[$(date '+%Y-%m-%d %H:%M:%S')] [3/5] 运行 PRT-002-A1 Seed 0 汇总与 Gate V 判定..."
python tools/summarize_prt002_a1.py --root outputs/PRT-002-A1 --output-dir outputs/PRT-002-A1

STOP_PDD=$(python -c "import json; data=json.load(open('outputs/PRT-002-A1/gate_report.json')); print(data.get('gate_checks', {}).get('Gate_V_seed0_feasibility', {}).get('stop_pdd', False))")
PASS_GATE_V=$(python -c "import json; data=json.load(open('outputs/PRT-002-A1/gate_report.json')); print(data.get('gate_checks', {}).get('Gate_V_seed0_feasibility', {}).get('passed', False))")

if [ "${STOP_PDD}" = "True" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Seed 0 明确失败，触发科学停止条件 (STOP_PDD=True)，终止后续运行以节省算力！"
elif [ "${PASS_GATE_V}" = "True" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Gate V 达成，允许启动 Seed 1 成对验证..."
    
    mkdir -p outputs/PRT-002-A1/B1-U/seed1 outputs/PRT-002-A1/PDD-U/seed1
    
    # B1-U seed 1
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [4/5] 启动 B1-U seed 1 训练 (12 epochs, seed=1)..."
    python tools/train.py configs/prtiny/fcos_r50_fpn_p2p6_unfrozen_aitodv2.py \
        --work-dir outputs/PRT-002-A1/B1-U/seed1 \
        --seed 1 2>&1 | tee outputs/PRT-002-A1/logs/train_b1u_seed1.log
    B1U_S1_CKPT=$(find outputs/PRT-002-A1/B1-U/seed1/ -name "best_*.pth" | head -n 1)
    if [ -z "${B1U_S1_CKPT}" ]; then
        B1U_S1_CKPT="outputs/PRT-002-A1/B1-U/seed1/epoch_12.pth"
    fi
    python tools/evaluate.py configs/prtiny/fcos_r50_fpn_p2p6_unfrozen_aitodv2.py \
        --checkpoint "${B1U_S1_CKPT}" \
        --work-dir outputs/PRT-002-A1/B1-U/seed1 2>&1 | tee outputs/PRT-002-A1/logs/eval_b1u_seed1.log

    # PDD-U seed 1
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [4/5] 启动 PDD-U seed 1 训练 (12 epochs, seed=1)..."
    python tools/train.py configs/prtiny/fcos_r50_pdd_p2p6_aitodv2.py \
        --work-dir outputs/PRT-002-A1/PDD-U/seed1 \
        --seed 1 2>&1 | tee outputs/PRT-002-A1/logs/train_pddu_seed1.log
    PDDU_S1_CKPT=$(find outputs/PRT-002-A1/PDD-U/seed1/ -name "best_*.pth" | head -n 1)
    if [ -z "${PDDU_S1_CKPT}" ]; then
        PDDU_S1_CKPT="outputs/PRT-002-A1/PDD-U/seed1/epoch_12.pth"
    fi
    python tools/evaluate.py configs/prtiny/fcos_r50_pdd_p2p6_aitodv2.py \
        --checkpoint "${PDDU_S1_CKPT}" \
        --work-dir outputs/PRT-002-A1/PDD-U/seed1 2>&1 | tee outputs/PRT-002-A1/logs/eval_pddu_seed1.log

    # 重新汇总并判定 Gate B
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [5/5] 重新生成包含 seed 0 与 seed 1 的 Gate 报告..."
    python tools/summarize_prt002_a1.py --root outputs/PRT-002-A1 --output-dir outputs/PRT-002-A1
    
    # 检查是否触发 seed 2
    NEED_SEED2=$(python -c "import json; data=json.load(open('outputs/PRT-002-A1/gate_report.json')); print(data.get('gate_checks', {}).get('seed2_trigger_condition', {}).get('triggered', False))")
    if [ "${NEED_SEED2}" = "True" ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 检测到歧义/灰区，按预注册规则自适应补测 seed 2..."
        mkdir -p outputs/PRT-002-A1/B1-U/seed2 outputs/PRT-002-A1/PDD-U/seed2
        
        python tools/train.py configs/prtiny/fcos_r50_fpn_p2p6_unfrozen_aitodv2.py \
            --work-dir outputs/PRT-002-A1/B1-U/seed2 \
            --seed 2 2>&1 | tee outputs/PRT-002-A1/logs/train_b1u_seed2.log
        B1U_S2_CKPT=$(find outputs/PRT-002-A1/B1-U/seed2/ -name "best_*.pth" | head -n 1)
        if [ -z "${B1U_S2_CKPT}" ]; then
            B1U_S2_CKPT="outputs/PRT-002-A1/B1-U/seed2/epoch_12.pth"
        fi
        python tools/evaluate.py configs/prtiny/fcos_r50_fpn_p2p6_unfrozen_aitodv2.py \
            --checkpoint "${B1U_S2_CKPT}" \
            --work-dir outputs/PRT-002-A1/B1-U/seed2 2>&1 | tee outputs/PRT-002-A1/logs/eval_b1u_seed2.log

        python tools/train.py configs/prtiny/fcos_r50_pdd_p2p6_aitodv2.py \
            --work-dir outputs/PRT-002-A1/PDD-U/seed2 \
            --seed 2 2>&1 | tee outputs/PRT-002-A1/logs/train_pddu_seed2.log
        PDDU_S2_CKPT=$(find outputs/PRT-002-A1/PDD-U/seed2/ -name "best_*.pth" | head -n 1)
        if [ -z "${PDDU_S2_CKPT}" ]; then
            PDDU_S2_CKPT="outputs/PRT-002-A1/PDD-U/seed2/epoch_12.pth"
        fi
        python tools/evaluate.py configs/prtiny/fcos_r50_pdd_p2p6_aitodv2.py \
            --checkpoint "${PDDU_S2_CKPT}" \
            --work-dir outputs/PRT-002-A1/PDD-U/seed2 2>&1 | tee outputs/PRT-002-A1/logs/eval_pddu_seed2.log

        python tools/summarize_prt002_a1.py --root outputs/PRT-002-A1 --output-dir outputs/PRT-002-A1
    fi
fi

echo "======================================================================"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 实验流水线执行完毕！正在同步磁盘数据..."
echo "======================================================================"
sync
sleep 5

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 触发 AutoDL 关机下机保护，防止 GPU 空转计费..."
/usr/bin/shutdown || shutdown -h now || /usr/sbin/poweroff || true
