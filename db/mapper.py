from collections import OrderedDict

from db.condition import Condition
from db.db import Database


class BaseMapper:
    model = None
    table_name = None

    def db_obj_map(self) -> OrderedDict:
        # Порядок важен, поэтому OrderedDict
        # Для None должен возвращаться словарь с пустыми значениями
        raise NotImplementedError

    def map_to_db(self, obj) -> OrderedDict:
        new_map = OrderedDict()
        for db_field, obj_field in self.db_obj_map().keys():
            new_map[db_field] = getattr(obj, obj_field)
        return new_map

    def _insert(self, obj, method='INSERT'):
        _map = self.map_to_db(obj)
        fields = ', '.join(_map.keys())
        values = ':' + ', :'.join(_map.keys())
        sql = "{method} INTO {table_name} ({fields}) VALUES ({values})"
        sql = sql.format(method=method, table_name=self.table_name, fields=fields, values=values)
        return Database.execute(sql, _map).rowcount

    def insert(self, obj):
        return self._insert(obj, 'INSERT')

    def update(self, obj):
        return self._insert(obj, 'REPLACE')

    def select(self, condition: Condition=None):
        _map = self.db_obj_map()
        fields = ', '.join(_map.keys())
        sql = "SELECT {fields} FROM {table_name}".format(fields=fields, table_name=self.table_name)
        where_params, where_sql = [], None
        if condition is not None:
            where_sql, where_params = condition.sql(self.db_obj_map())
            if where_sql:
                sql += " WHERE {where}".format(where=where_sql)
        result = []
        for row in Database.execute(sql, where_params).fetchall():
            result.append(self.model(*row))
        return result
