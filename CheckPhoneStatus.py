#!/usr/bin/python3
# -*- coding:utf-8 -*-

import os
import subprocess
import re
import time

from Logs.loggerDefine import loggerDefine

dir = os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")), "Logs/"))
logger = loggerDefine(dir, "CheckPhoneStatus", "")


# 通用shell
def adb_shell(cmd):
    result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    return str(result.stdout.read())


# 查询设备
def search_devices():
    cmd = "adb devices"
    devices = [msg for msg in re.findall(r'\\n(.*?)\\r', adb_shell(cmd), re.S) if msg]
    if not devices:
        logger.warning('*** 请连接手机，并给手机root权限 ***')
    logger.info('--- 已连接 {} 台手机 ---'.format(len(devices)))
    return devices


# 手机重启
def phone_reboot(udid):
    cmd = "adb -s {} reboot".format(udid)
    adb_shell(cmd)

    status = True
    status_count = 0
    while status:
        if status_count > 60:
            break

        devices = [msg for msg in re.findall(r'\\n(.*?)\\r', adb_shell("adb devices"), re.S) if msg]
        for device in devices:
            if udid not in device:
                logger.info('--- 手机 {} 重启中， 请等待... ---'.format(udid))
                time.sleep(15)

            else:
                time.sleep(30)
                logger.info('--- 手机 {} 已重启 ---'.format(udid))
                return True


# 重置adb server
def adb_reboot():
    logger.info('adb server 重启中， 请稍等...')
    cmd = "adb kill-server"
    result = adb_shell(cmd)
    time.sleep(3)

    cmd = "adb start-server"
    result = adb_shell(cmd)
    time.sleep(1)