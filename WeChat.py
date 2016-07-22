# coding=utf-8
from __future__ import print_function  #使python2.0与3.0的print通用
from ZabbixTriggerDb import SQLiteDB
from random import random
from repr   import repr


from threading import Thread

import os,re,time,sys
import requests,ssl
import xml.dom.minidom,json

if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context
db = SQLiteDB
#伪装请求头
headers = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36'}
myRequests = requests.Session()
myRequests.headers.update(headers)

if sys.platform.startswith('win'):
    pass
else:
    try:
        import qrcode
    except:
        print ("Please use 'pip install qrcode' to install qrcode template")
        exit()


QRImagePath = os.path.join(os.getcwd(), 'qrcode.jpg')



DEBUG = False

#微信
class WeChat(object):

    def __init__(self):
        self.uuid = ''
        self.base_uri = ''
        self.push_uri = ''
        self.redirect_uri = ''
        self.BaseRequest = {}
        self.skey = ''
        self.wxuin = ''
        self.wxsid = ''
        self.skey = ''
        self.deviceId = 'e' + repr(random())[2:17]     #随机生成15位机器码
        self.pass_ticket = ''
        self.MemberList =[]
        self.ContactList = []
        self.AlarmFriends =[]
        self.Intervals = ''
        self.xintiao = ''


    #获取UUID
    def Get_UUID(self):
        url = 'https://login.weixin.qq.com/jslogin'
        params = {
            'appid': 'wx782c26e4c19acffb',
            'fun': 'new',
            'lang': 'zh_CN',
            '_': int(time.time()),
        }
        r = myRequests.get(url=url, params=params)
        r.encoding = 'utf-8'
        data = r.text
        #       data返回,code=200为状态.uuid="IZTW06WnSg=="为uuid
        #   window.QRLogin.code = 200; window.QRLogin.uuid = "IZtWO6WnSg==";
        # 正则匹配:匹配出状态码    以及UUID

        regx = r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)"'
        PM = re.search(regx, data)
        code = PM.group(1)

        if code == '200':
            self.uuid = PM.group(2)
            return True
        return False


    #用于判断发送的内容
    def _transcoding(self, data):
        if not data:
            return data
        result = None
        if type(data) == unicode:
            result = data
        elif type(data) == str:
            result = data.decode('utf-8')
        return result

    #用于显示好友列表
    def _untostr(self,data):
        if type(data) == unicode:
            result = data.encode('utf-8')
            Re = re.compile("\<.*\>")
            info = re.sub(Re, '', result)
        elif type(data) == str:
            info = data
        return info

    #   windows下直接打开二维码图
    def _openWinQRCodeImg(self):
        url = 'https://login.weixin.qq.com/qrcode/' + self.uuid
        params = {
            't': 'webwx',
            '_': int(time.time())
        }

        r = myRequests.get(url=url, params=params)
        f = open(QRImagePath, 'wb')
        f.write(r.content)
        f.close()
        time.sleep(1)
        os.startfile(QRImagePath)

    #   Linux下的二维码处理
    def _printQR(self, mat):
        for i in mat:
            BLACK = '\033[40m  \033[0m'
            WHITE = '\033[47m  \033[0m'
            print (''.join([BLACK if j else WHITE for j in i]))


    def _str2qr(self, str):
        qr = qrcode.QRCode()
        qr.border = 1
        qr.add_data(str)
        mat = qr.get_matrix()
        self._printQR(mat)  # qr.print_tty() or qr.print_ascii()

    #   判断操作系统,选择打开二维码扫描方式
    def genQRCode(self):
        if sys.platform.startswith('win'):
            self._openWinQRCodeImg()
        else:
            self._str2qr('https://login.weixin.qq.com/l/' + self.uuid)


    #等待登陆
    def WaitForLogin(self, tip=1):
        time.sleep(tip)
        url = 'https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login?tip=%s&uuid=%s&_=%s' % (
            tip, self.uuid, int(time.time()))
        r = myRequests.get(url=url)
        r.encoding = 'utf-8'
        data = r.text
        #   data返回：
        #   window.code = 201;

        #判断返回码
        regx = r'window.code=(\d+);'
        pm = re.search(regx, data)
        code = pm.group(1)

        if code == '201':  # 已扫描
            print('[*]成功扫描,请在手机上点击确认以登录')
        elif code == '200':  # 已登录
            print('[.]正在登录...')
            regx = r'window.redirect_uri="(\S+?)";'
            pm = re.search(regx, data)
            self.redirect_uri = pm.group(1) + '&fun=new'
            base_uri = self.redirect_uri[:self.redirect_uri.rfind('/')]
            # push_uri与base_uri对应关系(排名分先后)
            services = [
                ('wx2.qq.com', 'webpush2.weixin.qq.com'),
                ('qq.com', 'webpush.weixin.qq.com'),
                ('web1.wechat.com', 'webpush1.wechat.com'),
                ('web2.wechat.com', 'webpush2.wechat.com'),
                ('wechat.com', 'webpush.wechat.com'),
                ('web1.wechatapp.com', 'webpush1.wechatapp.com'),
            ]
          #  self.push_uri = self.base_uri
            self.push_uri = base_uri
            for (searchUrl, pushUrl) in services:
                if base_uri.find(searchUrl) >= 0:
                    self.push_uri = 'https://%s/cgi-bin/mmwebwx-bin' % pushUrl
                    self.base_uri = 'https://%s/cgi-bin/mmwebwx-bin' % searchUrl
                    break
        elif code == '408':  # 超时
            pass
        # elif code == '400' or code == '500':
        return code

    #登陆
    def login(self):
        r = myRequests.get(url=self.redirect_uri)
        r.encoding = 'utf-8'
        data = r.text
    #    print (data)
        # data返回
        #   < ret > 0 < / ret > < message > OK < / message >
        #   < skey >XXXX < skey >
        #   < wxsid > XXXX < / wxsid >
        #   < wxuin > XXXX < / wxuin >
        #   < pass_ticket > XXXX < / pass_ticket >
        #   < isgrayscale > 1 < / isgrayscale >

        #解析XML文件
        doc = xml.dom.minidom.parseString(data)
        root = doc.documentElement

        for node in root.childNodes:
            if node.nodeName == 'skey':
                self.skey = node.childNodes[0].data
            elif node.nodeName == 'wxsid':
                self.wxsid = node.childNodes[0].data
            elif node.nodeName == 'wxuin':
                self. wxuin = node.childNodes[0].data
            elif node.nodeName == 'pass_ticket':
                self.pass_ticket = node.childNodes[0].data

    #    print('skey: %s, wxsid: %s, wxuin: %s, pass_ticket: %s' % (skey, wxsid,wxuin, pass_ticket))
        if not all((self.skey, self.wxsid, self.wxuin, self.pass_ticket)):
            return False

        self.BaseRequest = {
            'Uin': int(self.wxuin),
            'Sid': self.wxsid,
            'Skey': self.skey,
            'DeviceID': self.deviceId,
        }
     #   print (self.push_uri)
        return True

    #验证RET状态 非0为健康状态
    @staticmethod
    def responseState(func, BaseResponse):
        ErrMsg = BaseResponse['ErrMsg']
        Ret = BaseResponse['Ret']
        if False or Ret != 0:
            print('func: %s, Ret: %d, ErrMsg: %s' % (func, Ret, ErrMsg))
        if Ret != 0:
            return False
        return True



    def webwxinit(self):
        url = ( self.base_uri +'/webwxinit?pass_ticket=%s&skey=%s&r=%s' \
                % (self.pass_ticket, self.skey, int(time.time())))
        params = {'BaseRequest': self.BaseRequest}
        headers = {'content-type': 'application/json; charset=UTF-8'}
        r = myRequests.post(url=url, data=json.dumps(params), headers=headers)
        r.encoding = 'utf-8'
        data = r.json()
        self.SyncKey = data['SyncKey']
        self.User = data['User']
        if False:
            f = open(os.path.join(os.getcwd(), 'webwxinit.json'), 'wb')
            f.write(r.content)
            f.close()

        self.synckey = '|'.join([str(keyVal['Key']) + '_' + str(keyVal['Val']) for keyVal in self.SyncKey['List']])
        state = self.responseState('webwxinit', data['BaseResponse'])
        # test = json.dumps(data,ensure_ascii=False)
        # print (test)
        # print (self.SyncKey)
        # print (self.synckey)
        return state

    def webwxstatusnotify(self):
        url = self.base_uri + \
            '/webwxstatusnotify?lang=zh_CN&pass_ticket=%s' % (self.pass_ticket)
        params = {
            'BaseRequest': self.BaseRequest,
            "Code": 3,
            "FromUserName": self.User['UserName'],
            "ToUserName": self.User['UserName'],
            "ClientMsgId": int(time.time())
        }
        r = myRequests.post(url=url, params=json.dumps(params))
        data = r.json()
        state = self.responseState('WexinStatusNoTify',data['BaseResponse'])
        #return data['BaseResponse']['Ret'] == 0
        return state

    #获取好友列表
    def webwxgetcontact(self):

        url = (self.base_uri +'/webwxgetcontact?pass_ticket=%s&skey=%s&r=%s' % (\
                self.pass_ticket, self.skey, int(time.time())))
        headers = {'content-type': 'application/json; charset=UTF-8'}

        r = myRequests.post(url=url, headers=headers)
        r.encoding = 'utf-8'
        data = r.json()
        if False:
            f = open(os.path.join(os.getcwd(), 'webwxgetcontact.json'), 'wb')
            f.write(r.content)
            f.close()
        self.MemberList = data['MemberList']
        SpecialUsers = ["newsapp", "fmessage", "filehelper", "weibo", "qqmail", "tmessage", "qmessage",\
                        "qqsync","floatbottle", "lbsapp", "shakeapp", "medianote", "qqfriend", "readerapp",\
                        "blogapp", "facebookapp", "masssendapp","meishiapp", "feedsapp", "voip",\
                        "blogappweixin", "weixin", "brandsessionholder", "weixinreminder",\
                        "wxid_novlwrv3lqwv11", "gh_22b87fa7cb3c", "officialaccounts",\
                        "notification_messages", "wxitil", "userexperience_alarm"]
        #将列表中特殊账号删除
        for i in range(len(self.MemberList) - 1, -1, -1):
            Member = self.MemberList[i]
            if Member['VerifyFlag'] & 8 != 0:  # 公众号/服务号
                self.MemberList.remove(Member)
            elif Member['UserName'] in SpecialUsers:  # 特殊账号
                self.MemberList.remove(Member)
            elif Member['UserName'].find('@@') != -1:  # 群聊
                self.MemberList.remove(Member)
            elif Member['UserName'] ==  self.User:  # 自己
                self.MemberList.remove(Member)
        self.ContactList = self.MemberList

        return True

    #发送信息
    def webwxsendmsg(self, word, to='filehelper'):
        url = self.base_uri + \
              '/webwxsendmsg?pass_ticket=%s' % (self.pass_ticket)
        clientMsgId = str(int(time.time() * 1000)) + \
                      str(random())[:5].replace('.', '')
        params = {
            'BaseRequest':{
                "Uin": int(self.wxuin),
                "Sid": self.wxsid,
                "Skey":self.skey,
                "DeviceID": self.deviceId,
            },
            'Scene': 0,
            'Msg':{
                "Type": 1,
                "Content": self._transcoding(word),
                "FromUserName": self.User['UserName'],
                "ToUserName": to,
                "LocalID": clientMsgId,
                "ClientMsgId": clientMsgId,
            }
        }
        headers = {'content-type': 'application/json; charset=UTF-8'}
        data = json.dumps(params, ensure_ascii=False).encode('utf8')
        r =myRequests.post(url,data=data,headers=headers)
        dic = r.json()
        state = self.responseState('SendMsg', dic['BaseResponse'])
        print (params)
        return state
      #  print (params)


    def Wx_Views(self):
        print ('[.]正在获取好友列表..')
        list = self.ContactList
        Alarmlist=[]
        # list = json.dump(List,ensure_ascii=False)
        for i in range(0,len(list)):
            if list:
                list[i]['id'] = i
                Name = self._untostr(list[i]['NickName'])
                Rname = self._untostr(list[i]['RemarkName'])
                Id = i
                #print (list[i])
                print ('\t %d  \t姓名:%s \t 备注:%s' %(Id,Name,Rname))
            else:
                print ('[!]获取失败!')
                exit()
        while True:
            try:
                iNput = raw_input("[.]请设置告警对象ID,使用空格隔开\n")
                Alist = iNput.split(' ')
            except:
                print ("[!]输入错误!")

            try:
                for i in range(0,len(Alist)):
                    if Alist:
                        for j in range(0, len(list)):
                            if int(Alist[i]) == list[j]['id']:
                                print ('[*]你设置的对象是:%s' % self._untostr(list[j]['NickName']))
                                Alarmlist.append(list[j]['UserName'])
                                self.AlarmFriends.append(list[j]['UserName'])
                            else:
                                pass
            except:
                continue
            if self.AlarmFriends:
                Input = raw_input ("[!]确认设置(y/n)")
                if Input == 'y':
                    self.AlarmFriends = Alarmlist
                    break
                elif Input == 'n':
                    Alarmlist = []
                    self.AlarmFriends = []
                    pass
                else:
                    Alarmlist = []
                    self.AlarmFriends = []
                    print ("[!]输入错误")
            else:
                print ("[!]检测不到有效输入,请重试")
        print (self.AlarmFriends)



    def syncCheck(self):
        url = self.push_uri + '/synccheck?'
        params = {
            'skey': self.skey,
            'sid': self.wxsid,
            'uin': self.wxuin,
            'deviceId': self.deviceId,
            'synckey': self.synckey,
            'r': int(time.time()),
        }
        r = myRequests.get(url=url, params=params)
        r.encoding = 'utf-8'
        data = r.text
        # print(data)
        # window.synccheck={retcode:"0",selector:"2"}
        regx = r'window.synccheck={retcode:"(\d+)",selector:"(\d+)"}'
        pm = re.search(regx, data)
        selector = pm.group(2)
        return selector

    def webwxsync(self):
        url = self.base_uri + '/webwxsync?lang=zh_CN&skey=%s&sid=%s&pass_ticket=%s' % \
                              (self.BaseRequest['Skey'], self.BaseRequest['Sid'], self.pass_ticket)
        params = {
            'BaseRequest': self.BaseRequest,
            'SyncKey': self.SyncKey,
            'rr': ~int(time.time()),
        }
        #headers = {'content-type': 'application/json; charset=UTF-8'}
        r = myRequests.post(url=url, data=json.dumps(params))
        r.encoding = 'utf-8'
        data = r.json()
        state = self.responseState('webwxsync', data['BaseResponse'])
        return state

    def Wx_heartBeatLoop(self):
        while True:
            selector = self.syncCheck()
            if selector != '0':
                self.webwxsync()
            time.sleep(int(self.xintiao))
            print ("[*]Wechat心跳正常..")


    def run(self):
        time.sleep(2)
        while True:
            SleepTime = int(self.Intervals)
            print("[*]告警检测心跳..")
            time.sleep(5)
            Time = int(time.time())
            LastTime = Time - int(SleepTime)
            Select_sql = "SELECT * FROM wechat_sendmsg WHERE TIME BETWEEN %d and %d" % (LastTime,Time)
            data = db.select(Select_sql)

            # print (data)
            if data:
                for i in data:
                    print (data )
                    triggerTime = self._untostr(i[0])
                    Hostname =  self._untostr(i[2])
                    HostIP = self._untostr(i[3])
                    Description = self._untostr(i[4])
                    level = self._untostr(i[5])
                    msg = """
[!]发现告警
告警服务器:%s
告警时间:%s
告警IP:%s
告警项:%s
告警级别:%s
""" %(Hostname,triggerTime,HostIP,Description,level)
                    print (msg)
                    for j in range(0,len(self.AlarmFriends)):
                        self.webwxsendmsg(msg,self.AlarmFriends[j])
                        # print (j)
                        # print (self.AlarmFriends)
            else:
                pass


