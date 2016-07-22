# coding=utf-8
import sqlite3,os

SQLiteDB = os.path.join(os.getcwd(), 'TriggerDB.db')
DBCON = sqlite3.connect(SQLiteDB,check_same_thread=False)
DBCUR = DBCON.cursor()

class SQLiteDB(object):


    @staticmethod
    def insert(sql):
        try:
            DBCUR.execute(sql)
        except sqlite3.Error as e:
            print ("[!]Insert Error! %s" % e.args[0])
        DBCON.commit()
   #     DBCON.close()

    @staticmethod
    def select(sql):
        data = []
        try:
            DBCUR.execute(sql)
            data = DBCUR.fetchall()
        except sqlite3.Error as e:
            print ("[!]Slect Error!%s"% e.args[0])
  #      DBCON.close()
        return data

    @staticmethod
    def CreatTable():
        zabbix_sql ="create table if not exists Zabbix_Trigger (DATA text,TIME integer,HOSTNAME text, \
             HOSTIP text,DESCRIPTION text,LEVEL text);"
        weixin_sql = "create table if not exists Wechat_Sendmsg (DATA text,TIME integer,HOSTNAME text, \
             HOSTIP text,DESCRIPTION text,LEVEL text);"
        try:
            DBCUR.execute(zabbix_sql)
            DBCUR.execute(weixin_sql)
        except sqlite3.Error as e:
            print ("[!]Creat Error! %s" % e.args[0])
        #DBCON.close()

