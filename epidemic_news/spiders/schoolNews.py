# -*- coding: utf-8 -*-
import scrapy

import sys
import os
path = os.path.dirname(__file__)
parent_path = os.path.dirname(path)
sys.path.append(parent_path)

import items

from scrapy.loader import ItemLoader

class SchoolnewsSpider(scrapy.Spider):
    name = 'schoolNews'
    allowed_domains = ['chd.edu.cn']
    start_urls = ['http://www.chd.edu.cn/yqfk/6070/list.htm']

    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
    }


    def parse(self, response):
        '''
        解析获取所有url，生成Request
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
        '''
        解析文章内容
        '''
        item_loader = ItemLoader(item = items.EpidemicNewsItem(),response=response)
        item_loader.add_xpath('title','//title/text()')
        item_loader.add_value('url',response.url)

        item = item_loader.load_item()

        yield item

    def parse_chd(self,response):
        '''
        长安大学官网
        解析域名：www.chd.edu.cn
        示例文章：http://www.chd.edu.cn/2020/0220/c391a121138/page.htm
        '''
        item_loader = ItemLoader(item = items.EpidemicNewsItem(),response=response)
        item_loader.add_xpath('title','//title/text()')
        item_loader.add_value('url',response.url)

        item = item_loader.load_item()

        yield item


    def parse_chdnews(self,response):
        '''
        长安大学新闻网
        解析域名：news.chd.edu.cn       
        示例文章：http://news.chd.edu.cn/2020/0203/c300a120344/page.htm
        '''
        pass

    def parse_jyt_shaanxi(self,response):
        '''
        陕西省教育厅
        解析域名：jyt.shaanxi.gov.cn
        示例文章：http://jyt.shaanxi.gov.cn/jynews/gdxx/202002/09/96635.html
        '''
        pass

    def parse_univs(self,response):
        '''
        中国大学生在线
        解析域名：univs.cn
        示例文章：http://www.univs.cn/zx/a/xy_gxlb/200219/1535583.shtml
        '''
        pass
    
    def parse_wechat(self,response):
        '''
        微信公众号
        解析域名：mp.weixin.qq.com
        示例文章：https://mp.weixin.qq.com/s/QD239VGRmictZPBp7kyehQ
        '''
        pass