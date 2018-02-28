#!/usr/bin/env python 3
# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup
from contextlib import closing
import requests, json, time, re, os, sys, time
import numpy as np
import csv
import pymysql
from requests.packages.urllib3.exceptions import InsecureRequestWarning
# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# 用来操作数据库的类
class MySQLCommand(object):
    # 类的初始化
    def __init__(self):
        self.host = 'localhost'
        self.port = 3306  # 端口号
        self.user = ''  # 用户名
        self.password = ""  # 密码
        self.db = ""  # 库
        self.table = ""  # 表

    # 链接数据库
    def connectMysql(self):
        try:
            self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user,
                                        passwd=self.password, db=self.db, charset='utf8')
            self.cursor = self.conn.cursor()
        except:
            print('connect mysql error.')

    # 插入数据，插入之前先查询是否存在，如果存在就不再插入
    def insertData(self, my_dict):
        table = "home_list"  # 要操作的表格
        # 注意，这里查询的sql语句url=' %s '中%s的前后要有空格
        sqlExit = "SELECT url FROM home_list  WHERE url = ' %s '" % (my_dict['url'])
        res = self.cursor.execute(sqlExit)
        if res:  # res为查询到的数据条数如果大于0就代表数据已经存在
            print("数据已存在", res)
            return 0
        # 数据不存在才执行下面的插入操作
        try:
            cols = ', '.join(my_dict.keys())#用，分割
            values = '"," '.join(my_dict.values())
            sql = "INSERT INTO home_list (%s) VALUES (%s)" % (cols, '"' + values + '"')
            #拼装后的sql如下
            # INSERT INTO home_list (img_path, url, id, title) VALUES ("https://img.huxiucdn.com.jpg"," https://www.huxiu.com90.html"," 12"," ")
            try:
                result = self.cursor.execute(sql)
                insert_id = self.conn.insert_id()  # 插入成功后返回的id
                self.conn.commit()
                # 判断是否执行成功
                if result:
                    print("插入成功", insert_id)
                    return insert_id + 1
            except pymysql.Error as e:
                # 发生错误时回滚
                self.conn.rollback()
                # 主键唯一，无法插入
                if "key 'PRIMARY'" in e.args[1]:
                    print("数据已存在，未插入数据")
                else:
                    print("插入数据失败，原因 %d: %s" % (e.args[0], e.args[1]))
        except pymysql.Error as e:
            print("数据库错误，原因%d: %s" % (e.args[0], e.args[1]))

    # 查询最后一条数据的id值
    def getLastId(self):
        sql = "SELECT max(id) FROM " + self.table
        try:
            self.cursor.execute(sql)
            row = self.cursor.fetchone()  # 获取查询到的第一条数据
            if row[0]:
                return row[0]  # 返回最后一条数据的id
            else:
                return 0  # 如果表格为空就返回0
        except:
            print(sql + ' execute failed.')

    def closeMysql(self):
        self.cursor.close()
        self.conn.close()  # 创建数据库操作类的实例


class ScrapyDouYin(object):
    def __init__(self):
        self.CsvFileName = "douyin_example.csv"
        self.CsvData = []
        pass

    def get_info(self, user_id):
        unique_id = ''
        while unique_id == '':
            search_url = 'https://api.amemv.com/aweme/v1/discover/search/?cursor=0&keyword=%s&count=10&type=1&retry_type=no_retry&iid=17900846586&device_id=34692364855&ac=wifi&channel=xiaomi&aid=1128&app_name=aweme&version_code=162&version_name=1.6.2&device_platform=android&ssmix=a&device_type=MI+5&device_brand=Xiaomi&os_api=24&os_version=7.0&uuid=861945034132187&openudid=dc451556fc0eeadb&manifest_version_code=162&resolution=1080*1920&dpi=480&update_version_code=1622' % user_id
            req = requests.get(url=search_url, verify=False)
            html = json.loads(req.text)
            try:
                user_list = html['user_list']
                print (user_list)
            except:
                return -1

            for user in user_list:
                aweme_count = user['user_info']['aweme_count']
                favoriting_count = user['user_info']['favoriting_count']
                total_favorited = user['user_info']['total_favorited']
                gender = user['user_info']['gender']
                bind_phone = user['user_info']['bind_phone']
                following_count = user['user_info']['following_count']
                follower_count = user['user_info']['follower_count']
                avatar_large = user['user_info']['avatar_larger']['url_list'][0]
                is_verified = user['user_info']['is_verified']
                school_name = user['user_info']['school_name']
                custom_verify = user['user_info']['custom_verify']
                r_dt = time.localtime(user['user_info']['create_time'])
                register_time = time.strftime("%Y-%m-%d %H:%M:%S", r_dt)
                birthday = user['user_info']['birthday']
                uid = user['user_info']['uid']
                nickname = user['user_info']['nickname']
                unique_id = user['user_info']['unique_id']
                short_id = user['user_info']['short_id']
                constellation = user['user_info']['constellation']


            # print (user_info)

        return uid, short_id, unique_id, nickname, custom_verify, gender, birthday, constellation, total_favorited, following_count, follower_count, aweme_count, favoriting_count, is_verified, bind_phone, school_name, register_time, avatar_large

    def run(self):
        self.hello()
        # user_id = input('请输入ID(例如173553803):')
        csvFile = open(self.CsvFileName, 'w', encoding='utf-8', newline='')
        douyinWriter = csv.writer(csvFile, dialect='excel')
        douyinWriter.writerow(["用户id", "短id", "自定义id", "昵称", "简介",  "性别", "生日", "星座",
                               "作品获赞", "关注数量", "粉丝数量", "作品总计", "喜爱视频总计", "是否实名",
                               "绑定手机", "学校名称", "注册时间", "头像地址"])
        for user_id in range(77054793,77054794):
            user_info = self.get_info(user_id)
            sys.stdout.write('爬取用户id-%s信息中: ...  ' % user_id)
            if user_info == -1:
                print ("failed.")
            else:
                self.CsvData.append(user_info)
                print ("success.")
        # 将CsvData中的数据循环写入到CsvFileName文件中
        try:
            for item in self.CsvData:
                douyinWriter.writerow(item)
        finally:
            csvFile.close()
        print ("成功导出CSV文件！")

    def hello(self):
        print('*' * 100)
        print('\t\t\t\t抖音App用户信息爬取')
        print('*' * 100)


if __name__ == '__main__':
    Scrapydouyin = ScrapyDouYin()
    start = time.time()
    Scrapydouyin.run()
    end = time.time()
    print (end - start)
