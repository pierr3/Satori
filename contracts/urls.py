from django.urls import path

from . import views

urlpatterns = [
    path('create', views.create, name='create'),
    path('pending', views.pending, name='pending'),
]