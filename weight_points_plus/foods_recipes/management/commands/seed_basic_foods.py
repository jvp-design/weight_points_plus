import os
from pathlib import Path

from django.core.management.base import BaseCommand

from weight_points_plus.foods_recipes.management.commands.utils import seed_foods


class Command(BaseCommand):
    help = "Delete and re-create basic foods in the database"

    def handle(self, *args, **options):
        base = Path(os.path.dirname(os.path.realpath(__file__)))
        new_basic_foods, new_excluded = seed_foods(
            base / "../../../fixtures/food_seed.csv", delete_foods=True
        )
        self.stdout.write(
            self.style.SUCCESS(f"Successfully added {new_basic_foods} basic foods")
        )

        new_free_foods, free_excluded = seed_foods(
            base / "../../../fixtures/free_foods_seed.csv"
        )
        self.stdout.write(
            self.style.SUCCESS(f"Successfully added {new_free_foods} 0-point foods")
        )

        if len(new_excluded) > 0:
            self.stdout.write(
                self.style.ERROR(f"There were {len(new_excluded)} foods not created.")
            )
            for food in new_excluded:
                self.stdout.write(food)

        if len(free_excluded) > 0:
            self.stdout.write(
                self.style.ERROR(
                    f"There were {len(new_excluded)} 0-point foods not created."
                )
            )
            for food in free_excluded:
                self.stdout.write(food)
