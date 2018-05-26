import requests
import re

song_sheet_id=input("请输入歌单id:")
headers={
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.',
    'Upgrade-Insecure-Requests':'1',
    'Host':'music.163.com',
    'Accept - Encoding': 'gzip, deflate',
    'Accept-Language':'zh-CN,zh;q=0.9'}
url='http://music.163.com/playlist?id='
result = requests.get(url+str(song_sheet_id),headers=headers,proxies={'http': 'http://127.0.0.1:1080'})
result=str(result.content,'utf-8')
print (result)
resutl_match=re.findall('<li><a href="/song\?id=(\d+)">([\S ]{1,30})</a></li>', result, re.I|re.M|re.S)
print (resutl_match)
for  rm in resutl_match:
    print(rm[0])
    print(rm[1])
