from django.core.management.base import BaseCommand
from django.apps import apps
from django.db.utils import IntegrityError
import json


class Command(BaseCommand):
    help = "Load a fixture and ignore existing entries."

    # def add_arguments(self, parser):
    #     parser.add_argument("fixture", type=str, help="Path to the fixture file")

    def handle(self, *args, **options):
        # fixture_path = options["fixture"]
        fixture_paths = [
            "bili2youtube/prepare_data/user_id_mapping_fixture.json",
            "bili2youtube/prepare_data/video_id_mapping_fixture.json",
        ]
        for fixture_path in fixture_paths:
            # Load your fixture data
            with open(fixture_path, "r") as fixture_file:
                data = json.load(fixture_file)

            for entry in data:
                model_name = entry["model"]
                fields = entry["fields"]

                # Dynamically get the model class
                app_label, model_label = model_name.split(".")
                model = apps.get_model(app_label=app_label, model_name=model_label)

                # Check if the object already exists
                exist = (
                    model.objects.filter(buid=fields["buid"]).exists()
                    if model_name == "bili2youtube.useridmapping"
                    else model.objects.filter(bvid=fields["bvid"]).exists()
                )
                if not exist:
                    try:
                        model.objects.create(**fields)
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Successfully added {model_name} with {fields}"
                            )
                        )
                    except IntegrityError as e:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Could not add {model_name} with {fields}: {str(e)}"
                            )
                        )
                else:
                    self.stdout.write(
                        self.style.NOTICE(
                            f"Skipped existing {model_name} with {fields}"
                        )
                    )
