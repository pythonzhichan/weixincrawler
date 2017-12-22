# -*- coding: utf-8 -*-

import logging
import time
import utils
import requests

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


class WeiXinCrawler:
    def crawl(self, offset=0):
        """
        爬取更多文章
        :return:
        """
        url = "https://mp.weixin.qq.com/mp/profile_ext?" \
              "action=getmsg&" \
              "__biz=MjM5MzgyODQxMQ==&" \
              "f=json&" \
              "offset={offset}&" \
              "count=10&" \
              "is_ok=1&" \
              "scene=&" \
              "uin=777&" \
              "key=777&" \
              "pass_ticket=25llsA6zWUPC9KHOvP4oE+QwJ3nS/3CjeWxeKBjDhxCb7V1lQQJa6d0ZrgSmCvWa&" \
              "wxtoken=&" \
              "appmsg_token=936_qKN8I1KSEO%2BWB2YUShHV8kgkIGXgzl-CT8JJpw~~&" \
              "x5=1&" \
              "f=json".format(offset=offset)  # appmsg_token 也是临时的

        headers = """
Host: mp.weixin.qq.com
Accept-Encoding: gzip, deflate
Cookie: devicetype=iOS10.3.3; lang=zh_CN; pass_ticket=25llsA6zWUPC9KHOvP4oE+QwJ3nS/3CjeWxeKBjDhxCb7V1lQQJa6d0ZrgSmCvWa; version=16060022; wap_sid2=CIDUopEDElxMaU1pSnJxNmQtSzhwYnlPRnFVQ25oOVBkVWxZczUteEJ4SS0yZlZYdjZkbmVCSDhyb2x0cldGendRbkZGU1o4QThMLVZRcGNOMUNKQXBjcS1NemlrcWdEQUFBfjD9nfXRBTgMQJRO; wxuin=841525760
Connection: keep-alive
Accept: */*
User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Mobile/14G60 MicroMessenger/6.6.0 NetType/WIFI Language/zh_CN
Referer: https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MjM5MzgyODQxMQ==&scene=124&devicetype=iOS10.3.3&version=16060022&lang=zh_CN&nettype=WIFI&a8scene=3&fontScale=100&pass_ticket=25llsA6zWUPC9KHOvP4oE%2BQwJ3nS%2F3CjeWxeKBjDhxCb7V1lQQJa6d0ZrgSmCvWa&wx_header=1
Accept-Language: zh-cn
X-Requested-With: XMLHttpRequest
"""
        headers = utils.str_to_dict(headers)
        response = requests.get(url, headers=headers, verify=False)
        result = response.json()
        if result.get("ret") == 0:
            msg_list = result.get("general_msg_list")
            logger.info("抓取数据：offset=%s, data=%s" % (offset, msg_list))
            # 递归调用
            has_next = result.get("can_msg_continue")
            if has_next == 1:
                next_offset = result.get("next_offset")
                time.sleep(2)
                self.crawl(next_offset)
        else:
            # 错误消息
            # {"ret":-3,"errmsg":"no session","cookie_count":1}
            logger.error("无法正确获取内容，请重新从Fiddler获取请求参数和请求头")
            exit()


if __name__ == '__main__':
    crawler = WeiXinCrawler()
    crawler.crawl()
