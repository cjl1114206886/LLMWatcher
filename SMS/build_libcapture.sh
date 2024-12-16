#!/bin/bash

# 设置要编译的源文件和输出动态库文件名
SRC_FILE="capture_output.c"
OUTPUT_LIB="libcapture.so"

# 检查源文件是否存在
if [ ! -f "$SRC_FILE" ]; then
    echo "Error: $SRC_FILE not found!"
    exit 1
fi

# 使用 gcc 编译为共享库
# -fPIC: 生成与位置无关的代码
# -shared: 生成共享库
# -ldl: 链接 dl 库，用于 dlsym, dlopen 等函数
gcc -fPIC -shared -o "$OUTPUT_LIB" "$SRC_FILE" -ldl

# 检查编译结果
if [ $? -eq 0 ]; then
    echo "Successfully built $OUTPUT_LIB"
else
    echo "Failed to build $OUTPUT_LIB"
    exit 1
fi
