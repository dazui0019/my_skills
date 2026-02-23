#!/usr/bin/env python3
"""
GD32 CMake Project Generator

Usage:
    python generate_project.py <firmware_lib_path> <chip_model> [project_name]

Examples:
    python generate_project.py E:/File/MCU/GD32 GD32F407
    python generate_project.py E:/File/MCU/GD32 GD32F405 my_project
    python generate_project.py E:/Downloads/GD32F4xx_Firmware_Library GD32F407
"""

import os
import sys
import shutil
import json
from pathlib import Path


# Default library base path
DEFAULT_LIB_BASE = Path("E:/File/MCU/GD32")

# Chip series to firmware library mapping
CHIP_SERIES_MAP = {
    "GD32F4": "GD32F4xx_Firmware_Library",
    "GD32F1": "GD32F1xx_Firmware_Library",
    "GD32F3": "GD32F3xx_Firmware_Library",
}


# Chip configuration mapping
CHIP_CONFIG = {
    "GD32F405": {
        "cpu": "cortex-m4",
        "float_abi": "hard",
        "fpu": "fpv4-sp-d16",
        "defines": "GD32F405",
        "linker": "gd32f405_405_407_xE_flash.ld",
        "startup": "startup_gd32f405_425.S"
    },
    "GD32F407": {
        "cpu": "cortex-m4",
        "float_abi": "hard",
        "fpu": "fpv4-sp-d16",
        "defines": "GD32F407",
        "linker": "gd32f405_407_xE_flash.ld",
        "startup": "startup_gd32f407_427.S"
    },
    "GD32F425": {
        "cpu": "cortex-m4",
        "float_abi": "hard",
        "fpu": "fpv4-sp-d16",
        "defines": "GD32F425",
        "linker": "gd32f425_427_xE_flash.ld",
        "startup": "startup_gd32f405_425.S"
    },
    "GD32F427": {
        "cpu": "cortex-m4",
        "float_abi": "hard",
        "fpu": "fpv4-sp-d16",
        "defines": "GD32F427",
        "linker": "gd32f427_427_437_xE_flash.ld",
        "startup": "startup_gd32f407_427.S"
    },
    "GD32F450": {
        "cpu": "cortex-m4",
        "float_abi": "hard",
        "fpu": "fpv4-sp-d16",
        "defines": "GD32F450",
        "linker": "gd32f450_470_xE_flash.ld",
        "startup": "startup_gd32f450_470.S"
    },
    "GD32F470": {
        "cpu": "cortex-m4",
        "float_abi": "hard",
        "fpu": "fpv4-sp-d16",
        "defines": "GD32F470",
        "linker": "gd32f450_470_xE_flash.ld",
        "startup": "startup_gd32f450_470.S"
    },
    "GD32F103": {
        "cpu": "cortex-m3",
        "float_abi": "soft",
        "fpu": "",
        "defines": "GD32F103",
        "linker": "gd32f103xe.ld",
        "startup": "startup_gd32f103xe.s"
    }
}


def copy_directory(src: Path, dst: Path):
    """Copy directory recursively."""
    if not src.exists():
        raise FileNotFoundError(f"Source directory not found: {src}")

    # Create destination parent if needed
    dst.mkdir(parents=True, exist_ok=True)

    # Copy files and subdirectories
    for item in src.rglob("*"):
        if item.is_file():
            rel_path = item.relative_to(src)
            dest_file = dst / rel_path
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest_file)


def generate_cmakelists(project_name: str, chip_config: dict, output_dir: Path):
    """Generate CMakeLists.txt file from template."""

    # Get skill template directory
    skill_dir = Path(__file__).parent.parent
    template_cmake = skill_dir / "template" / "CMakeLists.txt"

    if not template_cmake.exists():
        raise FileNotFoundError(f"CMakeLists.txt template not found: {template_cmake}")

    # Read template
    with open(template_cmake, "r", encoding="utf-8") as f:
        cmake_content = f.read()

    # Replace project name
    cmake_content = cmake_content.replace("project(hello_world)", f"project({project_name})")

    # Replace chip definition (e.g., -DGD32F407)
    for chip in CHIP_CONFIG.values():
        cmake_content = cmake_content.replace(f"-D{chip['defines']}", f"-D{chip_config['defines']}")

    # Replace linker script
    for chip in CHIP_CONFIG.values():
        if "linker" in chip:
            cmake_content = cmake_content.replace(chip["linker"], chip_config["linker"])

    # Replace startup script
    for chip in CHIP_CONFIG.values():
        if "startup" in chip:
            cmake_content = cmake_content.replace(chip["startup"], chip_config.get("startup", "startup_gd32f407_427.S"))

    # Write to output
    with open(output_dir / "CMakeLists.txt", "w", encoding="utf-8") as f:
        f.write(cmake_content)


