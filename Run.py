# coding=utf-8
from __future__ import print_function  #使python2.0与3.0的print通用
from Zabbix import Zabbix
from ZabbixTriggerDb import SQLiteDB
from WeChat import WeChat
import os,sys,thread,time








if __name__ == '__main__':


    db = SQLiteDB
    db.CreatTable()
    z = Zabbix()    #zabbix类
    w = WeChat()    #wechat类
    th = []

    z.Zabbix_Address = ''
    z.Zabbix_Username = ''
    z.Passwd = ''

    z.z_Intervals = 600     #zabbix告警入库间隔
    z.w_Intervals = 3600    #wechat告警入库间隔

    z.sleeptime = 10        #Zabbix心跳间隔
    w.Intervals = 3         #告警检测心跳间隔
    w.xintiao = 2           #微信心跳间隔

    z.get_auth()            #zabbix token
    z.get_host()            #zabbix hostlist
    z.get_triggerlist()     #zabbix triggerlist


    if not w.Get_UUID():
        print('[!]获取uuid失败,请重新运行!')
    print('[*]正在获取二维码图片...')

    w.genQRCode()       #获取二维码

    while w.WaitForLogin() != '200':
        pass

    w.login()           #登陆
    if sys.platform.startswith('win'):
        os.remove(QRImagePath)

    w.webwxinit()       #初始化
    w.webwxgetcontact() #获取好友列表
    w.Wx_Views()        #设置告警好友

    def RUN():
        thread.start_new(z.run, ())
        thread.start_new(w.run, ())
    RUN()
    w.Wx_heartBeatLoop()





