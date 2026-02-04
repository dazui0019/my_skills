---
name: bin_test
description: BIN resistance level test tool for verifying that the LED current of the DUT matches the BIN resistance level. Depends on device-control skill for programmable resistor and power supply control. Uses headlight configuration for "LB/HB" queries and signal LED configuration (64 channels, current x64) for "TI/DRL/PL" queries.
---

# BIN Test Skill

This skill executes BIN resistance level testing to verify that the LED output current of the Device Under Test (DUT) matches the BIN resistance levels.

## Workflow

1. **Connection Check** - Ensure programmable resistor and power supply are connected
2. **Set BIN Resistance** - Configure programmable resistor value based on test level
3. **Power Cycle DUT** - Cycle power to apply the new resistance value
4. **Measure Current** - Use oscilloscope channel 4 to read LED output current average
5. **Result Validation** - Check if current is within ±5% tolerance

## LED Type Recognition

Automatically selects configuration file based on user input:

| Keyword | LED Type | Config File | Current Multiplier |
|---------|----------|-------------|---------------------|
| LB, HB | Headlight | `bin_res.txt` | 1x |
| TI, DRL, PL | Signal LED | `bin_res_sigled.txt` | 64x |

- **Headlight**: Single channel current configuration
- **Signal LED**: 64 channels, theoretical current automatically multiplied by 64

## Usage

### Quick Start

Run the automated test script:
```bash
python ~/.claude/skills/bin_test/scripts/run_bin_test.py
```

The script will prompt for:
1. Device serial port confirmation
2. LED type auto-detection (auto-selected when user says LB/HB/TI/DRL/PL)
3. List of levels to test
4. Power supply voltage

### Manual Single Level Test

```bash
# 1. Set BIN resistance
cd ~/test_script/res_ctrl && uv run resistance_cli.py -p /dev/ttyUSB0 -v 10000

# 2. Power cycle
cd ~/test_script/power_ctrl && uv run power_ctrl_cli.py -o off
sleep 2
cd ~/test_script/power_ctrl && uv run power_ctrl_cli.py -v 13.5 -o on

# 3. Measure current (oscilloscope channel 4)
cd ~/test_script/yokogawa && uv run yokogawa_pyvisa.py mean -c 4
```

## Configuration Files

| File | Purpose |
|------|---------|
| `~/test_script/res_ctrl/bin_res.txt` | Headlight BIN configuration (23 levels) |
| `~/test_script/res_ctrl/bin_res_sigled.txt` | Signal LED BIN configuration (15 levels) |

**Format**: `typical:min:max;theoretical_current`

Example:
```
# Headlight
638:526:752;700

# Signal LED (64 channels)
2500:2450:2550;30  # Actual expected current 30x64=1920mA
```

## Dependent Devices

This skill depends on `device-control` skill:

| Device | Purpose |
|--------|---------|
| Programmable Resistor (RM550) | Set BIN resistance value |
| Programmable Power Supply | Power the DUT, supports power cycling |
| Yokogawa Oscilloscope CH4 | Measure LED output current average |

## Device Connection Check

```bash
# Check serial devices
ls /dev/ttyUSB*

# Check programmable resistor
cd ~/test_script/res_ctrl && uv run resistance_cli.py -p /dev/ttyUSB0 -v OPEN

# Check power supply
cd ~/test_script/power_ctrl && uv run power_ctrl_cli.py -l

# Check oscilloscope
cd ~/test_script/yokogawa && uv run yokogawa_pyvisa.py list
```

If devices are not listed:
```bash
python ~/.claude/skills/device-control/scripts/bind_usb.py
```

## Test Results

Results are automatically saved to `~/test_script/res_ctrl/bin_test_result_YYYYMMDD_HHMMSS.csv`

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
