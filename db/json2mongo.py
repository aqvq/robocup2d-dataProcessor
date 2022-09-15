"""
 Json2MongoDB
 written by shang at 2022年9月15日
 读json文件, 写入Mongo中并把json文件的文件名作为集合名
"""

from loguru import logger
import json
import os
import time
from time import sleep
import yaml
from pymongo import MongoClient
import utils.files
from collections.abc import Iterable


def fixLogFile(filename):
    afterFixLines = []
    fixLines = 0
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file.readlines():
            if not (
                    line.endswith('},\n') or
                    line.endswith('],\n') or
                    line.endswith('}\n') or
                    line.endswith(']\n') or
                    line.endswith('[\n') or
                    line.endswith('ULG6\n')
            ):
                # if line.__contains__("count"):
                #     line = ','.join(line.split(',')[:-2])+'}}]},\n'
                # else:
                #     line = ','.join(line.split(',')[:-2])+'}]},\n'

                fixLines += 1
                # logger.debug("删除错误行: {}".format(line))
                continue
            afterFixLines.append(line)
    with open(filename, 'w', encoding='utf-8') as file:
        file.writelines(afterFixLines)
    return fixLines


def formatTime(duration):
    duration = int(duration)
    m, s = divmod(duration, 60)
    h, m = divmod(m, 60)
    if h == 0 and m == 0:
        return "{}秒".format(s)
    elif h == 0:
        return "{}分钟{}秒".format(m, s)
    else:
        return "{}小时{}分钟{}秒".format(h, m, s)


class Json2MongoDB:
    def __init__(self, configPath='config.yaml.bak'):
        self.configPath = configPath
        self.successCount = 0
        self.failCount = 0
        with open(self.configPath, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        logger.add(self.config['log']['output'],
                   rotation=self.config['log']['rotation'],
                   retention=self.config['log']['retention'],
                   level=self.config['log']['level'].upper())
        if self.config['mongodb']['auth']:
            self.client = MongoClient(self.config['mongodb']['host'],
                                      self.config['mongodb']['port'],
                                      username=self.config['mongodb']['username'],
                                      password=self.config['mongodb']['password'],
                                      authSource=self.config['mongodb']['database'])
        else:
            self.client = MongoClient(self.config['mongodb']['host'],
                                      self.config['mongodb']['port'])

    def importJsonFileToMongo(self, file):
        # logger.debug("正在处理文件: {}".format(file))
        filename = os.path.basename(file)[:-4]
        collection = self.client.get_database(self.config['mongodb']['database']).get_collection(filename)
        if filename == 'incomplete':
            logger.info("跳过: {}".format(file))
            return
        if collection.estimated_document_count() > 0:
            # logger.debug("文件已存在: {}".format(file))
            return
        with open(file, "r", encoding='utf-8') as json_file:
            json_file.readline()  # 过滤首行
            try:
                records = json.load(json_file)
            except json.decoder.JSONDecodeError as e:
                logger.warning("格式错误 ({}): {}".format(e.msg, file))
                if self.config['scan']['skip'].lower() == 'none':
                    raise e
                elif self.config['scan']['skip'].lower() == 'file':
                    logger.info("跳过: {}".format(file))
                    self.failCount += 1
                    return
                elif self.config['scan']['skip'].lower() == 'line':
                    logger.info("尝试修复: {}".format(file))
                    fixLines = fixLogFile(file)
                    if fixLines > 0:
                        # logger.debug("文件修复成功 (删除错误行数: {}): {}".format(fixLines, file))
                        self.importJsonFileToMongo(file)
                    else:
                        self.failCount += 1
                        logger.error("无法修复: {}".format(file))
                    return
                else:
                    raise Exception("无法识别的参数: {}".format(self.config['scan']['skip']))
        collection.insert_many(records)
        self.successCount += 1
        logger.success("导入成功: {}".format(file))

    def importJsonDirToMongo(self, directory):
        if os.path.isfile(directory):
            self.importJsonFileToMongo(directory)
        else:
            files = utils.files.findAllLogfiles(directory)
            for file in files:
                self.importJsonFileToMongo(file)

    def importJsonToMongo(self, obj):
        if isinstance(obj, Iterable) and not isinstance(obj, str):
            for directory in obj:
                self.importJsonDirToMongo(directory)
        else:
            self.importJsonDirToMongo(obj)

    def execute(self):
        # logger.debug("CONFIG: {}".format(self.config))

        while True:
            startTime = time.time()
            self.successCount = 0
            self.failCount = 0
            self.importJsonToMongo(self.config['scan']['source'])
            logger.info(
                "所有任务已完成 (成功: {}, 失败: {}, 用时: {}), 等待新的任务中...".format(
                    self.successCount,
                    self.failCount,
                    formatTime(time.time() - startTime)))
            sleep(self.config['scan']['interval'])
