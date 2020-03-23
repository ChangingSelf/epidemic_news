# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging
import time
import os.path
import json
import os

from scrapy.exceptions import DropItem

from epidemic_news.settings import REDIS_CONFIG_KEY, CHANNEL_ID, QINIU_CONFIG_SECTION, TEST_MODE
from epidemic_news.items import ImageItem
from epidemic_news.utils.config import config
from epidemic_news.models.news_model import SpiderModel
from epidemic_news.models.news_redis import NewsSet
from epidemic_news.utils.config import config

if TEST_MODE: # 测试模式 不进行实际图片上传
    from epidemic_news.utils.qiniu_cloud import TestUploadImage as UploadImage
else:
    from epidemic_news.utils.qiniu_cloud import UploadImage

logger = logging.getLogger()


class ImagePipeline:
    '''
    对content和img字段中的图片链接进行处理
    对图片内容进行处理
    '''
    def open_spider(self,spider):
        self.upload = UploadImage()
        # 获取七牛云的链接
        *_, self.qiniu_url = config.read_qiniu_conf(QINIU_CONFIG_SECTION)

    def process_item(self, item, spider):
        if isinstance(item, ImageItem):
            # 上传图像
            content = item.get("content")
            article_url = item.get("article_url")
            image_url = item.get("image_url")
            filename = self.image_name(image_url)
            if content:
                self.upload.uplode(image_content=content,filename=filename)
            else:
                logger.error("没有解析到图片,文章地址：{}，图片地址：{}".format(article_url,image_url))

            raise DropItem("image 处理完毕 丢弃")
        else:
            img_urls = item.get("img")
            content = item.get("content")
            # 替换图像链接
            if img_urls:
                # 替换后的链接列表
                replace_urls = [self.image_url(url) for url in img_urls]
                first_img_url = replace_urls[0]
                # 替换content中的链接
                for i in range(len(img_urls)):
                    content = content.replace(img_urls[i], replace_urls[i])
            else:
                first_img_url = ""

            item = dict(item)
            item['content'] = content
            item['image'] = first_img_url

            return item

    def thumbnail(self, content):
        ''' 制作缩略图, 暂时没写, 就用的第一张原图 '''
        pass

    def image_name(self, img_url):
        '''
        七牛云中存储的 图像名称
        :param img_url: 图片链接
        :return: 图片名称
        '''
        name = img_url.split("/")[-1]
        name_suffix = name.split("=")[-1]
        if not name_suffix:
            name_suffix = name.split("=")[-2]
        name = "weappnews/" + name_suffix
        return name

    def image_url(self, img_url):
        '''
        存储在七牛云中图片的完整链接
        :param img_url: 图片链接
        :return: 七牛云中图片完整链接
        '''
        return os.path.join(self.qiniu_url, self.image_name(img_url))


class PrepareItemsPipeline:
    '''
    | id | channel_id | model_id | title | flag | image | keywords | description | tags | weigh | views | comments
    | likes | dislikes | diyname | createtime | updatetime | publishtime | deletetime | status | power
    '''
    def process_item(self, item, spider):
        item = dict(item)
        item.update({
            # # archives表
            # id
            # 'channel_id' : self.channel_id, # 此字段在之后的管道中添加
            'model_id' : 1,
            # 'title'
            'flag' : '',
            # 'image' : item.get('img'), # img字段是所有图片链接, 经过ImagePipeline处理后才有image字段(第一张图片链接,缩略图)
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


class WriteNewsPipeline:
    def open_spider(self,spider):
        # 获取 Spider 在redis中存储文章链接的 键
        self.key = self._redis_key(spider.name)
        # 获取 栏目ID
        self.channel_id = self._chnnel_id(spider.name)
        # 数据库实例化
        self.model = SpiderModel()
        self.set = NewsSet(self.key)

    def process_item(self, item, spider):
        article_url = item.get("article_url")
        if not article_url:
            logger.critical(f"item中不存在文章链接, spdier:{spider.name}")
            raise DropItem("文章链接遗漏")

        item['channel_id'] = self.channel_id
        archives_id = self.model.write_archives(**item)
        if not item.get("content"):
            logger.error(f"article_url:{item.get('article_url')},content为空")
            return None
        if archives_id:
            addonnews_id = self.model.write_addonnews(archives_id, **item)
            if addonnews_id:
                self.model.write_tags(addonnews_id, item.get('tags'))
                self.set.sadd(article_url)
                logger.info(f"数据写入成功, id:{addonnews_id}, article_url:{item.get('article_url')}")
        else:
            logger.info("数据写入失败")

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


class OrderWriteNewsPipeline(WriteNewsPipeline):
    def open_spider(self,spider):
        self.tmp = spider.settings.get('TMP_DIR_PATH')
        if not self.tmp:
            raise ValueError("没有指定临时文件夹")
        super().open_spider(spider)

    def process_item(self, item, spider):
        index = item.get("index")
        print(f"正在写入json , index为{index}")
        filename = f"{self.tmp}{index:0>5d}-{spider.name}.json"
        text = json.dumps(dict(item), ensure_ascii=True)
        with open(filename, "w") as fn:
            fn.write(text)

    def close_spider(self, spider):
        print("执行order中close_spider")
        filenames = [self.tmp + filename for filename in os.listdir(self.tmp) if os.path.splitext(filename)[1]==".json"]
        filenames = sorted(filenames, reverse=True) # 从大到小 排序
        print(filenames)

        for file in filenames:
            print(f"正在将{file}写入数据库")
            with open(file, "r") as fn:
                item = json.load(fn)
                super().process_item(item, spider)
            os.remove(file)
            print(f"文件{file}已删除")