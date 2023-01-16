数据库用的sqlite，代码上免除了配置数据库的过程 ~~但是要装python~~
基本上装个httpapi，输个4行代码就能跑


[项目地址](https://github.com/liu-zhou-L/swordbot)

# swordbot
一个基于`Mirai`和`Graia`实现的宝剑游戏机器人（复刻[https://github.com/Micalhl/NiuZi](https://github.com/Micalhl/NiuZi)）

**python_version >= '3.8' and python_version < '4.0'**

作者使用的是**python3.11.1**

## 使用方法

### 部署

首先确保`Mirai`已安装`mirai-api-http`插件并配置正确

将项目克隆到本地

```
git clone git@github.com:liu-zhou-L/swordbot.git
```

安装`pipenv`，如果已安装忽略此步

```
pip3 install pipenv
```

使用`pipenv`创建虚拟环境并安装依赖

```
pipenv install -r requirements.txt
```

### 配置

机器人的配置文件如下

```
QQ: 12345 # 你的机器人的 qq 号
VerifyKey: "12345" # 填入 VerifyKey
Host: "http://localhost:7789" # adapterSetting下的host
GroupBlackList: [] # 群聊黑名单
UserBlackList: [] # 用户黑名单
```

其中前三项启动后更改需重启机器人（不需要重启`Mirai`）
`VerifyKey`和`Host`需填入`Mirai`路径下`config/net.mamoe.mirai-api-http/setting.yml`文件中对应的值

### 运行

前两步完成后，先运行`Mirai`然后在`swordbot`路径下使用

```
pipenv run python bot.py
```

启动机器人

### 使用

目前支持的指令

```
宝剑系统：查看可用指令
我的宝剑：查看自己的宝剑信息
白嫖宝剑：获得一把宝剑
比划比划@群内用户：和群内用户进行对决，赚取宝剑长度
随机比划: 与另一位随机宝剑对决，无需@
（群）宝剑榜：查看群内用户的宝剑排名
总宝剑榜：查看宝剑系统所有宝剑的排名
绑定对象+@群内用户：将自己的宝剑对象意向设定为某群内用户，互为彼此意向时，形成对象联系
双修功法：与对象一起修炼，赚取宝剑长度
冲咖啡：冲杯咖啡赚取宝剑长度
宝剑改名+新名称：接受长度在2~30的宝剑名称，会自动去除所有空格，改名成功会消耗 25cm 长度
```


对`python`、`Mirai`、`Graia`的使用均为小白级，代码一塌糊涂，qwq
