import os
from pathlib import Path

from django.core.management.base import BaseCommand

from weight_points_plus.foods_recipes.management.commands.utils import seed_foods


class Command(BaseCommand):
    help = "Delete and re-create basic foods in the database"

    def handle(self, *args, **options):
        base = Path(os.path.dirname(os.path.realpath(__file__)))
        seed_foods(base / "../../../fixtures/food_seed.csv", delete_foods=True)
        seed_foods(base / "../../../fixtures/free_foods_seed.csv")
