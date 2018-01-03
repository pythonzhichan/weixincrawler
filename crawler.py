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
              "pass_ticket=mXHYjLnkYux1rXx8BxNrZpgW4W+yLZxcuvpDWlxbBrjvJo3ECB+ckDAsy/TJJK6P&" \
              "wxtoken=&" \
              "appmsg_token=938_8mF38Lwo0pEMdSKj3kbHYloqANS9CE7-1Wy_pA~~&" \
              "x5=1&" \
              "f=json".format(offset=offset)  # appmsg_token 是临时的

        headers = """
Host: mp.weixin.qq.com
Connection: keep-alive
X-Requested-With: XMLHttpRequest
User-Agent: Mozilla/5.0 (Linux; Android 7.0; M1 E Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.49 Mobile MQQBrowser/6.2 TBS/043632 Safari/537.36 MicroMessenger/6.6.1.1220(0x26060133) NetType/WIFI Language/zh_CN
Accept: */*
Referer: https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MjM5MzgyODQxMQ==&devicetype=android-24&version=26060133&lang=zh_CN&nettype=WIFI&a8scene=7&session_us=gh_c744c4d09c36&pass_ticket=mXHYjLnkYux1rXx8BxNrZpgW4W%2ByLZxcuvpDWlxbBrjvJo3ECB%2BckDAsy%2FTJJK6P&wx_header=1
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,en-US;q=0.8
Cookie: rewardsn=05c38771473771b68376; wxtokenkey=85cfbccfeb5ea40c4dd1af9f2bf871a94fbb8ad2261ab776fcedd86870248d86; wxuin=525477518; devicetype=android-24; version=26060133; lang=zh_CN; pass_ticket=mXHYjLnkYux1rXx8BxNrZpgW4W+yLZxcuvpDWlxbBrjvJo3ECB+ckDAsy/TJJK6P; wap_sid2=CI7NyPoBElxYOXJXWHFSNXBxLWNydFQ1UUtlWEZ3LVFQZUozQTNHTVNrNTBqNER5UW1NLUtGM2w2Z1ZDOFFrMVhacWhrWFhxS0YyMXVWZDVJV3ZUaWFZcVVVWDIwS29EQUFBfjCF2LPSBTgMQJRO
Q-UA2: QV=3&PL=ADR&PR=WX&PP=com.tencent.mm&PPVN=6.6.1&TBSVC=43602&CO=BK&COVC=043632&PB=GE&VE=GA&DE=PHONE&CHID=0&LCID=9422&MO= M1E &RL=1080*1920&OS=7.0&API=24
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

        data_url_params = {'__biz': 'MjM5MzgyODQxMQ==', 'appmsg_type': '9', 'mid': '2650367727',
                           'sn': '08ce54f6f36873e74c638421012bb495', 'idx': '1', 'scene': '0',
                           'title': '2017%E5%B9%B4%EF%BC%8C%E6%84%9F%E8%B0%A2%E4%BD%A0%E4%BB%AC%EF%BC%8C2018%E5%B9%B4%EF%BC%8C%E6%88%91%E4%BB%AC%E7%BB%A7%E7%BB%AD%E5%8A%AA%E5%8A%9B%E5%89%8D%E8%A1%8C',
                           'ct': '1514796292',
                           'abtest_cookie': 'AwABAAoADAANAAgAJIgeALuIHgDhiB4A/IgeAPqJHgANih4ATYoeAF6KHgAAAA==',
                           'devicetype': 'android-24',
                           'version': '/mmbizwap/zh_CN/htmledition/js/appmsg/index3a9713.js', 'f': 'json',
                           'r': '0.6452677228890584', 'is_need_ad': '1', 'comment_id': '1741225191',
                           'is_need_reward': '1', 'both_ad': '0', 'reward_uin_count': '24', 'msg_daily_idx': '1',
                           'is_original': '0', 'uin': '777', 'key': '777',
                           'pass_ticket': 'mXHYjLnkYux1rXx8BxNrZpgW4W%252ByLZxcuvpDWlxbBrjvJo3ECB%252BckDAsy%252FTJJK6P',
                           'wxtoken': '1805512665', 'clientversion': '26060133',
                           'appmsg_token': '938_VN3Rr7O4RIU7lm%2F8_amSJbZBo3RJXACjIMDwDu5ZPbSm2_SW6RpnZGb2Vrp6ECxr9y5QoVCI7H-iQotJ',
                           'x5': '1'}

        # url转义处理
        content_url = html.unescape(post.content_url)
        # 截取查询参数部分
        content_url_params = urlsplit(content_url).query
        # 将参数转化为字典类型
        content_url_params = utils.str_to_dict(content_url_params, "&", "=")
        # 更新到data_url
        data_url_params.update(content_url_params)
        body = "is_only_read=1&req_id=03230SZyTR8kQlPVkKwxbt1A&pass_ticket=mXHYjLnkYux1rXx8BxNrZpgW4W%25252ByLZxcuvpDWlxbBrjvJo3ECB%25252BckDAsy%25252FTJJK6P&is_temp_url=0"
        data = utils.str_to_dict(body, "&", "=")

        headers = """
