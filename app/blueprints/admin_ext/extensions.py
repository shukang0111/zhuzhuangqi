import hashlib
import json
import urllib

import requests
import xmltodict as xmltodict
from urllib import parse
from flask import request, make_response, current_app, redirect, url_for, render_template, session, jsonify

from app.blueprints.admin_ext import bp_admin_ext
from app.models import db, models, Admin
from app.utils.redis_util import redis_client
from app.utils.weixin_util import get_access_token, create_menu, get_menu, delete_menu, get_wx_user_detail, \
    get_auth2_access_token, WEIXIN, get_auth_url

WX_TOKEN = "shukang"


@bp_admin_ext.route('/data/init/', methods=['GET'])
def data_init():
    """数据初始化"""
    db.create_tables(models)
    if Admin.select().count() == 0:
        Admin.new('admin', 'zhuzhuangqi')
    return 'Success'


@bp_admin_ext.route('/wx/verify/', methods=['GET', 'POST'])
def verify_ex_token():
    """测试"""
    if request.method == 'GET':
        args = request.args
        print(args)

        token = WX_TOKEN
        data = request.args
        signature = data.get('signature', '')
        timestamp = data.get('timestamp', '')
        nonce = data.get('nonce', '')
        echostr = data.get('echostr', '')
        s = sorted([timestamp, nonce, token])
        # 字典排序
        s = ''.join(s)
        if hashlib.sha1(s.encode('utf-8')).hexdigest() == signature:
            # 判断请求来源，并对接受的请求转换为utf-8后进行sha1加密
            response = make_response(echostr)
            return response

    elif request.method == "POST":
        xml_str = request.data
        print(xml_str)
        current_app.logger.info(xml_str)
        if not xml_str:
            return ""
        # 对xml字符串进行解析
        xml_dict = xmltodict.parse(xml_str)
        # current_app.logger.info(xml_dict)
        xml_dict = xml_dict.get("xml")
        current_app.logger.info(xml_dict)
        msg_type = xml_dict.get("MsgType")

        if msg_type == "event":  # 用户关注/取消关注信息
            event = xml_dict.get("Event")
            # 获取系统用户信息
            if event == "subscribe":  # 用户未关注，进行关注后的事件推送
                # user = xml_dict.get("EventKey")
                # user_id = eval(user.split("_")[1])
                # current_app.logger.info("{0}_{1}_{2}_{3}".format(msg_type, user_id, type(msg_type), type(user_id)))
                access_token = get_access_token()
                redis_client.set("ACCESS_TOKEN", access_token, ex=7000)
                # access_token = redis_client.get("WX_ACCESS_TOKEN")
                openid = xml_dict.get("FromUserName")
                ToUserName = xml_dict.get("ToUserName")  # 开发者微信号
                create_time = xml_dict.get("CreateTime")
                # 获取用户信息
                user_info_url = 'https://api.weixin.qq.com/cgi-bin/user/info?'
                params = {
                    "access_token": access_token,
                    "openid": openid,
                    "lang": "zh_CN"
                }
                resp_json = requests.get(user_info_url, params=params).json()
                current_app.logger.info(resp_json)
                item = dict()
                item['scan_code'] = 1
                item['subscribe'] = resp_json.get("subscribe")
                item['openid'] = openid
                item['nickname'] = resp_json.get("nickname")
                item['headimgurl'] = resp_json.get('headimgurl')
                item['event'] = event
                item['unionid'] = resp_json.get("unionid")
                current_app.logger.info(item)

            # elif event == "SCAN":  # 用户已关注时的事件推送
            #     openid = xml_dict.get('FromUserName')
            #     user_id = eval(xml_dict.get("EventKey"))
            #
            #     if merchant_token.wx_user_info and (merchant_token.wx_user_info.get(openid) == openid):
            #         pass
            #     else:
            #         access_token = redis_client.get("WX_ACCESS_TOKEN")
            #         # 获取用户信息
            #         user_info_url = 'https://api.weixin.qq.com/cgi-bin/user/info?'
            #         params = {
            #             "access_token": access_token,
            #             "openid": openid,
            #             "lang": "zh_CN"
            #         }
            #         resp_json = requests.get(user_info_url, params=params).json()
            #         item = dict()
            #         item['scan_code'] = 1
            #         item['subscribe'] = resp_json.get("subscribe")
            #         item['openid'] = openid
            #         item['nickname'] = resp_json.get("nickname")
            #         item['headimgurl'] = resp_json.get('headimgurl')
            #         item['event'] = event
            #         item['event_key'] = eval(xml_dict.get("EventKey"))
            #         item['unionid'] = resp_json.get("unionid")
            # elif event == "unsubscribe":  # 用户取消订阅
                # merchant_token.update_wx_user_info(None)
                # pass
        return "success"
    # code = request.args.get('code')
    # current_app.logger.info(code)
    # url = "https://api.weixin.qq.com/sns/oauth2/access_token?"
    # item = {
    #     "appid": WEIXIN['app_id'],
    #     "code": code,
    #     "grant_type": "authorization_code"
    # }
    # wx_url = url + urllib.parse.urlencode(item)
    # print(wx_url)
    # resp = requests.get(wx_url).json()
    # print(resp)
    # if resp:
    #     return resp['openid']
    # else:
    #     return '空的'


@bp_admin_ext.route('/create_menu/', methods=['POST'])
def create_self_menu():
    """创建菜单"""
    number = request.json.get('number')
    item = None
    if number == 1:
        item = create_menu()
    elif number == 2:
        item = get_menu()
    elif number == 3:
        item = delete_menu()
    # elif number == 4:
    #     item = get_auth_url()
    #     print(item)
    return make_response({"code": 0, "message": item})
    # return item







