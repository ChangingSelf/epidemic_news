# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import time
from scrapy.loader.processors import TakeFirst,Join,MapCompose


from scrapy.loader import ItemLoader

# 需要继承内置的ItemLoader类
class EpidemicNewsItemLoader(ItemLoader):
    # 自定义itemloader，默认的输出处理器为取第一个非空元素
    default_output_processor = TakeFirst()

# 在前面写的几个都是比较常用的函数
def urljoin_url(url,loader_context):
    ''' 补全单个连接 '''
    return loader_context['response'].urljoin(url)

def dispose_time(time_str):
    '''
    处理时间,转换成整数时间戳
    :param time_str:  时间字符串,e.g '发布时间：%Y-%m-%d'
    :return: 时间戳
    '''
    tupletime = time.strptime(time_str,'发布时间：%Y-%m-%d')
    return int(time.mktime(tupletime))

class EpidemicNewsItem(scrapy.Item):
    # 如果要使用itemLoader，使用上方定义的EpidemicNewsItemLoader，output_processor默认使用TakeFirst()
    # 文章标题
    title = scrapy.Field()
    # 原文url
    url = scrapy.Field() 
    # 缩略图
    litimg = scrapy.Field()
    # 版块/标签
    block_type = scrapy.Field()
    # 作者/来源
    author = scrapy.Field()
    # 文章内容
    content = scrapy.Field()
    # 创建时间
    create_time = scrapy.Field()
    # 文章链接
    article_url = scrapy.Field()
    # 图片链接(不需要进行保存,只是中间处理会用到)
    img_url = scrapy.Field()
    # 权限
    power = scrapy.Field()

class ChdItem(EpidemicNewsItem):
    '''
    长安大学疫情防控专题网
    '''
    pass

class ChdNewsItem(EpidemicNewsItem):
    '''
    学校新闻网 items
    '''
    content = scrapy.Field(output_processor=TakeFirst())
    detail_time = scrapy.Field(input_processor=MapCompose(str.strip, dispose_time), output_processor=TakeFirst())
    img = scrapy.Field(input_processor=MapCompose(urljoin_url))

class JytShanxiItem(EpidemicNewsItem):
    '''
    陕西省教育厅
    '''
    pass

class UnivsItem(EpidemicNewsItem):
    '''
    中国大学生在线
    '''
    pass

class WeChatItem(EpidemicNewsItem):
    '''
    微信公众号文章
    '''
    pass