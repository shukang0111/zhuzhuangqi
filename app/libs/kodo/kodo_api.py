# -*- coding: utf-8 -*-
# @Time     : 2019/8/31 3:29 PM
# @Author   : zhangxinhe@wangzhu.com
# @FileName : kodo_api.py
# @Description: 七牛云存储 Kodo 相关api接口封装
import string
import time
from qiniu import Auth
from qiniu import BucketManager
from qiniu import put_data


from app.utils.common_util import gen_random_str, FileType


class KodoApi(object):
    """
    云存储操作相关API
    """
    # todo:配置信息不能明文配置在代码中，搭建通用的权限配置中心
    __access_key = 'KrGHoCcpnajTWIwWPSksomPWa02MfqDw5iotrwfC'
    __secret_key = 'jkTsrcAEyIvH3pdT6cwHCVCSU2clGTSIzjolSF7C'
    __private_access_key = 'KrGHoCcpnajTWIwWPSksomPWa02MfqDw5iotrwfC'
    __private_secret_key = 'jkTsrcAEyIvH3pdT6cwHCVCSU2clGTSIzjolSF7C'

    __q = Auth(__access_key, __secret_key)
    __q_private = Auth(__private_access_key, __private_secret_key)
    __bucket_name = 'wangzhu_cloud_test'
    __bucket_name_private = 'wangzhucloudprivate'
    __file_type = ['image', 'video', 'file']
    __bucket = BucketManager(__q)
    __bucket_private = BucketManager(__q_private)
    __server_url = 'http://cdn.e-shigong.com/'
    __server_url_private = 'http://pz8sy3jve.bkt.clouddn.com'

    __thumbnail_format = 'imageView2/0/w/{}/h/{}/interlace/1'
    __video_frame_format = 'vframe/jpg/offset/{}'

    @classmethod
    def __gen_file_key(cls, file_type_value, file_name):
        """
        根据上传文件的文件名称，生成上传到七牛上的key

        :param file_name: 上传文件名
        :return:
        """
        file_type = cls.__file_type[file_type_value]
        timestamp = int(time.time())
        return "common-{}-{}-{}".format(file_type, timestamp, file_name)

    @classmethod
    def __gen_project_file_key(cls, user_id, file_type_value, file_name):
        """
        根据上传文件的项目id、阶段id、文件名称，生成上传到七牛上的key

        :param project_id: 项目id
        :param phase_id: 上传文件阶段
        :param file_name: 上传文件名
        :return:
        """
        file_type = cls.__file_type[file_type_value]
        timestamp = int(time.time())
        return "user-{}-{}-{}-{}".format(user_id, file_type, timestamp, file_name)

    @classmethod
    def __gen_company_file_key(cls, company_id, file_type, file_name):
        """
        公司账号文件上传七牛云

        :param company_id:
        :param file_type:
        :param file_name:
        :return:
        """
        file_type = cls.__file_type[file_type]
        timestamp = int(time.time())
        return "company-{}-{}-{}-{}".format(company_id, file_type, timestamp, file_name)

    @classmethod
    def __gen_avatar_key(cls, user_id, file_name):
        """
        生成用户头像存储路径

        :param file_name: 头像文件名
        :return:
        """
        return "user-{}-avatar-{}".format(user_id, file_name)

    @classmethod
    def get_image_thumbnail(cls, origin_url, width=200, height=200):
        """
        获取图片缩略图

        :param width: 缩略图宽度
        :param length: 缩略图长度
        :return:
        """
        para_format = cls.__thumbnail_format.format(width, height)
        if '?' in origin_url:
            # return cls.__q.private_download_url(origin_url + '&' + para_format, expires=3600*12)
            return origin_url + '&' + para_format
        else:
            # return cls.__q.private_download_url(origin_url + '?' + para_format, expires=3600*12)
            return origin_url + '?' + para_format

    @classmethod
    def get_video_frame_image(cls, origin_url, frame_num=1):
        """
        指定获取视频的第几帧图片

        :param frame_num:
        :return:
        """
        frame_format = cls.__video_frame_format.format(frame_num)
        if '?' in origin_url:
            return cls.__q.private_download_url(origin_url + '&' + frame_format, expires=3600*12)
        else:
            return cls.__q.private_download_url(origin_url + '?' + frame_format, expires=3600*12)

    @classmethod
    def get_file_upload_token(cls, file_list):
        """
        获取文件上传token

        :param file_list: [{"name": "file1.jpg", "type": 0}]
        :return: 返回上传token和文件的key值
        """
        upload_token_list = []
        for file in file_list:
            file_name = file['name']
            file_type = file['type']
            q = cls.__q
            bucket_name = cls.__bucket_name
            server_url = cls.__server_url

            # if file_type == FileType.OTHER.value:
            #     q = cls.__q_private
            #     bucket_name = cls.__bucket_name_private
            #     server_url = cls.__server_url_private

            key = cls.__gen_file_key(file_type, file_name)
            url = server_url + key
            token = q.upload_token(bucket_name, key, 3600 * 12)  # 一小时过期

            upload_token_list.append({"url": url, "token": token, "key": key})

        return upload_token_list

    @classmethod
    def get_project_file_upload_token(cls, user_id, file_list):
        """
        获取项目文件上传token

        :param user_id: 项目id
        :param file_list: [{"name": "file1.jpg", "type": 0}]
        :return: 返回上传token和文件的key值
        """
        upload_token_list = []
        for file in file_list:
            file_name = file.get('name', 'unknown')
            file_type = file['type']
            q = cls.__q
            bucket_name = cls.__bucket_name
            server_url = cls.__server_url

            # if file_type == FileType.OTHER.value:
            #     q = cls.__q_private
            #     bucket_name = cls.__bucket_name_private
            #     server_url = cls.__server_url_private

            key = cls.__gen_project_file_key(user_id, file_type, file_name)
            url = server_url + key
            token = q.upload_token(bucket_name, key, 3600*12)  # 一小时过期

            upload_token_list.append({"url": url, "token": token, "key": key})

        return upload_token_list

    @classmethod
    def get_company_file_upload_token(cls, company_id, file_list):
        """
        获取公司文件上传token

        :param company_id:
        :param file_list:
        :return:
        """
        upload_token_list = []
        for file in file_list:
            file_name = file['name']
            file_type = file['type']

            q = cls.__q
            bucket_name = cls.__bucket_name
            server_url = cls.__server_url

            # if file_type == FileType.OTHER.value:
            #     q = cls.__q_private
            #     bucket_name = cls.__bucket_name_private
            #     server_url = cls.__server_url_private

            key = cls.__gen_company_file_key(company_id, file_type, file_name)
            url = server_url + key
            token = q.upload_token(bucket_name, key, 3600)  # 一小时过期

            upload_token_list.append({"url": url, "token": token, "key": key})

        return upload_token_list

    @classmethod
    def get_user_avatar_upload_token(cls, user_id, file_name):
        """
        获取用户头像上传token

        :param user_id 用户编号
        :param file_name 头像文件名
        :return:
        """
        key = cls.__gen_avatar_key(user_id, file_name)

        token = cls.__q.upload_token(cls.__bucket_name, key, 3600)  # 一小时过期

        return token

    @classmethod
    def get_download_token_list(cls, url_list):
        """
        获取下载资源路径的token

        :return:
        """
        url_token_list = []
        for url in url_list:
            private_url = cls.get_download_token(0, url)  # 截取url路径，过滤掉路径中参数
            url_token_list.append(private_url)  # 拼接返回完整访问的url

        return url_token_list

    @classmethod
    def get_download_token(cls, file_type, url, expires=3600*12):
        """
        获取下载资源路径的token

        :param file_type: 文件类型
        :param url: url链接
        :param expires: 过期时间
        :return:
        """
        if file_type == FileType.OTHER.value:
            return cls.__q_private.private_download_url(url.split('?')[0], expires=expires)
        else:
            return url

    @classmethod
    def upload_file(cls, fp):
        """
        上传文件

        :param fp:
        :return:
        """

        key = 'uploaded_img' + str(int(time.time() * 1000)) + gen_random_str(4, chars=string.ascii_letters)
        upload_token = cls.__q.upload_token(cls.__bucket_name, key, 3600)
        ret, info = put_data(upload_token, key, fp)

        return cls.__server_url + key


class KodoUploadInstance:
    """
    kodo上传实例
    """

    def upload_file(self, fp):
        access_key = 'KrGHoCcpnajTWIwWPSksomPWa02MfqDw5iotrwfC'
        secret_key = 'jkTsrcAEyIvH3pdT6cwHCVCSU2clGTSIzjolSF7C'
        server_url = 'http://cdn.e-shigong.com/'

        auth = Auth(access_key, secret_key)

        key = 'uploaded_img' + str(int(time.time() * 1000)) + gen_random_str(4, chars=string.ascii_letters)
        upload_token = auth.upload_token('wangzhu_cloud_test', key, 3600)
        put_data(upload_token, key, fp)

        return server_url + key