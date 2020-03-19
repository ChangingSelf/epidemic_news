import pytest
from epidemic_news.models.news_model import SpiderModel
import time

@pytest.fixture
def spider_model():
    instance = SpiderModel()
    return instance

@pytest.fixture
def item():
    return {
        'article_url': "http://article.url",
        # # archives表
        # id
        'channel_id' : 46, # 此字段在之后的管道中添加
        'model_id' : 1,
        'title' : "title",
        'flag' : '',
        'image' : 'http://img.url',
        'keywords' : '',
        'description' : '',
        'tags' : 'yqfk',
        'weigh' : 0,
        'views' : 0,
        'comments' : 0,
        'likes' : 0,
        'dislikes' : 0,
        'diyname' : '',
        'createtime' : '1234567890',
        'publishtime' : int(time.time()),
        'status' : 'normal',
        'power' : 'all',  # 'all'.'student','teacher',

        # addonnews表
        'content' : "content",
        'author' : 'author',
        'style' : 2 ,
    }

class TestSpiderModel():

    def test_write_archives(self, spider_model, item):
        id = spider_model.write_archives(**item)
        print(id)
        assert isinstance(id, int)

    def test_write_addonnews(self, spider_model, item):
        id = spider_model.write_archives(**item)
        id = spider_model.write_addonnews(id, **item)
        assert isinstance(id, int)

    def test_write_tags(self, spider_model, item):
        id = spider_model.write_archives(**item)
        spider_model.write_tags(id, **item)




if __name__ == '__main__':
    pytest.main(["-s"])