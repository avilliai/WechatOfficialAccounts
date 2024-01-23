import asyncio
import logging
import os.path
import threading
import zhipuai
import colorlog
import yaml
from zhipuai import ZhipuAI

from cumulus.plugins.txt2img import txtImg


def newLogger():
    # 创建一个logger对象
    logger = logging.getLogger("bert_chatter")
    # 设置日志级别为DEBUG，这样可以输出所有级别的日志
    logger.setLevel(logging.DEBUG)
    # 创建一个StreamHandler对象，用于输出日志到控制台
    console_handler = logging.StreamHandler()
    # 设置控制台输出的日志格式和颜色
    logger.propagate = False
    console_format = '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    console_colors = {
        'DEBUG': 'white',
        'INFO': 'cyan',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
    console_formatter = colorlog.ColoredFormatter(console_format, log_colors=console_colors)
    console_handler.setFormatter(console_formatter)
    # 将控制台处理器添加到logger对象中
    logger.addHandler(console_handler)
    # 使用不同级别的方法来记录不同重要性的事件
    return logger
logger=newLogger()
class CListen(threading.Thread):
    def __init__(self, loop):
        threading.Thread.__init__(self)
        self.mLoop = loop

    def run(self):
        asyncio.set_event_loop(self.mLoop)  # 在新线程中开启一个事件循环

        self.mLoop.run_forever()

from django.shortcuts import render
import hashlib
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import xml.etree.ElementTree as ET
import time
import requests
import random
with open('config.yaml', 'r', encoding='utf-8') as f:
    conf = yaml.load(f.read(), Loader=yaml.FullLoader)
token = conf.get("token")
appid = conf.get("appid")
secret = conf.get("secret")
# 线程预备
newLoop = asyncio.new_event_loop()
listen = CListen(newLoop)
listen.setDaemon(True)
listen.start()
with open('data/chatGLMData.yaml', 'r', encoding='utf-8') as f:
    cha = yaml.load(f.read(), Loader=yaml.FullLoader)
global chatGLMData
chatGLMData = cha
def get_reply(info, username):  # 这个key是一个我自己申请的，大家可以自己注册图灵机器人来获取一个key
    global chatGLMData
    # 构建新的prompt
    if info=="/clear":
        chatGLMData.pop(username)
        return "已清空对话"
    elif info=="帮助":
        return "施工中·"
    tep = {"role": "user", "content": info}
    # print(type(tep))
    # 获取以往的prompt
    if username in chatGLMData:
        prompt = chatGLMData.get(username)
        prompt.append({"role": "user", "content": info})
    # 没有该用户，以本次对话作为prompt
    else:
        prompt = [tep]
        chatGLMData[username] = prompt


    b=asyncio.run_coroutine_threadsafe(asyncchatGLM(prompt,username), newLoop)
    if "[系统检测到输入或生成内容可能包含不安全或敏感内容，请您避免输入易产生敏感内容的提示语，感谢您的配合。]" in b.result():
        return b.result().replace("[系统检测到输入或生成内容可能包含不安全或敏感内容，请您避免输入易产生敏感内容的提示语，感谢您的配合。]","\nps:如果出现聊天异常可以发送 /clear")
    return b.result()

#CharacterchatGLM部分
def chatGLM(prompt):
    #zhipuai.api_key =

    client = ZhipuAI(api_key=conf.get("zhipuai.api_key"))  # 填写您自己的APIKey
    response = client.chat.completions.create(
        model="glm-4",  # 填写需要调用的模型名称
        messages=prompt,
        stream=True,
    )

    str1=''
    for chunk in response:
        str1 += chunk.choices[0].delta.content
        #print()

    '''meta={'user_info': "读者是热爱学习人文社科和先进技术，希望通过与小云的交流学习到更多人文社科相关知识",'user_name': '读者同志','bot_name': '小云','bot_info':"小云是一个热爱人文社科和学习先进技术的ai，小云会回复读者的种种疑问，小云具有丰富的人文社科知识，对于政治学、社会学都有相当程度的专业认知"}
    response = zhipuai.model_api.sse_invoke(
        model="glm-4",
        #meta= meta,
        prompt= prompt,
        incremental=True
    )

    str1=""
    for event in response.events():
      if event.event == "add":
          str1+=event.data
          #print(event.data)
      elif event.event == "error" or event.event == "interrupted":
          str1 += event.data
          #print(event.data)
      elif event.event == "finish":
          str1 += event.data
          #print(event.data)
          print(event.meta)
      else:
          str1 += event.data
          #print(event.data)
    #print(str1)'''
    return str1
