# -*- coding: utf-8 -*-

import html
import json
import logging
import time
from datetime import datetime

import requests

import utils
from models import Post

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
            self.save(msg_list)
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

    @staticmethod
    def save(msg_list):
        # TODO 处理多图文 multi_app_msg_item_list

        msg_list = html.unescape(msg_list).replace("\/", "/")
        data = json.loads(msg_list)
        posts = data.get("list")
        for item in posts:
            msg_info = item.get("app_msg_ext_info")  # 非图文消息没有此字段
            if msg_info:
                keys = ('title', 'author', 'content_url', 'digest', 'cover', 'source_url')
                sub_data = utils.sub_dict(item.get("app_msg_ext_info"), keys)
                post = Post(**sub_data)

                p_date = item.get("comm_msg_info").get("datetime")

                p_date = datetime.fromtimestamp(p_date)
                post["p_date"] = p_date
                logger.info('save data %s ' % post.title)
                try:
                    post.save()
                except Exception as e:
                    logger.error("保存失败 data=%s" % post.to_json(), exc_info=True)
            else:
                logger.warning(u"此消息不是图文推送，data=%s" % json.dumps(item.get("comm_msg_info")))

    def update(self, post):

        url = "https://mp.weixin.qq.com/mp/getappmsgext"
        params = { 'appmsg_type': '9',
                  'title': 'Python%E8%AF%AD%E8%A8%80%E7%9A%842017%E5%B9%B4%E7%BB%88%E6%80%BB%E7%BB%93',
                  'ct': '1514161452',
                  'abtest_cookie': 'AwABAAoADAANAAgAJIgeALuIHgDZiB4A4YgeAPyIHgD6iR4AGYoeAE2KHgAAAA==',
                  'devicetype': 'android-24', 'version': '', 'f': 'json', 'r': '0.20108094088792017', 'is_need_ad': '1',
                  'comment_id': '3571913022', 'is_need_reward': '1', 'both_ad': '0', 'reward_uin_count': '24',
                  'msg_daily_idx': '1', 'is_original': '0', 'uin': '777', 'key': '777',
                  'pass_ticket': 'RzRbFPFuRYaUzzjkFyyXjZwkKLxPvHOMXsEbCB2klbc%25252FC2%25252BnvUgnLCdmwE7Q1gry',
                  'wxtoken': '648184136', 'clientversion': '26060030',
                  'appmsg_token': '936_kIs%252FCFfFqF88lhIr1nm-8z8hozrvPvR5cLWQLfIR3gDSVDSjqjVPyjhkfq9mv-XMErWYoqV3TydDLEfx',
                  'x5': '1'}

        from urllib.parse import urlsplit
        print(utils.str_to_dict(urlsplit(html.unescape(post.content_url)).query, "&", "="))

        params.update(utils.str_to_dict(urlsplit(html.unescape(post.content_url)).query, "&", "="))
        body = "is_only_read=1&req_id=27023kwPl9AhxVXl0MLl0JfB&pass_ticket=RzRbFPFuRYaUzzjkFyyXjZwkKLxPvHOMXsEbCB2klbc%25252FC2%25252BnvUgnLCdmwE7Q1gry&is_temp_url=0"
        data = utils.str_to_dict(body, "&", "=")

        headers = """
        
        Host: mp.weixin.qq.com
Connection: keep-alive
Content-Length: 149
Origin: https://mp.weixin.qq.com
X-Requested-With: XMLHttpRequest
User-Agent: Mozilla/5.0 (Linux; Android 7.0; M1 E Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.49 Mobile MQQBrowser/6.2 TBS/043632 Safari/537.36 MicroMessenger/6.6.1200(0x26060030) NetType/WIFI Language/zh_CN
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
Accept: */*
Referer: https://mp.weixin.qq.com/s?__biz=MjM5MzgyODQxMQ==&mid=2650367689&idx=1&sn=fa6fc5c58456cbd4e60001582ae28a78&chksm=be9cdd9d89eb548bc2eeb14108131dce3c8572b66a26a9684e35af4ba4e2c152ab1733af6fbd&scene=38&ascene=0&devicetype=android-24&version=26060030&nettype=WIFI&abtest_cookie=AwABAAoADAANAAgAJIgeALuIHgDZiB4A4YgeAPyIHgD6iR4AGYoeAE2KHgAAAA%3D%3D&lang=zh_CN&pass_ticket=RzRbFPFuRYaUzzjkFyyXjZwkKLxPvHOMXsEbCB2klbc%2FC2%2BnvUgnLCdmwE7Q1gry&wx_header=1
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,en-US;q=0.8
Cookie: rewardsn=5825ac5a141e94def5ce; wxuin=525477518; devicetype=android-24; version=26060030; lang=zh_CN; pass_ticket=RzRbFPFuRYaUzzjkFyyXjZwkKLxPvHOMXsEbCB2klbc/C2+nvUgnLCdmwE7Q1gry; wap_sid2=CI7NyPoBEogBWV80N1N0MnlUcE4taVZhUFJsbFhtcllTUHNYYmhrUUV0dzk3MUE0dDA4eERoTEk0TklubzhyNlRuNjJ4UGJUZVg0SkxPOGhxaWdHeFp0R3VPM3NsWDBIOUJrckZLWGNLUUJSLWJjZV9qeFlUMXpWOUNNcHZlbVp6QnVJQ0ppNGhxQU1BQUF+fjDZo4rSBTgNQAE=; wxtokenkey=9e56783d1b480a605350404acf20e7b09a00f1068e90efb13b62d804b7520920
Q-UA2: QV=3&PL=ADR&PR=WX&PP=com.tencent.mm&PPVN=6.6.0&TBSVC=43602&CO=BK&COVC=043632&PB=GE&VE=GA&DE=PHONE&CHID=0&LCID=9422&MO= M1E &RL=1080*1920&OS=7.0&API=24
Q-GUID: 0fd685fa8c515a30dd9f7caf13b788cb
Q-Auth: 31045b957cf33acf31e40be2f3e71c5217597676a9729f1b
        """
        print(utils.str_to_dict(headers))
        r = requests.post(url, data=body, params=params, verify=False, headers=utils.str_to_dict(headers))
        print(r.text)


if __name__ == '__main__':
    crawler = WeiXinCrawler()
    # crawler.crawl()
    for post in Post.objects(read_num=0):
        print(post.content_url)
        crawler.update(post)
        break
