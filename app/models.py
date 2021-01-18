from __future__ import annotations

import os
from json import dumps, loads
from time import time
from uuid import uuid4
from datetime import datetime
from typing import Iterable, Optional, Type, TypeVar, Union

from flask import current_app
from peewee import *
from werkzeug.security import generate_password_hash, check_password_hash

from app.api_utils import APIError
from app.utils.aes_util import aes_crypto

db = MySQLDatabase(
    'zhuzhuangqi',
    user='root',
    password='' or os.getenv('MYSQL_PASSWORD'),
    host='127.0.0.1',
    port=3306,
    charset='utf8mb4'
)
T = TypeVar('T', bound='BaseModel')
_nullable_strip = (lambda s: s.strip() or None if s else None)


class _ObjectField(Field):
    """python对象字段"""
    field_type = 'TEXT'

    def db_value(self, value):
        return None if value is None else repr(value)

    def python_value(self, value):
        return None if value is None else eval(value)


class _JsonField(TextField):
    """JSON字段"""
    def db_value(self, value):
        if value is not None:
            return dumps(value)

    def python_value(self, value):
        if value is not None:
            return loads(value)


class BaseModel(Model):
    """表基类"""

    id = AutoField()  # 主键
    uuid = UUIDField(unique=True, default=uuid4)  # UUID
    create_time = DateTimeField(default=datetime.now)  # 创建时间
    update_time = DateTimeField(default=datetime.now)  # 更新时间
    weight = IntegerField(default=0)  # 权重
    show = BooleanField(default=True)  # 展示
    is_delete = BooleanField(default=False)

    class Meta:
        database = db
        only_save_dirty = True

    @classmethod
    def _excluded_field_names(cls):
        """转换为dict时排除在外的字段名"""
        return set()

    @classmethod
    def _extra_attr_names(cls):
        """转换为dict时额外增加的属性名"""
        return set()

    @classmethod
    def get_by_id(cls: Type[T], _id: Union[int, str], code: int = 0, message: str = None) -> Optional[T]:
        """根据主键获取

        Args:
            _id: 主键
            code: APIError错误码
            message: APIError错误描述
        """
        try:
            return cls.select().where(cls.id == _id).get()
        except cls.DoesNotExist:
            if code:
                raise APIError(code, message)

    @classmethod
    def get_by_uuid(cls: Type[T], _uuid: str, code: int = 0, message: str = None) -> Optional[T]:
        """根据UUID获取

        Args:
            _uuid: UUID
            code: APIError错误码
            message: APIError错误描述
        """
        try:
            return cls.select().where(cls.uuid == _uuid).get()
        except cls.DoesNotExist:
            if code:
                raise APIError(code, message)

    def to_dict(self, *, only: Iterable[str] = None, exclude: Iterable[str] = None, recurse: bool = False,
                max_depth: int = None) -> dict:
        """转换为dict

        Args:
            only: 仅包含在内的字段名列表
            exclude: 排除在外的字段名列表
            recurse: 是否对外键进行递归转换
            max_depth: 递归深度，默认无限制
        """
        only = set(only or [])
        exclude = set(exclude or []) | self._excluded_field_names()
        if max_depth is None:
            max_depth = -1
        if max_depth == 0:
            recurse = False
        data = {}

        # fields
        for field_name, field in self._meta.fields.items():
            if field_name in exclude or (only and field_name not in only):
                continue
            field_data = self.__data__.get(field_name)
            if recurse and isinstance(field, ForeignKeyField):
                if field_data:
                    rel_obj = getattr(self, field_name)
                    field_data = rel_obj.to_dict(recurse=True, max_depth=max_depth - 1)
                else:
                    field_data = None
            data[field_name] = field_data

        # extra
        for attr_name in self._extra_attr_names():
            if attr_name in exclude or (only and attr_name not in only):
                continue
            attr = getattr(self, attr_name)
            data[attr_name] = attr() if callable(attr) else attr
        return data

    def save_ut(self) -> int:
        """记录更新时间并持久化到数据库"""
        self.update_time = datetime.now()
        return self.save()

    # def save_if_changed(self, update_ut: bool = True) -> Optional[int]:
    #     """若有数值变动则持久化到数据库
    #
    #     Args:
    #         update_ut: 是否记录更新时间
    #     """
    #     db_obj = self.get_by_id(self.id)
    #     for f in self._dirty:
    #         if self.__data__.get(f) != db_obj.__data__.get(f):
    #             if update_ut:
    #                 return self.save_ut()
    #             else:
    #                 return self.save()

    def update_show(self, show: int) -> show:
        """设置是否展示"""
        self.show = show
        return self.save()

    def update_weight(self, weight: int) -> weight:
        """设置排序权重"""
        self.weight = weight
        return self.save()

    def update_delete(self, is_delete: int) -> is_delete:
        """删除"""
        self.is_delete = is_delete
        return self.save()


