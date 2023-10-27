from django.urls import path
from . import views

urlpatterns = [
    path("migrate_uploader", views.migrate_uploader, name="migrate_uploader"),
    path("migrate_viewer", views.migrate_viewer, name="migrate_viewer"),
]
