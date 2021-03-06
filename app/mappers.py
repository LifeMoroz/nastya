from collections import OrderedDict

from db.mapper import BaseMapper
from app.app_models import User, Hotel, HotelCategory, Tag, TagLink


class UserMapper(BaseMapper):
    model = User
    table_name = 'user'

    def db_obj_map(self) -> OrderedDict:
        new_map = OrderedDict()
        new_map['id'] = 'id'
        new_map['login'] = 'login'
        new_map['password'] = 'password'
        new_map['first_name'] = 'first_name'
        new_map['last_name'] = 'last_name'
        new_map['phone'] = 'phone'
        return new_map


class HotelMapper(BaseMapper):
    model = Hotel
    table_name = 'hotel'

    def db_obj_map(self) -> OrderedDict:
        new_map = OrderedDict()
        new_map['id'] = 'id'
        new_map['title'] = 'title'
        new_map['category'] = 'category'
        new_map['address'] = 'address'
        new_map['rating'] = 'rating'
        new_map['phone'] = 'phone'
        new_map['image'] = 'image'
        return new_map


class HotelCategoryMapper(BaseMapper):
    model = HotelCategory
    table_name = 'hotel_category'

    def db_obj_map(self) -> OrderedDict:
        new_map = OrderedDict()
        new_map['id'] = 'id'
        new_map['title'] = 'title'
        new_map['parent'] = 'parent'
        return new_map


class TagMapper(BaseMapper):
    model = Tag
    table_name = 'tag'

    def db_obj_map(self) -> OrderedDict:
        new_map = OrderedDict()
        new_map['id'] = 'id'
        new_map['title'] = 'title'
        return new_map


class TagLinkMapper(BaseMapper):
    model = TagLink
    table_name = 'tag_hotel_link'

    def db_obj_map(self) -> OrderedDict:
        new_map = OrderedDict()
        new_map['id'] = 'id'
        new_map['h_id'] = 'h_id'
        new_map['t_id'] = 't_id'
        return new_map
