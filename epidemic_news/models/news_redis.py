import redis
from configparser import ConfigParser

from epidemic_news.settings import DB_CONFIG_PATH,REDIS_CONFIG_SECTION

def redis_conf(section):
    config = ConfigParser()
    config.read(DB_CONFIG_PATH)
    if config.has_section(section):
        host = config.get(section,"host")
        port = config.get(section,"port")
        password = config.get(section,"password")
        db = config.get(section,"db")
        return host,port,password,db
    else:
        raise Exception("读取redis配置出现错误")

class ConnectRedis():
    ''' 连接redis '''
    def __init__(self):
        host,port,password,db = redis_conf(REDIS_CONFIG_SECTION)
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