# Generated by Django 4.2.1 on 2023-06-12 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_item_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='equip_level',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
