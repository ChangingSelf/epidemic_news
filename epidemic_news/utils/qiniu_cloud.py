from configparser import ConfigParser
import os.path
from qiniu import Auth,put_file,etag,BucketManager,put_stream,config,put_data

from settings import QINIU_CONFIG_SECTION
from utils.config import config

class UploadImage():
    '''
    用于上传图片到七牛云
    bucket_name : 对象存储空间名称
    '''
    def __init__(self):
        self.access_key,self.secret_key,self.bucket_name,self.url = config.read_qiniu_conf(QINIU_CONFIG_SECTION)
        self.q = Auth(access_key=self.access_key, secret_key=self.secret_key) # 鉴权对象

    def uplode(self,image_content,filename):
        token = self.q.upload_token(self.bucket_name, filename, 3600)
        ret, info = put_data(token, filename, image_content)
        img_url = os.path.join(self.url,filename)
        return img_url

if __name__ == '__main__':
    import requests
    upload_image = UploadImage()
    response = requests.get("http:xxx")

    upload_image.uplode(response.content,filename="test.png")