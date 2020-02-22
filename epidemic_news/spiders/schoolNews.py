# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from scrapy.shell import inspect_response

import sys
from urllib.parse import urlparse
import os
#'''
#删去上方第一个#即注释此代码块
path = os.path.dirname(__file__)
parent_path = os.path.dirname(path)
sys.path.append(parent_path)
#'''
#from epidemic_news import items#pycharm
import items#vscode
from scrapy.loader import ItemLoader

from urllib.parse import urlparse
import time

class SchoolnewsSpider(scrapy.Spider):
    name = 'schoolNews'
    allowed_domains = ['chd.edu.cn', 'jyt.shaanxi.gov.cn', 'www.univs.cn', 'mp.weixin.qq.com']
    start_urls = ['http://www.chd.edu.cn/yqfk/6070/list.htm']

    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
    }

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)

        self.parser_domain_map = {
            #注意此处是域名，改成www.chd.edu.cn/yqfk/的话大部分文章都爬不到了啊
            'www.chd.edu.cn' : self.parse_chd,
            'news.chd.edu.cn' : self.parse_chdnews,
            'jyt.shaanxi.gov.cn' : self.parse_jyt_shanxi,
            'www.univs.cn' : self.parse_univs,
            'mp.weixin.qq.com' : self.parse_wechat
        }#域名和解析函数的映射字典

        self.default_parser = self.parse_news #默认解析函数，当没有找到匹配的域名时使用的函数

    def parse_domain(self,url:str):
        '''
        解析域名
        '''
        return urlparse(url).netloc

    def parse(self, response):
        '''
        解析一级子网站，即目录，获取所有url，生成对应的Request
        '''
        # 获取当前页所有的新闻链接
        news_list = response.xpath('//ul[contains(@class,"news_list")]')
        url_list = news_list.xpath('//li[contains(@class,"news")]//span[contains(@class,"news_title")]/a/@href').extract()
        if url_list != None:
            for url in url_list:
                url = response.urljoin(url)
                #callback = self.parser_domain_map.get(self.parse_domain(url)) or self.default_parser #获取域名
                callback = self.default_parser#测试语句
                yield scrapy.Request(url,callback=callback,dont_filter=True)

        # 获取下一页
        next_page = response.xpath('//li[contains(@class,"page_nav")]//a[contains(@class,"next")]/@href')
        next_url = next_page.extract_first()
        next_url = response.urljoin(next_url)
        if 'javascript' not in next_url:
            # 如果还有下一页（末页的href是javascript:void(0);）
            yield scrapy.Request(next_url,callback=self.parse)


    def parse_news(self,response):
        '''
        默认解析器，解析文章内容
        '''
        item_loader = items.EpidemicNewsItemLoader(item = items.EpidemicNewsItem(),response=response)
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
        loader = ItemLoader(item=items.JytShanxiItem(), response=response)

        index = response.meta.get("index")
        title = response.meta.get('title')
        block_type = response.meta.get('block_type')

        article_metas = response.xpath("//div[@class='article']//p[@class='arti_metas']//span//text()").extract()

        loader.add_value("title", title)
        loader.add_value("create_time", article_metas[1], re='发布时间：(.*?)')
        loader.add_value("author", article_metas[0], re='发布者：(.*)')
        loader.add_value("block_type", block_type)
        loader.add_value("content", "//div[@class='wp_articlecontent']")
        #loader.add_xpath("img", "//div[@class='wp_articlecontent']//@src")
        loader.add_value("article_url", response.url)
        loader.add_value("block_type", block_type)
        loader.add_value("index", index)

        # yield一个用于下载图片的请求
        imgs = loader.get_collected_values("img")

    def parse_chdnews(self,response):
        '''
        长安大学新闻网
        解析域名：news.chd.edu.cn       
        示例文章：http://news.chd.edu.cn/2020/0203/c300a120344/page.htm
        '''

        loader = ItemLoader(item=items.ChdNewsItem(), response=response)

        index = response.meta.get("index")
        title = response.meta.get('title', None)
        block_type = response.meta.get('block_type')

        article_metas = response.xpath("//div[@class='article']//p[@class='arti-metas']//span//text()").extract() # 时间和作者

        loader.add_value("title", title)
        loader.add_value("create_time", article_metas[0])
        loader.add_value("author", article_metas[1], re='作者：(.*)')
        loader.add_value("block_type", block_type)
        loader.add_value("content", "//div[@id='content']")
        loader.add_xpath("img", "//div[@id='content']//@src")
        loader.add_value("article_url", response.url)
        loader.add_value("block_type", block_type)
        loader.add_value("index", index)

        imgs = loader.get_collected_values("img")

    def parse_jyt_shanxi(self,response):
        '''
        陕西省教育厅
        解析域名：jyt.shaanxi.gov.cn
        示例文章：http://jyt.shaanxi.gov.cn/jynews/gdxx/202002/09/96635.html
        '''

        '''
        需要进行修改部分的标记,测试的时候顺便修改
        '''

        loader = ItemLoader(item=items.JytShanxiItem(), response=response)

        index = response.meta.get("index")
        title = response.meta.get('title')
        block_type = response.meta.get('block_type')

        article_metas = response.xpath("//h1[@class='title']/../../../tr[5]/td/text()").extract()


        loader.add_value("create_time", article_metas[0], re='日期：(.*?)')  # 格式:'日期：2020-02-09 17:22:42'
        loader.add_value("title", title)
        loader.add_value("author", '陕西省教育厅')
        loader.add_value("block_type", block_type)
        loader.add_value("content", "//div[@id='article']")
        #loader.add_xpath("img", "//div[@id='content']//@src")
        loader.add_value("article_url", response.url)
        loader.add_value("block_type", block_type)
        loader.add_value("index", index)

        # yield一个用于下载图片的请求
        imgs = loader.get_collected_values("img")

    def parse_univs(self,response):
        '''
        中国大学生在线
        解析域名：univs.cn
        示例文章：http://www.univs.cn/zx/a/xy_gxlb/200219/1535583.shtml
        '''
        loader = ItemLoader(item=items.UnivsItem(), response=response)

        index = response.meta.get("index")
        title = response.meta.get('title', None)
        block_type = response.meta.get('block_type')

        # 来源 和 时间
        article_metas = response.xpath("//div[@class='detail_t clearfix']")

        loader.add_value("title", title)
        loader.add_value("create_time", "//div[@class='detail_t clearfix']/span[2]//text()") # [2020-02-19]
        loader.add_value("author", "//div[@class='detail_t clearfix']/span[1]//text()", re="来源：(.*?)")
        loader.add_value("block_type", block_type)
        loader.add_value("content", "//div[@class='detail-content']/div[1]")
        #loader.add_xpath("img", "//div[@class='detail-content']/div[1]//@src")
        loader.add_value("article_url", response.url)
        loader.add_value("block_type", block_type)
        loader.add_value("index", index)

    def parse_wechat(self,response):
        '''
        微信公众号
        解析域名：mp.weixin.qq.com
        示例文章：https://mp.weixin.qq.com/s/QD239VGRmictZPBp7kyehQ
        '''
        loader = ItemLoader(item=items.WeChatItem(), response=response)

        index = response.meta.get("index")
        title = response.meta.get('title')
        block_type = response.meta.get('block_type')
        create_time = response.meta.get('create_time') # 要在上个页面获取,文章页面没看到时间

        loader.add_value("title", title)
        loader.add_value("create_time", create_time)
        loader.add_value("author", "//div[@id='meta_content']/span[1]/text()") # 把左右两边的空格去掉就行
        loader.add_value("block_type", block_type)
        loader.add_value("content", "//div[@class='rich_media_content ']")
        #loader.add_xpath("img", "//div[@class='rich_media_content ']//@src")
        loader.add_value("article_url", response.url)
        loader.add_value("block_type", block_type)
        loader.add_value("index", index)


    def parse_img(self,responsee):
        '''
        下载、保存图片
        :param responsee:
        :return:
        '''
        pass

    def request_imgs(self, response, imgs):
        '''
        构造一个图片请求
        :param response:
        :param imgs:
        :return:
        '''
        if imgs:
            for img in imgs:
                if "http" in img:
                    yield Request(img, callback=self.parse_img, dont_filter=True,
                                  meta={"type": "image", "article_url": response.url})