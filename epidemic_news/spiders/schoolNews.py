# -*- coding: utf-8 -*-
from urllib.parse import urlparse
import logging

import scrapy
from scrapy.http import Request
from scrapy.shell import inspect_response
from scrapy.exceptions import IgnoreRequest
from scrapy.http.cookies import CookieJar

'''
import sys
import os

path = os.path.dirname(__file__)
parent_path = os.path.dirname(path)
sys.path.append(parent_path)
import items # vscode
'''
from epidemic_news import items # shell
from epidemic_news.items import EpidemicNewsItemLoader as ItemLoader


cookjar = CookieJar()

class SpiderTools():
    ''' 在Spider中常用的函数 '''
    def __init__(self):
        self.meta_keys = None
        raise AttributeError("SpiderTools 不可以直接使用")

    def parse_domain(self, url: str):
        '''
        解析域名
        '''
        return urlparse(url).netloc

    def get_meta(self, meta, *meta_keys):
        '''
        返回meta中的值
        '''
        if meta_keys:
            return [meta.get(key, None) for key in meta_keys]
        else:
            return [meta.get(key, None) for key in self.meta_keys]

class SchoolnewsSpider(scrapy.Spider, SpiderTools):
    name = 'schoolNews'
    allowed_domains = ['chd.edu.cn', 'www.univs.cn', 'mp.weixin.qq.com',
                       'www.gov.cn', 'jyt.shaanxi.gov.cn', 'www.moe.gov.cn', 'www.xa.gov.cn', 'www.qinfeng.gov.cn','www.nhc.gov.cn',
                       'cpc.people.com.cn']
    # allowed_domains = ['chd.edu.cn', 'www.moe.gov.cn',]

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)

        self.meta_keys = ["title", "block_type", "create_time"]

        self.parser_domain_map = {
            'www.chd.edu.cn' : self.parse_chdnews,
            'news.chd.edu.cn' : self.parse_chdnews,

            'www.univs.cn' : self.parse_univs,

            'mp.weixin.qq.com' : self.parse_wechat,

            'www.gov.cn': self.parse_gov,
            'jyt.shaanxi.gov.cn': self.parse_jyt_shanxi,
            'www.xa.gov.cn': self.parse_xa_gov,
            'www.moe.gov.cn': self.parse_moe_gov,
            'www.qinfeng.gov.cn': self.parse_qinfeng_gov,
            'www.nhc.gov.cn': self.parse_nhc_gov,

            'cpc.people.com.cn': self.parse_cpc_people,

            'news.cnhubei.com': self.parse_cnhubei,

            'www.piyao.org.cn': self.parse_piyao,
        }#域名和解析函数的映射字典

    def start_requests(self):
        # 上级精神
        yield scrapy.Request(url="http://www.chd.edu.cn/yqfk/6069/list.htm", meta={"block_type":"上级精神"}, dont_filter=True)
        # 工作动态
        yield scrapy.Request(url="http://www.chd.edu.cn/yqfk/6070/list.htm", meta={"block_type":"工作动态"}, dont_filter=True)
        # 基层动态
        yield scrapy.Request(url="http://www.chd.edu.cn/yqfk/jcdt/list.htm", meta={"block_type":"基层动态"}, dont_filter=True)
        # 通知公告
        yield scrapy.Request(url="http://www.chd.edu.cn/yqfk/6071/list.htm", meta={"block_type":"通知公告"}, dont_filter=True)
        # 防治知识
        yield scrapy.Request(url="http://www.chd.edu.cn/yqfk/6072/list.htm", meta={"block_type":"防治知识"}, dont_filter=True)
        # 拒绝谣言
        yield scrapy.Request(url="http://www.chd.edu.cn/yqfk/6073/list.htm", meta={"block_type":"拒绝谣言"}, dont_filter=True)

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
            raise IgnoreRequest("没有对应的解析函数")

    def parse_test(self,response):
        raise IgnoreRequest("测试")


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
        next_page = response.xpath('//li[@class="page_nav"]//a[@class="next"]/@href')
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
        title, block_type, create_time = self.get_meta(response.meta)

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
        title, block_type, create_time = self.get_meta(response.meta)

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
        title, block_type, create_time = self.get_meta(response.meta)

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
        title, block_type, create_time = self.get_meta(response.meta)

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
        title, block_type, create_time = self.get_meta(response.meta)

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

    def parse_gov(self, response):
        '''
        中国政府网
        解析域名：www.gov.cn
        示例文章：http://www.gov.cn/zhuanti/yqhy/mobile.htm
        '''
        loader = ItemLoader(item=items.GovItem(), response=response)
        title, block_type, create_time = self.get_meta(response.meta)

        loader.add_value("title", title)
        loader.add_value("create_time", create_time)  # 2020-02-19
        loader.add_value("author", "中国政府网")
        loader.add_value("block_type", block_type)
        if "www.gov.cn/xinwen" in response.url:
            content_xpath = "//div[@class='pages_content']"
            img_xpath = "//div[@class='pages_content']//@src"
        else:
            content_xpath = "//div[@class='container']"
            img_xpath = "//div[@class='container']//@src"
        loader.add_xpath("content", content_xpath)
        loader.add_xpath("img", img_xpath)
        loader.add_value("article_url", response.url)

        imgs = loader.get_collected_values("img")
        yield from self.request_imgs(response, imgs)

        yield loader.load_item()

    def parse_xa_gov(self, response):
        '''
        西安市人民政府
        解析域名：www.xa.gov.cn
        示例文章：http://www.xa.gov.cn/xw/gsgg/5e3d08b6f99d65775059122d.html
        '''
        loader = ItemLoader(item=items.XaGovItem(), response=response)
        title, block_type, create_time = self.get_meta(response.meta)

        article_metas = response.xpath("//div[contains(@class, 'm-txt-crm')]/span//text()").extract()

        loader.add_value("title", title)
        loader.add_value("block_type", block_type)
        loader.add_value("article_url", response.url)
        loader.add_value("create_time", article_metas[1], re='发布时间：(.*)')  # '发布时间：2020-02-07 14:44'
        loader.add_value("author",article_metas[0], re='来源：(.*)') # '来源：西安发布'
        loader.add_xpath("content", "//div[@class='m-txt-article']")
        loader.add_xpath("img", "//div[@class='m-txt-article']//@src")

        imgs = loader.get_collected_values("img")
        yield from self.request_imgs(response, imgs)

        yield loader.load_item()

    def parse_moe_gov(self, response):
        '''
        中国人民共和国教育部
        解析域名：www.moe.gov.cn
        示例文章：http://www.moe.gov.cn/jyb_xwfb/gzdt_gzdt/202002/t20200222_423052.html
        '''
        loader = ItemLoader(item=items.MoeGovItem(), response=response)
        title, block_type, create_time = self.get_meta(response.meta)

        article_metas = response.xpath("//div[@id='content_date_source']/text()").extract_first()

        loader.add_value("title", title)
        loader.add_value("block_type", block_type)
        loader.add_value("article_url", response.url)
        loader.add_value("create_time", article_metas, re='\d{4}-\d{2}-\d{2}')  # '2020-02-21'
        loader.add_value("author", article_metas, re='来源：(.*)')  # '来源：新华网'  需要去空格
        loader.add_xpath("content", "//div[@class='TRS_Editor']")
        loader.add_xpath("img", "//div[@class='TRS_Editor']//@src")

        imgs = loader.get_collected_values("img")
        yield from self.request_imgs(response, imgs)

        yield loader.load_item()

    def parse_qinfeng_gov(self, response):
        '''
        秦风
        解析域名：www.qinfeng.gov.cn
        示例文章：http://www.qinfeng.gov.cn/info/2101/120602.htm
        '''
        loader = ItemLoader(item=items.QinfengItem(), response=response)
        title, block_type, create_time = self.get_meta(response.meta)

        article_metas = response.xpath("//div[@class='article_date']/text()").extract_first().split()

        loader.add_value("title", title)
        loader.add_value("block_type", block_type)
        loader.add_value("article_url", response.url)
        loader.add_value("create_time", article_metas[0]+" "+article_metas[1], re='时间：(.*)')  # 时间：2020-02-14 17:02
        loader.add_value("author", article_metas, re='来源：(.*)')  # 来源：秦风网
        loader.add_xpath("content", "//div[@class='v_news_content']")
        loader.add_xpath("img", "//div[@class='v_news_content']//@src")

        imgs = loader.get_collected_values("img")
        yield from self.request_imgs(response, imgs)

        yield loader.load_item()

    def parse_nhc_gov(self, response):
        '''
        中国人民共和国国家卫生健康委员会
        解析域名：www.nhc.gov.cn
        示例文章：http://www.nhc.gov.cn/xcs/pfzs/202002/6090ed34d8e64d038fbed94b9f957059.shtml
        '''
        loader = ItemLoader(item=items.NhcGovItem(), response=response)
        title, block_type, create_time = self.get_meta(response.meta)

        article_metas = response.xpath("//div[class='list']//div[class='source']/span/text()").extract()
        if not article_metas:
            cookjar.extract_cookies(response, response.request) # 提取cookies
            yield scrapy.Request(response.url, callback=self.get_parse(response.url), meta=response.meta, dont_filter=True, cookies=cookjar)
        else:
            loader.add_value("title", title)
            loader.add_value("block_type", block_type)
            loader.add_value("article_url", response.url)
            loader.add_value("create_time", article_metas[0], re='发布时间：([\w\W].*)')  # 发布时间： 2020-02-10
            loader.add_value("author", article_metas[1], re='来源：([\w\W]*)')  # 来源：
            loader.add_xpath("content", "//div[@class='con']")
            loader.add_xpath("img", "//div[@class='con']//@src")

            imgs = loader.get_collected_values("img")
            yield from self.request_imgs(response, imgs)

            yield loader.load_item()

    def parse_cpc_people(self, response):
        '''
        中国共产党新闻网
        解析域名：cpc.people.com.cn
        示例文章：http://cpc.people.com.cn/n1/2020/0203/c164113-31568437.html
        '''
        loader = ItemLoader(item=items.CpcPeopleItem(), response=response)
        title, block_type, create_time = self.get_meta(response.meta)

        article_metas = response.xpath("//div[@class='text_c']/p[@class='sou']//text()").extract()

        loader.add_value("title", title)
        loader.add_value("block_type", block_type)
        loader.add_value("article_url", response.url)
        loader.add_value("create_time", article_metas[0], re=r'\d{4}.*\d{2}')  # '2020年02月25日09:12'
        loader.add_value("author",article_metas[1]) # '人民网-中国共产党新闻网'
        loader.add_xpath("content", "//div[@class='show_text']")
        loader.add_xpath("img", "//div[@class='show_text']//@src")

        imgs = loader.get_collected_values("img")
        yield from self.request_imgs(response, imgs)

        yield loader.load_item()

    def parse_cnhubei(self, response):
        '''
        荆楚网(湖北日报网)
        解析域名：news.cnhubei.com
        示例文章：http://news.cnhubei.com/content/2020-02/23/content_12772797.html?spm=zm1033-001.0.0.2.oMqH8W
        '''
        loader = ItemLoader(item=items.CnHubeiItem(), response=response)
        title, block_type, create_time = self.get_meta(response.meta)

        article_metas = response.xpath("//div[@id='lmy_information01']//text()").extract()
        article_metas = "".join([i.strip() for i in article_metas]) # '发布时间：2020年02月23日17:13来源：中国新闻网'

        loader.add_value("title", title)
        loader.add_value("block_type", block_type)
        loader.add_value("article_url", response.url)
        loader.add_value("create_time", article_metas, re='发布时间：(.*\d{2})')  # 2020年02月23日17:13
        loader.add_value("author", article_metas, re='来源：(.*)')  # 来源：中国新闻网
        loader.add_xpath("content", "//div[@class='article_w']")
        loader.add_xpath("img", "//div[@class='article_w']//@src")

        imgs = loader.get_collected_values("img")
        yield from self.request_imgs(response, imgs)

        yield loader.load_item()

    def parse_piyao(self, response):
        '''
        中国互联网联合辟谣平台
        解析域名：www.piyao.org.cn
        示例文章：http://www.piyao.org.cn/2020-02/24/c_1210487719.htm
        '''
        loader = ItemLoader(item=items.PiYaoItem(), response=response)
        title, block_type, create_time = self.get_meta(response.meta)

        article_metas = response.xpath("//div[@class='con_tit']/p//text()").extract()

        loader.add_value("title", title)
        loader.add_value("block_type", block_type)
        loader.add_value("article_url", response.url)
        loader.add_value("create_time", article_metas[1], re='时间：(.*)')  # 时间：  2020-02-24
        loader.add_value("author", article_metas[0], re='来源：(.*)')  # 来源： 央视新闻客户端
        loader.add_xpath("content", "//div[@class='con_txt']")
        loader.add_xpath("img", "//div[@class='con_txt']//@src")

        imgs = loader.get_collected_values("img")
        yield from self.request_imgs(response, imgs)

        yield loader.load_item()

    def parse_img(self,response):
        '''
        下载、保存图片
        :param responsee:
        :return:
        '''
        image_item = items.ImageItem()

        image_item["content"] = response.body
        image_item["article_url"] = response.meta.get("article_url")
        image_item["image_url"] = response.url

        # 下载图片失败, 可以重试一次
        if not response.body:
            yield Request(response.url, callback=self.parse_img,
                          meta={"type": "image", "article_url": image_item["article_url"]})
        yield image_item

    def request_imgs(self, response, imgs):
        '''
        构造一个图片请求
        :param response:
        :param imgs:
        :return:
        '''
        if imgs:
            for img in imgs:
                if "http" not in img:
                    img = response.urljoin(img)
                yield Request(img, callback=self.parse_img, dont_filter=True,
                              meta={"type": "image", "article_url": response.url})


