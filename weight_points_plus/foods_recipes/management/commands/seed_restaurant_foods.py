import os
from pathlib import Path

from django.core.management import CommandParser
from django.core.management.base import BaseCommand

from weight_points_plus.foods_recipes.management.commands.utils import seed_foods


class Command(BaseCommand):
    help = "Delete and re-create basic foods in the database"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "letter",
            help="Pass a letter to only seed restaurants that start with that letter",
        )

    def handle(self, *args, **options):
        base = Path(os.path.dirname(os.path.realpath(__file__)))
        file_name = base / "../../../fixtures/restaurant_foods_cleaned.csv"
        if options.get("letter") is not None:
            file_name = (
                base / f"../../../fixtures/restaurant_foods_{options.get('letter')}.csv"
            )
        new_foods, excluded_foods = seed_foods(
            file_name,
            restaurant_foods=True,
            delete_foods=False,
        )
        self.stdout.write(
            self.style.SUCCESS(f"Successfully added {new_foods} basic foods")
        )
        if len(excluded_foods) > 0:
            self.stdout.write(
                self.style.ERROR(f"There were {len(excluded_foods)} foods not created.")
            )
            for food in excluded_foods:
                self.stdout.write(food)
