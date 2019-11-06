# -*- coding: utf-8 -*-
import scrapy
from scrapy import Selector
from scrapy.linkextractors import LinkExtractor
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy.spiders import CrawlSpider, Rule
from scrapy.utils.project import get_project_settings
from twisted.internet.error import DNSLookupError, TimeoutError

from Ads.dborm import getsession


class Ads(CrawlSpider):
    name = 'ads'
    handle_httpstatus_list = [404, 500]
    # 每一个 spider 设置不一样的 pipelines
    custom_settings = {
        # 'ITEM_PIPELINES': {
        #     '.pipelines.MoviescrapyPipeline': 100,
        # },
        'DOWNLOAD_DELAY': 2
    }

    '''
    全部的公司域名
    '''
    spider_domains = {
        'xtools-crm.com', 'rishin.cn', 'cnmail.biz', 'sky-sip.com', 'whomx.com', 'liaozi.info', 'yixin-im.com',
        'weidali.net', 'rishin.com.cn', '企业邮.cn', '163edm.com', 'qiangbi.cc', 'salesmen.cn', 'lenovobox.com.cn',
        'salesman.cc', 'hi-link.net', 'hi-link.com.cn', '51malatang.cn', 'kangnibaobao.cn', 'jiameng.work',
        'xueqianpeixun.cn', 'youdao.work', 'aichihuoguo.cn', '1fangyun.cn', 'scrm.work', 'youxiaoxianjieban.cn',
        'jujinghuishen.cn', 'sdwjpf.com.cn', 'jikezhanji.com.cn', 'baihi.com', 'zlei.cn', 'it1980.com',
        'jikezhanji.net', 'sdkairen.cn', 'haifo.com.cn', '16tu.net', 'yryf.net', 'hxmail.cn', 'txwd.com', 'vps100.cn',
        'txwd.cn', 'sohux.net', 'xgb.mobi', 'guai.work', 'qiangbi.net.cn', 'linuogroup.com.cn', '163m.biz',
        'xtools-crm.com', 'qiangbi.cc', 'ubuntu365.cn', 'hi-link.net', 'qiangbi.co', 'almail.cn', '126-m.com',
        'soft365.cc', 'yizhixin.net', '企业邮.中国', 'qiangbi.info', 'youdao.work', 'qiyvkf.cn', 'sdwjpf.com.cn',
        'jikezhanji.net', '16tu.net', 'hxmail.cn', 'qiyeshangyun.net', 'xgb.red', 'xgb.mobi', '4006360163.com',
        'sdpiao.com', 'qiyvkf.com', 'qiyeshangyun.com.cn', 'jiaoyuxi.cn', '17shiting.cn', '163hmail.com.cn',
        'qiyeshangyun.com.cn', 'sitegroup.com.cn', 'jiaoyuxi.cn', 'jiaoyuchu.cn', '17shiting.com', '17shiting.cn',
        'xiaoguobang.cn', 'youdao.so', '163hm.com.cn', 'cio.club', 'linuogroup.cn', 'qq-tim.cn', 'hnst163.cn',
        'linuogroup.cn', 'jinseyulin.cc', 'wie.cc', 'sdwjpf.com', 'qq-tim.cn', 'dunhuangwang.cn', 'wpsyxz.cn',
    }
    '''
    黑名单关键词列表
    '''
    black_list = {'万能', '顶级', '无敌', '最新科学', '著名', '最新科技', '仅此一次', '最爱', '最便宜', '销量冠军', '创领品牌', '优秀', '首个', '最后', '至尊',
                  '全网第一', '全球首发', '最低级', '特效', '最受欢迎', '宇宙级', '领导者', '领袖品牌', '全国第一', '王者', '最奢侈', '国家级', '前无古人', '第一',
                  '严禁使用绝对值', '最流行', '领导品牌', '最低价', '纯天然', '最先享受', '首选', '最优秀', '最新', '世界全国', '领袖', '最时尚', '独一无二', '最高',
                  '全国X大品牌之一', '巅峰', '史无前例', '最先进', '极品', '最先进加工工艺', '起赚', '巨星', '全球级', '最大程度', '正品', '一天', '高档', '终极',
                  '唯一', '一流', '极佳', '最高级', '排名第一', '之王', '国家级产品', '时尚最低价', '独家配方', '绝无仅有', '金牌', '最首家', '精确', '最聚拢',
                  'T0P.1', '严禁使用最高', '最符合', '国家（国家免检）', '全国首发', '第一 ', '最新技术', '祖传', '国际品质', '尖端', '全国销量冠军', '世界级',
                  '掌门人', '国家领导人', '销量第一', '名牌', '首款', '第一品牌', '全网首发', '顶级工艺', 'N0.1', '最后一波'}

    def __init__(self, *args, **kwargs):
        super(Ads, self).__init__(*args, **kwargs)

        # settings = get_project_settings()
        # dbargs = dict(
        #     host=settings.get('MYSQL_HOST'),
        #     user=settings.get('MYSQL_USER'),
        #     password=settings.get('MYSQL_PASSWD'),
        #     db=settings.get('MYSQL_DBNAME')
        # )
        # self.DBSession = getsession(**dbargs)

    def start_requests(self):
        '''
        首先获取第一页 然后获取总的数量 用来判断总共多少页面
        '''
        for domain in self.spider_domains:
            url = 'http://' + domain
            request = scrapy.Request(url=url, callback=self.parse_list, errback=self.errback_httpbin)
            request.meta['url'] = url
            # yield request

    def errback_httpbin(self, failure):
        ''' 请求异常操作
        :param failure:
        :return:
        '''
        # log all errback failures,
        # in case you want to do something special for some errors,
        # you may need the failure's type
        self.logger.error(repr(failure))
        # if isinstance(failure.value, HttpError):
        if failure.check(HttpError):
            # you can get the response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        # elif isinstance(failure.value, DNSLookupError):
        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        # elif isinstance(failure.value, TimeoutError):
        elif failure.check(TimeoutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)

    def parse_list(self, response):
        '''
        解析列表
        :param response:
        :return:
        '''
        if response.status in self.handle_httpstatus_list:
            #     网站不能打开 404 500
            pass
        parenturl = response.meta['url']
        sel = Selector(response)
        #  取出全部 a 链接
        atags = sel.xpath('//a')
        for a in atags:
            print(a)
            return
            # item = AutomaticmoviemanageItem()
            # item['comefrom'] = 'btbtdy'
            # title = li.xpath('*[contains(@class,"cts_ms")]/*[contains(@class,"title")]/a')
            # href = title.xpath('@href').extract_first()
            # text = title.xpath('text()').extract_first()
            # item['coversrc'] = li.xpath('*[contains(@class,"liimg")]/a/img/@data-src').extract_first()
            # item['title'] = text.strip()
            # item['name'] = item['title']
            # #  跳过已经爬取的 且 没爬取的
            # if self.skiprepeat and self.get_movie(item['title']) is None:
            #     # 获取详细内容页面 的url 使用相对路径跟绝对路径
            #     item['region_id'] = 0
            #     item['region_name'] = ''
            #     if href:
            #         # 截取movie_id 出来
            #         movie_id = href[8:href.find('.html')]
            #         # 把相对路径转换为绝对路径
            #         href = urllib.parse.urljoin(parenturl, href)
            #         item['href'] = href
            #         print('开始爬取' + item['title'])
            #         request = scrapy.Request(url=href, callback=self.parse_content, priority=20)
            #         request.meta['item'] = item
            #         request.meta['id'] = movie_id
            #         yield request
            # else:
            #     print('**********************************')
            #     print(item['title'] + '电影已经存在，放弃爬取数据')
            #     print('**********************************')

    def subhtml(self, html):
        dr = re.compile(r'<[^>]+>', re.S)
        return dr.sub('', html)

    def parse_content(self, response):
        '''
        解析页面的内容 解析每一个页面的数据
        '''
        item = response.meta['item']
        id = response.meta['id']
        sel = Selector(response)
        # 这个地方要修改 为
        content = sel.xpath(
            '/html/body/*[contains(@class,"topur")]/*[contains(@class,"play")]/*[contains(@class,"vod")]/*[contains(@class,"vod_intro")]')
        ages = content.xpath('h1/span/text()').extract_first()
        item['ages'] = ages[2:len(ages) - 1] if ages else ''
        des = content.xpath('string(.//*[@class="des"])').extract_first()
        item['summary'] = des.replace('剧情介绍：', '').replace(u'\u3000', u'') if des else ''
        field = content.xpath('dl').extract_first()
        # 清除空格 清除 &nbsp;
        field = field.replace(u'\u3000', u'').replace(u'\xa0', u'')
        fieldlist = field.split('</dd>')
        fieldslist = list(map(self.subhtml, fieldlist))
        item['country'] = country = fieldslist[3].replace('地区:', '')
        item['type'] = fieldslist[2].replace('类型:电影', '').replace(' ', '')
        item['language'] = fieldslist[4].replace('语言:', '')
        item['starring'] = fieldslist[6].replace('主演:', '')
        item['content'] = reduce(lambda x, y: x + '<br/>' + y, fieldslist) + '<br/>' + des
        if country == '大陆':
            item['region_id'] = '4'
            item['region_name'] = '大陆电影'
        elif country == '香港' or country == '台湾':
            item['region_id'] = '3'
            item['region_name'] = '港台电影'
        elif country == '日本' or country == '韩国':
            item['region_id'] = '2'
            item['region_name'] = '日韩电影'
        elif country == '欧美':
            item['region_id'] = '1'
            item['region_name'] = '欧美电影'
        elif country == '美国':
            item['region_id'] = '1'
            item['region_name'] = '欧美电影'
        elif country == '泰国':
            item['region_id'] = '8'
            item['region_name'] = '泰国电影'
        elif country == '印度':
            item['region_id'] = '6'
            item['region_name'] = '印度电影'
        # 接下来新发起一个请求 请求下下载链接
        url = self.downloadlink_url % id
        request = scrapy.Request(url=url, callback=self.parse_downloadlink, priority=30)
        request.meta['item'] = item
        yield request

    def parse_downloadlink(self, response):
        item = response.meta['item']
        sel = Selector(response)
        downloadlist = sel.xpath('//div[@class="p_list"]')
        a_download_info = []
        for perdownload in downloadlist:
            lis = perdownload.xpath('ul/li')
            for li in lis:
                text = li.xpath('a/text()').extract_first()
                link = li.xpath('.//a[contains(@href,"magnet:")]/@href').extract_first()
                type_id = 1
                type_name = '磁力下载'
                a_download_info.append(
                    {'href': link, 'pwd': '', 'text': text, 'type_id': type_id, 'type_name': type_name})
        item['download_a'] = a_download_info
        return item
