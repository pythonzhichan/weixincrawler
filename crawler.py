# -*- coding: utf-8 -*-

import json
import logging
import time
from datetime import datetime

import requests

import utils
from models import Post

requests.packages.urllib3.disable_warnings()
from urllib.parse import urlsplit
import html

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
              "appmsg_token=937_UHGd449%2FBhXAOu4LEX3_DAClCTPtdLXXpUqHQg~~&" \
              "x5=1&" \
              "f=json".format(offset=offset)  # appmsg_token 是临时的

        headers = """
Host: mp.weixin.qq.com
Accept-Encoding: gzip, deflate
Cookie: ts_uid=3175878595; devicetype=iOS10.3.3; lang=zh_CN; pass_ticket=YZe3bIk+CZTU9OKVtY18FMsPmra+SBBXM1/JKTMgppKJ/0V3B99XDPcwlChD+3GL; version=16060120; wap_sid2=CIDUopEDElxKbHZCekJBVEJJT0FZb1VQSTZBZDlqNllaLXJpX0ptdWplVDVHTlF4UmlzdmxwNE85VWNJanJuYlhkOTJpZkxBU0ROSU1US0taNzVwZVNXNkpTY1dHYWtEQUFBfjDA6pTSBTgMQJRO; wxuin=841525760; wxtokenkey=0764bcd88cd2a131bbb205daa5f78bbd51a67bafef98327188df0288e2450363; ua_id=0QjBcaeG8vk11IhBAAAAAGHV4Cqd2-aR9dxpfQrd_L8=; pgv_pvid=7585005942; sd_cookie_crttime=1514388301744; sd_userid=79621514388301744
Connection: keep-alive
Accept: */*
User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Mobile/14G60 MicroMessenger/6.6.1 NetType/WIFI Language/zh_CN
Referer: https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MjM5MzgyODQxMQ==&devicetype=iOS10.3.3&version=16060120&lang=zh_CN&nettype=WIFI&a8scene=7&session_us=gh_c744c4d09c36&fontScale=100&pass_ticket=YZe3bIk%2BCZTU9OKVtY18FMsPmra%2BSBBXM1%2FJKTMgppKJ%2F0V3B99XDPcwlChD%2B3GL&wx_header=1
Accept-Language: zh-cn
X-Requested-With: XMLHttpRequest
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

        msg_list = msg_list.replace("\/", "/")
        data = json.loads(msg_list)
        msg_list = data.get("list")
        for msg in msg_list:
            p_date = msg.get("comm_msg_info").get("datetime")
            msg_info = msg.get("app_msg_ext_info")  # 非图文消息没有此字段
            if msg_info:
                WeiXinCrawler._insert(msg_info, p_date)
                multi_msg_info = msg_info.get("multi_app_msg_item_list")
                for msg_item in multi_msg_info:
                    WeiXinCrawler._insert(msg_item, p_date)
            else:
                logger.warning(u"此消息不是图文推送，data=%s" % json.dumps(msg.get("comm_msg_info")))

    @staticmethod
    def _insert(item, p_date):
        keys = ('title', 'author', 'content_url', 'digest', 'cover', 'source_url')
        sub_data = utils.sub_dict(item, keys)
        post = Post(**sub_data)
        p_date = datetime.fromtimestamp(p_date)
        post["p_date"] = p_date
        logger.info('save data %s ' % post.title)
        try:
            post.save()
        except Exception as e:
            logger.error("保存失败 data=%s" % post.to_json(), exc_info=True)

    @staticmethod
    def update_post(post):


        data_url_params = {'__biz': 'MjM5MzgyODQxMQ==', 'appmsg_type': '9', 'mid': '2650367680',
                           'sn': '2e8ef8bcf4dc176c46376508cb5a8fa7', 'idx': '1', 'scene': '21',
                           'title': '%E5%85%B3%E4%BA%8E%E6%AD%A3%E5%88%99%E8%A1%A8%E8%BE%BE%E5%BC%8F%E7%9A%845%E4%B8%AA%E5%B0%8F%E8%B4%B4%E5%A3%AB',
                           'ct': '1513900976',
                           'abtest_cookie': 'AwABAAoADAANAAcAJIgeALuIHgDhiB4A/IgeAPqJHgAZih4ATYoeAAAA',
                           'devicetype': 'android-24',
                           'version': '/mmbizwap/zh_CN/htmledition/js/appmsg/index3a9713.js',
                           'f': 'json', 'r': '0.7675446466698528', 'is_need_ad': '1', 'comment_id': '3799137919',
                           'is_need_reward': '1', 'both_ad': '0', 'reward_uin_count': '24', 'msg_daily_idx': '1',
                           'is_original': '0', 'uin': '777', 'key': '777',
                           'pass_ticket': 'J1PFXucN0v4vmF19Pkngffyo4CvzTAkiJNdFJN9uQNIMVLMBFeSl6P8zbfwBJ4sO',
                           'wxtoken': '204390160', 'clientversion': '26060030',
                           'appmsg_token': '937_D8gMA6eZWUYVZo6QUXO6keTPdtbgwSEexQWAhnI8XvC1V1BMh3m05cmSURoPtkr5ppr0iDTw7bWgBkMr',
                           'x5': '1'}

        # url转义处理
        content_url = html.unescape(post.content_url)
        # 截取查询参数部分
        content_url_params = urlsplit(content_url).query
        # 将参数转化为字典类型
        content_url_params = utils.str_to_dict(content_url_params, "&", "=")
        # 更新到data_url
        content_url_params.update(content_url_params)
        body = "is_only_read=1&req_id=2900i1sqRlQwikp0KEVJieW4&pass_ticket=J1PFXucN0v4vmF19Pkngffyo4CvzTAkiJNdFJN9uQNIMVLMBFeSl6P8zbfwBJ4sO&is_temp_url=0"
        data = utils.str_to_dict(body, "&", "=")

        headers = """
        
