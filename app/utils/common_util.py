import string
from enum import Enum
from random import choice

from app.models import Area


def gen_random_str(length=8, chars=string.ascii_letters + string.digits + string.punctuation):
    """
    生成随机密码

    :return:
    """
    return ''.join([choice(chars) for i in range(length)])


class EnumBase(Enum):
    """
    enum基类
    """
    @classmethod
    def is_contained(cls, value):
        for name, member in cls.__members__.items():
            if value == member.value:
                return True

    @classmethod
    def get_value_list(cls):
        value_list = []
        for name, member in cls.__members__.items():
            value_list.append(member.value)
        return value_list


class FileType(EnumBase):
    """
    上传文件类型

    0 - 图片类型，如png/jpg等
    1 - 视频类型，如mp4等
    2 - 其他类型，如doc、pdf、excel等
    3 - 全景图
    4 - doc
    5 - pdf
    """
    IMAGE = 0
    VIDEO = 1
    OTHER = 2
    PANORAMA = 3
    DOC = 4
    PDF = 5


def get_detail_area_info(area_info_id):
    """获取地区全称"""
    area_list = []
    area = Area.get_by_id(area_info_id)
    area_list.append(area.name)
    if area.pid:
        query = Area.select().where(Area.id == area.pid)
        area_1 = None if query.count() < 1 else query[0]
        if area_1:
            area_list.append(area_1.name)
        if area_1.pid:
            query = Area.select().where(Area.id == area_1.pid)
            area_2 = None if query.count() < 1 else query[0]
            if area_2:
                area_list.append(area_2.name)

    area_str = ''.join(reversed(area_list))
    return area_str
