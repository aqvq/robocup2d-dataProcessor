import numpy as np
import pymongo
import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.use('TkAgg')
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False
mongo_client = pymongo.MongoClient('127.0.0.1', 27017)
print("连接成功" if mongo_client.server_info() else "连接失败")  # 判断是否连接成功
mongo_db = mongo_client['robocup']
mongo_collection = mongo_db['202209152350-HfutEngine2021_2-vs-YuShan2022_3']
find_condition = {
    'type': "show"
}

# 查找153周期的一条数据并显示字段type,time,ball信息
cursor = mongo_collection.find(find_condition, projection={'time': True, 'players': True, '_id': False})
kick = 0
x = []
y = []
unum = 11
for i in cursor:
    x.append(i['players'][unum-1]['x'])
    y.append(i['players'][unum-1]['y'])

print(x)
print(y)
img = plt.scatter(x, y, s=1, c='g')
plt.title('{}号球员在一场比赛中的移动轨迹'.format(unum))
plt.axis([-55, 55, -35, 35])
plt.show()
