# Programmable Resistor Skill

此 skill 用于控制 RM550 程控电阻设备，支持模拟 BIN 档位电阻以及 NTC 温度电阻特性。

## 设备脚本

- `~/test_script/res_ctrl/resistance_cli.py` - 通用电阻控制 CLI 工具
- `~/test_script/res_ctrl/temp_resistance_cli.py` - 基于温度的电阻设置工具

## 主要功能

- **设置电阻值** - 直接设置阻值或开路 (OPEN)
- **继电器控制** - connect/disconnect 控制继电器通断
- **短路控制** - short/unshort 控制短路状态
- **温度查表** - 根据温度查找对应 NTC 电阻值

## 常用命令

```bash
cd ~/test_script/res_ctrl

# 设置电阻为 1000 欧姆 (必须用 -p 指定串口号)
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

## 参数说明

| 参数 | 说明 |
|------|------|
| `-p`, `--port` | **(必填)** 串口号。Windows: `COMx`，Linux: `/dev/ttyUSBx` |
| `-v`, `--value` | 设置电阻值，支持数字或 "OPEN" |
| `--action` | 执行动作: `connect`, `disconnect`, `short`, `unshort` |
| `-t`, `--temp` | **(temp_resistance_cli.py 必填)** 目标温度 |
| `-f`, `--file` | **(temp_resistance_cli.py 必填)** 电阻值对应文件路径 |
| `--verbose` | 显示详细执行过程和日志信息 |

## 配置文件

- `ntc_res.txt` - NTC 热敏电阻温度对照表 (格式: `电阻值 ;温度注释`)
- `hb_lb_res.txt`, `lh_res.txt`, `signal_res.txt` - BIN 档位或信号电阻定义文件

## 重要说明

- **必须使用 `-p` 参数指定串口号**
- 执行单一指令后会**断开串口连接**，但**保持电阻器的物理状态**

## 串口排查

如果没有可用串口：

1. 确认设备已连接：`ls /dev/ttyUSB*`

2. **使用自动绑定脚本**（推荐）：
   ```bash
   python ~/.claude/skills/device-control/scripts/bind_usb.py
   ```
   脚本会自动扫描可用设备并引导绑定。

3. 手动绑定 USB 设备到 WSL：
   ```bash
   # 查看可用设备 (Windows PowerShell)
   pwsh.exe -Command "usbipd list"

   # 绑定设备 (替换 <busid> 为实际总线 ID)
   pwsh.exe -Command "usbipd attach --busid <busid> --wsl"
   ```
