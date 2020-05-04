# -*- coding: utf-8 -*-

# Scrapy settings for epidemic_news project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'epidemic_news'

SPIDER_MODULES = ['epidemic_news.spiders']
NEWSPIDER_MODULE = 'epidemic_news.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'epidemic_news (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
    'epidemic_news.middlewares.EpidemicNewsSpiderMiddleware': 543,
}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'epidemic_news.middlewares.FilterUrlDownloaderMiddleware': 543,
    'epidemic_news.middlewares.EpidemicNewsDownloaderMiddleware': 543,
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html

# 增量爬取
INCREACE_CRAWL = True
# 是否要求顺序写入(用于第一次写入)
ITEM_ORDER = False
ITEM_PIPELINES = {
    'epidemic_news.pipelines.ImagePipeline': 100,
    'epidemic_news.pipelines.PrepareItemsPipeline': 200,
    'epidemic_news.pipelines.OrderWriteNewsPipeline' if ITEM_ORDER else 'epidemic_news.pipelines.WriteNewsPipeline' : 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# 使用test配置进行运行
TEST_MODE = False

# 配置最大线程数量：
REACTOR_THREADPOOL_MAXSIZE = 100

# 配置日志
if TEST_MODE:
    LOG_LEVEL = 'INFO'
else:
    LOG_LEVEL = 'ERROR'
    LOG_FILE = 'log.txt'

# 临时文件夹
TMP_DIR_PATH = '/home/py/spider/epidemic_news/epidemic_news/tmp/'

# 数据库相关配置
DB_CONFIG_PATH = '/home/py/spider/epidemic_news/epidemic_news/config.conf'
if TEST_MODE:
    MYSQL_CONFIG_SECTION = 'mysql_test'
    REDIS_CONFIG_SECTION = 'redis_test'
else:
    MYSQL_CONFIG_SECTION = 'mysql_235'
    REDIS_CONFIG_SECTION = 'redis_local'

QINIU_CONFIG_SECTION = 'qiniu_teacher'
REDIS_CONFIG_KEY = 'redis_key'
REDIS_CONFIG_IMAGE_KEY = 'redis_image_key'
# archives表中 爬取大栏目(spider)对应的 channel_id
CHANNEL_ID = {
    "schoolNews": 56,
}

# 超时 设置为30s
DOWNLOAD_TIMEOUT = 30