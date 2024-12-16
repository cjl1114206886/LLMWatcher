import os
import time
import yaml
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from multiprocessing import Process
import psutil
import getpass  # 获取当前用户名

CONFIG_PATH = "config.yaml"

def load_config():
    with open(CONFIG_PATH, "r") as file:
        return yaml.safe_load(file)

def send_email(config, subject, body):
    email_config = config["email"]
    try:
        msg = MIMEMultipart()
        msg['From'] = email_config['sender_email']
        msg['To'] = email_config['recipient_email']
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP_SSL(email_config["smtp_server"], email_config["smtp_port"]) as server:
            server.login(email_config["sender_email"], email_config["sender_password"])
            server.send_message(msg)

        print("邮件发送成功")
    except Exception as e:
        print(f"邮件发送失败: {e}")

def check_python_processes(config, monitored_processes):
    monitoring_config = config["monitoring"]
    keywords = monitoring_config["keywords"]
    current_user = getpass.getuser()

    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'username']):
        try:
            if proc.info['username'] == current_user and proc.info['name'] and 'python' in proc.info['name']:
                pid = proc.info['pid']
                if pid not in monitored_processes:
                    script_path = proc.info['cmdline'][-1] if proc.info['cmdline'] else None

                    if script_path and os.path.isfile(script_path):
                        with open(script_path, 'r') as script_file:
                            header = script_file.read(1024)
                            for keyword in keywords:
                                if keyword in header:
                                    monitored_processes[pid] = {
                                        'proc': proc,
                                        'script_path': script_path,
                                    }
                                    print(f"开始监控进程: {script_path} (PID: {pid})")
                                    break
        except Exception:
            continue

def capture_existing_output(pid):
    """
    读取共享库捕获的输出文件
    """
    current_user = getpass.getuser()
    output_file = f"/tmp/sms/captured_output_{current_user}_{pid}.log"
    output = ""
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            output = f.read()
    else:
        output = "无法获取程序输出，输出文件不存在。"
    return output

def monitor_processes(config):
    monitored_processes = {}
    while True:
        check_python_processes(config, monitored_processes)

        finished_pids = []
        for pid, info in monitored_processes.items():
            proc = info['proc']
            if not proc.is_running():
                print(f"检测到进程结束: {info['script_path']} (PID: {pid})")

                # 读取输出内容
                script_output = capture_existing_output(pid)

                # 准备邮件内容
                subject = "目标程序已结束"
                body = f"包含大模型库的 Python 脚本已结束运行：\n\n路径: {info['script_path']}\n进程 ID: {pid}\n\n程序输出:\n{script_output}"
                send_email(config, subject, body)

                # 清理
                finished_pids.append(pid)
                # 删除临时输出文件
                current_user = getpass.getuser()
                output_file = f"/tmp/captured_output_{current_user}_{pid}.log"
                if os.path.exists(output_file):
                    os.remove(output_file)

        for pid in finished_pids:
            del monitored_processes[pid]

        time.sleep(config["monitoring"]["check_interval"])

def daemonize():
    process = Process(target=monitor_processes, args=(load_config(),))
    process.daemon = True
    process.start()
    print(f"监控守护进程已启动 (PID: {process.pid})")
    process.join()

if __name__ == "__main__":
    daemonize()
