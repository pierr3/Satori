from django.urls import path

from . import views

urlpatterns = [
    path('create', views.create),
    path('pending', views.pending),
    path('view/<int:contract_id>', views.view)
]