# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from fake_useragent import UserAgent
import requests


class RandomUserAgent(object):
    """This middleware allows spiders to override the user_agent"""

    def __init__(self):
        self.user_agent = UserAgent()

    def process_request(self, request, spider):

        # proxy = requests.get('http://127.0.0.1:5010/get/').text
        # request.meta['proxy'] = 'http://' + proxy
        request.headers.setdefault(b'User-Agent', self.user_agent.random)