from django.urls import path
from . import views

urlpatterns = [
    path("B2Y/migrate_uploader", views.migrate_uploader, name="migrate_uploader"),
    path("B2Y/migrate_viewer", views.migrate_viewer, name="migrate_viewer"),
    # path("B2Y/migrate_uploader_all", views.migrate_uploader_all, name="migrate_uploader_all"),
    # path("B2Y/migrate_viewer_all", views.migrate_viewer_all, name="migrate_viewer_all"),
    path("bilibili/qrcode", views.get_Bilibili_QRcode, name="login_bilibili_qrcode"),
    path(
        "bilibili/qrcode/poll",
        views.check_Bilibili_QRcode,
        name="login_bilibili_qrcode_check",
    ),
    path("B2Y/uploader", views.B2Y_get_uploader_info, name="B2Y_uploader_get"),
    path("B2Y/viewer", views.B2Y_get_viewer_info, name="B2Y_viewer_get"),
]
