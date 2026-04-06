from django.urls import path
from . import views

urlpatterns = [
    path("resource/<int:resource_id>/", views.delete_resource_view, name="delete-resource"),
    path("resources/", views.list_resources_view, name="list-resources"),
]
