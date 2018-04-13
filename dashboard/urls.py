from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('change_role', views.change_role, name='change_role')
]