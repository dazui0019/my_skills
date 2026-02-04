# Oscilloscope Skill

此 skill 用于控制 Yokogawa (横河) DLM 系列示波器。

## 设备脚本

- `~/test_script/yokogawa/yokogawa.py` - Windows 版本
- `~/test_script/yokogawa/yokogawa_pyvisa.py` - Linux 版本

## 主要功能

- **mean** - 读取指定通道的 Mean (平均值)
- **shot** - 获取屏幕截图并保存为 PNG
- **list** - 列出系统可用的 VISA 设备资源 (仅 Linux)

## 常用命令

### Linux

```bash
# 读取通道4均值 (默认仅输出数值)
cd ~/test_script/yokogawa && uv run yokogawa_pyvisa.py mean -c 4

# 详细输出模式
cd ~/test_script/yokogawa && uv run yokogawa_pyvisa.py mean -c 4 -v

# 截图保存
cd ~/test_script/yokogawa && uv run yokogawa_pyvisa.py shot -o screen.png

# 列出可用设备
cd ~/test_script/yokogawa && uv run yokogawa_pyvisa.py list
```

### Windows

```bash
# 读取均值
cd ~/test_script/yokogawa && uv run yokogawa.py mean

# 指定IP截图
cd ~/test_script/yokogawa && uv run yokogawa.py --ip 192.168.1.100 shot
```

## 注意事项

- **读取均值时，默认仅输出数值** (干净模式)。如需详细日志输出，添加 `-v/--verbose` 参数
