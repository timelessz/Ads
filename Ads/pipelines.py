# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from Ads.dborm import getsession


class AdsPipeline(object):

    def __init__(self, dbargs):
        self.DBSession = getsession(**dbargs)

        # self.typeManage = MovieTypeManage(dbargs)
        # self.movieManage = MovieManage(dbargs)

    # 从配置文件中读取数据
    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        dbargs = dict(
            host=settings.get('MYSQL_HOST'),
            user=settings.get('MYSQL_USER'),
            password=settings.get('MYSQL_PASSWD'),
            db=settings.get('MYSQL_DBNAME')
        )
        return cls(dbargs)

    # pipeline默认调用
    def process_item(self, item, spider):
        # 正确取到数据
        # 首先取出 封面图片
        # 首先从数据库中取出
        if 'imglist' in item.keys():
            for imgsrc in item['imglist']:
                if 'coversrc' not in item.keys() or item['coversrc'] == '':
                    item['coversrc'] = imgsrc
                    break
        print('______________________________')
        print(item)
        print('______________________________')
        # 首先从数据库中取出
        # 相关定影的信息
        type_ids_string = ',,'
        if 'type' in item.keys():
            movietype_info = re.split('/| ', item['type'])
            type_ids_string = ''
            if movietype_info:
                type_ids_string = self.typeManage.getSetMovieType(movietype_info)
        movieInfo = self.movieManage.searchMovieInfo(item)
        item = self.movieManage.fieldSet(item)
        print('-----------------------------')
        print(movieInfo)
        print('-----------------------------')
        if movieInfo:
            movieId = movieInfo.id
            movieName = movieInfo.name
            # 表示存在该电影 找出不一致的地方然后更新 差找出不一致的字段然后更新
            diffResult = self.movieManage.diffField(movieInfo, item)
            print('==============================')
            print(diffResult)
            print('==============================')
            # 电影更新信息
            self.movieManage.updateMovieInfo(diffResult, movieId, movieName)
        else:
            # 表示不存在电影的情况 更新
            movieInfo = self.movieManage.addMovieInfo(item, type_ids_string)
            print('|||||||||||||||||||||||||||||||||')
            print(movieInfo)
            print('|||||||||||||||||||||||||||||||||')
            movieId = movieInfo['id']
            movieName = movieInfo['name']
            pass
            # 匹配操作下载链接 还有图片集
        if 'download_a' in item.keys():
            print(item['download_a'])
            self.movieManage.addMovieDownload(item['download_a'], movieId, movieName, item['href'],
                                              item['comefrom'])
        if 'imglist' in item.keys():
            self.movieManage.addMovieImgset(item['imglist'], movieId, movieName, item['comefrom'],
                                            item['href'])
        # 修改电影是不是已经爬取了
        self.movieManage.changeMovieHasScrapy(movieName, item['comefrom'])
