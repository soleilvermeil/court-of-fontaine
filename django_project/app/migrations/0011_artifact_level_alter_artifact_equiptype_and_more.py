# Generated by Django 4.2.7 on 2023-12-03 14:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0010_substat_ismainstat_alter_substat_rolls"),
    ]

    operations = [
        migrations.AddField(
            model_name="artifact",
            name="level",
            field=models.IntegerField(default=0, max_length=2),
        ),
        migrations.AlterField(
            model_name="artifact",
            name="equiptype",
            field=models.CharField(
                choices=[
                    ("EQUIP_BRACER", "Flower"),
                    ("EQUIP_NECKLACE", "Feather"),
                    ("EQUIP_SHOES", "Sands"),
                    ("EQUIP_RING", "Goblet"),
                    ("EQUIP_DRESS", "Circlet"),
                ],
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="substat",
            name="rolls",
            field=models.IntegerField(default=0, max_length=1),
        ),
    ]
