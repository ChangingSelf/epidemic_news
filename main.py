import json
from urllib.parse import urlparse
'''
测试模块
'''

def readJson(filename):
    '''
    读取输出的json文件
    '''
    with open(filename) as f:
        data = json.load(f)
        #print(data)
        domains = set()
        for k in data:
            domain = k['url']
            domain = parse_domain(domain)
            domains.add(domain)
            print(k)
        
        #print(domains)

def parse_domain(url:str):
    return urlparse(url).netloc




if __name__ == '__main__':
    readJson('test.json')
    