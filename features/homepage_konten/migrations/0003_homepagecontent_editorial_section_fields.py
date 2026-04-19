from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("homepage_konten", "0002_homepagestatisticitem"),
    ]

    operations = [
        migrations.AddField(
            model_name="homepagecontent",
            name="contact_description",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="homepagecontent",
            name="contact_title",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="homepagecontent",
            name="gallery_description",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="homepagecontent",
            name="gallery_title",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="homepagecontent",
            name="potential_opportunities_title",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="homepagecontent",
            name="potential_title",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="homepagecontent",
            name="recovery_description",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="homepagecontent",
            name="recovery_title",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
    ]
