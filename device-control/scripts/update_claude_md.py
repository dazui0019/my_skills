#!/usr/bin/env python3
"""更新 CLAUDE.md 文件，自动扫描 ~/test_script 目录下的脚本"""

import os
import re
from pathlib import Path

TEST_SCRIPT_DIR = Path.home() / "test_script"
CLAUDE_MD_PATH = TEST_SCRIPT_DIR / "CLAUDE.md"

def find_scripts_and_readmes():
    """扫描目录，查找脚本和 README"""
    scripts = {}
    readmes = {}

    for root, dirs, files in os.walk(TEST_SCRIPT_DIR):
        # 忽略隐藏目录和特殊目录
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for file in files:
            path = Path(root) / file
            rel_path = path.relative_to(TEST_SCRIPT_DIR)

            # 跳过 lib 目录下的文件
            parts = str(rel_path).split('/')
            if any('lib' in p for p in parts):
                continue

            if file.lower().startswith('readme'):
                readmes[str(rel_path.parent)] = path
            elif file.endswith(('.py', '.sh')) and not file.startswith('_'):
                scripts[str(rel_path)] = path

    return scripts, readmes

def get_script_summary(script_path):
    """从脚本或 README 提取一句话摘要"""
    # 优先读取同名 README
    readme_path = script_path.parent / f"README.md"
    if readme_path.exists():
        content = readme_path.read_text()
        # 提取第一段描述性文字
        lines = content.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('|'):
                return line[:100]  # 截断到100字符
        # 如果没找到，尝试第一行
        if lines:
            return lines[0].strip('#').strip()[:100]

    # 读取脚本注释
    content = script_path.read_text()
    # 找 docstring 或首行注释
    match = re.search(r'["\']{3}(.+?)["\']{3}', content, re.DOTALL)
    if match:
        summary = match.group(1).strip().split('\n')[0]
        return summary[:100]

    return "设备控制脚本"

def generate_claude_md():
    """生成 CLAUDE.md 内容"""
    scripts, readmes = find_scripts_and_readmes()

    # 按目录分组
    groups = {}
    for rel_path, script_path in scripts.items():
        dir_name = str(rel_path).split('/')[0]
        if dir_name not in groups:
            groups[dir_name] = []
        groups[dir_name].append((rel_path, script_path))

    lines = [
        "# CLAUDE.md - Device Control Scripts Reference",
        "",
        "此文件记录 ~/test_script 目录下所有可用的设备控制脚本。",
        ""
    ]

    for dir_name, script_list in sorted(groups.items()):
        lines.append(f"## {dir_name}")
        lines.append("")
        lines.append("| 脚本 | 功能 |")
        lines.append("|------|------|")

        for rel_path, script_path in sorted(script_list):
            summary = get_script_summary(script_path)
            lines.append(f"| `{rel_path}` | {summary} |")

        lines.append("")

    content = '\n'.join(lines)
    CLAUDE_MD_PATH.write_text(content)
    print(f"已更新 {CLAUDE_MD_PATH}")

if __name__ == "__main__":
    generate_claude_md()
