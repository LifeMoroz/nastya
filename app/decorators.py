from django.http import HttpResponseRedirect
from django.urls import reverse

from db.condition import Condition
from app.const import AUTH_COOKIE
from app.mappers import UserMapper


def auth_required(view, *args, **kwargs):
    def wrapper(self, request, *args, **kwargs):
        user_cookie = request.COOKIES.get(AUTH_COOKIE)
        if user_cookie:
            users = UserMapper().select(Condition('id', user_cookie))
        if not user_cookie or not users:
            return HttpResponseRedirect(reverse('auth'))
        else:
            user = users[0]
        self.user = user
        return view(self, request, *args, **kwargs)
    return wrapper