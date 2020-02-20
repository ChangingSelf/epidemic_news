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