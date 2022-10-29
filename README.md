> Written by shang at 2022年9月11日

# 概述

- 由于17的Server支持了JSON格式，这里我们只需要简单修改配置即可导出JSON格式的日志文件。
- 再使用MongoDB（一种文档型数据库）导入日志文件，对日志进行分布式、结构化、跨平台的管理，使数据更易存储与查询（可专门使用一台大容量硬盘服务器安装MongoDB作为日志存储设备）。
- 最后可使用Python连接到MongoDB轻松获取数据进行数据挖掘和特征学习等操作。
# 让Rcssserver支持JSON格式
> 要求：rcssserver的版本必须大于等于17

打开server配置文件（通常在`~/.rcssserver/server.conf`）
找到`server::game_log_version`将值修改为6
# 日志内容简介
## RCG文件
> 解析日志时需要用到，建议看看

### Format Version
文件第一行指示rcg日志格式版本，此处为`ULG6`表示为JSON格式日志。
默认使用的是`ULG5`，如果要使用JSON格式的日志文件，需要手动修改。
以下内容讲解基于`ULG6`
### Header
记录服务器版本信息和比赛时间戳
```json
{
    "type": "header",
    "version": "17.0.1",
    "timestamp": "2022-09-11T20:11:15+0800"
},
```
#### type值
根据type所指示的值不同，其兄弟属性亦有区别，遍历与分析数据时应先判断type值。
### Server Param
记录来自服务器配置文件的服务器参数
```json
{
    "type": "server_param",
    "params": {
        "audio_cut_dist": 50,
        "auto_mode": false,
        "back_dash_rate": 0.7,
        "back_passes": true,
        "ball_accel_max": 2.7,
        "ball_decay": 0.94,
      	......
    }
},
```
### Player Param
记录球员参数
```json
{
    "type": "player_param",
    "params": {
        "allow_mult_default_type": false,
        "catchable_area_l_stretch_max": 1.3,
        "catchable_area_l_stretch_min": 1,
        "dash_power_rate_delta_max": 0,
        "dash_power_rate_delta_min": 0,
        "effort_max_delta_factor": -0.004,
      	......
    }
},
```
### Player Type
记录球员类型和其对应的客制化参数，其中的id值会被下述Show部分中的player type引用。
不同类型有不同的特质。具体的英文解释的很明白。
```json
{
    "type": "player_type",
    "id": 7, // type id
    "params": {
        "player_speed_max": 1.05,
        "stamina_inc_max": 49.8058,
        "player_decay": 0.373799,
        "inertia_moment": 4.34496,
        "dash_power_rate": 0.00519903,
        "player_size": 0.3,
        "kickable_margin": 0.681793,
        "kick_rand": 0.0817935,
        "extra_stamina": 70.4846,
        "effort_max": 0.918061,
        "effort_min": 0.518061,
        "kick_power_rate": 0.027,
        "foul_detect_probability": 0.5,
        "catchable_area_l_stretch": 1.0689
    }
},
```
### Team Graphic
用于绘制球队UI
```json
{
    "type": "team_graphic",
    "side": "l",
    "x": 0,
    "y": 0,
    "xpm": [
        "8 8 7 1",
        "a c #97DCF2",
        "f c #A6DEF2",
        "g c #B3D7E9",
        "c c #B7E8F5",
        "m c #C5DBE6",
        "M c #C6EBF6",
        "N c #D3EDF8",
        "ccgMccMN",
        "ccccMgcM",
        "McccMggc",
        "cmMMMcff",
        "MMcMccff",
        "MMMMcgga",
        "MMMMcgfc",
        "MMMMcfcc"
    ]
},
```
### Show
日志文件的主要部分，记录每个周期的球和球员信息
```json

{
    "type": "show",
    "time": 21, // 周期
    "ball": {
        "x": 6.497, // 球的x坐标
        "y": -12.2737, // 球的y坐标
        "vx": 0.6713, // 球的速度x量
        "vy": -2.0568 // 球的速度y量
    },
    "players": [
        {
            "side": "l", // 指示哪边球员
            "unum": 1, // 球员编号
            "type": 0, // 球员类型
            "state": 1, // 球员状态标志位
            "x": -49.4885, // 球员x坐标
            "y": 0.08, // 球员y坐标
            "vx": -0, // 球员速度x量
            "vy": 0, // 球员速度y量
            "body": -90.103, // 身体方向
            "neck": 90, // 脖子方向
            "vq": "h", // 视野质量
            "vw": 180, // 视野宽度
            "stamina": 8000, // 当前体能
            "effort": 1, // 体力效能
            "recovery": 1, // 恢复效率
            "capacity": 130510, // 总体力值
            "fside": "r", // 其所关注球员的位置（可省略）
            "fnum": 4, // 其所关注球员的编号（可省略）
            "count": { // 统计量
                "kick": 0,
                "dash": 2,
                "turn": 69,
                "catch": 0,
                "move": 1,
                "turn_neck": 72,
                "change_view": 1,
                "say": 2,
                "tackle": 0,
                "pointto": 0,
                "attentionto": 20
            }
        },
      ......
    ]
}
```
#### state值
state是一个16进制表示的一个状态flag，每一个位标志一个状态。最常见的：0x9表示守门员，0x1是普通球员。
可以通过这个flag获取球员现在的信息。下面详细内容：
```json
DISABLE : x00000000
STAND : x00000001
KICK : x00000002
KICK_FAULT : x00000004
GOALIE : x00000008
CATCH : x00000010
CATCH_FAULT : x00000020
BALL_TO_PLAYER : x00000040
PLAYER_TO_BALL : x00000080
DISCARD : x00000100
LOST : x00000200 // added for 3D viewer/commentator/small league
BALL_COLLIDE : x00000400 // player collided with the ball
PLAYER_COLLIDE : x00000800 // player collided with another player
TACKLE : x00001000
TACKLE_FAULT : x00002000
BACK_PASS : x00004000
FREE_KICK_FAULT : x00008000
POST_COLLIDE : x00010000 // player collided with goal posts
FOUL_CHARGED : x00020000 // player is frozen by intentional tackle foul
YELLOW_CARD : x00040000
RED_CARD : x00080000
ILLEGAL_DEFENSE : x00100000
```
#### vq值
视野质量（view quality），h表示high，l表示low
#### vw值
视野宽度（view width / visible angle），值用角度表示，但代码用常量表示：narrow | normal | wide，分别对应60/120/180。
#### count值
count是各种统计量，主要统计当前周期为止，球员执行命令统计值。被统计的量依次分别是：kick、dash、turn、catch、move、turn neck、change view、say、tackle、arm、attention to
### Play Mode
记录比赛状态
```json
{
    "type": "playmode",
    "time": 816, // 周期
    "mode": "kick_in_l" // 比赛状态
},
```
具体的mode有：
```json
before_kick_off                  
time_over                        
play_on                          
kick_off_l                       
kick_off_r                       
kick_in_l                        
kick_in_r                        
free_kick_l                      
free_kick_r                      
corner_kick_l                    
corner_kick_r                    
goal_kick_l                      
goal_kick_r                      
goal_l                           
goal_r                           
drop_ball                        
offside_l                        
offside_r                        
penalty_kick_l                   
penalty_kick_r                   
first_half_over                  
pause                            
human_judge                      
foul_charge_l                    
foul_charge_r                    
foul_push_l                      
foul_push_r                      
foul_multiple_attack_l           
foul_multiple_attack_r           
foul_ballout_l                   
foul_ballout_r                   
back_pass_l                      
back_pass_r                      
free_kick_fault_l                
free_kick_fault_r                
catch_fault_l                    
catch_fault_r                    
indirect_free_kick_l             
indirect_free_kick_r             
penalty_setup_l                  
penalty_setup_r                  
penalty_ready_l                  
penalty_ready_r                  
penalty_taken_l                  
penalty_taken_r                  
penalty_miss_l                   
penalty_miss_r                   
penalty_score_l                  
penalty_score_r                  
illegal_defense_l                
illegal_defense_r                 
```
### Team
记录各边球队的名称和得分，如果有点球，后面还会有相应的点球比分。
```json
{
    "type": "team",
    "time": 1953, // 周期
    "teams": [
        {
            "side": "l", // 球队位置
            "name": "AHUTI", // 球队名称
            "score": 2 // 球队得分
        },
        {
            "side": "r", // 球队位置
            "name": "HfutEngine2021", // 球队名称
            "score": 0 // 球队得分
        }
    ]
},

```
### Msg
记录向服务器发送的信息，后面的参数是周期、board type（1是msg board，2是log board，用的很少），引号里的是msg的内容。
```json
{
    "type": "msg",
    "time": 6000,
    "board": 1,
    "message": "(result 202209112011 AHUTI_7-vs-HfutEngine2021_2)"
},
```
## RCL文件
rcl文件记录每个周期server接收到球员发给它的命令及教练发送给球员的命令，为了能让server在下一个周期对这些请求做出相应动作反应。具体内容格式如下：

