from django.db import models


class UserIDMapping(models.Model):
    buid = models.CharField(
        max_length=100, unique=True, verbose_name="Bilibili User ID"
    )
    yuid = models.CharField(max_length=100, unique=True, verbose_name="YouTube User ID")

    def __str__(self):
        return f"{self.buid} -> {self.yuid}"


class VideoIDMapping(models.Model):
    bvid = models.CharField(
        max_length=100, unique=True, verbose_name="Bilibili Video ID"
    )
    yvid = models.CharField(
        max_length=100, unique=True, verbose_name="YouTube Video ID"
    )

    def __str__(self):
        return f"{self.bvid} -> {self.yvid}"
