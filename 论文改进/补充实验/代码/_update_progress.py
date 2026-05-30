"""
Auto-update progress file after experiment completion.
Import and call `update_progress(experiment_number, status, key_result="")` at end of main().
"""
import os
import re
from datetime import datetime


_PROGRESS_FILE = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "..", "..", "20260529_补充实验进度.md"))


# Map script name to experiment number
_EXP_MAP = {
    "run_phase63_ablation": 1,
    "run_random_split": 2,
    "run_brdf_sensitivity": 3,
    "run_occlusion_analysis": 4,
    "run_resnet_baseline": 5,
    "run_noise_robustness": 6,
    "run_roll_sensitivity": 7,
}

_EXP_NAMES = {
    1: "Phase63 公平消融",
    2: "随机 80/20 split",
    3: "BRDF 参数敏感性",
    4: "遮挡 w/ vs w/o",
    5: "ResNet-18 baseline",
    6: "OCS 噪声鲁棒性",
    7: "Roll 小规模敏感性",
}


def update_progress(exp_name, status, key_result="", output_dir=""):
    """Update the progress file with experiment status.

    Args:
        exp_name: e.g. "run_roll_sensitivity"
        status: one of "completed", "running", "failed"
        key_result: one-line summary of key finding
        output_dir: where results were saved
    """
    exp_num = _EXP_MAP.get(exp_name)
    if exp_num is None:
        print(f"[update_progress] Unknown experiment: {exp_name}")
        return

    if not os.path.exists(_PROGRESS_FILE):
        print(f"[update_progress] Progress file not found: {_PROGRESS_FILE}")
        return

    with open(_PROGRESS_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Find the table row for this experiment and update its status
    exp_label = _EXP_NAMES[exp_num]
    pattern = rf"(\| {exp_num} \| .*{exp_label}.*\| )(待运行|⚠️.*\|)(.*)$"
    replacement = rf"\1✅ 已完成 | {datetime.now().strftime('%Y-%m-%d %H:%M')}\3"

    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

    # If key_result provided, append to the completed experiments section
    if key_result:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Find the "## 已完成实验" section and append
        section_marker = "## 已完成实验"
        if section_marker in content:
            result_entry = (
                f"\n### 实验 {exp_num}：{exp_label}\n\n"
                f"- **产物**：`论文改进/补充实验/结果/{output_dir}`\n"
                f"- **结论**：{key_result}\n"
            )
            # Insert after the section header (after first two lines following it)
            # Find the next "###" or "---" after the section marker
            idx = content.find(section_marker)
            # Find the next section heading after this one
            next_section = content.find("\n## ", idx + len(section_marker))
            if next_section == -1:
                next_section = len(content)
            content = content[:next_section] + result_entry + content[next_section:]

    with open(_PROGRESS_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[update_progress] Updated {_PROGRESS_FILE} for experiment {exp_num}")
