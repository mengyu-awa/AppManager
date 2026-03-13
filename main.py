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
    if response["main"]["version"] > version:                           #本程序版本不是最新版
        #print("update main")
        resp = requests.get(response["main"]["download"])               #下载新版安装程序
        with open("updater.exe","wb") as f:                             
            f.write(resp.content)
        os.startfile("updater.exe")                                     #安装新版
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
                resp = requests.get(response["others"]["Programs"][name]["download"])                                   #下载安装程序
                with open("updater.exe","wb") as f:
                    f.write(resp.content)
                os.startfile("updater.exe")                                                                             #运行安装程序以更新
                #time.sleep(10)
        else:
            #print("install " + name)
            resp = requests.get(response["others"]["Programs"][name]["download"])                                       #程序未正确安装，下载安装程序
            with open("updater.exe","wb") as f:
                f.write(resp.content)
            os.startfile("updater.exe")                                                                                 #安装
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

def wait_for_connect():
    """
    等待网络正常
    :return: 无返回值
    """
    while True:
        try:
            resp = requests.get(url)                                #测试连接是否正常                            
            if resp.status_code == 200:
                return
        except:
            time.sleep(30)                                          #不正常则30秒后重试


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
                resp = requests.get(response["others"]["Programs"][name]["download"])       #重新安装
                with open("updater.exe", "wb") as f:
                    f.write(resp.content)
                os.startfile("updater.exe")
                #time.sleep(10)
            elif not str(get_file_sha256(i["path"])) == i["SHA256"]:                        #有文件被替换
                #print("reinstall " + name)
                resp = requests.get(response["others"]["Programs"][name]["download"])       #重新安装
                with open("updater.exe","wb") as f:
                    f.write(resp.content)
                os.startfile("updater.exe")
                #time.sleep(10)

if __name__ == "__main__":
    wait_for_connect()          #等待网络
    update()                    #更新自身
    update_others()             #更新其他应用
    verify()                    #校验应用情况，并修复
    launch()                    #启动应用
