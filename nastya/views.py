from django.forms import CharField, Form
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from db.condition import Condition
from nastya.const import AUTH_COOKIE
from nastya.decorators import auth_required
from nastya.mappers import UserMapper, HotelMapper, HotelCategoryMapper, TagMapper, TagLinkMapper
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
    tag_mapper = TagMapper()
    taglink_mapper = TagLinkMapper()
    model = User

    def add_tags_to_hotels(self, hotels, tags):
        taglinks = self.taglink_mapper.select()
        # Экономим запросы в базу
        hotel_id_to_tag = {}
        __tag_id_map = {}
        for tag in tags:
            __tag_id_map[tag.id] = tag
        for link in taglinks:
            hotel_id_to_tag.setdefault(link.h_id, [])
            hotel_id_to_tag[link.h_id].append(__tag_id_map[link.t_id])

        for h in hotels:
            h.tags = hotel_id_to_tag.get(h.id, [])

    def get(self, request):
        categories = self.category_mapper.select()
        # hotels = self.get_hotels_list(categories)
        category_tree = Tree(categories).build_tree()
        tags = self.tag_mapper.select()
        c = Condition()

        cids = [c.id for c in categories]

        if 'cids[]' in self.request.GET:
            cids = [int(cid) for cid in self.request.GET.getlist('cids[]')]
            c &= Condition("category", cids)
        tag_titles = []
        if "tags[]" in self.request.GET:
            tag_titles = [str(ttitle) for ttitle in self.request.GET.getlist('tags[]') if ttitle]
            if tag_titles:
                tag_ids = [x.id for x in self.tag_mapper.select(Condition("title", tag_titles))]
                taglinks = self.taglink_mapper.select(Condition("t_id", tag_ids, action="IN"))
                c &= Condition("id", [x.id for x in taglinks])
        if 'search_string' in self.request.GET:
            c &= Condition('title', "%" + self.request.GET['search_string'] + "%", action='LIKE')
        found_hotels = self.hotel_mapper.select(c)
        self.add_tags_to_hotels(found_hotels, tags)
        return render(
            request,
            'index.html',
            {
                'tags': tags,
                'ct_tree': category_tree,
                'found_hotels': found_hotels,
                'checked': [int(cid) for cid in cids],
                'selected_tags': tag_titles
            })


class AuthDD(View):
    mapper = UserMapper()

    class AuthForm(Form):
        login = CharField(label='Логин', max_length=25)
        password = CharField(label='Пароль', max_length=25)

    def get(self, request):
        form = self.AuthForm()
        return render(request, 'auth.html', {"form": form, "no_auth": request.GET.get("no_auth", 0)})

    def post(self, request):
        form = self.AuthForm(data=request.POST)
        if not form.is_valid():
            return HttpResponseRedirect(reverse('auth') + "?no_auth=1")

        users = self.mapper.select(Condition('login', form.cleaned_data['login']) & Condition('password', form.cleaned_data['password']))
        if not users:
            return HttpResponseRedirect(reverse('auth') + "?no_auth=1")
        elif len(users) > 1:
            raise RuntimeError("login should be unique")
        response = HttpResponseRedirect(reverse('index'))
        response.set_cookie(AUTH_COOKIE, users[0].id)
        return response


class CompareDD(View):
    hotel_mapper = HotelMapper()
    tag_mapper = TagMapper()
    taglink_mapper = TagLinkMapper()
    category_mapper = HotelCategoryMapper()

    def add_tags_to_hotels(self, hotels):
        tags = self.tag_mapper.select()
        taglinks = self.taglink_mapper.select()
        # Экономим запросы в базу
        hotel_id_to_tag = {}
        __tag_id_map = {}
        for tag in tags:
            __tag_id_map[tag.id] = tag
        for link in taglinks:
            hotel_id_to_tag.setdefault(link.h_id, [])
            hotel_id_to_tag[link.h_id].append(__tag_id_map[link.t_id])

        for h in hotels:
            h.tags = hotel_id_to_tag.get(h.id, [])

    def add_category_to_hotels(self, hotels):
        categories = self.category_mapper.select()
        # Экономим запросы в базу
        hotel_id_to_category = {}
        for c in categories:
            hotel_id_to_category[c.id] = c

        for h in hotels:
            h.category = hotel_id_to_category.get(int(h.category), None)

    @auth_required
    def get(self, request):
        ids = request.COOKIES.get('compare', '').split(' ')
        if not ids:
            return render(request, 'compare.html')
        cond = Condition('id', ids)
        hotels = self.hotel_mapper.select(cond)
        self.add_tags_to_hotels(hotels)
        self.add_category_to_hotels(hotels)
        return render(request, 'compare.html', {'hotels': hotels, 'width': 420 * len(hotels)})
