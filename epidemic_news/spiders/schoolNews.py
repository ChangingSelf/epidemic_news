# -*- coding: utf-8 -*-
import scrapy

import sys
import os
path = os.path.dirname(__file__)
parent_path = os.path.dirname(path)
sys.path.append(parent_path)

import items

class SchoolnewsSpider(scrapy.Spider):
    name = 'schoolNews'
    allowed_domains = ['chd.edu.cn']
    start_urls = ['http://www.chd.edu.cn/yqfk/6070/list.htm']

    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
    }


    def parse(self, response):
        '''
        解析获取所有url
        '''
        # 获取当前页所有的新闻链接
        news_list = response.xpath('//ul[contains(@class,"news_list")]')
        url_list = news_list.xpath('//li[contains(@class,"news")]//span[contains(@class,"news_title")]/a/@href').extract()
        if url_list != None:
            for url in url_list:
                url = response.urljoin(url)
                yield scrapy.Request(url,callback=self.parse_news,dont_filter=True)

        # 获取下一页
        next_page = response.xpath('//li[contains(@class,"page_nav")]//a[contains(@class,"next")]/@href')
        next_url = next_page.extract_first()
        next_url = response.urljoin(next_url)
        if 'javascript' not in next_url:
            # 如果还有下一页（末页的href是javascript:void(0);）
            yield scrapy.Request(next_url,callback=self.parse)

    def parse_news(self,response):
        item = items.EpidemicNewsItem()
        #item['title'] = response.xpath('//h1[contains(@class,"arti-title") or contains(@class,"arti_title")]/text()').extract_first()#不适用于别的网站的文章
        item['title'] = response.xpath('//title/text()').extract_first()
        item['url'] = response.url
        yield item
        #next_page = response.xpath('//li[contains(@class,"page_nav")]//a[contains(@class,"next")]/@href')
        '''
        In [5]: response.xpath('//*[contains(@class,"arti-title")]/text()').extract_first()
        Out[5]: '学校召开新冠肺炎疫情防控专题工作视频会议 安排部署疫情防控相关工作'
        '''