import yaml
import os

import sqlite3
import math
from graia.scheduler import timers
from graia.scheduler.saya import SchedulerSchema
import threading

import random
import time
from datetime import datetime

from operator import itemgetter, attrgetter

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group, Member
from graia.ariadne.message.element import At, Plain, Image, Forward, ForwardNode

from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

from graia.ariadne.message.parser.base import DetectPrefix, MatchContent, DetectSuffix

import re

sex = ['男', '女']
# suggestmes = "\n[*]推荐添加机器人为好友获取跨群比划提醒"
suggestmes = ""

channel = Channel.current()

def checkblacklist(GroupId = None, UserId = None):

    file = open("bot.yml", 'r', encoding="utf-8")
    yamlfile = file.read()
    file.close()
    data =  yaml.full_load(yamlfile)
    if GroupId != None and GroupId in data['GroupBlackList']:
        return True
    if UserId != None and UserId in data['UserBlackList']:
        return True
    return False

def createdb():
    conn = sqlite3.connect('NiuZi.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE niuzi
                (owner NUMBER,
                name TEXT,
                sex NUMBER,
                length TEXT,
                stopuntil TEXT,
                npy NUMBER,
                coffee_tot NUMBER,
                cfuntil TEXT,
                ttuntil TEXT);''')
                # 0男 1女
    conn.commit()
    conn.close()

def initniuzi(member):
    conn = sqlite3.connect('NiuZi.db')
    cur = conn.cursor()
    tdata = [(member.id, member.name + 'の宝剑', 0, str(random.uniform(8, 13)), str(0), -1, 0, str(0), str(0))]
    cur.executemany('''INSERT INTO niuzi VALUES (?,?,?,?,?,?,?,?,?)''', tdata)
    conn.commit()
    conn.close()

def __getniuzi(id):
    conn = sqlite3.connect('NiuZi.db')
    cur = conn.cursor()
    text_re = '''SELECT * FROM niuzi WHERE owner=''' + str(id)
    cur.execute(text_re)
    ret = cur.fetchone()
    conn.close()
    return ret

def __setniuzi(cc=None, id=None, length=None, tsex=None, coffee_tot=None, cfuntil=None, tuntil=None, name=None, npy=None, ttuntil=None):
    if cc != None:
        if id == None:
            id=cc[0]
        if name == None:
            name=cc[1]
        if tsex == None:
            tsex=cc[2]
        if length == None:
            length=cc[3]
        if tuntil == None:
            tuntil = cc[4]
        if npy == None:
            npy = cc[5]
        if coffee_tot == None:
            coffee_tot=cc[6]
        if cfuntil == None:
            cfuntil = cc[7]
        if ttuntil == None:
            ttuntil = cc[8]
    conn = sqlite3.connect('NiuZi.db')
    cur = conn.cursor()
    text_re = '''UPDATE niuzi SET length="%s", sex=%d, coffee_tot=%d, cfuntil="%s", stopuntil="%s", name="%s", npy=%d , ttuntil="%s" WHERE owner=%d;'''%(str(length), tsex, coffee_tot, str(cfuntil), str(tuntil), name, npy, str(ttuntil), id)
    cur.execute(text_re)
    ret = cur.fetchone()
    conn.commit()
    conn.close()
    return ret

def getniuzi(id):
    try:
        c = __getniuzi(id)
    except:
        createdb()
        return None
    return c

def getsomeniuzi(num = -1):
    try:
        conn = sqlite3.connect('NiuZi.db')
        cur = conn.cursor()
        text_re = '''SELECT * FROM niuzi'''
        cur.execute(text_re)
        if num == -1:
            ret = cur.fetchall()
        elif num >= 0:
            ret = cur.fetchmany(num)
        def nzcmp(elem):
            return float(elem[3])
        ret.sort(key=nzcmp, reverse=True)
        conn.close()
    except:
        createdb()
        return None 
    return ret

@channel.use(SchedulerSchema(timers.crontabify("0 0 * * *")))
async def setqiandao():
    print("手冲咖啡重置\n")
    conn = sqlite3.connect('NiuZi.db')
    cur = conn.cursor()
    cur.execute('''UPDATE niuzi SET coffee_tot=0''')
    conn.commit()
    conn.close()


@channel.use(ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[MatchContent("宝剑系统")],
    ))
async def help(app: Ariadne, group: Group, member: Member):
    if checkblacklist(group.id, member.id):
        return
    if (await app.get_friend(member.id)) == None:
        flag = False
    else:
        flag = True

    await app.send_message(
        group,
        MessageChain(At(member.id), '''\n我的宝剑：查看自己的宝剑信息\n白嫖宝剑：获得一把宝剑\n比划比划@群内用户：和群内用户进行对决，赚取宝剑长度\n随机比划: 与另一位随机宝剑对决，无需@\n（群）宝剑榜：查看群内用户的宝剑排名\n总宝剑榜：查看宝剑系统所有宝剑的排名\n绑定对象+@群内用户：将自己的宝剑对象意向设定为某群内用户，互为彼此意向时，形成对象联系\n双修功法：与对象一起修炼，赚取宝剑长度\n冲咖啡：冲杯咖啡赚取宝剑长度\n宝剑改名+新名称：接受长度在2~30的宝剑名称，会自动去除所有空格，改名成功会消耗 25cm 长度''' + ("" if flag else suggestmes)),
    )

def bjinfo(cc):
    ret = getsomeniuzi()
    num = 0
    while num <= (len(ret) - 1):
        if ret[num][0] == cc[0]:
            break
        num += 1
    # return '\n名称: %s\n性别: %s\n长度: %s\n对象: %s\n排名: %d'%(cc[1], sex[cc[2]], cc[3], '还没有' if (isduixiang(cc[0], cc[5])==False) else (getniuzi(cc[5])[1]), num + 1)
    return '\n主人: %d\n名称: %s\n长度: %s\n对象: %s\n排名: %d'%(cc[0], cc[1], cc[3], '还没有' if (isduixiang(cc[0], cc[5])==False) else (getniuzi(cc[5])[1]), num + 1)


@channel.use(ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[MatchContent("我的宝剑")],
    ))
async def mine(app: Ariadne, group: Group, member: Member):
    if checkblacklist(group.id, member.id):
        return
    if (await app.get_friend(member.id)) == None:
        flag = False
    else:
        flag = True

    c = getniuzi(member.id)
    pam = ''
    if c == None:
        await app.send_message(
            group,
            MessageChain(At(member.id), '\n你还没有宝剑，尝试 白嫖宝剑' + ("" if flag else suggestmes)),
        )
        return
    
    await app.send_message(
        group,
        MessageChain(At(member.id), bjinfo(c)),
    )

@channel.use(ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[MatchContent("白嫖宝剑")],
    ))
async def shou(app: Ariadne, group: Group, member: Member):
    if checkblacklist(group.id, member.id):
        return
    if (await app.get_friend(member.id)) == None:
        flag = False
    else:
        flag = True

    c = getniuzi(member.id)
    pam = ''
    if c == None:
        initniuzi(member)
        pam += '\n⚔️白嫖成功⚔️\n尝试输入“宝剑系统”查看指令菜单'
        c = getniuzi(member.id)
        await app.send_message(
            group,
            MessageChain(At(member.id), pam + bjinfo(c) + ("" if flag else suggestmes)),
        )
    else:
        await app.send_message(
            group,
            MessageChain(At(member.id), '\n你已经有宝剑了，输入 我的宝剑 查看宝剑信息' + ("" if flag else suggestmes)),
        )
        return

@channel.use(ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[MatchContent("随机比划")],
    ))
async def randpk(app: Ariadne, group: Group, member: Member, message: MessageChain = MatchContent("随机比划")):
    if checkblacklist(group.id, member.id):
        return
    if (await app.get_friend(member.id)) == None:
        flag = False
    else:
        flag = True

    try:
        ret = getsomeniuzi()
        if len(ret)==0 or ret == None:
            await app.send_message(
                group,
                MessageChain(At(member.id), '\n数据库出错了' + ("" if flag else suggestmes)),
            )
            return
        memc = getniuzi(member.id)
        if memc == None:
            await app.send_message(
                group,
                MessageChain(At(member.id), '\n你还没有宝剑，尝试 白嫖宝剑' + ("" if flag else suggestmes)),
            )
            return
        for i in range(0, len(ret) - 1):
            if ret[i][0] == member.id:
                del ret[i]
                break
        tarc = random.choice(ret)
        if float(memc[4]) - time.time() > 0:
            await app.send_message(
                group,
                MessageChain(At(member.id), '\n你的宝剑磨损了，还需要等 %ds 才能修复😓'%(math.ceil(float(memc[4]) - time.time())) + ("" if flag else suggestmes)),
            )
            return
        if float(tarc[4]) - time.time() > 0:
            await app.send_message(
                group,
                MessageChain(At(member.id), '\n宝剑 %s 磨损了😓'%(tarc[1]) + ("" if flag else suggestmes)),
            )   
            return
        qk = random.randint(0, 3)
        dd = random.uniform(3, 40)
        waittime = random.randint(20, 300)
        MOD = 2/3
        if qk == 0:
            __setniuzi(memc, length=float(memc[3]) - dd * MOD, tuntil=time.time() + waittime)
            __setniuzi(tarc, length=float(tarc[3]) - dd * MOD, tuntil=time.time() + waittime)
            await app.send_message(
                group,
                MessageChain(At(member.id), '\n⚔️你的宝剑和 %s(%d) 进行了比划\n缠住了，你俩都断了 %s cm😓\n但双方都磨损了，需要等 %ds 才能修复'%(tarc[1], tarc[0], str(dd * MOD), waittime) + ("" if flag else suggestmes)),
            )
            memm = await app.get_friend(tarc[0])
            if memm != None:
                await app.send_message(
                    memm,
                    MessageChain('[宝剑比划提醒]\n⚔️你的宝剑和 %s(%d) 进行了比划\n缠住了，你俩都断了 %s cm😓\n但双方都磨损了，需要等 %ds 才能修复'%(memc[1], memc[0], str(dd * MOD), waittime)),
                )
            return
        elif qk in [1, 2]:
            __setniuzi(memc, length=float(memc[3]) + dd, tuntil=time.time() + waittime)
            __setniuzi(tarc, length=float(tarc[3]) - dd * MOD, tuntil=time.time() + waittime)
            await app.send_message(
                group,
                MessageChain(At(member.id), '\n🤺你的宝剑和 %s(%d) 进行了比划\n你赢了 %s cm😄\n对方折了 %s cm\n但双方都磨损了，需要等 %ds 才能修复'%(tarc[1], tarc[0], str(dd), str(dd * MOD), waittime) + ("" if flag else suggestmes)),
            )
            memm = await app.get_friend(tarc[0])
            if memm != None:
                await app.send_message(
                    memm,
                    MessageChain('[宝剑比划提醒]\n🤺你的宝剑和 %s(%d) 进行了比划\n你输了 %s cm😓\n对方赢了 %s cm\n但双方都磨损了，需要等 %ds 才能修复'%(memc[1], memc[0], str(dd * MOD), str(dd), waittime)),
                )
            return
        else:
            __setniuzi(memc, length=float(memc[3]) - dd * MOD, tuntil=time.time() + waittime)
            __setniuzi(tarc, length=float(tarc[3]) + dd)
            await app.send_message(
                group,
                MessageChain(At(member.id), '\n🤺你的宝剑和 %s(%d) 进行了比划\n你输了 %s cm😓\n对方赢了 %s cm\n你磨损了，需要等 %ds 才能修复'%(tarc[1], tarc[0], str(dd * MOD), str(dd), waittime) + ("" if flag else suggestmes)),
            )
            memm = await app.get_friend(tarc[0])
            if memm != None:
                await app.send_message(
                    memm,
                    MessageChain(At(member.id), '[宝剑比划提醒]\n🤺你的宝剑和 %s(%d) 进行了比划\n你赢了 %s cm😄\n对方折了 %s cm'%(memc[1], memc[0], str(dd), str(dd * MOD))),
                )
            return
    except:
        await app.send_message(
            group,
            MessageChain(At(member.id), '\n发生了未知错误'),
        )
        return
    pass

@channel.use(ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[DetectPrefix("比划比划")],
    ))
async def pk(app: Ariadne, group: Group, member: Member, message: MessageChain = DetectPrefix("比划比划")):
    if checkblacklist(group.id, member.id):
        return
    if (await app.get_friend(member.id)) == None:
        flag = False
    else:
        flag = True

    newmes = message.include(At)
    if At(app.account) in newmes:
        await app.send_message(
            group,
            MessageChain(At(member.id), '\n你和机器人比划个啥啊😓' + ("" if flag else suggestmes)),
        )
        return
    if len(newmes) > 1:
        await app.send_message(
            group,
            MessageChain(At(member.id), '\n你到底想和谁比划啊😓' + ("" if flag else suggestmes)),
        )
        return
    elif len(newmes) < 1:
        await app.send_message(
            group,
            MessageChain(At(member.id), '\n你想和谁比划😓\n在“比划比划”后面@ta' + ("" if flag else suggestmes)),
        )
        return
    memc = getniuzi(member.id)
    if memc == None:
        await app.send_message(
            group,
            MessageChain(At(member.id), '\n你还没有宝剑，尝试 白嫖宝剑' + ("" if flag else suggestmes)),
        )
        return
    if float(memc[4]) - time.time() > 0:
        await app.send_message(
            group,
            MessageChain(At(member.id), '\n你的宝剑磨损了，还需要等 %ds 才能修复😓'%(math.ceil(float(memc[4]) - time.time())) + ("" if flag else suggestmes)),
        )
        return
    member_list = await app.get_member_list(group)
    for tar in member_list:
        if At(tar) in message:
            if tar.id == member.id:
                await app.send_message(
                    group,
                    MessageChain(At(member.id), '\n你和自己比划什么啊😓' + ("" if flag else suggestmes)),
                )
                return
            tarc = getniuzi(tar.id)
            if tarc == None:
                await app.send_message(
                    group,
                    MessageChain(At(member.id), '\n对方还没有宝剑😓' + ("" if flag else suggestmes)),
                )
                return
            elif float(tarc[4]) - time.time() > 0:
                await app.send_message(
                    group,
                    MessageChain(At(member.id), '\n对方的宝剑磨损了😓' + ("" if flag else suggestmes)),
                )
                return
            else:
                qk = random.randint(0, 3)
                dd = random.uniform(3, 40)
                waittime = random.randint(20, 300)
                MOD = 2/3
                if qk == 0:
                    __setniuzi(memc, length=float(memc[3]) - dd * MOD, tuntil=time.time() + waittime)
                    __setniuzi(tarc, length=float(tarc[3]) - dd * MOD, tuntil=time.time() + waittime)
                    await app.send_message(
                        group,
                        MessageChain(At(member.id), '\n⚔️缠住了，你俩都断了 %s cm😓\n都磨损了，需要等 %ds 才能修复'%(str(dd * MOD), waittime) + ("" if flag else suggestmes)),
                    )
                    return
                elif qk in [1, 2]:
                    __setniuzi(memc, length=float(memc[3]) + dd, tuntil=time.time() + waittime)
                    __setniuzi(tarc, length=float(tarc[3]) - dd * MOD, tuntil=time.time() + waittime)
                    await app.send_message(
                        group,
                        MessageChain(At(member.id), '\n🤺你赢了 %s cm😄\n对方折了 %s cm\n但双方都磨损了，需要等 %ds 才能修复'%(str(dd), str(dd * MOD), waittime) + ("" if flag else suggestmes)),
                    )
                    return
                else:
                    __setniuzi(memc, length=float(memc[3]) - dd * MOD, tuntil=time.time() + waittime)
                    __setniuzi(tarc, length=float(tarc[3]) + dd)
                    await app.send_message(
                        group,
                        MessageChain(At(member.id), '\n🤺你输了 %s cm😓\n对方赢了 %s cm\n你磨损了，需要等 %ds 才能修复'%(str(dd * MOD), str(dd), waittime) + ("" if flag else suggestmes)),
                    )
                    return
    await app.send_message(
        group,
        MessageChain(At(member.id), '\n群里没找到你要比划的人，你怎么@到他的😓' + ("" if flag else suggestmes)),
    )
    return
    
@channel.use(ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[DetectSuffix('宝剑榜')],
    ))
async def phb(app: Ariadne, group: Group, member: Member, message: MessageChain = DetectSuffix('宝剑榜')):
    if checkblacklist(group.id, member.id):
        return
    if (await app.get_friend(member.id)) == None:
        flag = False
    else:
        flag = True
    conn = sqlite3.connect('NiuZi.db')
    cur = conn.cursor()
    if message.display == '总':
        ret = getsomeniuzi()
        fwd_nodeList = [
            ForwardNode(
                target=member,
                time=datetime.now(),
                message=MessageChain('⚔️总宝剑榜（仅显示前100）⚔️' + ("" if flag else suggestmes)),
            )
        ]
    elif message.display in ['群', '']:
        ret = []
        member_list = await app.get_member_list(group)
        for i in member_list:
            text_re = '''SELECT * FROM niuzi WHERE owner=%d'''%(i.id)
            cur.execute(text_re)
            c = cur.fetchone()
            if c != None:
                ret.append(c)
        conn.close()
        fwd_nodeList = [
            ForwardNode(
                target=member,
                time=datetime.now(),
                message=MessageChain('⚔️群宝剑榜（仅显示前100）⚔️' + ("" if flag else suggestmes)),
            )
        ]
    else:
        return
    if len(ret) == 0:
        await app.send_message(
            group,
            MessageChain(At(member.id), '\n没找到指定范围的宝剑😓' + ("" if flag else suggestmes)),
        )
        return
    i = 1
    def nzcmp(elem):
        return float(elem[3])
    ret.sort(key=nzcmp, reverse=True)
    for nz in ret:
        if i > 100:
            break
        fwd_nodeList.append(
            ForwardNode(
                target=member,
                time=datetime.now(),
                message=MessageChain("⚔️No.%d%s"%(i, bjinfo(nz))),
            )
        )
        i += 1
    await app.send_message(
        group,
        MessageChain(Forward(nodeList=fwd_nodeList)),
    )


@channel.use(ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[MatchContent("冲咖啡")],
    ))
async def qiandao(app: Ariadne, group: Group, member: Member, message: MessageChain = MatchContent("冲咖啡")):
    if checkblacklist(group.id, member.id):
        return
    if (await app.get_friend(member.id)) == None:
        flag = False
    else:
        flag = True
    
    c = getniuzi(member.id)
    if c == None:
        await app.send_message(
            group,
            MessageChain(At(member.id), '\n你好像还没有宝剑😓，尝试 白嫖宝剑' + ("" if flag else suggestmes)),
        )
        return
    if float(c[7]) - time.time() > 0:
        await app.send_message(
            group,
            MessageChain(At(member.id), '\n你这冲的也太频繁了😓\n等 %ds 后再来罢'%(math.ceil(float(c[7]) - time.time())) + ("" if flag else suggestmes)),
        )
        return
    ts = random.uniform(2, 50) * pow(0.75, c[6])
    waittime = random.randint(600, 3600)
    conn = sqlite3.connect('NiuZi.db')
    cur = conn.cursor()
    cur.execute('''UPDATE niuzi SET length=''' + str(float(c[3]) + ts) + ''', coffee_tot=''' + str(c[6] + 1) + ''', cfuntil=''' + str(time.time() + waittime) + ''' WHERE owner=''' + str(member.id))
    conn.commit()
    conn.close()
    c = getniuzi(member.id)
    pam = '\n☕冲完了😄\n这是你今天第 %d 次冲☕'%c[6]
    if c[6] > 2:
        pam += '\n咖啡喝多了也不好哦😓'
    if c[6] == 4:
        pam += '\n后面再冲不会长长了'
    if c[6] > 4:
        await app.send_message(
            group,
            MessageChain(At(member.id), pam + '\n☕冲多了，这次没有增长长度😓\n后面也不会了，放弃吧' + ("" if flag else suggestmes)),
        )
    else:
        await app.send_message(
            group,
            MessageChain(At(member.id), pam + '\n喝完☕精力++，宝剑长度增长了 %scm\n当前长度: %s\n但需要等 %ds 才能再冲☕'%(str(ts), c[3], waittime) + ("" if flag else suggestmes)),
        )
    pass

def isduixiang(id_1, id_2):
    u_1 = getniuzi(id_1)
    u_2 = getniuzi(id_2)
    if u_1 != None and u_2 != None:
        if u_1[5] == id_2 and u_2[5] == id_1:
            return True
    return False

@channel.use(ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[DetectPrefix("绑定对象")],
    ))
async def setniuziname(app: Ariadne, group: Group, member: Member, message: MessageChain = DetectPrefix("绑定对象")):
    if checkblacklist(group.id, member.id):
        return
    if (await app.get_friend(member.id)) == None:
        flag = False
    else:
        flag = True
    newmes = message.include(At)
    if len(newmes) > 1:
        await app.send_message(
            group,
            MessageChain(At(member.id), '\n你到底想和谁绑定啊😓' + ("" if flag else suggestmes)),
        )
        return
    elif len(newmes) < 1:
        await app.send_message(
            group,
            MessageChain(At(member.id), '\n你到底想和谁绑定啊😓\n在 绑定对象 后面@ta' + ("" if flag else suggestmes)),
        )
        return
    if At(app.account) in newmes:
        await app.send_message(
            group,
            MessageChain(At(member.id), '\n你和机器人绑定个啥啊😓' + ("" if flag else suggestmes)),
        )
        return
    memc = getniuzi(member.id)
    if memc == None:
        await app.send_message(
            group,
            MessageChain(At(member.id), '\n你还没有宝剑，尝试 白嫖宝剑' + ("" if flag else suggestmes)),
        )
        return
    member_list = await app.get_member_list(group)
    for tar in member_list:
        if At(tar) in newmes:
            if tar.id == member.id:
                await app.send_message(
                    group,
                    MessageChain(At(member.id), '\n你和自己绑定什么啊😓' + ("" if flag else suggestmes)),
                )
                return
            tarc = getniuzi(tar.id)
            if tarc == None:
                await app.send_message(
                    group,
                    MessageChain(At(member.id), '\n对方还没有宝剑😓' + ("" if flag else suggestmes)),
                )
                return
            else:
                __setniuzi(memc, npy=tarc[0])
                if isduixiang(memc[0], tarc[0]):
                    await app.send_message(
                        group,
                        MessageChain(At(memc[0]), '\n', At(tarc[0]), '\n🎉绑定对象成功，对象联系已建立' + ("" if flag else suggestmes)),
                    )
                else:
                    await app.send_message(
                        group,
                        MessageChain(At(member.id), '\n🎉绑定成功，等待对方也绑定后即可建立联系' + ("" if flag else suggestmes)),
                    )
                return
    await app.send_message(
        group,
        MessageChain(At(member.id), '\n群里没找到你要比划的人，你怎么@到他的😓' + ("" if flag else suggestmes)),
    )
    return

@channel.use(ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[DetectPrefix("宝剑改名")],
    ))
async def setniuziname(app: Ariadne, group: Group, member: Member, message: MessageChain = DetectPrefix("宝剑改名")):
    if checkblacklist(group.id, member.id):
        return
    if (await app.get_friend(member.id)) == None:
        flag = False
    else:
        flag = True

    c = getniuzi(member.id)
    if c == None:
        await app.send_message(
            group,
            MessageChain(At(member.id), '\n你好像还没有宝剑😓，尝试 白嫖宝剑' + ("" if flag else suggestmes)),
        )
    else:
        newname = message.display.replace(" ", "")
        if len(newname) <= 1 or len(newname) >= 31:
            await app.send_message(
                group,
                MessageChain(At(member.id), '\n只接受长度在2~30的宝剑名称，会自动去除所有空格\n改名成功会消耗 25cm 长度' + ("" if flag else suggestmes)),
            )
        else:
            __setniuzi(c, name=newname, length=float(c[3])-25)
            c = getniuzi(member.id)
            await app.send_message(
                group,
                MessageChain(At(member.id), '\n改名成功，消耗 25cm 长度' + bjinfo(c) + ("" if flag else suggestmes)),
            )
    
    return

@channel.use(ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[MatchContent("双修功法")],
    ))
async def tietie(app: Ariadne, group: Group, member: Member, message: MessageChain = MatchContent("双修功法")):
    if checkblacklist(group.id, member.id):
        return
    if (await app.get_friend(member.id)) == None:
        flag = False
    else:
        flag = True

    c = getniuzi(member.id)
    if c == None:
        await app.send_message(
            group,
            MessageChain(At(member.id), '\n你好像还没有宝剑😓，尝试 白嫖宝剑' + ("" if flag else suggestmes)),
        )
    else:
        if isduixiang(c[0], c[5]) == False:
            await app.send_message(
                group,
                MessageChain(At(member.id), '\n你的宝剑好像还没有对象😓，尝试 绑定对象' + ("" if flag else suggestmes)),
            )
            return
        npyt = getniuzi(c[5])
        if npyt == None:
            await app.send_message(
                group,
                MessageChain(At(member.id), '\n找不到你的对象😓' + ("" if flag else suggestmes)),
            )
        if float(c[8]) - time.time() > 0:
            await app.send_message(
                group,
                MessageChain(At(member.id), '\n你修炼得也太频繁了吧😓\n等 %ds 后再来'%(math.ceil(float(c[8]) - time.time())) + ("" if flag else suggestmes)),
            )
            return
        elif float(npyt[8]) - time.time() > 0:
            await app.send_message(
                group,
                MessageChain(At(member.id), '\n你对象修炼时间还没到呢😓\n等 %ds 后再来'%(math.ceil(float(npyt[8]) - time.time())) + ("" if flag else suggestmes)),
            )
            return
        else:
            if random.randint(1, 6) == 1:
                tt = random.randint(3600 * 4, 3600 * 24)
                __setniuzi(c, length=float(c[3]) - 233, ttuntil=time.time() + tt)
                __setniuzi(npyt, length=float(npyt[3]) - 233, ttuntil=time.time() + tt)
                c = getniuzi(member.id)
                await app.send_message(
                    group,
                    MessageChain(At(member.id), '\n修炼走火入魔了😓\n长度减 233cm\n下次修炼需等 %ds'%(math.ceil(float(c[8]) - time.time())) + ("" if flag else suggestmes)),
                )
            else:
                ts = random.uniform(30, 150)
                tt = random.randint(3600 * 4, 3600 * 48)
                __setniuzi(c, length=float(c[3]) + ts, ttuntil=time.time() + tt)
                __setniuzi(npyt, length=float(npyt[3]) + ts, ttuntil=time.time() + tt)
                c = getniuzi(member.id)
                await app.send_message(
                    group,
                    MessageChain(At(member.id), '\n✨修炼成功😄\n获得长度 %scm\n下次修炼需等 %ds'%(str(ts), math.ceil(float(c[8]) - time.time())) + ("" if flag else suggestmes)),
                )

