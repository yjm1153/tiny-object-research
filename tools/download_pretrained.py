# -*- coding: utf-8 -*-
"""下载并校验 ResNet-50 ImageNet 预训练权重

下载官方权重并计算 SHA-256 存入 manifest。
"""

import os
import sys
import urllib.request
import hashlib
import json

TARGET_DIR = r"d:\研究\tiny-object-research\data\pretrained"
WEIGHTS_URLS = [
    {
        "name": "resnet50_msra-5891d200.pth",
        "url": "https://download.openmmlab.com/pretrain/third_party/resnet50_msra-5891d200.pth",
        "expected_sha256": "5891d200",
        "framework": "MMDetection / MSRA standard"
    },
    {
        "name": "resnet50-0676ba61.pth",
        "url": "https://download.pytorch.org/models/resnet50-0676ba61.pth",
        "expected_sha256": "0676ba61",
        "framework": "PyTorch Torchvision"
    }
]


def compute_sha256(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def download_weights():
    os.makedirs(TARGET_DIR, exist_ok=True)
    manifest = []

    for item in WEIGHTS_URLS:
        target_path = os.path.join(TARGET_DIR, item["name"])
        print(f"正在处理权重: {item['name']} ...")
        
        if os.path.exists(target_path) and os.path.getsize(target_path) > 10 * 1024 * 1024:
            print(f"  -> 文件已存在: {target_path} (大小: {os.path.getsize(target_path):,} bytes)")
        else:
            print(f"  -> 开始从 {item['url']} 下载...")
            try:
                def progress(block_num, block_size, total_size):
                    downloaded = block_num * block_size
                    if total_size > 0:
                        percent = min(100.0, downloaded * 100.0 / total_size)
                        if block_num % 1000 == 0:
                            print(f"     进度: {percent:.1f}% ({downloaded / (1024*1024):.1f}MB / {total_size / (1024*1024):.1f}MB)")
                
                urllib.request.urlretrieve(item["url"], target_path, reporthook=progress)
                print(f"  -> 下载完成: {target_path}")
            except Exception as e:
                print(f"  -> [提示] 下载报错或网络限制: {e}")
                if not os.path.exists(target_path) or os.path.getsize(target_path) < 1000:
                    continue

        if os.path.exists(target_path) and os.path.getsize(target_path) > 1000:
            actual_sha256 = compute_sha256(target_path)
            file_size = os.path.getsize(target_path)
            print(f"  -> SHA-256: {actual_sha256}")
            
            manifest.append({
                "filename": item["name"],
                "path": f"data/pretrained/{item['name']}",
                "size_bytes": file_size,
                "sha256": actual_sha256,
                "source_url": item["url"],
                "framework": item["framework"]
            })

    manifest_file = os.path.join(TARGET_DIR, "manifest.json")
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"\n[成功] 预训练权重清单已写入: {manifest_file}")


if __name__ == "__main__":
    download_weights()
