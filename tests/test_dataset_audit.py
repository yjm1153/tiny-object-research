import json
from pathlib import Path


def test_data_manifest_integrity():
    """验证数据清单存在且符合规范"""
    manifest_path = Path("outputs/PRT-001/data_manifest.json")
    assert manifest_path.exists(), "数据清单 outputs/PRT-001/data_manifest.json 不存在"
    
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert data.get("dataset") == "AI-TOD-v2"
    assert "train" in data.get("splits", [])
    assert "val" in data.get("splits", [])
    assert "test" in data.get("splits", [])
    assert data.get("scale_definition") == "s = sqrt(w * h)"
    assert data.get("diagnostic_bins") == ["[2,4)", "[4,6)", "[6,8)", "[8,16)"]
    assert "PASSED" in data.get("leakage_check", "")


def test_aitodv2_config_classes():
    """验证 AI-TOD-v2 配置中的类别数与定义"""
    import configs.prtiny.aitodv2 as cfg
    
    assert cfg.num_classes == 8
    assert cfg.class_names == [
        'airplane',
        'bridge',
        'storage-tank',
        'ship',
        'swimming-pool',
        'vehicle',
        'person',
        'wind-mill'
    ]
    assert cfg.input_size == (800, 800)
