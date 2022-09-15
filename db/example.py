import pymongo

mongo_client = pymongo.MongoClient('127.0.0.1', 27017)
print("连接成功" if mongo_client.server_info() else "连接失败")  # 判断是否连接成功
mongo_db = mongo_client['Robocup']
mongo_collection = mongo_db['test']
find_condition = {
    'time': 153
}
# 查找153周期的一条数据并显示字段type,time,ball信息
select_item = mongo_collection.find_one(find_condition, projection={'type': True, 'time': True, 'ball': True})
print(select_item)  # 打印数据信息

for collection in mongo_db.list_collection_names():
    print(collection)
