from django.forms import CharField, Form
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from db.condition import Condition
from nastya.const import AUTH_COOKIE
from nastya.decorators import auth_required
from nastya.mappers import UserMapper, HotelMapper, HotelCategoryMapper
from nastya.app_models import User


class Tree:
    def __init__(self, categories):
        self.categories = categories
        self.tree = []

    def add_childs(self, root, to):
        childs = [x for x in self.categories if x.parent == root.id]
        for child in childs:
            new = {'category': child, 'items': []}
            to.append(new)
            self.add_childs(child, new['items'])

    def build_tree(self):
        head = [x for x in self.categories if x.parent is None]
        for node in head:
            new = {'category': node, 'items': []}
            self.tree.append(new)
            self.add_childs(node, new['items'])
        return self.tree


# Ниже определены модели страниц
# Она знает какие мапперы использует и какие модели её неужны
# Отсюда логика размазывается по приложению.
class IndexDD(View):
    user_mapper = UserMapper()
    hotel_mapper = HotelMapper()
    category_mapper = HotelCategoryMapper()
    model = User

    def get_hotels_list(self, category_list):
        hotels = self.hotel_mapper.select()

        hotel_map = dict((x.id, []) for x in category_list)
        for hotel in hotels:
            if hotel.category:
                hotel_map[int(hotel.category)].append(hotel)
        return hotel_map

    @auth_required
    def get(self, request):
        categories = self.category_mapper.select()
        hotels = self.get_hotels_list(categories)
        category_tree = Tree(categories).build_tree()

        c = Condition()
        cids = [c.id for c in categories]
        if 'cids[]' in self.request.GET:
            cids = self.request.GET.getlist('cids[]')
            c &= Condition("category", cids)
        if 'search_string' in self.request.GET:
            c &= Condition('title', "%" + self.request.GET['search_string'] + "%", action='LIKE')
        found_hotels = self.hotel_mapper.select(c)
        return render(
            request,
            'index.html',
            {
                'user': self.user,
                'hotels': hotels,
                'ct_tree': category_tree,
                'found_hotels': found_hotels,
                'checked': [int(cid) for cid in cids]
            })


class AuthDD(View):
    mapper = UserMapper()

    class AuthForm(Form):
        login = CharField(label='Логин', max_length=25)
        password = CharField(label='Пароль', max_length=25)

    def get(self, request):
        form = self.AuthForm()
        return render(request, 'auth.html', {"form": form})

    def post(self, request):
        form = self.AuthForm(data=request.POST)
        if not form.is_valid():
            return HttpResponseRedirect('/')

        users = self.mapper.select(Condition('login', form.cleaned_data['login']) & Condition('password', form.cleaned_data['password']))
        if not users:
            return None
        elif len(users) > 1:
            raise RuntimeError("login should be unique")
        response = HttpResponseRedirect(reverse('index'))
        response.set_cookie(AUTH_COOKIE, users[0].id)
        return response


class CompareDD(View):
    hotel_mapper = HotelMapper()

    def get(self, request):
        ids = request.COOKIES.get('compare', '').split(' ')
        if not ids:
            return render(request, 'compare.html')
        cond = Condition('id', ids)
        hotels = self.hotel_mapper.select(cond)
        return render(request, 'compare.html', {'hotels': hotels, 'width': 420 * len(hotels)})
