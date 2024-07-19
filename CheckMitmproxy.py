#!/usr/bin/python3
# -*- coding:utf-8 -*-

import os
import re
import shutil
import sys
import threading
import time

import psutil

from AuthorityConfirmation import adb_shell
from Logs.loggerDefine import loggerDefine

dir = os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")), "Logs/"))
logger = loggerDefine(dir, "CheckMitmproxy", "")


# 全局查找mitmproxy文件夹
def mitmproxy_path():
    tfs = [re.search(r"='(.*?)\\'", str(tf)).group(1) for tf in psutil.disk_partitions() if re.search(r"='(.*?)\\'", str(tf)).group(1)]
    for file_dir in tfs:
        for path, dirs, files in os.walk(file_dir):
            if path.endswith('\.mitmproxy'):
                logger.info('--- 查找到路径 {} ---'.format(path))
                return os.path.abspath(path)
        return False


# 查找所有文件
def select_files(file_dir):
    for path, dirs, files in os.walk(file_dir):
        logger.info('--- 查找到所有文件：{} ---'.format(files))
        return files


# 检查文件
def check_certificate_files():
    # mitmproxy证书路径
    file_dir = mitmproxy_path()

    # 返回所有文件
    files = select_files(file_dir)

    # 如果空  则重新创建
    if not file_dir or not files:
        cmd = "mitmdump"
        task = threading.Thread(target=adb_shell, args=(cmd,))
        task.start()
        logger.info('--- 重新加载mitmproxy证书 ---')

        # 返回所有文件
        time.sleep(10)
        files = select_files(file_dir)


    # 检查是否有已转换的文件
    fp_status = False
    for fp in files:
        if fp.endswith('.0'):
            fp_status = True

    # 检查是否有已转换的文件
    ca_cert_status = False
    if 'mitmproxy-ca-cert.cer' in files:
        ca_cert_status = True

    if not fp_status and not ca_cert_status:
        logger.warning('--- 证书不齐全，需要删除重新加载，请等待 ---')
        # 删除文件夹
        shutil.rmtree(file_dir, True)
        os.mkdir(file_dir)

    # cer 文件有   但是没有转换的文件
    elif ca_cert_status and not fp_status:
        "openssl x509 -subject_hash_old -in C:/Users/king/.mitmproxy/mitmproxy-ca-cert.cer"
        cmd = "openssl x509 -subject_hash_old -in {}/mitmproxy-ca-cert.cer".format(file_dir)
        result = adb_shell(cmd)
        certificate_name = str(result).split(r'\n')[0].replace("b'", "") + '.0'
        try:
            shutil.copy("{}/mitmproxy-ca-cert.cer".format(file_dir), "{}/{}".format(file_dir, certificate_name))

            time.sleep(3)
            files = select_files(file_dir)
            if certificate_name in files:
                logger.info('--- cer证书转换成功 ---')
            else:
                logger.info('--- cer证书转换失败 ---')
        except IOError as e:
            logger.warning("Unable to copy file. %s" % e)
        except:
            logger.warning("Unexpected error:", sys.exc_info())
