import pymongo
from loguru import logger
from pymongo.errors import ServerSelectionTimeoutError

"""
数据库类，用于实例化并操作数据库
"""
class Client:
    def __init__(self, host, port, dbname):
        try:
            self.mongo_client = pymongo.MongoClient(host, port)
        except ServerSelectionTimeoutError:
            logger.error("连接数据库超时，请检查网络")
            return
        logger.success("连接成功" if self.mongo_client.server_info() else "连接失败")  # 判断是否连接成功
        self.mongo_db = self.mongo_client[dbname]

    def db(self):
        return self.mongo_db

    def __del__(self):
        self.mongo_db = None
        self.mongo_client = None

    """
    获取所有比赛
    """
    def getAllGames(self):
        return self.db.collection_names()

"""
比赛类，用于实例化某一场比赛并获取相关信息
"""
class Game:
    def __init__(self,db, game):
        self.collection = db[game]

    """
    获取指定周期的球坐标
    """
    def getBallPos(self, cycle, projection={'time': True, 'players': True, '_id': False}):
        find_condition = { 'cycle': cycle }
        self.collection.find(find_condition, projection)

    """
    获取指定周期的球速度
    """
    def getBallVel(self, cycle, projection={'time': True, 'players': True, '_id': False}):
        find_condition = { 'cycle': cycle }
        self.collection.find(find_condition, projection)


if __name__ == "__main__":
    db = Client("172.18.89.26", 27017, "robocup")
    # games = db.getAllGames()
    # print(games)