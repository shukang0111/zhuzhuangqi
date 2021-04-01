# -*- coding: utf-8 -*-
import hashlib
import json
import os
import datetime
import calendar
import random
import string
from hashlib import md5
import urllib
from urllib import parse
from .redis_util import redis_client
from .string_util import to_bytes

import time

from flask import current_app, url_for
import requests
# import xmltodict


# VERIFY = os.getenv('CA_CERTS_PATH') or False
WEIXIN = {
    'app_id': 'wx36fe24ffe00a7250',
    # 'app_id': 'wxb8f27e67d93fa31f',  # 测试
    'app_secret': '29ce21eb591d6b2b54869094b4121e5b',
    # 'app_secret': '7330e6f5a480f612c1683ac7810673bb',  # 测试
}


def get_auth_url(redirect_url):
    """获取授权链接"""
    url = "https://open.weixin.qq.com/connect/oauth2/authorize"
    item = {
        "appid": WEIXIN['app_id'],
        # "redirect_uri": "http://d0269770c756.ngrok.io/api.user/",
        "redirect_uri": redirect_url,
        "response_type": "code",
        "scope": "snsapi_base",
        "state": "STATE"
    }
    wx_url = url + "?" + urllib.parse.urlencode(item) + "#wechat_redirect"

    return wx_url


def get_auth2_access_token(code):
    """通过code获取网页auth授权access_token"""
    url = " https://api.weixin.qq.com/sns/oauth2/access_token"
    item = {
        "appid": WEIXIN['app_id'],
        "secret": WEIXIN['app_secret'],
        "code": code,
        "grant_type": "authorization_code"
    }
    wx_url = url + "?" + urllib.parse.urlencode(item)
    resp = requests.get(wx_url).json()
    current_app.logger.info(resp)
    return resp


def get_wx_user_detail(access_token, openid):
    """拉取微信用户信息"""
    url = " https://api.weixin.qq.com/sns/userinfo"
    item = {
        "access_token": access_token,
        "openid": openid,
        "lang": "zh_CN"
    }
    wx_url = url + "?" + urllib.parse.urlencode(item)
    resp = requests.get(wx_url).json()
    current_app.logger.info(resp)
    return resp


def get_access_token() -> str:
    """获取access_token 基础支持中的token和网页授权有区别"""
    url = 'https://api.weixin.qq.com/cgi-bin/token'

    params = {
        'grant_type': 'client_credential',
        'appid': WEIXIN['app_id'],
        'secret': WEIXIN['app_secret']
    }
    ret = requests.get(url, params=params).json()
    current_app.logger.info(ret)
    access_token = ret.get('access_token')
    if not access_token:
        raise RuntimeError(repr(ret))
    return access_token


def get_weixin_jsapi_ticket(access_token):
    """获取jsapi_ticket，jsapi_ticket是公众号用于调用微信JS接口的临时票据"""
    param = {
        'access_token': access_token,
        'type': 'jsapi'
    }
    url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket'
    resp = requests.get(url, params=param).json()
    current_app.logger.info(resp)
    jsapi_ticket = resp.get("ticket")
    if not jsapi_ticket:
        raise RuntimeError(repr(resp))
    return jsapi_ticket


def get_weixin_sign(url):
    """获取微信分享链接签名"""
    try:
        access_token = (redis_client.get("ACCESS_TOKEN")).decode()
    except:
        access_token = get_access_token()
        redis_client.set("ACCESS_TOKEN", access_token, ex=7000)

    # 先从缓存获取ticket
    try:
        js_ticket = redis_client.get("WEIXIN_JSAPI_TICKET").decode()
    except:
        js_ticket = get_weixin_jsapi_ticket(access_token)
        redis_client.set("WEIXIN_JSAPI_TICKET", js_ticket, ex=7000)

    # 动态生成签名数据
    noncestr = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))
    timestamp = int(time.time())
    data = {
        "noncestr": noncestr,
        "jsapi_ticket": js_ticket,
        "timestamp": timestamp,
        "url": url
    }
    sort_string = '&'.join(['%s=%s' % (key.lower(), data[key]) for key in sorted(data)])
    data['signature'] = hashlib.sha1(sort_string.encode('utf-8')).hexdigest()
    data['app_id'] = WEIXIN['app_id']
    return data


# def send_template_msg(openid, template_id):
#     """发送模板消息"""
#     url = 'https://api.weixin.qq.com/cgi-bin/message/template/send'
#     try:
#         access_token = (redis_client.get("ACCESS_TOKEN")).decode()
#     except:
#         access_token = get_access_token()
#         redis_client.set("ACCESS_TOKEN", access_token, ex=7000)
#     params = {
#         'access_token': access_token
#     }
#     data = {
#         'touser': openid,
#         'template_id': template_id,
#         'data': {
#             'first': {
#                 'value': '订阅成功',
#                 'color': '#173177'
#             },
#             'keyword1': {
#                 'value': 'xxx',
#                 'color': '#173177'
#             },
#             'remark': {
#                 'value': 'xxx',
#                 'color': '#173177'
#             }
#         }
#     }
#     resp = requests.post(url, params=params, data=json.dumps(data)).json()
#     return resp


def create_menu(data):
    """
    创建自定义菜单
    data = {
        "button": [
            {
                "name": "菜单",
                "sub_button": [
                    {
                        "type": "view",
                        "name": "首页",
                        "url": "https://zzqapi.e-shigong.com/"
                    }
                ]
            }
        ]
    }
    """
    try:
        access_token = (redis_client.get("ACCESS_TOKEN")).decode()
    except:
        access_token = get_access_token()
        redis_client.set("ACCESS_TOKEN", access_token, ex=7000)
    url = 'https://api.weixin.qq.com/cgi-bin/menu/create?access_token={}'.format(access_token)

    resp = requests.post(url, data=data).json()
    current_app.logger.info('resp：{}'.format(resp))
    return resp


def get_menu():
    """查询自定义菜单"""
    try:
        access_token = (redis_client.get("ACCESS_TOKEN")).decode()
    except:
        access_token = get_access_token()
        redis_client.set("ACCESS_TOKEN", access_token, ex=7000)
    url = 'https://api.weixin.qq.com/cgi-bin/get_current_selfmenu_info?access_token={}'.format(access_token)
    resp = requests.get(url).json()
    current_app.logger.info('自定义菜单：{}'.format(resp))
    return resp


def delete_menu():
    """删除自定义菜单"""
    try:
        access_token = (redis_client.get("ACCESS_TOKEN")).decode()
    except:
        access_token = get_access_token()
        redis_client.set("ACCESS_TOKEN", access_token, ex=7000)
    url = 'https://api.weixin.qq.com/cgi-bin/menu/delete?access_token={}'.format(access_token)
    resp = requests.get(url).json()
    current_app.logger.info('resp：{}'.format(resp))
    return resp