def generate_cmake_toolchain():
    """Generate cmake toolchain file."""
    content = """# ARM GCC Toolchain settings for GD32

set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR ARM)

# Toolchain paths - adjust if needed
# set(CMAKE_PREFIX_PATH /path/to/arm-none-eabi-gcc)

# Find compiler
find_program(CMAKE_C_COMPILER arm-none-eabi-gcc)
find_program(CMAKE_CXX_COMPILER arm-none-eabi-g++)
find_program(CMAKE_ASM_COMPILER arm-none-eabi-gcc)
find_program(CMAKE_OBJCOPY arm-none-eabi-objcopy)
find_program(CMAKE_OBJDUMP arm-none-eabi-objdump)
find_program(CMAKE_SIZE arm-none-eabi-size)

if(NOT CMAKE_C_COMPILER)
    message(FATAL_ERROR "arm-none-eabi-gcc not found. Please install ARM GCC toolchain.")
endif()

# Skip compiler tests
set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)
"""

    return content


def generate_gitignore():
    """Generate .gitignore file for embedded project."""
    return '''# Build outputs
build/
*.o
*.a
*.elf
*.hex
*.bin
*.list
*.map

# IDE
.idea/
*.swp
*.swo
*~

# Python
__pycache__/
*.pyc

# OS
.DS_Store
Thumbs.db

# CMake
CMakeCache.txt
CMakeFiles/
cmake_install.cmake
Makefile
*.cmake

# Ninja
.ninja_*
*.ninja

# Toolchain
*.launch
*.cfg
'''


def generate_readme(project_name: str, chip_model: str):
    chip_info = CHIP_CONFIG.get(chip_model, CHIP_CONFIG["GD32F407"])

    return f'''# {project_name} - {chip_model} Project

## Overview

A GD32 {chip_model} CMake project.

## Hardware

- MCU: {chip_model}
- Core: ARM {chip_info["cpu"].replace("cortex-", "Cortex-").upper()} with FPU
- Float ABI: {chip_info["float_abi"]}

## Build

```bash
# Configure
cmake -B build -S . -DCMAKE_TOOLCHAIN_FILE="cmake/arm-none-eabi-gcc.cmake" -DCMAKE_GENERATOR="Ninja Multi-Config"

# Build
cmake --build .\\build\\ --config Release
```

## Output

- `build/Release/{project_name}.elf` - ELF file
- `build/Release/{project_name}.hex` - HEX file
- `build/Release/{project_name}.bin` - Binary file

## Flash

```bash
# Using pyocd
pyocd flash -t {chip_model} build/Release/{project_name}.bin

# Using J-Link
JLinkGDBServer -device {chip_model}VK -if SWD -speed 4000

# Using ST-Link
openocd -f interface/stlink.cfg -f target/stm32f4x.cfg -c "program build/Release/{project_name}.elf verify reset exit"
```

## Requirements

- arm-none-eabi-gcc
- CMake
- Ninja
- pyocd (optional)
'''
    return '''/*!
    \\file    main.h
    \\brief   main header file
*/

#ifndef __MAIN_H
#define __MAIN_H

#include "gd32f4xx.h"

#endif /* __MAIN_H */
'''


