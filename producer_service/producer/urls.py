from django.urls import path
from . import views

urlpatterns = [
    path("send-delete/<str:resource_id>/", views.send_delete, name="send-delete"),
]
