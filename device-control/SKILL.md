---
name: device-control
description: Control electronic test equipment including oscilloscopes, programmable power supplies, and other test instruments. Use when user mentions electronic test devices like oscilloscopes, power supplies, function generators, multimeters, etc. Supports operations such as reading measurements, capturing screenshots, setting parameters, and running automated tests.
---

# Device Control Skill

此 skill 用于协调控制 ~/test_script 目录下的电子测试设备。

## 可用设备 Skills

| 设备类型 | Skill | 说明 |
|----------|-------|------|
| 示波器 | @oscilloscope | Yokogawa (横河) DLM 系列示波器控制 |
| 电源 | @power-supply | 可编程电源控制 (如 ITECH IT6722) |
| 程控电阻 | @programmable-resistor | RM550 程控电阻设备控制 |

## 设备脚本索引

@/home/bonbon/test_script/CLAUDE.md

## 使用方法

### 查看可用脚本

用户询问可用设备或脚本时，读取 CLAUDE.md 文件。

### 控制具体设备

根据用户需求，使用相应的专业 skill：
- **示波器相关操作** → 使用 @oscilloscope skill
- **电源相关操作** → 使用 @power-supply skill
- **电阻相关操作** → 使用 @programmable-resistor skill

## 设备连接排查

当设备命令执行失败（如 "未找到 VISA 设备"）时：

1. **自动 attach 设备**（推荐）：
   - 执行 `pwsh.exe -Command "usbipd list"` 查看已共享的设备
   - 根据设备类型识别正确的 BUSID（示波器通常是 DLM series，电源通常是 USB Test and Measurement）
   - 执行 `pwsh.exe -Command "usbipd attach --busid <BUSID> --wsl"` attach 到 WSL

2. **使用交互式绑定脚本**：
   ```bash
   python ~/my_skills/device-control/scripts/bind_usb.py
   ```
   该脚本会：
   - 检查 usbipd 是否已安装
   - 扫描可用的 USB 设备
   - 引导用户选择并绑定设备到 WSL

## 未知设备处理

如果用户需要的设备在 CLAUDE.md 中不存在：

1. 询问用户：
   - 设备型号/品牌
   - 需要的操作功能
   - 是否有现成的控制脚本或 API

2. 根据回答创建新的设备 skill 或更新现有 skill

## 更新 CLAUDE.md

当用户通过 git clone 或其他方式添加新脚本到 ~/test_script 后：

1. 扫描 ~/test_script 目录下的脚本文件
2. 读取每个脚本的 README 或代码注释
3. 更新 CLAUDE.md 文件
