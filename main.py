import json
import time
import requests
import os

infoUrl = 'http://api.bilibili.com/x/space/acc/info?mid='
guardUrl = 'https://api.live.bilibili.com/xlive/app-room/v2/guardTab/topList'
sendUrl = 'http://api.vc.bilibili.com/web_im/v1/web_im/send_msg'

settings = {}
with open('setting.json') as f:
    settings = json.load(f)


UID = settings['UID']
ROOM = settings['RoomID']
SESSDATA = settings['SESSDATA']
CSRF = settings['bili_jct']


guard_info = requests.get(guardUrl, {
    'roomid': ROOM,
    'page': 1,
    'page_size': 30,
    'ruid': UID
}).json()

guard_num = guard_info['data']['info']['num']
page_num = guard_info['data']['info']['page']

recieve_list = []
name_list = []
for i in range(3):
    recieve_list.append(guard_info['data']['top3'][i]['uid'])
    name_list.append(guard_info['data']['top3'][i]['username'])

for i in range(page_num):
    info = requests.get(guardUrl, {
        'roomid': ROOM,
        'page': i+1,
        'page_size': 30,
        'ruid': UID
    }).json()
    for g in info['data']['list']:
        recieve_list.append(g['uid'])
        name_list.append(g['username'])

# 私信
session = requests.session()
scookies = requests.cookies.RequestsCookieJar()
scookies.set('SESSDATA', SESSDATA, domain='.bilibili.com')
session.cookies = scookies

# 准备好模板
template = ''
with open('template.txt', 'r', encoding='utf-8') as f:
    template = f.read()

codes = []
with open('codes.txt', 'r', encoding='utf-8') as f:
    codes = f.readlines()

if (len(codes) != guard_num):
    print("兑换码与舰长数量不符，请检查。")
    print("兑换码：%d个；舰长：%d个" % (len(codes), guard_num))
    exit()

sendNum = 0

for index in range(len(recieve_list)):
    uname = name_list[index]
    text = template.replace('{name}', uname)
    text = text.replace('{code}', codes[index].replace('\n', ''))
    print('(%d/%d)' % (index+1, len(recieve_list)))
    print('私信内容:')
    print('========')
    print(text)
    print('========')
    cmd = input('确定：')
    os.system('cls')
    if (cmd == 'q'):
        continue
    sendNum += 1
    content = json.dumps({'content': text}, ensure_ascii=False)
    postData = {
        'msg[receiver_type]': 1,
        'msg[receiver_id]': recieve_list[index],                # 接收者id
        'msg[msg_type]': 1,                             # 消息类型 1:文本
        'msg[content]': content,                        # 正文
        'msg[timestamp]': int(time.time()),             # 时间戳
        'msg[sender_uid]': UID,  # 发送者id
        'csrf_token': CSRF,  # csrf_token
        'csrf': CSRF
    }
    data = session.post(sendUrl, data=postData).json()
    if ('code' in data and data['code'] == 0):
        print('Last Send Success')
    else:
        print('Last Send Failed')
        index = index - 1

print('发送完毕(%d/%d)' % (sendNum, len(recieve_list)))
input()
