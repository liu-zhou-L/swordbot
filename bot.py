import yaml
import os

import pkgutil

from creart import create
from graia.ariadne.app import Ariadne
from graia.ariadne.connection.config import (
    HttpClientConfig,
    WebsocketClientConfig,
    config,
)
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from graia.broadcast import Broadcast
from graia.ariadne.message.element import Plain

from graia.saya import Saya

saya = create(Saya)

file = open("bot.yml", 'r', encoding="utf-8")
yamlfile = file.read()
file.close()
data =  yaml.full_load(yamlfile)

app = Ariadne(
    connection=config(
        data['QQ'],  # 你的机器人的 qq 号
        data['VerifyKey'],  # 填入 VerifyKey
        HttpClientConfig(host=data['Host']),
        WebsocketClientConfig(host=data['Host'])
    )
)

with saya.module_context():
    saya.require("modules.NiuZi")    

app.launch_blocking()
