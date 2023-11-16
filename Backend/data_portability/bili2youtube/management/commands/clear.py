from django.core.management.base import BaseCommand
from bili2youtube.models import UserIDMapping, VideoIDMapping


class Command(BaseCommand):
    help = "Clear all data from UserIDMapping, VideoIDMapping"

    def handle(self, *args, **kwargs):
        UserIDMapping.objects.all().delete()
        VideoIDMapping.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS("Successfully cleared UserIDMapping, VideoIDMapping")
        )
