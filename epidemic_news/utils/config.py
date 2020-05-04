from configparser import ConfigParser

from epidemic_news.settings import DB_CONFIG_PATH

class Single():
    ''' 单例模式 '''
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

class ReadConfig(Single):
    ''' 读取配置文件, 且只进行一次读取 '''
    def __init__(self, *args, config_path=None, **kwargs):
        if not hasattr(self, "config"):
            self.init(*args, config_path=config_path, **kwargs)

    def init(self, *args, config_path=None, **kwargs):
        ''' 需要在程序运行过程中更新配置文件时会用到( 目前需求下,不会直接调用此函数 ) '''
        self.config = ConfigParser()
        if config_path:
            self.config.read(config_path)
        else:
            raise TypeError("配置路径参数缺失")

    def read_mysql_conf(self, section):
        ''' 读取mysql配置文件 '''
        if self.config.has_section(section):
            host = self.config.get(section, "host")
            port = self.config.getint(section, "port")
            username = self.config.get(section, "username")
            password = self.config.get(section, "password")
            db = self.config.get(section, "db")
            return host, port, username, password, db
        else:
            raise Exception("读取mysql配置出现错误")

    def read_redis_conf(self, section):
        if self.config.has_section(section):
            host = self.config.get(section, "host")
            port = self.config.get(section, "port")
            password = self.config.get(section, "password")
            db = self.config.get(section, "db")
            return host, port, password, db
        else:
            raise Exception("读取redis配置出现错误")

    def read_redis_key(self, section, spider_name):
        ''' 读取redis存储链接的 键 '''
        if self.config.has_section(section):
            key = self.config.get(section, spider_name)
            return key
        else:
            raise Exception("redis键 配置出现错误")

    def read_qiniu_conf(self,section):
        ''' 读取七牛云相关配置 '''
        if self.config.has_section(section):
            access_key = self.config.get(section, "access_key")
            secret_key = self.config.get(section, "secret_key")
            bucket_name = self.config.get(section, "bucket_name")
            url = self.config.get(section, "url")
            return access_key,secret_key,bucket_name,url
        else:
            raise Exception("七牛云配置出现错误")

config = ReadConfig(config_path=DB_CONFIG_PATH)

if __name__ == '__main__':
    from epidemic_news.settings import REDIS_CONFIG_SECTION, REDIS_CONFIG_KEY
    config.read_redis_conf(REDIS_CONFIG_SECTION)
    print(config.read_redis_key(REDIS_CONFIG_KEY, 'schoolNews'))