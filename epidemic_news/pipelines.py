# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging
import time
from configparser import ConfigParser

from scrapy.exceptions import DropItem

from settings import REDIS_CONFIG_KEY, CHANNEL_ID
from utils.config import config
from models.news_model import SpiderModel
from models.news_redis import NewsSet
from epidemic_news.spiders.schoolNews import SchoolnewsSpider

class PrepareItemsPipeline(object):
    '''
    | id | channel_id | model_id | title | flag | image | keywords | description | tags | weigh | views | comments
    | likes | dislikes | diyname | createtime | updatetime | publishtime | deletetime | status | power
    '''
    def process_item(self, item, spider):
        item.update({
            # # archives表
            # id
            # 'channel_id' : self.channel_id, # 此字段在之后的管道中添加
            'model_id' : 1,
            # 'title'
            'flag' : '',
            'image' : item.get('img'),
            'keywords' : '',
            'description' : '',
            'tags' : item.get('block_type'),
            'weigh' : 0,
            'views' : 0,
            'comments' : 0,
            'likes' : 0,
            'dislikes' : 0,
            'diyname' : '',
            'createtime' : item.get('create_time'),
            'publishtime' : int(time.time()),
            'status' : 'normal',
            'power' : item.get('power', 'all'),  # 'all'.'student','teacher',

            # addonnews表
            # 'content'
            'author' : item.get("author",""),
            'style' : 2 if item.get('img') else 0,
        })
        return self.prepare(item)

    def prepare(self, item):
        ''' 对某些字段进行修改, 之后的扩展可以直接添加prepare_func 函数进行修改字段 '''
        for key, value in item.items():
            # 获取修改函数
            prepare_func = "prepare_"+key
            if hasattr(self, prepare_func):
                prepare_func = getattr(self, prepare_func)
                item[key] = prepare_func(value)

        return item


class WriteNewsPipeline(object):
    def open_spider(self,spider):
        self.logger = logging.getLogger()
        # 获取 Spider 在redis中存储文章链接的 键
        self.key = self._redis_key(spider.name)
        # 获取 栏目ID
        self.channel_id = self._chnnel_id(spider.name)
        # 数据库实例化
        self.model = SpiderModel()
        self.set = NewsSet()

    def process_item(self, item, spider):
        article_url = item.get("article_url")
        if not article_url:
            self.logger.critical(f"item中不存在文章链接, spdier:{spider.name}")
            raise DropItem("文章链接遗漏")

        item['channel_id'] = self.channel_id
        archives_id = self.model.write_archives(**item)
        if archives_id:
            addonnews_id = self.model.write_addonnews(archives_id, **item)
            if addonnews_id:
                self.model.write_tags(addonnews_id, item.get('tags'))
                self.set.sadd(article_url)
                self.logger.info(f"数据写入成功, id:{addonnews_id}, article_url:{item.get('article_url')}")
        else:
            self.logger.info("数据写入失败")
        return item

    def _redis_key(self, name):
        '''
        返回Redis中 存储文章链接的集合 的 键key
        '''
        return config.read_redis_key(REDIS_CONFIG_KEY, name)

    def _chnnel_id(self, name):
        ''' 返回对应的channel_id '''
        channel_id = CHANNEL_ID.get(name)
        if channel_id:
            return channel_id
        else:
            raise KeyError("没有为Spider配置channel_id, 请查看settings.py")
