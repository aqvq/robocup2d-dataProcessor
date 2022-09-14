"""
读 json 文件，写入 Mongo 中
并把json文件的文件名作为集合名
"""
import json
import os
from pymongo import MongoClient
import utils.files
from collections.abc import Iterable


def importJsonFileToMongo(host, port, database, file):
    print("Processing file: " + file)
    client = MongoClient(host, port)
    filename = os.path.basename(file)[:-4]
    collection = client.get_database(database).get_collection(filename)
    if collection.count_documents({}) > 0:
        print("The file already exists!")
        return
    with open(file, "r") as json_file:
        json_file.readline()  # 过滤首行
        try:
            records = json.load(json_file)
        except json.decoder.JSONDecodeError as e:
            print(e)
            print("The file has been broken, fixing...")
            if fixLogFile(file):
                print("File fixed successfully, re-importing...")
                importJsonFileToMongo(host, port, database, file)
            else:
                print("This file cannot be fixed, skipping...")
            return
    collection.insert_many(records)
    print("The file has been successfully imported into the MongoDB!")


def importJsonDirToMongo(host, port, database, directory):
    if os.path.isfile(directory):
        importJsonFileToMongo(host, port, database, directory)
    else:
        files = utils.files.findAllLogfiles(directory)
        for file in files:
            importJsonFileToMongo(host, port, database, file)


def importJsonToMongo(host, port, database, obj):
    if isinstance(obj, Iterable) and not isinstance(obj, str):
        for directory in obj:
            importJsonDirToMongo(host, port, database, directory)
    else:
        importJsonDirToMongo(host, port, database, obj)


def fixLogFile(filename):
    retFlag = False
    afterFixLines = []
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file.readlines():
            if line.endswith(',,\n'):
                line = line.replace(',,\n', '}]},\n')
                retFlag = True
            afterFixLines.append(line)
    with open(filename, 'w', encoding='utf-8') as file:
        file.writelines(afterFixLines)
    return retFlag


if __name__ == '__main__':
    importJsonToMongo('localhost', 27017, 'Robocup', '../log')
    print("All the work has been completed")