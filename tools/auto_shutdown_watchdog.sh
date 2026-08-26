#!/usr/bin/env bash
# ==============================================================================
# PRTiny 训练结束自动下机看门狗 (AutoDL 零空转计费保护)
# 监听训练 PID 并在其正常结束后安全落盘并触发关机下机
# ==============================================================================

TRAIN_PID=${1:-6716}
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 自动下机看门狗已激活，正在监听训练进程 PID: ${TRAIN_PID}..."

while kill -0 ${TRAIN_PID} 2>/dev/null; do
    sleep 30
done

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 检测到训练进程 ${TRAIN_PID} 已结束！"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 正在安全同步磁盘数据与日志..."
sync
sleep 5

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 正在触发 AutoDL 自动关机下机指令，彻底避免 GPU 空转计费..."
/usr/bin/shutdown || shutdown -h now || /usr/sbin/poweroff
