# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import sqlite3


class WorkSpiderPipeline(object):
    def process_item(self, item, spider):
        return item


# class SaveSQLPipeline(object):
#
#     def __init__(self):
#         self.coon = pymysql.connect(
#             host='127.0.0.1',
#             user='root',
#             password='19960701',
#             db='backend_recruit',
#             port=3306,
#             # 如果需要保存中文，配置以下字符编码
#             use_unicode=True,
#             charset='utf8'
#         )
#         self.cursor = self.conn.cursor()
#
#     def process_item(self, item, spider):
#         pass

# class SaveSQLPipeline(object):
#     conn = ''
#     cursor = ''
#
#     def close_sql(self):
#         self.conn.commit()
#         self.cursor.close()
#         self.conn.close()
#
#     def connect_sql(self):
#         self.conn = sqlite3.connect('backend_recruit.db')
#         self.cursor = self.conn.cursor()
#
#     def process_item(self, item, spider):
#         self.connect_sql()
#
#         item.save(self.cursor)
#         self.close_sql()
#
#         return item


from twisted.enterprise import adbapi
from pymysql import cursors


class TwistedMysqlPipeline(object):

    @classmethod
    def from_settings(cls, settings):

        # 准备需要用到的链接MySQL的参数
        db_prams = dict(
            host=settings['MYSQL_HOST'],
            user=settings['MYSQL_USER'],
            password=settings['MYSQL_PW'],
            db=settings['MYSQL_DB'],
            port=3306,
            use_unicode=True,
            charset=settings['MYSQL_CHARSET'],

            cursorclass=cursors.DictCursor
        )

        db_pool = adbapi.ConnectionPool('pymysql', **db_prams)

        return cls(db_pool)

    def __init__(self, db_pool):
        self.db_pool = db_pool

    def process_item(self, item, spider):
        query = self.db_pool.runInteraction(self.insert_sql, item)

        # 执行sql出现异常错误时，回调的函数
        query.addErrback(self.handle_error, item, spider)

    def handle_error(self, failure, item, spider):
        print('报错了...')
        print(failure)
        print(item)

    def insert_sql(self, cursor, item):
        item.save(item, cursor)
