# -*- coding: utf-8 -*-
import base64
import codecs
import json
import random
import time
import re
from threading import Thread
import threading

import jieba
# import matplotlib.pyplot as plt
import numpy as np
import requests
from Crypto.Cipher import AES
from PIL import Image
from wordcloud import WordCloud
from ip_proxy import get_proxy_ip_list

all_comments_list = [] # 存放所有评论
result_filter=[]
warning_msg=[]
global gl_num_remark_all
global proxy_arr
global index_proxy
global proxies
global use_proxy
#爬虫线程
class CommentSpider(Thread):
    def __init__(self,url,filter,song_name,params,encSecKey,i):
        super(CommentSpider,self).__init__()
        self.url=url
        self.filter=filter
        self.song_name=song_name
        self.params=params
        self.encSecKey=encSecKey
        self.i=i

    def run(self):
        json_text = get_json(self.url,self.params,self.encSecKey)
        json_dict = json.loads(json_text)
        try:
            for item in json_dict['comments']:
                comment = item['content'] # 评论内容
                likedCount = item['likedCount'] # 点赞总数
                comment_time = item['time'] # 评论时间(时间戳)
                userID = item['user']['userId'] # 评论者id
                nickname = item['user']['nickname'] # 昵称
                avatarUrl = item['user']['avatarUrl'] # 头像地址
                comment_info = str(self.song_name) + " " +str(userID) + " " + str(nickname) + " " + str(avatarUrl) + " " + str(comment_time) + " " + str(likedCount) + " " + str(comment) + "\n"
                if comment_info.find(self.filter)!=-1:
                    result_filter.append(comment_info)
                #all_comments_list.append(comment_info)

                all_comments_list.append(str(comment_time)+'  '+str(nickname)+'  '+str(comment)+'\n')
            print("第%d页抓取完毕!" % (self.i+1))

        except Exception as err:
            print("第%d页抓取时出现错误!" % (self.i+1))

# 头部信息 #需根据自己浏览器的信息进行替换
headers={    
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
    'Referer':'http://music.163.com/song?id=26124797',
    'Origin':'http://music.163.com',
    'Host':'music.163.com'}

# offset的取值为:(评论页数-1)*20,total第一页为true，其余页为false
# first_param = '{rid:"", offset:"0", total:"true", limit:"20", csrf_token:""}' # 第一个参数
second_param = "010001" # 第二个参数
# 第三个参数
third_param = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
# 第四个参数
forth_param = "0CoJUm6Qyw8W8jud"

def get_ano_proxy_ip():
    global index_proxy
    global proxy_arr
    if index_proxy==len(proxy_arr)-1:
        index_proxy=0
    ip_proxy=proxy_arr[int(index_proxy)]
    index_proxy = index_proxy + 1
    return {'http': 'http://'+ip_proxy}

# 获取参数
def get_params(page): # page为传入页数
    iv = "0102030405060708"
    first_key = forth_param
    second_key = 16 * 'F'
    if(page == 1): # 如果为第一页
        first_param = '{rid:"", offset:"0", total:"true", limit:"20", csrf_token:""}'
        h_encText = AES_encrypt(first_param, first_key, iv)
    else:
        offset = str((page-1)*20)
        first_param = '{rid:"", offset:"%s", total:"%s", limit:"20", csrf_token:""}' %(offset,'false')
        h_encText = AES_encrypt(first_param, first_key, iv)
    h_encText = AES_encrypt(h_encText, second_key, iv)
    return h_encText

# 获取 encSecKey
def get_encSecKey():
    encSecKey = "257348aecb5e556c066de214e531faadd1c55d814f9be95fd06d6bff9f4c7a41f831f6394d5a3fd2e3881736d94a02ca919d952872e7d0a50ebfa1769a7a62d512f5f1ca21aec60bc3819a9c3ffca5eca9a0dba6d6f7249b06f5965ecfff3695b54e1c28f3f624750ed39e7de08fc8493242e26dbc4484a01c76f739e135637c"
    return encSecKey


# 解密过程
def AES_encrypt(text, key, iv):
    pad = 16 - len(text) % 16
    text = text + pad * chr(pad)
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    encrypt_text = encryptor.encrypt(text)
    encrypt_text = base64.b64encode(encrypt_text)
    encrypt_text = str(encrypt_text, encoding="utf-8") #注意一定要加上这一句，没有这一句则出现错误
    return encrypt_text

# 获得评论json数据
def get_json(url, params, encSecKey):
    data = {
         "params": params,
         "encSecKey": encSecKey
    }
    if not use_proxy:
        response = requests.post(url, headers=headers, data=data)
    else:
        response = requests.post(url, headers=headers, data=data,proxies=proxies)
    return response.content

# 抓取某一首歌的全部评论
def get_all_comments(url,filter,song_name):
    global gl_num_remark_all
    global proxies
    params = get_params(1)
    encSecKey = get_encSecKey()
    json_text = get_json(url,params,encSecKey)
    json_dict = json.loads(json_text)

    with open("./temp/commentSpider.json",'w',encoding='utf-8') as json_file:
        json.dump(json_dict,json_file,ensure_ascii=False,indent=2)

    if json_dict['code']!=200:
        print("爬取失败！")
        return False
    else:
        comments_num = int(json_dict['total'])
        if(comments_num % 20 == 0):
            page = comments_num / 20
        else:
            page = int(comments_num / 20) + 1
        # if mode=='ss' and page > 500:
        #     return False
        print("共有%d页评论!" % page)
        # 保存线程
        Thread_list = []
        for i in range(int(page)):  # 逐页抓取
            gl_num_remark_all=gl_num_remark_all+1
            if gl_num_remark_all % 200 ==0:
                time.sleep(2)
            if gl_num_remark_all>500:
                time.sleep(60)
                proxies=get_ano_proxy_ip()
                gl_num_remark_all=0
            params = get_params(i+1)
            encSecKey = get_encSecKey()
            p=CommentSpider(url,filter,song_name,params,encSecKey,i)
            p.start()
            Thread_list.append(p)
        for i in Thread_list:
            i.join()
        
        return True

