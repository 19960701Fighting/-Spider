# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import datetime

from .tools import LngLat

from ..items import JobItem, FirmItem
from scrapy_redis.spiders import RedisSpider


class LiepinSpider(RedisSpider):
    name = 'liepin'
    allowed_domains = ['liepin.com']
    # start_urls = ['https://www.liepin.com/zhaopin/?sfrom=click-pc_homepage-centre_searchbox-search_new&d_sfrom=search_fp&key=python']
    # redis_key 启动爬虫是，会使用这个值作为从redis读取url地址的标识
    redis_key = 'liepin:start_urls'
    base_url = 'https://www.liepin.com'
    count = 1

    def parse(self, response):

        hrefs = response.xpath('//div[@class="job-info"]/h3/a/@href').extract()
        for href in hrefs:

            yield Request(
                url=href,
                meta={
                    'href': href
                },
                callback=self.parse_list

            )

        # 获取下一页链接
        next_page = response.xpath('//div[@class="pagerbar"]/a[last()-1]').extract()
        if next_page:
            if '下一页' in next_page[0]:
                for next_href in next_page:
                    next_url = response.xpath('//div[@class="pagerbar"]/a[last()-1]/@href').extract_first('')
                    url = self.base_url + next_url
                    self.count += 1
                    print('正在爬取第{}页数据信息.... 请稍后！！！'.format(self.count))

                    yield Request(
                        url=url,
                    )
            else:
                print('没有下一页！！！')
        else:
            print('数据爬取完毕！！！')

    def parse_list(self, response):
        # 来源
        resource = '猎聘'
        # 获取职位详情页面href
        job_href = response.meta.get('href')
        # 获取职位名称
        job_title = response.xpath('//div[@class="title-info"]/h1/@title').extract_first('无')
        # 职位薪资
        salary = response.xpath('//p[@class="job-item-title"]/text()').extract_first('')
        if '-' in salary:
            # 薪资最小
            salary_from = salary.split('-')[0]
            # 薪资最高
            salary_to = salary.split('-')[-1].split('万')[0]

            # 是否面议
            is_negotiable = 0
            # 是否年薪
            is_annual_salary = 1
        else:
            salary_from = 0
            salary_to = 0
            is_negotiable = 1
            is_annual_salary = 0

        # 工作经验
        years_of_work = response.xpath('//div[@class="job-qualifications"]/span[2]/text()').extract_first('0')
        if '年' in years_of_work:
            # 最低工作经验
            years_of_work_from = years_of_work.split('年')[0]
            # 最高工作经验
            years_of_work_to = '更多'
        else:
            years_of_work_from = 0
            years_of_work_to = 0

        # 学历要求
        degree = response.xpath('//div[@class="job-qualifications"]/span[1]/text()').extract_first('不限学历')
        # 工作地点
        work_place = response.xpath('//p[@class="basic-infor"]/span/a/text()').extract_first('无')
        # 职位福利
        temptations = response.xpath('//ul[@class="comp-tag-list clearfix"]/li/span/text()').extract()
        temptation = ';'.join(temptations)
        # 发布日期
        release = response.xpath('//p[@class="basic-infor"]/time/@title').extract_first('无')
        # 职位描述
        descriptions = response.xpath('//div[@class="content content-word"]/text()').extract()
        if descriptions:
            description = ';'.join(descriptions).strip('\r\n').strip('\t').replace(';', '').strip()
        else:
            description = '无职位描述'

        # 招聘人数
        member = '未知'

        # 上班地址 即所属部门
        belong_code = response.xpath('//div[@class="content"]/ul/li[1]/label/text()').extract_first('无')

        # 创建时间
        created_time = datetime.datetime.now()
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
        item['years_of_work_from'] = years_of_work_from
        item['years_of_work_to'] = years_of_work_to
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

        # 获取公司详情页面地址
        firm_url = response.xpath('//div[@class="title-info"]/h3/a/@href').extract_first('')

        # 公司名字
        firm_name = response.xpath('//div[@class="title-info"]/h3/a/@title').extract_first('无')

        yield Request(
            url=firm_url,
            meta={
                'firm_name': firm_name,
                'member': member,
                'work_place': work_place
            },
            callback=self.parse_detail
        )

    def parse_detail(self, response):
        # 获取公司名字
        firm_name = response.meta.get('firm_name')
        # 获取招聘人数
        firm_nature = response.meta.get('member')
        # 公司所在城市
        firm_place = response.meta.get('work_place')
        # 获取公司简介
        firm_introductions = response.xpath('//div[@class="company-introduction clearfix"]/p[@class="profile"]/text()').extract()
        if firm_introductions:
            # 公司简介
            firm_introduction = ';'.join(firm_introductions).strip('\r\n').strip('\t').replace(';', '').strip()

            if 'http://' in firm_introductions[-1]:
                # 公司主页官网
                firm_website = firm_introductions[-1].split('：')[-1].strip('\r\n').strip('\t')
            else:
                firm_website = '无'
        else:
            firm_introduction = '无'
            firm_website = '无'

        # 公司规模
        firm_scale = response.xpath('//div[@class="comp-summary-tag"]/a/text()').extract()
        if '人' in firm_scale[1]:
            # 公司规模人数最少
            firm_scale_from = firm_scale[1].split('-')[0]

            # 公司规模人数最多
            firm_scale_to = firm_scale[1].split('-')[-1].split('人')[0]
        elif '人' in firm_scale[0]:
            firm_scale_from = firm_scale[0].split('-')[0]
            firm_scale_to = firm_scale[0].split('-')[-1].split('人')[0]
        else:
            firm_scale_from = 0
            firm_scale_to = 0
        # 公司经营行业
        firm_industry = firm_scale[-1]

        # 公司地址
        firm_location = response.xpath('//ul[@class="new-compintro"]/li/@title').extract_first('无')
        try:
            lng_lat = LngLat()
            lng_lat_1 = lng_lat.gaode_api(firm_location)
            # 公司经度
            firm_lng = lng_lat_1[0]
            # 公司维度
            firm_lat = lng_lat_1[1]
        except Exception as e:
            print('没有返回经纬度！！！！')
            firm_lng = 0
            firm_lat = 0

        # 创建时间
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