Host: mp.weixin.qq.com
Connection: keep-alive
Content-Length: 137
Origin: https://mp.weixin.qq.com
X-Requested-With: XMLHttpRequest
User-Agent: Mozilla/5.0 (Linux; Android 7.0; M1 E Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.49 Mobile MQQBrowser/6.2 TBS/043632 Safari/537.36 MicroMessenger/6.6.1200(0x26060030) NetType/WIFI Language/zh_CN
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
Accept: */*
Referer: https://mp.weixin.qq.com/s?__biz=MjM5MzgyODQxMQ==&mid=2650367680&idx=1&sn=2e8ef8bcf4dc176c46376508cb5a8fa7&chksm=be9cdd9489eb54822dc5993ff71050ca9011aff07fdf642b3eccdee7e20dc2efad9f21fb1a63&scene=21&ascene=7&devicetype=android-24&version=26060030&nettype=WIFI&abtest_cookie=AwABAAoADAANAAcAJIgeALuIHgDhiB4A%2FIgeAPqJHgAZih4ATYoeAAAA&lang=zh_CN&pass_ticket=J1PFXucN0v4vmF19Pkngffyo4CvzTAkiJNdFJN9uQNIMVLMBFeSl6P8zbfwBJ4sO&wx_header=1
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,en-US;q=0.8
Cookie: pgv_info=ssid=s2190841734; pgv_pvid=9172712625; rewardsn=a520f9c4f8c2c14d9ab0; wxtokenkey=902a8ac15e846d9a567021f9652cec8ddd60662aee0c86db3cb47e638f2a4bf5; wxuin=525477518; devicetype=android-24; version=26060030; lang=zh_CN; pass_ticket=J1PFXucN0v4vmF19Pkngffyo4CvzTAkiJNdFJN9uQNIMVLMBFeSl6P8zbfwBJ4sO; wap_sid2=CI7NyPoBElw4bFowVktRcDNGZFBkSzRxeDNRS1BZclFQYTZXa1hWNWg4THVFN21tVnVJQ1YtZjk5Qml2RjkxTThqcFZJZUFCenZ2cnpiUXhiN2dXcVI4X1pWYUJCS2tEQUFBfjCHspTSBTgNQAE=
Q-UA2: QV=3&PL=ADR&PR=WX&PP=com.tencent.mm&PPVN=6.6.0&TBSVC=43602&CO=BK&COVC=043632&PB=GE&VE=GA&DE=PHONE&CHID=0&LCID=9422&MO= M1E &RL=1080*1920&OS=7.0&API=24
Q-GUID: 0fd685fa8c515a30dd9f7caf13b788cb
Q-Auth: 31045b957cf33acf31e40be2f3e71c5217597676a9729f1b
        """

        headers = utils.str_to_dict(headers)

        url = "https://mp.weixin.qq.com/mp/getappmsgext"
        r = requests.post(url, data=data, verify=False, params=content_url_params, headers=headers)

        result = r.json()
        if result.get("appmsgstat"):
            post['read_num'] = result.get("appmsgstat").get("read_num")
            post['like_num'] = result.get("appmsgstat").get("like_num")
            post['reward_num'] = result.get("reward_total_count")
            post['u_date'] = datetime.now()
            logger.info("「%s」read_num: %s like_num: %s reward_num: %s" %
                        (post.title, post['read_num'], post['like_num'], post['reward_num']))
            post.save()
        else:
            logger.warning(u"没有获取的真实数据，请检查请求参数是否正确，data=%s" % r.text)


if __name__ == '__main__':
    # 直接运行这份代码很定或报错，或者根本抓不到数据
    # 因为header里面的cookie信息已经过去，还有URL中的appmsg_token也已经过期
    # 你需要配合Fiddler或者charles通过手机重新加载微信公众号的更多历史消息
    # 从中获取最新的headers和appmsg_token替换上面
    crawler = WeiXinCrawler()
    crawler.crawl()
    # for post in Post.objects(read_num=0):
    #     crawler.update(post)
    #     time.sleep(1)