# 将评论写入文本文件
def save_to_file(list,filename,filename_id):
    try:
        with open(filename,'w',encoding='utf-8') as f:
            f.writelines(list)
        print("写入文件成功!")
    except OSError as e:
        with open(filename_id,'w',encoding='utf-8') as f:
            f.writelines(list)
        print("写入文件成功!")

if __name__ == "__main__":

    song_arr=[]
    sleep_time=5
    global gl_num_remark_all
    gl_num_remark_all=0
    global proxy_arr
    proxy_arr = get_proxy_ip_list()
    #更换为自己的代理示例
    # proxy_arr = ['127.0.0.1:1080','127.0.0.1:1080']
    global index_proxy
    index_proxy = 0
    global proxies
    proxies=get_ano_proxy_ip()
    global use_proxy
    use_proxy=False
    while(True):
        user_input=input("获取单首歌曲评论请输入s,获取歌单下所有歌曲评论请输入ss：")
        if user_input=='s':
            song_id=input("请输入歌曲id：")
            song_arr.append({'song_id':str(song_id),'song_name':str(song_id)})
            break
        elif user_input=='ss':
            # 输入歌单id,生成song——arr
            song_sheet_id = input("请输入歌单id:")
            song_sheet_url = 'http://music.163.com/playlist?id=' + str(song_sheet_id)
            use_proxy_input=input("是否使用代理n/y：")
            if use_proxy_input=='y' or use_proxy_input=='Y':
                print('默认使用http://www.xicidaili.com/nn/的代理，但是经测试代理很不稳定，可手动更换为自己的代理，在commentSpider。py中搜索"更换为自己的代理示例"可以更改。')
                use_proxy=True
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.',
                'Upgrade-Insecure-Requests': '1',
                'Host': 'music.163.com',
                'Accept - Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9'}

            proxy_ip_is_available=False
            result=None
            while(not proxy_ip_is_available):
                try:
                    if not use_proxy:
                        proxy_ip_is_available = True
                        result = requests.get(song_sheet_url, headers=headers)
                    else:
                        proxy_ip_is_available = True
                        proxies=get_ano_proxy_ip()
                        print(proxies)
                        result = requests.get(song_sheet_url, headers=headers, proxies=proxies,timeout=2)
                except BaseException:
                    print('代理不可用更换代理')
                    proxy_arr.pop(index_proxy)
                    index_proxy=index_proxy-1
                    proxy_ip_is_available = False
            result = str(result.content, 'utf-8')
            resutl_match = re.findall('<li><a href="/song\?id=(\d+)">([\S ]{1,35})</a></li>', result,re.I | re.M | re.S)
            for rm in resutl_match:
                song_arr.append({'song_id': str(rm[0]), 'song_name': rm[1]})
                # print(rm[0])
                # print(rm[1])
            break
        else:
            print('输入错误\n')
    filter=input("请输入筛选关键词：")
    print(song_arr)
    index_song=0
    for song in song_arr:
        # if index_song<56:
        #     index_song=index_song+1
        #     continue
        # song_id=input("输入歌曲id：")
        headers['Referer']='http://music.163.com/song?id=' + song['song_id'] + ''
        start_time = time.time() # 开始时间
        url = "http://music.163.com/weapi/v1/resource/comments/R_SO_4_" + song['song_id'] + "?csrf_token=" #替换为你想下载的歌曲R_SO的链接
        filename ="./comments_txt/"+ song['song_name']+".txt" #修改歌曲名称
        filename_id = "./comments_txt/" + song['song_id'] + ".txt"  # 修改歌曲名称
        isCrawSuccess = get_all_comments(url,filter,song['song_name'])

        if isCrawSuccess:
            save_to_file(all_comments_list,filename,filename_id)
            end_time = time.time() #结束时间
            print("爬取评论耗时%f秒." % (end_time - start_time))
            # cloud_mask =np.array(Image.open("cloud.png"))
            # content_text=" ".join(all_comments_list)

            # print("jieba分词开始......")
            # cut_text=" ".join(jieba.cut(content_text))
            # print("jieba分词结束")

            # print("开始生成词云......")
            # wordcloud=WordCloud(background_color="white",width=2000, height=1200, mask=cloud_mask, font_path="myfont.ttf",max_words=2000).generate(cut_text)
            # plt.figure()
            # plt.imshow(wordcloud,interpolation='bilinear')
            # plt.axis('off')
            # plt.show()
            # print("生成完毕！")
            # wordcloud.to_file("./word_cloud/"+song_id+'.png')
        index_song=index_song+1
        # if (index_song % 10) ==0:
        #     time.sleep(120)
        time.sleep(sleep_time)
    print("下面是匹配到的信息：")
    print(result_filter)
    print("下面是报警信息：")
    print(warning_msg)