class Admin(BaseModel):
    """后台管理员账号"""
    TOKEN_EXPIRES = 7  # 身份令牌的过期时间（天）
    username = CharField()
    password = CharField()

    class Meta:
        table_name = 'admin'

    @classmethod
    def new(cls, username, password):
        return cls.create(
            username=username.strip(),
            password=generate_password_hash(password)
        )

    @classmethod
    def get_by_username(cls, username: str) -> Optional[Admin]:
        """根据用户名获取"""
        try:
            return cls.select().where(cls.username == username).get()
        except cls.DoesNotExist:
            pass

    @classmethod
    def get_by_token(cls, token: str) -> Optional[Admin]:
        """根据身份令牌获取"""
        try:
            text = aes_crypto.decrypt(token)
            _uuid, expires = text.split(':')
            expires = int(expires)
        except Exception as e:
            current_app.logger.error(e)
        else:
            if expires > time():
                return cls.get_by_uuid(_uuid)

    def gen_token(self) -> str:
        """生成身份令牌"""
        text = '{0}:{1}'.format(self.uuid, int(time()) + 86400 * self.TOKEN_EXPIRES)
        return aes_crypto.encrypt(text)

    def set_password(self, password):
        """设置密码"""
        self.password = generate_password_hash(password)
        return self.save_ut()

    def check_password(self, password):
        """检查密码"""
        return check_password_hash(self.password, password)


class WXUser(BaseModel):
    """微信用户信息表"""
    TOKEN_EXPIRES = 30  # 身份令牌的过期时间（天）

    openid = CharField()  # 用户openid
    avatar = CharField(null=True)  # 用户头像
    nickname = CharField()  # 用户昵称
    phone = CharField(null=True)  # 电话号码
    wx_number = CharField(null=True)  # 微信号
    qr_code_url = CharField(null=True)  # 用户二维码，自己上传
    brand = CharField(null=True)  # 品牌
    room_size = DecimalField(default=0, max_digits=6, decimal_places=2)  # 房屋面积
    area_info_id = IntegerField(default=0)  # 地区id

    class Meta:
        table_name = "wx_user"

    @classmethod
    def new(cls, openid, avatar, nickname):
        return cls.create(
            openid=openid,
            avatar=avatar,
            nickname=nickname
        )

    @classmethod
    def get_by_token(cls, token: str) -> Optional[Admin]:
        """根据身份令牌获取"""
        try:
            text = aes_crypto.decrypt(token)
            _uuid, expires = text.split(':')
            expires = int(expires)
        except Exception as e:
            current_app.logger.error(e)
        else:
            if expires > time():
                return cls.get_by_uuid(_uuid)

    def gen_token(self) -> str:
        """生成身份令牌"""
        text = '{0}:{1}'.format(self.uuid, int(time()) + 86400 * self.TOKEN_EXPIRES)
        return aes_crypto.encrypt(text)

    @classmethod
    def get_by_openid(cls, openid):
        """根据openid查询"""
        wx_user = None
        try:
            wx_user = cls.select().where(cls.openid == openid).get()
        finally:
            return wx_user

    def update_info(self, avatar, nickname, phone, wx_number, qr_code_url):
        """更新用户信息"""
        self.avatar = avatar
        self.nickname = nickname
        self.qr_code_url = qr_code_url
        self.phone = phone
        self.wx_number = wx_number
        return self.save_ut()


