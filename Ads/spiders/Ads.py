# -*- coding: utf-8 -*-
import re
import time
import urllib

import scrapy
from scrapy import Selector
from scrapy.linkextractors import LinkExtractor
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy.spiders import CrawlSpider, Rule
from scrapy.utils.project import get_project_settings
from twisted.internet.error import DNSLookupError, TimeoutError

from Ads.dborm import getsession
from Ads.redisorm import get_redis
from models import AdsDomain, AdsSensitive


class Ads(CrawlSpider):
    name = 'ads'
    handle_httpstatus_list = [404, 500]
    # 每一个 spider 设置不一样的 pipelines
    custom_settings = {
        'ITEM_PIPELINES': {
            'Ads.pipelines.AdsPipeline': 100,
        },
        'DOWNLOAD_DELAY': 2
    }

    '''
    全部的公司域名
    '''
    allowed_domains = [
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
    ]

    '''
    黑名单关键词列表
    '''
    black_ads_list = ['万能', '顶级', '无敌', '最新科学', '著名', '最新科技', '仅此一次', '最爱', '最便宜', '销量冠军', '创领品牌', '优秀', '首个', '最后',
                      '至尊', '全网第一', '全球首发', '最低级', '特效', '最受欢迎', '宇宙级', '领导者', '领袖品牌', '全国第一', '王者', '最奢侈', '国家级',
                      '前无古人', '第一', '绝对值', '最流行', '领导品牌', '最低价', '纯天然', '最先享受', '首选', '最优秀', '最新', '世界全国', '领袖',
                      '最时尚', '独一无二', '最高', '全国X大品牌之一', '巅峰', '史无前例', '最先进', '极品', '最先进加工工艺', '起赚', '巨星', '全球级', '最大程度',
                      '正品', '高档', '终极', '唯一', '一流', '极佳', '最高级', '排名第一', '之王', '国家级产品', '时尚最低价', '独家配方', '绝无仅有',
                      '金牌', '最首家', '精确', '最聚拢', 'T0P.1', '最高', '最符合', '国家（国家免检）', '全国首发', '第一 ', '最新技术', '祖传',
                      '国际品质', '尖端', '全国销量冠军', '世界级', '掌门人', '国家领导人', '销量第一', '名牌', '首款', '第一品牌', '全网首发', '顶级工艺', 'N0.1',
                      '最后一波']

    black_list = ['棋牌', '赌', '娱乐', '博彩', '色情', '担保', '转让', '域名', '成人', '性', '葡京', '彩票', 'av', '黄色', '游戏', '激情网',
                  '开奖', '配资', '股票', '撸', '射', '真人', '裸聊室', '三级', '体育', 'F1', '车队', '彩', 'pk', 'PK', '开户', '竞技', '投注',
                  '赛车', '大发', '比分', '皇冠', '澳门', '大奖', '贵宾', '啪啪啪', '充值', '啪', 'AG', '太阳城']

    def __init__(self, *args, **kwargs):
        super(Ads, self).__init__(*args, **kwargs)
        settings = get_project_settings()
        dbargs = dict(
            host=settings.get('MYSQL_HOST'),
            user=settings.get('MYSQL_USER'),
            password=settings.get('MYSQL_PASSWD'),
            db=settings.get('MYSQL_DBNAME')
        )
        self.DBSession = getsession(**dbargs)

    def start_requests(self):
        '''
        首先获取第一页 然后获取总的数量 用来判断总共多少页面
        '''
        redis_cli = get_redis()
        redis_cli.delete('has_scrapy_href')
        for domain in self.allowed_domains:
            url = 'http://' + domain
            yield self.add_scrapy(url, domain, 0)

    def add_scrapy(self, href, domain, priority):
        #  判断如果已经爬的数据 不再取数据
        if href.find('feedback') == -1:
            redis_cli = get_redis()
            if not redis_cli.sismember('has_scrapy_href', href):
                redis_cli.sadd('has_scrapy_href', href)
                request = scrapy.Request(url=href, callback=self.parse, errback=self.errback_httpbin, priority=priority)
                request.meta['url'] = href
                request.meta['domain'] = domain
                return request

    def errback_httpbin(self, failure):
        ''' 请求异常操作
        :param failure:
        :return:
        '''
        # log all errback failures,
        # in case you want to do something special for some errors,
        # you may need the failure's type
        # self.logger.error(repr(failure))
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


    def parse(self, response):
        '''
        解析列表
        :param response:
        :return:
        '''
        parenturl = response.meta['url']
        domain = response.meta['domain']
        self.add_attack(response.status, domain)
        # if response.status in self.handle_httpstatus_list:
        # 网站不能打开 404 500
        # 添加 攻击记录
        sel = Selector(response)
        #  取出全部 a 链接
        atags = sel.xpath('//a')
        #  html
        html = response.text
        text = self.subhtml(html)
        # self.logger.info(text)
        list = self.check_ads(html, response.url, domain)
        # attacklist = self.check_attack(html, response.url, domain)

        # 添加广告记录
        self.add_ads_sensitive(list)
        # self.add_ads_sensitive(attacklist)
        for a in atags:
            # 把相对路径转换为绝对路径
            href = a.xpath('@href').extract_first()
            #  判断是带 http
            if href.find('javascript') >= 0 or href.find('#') >= 0:
                pass
            elif href.find("http") >= 0 and len(href) != 0:
                # 包含 http
                yield self.add_scrapy(href, domain, 20)
            else:
                href = urllib.parse.urljoin(parenturl, href)
                yield self.add_scrapy(href, domain, 20)

    def check_ads(self, html, url, domain):
        '''
        :param url:
        :param domain:
        :param html:
        :return:
        '''
        list = []
        for word in self.black_ads_list:
            if word in html:
                list.append({'word': word, 'url': url, 'domain': domain, 'type': 'ADS'})
        return list

    def check_attack(self, html, url, domain):
        '''
        :param html:
        :param url:
        :param domain:
        :return:
        '''
        list = []
        for word in self.black_list:
            if word in html:
                list.append({'word': word, 'url': url, 'domain': domain, 'type': 'ATTACK'})
        return list

    def subhtml(self, html):
        dr = re.compile(r'<[^>]+>', re.S)
        return dr.sub('', html)

    def add_ads_sensitive(self, list):
        '''
        添加  违规广告列表记录
        :param list:
        :return:
        '''
        listarr = []
        currenttime = int(time.time())
        for plist in list:
            listarr.append(
                AdsSensitive(
                    domain=plist['domain'],
                    href=plist['url'],
                    word=plist['word'],
                    opstatus=False,
                    type=plist['type'],
                    created_at=currenttime,
                    updated_at=currenttime,
                ))
        self.DBSession.add_all(listarr)
        self.DBSession.flush()
        self.DBSession.commit()
        return True

    def add_attack(self, code, domain):
        '''
        :param code:
        :param domain:
        :return:
        '''
        # 查看下当前域名是不是存在
        if self.DBSession.query(AdsDomain).filter_by(domain=domain, httpcode=code).first() is None:
            currenttime = int(time.time())
            domainlist = AdsDomain(
                domain=domain,
                httpcode=code,
                detail='',
                created_at=currenttime,
                updated_at=currenttime,
            )
            self.DBSession.add(domainlist)
            self.DBSession.commit()
        return True
