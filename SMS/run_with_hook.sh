#!/bin/bash

# 获取脚本所在目录路径
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 动态库相对于脚本所在目录的路径（假设 libcapture.so 和脚本在同一目录下）
LIB_PATH="$SCRIPT_DIR/libcapture.so"

# 检查动态库是否存在
if [ ! -f "$LIB_PATH" ]; then
    echo "Error: libcapture.so not found in $SCRIPT_DIR"
    exit 1
fi

# 如果用户没有传入参数，则提示使用方法
if [ $# -eq 0 ]; then
    echo "Usage: $0 [COMMAND or SCRIPT] [ARGS...]"
    echo "If a Python script is provided without a command, python3 will be used by default."
    echo "Examples:"
    echo "  $0 python3 your_script.py"
    echo "  $0 your_script.py"
    exit 1
fi

# 第一个参数可以是命令也可以是脚本名字
first_arg="$1"
shift # 移除第一个参数，剩下的是 ARGS

# 如果第一个参数不是可执行文件或已知的命令，则判断其是否为 Python 脚本
# 当没有指定解释器时，如果文件名以 .py 结尾，则默认为 python3
if [ ! -x "$(command -v "$first_arg")" ] && [[ "$first_arg" == *.py ]]; then
    # 第一个参数是一个 Python 脚本名称, 检查文件是否存在
    if [ ! -f "$first_arg" ]; then
        # 尝试使用当前目录查找脚本
        if [ ! -f "./$first_arg" ]; then
            echo "Error: script $first_arg not found."
            exit 1
        else
            first_arg="./$first_arg"
        fi
    fi
    # 自动为 Python 脚本添加默认解释器 python3
    command_to_run="python3 $first_arg $@"
else
    # 否则，用户已经指定了命令或这是个可执行文件
    # 直接使用用户指定的命令和参数
    command_to_run="$first_arg $@"
fi

# 设置LD_PRELOAD仅对本次命令生效
LD_PRELOAD="$LIB_PATH" $command_to_run
