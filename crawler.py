from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from epidemic_news.spiders.schoolNews import SchoolnewsSpider


if __name__ == '__main__':
    settings = get_project_settings()
    # print(os.path.realpath(__file__))
    process = CrawlerProcess(settings)

    process.crawl(SchoolnewsSpider)

    process.start()