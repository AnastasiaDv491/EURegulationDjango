# Generated by Django 3.2.7 on 2023-07-06 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("db", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="fxpair",
            name="code",
            field=models.CharField(
                db_index=True, default="XXXYYY", max_length=6, unique=True
            ),
            preserve_default=False,
        )
    ]
