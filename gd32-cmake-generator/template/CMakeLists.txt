cmake_minimum_required(VERSION 3.17.0)
project(hello_world)

# Enable languages
enable_language(C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add cmake module path
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# LTO option
option(USE_LTO "Enable LTO" ON)

if(USE_LTO)
    include(CheckIPOSupported)
    check_ipo_supported(RESULT supported OUTPUT error)
    set(CMAKE_INTERPROCEDURAL_OPTIMIZATION TRUE)
endif()

# Multi-config generator support
get_property(isMultiConfig GLOBAL PROPERTY GENERATOR_IS_MULTI_CONFIG)
if(isMultiConfig)
    set(CMAKE_CROSS_CONFIGS "Release;Debug")
    set(CMAKE_DEFAULT_BUILD_TYPE "Release")
    set(CMAKE_DEFAULT_CONFIGS "Release;Debug")
endif()

# Colored output
option(FORCE_COLORED_OUTPUT "Always produce ANSI-colored output (GNU/Clang only)." TRUE)
if(${FORCE_COLORED_OUTPUT})
    if("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
       add_compile_options(-fdiagnostics-color=always)
    elseif("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")
       add_compile_options(-fcolor-diagnostics)
    endif()
endif()

# Suppress warnings for newer GCC
if(CMAKE_CXX_COMPILER_VERSION VERSION_GREATER_EQUAL 12.0)
    add_link_options(-Wl,--no-warn-rwx-segments)
endif()

# Chip definition
add_definitions(
    -DGD32F407
)

# Compile options
add_compile_options(
    -mcpu=cortex-m4 -mfloat-abi=hard -mfpu=fpv4-sp-d16 -specs=nosys.specs -ffunction-sections -fdata-sections -fstack-usage -ffast-math
    "$<$<CONFIG:Debug>:-Og;-DDEBUG;-g;-funwind-tables>"
    "$<$<CONFIG:Release>:-O2;-DNDEBUG>"
    "$<$<CONFIG:MinSizeRel>:-Os;-DNDEBUG>"
    "$<$<CONFIG:RelWithDebInfo>:-O2;-g;-DNDEBUG>"
)

# Link options
add_link_options(
    -mcpu=cortex-m4 -mfloat-abi=hard -mfpu=fpv4-sp-d16 -specs=nosys.specs -ffunction-sections -fdata-sections -fstack-usage -ffast-math -static -u _printf_float -Wl,--start-group -lc -lm -lstdc++ -lsupc++ -Wl,--end-group -Wl,--gc-sections
    -T${PROJECT_SOURCE_DIR}/Drivers/CMSIS/GD/GD32F4xx/Source/GCC/Ld/gd32f405_407_xE_flash.ld
)

set(CMAKE_EXECUTABLE_SUFFIX .elf)

# Source directories (all .c files in Core/Src)
file(GLOB CORE_SRC
    "${PROJECT_SOURCE_DIR}/Core/Src/*.c"
)

set(CMSIS_SRC
    ${PROJECT_SOURCE_DIR}/Drivers/CMSIS/GD/GD32F4xx/Source/system_gd32f4xx.c
)

# Startup files (GCC)
set(STARTUP_FILE ${PROJECT_SOURCE_DIR}/Drivers/CMSIS/GD/GD32F4xx/Source/GCC/startup_gd32f407_427.S)

# Standard peripheral sources (all .c files)
file(GLOB PERIPH_SRC
    "${PROJECT_SOURCE_DIR}/Drivers/GD32F4xx_standard_peripheral/Source/*.c"
)

# Add executable
add_executable(${PROJECT_NAME}
    ${CORE_SRC}
    ${CMSIS_SRC}
    ${STARTUP_FILE}
    ${PERIPH_SRC}
)

# Include directories
target_include_directories(${PROJECT_NAME} PRIVATE
    ${PROJECT_SOURCE_DIR}/Core/Inc
    ${PROJECT_SOURCE_DIR}/Drivers/CMSIS/GD/GD32F4xx/Include
    ${PROJECT_SOURCE_DIR}/Drivers/CMSIS
    ${PROJECT_SOURCE_DIR}/Drivers/GD32F4xx_standard_peripheral/Include
)

# Post-build: generate bin/hex/list files
add_custom_command(TARGET ${PROJECT_NAME}
    POST_BUILD
    COMMAND ${CMAKE_OBJDUMP} -h -S $<TARGET_FILE:${PROJECT_NAME}> > $<TARGET_FILE_DIR:${PROJECT_NAME}>/${PROJECT_NAME}.list
    COMMAND ${CMAKE_OBJCOPY} -O ihex $<TARGET_FILE:${PROJECT_NAME}> $<TARGET_FILE_DIR:${PROJECT_NAME}>/${PROJECT_NAME}.hex
    COMMAND ${CMAKE_OBJCOPY} -O binary $<TARGET_FILE:${PROJECT_NAME}> $<TARGET_FILE_DIR:${PROJECT_NAME}>/${PROJECT_NAME}.bin
)

# Print size info
add_custom_command(TARGET ${PROJECT_NAME}
    POST_BUILD
    COMMAND ${CMAKE_SIZE_UTIL} $<TARGET_FILE:${PROJECT_NAME}>
)
