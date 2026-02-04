#!/usr/bin/env python3
"""
USB Device Binding Script for WSL

此脚本帮助将 Windows 上连接的 USB 设备绑定到 WSL 环境。
需要 Windows 上已安装 usbipd 工具。
"""

import subprocess
import sys


def run_powershell(cmd: str) -> str:
    """运行 Windows PowerShell 命令"""
    try:
        result = subprocess.run(
            ["pwsh.exe", "-Command", cmd],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout + result.stderr
    except Exception as e:
        return f"执行失败: {e}"


def list_usb_devices() -> list[dict]:
    """列出可用的 USB 设备"""
    output = run_powershell("usbipd list")

    devices = []
    for line in output.strip().split("\n"):
        if "BUSID" in line or "---" in line or not line.strip():
            continue

        parts = line.split()
        if len(parts) >= 3:
            busid = parts[0]
            vid_pid = parts[1] if len(parts) > 1 else ""
            device_name = " ".join(parts[2:]) if len(parts) > 2 else ""

            # 过滤已绑定的设备
            if "[Attached]" not in line and "[BoundToWsld]" not in line:
                devices.append({
                    "busid": busid,
                    "vid_pid": vid_pid,
                    "name": device_name
                })

    return devices


def bind_device(busid: str) -> bool:
    """将设备绑定到 WSL"""
    print(f"正在将设备 {busid} 绑定到 WSL...")
    output = run_powershell(f"usbipd attach --busid {busid} --wsl")

    if "success" in output.lower() or "已成功" in output:
        print(f"成功: {output}")
        return True
    else:
        print(f"结果: {output}")
        return "成功" in output or "success" in output.lower()


def main():
    print("=" * 50)
    print("USB 设备绑定工具 (WSL)")
    print("=" * 50)

    # 检查 usbipd 是否可用
    print("\n[1/3] 检查 usbipd 工具...")
    check_output = run_powershell("usbipd --version")
    if "usbipd" not in check_output.lower():
        print("错误: 未找到 usbipd 工具。")
        print("请先在 Windows 上安装 usbipd：")
        print("  winget install --id=USBIPd  (或从 https://github.com/dorssel/usbipd-win 下载)")
        sys.exit(1)
    print("usbipd 已安装")

    # 列出可用设备
    print("\n[2/3] 扫描可用 USB 设备...")
    devices = list_usb_devices()

    if not devices:
        print("\n未找到可绑定的 USB 设备。")
        print("可能原因：")
        print("  - 设备未连接到 Windows")
        print("  - 设备已被绑定到 WSL")
        print("\n所有 USB 设备状态：")
        all_devices = run_powershell("usbipd list")
        print(all_devices)
        sys.exit(0)

    print(f"\n找到 {len(devices)} 个可绑定的设备：")
    for i, dev in enumerate(devices, 1):
        print(f"  {i}. {dev['busid']}  {dev['vid_pid']}  {dev['name']}")

    # 选择设备
    print(f"\n[3/3] 绑定设备")
    print("请选择要绑定的设备编号 (输入 q 退出): ", end="")

    while True:
        choice = input().strip()

        if choice.lower() == 'q':
            print("已取消")
            sys.exit(0)

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(devices):
                if bind_device(devices[idx]["busid"]):
                    print("\n绑定成功！设备现可在 WSL 中使用。")
                    print(f"串口号通常为: /dev/ttyUSB0 或 /dev/ttyACM0")
                else:
                    print("\n绑定可能失败，请检查上方输出或手动重试。")
                sys.exit(0)
            else:
                print(f"无效选择，请输入 1-{len(devices)} 或 q 退出: ", end="")
        except ValueError:
            print("请输入数字或 q 退出: ", end="")


if __name__ == "__main__":
    main()
