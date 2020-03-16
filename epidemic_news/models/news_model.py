'''
三个数据表对应三个类 ArchivesModel, AddonnewsModel, TagsModel

整体操作数据表的逻辑在 SpiderModel类中( 三个数据库的操作, 以及过程中的日志 )
'''
import pymysql
import logging
from configparser import ConfigParser

from epidemic_news.settings import DB_CONFIG_PATH,MYSQL_CONFIG_SECTION
from utils.config import config

class Model():
    def __init__(self, *args, **kwargs):
        host, port, username, password, db = config.read_mysql_conf(MYSQL_CONFIG_SECTION)
        self.con = pymysql.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            db=db,
        )
        self.cursor = self.con.cursor()
        self.logger = logging.getLogger()

class ArchivesModel(Model):

    def inquire_archives(self, channel_id, title, tags, createtime):
        '''
        判断archives数据表中是否已经有这篇文章 并 返回id和power
        :param channel_id: 模型id
        :param title: 文章标题
        :param block_type: 标签
        :return: 存在返回(id, power) 否则为None
        '''
        sqlagr = "SELECT id,power FROM fa_cms_archives WHERE channel_id='{}' AND title='{}' AND tags='{}' AND createtime='{}';".format(channel_id, title, tags, createtime)
        rows = self.cursor.execute(sqlagr)
        if rows >= 1:
            return self.cursor.fetchone()

    def insert_archives(self,article_url,channel_id,model_id,title,flag,image,keywords,description,tags,weigh,views,comments,likes,dislikes,diyname,createtime,publishtime,status,power,*args,**kwargs):
        ''' 插入数据库 '''
        if len(title)>=200:
            title = title[0:200]
        title = pymysql.escape_string(title)
        image = pymysql.escape_string(image)
        # attachfile = pymysql.escape_string(attachfile)
        sqlagr = '''INSERT INTO fa_cms_archives set `channel_id`="{}",`model_id`="{}",`title`="{}",`flag`="{}",`image`="{}",`keywords`="{}",`description`="{}",`tags`="{}",`weigh`="{}",`views`="{}",`comments`="{}",`likes`="{}",`dislikes`="{}",`diyname`="{}",`createtime`="{}",`publishtime`="{}",`status`="{}",`power`="{}";'''.format(
            channel_id, model_id, title, flag, image, keywords, description, tags, weigh, views, comments, likes,dislikes, diyname, createtime, publishtime, status, power)
        rows = self.cursor.execute(sqlagr)
        self.con.commit()
        if rows>=1:
            return True

    def update_power(self,id,old_power,power):
        ''' 更新可阅读权限 '''
        if old_power == "all":
            return
        elif old_power == power:
            return
        else:
            sqlagr = "update fa_cms_archives set power='all' where id={};".format(id)
            self.cursor.execute(sqlagr)
            self.con.commit()

class AddonnewsModel(Model):

    def inquire_addonnews(self, id):
        '''
        判断addonnews内容表中是否存在内容
        :param id: archives表中数据对应的id
        :return:  存在返回True 否则为None
        '''
        sqlagr = "SELECT id FROM fa_cms_addonnews WHERE id={};".format(id)
        rows = self.cursor.execute(sqlagr)
        if rows >= 1:
            return True

    def insert_addonnews(self,id,content,author,style,*args,**kwargs):
        ''' 插入fa_cms_addonnews表 '''
        content = pymysql.escape_string(content)
        author = pymysql.escape_string(author)

        sqlagr = 'insert into fa_cms_addonnews(id,content,author,style) values ("{}","{}","{}","{}");'.format(
            id,content,author,style)
        row = self.cursor.execute(sqlagr)
        self.con.commit()
        if row>=1:
            return True

class TagsModel(Model):

    def inquire_tag(self,tag,*args,**kwargs):
        ''' 查询tag，存在就返回对应的id, archives, nums数据 '''
        sqlagr = "select id,archives,nums from fa_cms_tags where `name`='{}';".format(tag)
        row = self.cursor.execute(sqlagr)
        if row >=1:
            return self.cursor.fetchone()

    def create_tag(self, tag):
        ''' 创建tag '''
        sqlagr = "insert into fa_cms_tags set `name`='{}',archives='{}',nums={};".format(tag, "", "0")
        row = self.cursor.execute(sqlagr)
        self.con.commit()
        if row >= 1:
            return True

    def insert_tag(self,tag_id, archives, nums, *args,**kwargs):
        ''' 插入或者更新tags表中archives字段 '''
        sqlagr = "update fa_cms_tags set archives='{}',nums={} where id={};".format(archives, nums, tag_id)
        row = self.cursor.execute(sqlagr)
        self.con.commit()


class SpiderModel(ArchivesModel, AddonnewsModel, TagsModel):

    def write_archives(self,article_url,channel_id,model_id,title,flag,image,keywords,description,tags,weigh,views,comments,likes,dislikes,diyname,createtime,publishtime,status,power,*args,**kwargs):
        ''''
        fa_cms_archives表
        :return: 数据写入成功(包括数据已存在)返回archives中对应的id, 失败返回None
        '''
        result = self.inquire_archives(channel_id, title, tags, createtime)
        if result:
            id, old_power = result
            if old_power == power:
                self.logger.error(f"archives表写入数据重复, id:{id}, article_url:{article_url}")
            else:
                self.update_power(id, old_power, power)
                self.logger.info(f"archives表power字段更新, id:{id}, article_url:{article_url}")
        # 数据没有重复
        else:
            result = self.insert_archives(article_url,channel_id,model_id,title,flag,image,keywords,description,tags,weigh,views,comments,likes,dislikes,diyname,createtime,publishtime,status,power,*args,**kwargs)
            if result:
                self.logger.info(f"archives表数据写入成功, id:{id}, article_url:{article_url}")
                id, power = self.inquire_archives(channel_id, title, tags, createtime)
            else:
                self.logger.error(f"archives表数据写入失败, article_url:{article_url}")
                return None

        return id

    def write_addonnews(self,id,article_url,content,author,style,*args,**kwargs):
        '''
        addonnews表
        :return: 写入成功返回id, 失败(包括数据已存在)为None
        '''
        result = self.inquire_addonnews(id)
        if result:
            self.logger.error(f"addonnews表数据已存在, id:{id}, article_url:{article_url}")
            return None
        else:
            result = self.insert_addonnews(id,content,author,style,*args,**kwargs)
            if result:
                return id
            else:
                self.logger.critical(f"addonnews表数据写入失败, id:{id}, article_url:{article_url}")
                return None

    def write_tags(self, id, tags, *args,**kwargs):
        tag_list = tags.split(",")
        for tag in tag_list:
            result = self.inquire_tag(tag)
            if result:
                tag_id, archives, nums = result
            else:
                self.create_tag(tag)
                tag_id, archives, nums = self.inquire_tag(tag)
            nums = int(nums) + 1
            archives = archives + "," + id if archives else str(id)
            self.insert_tag(tag_id, archives, nums, *args, **kwargs)
            self.logger.info(f"tags表数据插入成功")


