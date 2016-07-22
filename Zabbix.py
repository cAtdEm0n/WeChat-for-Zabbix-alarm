# coding=utf-8
import requests,time,json
from ZabbixTriggerDb import SQLiteDB

myRequests = requests.Session()
db = SQLiteDB

class Zabbix(object):
    def __init__(self):
        self.Holist = []
        self.Zabbix_Address = ''
        self.Zabbix_Username=''
        self.Time = time.strftime('%Y-%m-%d %H:%M')
        self.Passwd = ''
        self.z_Intervals = ''
        self.w_Intervals = ''
        self.sleeptime = ''
        self.Trigger= []
        self.LastTrigger = []
        self.WxTriggerList = []


    def get_auth(self):
        url = '%s/api_jsonrpc.php' % self.Zabbix_Address
        params = json.dumps({
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": self.Zabbix_Username,
                "password": self.Passwd
                },
            "id": 0
        })
        headers = {'content-type': 'application/json; charset=UTF-8'}
        r = myRequests.post(url=url, data=params, headers=headers)
        r.encoding = 'utf-8'
        data = r.json()
        return data['result']




    def get_host(self):
        url = '%s/api_jsonrpc.php' % self.Zabbix_Address
        params = json.dumps({
                "jsonrpc": "2.0",
                "method": "host.get",
                "params": {
                    "output":[
                        "hostid",
                        "name"
                    ],
                "selectInterfaces":[
                    "interfaceid",
                    "ip",
                ]
                },
                "id":2,
                "auth":self.get_auth()
        })
        headers = {'content-type': 'application/json; charset=UTF-8'}
        r = myRequests.post(url=url, data=params, headers=headers)
        r.encoding = 'utf-8'
        data = r.json()
        self.Holist = data['result']
        return self.Holist


    def get_trig(self,hostid):
        url = '%s/api_jsonrpc.php' % self.Zabbix_Address
        params = json.dumps({
                "jsonrpc":"2.0",
                "method":"trigger.get",
                "params": {
                    "output": [
                            "triggerid",
                            "description",
                            "priority"
                            ],
                    "filter": {
                            "value": 1,
                            "hostid":hostid
                            },
                    "sortfield": "priority",
                    "sortorder": "DESC"
                         },
                "auth": self.get_auth(),
                "id":1
        })
        headers = {'content-type': 'application/json; charset=UTF-8'}
        r = myRequests.post(url=url, data=params, headers=headers)
        r.encoding = 'utf-8'
        data = r.json()
        if data['result']:
     #       text = json.dumps(data,ensure_ascii=False)
            return data['result']
        else:
            return None

    #编码
    def _untostr(self,data):
        if type(data) == unicode:
            result = data.encode('utf-8')
        elif type(data) == str:
            result = data
        else:
            result = ''
        return result

    def get_triggerlist(self):
        list = self.Holist
        if list:
            for i in range(0,len(list)):
                # ip = self._untostr(list[i]['interfaces']['ip'])
                trigger = self.get_trig(list[i]['hostid'])
                Level = {'1':'DISASTER','2':'HIGH','3':'AVERAGE','4':'WARNING','5':'INFORMATION',\
                            '6':'NOT CLASSIFIED'}
                if trigger != None:
                    Trigger = self._untostr(trigger[0]['description'])
                    level = self._untostr(trigger[0]['priority'])
                    name = self._untostr(list[i]['name'])
                    ip = self._untostr(list[i]['interfaces'][0]['ip'])
                    Datatime = time.strftime("%Y-%m-%d %H:%M", time.localtime())
                    Time = int(time.time())
                    z_LastTime = Time - int(self.z_Intervals)
                    w_LastTime = Time - int(self.w_Intervals)
                    zabbix_sql = "SELECT * FROM zabbix_trigger WHERE HOSTNAME='%s' and \
    DESCRIPTION='%s' and TIME BETWEEN %d and %d " % (name,Trigger,z_LastTime,Time)
                    z_data = db.select(zabbix_sql)

                    if z_data:
                        pass
                    else:
                        z_Inset_sql = "INSERT INTO zabbix_trigger(DATA,TIME,HOSTNAME,HOSTIP,DESCRIPTION,LEVEL)\
    VALUES('%s',%d,'%s','%s','%s','%s');" % (Datatime,Time,name,ip,Trigger,Level[level])
                        db.insert(z_Inset_sql)

                    wechat_sql = "SELECT * FROM wechat_sendmsg WHERE HOSTNAME='%s' and \
    DESCRIPTION='%s' and TIME BETWEEN %d and %d limit 1" % (name, Trigger, w_LastTime, Time)
                    w_data = db.select(wechat_sql)
                    if w_data:
                        pass
                    else:
                        w_Inset_sql = "INSERT INTO wechat_sendmsg(DATA,TIME,HOSTNAME,HOSTIP,DESCRIPTION,LEVEL)\
    VALUES('%s',%d,'%s','%s','%s','%s');" % (Datatime, Time, name, ip, Trigger, Level[level])
                        db.insert(w_Inset_sql)

        else:
            print ("[!]获取主机列表失败,正在重新获取...")
            self.get_auth()
            self.get_host()
            self.get_triggerlist()



    def run(self):
        while True:
            print ("[*]Zabbix心跳正常..")
            time.sleep(self.sleeptime)
            self.get_triggerlist()



