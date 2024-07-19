#!/usr/bin/python3
# -*- coding:utf-8 -*-

import os
import time
from multiprocessing.pool import ThreadPool
from multiprocessing import Process

from CheckMitmproxy import check_certificate_files, mitmproxy_path
from CheckPhoneStatus import search_devices, phone_reboot, adb_reboot
from AuthorityConfirmation import check_root, check_adb_authorized, handle_read_only, handle_remount, handle_read_write, \
    push_hash_file
from Logs.loggerDefine import loggerDefine

_dir = os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")), "Logs/"))
logger = loggerDefine(_dir, "run", "")


# 检查手机环境
def environment(device):
    # 检查手机是否允许 adb 操作
    adb_authorized = check_adb_authorized(device)
    if not adb_authorized: return

    else:
        # 手机以 root 权限运行
        root_authorized = check_root(adb_authorized)
        if not root_authorized: return

        else:
            # 解决目录 read only 关键命令行
            read_only_status = handle_read_only(adb_authorized)
            if not read_only_status: return

            # 重启
            reboot_status = phone_reboot(adb_authorized)
            if not reboot_status:return

            # 手机以 root 权限运行
            root_authorized = check_root(adb_authorized)
            if not root_authorized: return

            # 重新挂载
            remount_status = handle_remount(adb_authorized)
            if not remount_status: return

            # 设置读写
            read_write_status = handle_read_write(adb_authorized)
            if not read_write_status: return

            logger.info('--- 手机 {} 已准备好环境---'.format(adb_authorized))

            # 检查hash文件是否存在，push证书到手机系统
            file_dir = mitmproxy_path()

            file_status = False
            for t in range(5):
                for path, dirs, files in os.walk(file_dir):
                    for file in files:
                        if str(file).endswith('.0'):
                            # 安装证书到安卓系统证书目录 /system/etc/security/cacerts
                            push_hash_file(adb_authorized, file_dir, file)
                            file_status = True
                            break
                if not file_status:
                    time.sleep(10)
                else:
                    break


# 多线程执行检查环境
def CommandThread(remove_bad=False, Async=True):
    thread_list = []

    # 重启adb
    adb_reboot()

    # 检查在线手机
    devices = search_devices()
    if not devices: return

    # 设置线程数
    pool = ThreadPool(processes=len(devices))

    for device in devices:
        if Async:
            out = pool.apply_async(func=environment, args=(device,))  # 异步
        else:
            out = pool.apply(func=environment, args=(device,))  # 同步
        thread_list.append(out)

    pool.close()
    pool.join()

    # 获取输出结果
    com_list = []
    if Async:
        for p in thread_list:
            com = p.get()  # get会阻塞
            com_list.append(com)
    else:
        com_list = thread_list
    if remove_bad:
        com_list = [i for i in com_list if i is not None]
    return com_list


# 多线程处理证书与手机环境
def CommandProcess():
    p1 = Process(target=check_certificate_files, args=())  # 必须加,号
    p2 = Process(target=CommandThread, args=())

    p1.start()
    p2.start()
    p2.join()
    if p1.is_alive():
        p1.terminate()


if __name__ == '__main__':
    CommandProcess()
