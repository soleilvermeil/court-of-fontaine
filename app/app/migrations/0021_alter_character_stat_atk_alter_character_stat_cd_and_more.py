# Generated by Django 4.2.7 on 2024-01-08 09:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0020_character_stat_atk_character_stat_cd_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="character",
            name="stat_atk",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="character",
            name="stat_cd",
            field=models.DecimalField(decimal_places=1, default=0, max_digits=5),
        ),
        migrations.AlterField(
            model_name="character",
            name="stat_cr",
            field=models.DecimalField(decimal_places=1, default=0, max_digits=5),
        ),
        migrations.AlterField(
            model_name="character",
            name="stat_def",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="character",
            name="stat_em",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="character",
            name="stat_er",
            field=models.DecimalField(decimal_places=1, default=0, max_digits=5),
        ),
        migrations.AlterField(
            model_name="character",
            name="stat_hp",
            field=models.IntegerField(default=0),
        ),
    ]
