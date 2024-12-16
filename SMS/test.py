import time
import os
import torch
from time import sleep

if __name__ == '__main__':
    # 打印当前进程的PID
    print(f"Current Process PID: {os.getpid()}", flush=True)

    a = 0
    if a == 0:
        print('afasdfasgadsgad', flush=True)
        a = a + 1

    # 休眠50秒
    time.sleep(50)

    # 打印当前工作目录
    print(os.getcwd(), flush=True)
