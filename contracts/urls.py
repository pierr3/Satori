from django.urls import path

from . import views

urlpatterns = [
    path('create', views.create),
    path('pending', views.pending),
    path('view/<int:contract_id>', views.view),
    path('view/<int:contract_id>/version/<int:contract_version>', views.view),
    path('upload_version/<int:contract_id>', views.upload_version)
]