# 创建一个异步函数
async def asyncchatGLM(prompt,username):
    global chatGLMData

    loop = asyncio.get_event_loop()
    # 使用 loop.run_in_executor() 方法来将同步函数转换为异步非阻塞的方式进行处理
    # 第一个参数是执行器，可以是 None、ThreadPoolExecutor 或 ProcessPoolExecutor
    # 第二个参数是同步函数名，后面跟着任何你需要传递的参数
    #result=chatGLM(apiKey,bot_info,prompt)

    st1 = await loop.run_in_executor(None, chatGLM,prompt)
    # 打印结果
    #print(result)

    logger.info("chatGLM:" + st1)

    if len(st1)>200:
        p1=txtImg(st1)
    # 更新该用户prompt
    prompt.append({"role": "assistant", "content": st1})
    # 超过10，移除第一个元素

    if len(prompt) > 10:
        logger.error("glm prompt超限，移除元素")
        del prompt[0]
        del prompt[0]
    chatGLMData[username] = prompt
    # 写入文件
    with open('data/chatGLMData.yaml', 'w', encoding="utf-8") as file:
        yaml.dump(chatGLMData, file, allow_unicode=True)
    return st1
def deal_with_content(content, usere):
    return get_reply(content,usere)

access_token = ""
expire_time = 0

def get_access_token():
    global access_token, expire_time
    if time.time() > expire_time:
        url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'.format(appid, secret)
        ans = json.loads(requests.get(url).text)
        access_token = ans["access_token"]
        expire_time = ans["expires_in"] + time.time()
    return access_token
def get_media_ID(path):
    img_url='https://api.weixin.qq.com/cgi-bin/material/add_material'
    payload_img={
        'access_token':get_access_token(),
        'type':'image'
    }
    data ={'media':open(path,'rb')}
    r=requests.post(url=img_url,params=payload_img,files=data)
    dict =r.json()
    return dict['media_id']

# Create your views here.


@csrf_exempt
def weixin_main(request):
    get_access_token()
    if request.method == 'GET':
        signature = request.GET.get('signature', None)
        timestamp = request.GET.get('timestamp', None)
        nonce = request.GET.get('nonce', None)
        echostr = request.GET.get('echostr', None)

        hashlist = [token, timestamp, nonce]
        hashlist.sort()
        hashstr = ''.join(hashlist)
        hashstr = hashlib.sha1(bytes(hashstr, encoding='utf-8')).hexdigest()
        if hashstr == signature:
            return HttpResponse(echostr)
        else:
            print("ERROR")
            return HttpResponse("ERROR")
    else:
        xmldata = ET.fromstring(request.body)
        msg_type = xmldata.find('MsgType').text
        FromUserName = xmldata.find('FromUserName').text
        ToUserName = xmldata.find('ToUserName').text
        if msg_type == 'text':
            Content = xmldata.find('Content').text
            Content = deal_with_content(Content, FromUserName)
            if os.path.isfile(Content):
                MediaId=get_media_ID(Content)
                return_data = """<xml>
                  <ToUserName><![CDATA[{toUser}]]></ToUserName>
                  <FromUserName><![CDATA[{fromUser}]]></FromUserName>
                  <CreateTime>{ctime}</CreateTime>
                  <MsgType><![CDATA[image]]></MsgType>
                  <Image>
                    <MediaId><![CDATA[{Content}]]></MediaId>
                  </Image>
                  </xml>""".format(toUser=FromUserName, fromUser=ToUserName, ctime=time.time(), Content=MediaId)
                return HttpResponse(return_data)
            return_data = """<xml>
  <ToUserName><![CDATA[{toUser}]]></ToUserName>
  <FromUserName><![CDATA[{fromUser}]]></FromUserName>
  <CreateTime>{ctime}</CreateTime>
  <MsgType><![CDATA[text]]></MsgType>
  <Content><![CDATA[{content}]]></Content>
</xml>""".format(toUser=FromUserName, fromUser=ToUserName, ctime=time.time(), content=Content)
            return HttpResponse(return_data)

        return HttpResponse("""<xml>
  <ToUserName><![CDATA[{toUser}]]></ToUserName>
  <FromUserName><![CDATA[{fromUser}]]></FromUserName>
  <CreateTime>{ctime}</CreateTime>
  <MsgType><![CDATA[text]]></MsgType>
  <Content><![CDATA[{content}]]></Content>
</xml>""".format(toUser=FromUserName, fromUser=ToUserName, ctime=time.time(), content="你好！这里是Cumulus积雨云\n博客：https://avilliai.github.io/\n笔记仓库：\nhttps://raonb.netlify.app/\nhttps://cumulus-clouds.netlify.app/\n\n发送 帮助 以获取功能列表\n公众号指令：\n/clear  此指令用于清理聊天内容"))