Host: mp.weixin.qq.com
Connection: keep-alive
Content-Length: 155
Origin: https://mp.weixin.qq.com
X-Requested-With: XMLHttpRequest
User-Agent: Mozilla/5.0 (Linux; Android 7.0; M1 E Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.49 Mobile MQQBrowser/6.2 TBS/043632 Safari/537.36 MicroMessenger/6.6.1.1220(0x26060133) NetType/WIFI Language/zh_CN
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
Accept: */*
Referer: https://mp.weixin.qq.com/s?__biz=MjM5MzgyODQxMQ==&mid=2650367727&idx=1&sn=08ce54f6f36873e74c638421012bb495&chksm=be9cddbb89eb54ad436af5c27c0d0db06da7e3aec613a33dd99f935d684a77b555241207f1ba&scene=0&ascene=7&devicetype=android-24&version=26060133&nettype=WIFI&abtest_cookie=AwABAAoADAANAAgAJIgeALuIHgDhiB4A%2FIgeAPqJHgANih4ATYoeAF6KHgAAAA%3D%3D&lang=zh_CN&pass_ticket=mXHYjLnkYux1rXx8BxNrZpgW4W%2ByLZxcuvpDWlxbBrjvJo3ECB%2BckDAsy%2FTJJK6P&wx_header=1
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,en-US;q=0.8
Cookie: rewardsn=05c38771473771b68376; wxtokenkey=92c034f1d4d5cfe011a9222522d96c3af508a6e35160b5f6fefa185431bda832; wxuin=525477518; devicetype=android-24; version=26060133; lang=zh_CN; pass_ticket=mXHYjLnkYux1rXx8BxNrZpgW4W+yLZxcuvpDWlxbBrjvJo3ECB+ckDAsy/TJJK6P; wap_sid2=CI7NyPoBElx2ZFNJVXFOVFh2S3U5X1hLS2pZb2Z0Ujd1NTBPdlMzbEpwMjdVRlYtTHluRWkwZzIwUzY4ZVM3Y294MzU5aDM5eWxfRWVKOVJoY0dvVmZuQTk2S1JLS29EQUFBfjCQ5LPSBTgNQAE=
Q-UA2: QV=3&PL=ADR&PR=WX&PP=com.tencent.mm&PPVN=6.6.1&TBSVC=43602&CO=BK&COVC=043632&PB=GE&VE=GA&DE=PHONE&CHID=0&LCID=9422&MO= M1E &RL=1080*1920&OS=7.0&API=24
Q-GUID: 0fd685fa8c515a30dd9f7caf13b788cb
Q-Auth: 31045b957cf33acf31e40be2f3e71c5217597676a9729f1b
        """

        headers = utils.str_to_dict(headers)

        data_url = "https://mp.weixin.qq.com/mp/getappmsgext"
        r = requests.post(data_url, data=data, verify=False, params=data_url_params, headers=headers)

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
            logger.warning(u"没有获取的真实数据，请检查请求参数是否正确，返回的数据为：data=%s" % r.text)


if __name__ == '__main__':
    # 直接运行这份代码很定或报错，或者根本抓不到数据
    # 因为header里面的cookie信息已经过去，还有URL中的appmsg_token也已经过期
    # 你需要配合Fiddler或者charles通过手机重新加载微信公众号的更多历史消息
    # 从中获取最新的headers和appmsg_token替换上面
    crawler = WeiXinCrawler()
    # crawler.crawl()
    for post in Post.objects(read_num=0):
        crawler.update_post(post)
        time.sleep(1)

