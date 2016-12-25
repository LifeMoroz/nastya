# Domain models

class User:
    def __init__(self, id=None, login=None, password=None, first_name=None, last_name=None, phone=None):
        self.id = id
        self.login = login
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone

    @property
    def full_name(self):
        return self.first_name + ' ' + self.last_name


class Hotel:
    def __init__(self, id=None, title=None, category=None, address=None, rating=None, phone=None):
        self.id = id
        self.title = title
        self.category = category
        self.address = address
        self.rating = rating
        self.phone = phone

    # Логика сравнения отелей?
    def __lt__(self, other):
        return self.rating < other.rating

    def __gt__(self, other):
        return self.rating > other.rating


class HotelCategory:
    def __init__(self, id=None, title=None, parent=None):
        self.id = id
        self.title = title
        self.parent = parent
