from configparser import ConfigParser

from settings import DB_CONFIG_PATH

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
        if self.config.has_section(section):
            host = self.config.get(section, "host")
            port = self.config.getint(section, "port")
            username = self.config.get(section, "username")
            password = self.config.get(section, "password")
            db = self.config.get(section, "db")
            return host, port, username, password, db
        else:
            raise Exception("读取mysql配置出现错误")

    def read_redis_key(self, section, spider_name):
        config = ConfigParser()
        config.read(DB_CONFIG_PATH)
        if config.has_section(section):
            key = config.get(section, spider_name)
            return key
        else:
            raise Exception("redis键 配置出现错误")

config = ReadConfig(config_path=DB_CONFIG_PATH)