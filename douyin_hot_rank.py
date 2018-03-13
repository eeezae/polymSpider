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


class ScrapyDouYin(object):
    def __init__(self):
        self.CsvFileName = "douyin_hot_rank_example.csv"
        self.CsvData = []
        pass

    def get_info(self, user_id):
        user_url = 'https://api.amemv.com/aweme/v1/discover/search/?cursor=0&keyword=%s&count=10&type=1&retry_type=no_retry&iid=17900846586&device_id=34692364855&ac=wifi&channel=xiaomi&aid=1128&app_name=aweme&version_code=162&version_name=1.6.2&device_platform=android&ssmix=a&device_type=MI+5&device_brand=Xiaomi&os_api=24&os_version=7.0&uuid=861945034132187&openudid=dc451556fc0eeadb&manifest_version_code=162&resolution=1080*1920&dpi=480&update_version_code=1622' % user_id
        user_req = requests.get(url=user_url, verify=False)
        user_html = json.loads(user_req.text)
        try:
            user_list = user_html['user_list']
        except:
            return -1

        for user in user_list:
            uid = user['user_info']['uid']
            follower_count = user['user_info']['follower_count']
            nickname = user['user_info']['nickname']

        post_url = 'https://www.douyin.com/aweme/v1/aweme/post/?user_id=%s&max_cursor=0&count=10' % uid
        post_req = requests.get(url=post_url, verify=False)
        post_html = json.loads(post_req.text)
        try:
            post_list = post_html['aweme_list']
            print (post_list)
        except:
            return -1

        play_count_list = []
        share_count_list = []
        comment_count_list = []

        for post in post_list:
            play_count_list.append(post['statistics']['play_count'])
            share_count_list.append(post['statistics']['share_count'])
            comment_count_list.append(post['statistics']['comment_count'])

        if play_count_list:
            play_count = max(play_count_list)
        else:
            play_count = 0
        if share_count_list:
            share_count = max(share_count_list)
        else:
            share_count = 0
        if comment_count_list:
            comment_count = max(comment_count_list)
        else:
            comment_count = 0

        return nickname, follower_count, play_count, comment_count, share_count

    def run(self):
        self.hello()
        user_id_str = input('请输入ID,多个id以逗号分隔(例如173, 255, 38, 63):')
        user_id_group = user_id_str.strip(' ').split(',')
        csvFile = open(self.CsvFileName, 'w', encoding='utf-8', newline='')
        douyinWriter = csv.writer(csvFile, dialect='excel')
        douyinWriter.writerow(["昵称", "粉丝数", "转发量", "评论数", "点赞数"])
        # for user_id in range(77054793, 77054794):
        for user_id in user_id_group:
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
        print('\t\t\t\t抖音App用户热度值爬取')
        print('*' * 100)


if __name__ == '__main__':
    Scrapydouyin = ScrapyDouYin()
    start = time.time()
    Scrapydouyin.run()
    end = time.time()
    print (end - start)
