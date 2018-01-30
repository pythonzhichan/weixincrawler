import urllib
import urllib.parse
from scrapy.crawler import CrawlerProcess
import scrapy


class WeixinSpider(scrapy.Spider):
    name = "weixin"

    def start_requests(self):
        params = {'action': 'getmsg',
                  '__biz': 'MjM5MzgyODQxMQ==',
                  'f': 'json',
                  'offset': '13',
                  'count': '10',
                  'is_ok': '1',
                  'scene': '124',
                  'uin': '777',
                  'key': '777',
                  'pass_ticket': '%2B8w2Z8mhF4GH%2BNSPyUvZwwQjXrgXNULyll%2Fj9r7UwXOHHv2W%2FijB%2F%2BmBd9%2Bj16qc',
                  # appmsg_token 是临时的
                  'wxtoken': '',
                  'appmsg_token': '941_XYFSVfr6tB9dZxRhgbPir_JGecvDUol-xn6lLg~~',  # appmsg_token 是临时的
                  'x5': '0'}
        params = urllib.parse.urlencode(params)
        urls = ["https://mp.weixin.qq.com/mp/profile_ext" + "?" + params]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        print(response)
        page = response.url.split("/")[-2]
        filename = 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)

if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(WeixinSpider)
    process.start()