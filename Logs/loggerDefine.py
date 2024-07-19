#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @author: Kevin
# @contact: huguangjing211@gmail.com
# @file: loggerDefine.py
# @time: 2020/4/7 11:38
# @desc: 日志的定义  按照info 和error日志区分开

import logging
import sys, os

import requests
from Logs.multiprocessloghandler import MultiprocessHandler

requests.packages.urllib3.disable_warnings()


def loggerDefine(dir, folder, loggerName):
    loggerName = 'log'
    # error日志路径
    errorDir = os.path.join(dir, "error/{}/".format(folder))
    if not os.path.exists(errorDir):
        os.makedirs(errorDir)

    # error日志文件
    errorFile = errorDir + "{0}".format(loggerName)

    log = logging.getLogger(folder+loggerName)
    log.handlers.clear()
    # 定义日志输出格式
    formattler = '%(asctime)s|%(processName)s|%(threadName)s|%(levelname)s|%(filename)s:%(lineno)d|%(funcName)s|%(message)s'
    fmt = logging.Formatter(formattler)

    # 设置日志控制台输出
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)

    # 设置控制台文件输出
    log_handler_err = MultiprocessHandler(errorFile)

    # 设置日志输出格式：
    stream_handler.setFormatter(fmt)
    log_handler_err.setFormatter(fmt)

    # 设置过滤条件
    info_filter = logging.Filter()
    info_filter.filter = lambda record: record.levelno < logging.WARNING  # 设置过滤等级
    err_filter = logging.Filter()
    err_filter.filter = lambda record: record.levelno >= logging.WARNING
    # 对文件输出日志添加过滤条件
    log_handler_err.addFilter(err_filter)

    # 对logger增加handler日志处理器
    log.addHandler(log_handler_err)
    log.addHandler(stream_handler)

    log.setLevel("INFO")
    return log
