#!/usr/bin/env python3
"""LB所有档位电流测试 - 只测试典型值"""

import subprocess
import time
import os
from datetime import datetime

# 配置
CONFIG_FILE = "/home/bonbon/my_skills/bin_test/config/bin_res_lbhb.txt"
RES_PORT = "/dev/ttyUSB0"
VOLTAGE = 13.5

# 设备脚本路径
RES_SCRIPTS = "/home/bonbon/.claude/skills/programmable-resistor/scripts/res_ctrl"
PWR_SCRIPTS = "/home/bonbon/.claude/skills/power-supply/scripts/power_ctrl"
OSC_SCRIPTS = "/home/bonbon/.claude/skills/oscilloscope/scripts/yokogawa"

def discover_power_address():
    """自动发现电源VISA地址"""
    result = subprocess.run(f"cd {PWR_SCRIPTS} && uv run power_ctrl_cli.py -l", shell=True, capture_output=True, text=True)
    for line in result.stdout.split('\n'):
        if 'ITECH' in line or '2EC7' in line:
            return line.strip()
    return None

def load_config():
    """加载BIN配置，只提取典型值"""
    levels = []
    with open(CONFIG_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split(';')
            if len(parts) != 2:
                continue
            res_parts = parts[0].split(':')
            if len(res_parts) != 3:
                continue
            centre = int(res_parts[0])
            current = int(parts[1])
            levels.append({"resistance": centre, "current": current})
    return levels

def set_resistance(ohms):
    """设置电阻"""
    cmd = f"cd {RES_SCRIPTS} && uv run resistance_cli.py -p {RES_PORT} -v {ohms}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0

def power_cycle(pwr_address):
    """电源循环"""
    # 关闭
    subprocess.run(f"cd {PWR_SCRIPTS} && uv run power_ctrl_cli.py -a '{pwr_address}' -o off", shell=True, capture_output=True)
    time.sleep(2)
    # 开启
    result = subprocess.run(f"cd {PWR_SCRIPTS} && uv run power_ctrl_cli.py -a '{pwr_address}' -v {VOLTAGE} -o on", shell=True, capture_output=True, text=True)
    return result.returncode == 0

def measure_current():
    """测量CH4电流"""
    result = subprocess.run(f"cd {OSC_SCRIPTS} && uv run yokogawa_pyvisa.py mean -c 4", shell=True, capture_output=True, text=True)
    try:
        return float(result.stdout.strip())
    except:
        return None

def main():
    # 自动发现电源地址
    pwr_address = discover_power_address()
    if not pwr_address:
        print("错误: 无法找到电源设备，请检查USB连接")
        return
    print(f"发现电源: {pwr_address}")

    levels = load_config()
    print(f"加载了 {len(levels)} 个档位\n")

    results = []
    start_time = datetime.now()

    for i, level in enumerate(levels):
        level_num = i + 1
        res = level["resistance"]
        expected = level["current"]

        print(f"[{level_num:2d}/{len(levels)}] 测试 BIN_LEVEL_{level_num} - 电阻 {res}Ω, 预期 {expected}mA")

        # 设置电阻
        if not set_resistance(res):
            print(f"  失败: 电阻设置失败")
            results.append({"level": level_num, "res": res, "expected": expected, "measured": 0, "pass": False})
            continue

        # 电源循环
        if not power_cycle(pwr_address):
            print(f"  失败: 电源循环失败")
            results.append({"level": level_num, "res": res, "expected": expected, "measured": 0, "pass": False})
            continue

        # 测量
        time.sleep(1.5)
        measured = measure_current()

        if measured is None:
            print(f"  失败: 电流测量失败")
            results.append({"level": level_num, "res": res, "expected": expected, "measured": 0, "pass": False})
            continue

        # 验证 (±5%)
        tolerance = expected * 0.05
        passed = abs(measured - expected) <= tolerance

        error = ((measured - expected) / expected * 100) if expected > 0 else 0
        status = "通过" if passed else "失败"
        print(f"  结果: {measured:.1f}mA (预期 {expected}mA ±{tolerance:.1f}, 误差 {error:+.1f}%) [{status}]")

        results.append({"level": level_num, "res": res, "expected": expected, "measured": measured, "pass": passed})

    # 输出结果汇总
    print("\n" + "="*70)
    print("测试结果汇总")
    print("="*70)
    print(f"{'档位':<10} {'电阻(Ω)':<10} {'预期(mA)':<12} {'实测(mA)':<12} {'误差(%)':<10} {'结果'}")
    print("-"*70)

    passed_count = 0
    for r in results:
        status = "通过" if r["pass"] else "失败"
        if r["pass"]:
            passed_count += 1
        error = ((r["measured"] - r["expected"]) / r["expected"] * 100) if r["expected"] > 0 else 0
        print(f"BIN_LEVEL_{r['level']:<5} {r['res']:<10} {r['expected']:<12} {r['measured']:<12.1f} {error:>+8.1f}%  {status}")

    print("-"*70)
    print(f"总计: {passed_count}/{len(results)} 通过 ({passed_count/len(results)*100:.1f}%)")
    print(f"耗时: {datetime.now() - start_time}")

    # 保存结果
    output_file = f"/home/bonbon/.claude/skills/bin_test/result/lb_all_levels_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        f.write("# LB BIN测试结果\n")
        f.write(f"# 时间: {datetime.now()}\n")
        f.write(f"\nLevel,Resistance(Ω),Expected(mA),Measured(mA),Error(%),Result\n")
        for r in results:
            error = ((r["measured"] - r["expected"]) / r["expected"] * 100) if r["expected"] > 0 else 0
            status = "PASS" if r["pass"] else "FAIL"
            f.write(f"BIN_LEVEL_{r['level']},{r['res']},{r['expected']},{r['measured']:.2f},{error:+.2f},{status}\n")
    print(f"\n结果已保存到: {output_file}")

if __name__ == "__main__":
    main()
