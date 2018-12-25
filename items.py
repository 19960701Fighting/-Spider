# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WorkSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


# 工作详情
class JobItem(scrapy.Item):

    job_href = scrapy.Field()
    job_title = scrapy.Field()
    salary_from = scrapy.Field()
    salary_to = scrapy.Field()
    years_of_work_from = scrapy.Field()
    years_of_work_to = scrapy.Field()
    work_place = scrapy.Field()
    degree = scrapy.Field()
    temptation = scrapy.Field()
    release = scrapy.Field()
    description = scrapy.Field()
    member = scrapy.Field()
    belong_code = scrapy.Field()
    is_annual_salary = scrapy.Field()
    is_negotiable = scrapy.Field()
    created_time =scrapy.Field()
    resource = scrapy.Field()
    modified_time = scrapy.Field()
    is_alive = scrapy.Field()
    is_add = scrapy.Field()

    def save(self, item, cursor):
        sql = """INSERT INTO jobs(resource, url, job_name, salary_from, salary_to, is_annual_salary, is_negotiable, years_of_work_from, years_of_work_to, work_place, degree, temptation, `release`, `description`, member, is_alive, created_time, modified_time, is_add, belong_code)VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        cursor.execute(sql, (item['resource'], item['job_href'], item['job_title'], item['salary_from'], item['salary_to'], item['is_annual_salary'], item['is_negotiable'], item['years_of_work_from'], item['years_of_work_to'], item['work_place'], item['degree'], item['temptation'], item['release'], item['description'], item['member'], item['is_alive'], item['created_time'], item['modified_time'], item['is_add'], item['belong_code']))


# 公司详情
class FirmItem(scrapy.Item):
    firm_introduction = scrapy.Field()
    firm_name = scrapy.Field()
    firm_scale_from = scrapy.Field()
    firm_scale_to = scrapy.Field()
    firm_nature = scrapy.Field()
    firm_industry = scrapy.Field()
    firm_location = scrapy.Field()
    firm_place = scrapy.Field()
    firm_website = scrapy.Field()
    firm_lat = scrapy.Field()
    firm_lng = scrapy.Field()
    created_time = scrapy.Field()

    def save(self, firms, cursor):
        sql = "INSERT INTO firm(firm_introduction, firm_name,firm_scale_from,firm_scale_to,firm_nature,firm_industry,firm_location,firm_place,firm_website,firm_lng,firm_lat,is_alive, created_time, modified_time,is_add)VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql, (firms['firm_introduction'],firms['firm_name'],firms['firm_scale_from'],firms['firm_scale_to'],firms['firm_nature'],firms['firm_industry'],firms['firm_location'],firms['firm_place'],firms['firm_website'],firms['firm_lng'], firms['firm_lat'],'1', firms['created_time'],'0','0'))


