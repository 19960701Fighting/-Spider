# -*- coding: utf-8 -*-
import scrapy
import json
import datetime
import requests
from lxml import etree
from scrapy.http import Request,FormRequest
from ..items import JobItem, FirmItem
from scrapy_redis.spiders import RedisSpider
'''
https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false

https://www.lagou.com/jobs/list_python?labelWords=&fromSearch=true&suginput=
https://www.lagou.com/gongsi/55446.html
https://www.lagou.com/upload/ltm/oss.html?u=/jobs/list_python&q=551&n=577&d=1020&l=2915&dns=0&p=4518&pi=329&qn=2566&t=1537358318156
https://www.lagou.com/jobs/list_python?labelWords=&fromSearch=true&suginput=
https://www.lagou.com/lagouhtml/a52.html?companyIds=62,1561,1686,534,5330,1499,30648,7902,64575,81970,21643,103299,14093,97399,18655
'''


class LagouSpider(RedisSpider):
    name = 'lagou'
    allowed_domains = ['lagou.com']
    # start_urls = ['http://www.baidu.com']
    redis_key = 'lagou:start_urls'
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Host': 'www.lagou.com',
        'Referer': 'https://www.lagou.com/jobs/list_python?labelWords=&fromSearch=true&suginput=',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    }

    def parse(self, response):
        for x in range(0, 30):
            s = x + 1
            print('正在获取第%s页链接....' % s)
            yield FormRequest(
                url='https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false',
                headers=self.headers,
                formdata={
                    'pn': str(s),
                    'kd': 'python',
                    'first': 'false'
                },
                callback=self.parse_list,
            )

    def parse_list(self, response):
        json_data = json.loads(response.text)
        success = json_data.get('success')
        if success:
            content = json_data.get('content')
            positionResult = content.get('positionResult')
            result = positionResult.get('result')
            for res in result:
                # 来源
                resource = '拉钩'
                # 职位名称
                job_title = res.get('positionName')
                salary = res.get('salary')
                # 薪资最低
                salary_from = salary.split('-')[0]
                # 薪资最高
                salary_to = salary.split('-')[-1]
                # 是否年薪
                is_annual_salary = 0
                # 是否面议
                is_negotiable = 0
                years_or_work = res.get('workYear')
                if '年' in years_or_work:
                    # 工作经验最低
                    years_or_work_from = years_or_work.split('-')[0]
                    # 工作经验最高
                    years_or_work_to = years_or_work.split('-')[-1].split('年')[0]
                else:
                    years_or_work_from = 0
                    years_or_work_to = 0

                # 工作地点
                work_place = res.get('city')
                # 学历要求
                degree = res.get('education')
                # 职位福利
                temptation = res.get('positionAdvantage')
                # 发布日期
                release = res.get('formatCreateTime')
                # 职位描述

                # 招聘人数
                member = '未知'
                # 创建时间
                created_time = res.get('createTime')
                # 上班地址

                # 公司数据
                # 公司简介
                # 公司名字
                firm_name = res.get('companyFullName')
                # 公司规模
                firm_scale = res.get('companySize')
                if '-' in firm_scale:
                    # 公司规模最低
                    firm_scale_from = firm_scale.split('-')[0]
                    # 公司规模最高
                    firm_scale_to = firm_scale.split('-')[-1].split('人')[0]
                else:
                    firm_scale_from = firm_scale.split('人')[0]
                    firm_scale_to = firm_scale.split('人')[-1]
                # 招聘人数
                firm_nature = '未知'
                # 经营行业
                firm_industry = res.get('industryField')
                # 公司所在地 firm_location
                # 公司所在城市
                firm_place = work_place
                # 公司主页网址
                # 公司经度
                firm_lng = res.get('longitude')
                # 公司维度
                firm_lat = res.get('latitude')

                # 工作id
                positionId = res.get('positionId')
                # 拼接工作页面url
                job_href = 'https://www.lagou.com/jobs/{}.html'.format(positionId)
                yield Request(
                    url=job_href,
                    headers={
                        'Host': 'www.lagou.com',
                        'Referer': 'https://www.lagou.com/jobs/list_python?labelWords=sug&fromSearch=true&suginput=pyt',
                        'Accept	': '*/*',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                        'Content-type': 'application/json;charset=utf-8',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0'
                    },
                    meta={
                        'job_href': job_href,
                        'job_title': job_title,
                        'salary_from': salary_from,
                        'salary_to': salary_to,
                        'is_negotiable': is_negotiable,
                        'is_annual_salary': is_annual_salary,
                        'years_or_work_from': years_or_work_from,
                        'years_or_work_to': years_or_work_to,
                        'work_place': work_place,
                        'degree': degree,
                        'temptation': temptation,
                        'release': release,
                        'member': member,
                        'created_time': created_time,
                        'resource': resource,
                    },
                    callback=self.parse_job
                )

                # 公司页面id
                companyId = res.get('companyId')
                # 拼接公司页面地址
                firm_url = 'https://www.lagou.com/gongsi/{}.html'.format(companyId)
                yield Request(
                    url=firm_url,
                    headers={
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Host': 'www.lagou.com',
                        'Referer': 'https://www.lagou.com/jobs/list_python?labelWords=sug&fromSearch=true&suginput=pyt',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0'

                    },
                    meta={
                        'firm_name': firm_name,
                        'firm_scale_from': firm_scale_from,
                        'firm_scale_to': firm_scale_to,
                        'firm_nature': firm_nature,
                        'firm_industry': firm_industry,
                        'firm_place': firm_place,
                        'firm_lng': firm_lng,
                        'firm_lat': firm_lat,
                    },
                    callback=self.parse_firm
                )

        else:
            print('网页请求失败！！！')

    def parse_job(self, response):
        job_href = response.meta.get('job_href')
        job_title = response.meta.get('job_title')
        salary_from = response.meta.get('salary_from')
        salary_to = response.meta.get('salary_to')
        is_negotiable = response.meta.get('is_negotiable')
        is_annual_salary = response.meta.get('is_annual_salary')
        years_or_work_from = response.meta.get('years_or_work_from')
        years_or_work_to = response.meta.get('years_or_work_to')
        work_place = response.meta.get('work_place')
        degree = response.meta.get('degree')
        temptation = response.meta.get('temptation')
        release = response.meta.get('release')
        resource = response.meta.get('resource')
        created_time = response.meta.get('created_time')
        member = response.meta.get('member')

        # 职位描述
        descriptions = response.xpath('//dd[@class="job_bt"]/div/p/text()').extract()
        if descriptions:
            description = ','.join(descriptions).replace(',', '').strip()
        else:
            description = '无'
        # 上班地址
        belong_code1 = response.xpath('//div[@class="work_addr"]//text()').extract()
        belong_code = ','.join(belong_code1).replace(',', '').strip().replace('\n', '').replace(' ', '')[:-4]
        modified_time = '0'
        is_add = '0'
        is_alive = '1'
        item = JobItem()
        item['job_href'] = job_href
        item['job_title'] = job_title
        item['salary_from'] = salary_from
        item['salary_to'] = salary_to
        item['is_negotiable'] = is_negotiable
        item['is_annual_salary'] = is_annual_salary
        item['years_of_work_from'] = years_or_work_from
        item['years_of_work_to'] = years_or_work_to
        item['work_place'] = work_place
        item['degree'] = degree
        item['temptation'] = temptation
        item['release'] = release
        item['description'] = description
        item['member'] = member
        item['belong_code'] = belong_code
        item['created_time'] = created_time
        item['resource'] = resource

        item['modified_time'] = modified_time
        item['is_add'] = is_add
        item['is_alive'] = is_alive
        yield item

    def parse_firm(self, response):
        # 获取公司官网地址
        firm_website = response.xpath('//div[@class="company_main"]/h1/a[@class="hovertips"]/@href').extract_first('未知')

        # 公司简介
        firm_introductions = response.xpath('//div[@class="company_intro_text"]/span[@class="company_content"]/p/text()').extract()
        if firm_introductions:
            firm_introduction = ','.join(firm_introductions).replace(',', '').strip().replace('\xa0', '').replace(' ', '')
        else:
            firm_introduction = '无'
        # 公司地址
        firm_location = response.xpath('//p[@class="mlist_li_desc"]/text()').extract_first('未知')
        if firm_location != '未知':
            firm_location = firm_location.replace(' ', '').strip('\n').strip()
        firm_name = response.meta.get('firm_name')
        firm_scale_from = response.meta.get('firm_scale_from')
        firm_scale_to = response.meta.get('firm_scale_to')
        firm_nature = response.meta.get('firm_nature')
        firm_industry = response.meta.get('firm_industry')
        firm_place = response.meta.get('firm_place')
        firm_lng = response.meta.get('firm_lng')
        firm_lat = response.meta.get('firm_lat')

        created_time = datetime.datetime.now()

        firms = FirmItem()
        firms['firm_introduction'] = firm_introduction
        firms['firm_name'] = firm_name
        firms['firm_scale_from'] = firm_scale_from
        firms['firm_scale_to'] = firm_scale_to
        firms['firm_nature'] = firm_nature
        firms['firm_industry'] = firm_industry
        firms['firm_location'] = firm_location
        firms['firm_place'] = firm_place
        firms['firm_website'] = firm_website
        firms['firm_lng'] = firm_lng
        firms['firm_lat'] = firm_lat
        firms['created_time'] = created_time

        yield firms








