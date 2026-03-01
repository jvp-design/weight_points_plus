from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("foods_recipes", "0008_fooditem_public"),
    ]

    operations = [
        migrations.AddField(
            model_name="fooditem",
            name="version",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name="fooditeminstance",
            name="food_version",
            field=models.PositiveIntegerField(default=1),
        ),
    ]
