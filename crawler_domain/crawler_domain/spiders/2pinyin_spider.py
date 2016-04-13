__author__ = 'laborc'

import os
import scrapy
from scrapy import log
from crawler_domain.items import DomainItem
import json


class PinyinSpider(scrapy.Spider):
    name = "2pinyin"
    allowed_domains = ["panda.www.net.cn"]
    custom_settings = {
        'ITEM_PIPELINES': {'crawler_domain.pipelines.PinyinDomainPipeline': 300}
    }

    def __init__(self, *a, **kw):
        super(PinyinSpider, self).__init__(*a, **kw)
        dat_file = open("2_words_pinyin.txt", 'rb')
        self.lines = dat_file.readlines()
        self.pinyinLength = len(self.lines)
        self.domainDic = {}
        dat_file.close()
        self.startNum = 0

    def start_requests(self):
        lastLine = self.get_last_line("out-2pinyin.txt")
        if lastLine:
            lastLine = lastLine.decode("utf-8").rstrip('\n')
            domainJson = json.loads(lastLine)
            self.startNum = int(domainJson["num"]) + 1
        yield scrapy.Request(self.getUrl(), callback=self.parse)

    def parse(self, response):
        resp = response.body.decode("utf-8")
        resp = resp.replace('("', "").replace('")', "")
        self.log(resp)
        for str in resp.split("#"):
            domainArray = str.split("|")
            item = DomainItem()
            item['key'] = domainArray[1]
            item['num'] = self.domainDic[domainArray[1].lower()]
            item['returncode'] = domainArray[2]
            item['original'] = domainArray[3]
            yield item
        if self.startNum <= self.pinyinLength:
            yield scrapy.Request(self.getUrl(), callback=self.parse)

    def getUrl(self):
        area_domain = ""
        for i in range(self.startNum, self.startNum + 50):
            domain = self.lines[self.startNum].decode("utf-8").rstrip('\n').rstrip('\r')+".com"
            self.domainDic[domain] = self.startNum
            area_domain += domain + ","
            self.startNum += 1
        return 'http://panda.www.net.cn/cgi-bin/check.cgi?area_domain=%s' % area_domain

    def get_last_line(self, inputfile):
        filesize = os.path.getsize(inputfile)
        blocksize = 1024
        dat_file = open(inputfile, 'rb')
        last_line = ""
        if filesize > blocksize:
            maxseekpoint = (filesize // blocksize)
            dat_file.seek((maxseekpoint - 1) * blocksize)
        elif filesize:
            dat_file.seek(0, 0)
        lines = dat_file.readlines()
        if lines:
            last_line = lines[-1].strip()
        dat_file.close()
        return last_line
