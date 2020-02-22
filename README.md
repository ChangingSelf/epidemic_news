# epidemic_news

爬取[学校网站新闻](http://www.chd.edu.cn/yqfk/)

[幕布链接](https://mubu.com/doc/2MY36Dq0r2u)：项目遇到的一些问题以及解决方案



## 需要爬取的字段

- [ ] 栏目ID：未知
- [x] 文章标题
- [x] 文章url
- [ ] 缩略图：每篇文章中第一张图的url
- [ ] 标签：未知
- [ ] 创建时间：不知道怎么获取
- [ ] 更新时间：不知道怎么获取
- [ ] 发布时间
- [ ] 权限：填写为full



## 使用

命令行移动到项目文件夹中：

```bash
$scrapy crawl schoolNews -o test.json
```

用了这个之后，就会爬取【学校新闻】版块的内容到test.json里面，目前爬取到的字段在上面勾选了

## Spider部分

### 部分名称详细

为了防止部分名称引发歧义导致不必要的误解,下面做些详细的描述

- **主网站:** http://www.chd.edu.cn/yqfk/main.htm
- **(一级)子网站:** 主网站下的六个子网站(分别对应六个板块),也就是爬取文章列表的地方
- **二级子网站:** 也就是具体文章所在的页面(网站)

### 图片

- 图片需要单独进行爬取,定义一个函数`request_imgs(self,response,imgs)`用于构造图片的请求

- 定义一个图片解析函数,`parse_img(self, response)`,进行图片下载/保存

## 写的过程中做的一些记录(hfldqwe)

- 解析函数里面还是有很多代码都是重复了(比如标题,索引,版块名称这些地方),可以进行一波修改(等写完了再改吧)



## 结构设计

### SchoolnewsSpider.py说明

- `start_url`列表里面存放六个一级子网站的url，依次解析这几个子网站

- `SchoolnewsSpider.parser()`解析一级子网站（目录）下的所有文章url，并根据域名生成不同的Request，获取完本页会继续获取下一页
  - 域名映射字典`self.parser_domain_map`里面存放着每个域名对应的解析回调函数，在生成Request时传入
  - 默认解析函数`self.default_parser`是在域名映射字典未找到对应的域名时，使用的解析函数
- 