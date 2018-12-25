# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import datetime
from ..items import JobItem, FirmItem
from .tools import LngLat
from scrapy_redis.spiders import RedisSpider


class A51jobSpider(RedisSpider):
    name = '51job'
    allowed_domains = ['51job.com']
    # start_urls = ['https://search.51job.com/list/170300%252C010000%252C040000,000000,0000,00,9,99,python,2,1.html?lang=c&stype=&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&providesalary=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=&dibiaoid=0&address=&line=&specialarea=00&from=&welfare=']
    redis_key = 'a51job:start_urls'
    count = 1

    def parse(self, response):
        # 51job网页职位链接
        hrefs = response.xpath('//p[@class="t1 "]/span/a/@href').extract()
        for href in hrefs:

            yield Request(
                url=href,
                meta={
                  'href': href
                },
                callback=self.parse_list
            )

        # 获取下一页链接
        next_page = response.xpath('//li[@class="bk"]/a/@href').extract()
        if next_page:
            for next_href in next_page:
                self.count += 1
                print('正在爬取第{}页数据，请稍后......'.format(self.count))
                yield Request(
                    url=next_href,
                )

        else:
            print('没有下一页链接，数据爬取完毕！！！')

    # 获取工作页面详细信息
    def parse_list(self, response):

        # 拿到工作详情页面地址
        job_href = response.meta.get('href')
        # 获取工作名称
        job_title = response.xpath('//div[@class="cn"]/h1/@title').extract_first('无')
        # 职位薪资
        salary = response.xpath('//div[@class="cn"]/strong/text()').extract_first('0')
        if salary == '0':
            # 职位最低薪资
            salary_from = 0

            # 职位最高薪资
            salary_to = 0

            # 是否面议
            is_negotiable = 1
            # 是否年薪
            is_annual_salary = 0
        else:
            is_negotiable = 0
            if '-' in salary:
                salary_from = salary.split('-')[0]
                salary_to = salary.split('-')[-1].split('/')[0]
            else:
                salary_from = 0
                salary_to = salary.split('/')[0]
            # 是否年薪, 年薪为1 月薪为2 天薪为3, 其他为0
            is_annual_salary = salary.split('/')[-1]
            if is_annual_salary == '年':
                is_annual_salary = 1
            elif is_annual_salary == '天':
                is_annual_salary = 2

            elif is_annual_salary == '月':
                is_annual_salary = 3
            else:
                is_annual_salary = 0

        p = response.xpath('//p[@class="msg ltype"]/text()').extract()
        if p:
            # 工作地点
            if p[0]:
                work_place = p[0].replace('\xa0', ' ').strip('\r\n').strip('\t').strip()
            else:
                work_place = '无'
            # 判断工作经验是否存在
            if '经验' in p[1]:
                # 工作经验年限
                years = p[1].strip('\xa0')

                if '无' in years:
                    # 工作经验最低年限
                    years_of_work_from = 0

                    # 工作经验最高年限
                    years_of_work_to = 0

                else:

                    if '-' in years:
                        years_of_work_from = years.split('-')[0]
                        years_of_work_to = years.split('-')[-1].split('年')[0]

                    else:
                        years_of_work_from = 0

                        years_of_work_to = years.split('年')[0]

            # 判断是否有学历要求
            if '招' not in p[2]:

                # 学历要求
                degree = p[2].strip('\xa0')
                # 招聘人数
                member = p[3].strip('\xa0').strip('招').strip('人')
                # 发布日期
                release = p[4].strip('\xa0').strip('\t')
            else:
                # 学历要求
                degree = '无'
                # 招聘人数
                member = p[2].strip('\xa0').strip('招').strip('人')
                # 发布日期
                release = p[3].strip('\xa0').strip('\t')
        else:
            print('没有工作等信息.......')
        # 福利待遇
        temptations = response.xpath('//span[@class="sp4"]/text()').extract()
        temptation = ','.join(temptations)

        div = response.xpath('//div[@class="bmsg job_msg inbox"]')
        # 职位描述
        descriptions = div.xpath('p/text()').extract()
        if descriptions == '':
            description = ','.join(div.xpath('ul/li/p/span/text()').extract()).replace(',', '').strip()
        else:
            description = ','.join(descriptions).replace(',', '').strip()
        # 创建时间
        created_time = datetime.datetime.now()
        # 上班地址
        belong_id1 = response.xpath('//div[@class="bmsg inbox"]/p[@class="fp"]/text()').extract()
        if belong_id1:
            belong_code = belong_id1[1].strip('\t')
        else:
            belong_code = '无'
        resource = '51job'
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

        # 公司详情页面地址
        firm_url = response.xpath('//p[@class="cname"]/a/@href').extract_first('0')
        # 公司名字
        firm_name = response.xpath('//p[@class="cname"]/a/@title').extract_first('无')
        yield Request(
            url=firm_url,
            meta={
                'firm_name': firm_name,
                'member': member,
                'work_place': work_place
            },
            callback=self.parse_detail
        )

    # 解析公司详情页面信息
    def parse_detail(self, response):
        # 获取公司名字
        firm_name = response.meta.get('firm_name')
        # 获取招聘人数
        firm_nature = response.meta.get('member')
        # 公司简介
        firm_introduction = ';'.join(response.xpath('//div[@class="con_txt"]/text()').extract())

        firm = response.xpath('//p[@class="ltype"]/text()').extract()
        firm_scale = firm[1].strip('\xa0')
        if '少' in firm_scale:
            # 公司人数规模最少
            firm_scale_from = 0
            # 公司人数规模最多
            firm_scale_to = firm_scale.split('人')[0].split('于')[-1]

        else:
            firm_scale_from = firm_scale.split('-')[0]

            firm_scale_to = firm_scale.split('-')[-1].split('人')[0]

        # 公司经营行业
        firm_industry = firm[2].strip('\xa0').strip('\t')
        # 公司所在地址
        firm_location = response.xpath('//div[@class="inbox"]/p[@class="fp"]/text()').extract()[1].strip('\r\n').strip()
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

        # 公司所在城市
        firm_place = response.meta.get('work_place')

        # 公司主页官网
        firm_website = response.xpath('//div[@class="inbox"]/p[@class="fp tmsg"]/a/@href').extract_first('null')
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
















