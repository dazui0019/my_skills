---
name: gd32-cmake-generator
description: |
  Generate GD32 CMake projects from GD32 Firmware Library. Use when user wants to create a new GD32 embedded project with CMake build system. Handles: (1) Copying CMSIS and peripheral drivers from firmware library, (2) Generating CMakeLists.txt with proper compiler flags, (3) Setting up project directory structure similar to hello_cc example.
---

# GD32 CMake Project Generator

## 直接运行脚本生成项目

当用户提供以下信息时，直接运行 Python 脚本：
- 固件库路径 (必需)
- 芯片型号 (必需)
- 项目名称 (可选，默认: gd32_project)

### 运行脚本

获取参数后，使用 Bash 工具执行：

```bash
python "C:/Users/dazui/.claude/skills/gd32-cmake-generator/scripts/generate_project.py" <firmware_lib_path> <chip_model> [project_name]
```

**示例：**
- `python "C:/Users/dazui/.claude/skills/gd32-cmake-generator/scripts/generate_project.py" E:/Downloads/GD32F4xx_Firmware_Library_V3.3.3 GD32F407`
- `python "C:/Users/dazui/.claude/skills/gd32-cmake-generator/scripts/generate_project.py" E:/Downloads/GD32F4xx_Firmware_Library_V3.3.3 GD32F405 my_project`

## 支持的芯片型号

- GD32F405
- GD32F407
- GD32F425
- GD32F427
- GD32F450
- GD32F470
- GD32F103

## 编译项目

生成项目后，使用以下命令编译：

```bash
# Configure
cmake -B build -S . -DCMAKE_TOOLCHAIN_FILE="cmake/arm-none-eabi-gcc.cmake" -DCMAKE_GENERATOR="Ninja Multi-Config"

# Build
cmake --build .\build\ --config Release
```

## Example Invocation

User says: "Create a GD32F407 project from E:\Downloads\GD32F4xx_Firmware_Library_V3.3.3"

Output:
```
gd32_project/
├── .gitignore
├── CMakeLists.txt
├── cmake/
│   └── arm-none-eabi-gcc.cmake
├── Core/
│   ├── Inc/
│   │   ├── main.h
│   │   ├── gd32f4xx_it.h
│   │   └── systick.h
│   └── Src/
│       ├── main.c
│       ├── gd32f4xx_it.c
│       └── systick.c
├── Drivers/
│   ├── CMSIS/
│   │   ├── core_*.h
│   │   └── GD/
│   └── GD32F4xx_standard_peripheral/
└── Libraries/
    └── (第三方库文件)
```

## 输出文件

- `${PROJECT_NAME}.elf` - ELF 可执行文件
- `${PROJECT_NAME}.hex` - Intel HEX 格式
- `${PROJECT_NAME}.bin` - 二进制文件
- `${PROJECT_NAME}.list` - 反汇编列表
