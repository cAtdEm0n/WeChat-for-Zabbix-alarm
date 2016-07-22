# Zabbix 微信个人账号告警
---
##  运行界面

![](https://raw.githubusercontent.com/cAtdEm0n/WeChat-for-Zabbix-alarm/master/images/1.jpg)

![](https://raw.githubusercontent.com/cAtdEm0n/WeChat-for-Zabbix-alarm/master/images/2.jpg)

![](https://raw.githubusercontent.com/cAtdEm0n/WeChat-for-Zabbix-alarm/master/images/3.jpg)

![](https://raw.githubusercontent.com/cAtdEm0n/WeChat-for-Zabbix-alarm/master/images/4.jpg)

![](https://raw.githubusercontent.com/cAtdEm0n/WeChat-for-Zabbix-alarm/master/images/5.jpg)

---




### 微信部分
优秀源码借鉴：

- [0x5e/wechat-deleted-friends][1]：查看被删除好友
- [Urinx / WeixinBot][2]：网页版微信API，包含终端版微信及微信机器人
- [geeeeeeeeek / electronic-wechat][3]： A better WeChat on macOS and Linux. Fewer bugs, more features. Built with Electron by Zhongyi Tong.
- [xiangzhai / qwx][4] - 网页微信客户端封包大全


  [1]: https://github.com/0x5e/wechat-deleted-friends
  [2]: https://github.com/Urinx/WeixinBot
  [3]:https://github.com/geeeeeeeeek/electronic-wechat
  [4]:https://github.com/xiangzhai/qwx/blob/master/doc/protocol.md

需要设定的部分：

```python
WeChat().Intervals = '3'			#检测心跳间隔
WeChat().xintiao = '2'				#通信心跳
```
---
### Zabbix
  需要设定部分：
  

``` python
Zabbix().Zabbix_Address=''					#Zabbix服务器地址
Zabbix().Zabbix_Username=''					#用户名
Zabbix().Passwd=''							#密码
Zabbix().z_Intervals = ' 600'				#每10分钟将告警记录插入zabbix告警表
Zabbix().w_Intervals = '3600'				#每小时发送一次告警
Zabbix().sleeptime='10'						#Zabbix心跳间隔
```
