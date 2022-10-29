import numpy as np
import pymongo
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.use('TkAgg')
mpl.rcParams['font.sans-serif']=['SimHei']
mpl.rcParams['axes.unicode_minus']=False
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
y = list(range(0, 6001, 600))
for i in cursor:
    if kick != i['players'][8]['count']['kick']:
        kick = i['players'][8]['count']['kick']
        x.append(i['time'])

print(x)
print(y)
img = plt.hist(x, bins=y, color='red', histtype='bar', rwidth=1.0)
plt.xlabel('统计9号球员在一场比赛的踢球次数在时间轴上的分布')
plt.ylabel('频次')
plt.show()
