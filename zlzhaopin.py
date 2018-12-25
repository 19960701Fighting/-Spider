# -*- coding: utf-8 -*-
import scrapy
import json
import datetime
import requests
from lxml import etree
from ..items import JobItem,FirmItem
from scrapy.http.request import Request
from scrapy_redis.spiders import RedisSpider
from .tools import LngLat


class ZhilianSpider(RedisSpider):
    name = 'zhilian'
    allowed_domains = ['zhaopin.com']
    # start_urls = ['https://fe-api.zhaopin.com/c/i/sou?start=0&pageSize=60&cityId=489&kw=python&kt=3'.format(job_name)]
    redis_key = 'zhilian:start_urls'
    page = 0

    def parse(self, response):
        data = json.loads(response.text)['data']
        results = data['results']
        if results == [ ]:
            return
        for result in results:
            resource = '智联'
            job_href = result['positionURL']
            job_title = result['jobName']
            money = result['salary']
            if '-' in money:
                salary_from = money.split('-')[0]
                salary_to = money.split('-')[1]
                is_negotiable = '否'
            else:
                salary_from = '0'
                salary_to = '0'
                is_negotiable = '是'
            is_annual_salary = '0'
            workingExp = result['workingExp']['name']
            if '-' in workingExp:
                years_of_work_from = workingExp.split('-')[0] + '年'
                years_of_work_to = workingExp.split('-')[1]
            else:
                years_of_work_from = '无经验'
                years_of_work_to = '无经验'
            work_place = result.get('city', '无').get('display', '无')
            degree = result.get('eduLevel','无').get('name','无')
            temptation = result.get('welfare')
            if temptation == [ ]:
                temptation = '暂无工作福利'
            else:
                temptation = ','.join(temptation)
            release = result.get('createDate', '无')
            number = result.get('number')
            url = 'https://jobs.zhaopin.com/{}.htm'.format(number)
            html = requests.get(url)
            res = etree.HTML(html.text)
            descriptions = res.xpath('//div[@class="tab-inner-cont"]/p/text()')
            if descriptions != '':
                description = ''.join(descriptions).replace('\n', '').replace(' ','').replace('\xa0','').replace('\r', '').replace('\t', '')
            else:
                description = '无'

            member = res.xpath('//ul[@class="terminal-ul clearfix"]/li[7]/strong/text()')[0]
            is_alive = '1'
            created_time = datetime.datetime.now()
            modified_time = result.get('updateDate', '无')
            is_add = '0'
            belong_code = result.get('city', '无').get('items')[0].get('code', '无')

            # 公司经度
            firm_lat = result.get('geo').get('lat')
            # 公司维度
            firm_lng = result.get('geo').get('lon')
            company_url = result['company']['url']
            self.page += 60
            next_page = 'https://fe-api.zhaopin.com/c/i/sou?start={}&pageSize=60&cityId=489&kw={}&kt=3'.format(
                self.page, self.name)
            yield Request(url=next_page,callback=self.parse)
            yield Request(url=company_url, meta={'work_place': work_place,'member': member,'firm_lat': firm_lat, 'firm_lng': firm_lng}, callback=self.parse_company, headers={'Host':'company.zhaopin.com','Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3'})
            item = JobItem()
            item['resource'] = resource
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
            item['created_time'] = created_time
            item['belong_code'] = belong_code

            item['modified_time'] = modified_time
            item['is_add'] = is_add
            item['is_alive'] = is_alive
            yield item

    def parse_company(self, response):
        # if 'company' not in response.url:
        #     return
        firm_name = response.xpath('//div[@class="mainLeft"]/div/h1/text()').extract_first().replace('\r\n', '').replace(' ', '')
        people = response.xpath('//table[@class="comTinyDes"]/tr[2]/td[2]/span/text()').extract_first()
        if '-' in people:
            firm_scale_from = response.xpath('//table[@class="comTinyDes"]/tr[2]/td[2]/span/text()').extract_first().split('-')[0] + '人'
            firm_scale_to = response.xpath('//table[@class="comTinyDes"]/tr[2]/td[2]/span/text()').extract_first().split('-')[1]
        else:
            firm_scale_from = '无'
            firm_scale_to = '无'
        firm_nature = response.meta['member']
        firm_place = response.meta['work_place']
        firm_lat = response.meta.get('firm_lat')
        firm_lng = response.meta.get('firm_lng')
        firm_introductions = response.xpath('//div[@class="company-content"]/p/text()').extract()
        if firm_introductions != '':
            firm_introduction = ''.join(firm_introductions).replace('\n', '').replace(' ','').replace('\xa0','').replace('\r', '').replace('\t', '')
        else:
            firm_introduction = '无'
        firm_website = response.xpath('//table[@class="comTinyDes"]/tr[3]/td[2]/span/a/text()').extract_first('无')
        if firm_website == '无':
            firm_industry = ' '.join(response.xpath('//table[@class="comTinyDes"]/tr[3]/td[2]/span/text()').extract())
            firm_location = response.xpath('//table[@class="comTinyDes"]/tr[4]/td[2]/span/text()').extract_first()
        else:
            firm_industry = ' '.join(response.xpath('//table[@class="comTinyDes"]/tr[4]/td[2]/span/text()').extract())
            firm_location = response.xpath('//table[@class="comTinyDes"]/tr[5]/td[2]/span/text()').extract_first()
        created_time = datetime.datetime.now()

        item = FirmItem()
        item['firm_name'] = firm_name
        item['firm_scale_from'] = firm_scale_from
        item['firm_scale_to'] = firm_scale_to
        item['firm_nature'] = firm_nature
        item['firm_place'] = firm_place
        item['firm_introduction'] = firm_introduction
        item['firm_website'] = firm_website
        item['firm_industry'] = firm_industry
        item['firm_location'] = firm_location
        item['firm_lat'] = firm_lat
        item['firm_lng'] = firm_lng
        item['created_time'] = created_time
        yield item























