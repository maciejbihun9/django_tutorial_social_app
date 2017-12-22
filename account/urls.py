from django.conf.urls import url
from django.contrib.auth.views import login
from django.contrib.auth.views import logout
from django.contrib.auth.views import logout_then_login
from django.contrib.auth.views import password_change
from django.contrib.auth.views import password_change_done
from django.contrib.auth.views import password_reset
from django.contrib.auth.views import password_reset_done
from django.contrib.auth.views import password_change_done
from django.contrib.auth.views import password_reset_confirm
from django.contrib.auth.views import password_reset_complete
from . import views

urlpatterns = [
    # Poprzedni widok logowania.
    url(r'^$', views.dashboard, name='dashboard'),
    # moje widoki
    # url(r'^login/$', views.user_login, name='login'),
    # url(r'^logout/$', views.user_logout, name='logout'),

    url(r'^register/$', views.register, name='register'),
    url(r'^edit/$', views.edit, name='edit'),

    # Wzorce adresów URL dla widoków logowania i wylogowania.
    url(r'^logout/$', logout, name='logout'),
    url(r'^login/$', login, name='login'),
    # url(r'^logout-then-login/$', logout_then_login, name='logout_then_login'),

    # Adresy URL przeznaczone do obsługi zmiany hasła.
    url(r'^password-change/$', password_change, name='password_change'),
    url(r'^password-change/done/$', password_change_done, name='password_change_done'),

# Adresy URL przeznaczone do obsługi procedury zerowania hasła.
    url(r'^password-reset/$', password_reset , name='password_reset'),
    url(r'^password-reset/done/$', password_reset_done, name='password_reset_done'),
    url(r'^password-reset/confirm/(?P<uidb64>[-\w]+)/(?P<token>[-\w]+)/$', password_reset_confirm, name='password_reset_confirm'),
    url(r'^password-reset/complete/$', password_reset_complete, name='password_reset_complete'),

    # url profilu użytkownika
    url(r'^users/$', views.user_list, name='user_list'),

    # musi być przed wzorcem url detail
    url(r'^users/follow/$', views.user_follow, name='user_follow'),

    url(r'^users/(?P<username>[-\w]+)/$', views.user_detail, name='user_detail'),

]