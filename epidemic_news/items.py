# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import time
from scrapy.loader.processors import TakeFirst,Join,MapCompose


from scrapy.loader import ItemLoader

class EpidemicNewsItemLoader(ItemLoader):

    default_output_processor = TakeFirst()

# 在前面写的几个都是比较常用的函数
def urljoin_url(url,loader_context):
    ''' 补全单个连接 '''
    return loader_context['response'].urljoin(url)

def dispose_time(format='%Y-%m-%d'):
    '''
    处理时间,转换成整数时间戳
    :param time_str:  时间字符串
    :param format: 时间格式 e.g '%Y-%m-%d'
    :return: 时间戳
    '''
    def func(time_str):
        tupletime = time.strptime(time_str,format)
        return int(time.mktime(tupletime))
    return func


class ImageItem(scrapy.Item):
    '''
    图片Item
    '''
    content = scrapy.Field()
    article_url = scrapy.Field()
    image_url = scrapy.Field()


class EpidemicNewsItem(scrapy.Item):
    # 文章标题
    title = scrapy.Field(output_processor = TakeFirst())
    # 版块/标签
    block_type = scrapy.Field()
    # 作者/来源
    author = scrapy.Field(input_processor=MapCompose(str.strip))
    # 文章内容
    content = scrapy.Field()
    # 创建时间
    create_time = scrapy.Field(input_processor=MapCompose(str.strip, dispose_time() ) )
    # 文章链接
    article_url = scrapy.Field()
    # 图片
    img = scrapy.Field()

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
    img = scrapy.Field(input_processor=MapCompose(urljoin_url))

class JytShanxiItem(EpidemicNewsItem):
    '''
    陕西省教育厅
    '''
    create_time = scrapy.Field(input_processor=MapCompose(str.strip, dispose_time('%Y-%m-%d %H:%M:%S')) )

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

class GovItem(EpidemicNewsItem):
    '''
    中国政府网
    '''
    pass

class XaGovItem(EpidemicNewsItem):
    '''
    西安市人民政府网
    '''
    create_time = scrapy.Field(input_processor=MapCompose(str.strip, dispose_time('%Y-%m-%d %H:%M')))

class MoeGovItem(EpidemicNewsItem):
    '''
    中华人民共和国教育部
    '''
    pass

class QinfengItem(EpidemicNewsItem):
    '''
    秦风
    '''
    create_time = scrapy.Field(input_processor=MapCompose(str.strip, dispose_time('%Y-%m-%d %H:%M')))

class NhcGovItem(EpidemicNewsItem):
    '''
    中国人民共和国国家卫生健康委员会
    '''
    pass

class CpcPeopleItem(EpidemicNewsItem):
    '''
    中国共产党新闻网
    '''
    create_time = scrapy.Field(input_processor=MapCompose(str.strip, dispose_time('%Y年%m月%d日%H:%M')))

class CnHubeiItem(EpidemicNewsItem):
    '''
    荆楚网(湖北日报网)
    '''
    create_time = scrapy.Field(input_processor=MapCompose(str.strip, dispose_time('%Y年%m月%d日%H:%M')))

class PiYaoItem(EpidemicNewsItem):
    '''
    中国互联网联合辟谣平台
    '''
    pass



