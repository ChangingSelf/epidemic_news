# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from scrapy.shell import inspect_response

'''
import sys
import os
#删去上方第一个#即注释此代码块
path = os.path.dirname(__file__)
parent_path = os.path.dirname(path)
sys.path.append(parent_path)
import items # vscode
'''
from epidemic_news import items # shell
from epidemic_news.items import EpidemicNewsItemLoader as ItemLoader

from urllib.parse import urlparse
import logging

class SchoolnewsSpider(scrapy.Spider):
    name = 'schoolNews'
    allowed_domains = ['chd.edu.cn', 'jyt.shaanxi.gov.cn', 'www.univs.cn', 'mp.weixin.qq.com']

    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
    }

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)

        self.parser_domain_map = {
            'www.chd.edu.cn' : self.parse_chdnews,
            'news.chd.edu.cn' : self.parse_chdnews,

            'www.univs.cn' : self.parse_univs,

            'mp.weixin.qq.com' : self.parse_wechat,

            'www.gov.cn': 'parse_test',
            'jyt.shaanxi.gov.cn': self.parse_jyt_shanxi,
            'www.moe.gov.cn': 'parse_test',
            'www.nhc.gov.cn': 'parse_test',
            'www.mem.gov.cn': 'parse_test',

            'www.xinhuanet.com': 'parse_test',
            'www.chinacdc.cn': 'parse_test',
            'health.people.com.cn': 'parse_test',

            'world.people.com.cn': 'parse_test',
            'cpc.people.com.cn': 'parse_test',

            'www.cnhubei.com': 'parse_test',
            'py.cnhubei.com': 'parse_test',

            'www.piyao.org.cn': 'parse_test',
        }#域名和解析函数的映射字典

    def start_requests(self):
        # 上级精神
        yield scrapy.Request(url="http://www.chd.edu.cn/yqfk/6069/list.htm", meta={"block_type":"上级精神"}, dont_filter=True)
        # 工作动态
        yield scrapy.Request(url="http://www.chd.edu.cn/yqfk/6070/list.htm", meta={"block_type":"上级精神"}, dont_filter=True)
        # 基层动态
        yield scrapy.Request(url="http://www.chd.edu.cn/yqfk/jcdt/list.htm", meta={"block_type":"上级精神"}, dont_filter=True)
        # 通知公告
        yield scrapy.Request(url="http://www.chd.edu.cn/yqfk/6071/list.htm", meta={"block_type":"上级精神"}, dont_filter=True)
        # 防治知识
        yield scrapy.Request(url="http://www.chd.edu.cn/yqfk/6072/list.htm", meta={"block_type":"上级精神"}, dont_filter=True)
        # 拒绝谣言
        yield scrapy.Request(url="http://www.chd.edu.cn/yqfk/6073/list.htm", meta={"block_type":"上级精神"}, dont_filter=True)

    def get_parse(self,url):
        '''
        通过域名,获取对应的解析函数
        :return: parse
        '''
        if 'www.chd.edu.cn/yqfk' in url:
            return self.parse_chd

        demain = self.parse_domain(url)
        parse = self.parser_domain_map.get(demain, None)
        # 返回对应解析器,没有给出一个Error
        if parse:
            return parse
        else:
            self.log(f"Not Parser Error , Url:{url}", level=logging.ERROR)

    def parse_domain(self,url:str):
        '''
        解析域名
        '''
        return urlparse(url).netloc

    def parse_test(self,response):
        pass

    def parse(self, response):
        '''
        解析一级子网站，即目录，获取所有url，生成对应的Request
        '''
        # 获取当前页所有的新闻链接
        box = response.xpath("//div[@class='col_news_con']")
        for li in box.xpath(".//ul[@class='news_list list2']//li"):
            url = li.xpath(".//span[@class='news_title']//a//@href").extract_first()
            title = li.xpath(".//span[@class='news_title']//a//@title").extract_first()
            create_time = li.xpath(".//span[@class='news_meta']//text()").extract_first()

            meta = {'title':title,'url':url,'create_time':create_time,'block_type':response.meta.get('block_type')}
            url = response.urljoin(url) if "http" not in url else url
            yield scrapy.Request(url, callback=self.get_parse(url), meta=meta)

        # 获取下一页
        next_page = response.xpath('//li[contains(@class,"page_nav")]//a[contains(@class,"next")]/@href')
        next_url = next_page.extract_first()
        next_url = response.urljoin(next_url)
        if 'javascript' not in next_url:
            # 如果还有下一页（末页的href是javascript:void(0);）
            yield scrapy.Request(next_url,callback=self.parse,meta={'block_type':response.meta.get('block_type')},dont_filter=True)

    def parse_chd(self,response):
        '''
        长安大学官网(疫情防控)
        解析域名：www.chd.edu.cn/yqfk
        示例文章：http://www.chd.edu.cn/yqfk/2020/0215/c6074a120819/page.htm
        '''
        loader = items.EpidemicNewsItemLoader(item=items.EpidemicNewsItem(), response=response)

        index = response.meta.get("index")
        title = response.meta.get('title')
        block_type = response.meta.get('block_type')

        article_metas = response.xpath("//div[@class='article']//p[@class='arti_metas']//span//text()").extract()

        loader.add_value("title", title)
        loader.add_value("create_time", article_metas[1], re='发布时间：(.*)') # 2020-02-18
        loader.add_value("author", article_metas[0], re='发布者：(.*)')
        loader.add_value("block_type", block_type)
        loader.add_xpath("content", "//div[@class='wp_articlecontent']")
        loader.add_xpath("img", "//div[@class='wp_articlecontent']//@src")
        loader.add_value("article_url", response.url)

        # yield一个用于下载图片的请求
        imgs = loader.get_collected_values("img")
        yield from self.request_imgs(response, imgs)

        yield loader.load_item()

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
        loader.add_value("create_time", article_metas[0], re='发布时间：(.*)') # 发布时间：2020-02-20
        loader.add_value("author", article_metas[1], re='作者：(.*)')
        loader.add_value("block_type", block_type)
        loader.add_xpath("content", "//div[@id='content']")
        loader.add_xpath("img", "//div[@id='content']//@src")
        loader.add_value("article_url", response.url)

        imgs = loader.get_collected_values("img")
        yield from self.request_imgs(response, imgs)

        yield loader.load_item()

    def parse_jyt_shanxi(self,response):
        '''
        陕西省教育厅
        解析域名：jyt.shaanxi.gov.cn
        示例文章：http://jyt.shaanxi.gov.cn/jynews/gdxx/202002/09/96635.html
        '''
        loader = ItemLoader(item=items.JytShanxiItem(), response=response)

        index = response.meta.get("index")
        title = response.meta.get('title')
        block_type = response.meta.get('block_type')

        article_metas = response.xpath("//h1[@class='title']/../../../tr[5]/td/text()").extract()

        loader.add_value("create_time", article_metas[0], re='日期：(\d{4}.*\d{2})')  # 格式:'日期：2020-02-09 17:22:42'
        loader.add_value("title", title)
        loader.add_value("author", '陕西省教育厅')
        loader.add_value("block_type", block_type)
        loader.add_xpath("content", "//div[@id='article']")
        loader.add_xpath("img", "//div[@id='content']//@src")
        loader.add_value("article_url", response.url)

        imgs = loader.get_collected_values("img")
        yield from self.request_imgs(response, imgs)

        yield loader.load_item()

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
        loader.add_xpath("create_time", "//div[@class='detail_t clearfix']/span[2]//text()") # 2020-02-19
        loader.add_xpath("author", "//div[@class='detail_t clearfix']/span[1]//text()", re="来源：(.*)")
        loader.add_value("block_type", block_type)
        loader.add_xpath("content", "//div[@class='detail-content']/div[1]")
        loader.add_xpath("img", "//div[@class='detail-content']/div[1]//@src")
        loader.add_value("article_url", response.url)

        imgs = loader.get_collected_values("img")
        yield from self.request_imgs(response, imgs)

        yield loader.load_item()

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
        loader.add_value("create_time", create_time) # 2020-02-19
        loader.add_xpath("author", "//div[@id='meta_content']/span[1]/text()") # 把左右两边的空白符去掉就行
        loader.add_value("block_type", block_type)
        loader.add_xpath("content", "//div[@class='rich_media_content ']")
        loader.add_xpath("img", "//div[@class='rich_media_content ']//@src")
        loader.add_value("article_url", response.url)

        imgs = loader.get_collected_values("img")
        yield from self.request_imgs(response, imgs)

        yield loader.load_item()


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
                else:
                    self.log(f"不是一个正常的图片链接, \n文章链接:{response.url} \n图片链接:{img} ")