# Generated by Django 4.2.1 on 2023-06-10 20:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_item_facts_updated_at_item_listsings_updated_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='datacenter',
            field=models.ForeignKey(default=5, on_delete=django.db.models.deletion.CASCADE, related_name='listings', to='app.datacenter'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sale',
            name='datacenter',
            field=models.ForeignKey(default=5, on_delete=django.db.models.deletion.CASCADE, related_name='sales', to='app.datacenter'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='worlditemfact',
            name='datacenter',
            field=models.ForeignKey(default=5, on_delete=django.db.models.deletion.CASCADE, related_name='facts', to='app.datacenter'),
            preserve_default=False,
        ),
    ]