def generate_main_source(chip_model: str):
    """Generate main.c with blinky example."""
    return f'''/*!
    \\file    main.c
    \\brief   main program
*/

#include "main.h"

void SystemClock_Config(void);
void Led_Config(void);

/*!
    \\brief    main function
    \\param[in]  none
    \\param[out] none
    \\retval     none
*/
int main(void)
{{
    /* configure systick */
    systick_config();

    /* configure system clock */
    SystemClock_Config();

    /* configure LED */
    Led_Config();

    /* print system clock */
    // rcu_periph_clock enable must be after SystemClock_Config for USART
    // rcu_periph_clock_enable(RCU_USART0);
    // printf("System Clock: %lu Hz\\n", rcu_clock_freq_get(CK_SYS));

    while (1) {{
        /* toggle LED */
        gpio_bit_toggle(GPIOA, GPIO_PIN_1);
        /* insert delay */
        delay_1ms(500);
    }}
}}

/*!
    \\brief    configure system clock
    \\param[in]  none
    \\param[out] none
    \\retval     none
*/
void SystemClock_Config(void)
{{
    /* enable PWR clock */
    rcu_periph_clock_enable(RCU_PMU);
    /* configure voltage */
    pmu_ldo_output_config(PMU_LDO_OUTPUT_NORMAL);

    /* wait PWR clock ready */
    while (SET != pmu_flag_get(PMU_FLAG_LDO)) {{
    }}

    /* configure HXTAL */
    rcu_hxtal_central_25m_50m_config(RCU_HXTAL_25M_50M);

    /* configure PLL */
    rcu_pll_config(RCU_PLL_HXTAL);
    rcu_system_clock_source_config(RCU_CKPLL_SRC_HXTAL);
    /* enable PLL */
    rcu_osci_on(RCU_PLL_CK);
    /* wait PLL stable */
    while (RESET == rcu_flag_get(RCU_FLAG_PLLSTB)) {{
    }}

    /* configure AHB, APB1, APB2 */
    rcu_ahb_clock_config(RCU_AHB_CK_SYS);
    rcu_apb1_clock_config(RCU_APB1_CK_AHB_DIV2);
    rcu_apb2_clock_config(RCU_APB2_CK_AHB_DIV1);

    /* select PLL as system clock source */
    rcu_system_clock_source_config(RCU_CKPLL_SRC_HXTAL);
    while (RESET != rcu_system_clock_source_get(RCU_CK_PLL)) {{
    }}

    /* configure USART clock */
    rcu_periph_clock_enable(RCU_USART0);
}}

/*!
    \\brief    configure LED
    \\param[in]  none
    \\param[out] none
    \\retval     none
*/
void Led_Config(void)
{{
    /* enable GPIO clock */
    rcu_periph_clock_enable(RCU_GPIOA);

    /* configure LED pin */
    gpio_mode_set(GPIOA, GPIO_MODE_OUTPUT, GPIO_PUPD_NONE, GPIO_PIN_1);
    gpio_output_options_set(GPIOA, GPIO_OTYPE_PP, GPIO_OSPEED_50MHZ, GPIO_PIN_1);

    /* LED off */
    gpio_bit_reset(GPIOA, GPIO_PIN_1);
}}
'''


def generate_it_header():
    """Generate gd32f4xx_it.h"""
    return '''/*!
    \\file    gd32f4xx_it.h
    \\brief   the header file of the interrupt service routine
*/

#ifndef __GD32F4XX_IT_H
#define __GD32F4XX_IT_H

#include "gd32f4xx.h"

#endif /* __GD32F4XX_IT_H */
'''


def generate_it_source():
    """Generate gd32f4xx_it.c"""
    return '''/*!
    \\file    gd32f4xx_it.c
    \\brief   the service routine for the different exceptions
*/

#include "gd32f4xx_it.h"

void NMI_Handler(void)
{
}

void HardFault_Handler(void)
{
    while (1) {
    }
}

void MemManage_Handler(void)
{
    while (1) {
    }
}

void BusFault_Handler(void)
{
    while (1) {
    }
}

void UsageFault_Handler(void)
{
    while (1) {
    }
}

void SVC_Handler(void)
{
}

void DebugMon_Handler(void)
{
}

void PendSV_Handler(void)
{
}

void SysTick_Handler(void)
{
}
'''


def generate_systick_header():
    """Generate systick.h"""
    return '''/*!
    \\file    systick.h
    \\brief   the header file of the systick
*/

#ifndef __SYSTICK_H
#define __SYSTICK_H

#include "gd32f4xx.h"

void systick_config(void);
void delay_1ms(uint32_t count);

#endif /* __SYSTICK_H */
'''


def generate_systick_source():
    """Generate systick.c"""
    return '''/*!
    \\file    systick.c
    \\brief   the configuration of the systick
*/

#include "systick.h"

volatile static uint32_t delay;

/*!
    \\brief    configure systick
    \\param[in]  none
    \\param[out] none
    \\retval     none
*/
void systick_config(void)
{
    /* setup systick timer for 1000Hz */
    if (SysTick_Config(SystemCoreClock / 1000)) {
        /* capture error */
        while (1) {
        }
    }
    /* configure systick */
    SysTick->CTRL &= ~SysTick_CTRL_ENABLE_Msk;
}

/*!
    \\brief    delay 1ms
    \\param[in]  count: delay count
    \\param[out] none
    \\retval     none
*/
void delay_1ms(uint32_t count)
{
    delay = count;
    while (delay) {
    }
}

/*!
    \\brief    delay decrement
    \\param[in]  none
    \\param[out] none
    \\retval     none
*/
void SysTick_Handler(void)
{
    if (delay > 0) {
        delay--;
    }
}
'''


