#!/usr/bin/env python3
"""
BIN Test Runner - BIN电阻档位自动测试工具

此脚本执行 BIN 电阻档位测试：
1. 设置程控电阻值
2. 重新上下电使电阻生效
3. 使用示波器测量 LED 电流平均值
4. 验证结果是否在 ±5% 误差范围内

每个档位测试 3 个电阻值：典型值、最小值、最大值（覆盖采样误差范围）
"""

import subprocess
import sys
import time
import os

# 默认配置文件路径
DEFAULT_CONFIG_FILE = "~/test_script/res_ctrl/bin_res.txt"
DEFAULT_SIGLED_FILE = "~/test_script/res_ctrl/bin_res_sigled.txt"

# LED 类型配置
LED_TYPES = {
    "1": {"name": "大灯", "file": DEFAULT_CONFIG_FILE, "channel_multiplier": 1},
    "2": {"name": "信号灯", "file": DEFAULT_SIGLED_FILE, "channel_multiplier": 64},
}


def load_bin_config(config_file: str) -> dict:
    """从配置文件加载 BIN 配置"""
    config = {}
    abs_path = os.path.expanduser(config_file)

    if not os.path.exists(abs_path):
        print(f"  警告: 配置文件不存在 {abs_path}")
        return None

    with open(abs_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # 跳过空行和注释
            if not line or line.startswith('#'):
                continue

            # 格式: 典型值:最小值:最大值;理论电流值
            parts = line.split(';')
            if len(parts) != 2:
                continue

            try:
                res_parts = parts[0].split(':')
                if len(res_parts) != 3:
                    continue

                centre = int(res_parts[0].strip())
                min_r = int(res_parts[1].strip())
                max_r = int(res_parts[2].strip())
                current = int(parts[1].strip())

                # 容差 ±5%
                tolerance = current * 0.05

                # 生成档位名称 (按顺序: BIN_LEVEL_1_典型值, BIN_LEVEL_1_最小值, BIN_LEVEL_1_最大值, ...)
                bin_num = len(config) // 3 + 1
                res_type_idx = len(config) % 3
                res_types = ["典型值", "最小值", "最大值"]
                res_type = res_types[res_type_idx]
                bin_name = f"BIN_LEVEL_{bin_num}"

                config[f"{bin_name}_{res_type}"] = {
                    "bin_name": bin_name,
                    "res_type": res_type,
                    "resistance": centre if res_type == "典型值" else (min_r if res_type == "最小值" else max_r),
                    "current": current,
                    "tolerance": tolerance,
                }
            except (ValueError, IndexError):
                continue

    return config


def run_command(cmd: str, cwd: str = None) -> bool:
    """执行命令"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  失败: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"  错误: {e}")
        return False


def check_device(path: str) -> bool:
    """检查设备文件是否存在"""
    return subprocess.run(f"test -e {path}", shell=True).returncode == 0


def set_resistance(port: str, ohms: int) -> bool:
    """设置程控电阻值"""
    print(f"  设置电阻: {ohms}Ω")
    cmd = f"cd ~/test_script/res_ctrl && uv run resistance_cli.py -p {port} -v {ohms}"
    return run_command(cmd)


def power_cycle(port: str, voltage: float = 13.5) -> bool:
    """电源上下电"""
    print("  关闭电源...")
    off_cmd = f"cd ~/test_script/power_ctrl && uv run power_ctrl_cli.py -o off"
    if not run_command(off_cmd):
        return False

    time.sleep(2)

    print("  打开电源...")
    on_cmd = f"cd ~/test_script/power_ctrl && uv run power_ctrl_cli.py -v {voltage} -o on"
    if not run_command(on_cmd):
        return False

    time.sleep(1)
    return True


def measure_current() -> float:
    """使用示波器通道4测量电流平均值"""
    print("  正在通过示波器通道4读取电流均值...")
    cmd = "cd ~/test_script/yokogawa && uv run yokogawa_pyvisa.py mean -c 4"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            output = result.stdout.strip()
            try:
                value = float(output)
                print(f"  示波器读数: {value}")
                return value
            except ValueError:
                pass

        print(f"  自动读取失败: {result.stderr or output}")
    except Exception as e:
        print(f"  读取失败: {e}")

    print("  请手动输入电流值:")
    while True:
        try:
            value = input("  > ").strip()
            return float(value)
        except ValueError:
            print("  无效输入，请输入数字")


def verify_result(current: float, expected: float, tolerance: float) -> bool:
    """验证电流是否在 ±5% 误差范围内"""
    min_c = expected - tolerance
    max_c = expected + tolerance
    passed = min_c <= current <= max_c

    status = "通过" if passed else "失败"
    print(f"  结果: {current:.1f} (预期: {expected} ± {tolerance:.1f}, 范围: {min_c:.1f}-{max_c:.1f}) [{status}]")

    return passed


def main():
    print("=" * 60)
    print("BIN 档位测试工具")
    print("(每个档位测试: 典型值、最小值、最大值)")
    print("=" * 60)

    # 设备连接检查
    print("\n[1/5] 检查设备连接...")

    res_port = input("  程控电阻串口号 (默认 /dev/ttyUSB0): ").strip() or "/dev/ttyUSB0"
    pwr_port = input("  电源串口号 (默认 /dev/ttyUSB1): ").strip() or "/dev/ttyUSB1"

    if not check_device(res_port):
        print(f"  错误: 程控电阻 {res_port} 不存在")
        print("  请使用 device-control 的 bind_usb.py 绑定设备")
        sys.exit(1)

    if not check_device(pwr_port):
        print(f"  错误: 电源 {pwr_port} 不存在")
        print("  请使用 device-control 的 bind_usb.py 绑定设备")
        sys.exit(1)

    print("  设备检查通过")

    # 选择 LED 类型
    print("\n[2/5] 选择 LED 类型...")
    print("  1. 大灯 (headlights)")
    print("  2. 信号灯 (signal LED, 64通道)")
    led_type = input("  选择 (默认 1): ").strip() or "1"

    if led_type not in LED_TYPES:
        print("  无效选择，使用大灯")
        led_type = "1"

    led_config = LED_TYPES[led_type]
    print(f"  已选择: {led_config['name']}")

    # 加载配置
    print("\n[3/5] 加载 BIN 配置...")
    config_file = input(f"  配置文件路径 (默认 {led_config['file']}): ").strip() or led_config['file']
    channel_multiplier = led_config["channel_multiplier"]

    bin_config = load_bin_config(config_file)

    if not bin_config:
        print("  错误: 无法加载配置文件")
        sys.exit(1)

    # 应用通道倍数 (信号灯需要乘以64)
    if channel_multiplier > 1:
        for key in bin_config:
            bin_config[key]["current"] *= channel_multiplier
            bin_config[key]["tolerance"] *= channel_multiplier
        print(f"  已应用通道倍数: {channel_multiplier}x")

    print(f"  已加载 {len(bin_config)} 个测试点")

    # 获取档位列表
    bin_names = set()
    for key in bin_config.keys():
        bin_names.add(bin_config[key]["bin_name"])
    bin_names = sorted(bin_names, key=lambda x: int(x.split('_')[-1]))

    print("  可用档位:", ", ".join(bin_names))

    bins = input("  输入测试档位 (逗号分隔, 留空测试全部): ").strip().upper()

    if bins:
        test_bins = []
        for b in bins.split(","):
            b = b.strip()
            # 尝试匹配 BIN_LEVEL_X 格式
            if "BIN_LEVEL_" not in b and b.isdigit():
                b = f"BIN_LEVEL_{b}"
            if b in bin_names:
                test_bins.append(b)
    else:
        test_bins = bin_names

    if not test_bins:
        print("  无效档位，测试全部")
        test_bins = bin_names

    print(f"  将测试: {', '.join(test_bins)}")
    print(f"  每个档位包含 3 个测试点 (典型值、最小值、最大值)")

    # 初始化电源
    print("\n[4/5] 初始化电源...")
    voltage = float(input("  输入电源电压 (默认 13.5V): ").strip() or "13.5")
    if not run_command(f"cd ~/test_script/power_ctrl && uv run power_ctrl_cli.py -v {voltage} -o on"):
        print("  电源初始化失败")
        sys.exit(1)

    # 执行测试
    print("\n[5/5] 执行测试...")
    results = {}

    for bin_name in test_bins:
        print(f"\n{'='*50}")
        print(f"  测试 {bin_name}")
        print(f"{'='*50}")

        for res_type in ["典型值", "最小值", "最大值"]:
            key = f"{bin_name}_{res_type}"
            if key not in bin_config:
                continue

            print(f"\n  [{bin_name}] {res_type}...")
            config = bin_config[key]

            # 设置电阻
            if not set_resistance(res_port, config["resistance"]):
                results[key] = "电阻设置失败"
                continue

            # 上下电
            if not power_cycle(pwr_port, voltage):
                results[key] = "上下电失败"
                continue

            # 测量电流
            current = measure_current()

            # 验证结果
            if verify_result(current, config["current"], config["tolerance"]):
                results[key] = f"通过 ({current:.1f})"
            else:
                results[key] = f"失败 ({current:.1f})"

    # 输出结果
    print("\n[6/6] 测试结果")
    print("-" * 60)
    print(f"{'档位':<14} {'类型':<8} {'电阻':<10} {'预期电流':<12} {'结果':<20}")
    print("-" * 60)

    for bin_name in test_bins:
        for res_type in ["典型值", "最小值", "最大值"]:
            key = f"{bin_name}_{res_type}"
            if key not in results:
                continue

            config = bin_config.get(key, {})
            result = results[key]
            print(f"{bin_name:<14} {res_type:<8} {config.get('resistance', '-'):<10} {config.get('current', '-'):<12} {result:<20}")

    print("-" * 60)

    passed = sum(1 for r in results.values() if "通过" in r)
    total = len(results)
    print(f"总计: {passed}/{total} 测试点通过")

    # 保存结果
    print("\n保存测试结果...")
    output_file = save_results(test_bins, results, bin_config, passed, total)
    print(f"结果已保存到: {output_file}")

    # 关闭电源
    print("\n关闭电源...")
    run_command(f"cd ~/test_script/power_ctrl && uv run power_ctrl_cli.py -o off")


def save_results(test_bins: list, results: dict, bin_config: dict, passed: int, total: int) -> str:
    """保存测试结果到文件"""
    from datetime import datetime

    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"~/test_script/res_ctrl/bin_test_result_{timestamp}.csv"

    abs_path = os.path.expanduser(output_file)

    led_type = "大灯" if "sigled" not in bin_config.get(list(bin_config.keys())[0], {}).get("bin_name", "") else "信号灯"

    with open(abs_path, 'w', encoding='utf-8') as f:
        f.write("# BIN 测试结果\n")
        f.write(f"# 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# LED类型: {led_type}\n")
        f.write(f"# 测试档位: {', '.join(test_bins)}\n")
        f.write(f"# 通过: {passed}/{total}\n")
        f.write("\n")

        f.write("档位,类型,电阻(Ω),预期电流(mA),实测电流(mA),结果,误差(%)\n")

        for bin_name in test_bins:
            for res_type in ["典型值", "最小值", "最大值"]:
                key = f"{bin_name}_{res_type}"
                if key not in results:
                    continue

                config = bin_config.get(key, {})
                result = results[key]

                # 解析实测电流
                measured = 0.0
                if "通过" in result or "失败" in result:
                    try:
                        measured = float(result.split("(")[1].replace(")", ""))
                    except (IndexError, ValueError):
                        pass

                # 计算误差
                expected = config.get("current", 0)
                error_pct = 0.0
                if expected > 0 and measured > 0:
                    error_pct = ((measured - expected) / expected) * 100

                status = "通过" if "通过" in result else "失败"

                f.write(f"{bin_name},{res_type},{config.get('resistance', '-')},{expected},{measured:.1f},{status},{error_pct:.2f}\n")

        f.write("\n")
        f.write(f"总计,,,,{passed}/{total},{passed/total*100:.1f}%\n")

    return output_file


if __name__ == "__main__":
    main()
