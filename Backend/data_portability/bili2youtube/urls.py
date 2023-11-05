from django.urls import path
from . import views

urlpatterns = [
    path("migrate_uploader", views.migrate_uploader, name="migrate_uploader"),
    path("migrate_viewer", views.migrate_viewer, name="migrate_viewer"),
    path("bilibili/qrcode", views.get_Bilibili_QRcode, name="login_bilibili_qrcode"),
    path("bilibili/qrcode/poll", views.check_Bilibili_QRcode, name="login_bilibili_qrcode_check"),
    path("B2Y/uploader", views.B2Y_get_uploader_info, name="B2Y_uploader_get"),
]
