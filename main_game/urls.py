from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^create_new_game/$', views.create_new_game),
    url(r'^validate_game/$', views.validate_game),
    url(r'^games/(?P<name>(\w)+)/$', views.show_game),
    url(r'^games/(?P<name>(\w)+)/mark/$', views.mark),
]