class Banner(BaseModel):
    """banner图"""
    cover_url = CharField()
    jump_url = CharField()

    class Meta:
        table_name = "banner"

    @classmethod
    def new(cls, cover_url, jump_url):
        return cls.create(
            cover_url=cover_url,
            jump_url=jump_url,
            show=False
        )

    def update_info(self, cover_url, jump_url):
        """更新banner图信息"""
        self.cover_url = cover_url
        self.jump_url = jump_url
        return self.save_ut()


class PosterType(BaseModel):
    """海报类型"""
    name = CharField()

    class Meta:
        table_name = "poster_type"

    @classmethod
    def new(cls, name):
        return cls.create(
            name=name
        )

    @classmethod
    def get_by_name(cls, name: str):
        try:
            return cls.select().where(cls.name == name, cls.is_delete == 0).get()

        except cls.DoesNotExist:
            pass

    def update_name(self, name):
        """更新海报名称"""
        self.name = name
        return self.save_ut()


class Poster(BaseModel):
    """海报"""
    poster_type_id = IntegerField(default=0)
    name = CharField()
    cover_url = CharField()
    real_use_count = IntegerField(default=0)
    extra_add_count = IntegerField(default=0)

    class Meta:
        table_name = 'poster'

    @classmethod
    def new(cls, poster_type_id, name, cover_url, extra_add_count):
        return cls.create(
            poster_type_id=poster_type_id,
            name=name,
            cover_url=cover_url,
            extra_add_count=extra_add_count
        )

    @classmethod
    def get_by_name(cls, name: str):
        try:
            return cls.select().where(cls.name == name).get()

        except cls.DoesNotExist:
            pass


class PosterTheme(BaseModel):
    """用户保存的海报方案"""
    wx_user_id = IntegerField()
    poster_id = IntegerField()
    name = CharField()
    cover_url = CharField()
    real_use_count = IntegerField(default=0)
    extra_add_count = IntegerField(default=0)

    class Meta:
        table_name = "poster_theme"

    @classmethod
    def new(cls, wx_user_id, poster_id, name, cover_url):
        return cls.create(
            wx_user_id=wx_user_id,
            poster_id=poster_id,
            name=name,
            cover_url=cover_url
        )

    def update_name(self, name):
        """更新我的海波名称"""
        self.name = name
        return self.save_ut()


class ArticleType(BaseModel):
    """文章分类"""
    name = CharField()
    wx_users = ManyToManyField(WXUser, backref='article_types')

    class Meta:
        table_name = 'article_type'

    @classmethod
    def new(cls, name):
        return cls.create(
            name=name
        )

    @classmethod
    def get_by_name(cls, name: str):
        try:
            return cls.select().where(cls.name == name, cls.is_delete == 0).get()

        except cls.DoesNotExist:
            pass


WXUserArticleTypeThrough = ArticleType.wx_users.get_through_model()


class Article(BaseModel):
    """文章"""
    article_type_id = IntegerField(default=0)  # 文章分类id
    title = CharField()
    contents = TextField(default='')
    cover_url = CharField(default='')
    real_use_count = IntegerField(default=0)
    extra_add_count = IntegerField(default=0)

    class Meta:
        table_name = "article"

    @classmethod
    def new(cls, article_type_id, title, contents, cover_url, extra_add_count):
        return cls.create(
            article_type_id=article_type_id,
            title=title,
            contents=contents,
            cover_url=cover_url,
            extra_add_count=extra_add_count
        )

    def update_info(self, title, contents, cover_url, extra_add_count):
        """更新文章信息"""
        self.title = title
        self.contents = contents
        self.cover_url = cover_url
        self.extra_add_count = extra_add_count
        return self.save_ut()

    def update_real_use_count(self):
        self.real_use_count += 1
        return self.save_ut()


