import redis
from configparser import ConfigParser

from epidemic_news.settings import REDIS_CONFIG_SECTION
from epidemic_news.utils.config import config

class ConnectRedis():
    ''' 连接redis '''
    def __init__(self):
        host,port,password,db = config.read_redis_conf(REDIS_CONFIG_SECTION)
        self.re = redis.Redis(host=host,port=port,password=password,db=db)

class NewsSet(ConnectRedis):
    def __init__(self, key):
        super().__init__()
        self.key = key

    def sismember(self, url):
        ''' url是否在集合中，如果没有，返回None '''
        exist = self.re.sismember(self.key, url)
        return exist

    def sadd(self, url):
        ''' 添加url '''
        self.re.sadd(self.key, url)