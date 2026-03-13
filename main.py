import requests
import os
import sys
import time
import hashlib

url = "https://mengyu-awa.github.io/mywebsite/data.json"

response = requests.get(url).json()

version = 0

def update():
    """
    更新本程序
    :return:无返回值
    """
    if response["main"]["version"] > version:
        #print("update main")
        resp = requests.get(response["main"]["download"])
        with open("updater.exe","wb") as f:
            f.write(resp.content)
        os.startfile("updater.exe")
        sys.exit(0)

def update_others():
    """
    更新其他程序
    :return: 无返回值
    """
    for name in response["others"]["list"]:
        if os.path.exists(os.path.join(response["others"]["Programs"][name]["program_path"],"version.txt")):
            with open(os.path.join(response["others"]["Programs"][name]["program_path"],"version.txt"), "r") as f:
                v = int(f.read())
            if v < response["others"]["Programs"][name]["latest_version"]:
                #print("update "+name)
                resp = requests.get(response["others"]["Programs"][name]["download"])
                with open("updater.exe","wb") as f:
                    f.write(resp.content)
                os.startfile("updater.exe")
                time.sleep(10)
        else:
            #print("install " + name)
            resp = requests.get(response["others"]["Programs"][name]["download"])
            with open("updater.exe","wb") as f:
                f.write(resp.content)
            os.startfile("updater.exe")
            time.sleep(10)

def launch():
    """
    开机启动其他程序
    :return: 无返回值
    """
    for file in response["launch"]["active_list"]:
        #print("launching " + file)
        os.startfile(file)

def wait_for_connect():
    """
    等待网络正常
    :return: 无返回值
    """
    while True:
        resp = requests.get(url)
        if resp.status_code == 200:
            return
        time.sleep(30)


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
    for name in response["others"]["list"]:
        for i in response["verify"][name]["Files"]:
            if not os.path.exists(os.path.join(i["path"])):
                #print("reinstall "+name)
                resp = requests.get(response["others"]["Programs"][name]["download"])
                with open("updater.exe", "wb") as f:
                    f.write(resp.content)
                os.startfile("updater.exe")
                time.sleep(10)
            elif not str(get_file_sha256(i["path"])) == i["SHA256"]:
                #print("reinstall " + name)
                resp = requests.get(response["others"]["Programs"][name]["download"])
                with open("updater.exe","wb") as f:
                    f.write(resp.content)
                os.startfile("updater.exe")
                time.sleep(10)

if __name__ == "__main__":
    wait_for_connect()
    update()
    update_others()
    verify()
    launch()