# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import TakeFirst
import time

class EpidemicNewsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 文章标题
    title = scrapy.Field(
        output_processor = TakeFirst()#提取第一个非空元素
    )
    # 原文url
    url = scrapy.Field(
        output_processor = TakeFirst()#提取第一个非空元素
    ) 
    # 更新时间（爬取时间）
    update_time = scrapy.Field(
        output_processor = TakeFirst()#提取第一个非空元素
    )
    # 文章发布时间
    public_time = scrapy.Field()
    # 缩略图
    litimg = scrapy.Field() 

