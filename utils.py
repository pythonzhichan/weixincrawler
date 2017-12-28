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


def str_to_dict(s, join_symbol="\n", split_symbol=":"):
    """
    key与value通过split_symbol连接， key,value 对之间使用join_symbol连接
    例如： a=b&c=d   join_symbol是&, split_symbol是=
    :param s: 原字符串
    :param join_symbol: 连接符
    :param split_symbol: 分隔符
    :return: 字典
    """
    s_list = s.split(join_symbol)
    data = dict()
    for item in s_list:
        item = item.strip()
        if item:
            k, v = item.split(split_symbol, 1)
            data[k] = v.strip()
    return data


if __name__ == '__main__':
    d = {"a": "1", "b": 2, "c": 3}
    print(sub_dict(d, ["a", "b"]))
