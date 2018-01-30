import html


def str_to_dict(headers):
    """
    将"Host: mp.weixin.qq.com"格式的字符串转换成字典类型
    转换成字典类型
    :param headers: str
    :return: dict
    """
    headers = headers.split("\n")
    d_headers = dict()
    for h in headers:
        h = h.strip()
        if h:
            k, v = h.split(":", 1)
            d_headers[k] = v.strip()
    return d_headers


def sub_dict(d, keys):
    return {k: html.unescape(d[k]) for k in d if k in keys}


def str_to_dict(s, join="\n", append=":"):
    """
    将由键值对组成的字符串转换成字典类型

    例如： a=b&c=d   join_symbol是&, split_symbol是=
    :param s: 原字符串
    :param join: 多個鍵值對之間的连接符， k1=v1&k2=v2
    :param append: key與value的連接符 key&value
    :return: dict
    """
    s_list = s.split(join)
    data = dict()
    for item in s_list:
        item = item.strip()
        if item:
            k, v = item.split(append, 1)
            data[k] = v.strip()
    return data


if __name__ == '__main__':
    url = "action=getmsg&__biz=MjM5MzgyODQxMQ==&f=json&offset=13&count=10&is_ok=1&scene=124&uin=777&key=777&pass_ticket=%2B8w2Z8mhF4GH%2BNSPyUvZwwQjXrgXNULyll%2Fj9r7UwXOHHv2W%2FijB%2F%2BmBd9%2Bj16qc&wxtoken=&appmsg_token=941_XYFSVfr6tB9dZxRhgbPir_JGecvDUol-xn6lLg~~&x5=0&f=json"
    print(str_to_dict(url, join="&", append="="))
