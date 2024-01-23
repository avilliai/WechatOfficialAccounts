import random

from PIL import Image
import numpy as np
def random_str(random_length=6,chars='AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789@$#_%'):
    """
    生成随机字符串作为验证码
    :param random_length: 字符串长度,默认为6
    :return: 随机字符串
    """
    string = ''

    length = len(chars) - 1
    # random = Random()
    # 设置循环每次取一个字符用来生成随机数
    for i in range(7):
        string +=  ((chars[random.randint(0, length)]))
    return string
import aspose.words as aw
def txtImg(text):
    print("输入到txt")
    p="data/temp/"+random_str()+".txt"
    with open(p,'w',encoding='utf-8') as fp:
        fp.write(text)
    doc = aw.Document(p)
    r=random_str()
    arr1=""
    for page in range(0, doc.page_count):
        extractedPage = doc.extract_pages(page, 1)
        extractedPage.save(f"data/imgs/{r}_{page + 1}.jpg")
        asf=np.array(Image.open(f"data/imgs/{r}_{page + 1}.jpg"))
        if page==0:
            arr1=asf
        else:
            arr1 = np.concatenate((arr1, asf), axis=0)
    img_v = Image.fromarray(arr1)
    p1="data/imgs/"+random_str()+"img_v.jpg"
    img_v.save(p1)
    return p1
#txtImg("抢夺注意力的竞争十分激烈。追热点而没有内线消息，结果就是被同质化产品淹没；不追热点想自己找方向则可能直接被观众忽略创意。**选题是媒体人的第一件大事**传统媒体时代已经过去，互动的媒介时代重要的是转发(指数增长规律)**用普通人的聊天搭建信息链条，形成“去中心化”的传播效果**，和古代有些相似，报纸电台时代倒像是插曲。")