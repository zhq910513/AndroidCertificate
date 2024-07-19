#!/usr/bin/python3
# -*- coding:utf-8 -*-

import os
import subprocess
import time

from CheckPhoneStatus import search_devices
from Logs.loggerDefine import loggerDefine

dir = os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")), "Logs/"))
logger = loggerDefine(dir, "AuthorityConfirmation", "")


# 通用 shell
def adb_shell(cmd):
    result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    return str(result.stdout.read())


# 手机 root
def check_root(udid=None):
    if not udid:
        phone_msg = search_devices()
        if not phone_msg:
            logger.warning('*** 请连接手机，并给手机root权限 ***')
        udid = phone_msg[0].split(r'\t')[0]

    for i in range(2):
        cmd = "adb -s {} root".format(udid)
        result = adb_shell(cmd)

        if "adbd is already running as root" in result:
            logger.info('--- 手机 {} 已获取root权限 ---'.format(udid))
            return True
        else:
            continue

    logger.warning('手机 {} 没有root权限'.format(udid))
    return False


# 手机 adb_authorized
def check_adb_authorized(device_msg):
    # 检查手机是否允许 adb 操作
    device_msg = str(device_msg).split(r'\t')
    udid = device_msg[0]
    msg = device_msg[1]

    if msg == "unauthorized":
        logger.info('--- 手机 {} 未允许在电脑使用adb操作，请在设置中打开 --- msg:【{}】'.format(udid, msg))
        return False
    return udid


# 解决目录 read only 关键命令行
def handle_read_only(udid=None):
    cmd = "adb -s {} disable-verity".format(udid)
    result = adb_shell(cmd)

    if "Verity already disabled on /system" in result:
        logger.info('--- 手机 {} 已处理read only ---'.format(udid))
        return True
    else:
        logger.warning('手机 {} 处理read only失败'.format(udid))
        return False


# 重新挂载
def handle_remount(udid=None):
    cmd = "adb -s {} remount".format(udid)
    result = adb_shell(cmd)

    if "remount succeeded" in result:
        logger.info('--- 手机 {} 已重新挂载 ---'.format(udid))
        return True
    else:
        logger.warning('手机 {} 重新挂载失败'.format(udid))
        return False


# 设置读写
def handle_read_write(udid=None):
    cmd = "adb -s {} shell mount -o rw,remount /system".format(udid)
    result = adb_shell(cmd)

    logger.info('--- 手机 {} 已设置读写 ---'.format(udid))
    return True


# 安装证书到安卓系统证书目录 /system/etc/security/cacerts
def push_hash_file(udid, file_path, file_name):
    file = os.path.abspath(os.path.join(file_path,file_name))
    cmd = "adb -s {} push {} /system/etc/security/cacerts".format(udid, file)
    result = adb_shell(cmd)

    time.sleep(1)
    cmd = "adb -s {} shell cat /system/etc/security/cacerts/{}".format(udid, file_name)
    result = adb_shell(cmd)
    if "BEGIN CERTIFICATE" in result:
        logger.info('--- 手机 {} 安装证书成功 ---'.format(udid))
        return True
    else:
        logger.warning('手机 {} 安装证书失败'.format(udid))
        return False