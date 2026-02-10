# Power Supply Skill

此 skill 用于通过 PyVISA 控制可编程电源设备，支持 SCPI 指令。已在 ITECH IT6722 上测试通过，同时支持 Yokogawa、Keysight、Tektronix、Rigol 等厂商设备。

## 设备脚本

- `~/.claude/skills/power-supply/scripts/power_ctrl/power_ctrl_cli.py` - 电源控制命令行工具
- `~/.claude/skills/power-supply/scripts/power_ctrl/power_supply_control.py` - 电源控制库及交互式工具

## 主要功能

- **设置电压** - 设置输出电压值
- **设置电流** - 设置电流限制
- **开关输出** - 打开或关闭电源输出
- **测量** - 读取当前电压和电流
- **列出设备** - 列出所有可用的 VISA 资源
- **本地模式切换** - 解锁前面板按键

## 常用命令

```bash
# 进入电源脚本目录
cd ~/.claude/skills/power-supply/scripts/power_ctrl

# 列出所有可用设备
uv run power_ctrl_cli.py -l

# 设置 5V，限流 1A 并打开输出（详细模式）
uv run power_ctrl_cli.py -v 5.0 -c 1.0 -o on --verbose

# 设置 5V，限流 1A，打开输出，并在结束后解锁面板
uv run power_ctrl_cli.py -v 5.0 -c 1.0 -o on --local

# 仅设置 9V 电压（不修改电流，不改变输出状态）
uv run power_ctrl_cli.py -v 9.0

# 关闭输出
uv run power_ctrl_cli.py -o off

# 仅测量当前状态
uv run power_ctrl_cli.py -m

# 交互式模式
uv run power_supply_control.py
```

## 交互式命令

在 `power_supply_control.py` 交互模式中：
- `v <数值>` - 设置电压 (例如 `v 12.0`)
- `c <数值>` - 设置电流限制 (例如 `c 2.0`)
- `on` / `off` - 打开或关闭输出
- `loc` - 切换到本地模式 (解锁前面板按键)
- `m` - 测量当前电压和电流
- `l` - 列出所有可用资源
- `q` - 退出

## 电源操作规则

当用户说 "设置电源电压" 时：
- **只设置电压**：使用 `-v <电压值>` 参数
- **不要同时设置电流**：不要添加 `-c` 参数
- **不要自动打开输出**：不要添加 `-o on` 参数
- 电源当前状态不变（包括电流限制和输出开关状态）

## 设备连接策略

- `power_supply_control.py`：优先自动连接 ITECH IT6722 设备
- `power_ctrl_cli.py`：默认强制搜索并连接 ITECH IT6722。如需控制其他设备，必须使用 `-a` 参数指定地址

## USB 权限问题 (Linux)

如果 `lsusb` 可见但脚本无法识别设备，添加 udev 规则：
```bash
echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="2ec7", ATTRS{idProduct}=="6700", MODE="0666"' | sudo tee /etc/udev/rules.d/99-itech.rules
sudo udevadm control --reload-rules
sudo udevadm trigger
# 拔掉 USB 再重新插入
```
