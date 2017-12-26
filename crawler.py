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
              "appmsg_token=936_wKfzZy72dKC2AMF%2FBweDXYMT-6YGIB4livZjPQ~~&" \
              "x5=1&" \
              "f=json".format(offset=offset)  # appmsg_token 是临时的

        headers = """
Host: mp.weixin.qq.com
Connection: keep-alive
X-Requested-With: XMLHttpRequest
User-Agent: Mozilla/5.0 (Linux; Android 7.0; M1 E Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.49 Mobile MQQBrowser/6.2 TBS/043632 Safari/537.36 MicroMessenger/6.6.1200(0x26060030) NetType/WIFI Language/zh_CN
Accept: */*
Referer: https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MjM5MzgyODQxMQ==&scene=124&devicetype=android-24&version=26060030&lang=zh_CN&nettype=WIFI&a8scene=3&pass_ticket=RzRbFPFuRYaUzzjkFyyXjZwkKLxPvHOMXsEbCB2klbc%2FC2%2BnvUgnLCdmwE7Q1gry&wx_header=1
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,en-US;q=0.8
Cookie: wxtokenkey=082334c921f8ddc8d9fe63cc369baef1594bd1b23edf0b72b09ef5503fc8bf3e; rewardsn=5825ac5a141e94def5ce; wxuin=525477518; devicetype=android-24; version=26060030; lang=zh_CN; pass_ticket=RzRbFPFuRYaUzzjkFyyXjZwkKLxPvHOMXsEbCB2klbc/C2+nvUgnLCdmwE7Q1gry; wap_sid2=CI7NyPoBEogBWV80N1N0MnlUcE4taVZhUFJsbFhtcllTUHNYYmhrUUV0dzk3MUE0dDA4eDZDazNzbHFUaUN4d24yWEFOQkpJUHJmSmpYS3V3ZW9XdDh3QlRCbU9Ea3Y0T21sRVA1RW5iZUgtUVhtaFU1MDZ2WE9WNGI3dnVpWHZEbkJhaVZyNTFxQU1BQUF+fjCUiIrSBTgMQJRO
Q-UA2: QV=3&PL=ADR&PR=WX&PP=com.tencent.mm&PPVN=6.6.0&TBSVC=43602&CO=BK&COVC=043632&PB=GE&VE=GA&DE=PHONE&CHID=0&LCID=9422&MO= M1E &RL=1080*1920&OS=7.0&API=24
Q-GUID: 0fd685fa8c515a30dd9f7caf13b788cb
Q-Auth: 31045b957cf33acf31e40be2f3e71c5217597676a9729f1b
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