def find_pack_file(chip_model: str) -> str:
    """Find the CMSIS pack file for the given chip model."""
    # Common locations for CMSIS pack files
    search_paths = [
        Path.home() / "AppData" / "Local" / "cmsis-pack-manager" / "cmsis-pack-manager" / "Pack",
    ]

    # Chip manufacturer to pack name mapping
    chip_to_pack = {
        "GD32F4": "GigaDevice.GD32F4xx_DFP",
        "GD32F1": "GigaDevice.GD32F1xx_DFP",
        "GD32F3": "GigaDevice.GD32F3xx_DFP",
    }

    # Determine pack prefix based on chip model
    pack_prefix = None
    for prefix, pack_name in chip_to_pack.items():
        if chip_model.startswith(prefix):
            pack_prefix = pack_name
            break

    if not pack_prefix:
        return ""

    # Search for pack file
    for search_path in search_paths:
        if not search_path.exists():
            continue

        # Look for pack files matching the pattern
        for pack_dir in search_path.rglob(f"{pack_prefix}*"):
            if pack_dir.is_file() and pack_dir.suffix == ".pack":
                return str(pack_dir)
            # Check if it's a directory with .pack inside
            for pack_file in pack_dir.rglob("*.pack"):
                return str(pack_file)

    print(f"Warning: Could not find pack file for {chip_model}")
    return ""


def generate_vscode_settings(chip_model: str, project_name: str):
    """Generate settings.json with replaced variables."""
    # Get skill template directory
    skill_dir = Path(__file__).parent.parent
    template_settings = skill_dir / "template" / ".vscode" / "settings.json"

    if not template_settings.exists():
        return None

    # Read template
    with open(template_settings, "r", encoding="utf-8") as f:
        settings_content = f.read()

    # Find pack file and escape backslashes for JSON
    pack_file = find_pack_file(chip_model)
    # Escape backslashes for JSON format (Windows paths)
    pack_file_escaped = pack_file.replace("\\", "\\\\")

    # Replace variables
    replacements = {
        "<chip>": chip_model,
        "<pack_file>": pack_file_escaped,
        "<hex_file>": f"{project_name}.hex",
    }

    for placeholder, value in replacements.items():
        settings_content = settings_content.replace(placeholder, value)

    return settings_content