1. 周期信息（含两部分）：非player_on模式下的周期，player_on模式下的周期
2. 队名及球员号码接收信息（以_隔开）：后跟接收信息具体命令
### 常见命令
下面列举了一些常见的命令格式（方括号表示参数可省略）：

| ( turn %lf ) | moment 力矩 |
| --- | --- |
| ( dash %lf [%lf] ) | power；direction（可省略） |
| ( turn_neck %lf ) | moment |
| ( attentionto off ) | turn attention to off |
| ( attentionto %s %d ) | team name：our、opp、l、r；球员编号 |
| ( kick %lf %lf ) | power；direction |
| ( long_kick %lf %lf ) | power；direction |
| ( tackle %lf [foul] ) | power；four：on/true、off/false（默认为false） |
| ( pointto off) | stop pointing |
| ( pointto %lf %lf ) | dist；head |
| ( catch %lf ) | （Goalie）direction |
| ( move %lf %lf ) | x；y |
| ( change_view width [quality] ) | width：narrow/normal/wide；quality：low/high（默认为high） |
| ( compression %d ) | level |

### 具体示例
下面给出一个具体的rcl文件样例
![image.png](https://cdn.nlark.com/yuque/0/2022/png/12709936/1662900532227-03ca9305-5f6a-43e8-986c-4c544e2dd7a1.png#clientId=ub91aaf3e-974e-4&crop=0&crop=0&crop=1&crop=1&errorMessage=unknown%20error&from=paste&id=u6626da1e&margin=%5Bobject%20Object%5D&name=image.png&originHeight=1024&originWidth=1280&originalType=url&ratio=1&rotation=0&showTitle=false&size=413467&status=error&style=none&taskId=u50e9b0e9-6401-488b-840e-9eb5f16d67d&title=)
# 使用MongoDB存储日志
## 为什么使用MongoDB
MongoDB是一个开源、高性能、无模式的文档型数据库，当初的设计就是用于简化开发和方便扩展，是NoSQL数据库产品中的一种。是最像关系型数据库（MySQL）的非关系型数据库。
它支持的数据结构非常松散，是一种类似于 JSON 的 格式叫BSON，所以它既可以存储比较复杂的数据类型，又相当的灵活。
MongoDB中的记录是一个文档，它是一个由字段和值对（field:value）组成的数据结构。MongoDB文档类似于JSON对象，即一个文档认为就是一个对象。字段的数据类型是字符型，它的值除了使用基本的一些类型外，还可以包括其他文档、普通数组和文档数组。
其特性十分适合存储rcg日志文件，既能适应日志文件的大容量存储与管理（一个日志文件约50MB，一千场比赛就约50GB了），还适合各种灵活的查询方式，便于后续使用Python直接分析而不占用本地磁盘（如果将MongoDB作为远程服务器），此外还可对数据库文档进行横向分析和横向扩展，便于以后写入分析后的特征或结果等，十分灵活。
此外，MongoDB优秀的数据结构设计极大地降低了（约75%）原来的磁盘占用：
![image.png](https://cdn.nlark.com/yuque/0/2022/png/12709936/1663135742151-aa13b6ad-d717-4c01-bdd7-d83f8acffa6c.png#clientId=u00e30ff9-16ce-4&crop=0&crop=0&crop=1&crop=1&errorMessage=unknown%20error&from=paste&height=833&id=u4e01c47a&margin=%5Bobject%20Object%5D&name=image.png&originHeight=833&originWidth=1418&originalType=binary&ratio=1&rotation=0&showTitle=false&size=78041&status=error&style=none&taskId=u8f3b3b31-fe14-47ae-bb4d-5effd042bfc&title=&width=1418)
## 安装
从官网下载最新版本：
> 支持跨平台，可安装Windows版本也可安装Ubuntu版本

安装Windows版本时记得选择完全安装，这样会自动安装一个Compass的可视化数据库管理工具，可以可视化地操作MongoDB数据库。
## 导入日志
> 可使用Compass导入也可使用CLI导入

导入前只需要删除日志文件的第一行即可成功导入到MongoDB中。
效果图：
![image.png](https://cdn.nlark.com/yuque/0/2022/png/12709936/1662907212052-de1c7861-0f92-4615-a41c-51390ac2b6d7.png#clientId=ub7000a02-5216-4&crop=0&crop=0&crop=1&crop=1&errorMessage=unknown%20error&from=paste&height=1393&id=ud8e6994d&margin=%5Bobject%20Object%5D&name=image.png&originHeight=1393&originWidth=2560&originalType=binary&ratio=1&rotation=0&showTitle=false&size=107083&status=error&style=none&taskId=u8413701e-e0bb-480b-8af9-ce7ff9081b9&title=&width=2560)

# 程序原理
## 使用Python操作日志数据
首先安装pymongo包：
```bash
pip3 install pymongo
# 或者
pip install pymongo
```
一个简单的示例代码：
```python
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

```
# 使用Python提取日志数据

- 加载配置文件，连接数据库；
- 扫描指定路径，将rcg文件转为符合规范的JSON格式文件（删除首行ULG6；删除信息残缺行，通常是最后一个周期）；
- 调用json库解析日志文件；
- 最后将整个文件的数据全部导入到数据库中：`collection.insert_many(records)`。

核心代码：
```python
def importJsonFileToMongo(self, file):
    # logger.debug("正在处理文件: {}".format(file))
    filename = os.path.basename(file)[:-4]
    collection = self.client.get_database(self.config['mongodb']['database']).get_collection(filename)
    if filename in self.ignoreList:
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
                    if self.config['scan']['error'].lower() == 'ignore':
                        self.ignoreList.append(filename)
                    logger.error("无法修复: {}".format(file))
                return
            else:
                raise Exception("无法识别的参数: {}".format(self.config['scan']['skip']))
    collection.insert_many(records)
    self.successCount += 1
    logger.success("导入成功: {}".format(file))

```
配置模板：
```yaml
# DCC config file
# written by shang at 2022年9月15日
#
# MongoDB配置信息
mongodb:
  # 主机ip地址
  host: localhost
  # 主机端口号
  port: 27017
  # 数据库名称
  database: Robocup
  # 是否需要验证
  # 如果需要验证，请输入用户名和密码
  auth: false
  # 用户名
  username:
  # 密码
  password:
#
# 主要配置信息
scan:
  # 扫描监听文件（夹）
  # 可指定多个文件或文件夹
  source:
    -
  # 处理出错的日志文件
  # 选项：
  # file：跳过出错的文件，不导入该文件
  # line：删除出错的行，继续尝试导入该文件
  # none：直接抛出异常
  skip: line
  # 完成一边扫描后的停止间隔时间，以秒为单位
  interval: 600
  # 对于无法修复的文件如何处理（选项不区分大小写）
  # repeat：重复扫描
  # ignore：忽略，但重启程序后会全部扫描一遍
  error: ignore
#
# 输出日志文件配置信息
log:
  # 输出日志等级
  # 选项（不区分大小写）：
  # DEBUG/INFO/WARNING/ERROR/CRITICAL
  level: INFO
  # 输出日志文件名
  output: log.txt
  # 转储规则（留空为禁用）
  rotation: 
  # 延迟删除规则（留空为禁用）
  retention: 1 week

```
