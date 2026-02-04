# CLAUDE.md - Device Control Scripts Reference

此文件记录 ~/test_script 目录下所有可用的设备控制脚本。

## res_ctrl

程控电阻控制工具，用于控制 RM550 设备，支持模拟 BIN 档位电阻以及 NTC 温度电阻特性。

| 脚本 | 功能 |
|------|------|
| `res_ctrl/resistance_cli.py` | 通用电阻控制 CLI 工具，支持设置阻值、控制继电器/短路状态。执行单一指令后断开串口连接，但保持电阻器物理状态。 |
| `res_ctrl/temp_resistance_cli.py` | 基于温度的电阻设置工具，通过查表将温度转换为对应电阻值。 |

### 环境准备

本项目使用 [uv](https://github.com/astral-sh/uv) 管理 Python 环境：
```bash
cd ~/my_skills/programmable-resistor/scripts/res_ctrl && uv sync
```

### 主要功能

- **设置电阻值** - 直接设置阻值或开路 (OPEN)
- **继电器控制** - connect/disconnect 控制继电器通断
- **短路控制** - short/unshort 控制短路状态
- **温度查表** - 根据温度查找对应 NTC 电阻值

### 常用命令

```bash
cd ~/my_skills/programmable-resistor/scripts/res_ctrl

# 设置电阻为 1000 欧姆
uv run resistance_cli.py -p /dev/ttyUSB0 -v 1000

# 设置电阻为开路
uv run resistance_cli.py -p /dev/ttyUSB0 -v OPEN

# 闭合/断开继电器
uv run resistance_cli.py -p /dev/ttyUSB0 --action connect
uv run resistance_cli.py -p /dev/ttyUSB0 --action disconnect

# 短路/取消短路
uv run resistance_cli.py -p /dev/ttyUSB0 --action short
uv run resistance_cli.py -p /dev/ttyUSB0 --action unshort

# 根据温度设置电阻 (需指定 NTC 查表文件)
uv run temp_resistance_cli.py -p /dev/ttyUSB0 -t 25 -f ntc_res.txt
uv run temp_resistance_cli.py -p /dev/ttyUSB0 -t -40 -f ntc_res.txt

# 详细输出模式
uv run resistance_cli.py -p /dev/ttyUSB0 -v 1000 --verbose
```

### 参数说明

| 参数 | 说明 |
|------|------|
| `-p`, `--port` | **(必填)** 串口号。Windows: `COMx`，Linux: `/dev/ttyUSBx` |
| `-v`, `--value` | 设置电阻值，支持数字或 "OPEN" |
| `--action` | 执行动作: `connect`, `disconnect`, `short`, `unshort` |
| `-t`, `--temp` | **(temp_resistance_cli.py 必填)** 目标温度 |
| `-f`, `--file` | **(temp_resistance_cli.py 必填)** 电阻值对应文件路径 |
| `--verbose` | 显示详细执行过程和日志信息 |

### 配置文件

- `ntc_res.txt` - NTC 热敏电阻温度对照表 (格式: `电阻值 ;温度注释`)
- `hb_lb_res.txt`, `lh_res.txt`, `signal_res.txt` - BIN 档位或信号电阻定义文件

### 串口排查

如果没有可用串口：

1. 确认设备已连接：`ls /dev/ttyUSB*`

2. **使用自动绑定脚本**（推荐）：
   ```bash
   python ~/my_skills/device-control/scripts/bind_usb.py
   ```
   脚本会自动扫描可用设备并引导绑定。

3. 手动绑定 USB 设备到 WSL：
   ```bash
   # 查看可用设备 (Windows PowerShell)
   pwsh.exe -Command "usbipd list"

   # 绑定设备 (替换 <busid> 为实际总线 ID)
   pwsh.exe -Command "usbipd attach --busid <busid> --wsl"
   ```

## yokogawa

| 脚本 | 功能 |
|------|------|
| `yokogawa/yokogawa.py` | Yokogawa (横河) DLM 系列示波器控制工具 (Windows)，支持读取均值、截图。 |
| `yokogawa/yokogawa_pyvisa.py` | Yokogawa (横河) DLM 系列示波器控制工具 (Linux)，支持读取均值、截图、列出设备。 |

### 主要功能

- **mean** - 读取指定通道的 Mean (平均值)
- **shot** - 获取屏幕截图并保存为 PNG
- **list** - 列出系统可用的 VISA 设备资源 (仅 Linux)

### 常用命令

```bash
# Linux - 读取通道4均值 (默认仅输出数值)
cd ~/my_skills/oscilloscope/scripts/yokogawa && uv run yokogawa_pyvisa.py mean -c 4

# Linux - 详细输出模式
cd ~/my_skills/oscilloscope/scripts/yokogawa && uv run yokogawa_pyvisa.py mean -c 4 -v

# Linux - 截图保存
cd ~/my_skills/oscilloscope/scripts/yokogawa && uv run yokogawa_pyvisa.py shot -o screen.png

# Linux - 列出可用设备
cd ~/my_skills/oscilloscope/scripts/yokogawa && uv run yokogawa_pyvisa.py list

# Windows - 读取均值
cd ~/my_skills/oscilloscope/scripts/yokogawa && uv run yokogawa.py mean

# Windows - 指定IP截图
cd ~/my_skills/oscilloscope/scripts/yokogawa && uv run yokogawa.py --ip 192.168.1.100 shot
```

## power_ctrl

| 脚本 | 功能 |
|------|------|
| `power_ctrl/power_ctrl_cli.py` | 可编程电源控制命令行工具，支持设置电压/电流、开关输出、测量。 |
| `power_ctrl/power_supply_control.py` | 电源控制库及交互式工具。 |

### 主要功能

- **设置电压** - 设置输出电压值
- **设置电流** - 设置电流限制
- **开关输出** - 打开或关闭电源输出
- **测量** - 读取当前电压和电流
- **列出设备** - 列出所有可用的 VISA 资源

### 常用命令

```bash
# 列出所有可用设备
cd ~/my_skills/power-supply/scripts/power_ctrl && uv run power_ctrl_cli.py -l

# 设置 5V，限流 1A 并打开输出
cd ~/my_skills/power-supply/scripts/power_ctrl && uv run power_ctrl_cli.py -v 5.0 -c 1.0 -o on

# 关闭输出
cd ~/my_skills/power-supply/scripts/power_ctrl && uv run power_ctrl_cli.py -o off

# 仅测量当前状态
cd ~/my_skills/power-supply/scripts/power_ctrl && uv run power_ctrl_cli.py -m

# 交互式模式
cd ~/my_skills/power-supply/scripts/power_ctrl && uv run power_supply_control.py
```