def generate_project(firmware_path: str, chip_model: str, project_name: str = "gd32_project"):
    """Generate the complete GD32 project."""

    firmware_path = Path(firmware_path)
    project_dir = Path.cwd() / project_name

    # Check if target directory is not empty
    if project_dir.exists() and any(project_dir.iterdir()):
        raise ValueError(f"Target directory '{project_dir}' is not empty. Please remove it first or choose a different project name.")

    # Get skill template directory
    skill_dir = Path(__file__).parent.parent

    print(f"Generating GD32 project: {project_dir}")
    print(f"Chip model: {chip_model}")
    print(f"Firmware library: {firmware_path}")

    # Get chip config
    if chip_model not in CHIP_CONFIG:
        print(f"Warning: Unknown chip {chip_model}, using GD32F407 config")
        chip_config = CHIP_CONFIG["GD32F407"]
    else:
        chip_config = CHIP_CONFIG[chip_model]

    # Create project directory structure with parents
    dirs_to_create = [
        project_dir / "cmake",
        project_dir / "Core" / "Inc",
        project_dir / "Core" / "Src",
        project_dir / "Drivers",
        project_dir / "Libraries",
    ]
    for d in dirs_to_create:
        d.mkdir(parents=True, exist_ok=True)

    # Copy firmware files
    firmware_dir = firmware_path / "Firmware"

    print("Copying CMSIS files...")
    cmsis_src = firmware_dir / "CMSIS"
    cmsis_dst = project_dir / "Drivers" / "CMSIS"
    if cmsis_src.exists():
        # Copy GD folder
        copy_directory(cmsis_src / "GD", cmsis_dst / "GD")
        # Copy core files
        for f in cmsis_src.glob("core_*.h"):
            shutil.copy2(f, cmsis_dst / f.name)
    else:
        print(f"Warning: CMSIS directory not found: {cmsis_src}")

    print("Copying peripheral drivers...")
    periph_src = firmware_dir / "GD32F4xx_standard_peripheral"
    periph_dst = project_dir / "Drivers" / "GD32F4xx_standard_peripheral"
    if periph_src.exists():
        copy_directory(periph_src, periph_dst)
    else:
        print(f"Warning: Peripheral directory not found: {periph_src}")

    print("Generating CMakeLists.txt...")
    generate_cmakelists(project_name, chip_config, project_dir)

    print("Generating README.md...")
    readme_content = generate_readme(project_name, chip_model)
    with open(project_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

    print("Generating .gitignore...")
    gitignore_content = generate_gitignore()
    with open(project_dir / ".gitignore", "w", encoding="utf-8") as f:
        f.write(gitignore_content)

    print("Copying cmake toolchain file...")
    toolchain_src = skill_dir / "template" / "arm-none-eabi-gcc.cmake"
    shutil.copy2(toolchain_src, project_dir / "cmake" / "arm-none-eabi-gcc.cmake")

    # Copy .vscode directory if exists
    template_vscode_dir = skill_dir / "template" / ".vscode"
    if template_vscode_dir.exists():
        print("Copying .vscode files...")
        copy_directory(template_vscode_dir, project_dir / ".vscode")

        # Generate and write settings.json with replaced variables
        settings_content = generate_vscode_settings(chip_model, project_name)
        if settings_content:
            print("Updating .vscode/settings.json with chip configuration...")
            settings_path = project_dir / ".vscode" / "settings.json"
            with open(settings_path, "w", encoding="utf-8") as f:
                f.write(settings_content)

    print("Copying Core files from template...")

    # Determine template subdirectory based on chip series
    if chip_model.startswith("GD32F4"):
        chip_series = "F4"
    elif chip_model.startswith("GD32F1"):
        chip_series = "F1"
    else:
        chip_series = "F4"  # default

    template_core_dir = skill_dir / "template" / "Core" / chip_series
    if not template_core_dir.exists():
        print(f"Warning: Template directory not found: {template_core_dir}")
    else:
        # Copy files from template - separate .h to Inc and .c to Src
        for f in template_core_dir.rglob("*"):
            if f.is_file() and f.suffix in ['.h', '.c']:
                if f.suffix == '.h':
                    dest_dir = project_dir / "Core" / "Inc"
                else:
                    dest_dir = project_dir / "Core" / "Src"
                dest_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, dest_dir / f.name)

    print(f"\nProject generated successfully: {project_dir}")
    print("\nTo build:")
    print(f"  cd {project_dir}")
    print(f"  mkdir build && cd build")
    print(f"  cmake -DCMAKE_BUILD_TYPE=Debug ..")
    print(f"  cmake --build .")


def get_firmware_path(input_path: str, chip_model: str) -> Path:
    """Get firmware library path based on input and chip model."""
    input_path = Path(input_path)

    # If input is already a firmware library directory (contains Firmware subfolder)
    if (input_path / "Firmware").exists():
        return input_path

    # If input is a base directory like E:\File\MCU\GD32, auto-detect based on chip series
    for series_prefix, lib_folder in CHIP_SERIES_MAP.items():
        if chip_model.startswith(series_prefix):
            firmware_path = input_path / lib_folder
            if firmware_path.exists():
                return firmware_path
            # Also check if lib_folder exists directly in the input directory
            for item in input_path.iterdir():
                if item.is_dir() and lib_folder.lower() in item.name.lower():
                    return item

    # Fallback: return input path as-is
    return input_path


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        print(f"\nDefault library base: {DEFAULT_LIB_BASE}")
        print("\nSupported chips:")
        for chip in CHIP_CONFIG:
            print(f"  - {chip}")
        sys.exit(1)

    input_path = sys.argv[1]
    chip_model = sys.argv[2]
    project_name = sys.argv[3] if len(sys.argv) > 3 else "gd32_project"

    # Get firmware path based on input and chip model
    firmware_path = get_firmware_path(input_path, chip_model)

    print(f"Using firmware library: {firmware_path}")

    try:
        generate_project(str(firmware_path), chip_model, project_name)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
