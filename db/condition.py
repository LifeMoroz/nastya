from datetime import datetime


class Logic:
    def __or__(self, other):
        new_q = Query()
        if isinstance(other, Query):
            new_q.stack.append((self, other, '|'))
        if isinstance(other, Condition):
            new_q.stack.append((self, other, '|'))
        return new_q

    def __and__(self, other):
        new_q = Query()
        if isinstance(other, Query):
            new_q.stack.append((self, other, '&'))
        if isinstance(other, Condition):
            new_q.stack.append((self, other, '&'))
        return new_q

    def sql(self, fields_map=None):
        raise NotImplementedError


class Query(Logic):
    def __init__(self):
        self.stack = []

    # noinspection PyMethodMayBeStatic
    def sql(self, fields_map=None):
        sql = ''
        left_params = []
        right_params = []
        for left, right, type in self.stack:
            operator = ' AND ' if type == '&' else ' OR '
            left_sql, left_params = left.sql(fields_map=fields_map)
            right_sql, right_params = right.sql(fields_map=fields_map)
            sql = '(' + left_sql + operator + right_sql + ')'
        return sql, left_params + right_params

    def __str__(self):
        return self.sql(self.stack)[0]


class Condition(Logic):
    def _get_action_by_value(self, value):
        if isinstance(value, str):
            return 'LIKE ?'
        if hasattr(value, '__iter__'):
            return 'IN (?)'
        return '=?'

    def __init__(self, field, value, action=None):
        self.field = field
        self.action = action
        self.action = self._get_action_by_value(value)
        if hasattr(value, '__iter__') and not isinstance(value, str):
            value = ', '.join(value)
            self.action = self.action.replace('?', value)
            self.value = None
        else:
            self.value = value

    def sql(self, fields_map=None):
        field = self.field
        if fields_map:
            field = fields_map.get(self.field, self.field)
        if isinstance(self.value, datetime):
            self.value = self.value.timestamp() * 1000
        return field + ' ' + self.action, [self.value] if self.value is not None else []

