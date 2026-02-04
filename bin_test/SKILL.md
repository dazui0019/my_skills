---
name: bin_test
description: BIN resistance level test tool for verifying that the LED current of the DUT matches the BIN resistance level. Depends on device-control skill for programmable resistor and power supply control. Uses headlight configuration for "LB/HB" queries and signal LED configuration (64 channels, current x64) for "TI/DRL/PL" queries.
---

# BIN Test Skill

This skill executes BIN resistance level testing to verify that the LED output current of the Device Under Test (DUT) matches the BIN resistance levels.

## Workflow

1. **Connection Check** - Ensure programmable resistor and power supply are connected
2. **Set BIN Resistance** - Configure programmable resistor value using `@programmable-resistor` skill
3. **Power Cycle DUT** - Cycle power using `@power-supply` skill to apply the new resistance value
4. **Measure Current** - Use `@oscilloscope` skill to read LED output current average from channel 4
5. **Result Validation** - Check if current is within ±5% tolerance

## Device Control (via device-control skill)

All device operations should use the corresponding device-control sub-skills:

| Operation | Skill to Use |
|-----------|--------------|
| Set BIN resistance | `@programmable-resistor` |
| Power on/off DUT | `@power-supply` |
| Measure current (CH4) | `@oscilloscope` |

## LED Type Recognition

Automatically selects configuration file based on user input:

| Keyword | LED Type | Config File | Current Multiplier |
|---------|----------|-------------|---------------------|
| LB, HB | Headlight | `bin_res_lbhb.txt` | 1x |
| TI, DRL, PL | Signal LED | `bin_res_sigled.txt` | 64x |

- **Headlight**: Single channel current configuration
- **Signal LED**: 64 channels, theoretical current automatically multiplied by 64

## Usage

### Quick Start

Run the automated test script:
```bash
python3 ~/.claude/skills/bin_test/scripts/run_bin_test.py
```

The script will prompt for:
1. Device serial port confirmation
2. LED type auto-detection (auto-selected when user says LB/HB/TI/DRL/PL)
3. List of levels to test
4. Power supply voltage

### Manual Single Level Test

Use device-control skills for device operations:

```bash
# 1. Set BIN resistance (use @programmable-resistor skill)
# Skill: programmable-resistor
# Scripts: ~/.claude/skills/programmable-resistor/scripts/res_ctrl/
# Command: cd ~/.claude/skills/programmable-resistor/scripts/res_ctrl/ && uv run resistance_cli.py -p /dev/ttyUSB0 -v 10000

# 2. Power cycle (use @power-supply skill)
# Skill: power-supply
# Scripts: ~/.claude/skills/power-supply/scripts/power_ctrl/
# Command: cd ~/.claude/skills/power-supply/scripts/power_ctrl/ && uv run power_ctrl_cli.py -v 13.5 -o on
# Wait 2 seconds, then: uv run power_ctrl_cli.py -o off

# 3. Measure current (use @oscilloscope skill)
# Skill: oscilloscope
# Scripts: ~/.claude/skills/oscilloscope/scripts/yokogawa/
# Command: cd ~/.claude/skills/oscilloscope/scripts/yokogawa/ && uv run yokogawa_pyvisa.py mean -c 4
```

## Configuration Files

| Directory | Purpose |
|-----------|---------|
| `~/.claude/skills/bin_test/config/` | BIN configuration files (bin_res_lbhb.txt, etc.) |
| `~/.claude/skills/bin_test/result/` | Test results (bin_test_result_*.csv) |

**Note**: Legacy files in `~/test_script/res_ctrl/` are still supported for backward compatibility.

**Format**: `typical:min:max;theoretical_current`

Example:
```
# Headlight
638:526:752;700

# Signal LED (64 channels)
2500:2450:2550;30  # Actual expected current 30x64=1920mA
```

## Dependent Devices

This skill depends on `device-control` skill for all device operations:

| Device | Purpose | Skill to Use |
|--------|---------|--------------|
| Programmable Resistor (RM550) | Set BIN resistance value | `@programmable-resistor` |
| Programmable Power Supply | Power the DUT, supports power cycling | `@power-supply` |
| Yokogawa Oscilloscope CH4 | Measure LED output current average | `@oscilloscope` |

## Device Connection Check

Before running the test, ensure devices are connected to WSL.

### Step 1: Check USBIPD Status on Windows

Run this command in WSL to check device binding status:
```bash
pwsh.exe -c "usbipd list"
```

Expected output shows device states:
- **Shared**: Device is bound but not attached to WSL
- **Not shared**: Device needs to be bound first
- **Persisted**: Device is remembered for automatic binding

**Typical devices:**
| Device | Type |
|--------|------|
| DLM series (Yokogawa) | Oscilloscope |
| USB-SERIAL CH340 | Programmable Resistor |
| USB Test and Measurement Device | Power Supply (ITECH) |

### Step 2: Attach Devices to WSL

If devices show **Shared** but not attached, run in Windows PowerShell:
```powershell
# Attach oscilloscope
pwsh.exe -c "usbipd attach --wsl --busid <BUSID>"

# Attach programmable resistor
pwsh.exe -c "usbipd attach --wsl --busid <BUSID>"
```

If devices show **Not shared**, first bind them:
```powershell
# Bind device (run as Administrator)
usbipd bind --busid <BUSID>

# Then attach to WSL
pwsh.exe -c "usbipd attach --wsl --busid <BUSID>"
```

### Step 3: Verify Connection in WSL

After attaching, verify devices are accessible:
```bash
# List USB devices (should show RM550, Yokogawa, etc.)
lsusb

# Check serial devices (Programmable Resistor)
ls /dev/ttyUSB*

# List VISA resources (Power Supply, Oscilloscope)
cd ~/.claude/skills/power-supply/scripts/power_ctrl && uv run power_ctrl_cli -l"
```

If devices are still not detected, use the `@device-control` skill for troubleshooting.

## Test Results

Results are automatically saved to `~/.claude/skills/bin_test/result/bin_test_result_YYYYMMDD_HHMMSS.csv`

**Note**: Results are saved in the skill's result directory.

**CSV Format**:
```csv
# Time: 2025-02-03 14:30:00
# LED Type: Headlight
# Test Levels: BIN_LEVEL_1, BIN_LEVEL_2
# Passed: 5/6

Level,Type,Resistance(Ω),Expected(mA),Measured(mA),Result,Error(%)
BIN_LEVEL_1,Typical,638,700,695.2,Pass,-0.69
BIN_LEVEL_1,Min,526,700,702.1,Pass,0.30
BIN_LEVEL_1,Max,752,700,Fail,0.0
...
Total,,,5/6,83.3%
```

## Key Features

- **BIN resistance is read at power-on only**: Resistance changes during operation are ineffective; power cycling is required
- **Each level tests 3 resistance values**: Typical, Minimum, Maximum
- **±5% tolerance range**: Current passes if within ±5% of expected value
- **Auto-save results**: CSV format for easy analysis
