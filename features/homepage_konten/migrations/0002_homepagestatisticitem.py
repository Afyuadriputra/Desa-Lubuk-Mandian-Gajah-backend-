from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("homepage_konten", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="HomepageStatisticItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("label", models.CharField(max_length=100)),
                ("value", models.CharField(max_length=100)),
                (
                    "homepage",
                    models.ForeignKey(on_delete=models.deletion.CASCADE, to="homepage_konten.homepagecontent"),
                ),
            ],
            options={
                "db_table": "homepage_statistic_item",
                "ordering": ["sort_order", "id"],
            },
        ),
    ]