class Course(BaseModel):
    """课程"""
    course_title = CharField()  # 视频标题
    course_url = CharField()  # 视频url地址
    cover_url = CharField()  # 封面图url地址
    real_use_count = IntegerField(default=0)  # 实际使用次数
    extra_add_count = IntegerField(default=0)  # 额外增加数量

    class Meta:
        table_name = "course"

    @classmethod
    def new(cls, course_title, course_url, cover_url, extra_add_count):
        return cls.create(
            course_title=course_title,
            course_url=course_url,
            cover_url=cover_url,
            extra_add_count=extra_add_count
        )

    def update_info(self, course_title, course_url, cover_url, extra_add_count):
        """更新课程信息"""
        self.course_title = course_title
        self.course_url = course_url
        self.cover_url = cover_url
        self.extra_add_count = extra_add_count
        return self.save_ut()


class Video(BaseModel):
    """视频"""
    video_title = CharField()  # 视频标题
    video_url = CharField()  # 视频url地址
    cover_url = CharField()  # 封面url地址
    real_use_count = IntegerField(default=0)  # 实际使用次数
    extra_add_count = IntegerField(default=0)  # 额外增加数量

    class Meta:
        table_name = "video"

    @classmethod
    def new(cls, video_title, video_url, cover_url, extra_add_count):
        return cls.create(
            video_title=video_title,
            video_url=video_url,
            cover_url=cover_url,
            extra_add_count=extra_add_count
        )

    def update_info(self, video_title, video_url, cover_url, extra_add_count):
        """更新视频信息"""
        self.video_title = video_title
        self.video_url = video_url
        self.cover_url = cover_url
        self.extra_add_count = extra_add_count
        return self.save_ut()

    def update_real_use_count(self):
        self.real_use_count += 1
        return self.save_ut()


class Share(BaseModel):
    """用户分享相关"""
    SHARE_TYPE = (
        (0, "装修报价"),
        (1, "海报"),
        (2, "文章"),
        (3, "课堂"),
        (4, "视频")
    )
    wx_user_id = IntegerField()  # 微信用户id
    tid = IntegerField(choices=SHARE_TYPE)  # 分享产品类型
    cid = IntegerField()  # 所属产品id（海报，文章，课堂，视频）
    share_time = DateTimeField(default=datetime.now)  # 分享时间
    real_use_count = IntegerField(default=0)

    class Meta:
        table_name = "share"

    @classmethod
    def new(cls, wx_user_id, tid, cid):
        return cls.create(
            wx_user_id=wx_user_id,
            tid=tid,
            cid=cid
        )

    def update_real_use_count(self):
        self.real_use_count += 1
        return self.save_ut()


class Visitor(BaseModel):
    """访客记录表"""
    wx_user_id = IntegerField()
    share_id = IntegerField(null=True)
    visitor_wx_user_id = IntegerField()  # 访客用户id
    visit_time = DateTimeField(default=datetime.now)

    class Meta:
        table_name = "visitor"

    @classmethod
    def new(cls, wx_user_id, visitor_wx_user_id, share_id):
        return cls.create(
            wx_user_id=wx_user_id,
            visitor_wx_user_id=visitor_wx_user_id,
            share_id=share_id
        )


class Area(BaseModel):
    """地区信息表"""
    name = CharField()
    pid = IntegerField(null=True)

    class Meta:
        table_name = 'area'

    @classmethod
    def new(cls, name, pid):
        return cls.create(
            name=name,
            pid=pid
        )


models = [Admin, WXUser, Banner, PosterType, Poster, PosterTheme, ArticleType, WXUserArticleTypeThrough, Article,
          Course, Video, Share, Visitor, Area]
