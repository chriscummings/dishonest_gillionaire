# Generated by Django 4.1.5 on 2023-02-12 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_worlditemfact_listing_hq_sale_hq'),
    ]

    operations = [
        migrations.CreateModel(
            name='RunTime',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('process_name', models.TextField()),
                ('process_caller', models.TextField()),
                ('started_at', models.DateTimeField()),
                ('ended_at', models.DateTimeField(null=True)),
                ('run_time', models.TextField(null=True)),
            ],
        ),
    ]