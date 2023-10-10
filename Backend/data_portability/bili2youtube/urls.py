from django.urls import path
from . import views

urlpatterns = [
    path("getdata", views.get_data, name="getdata"),
]
