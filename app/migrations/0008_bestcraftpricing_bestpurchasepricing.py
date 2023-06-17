# Generated by Django 4.2.1 on 2023-06-17 11:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_rename_level_item_item_level'),
    ]

    operations = [
        migrations.CreateModel(
            name='BestCraftPricing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='BestPurchasePricing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('home_nq_sold_mean', models.FloatField(null=True)),
                ('home_nq_sold_median', models.FloatField(null=True)),
                ('home_nq_sold_mode', models.FloatField(null=True)),
                ('home_nq_sold_high', models.IntegerField(null=True)),
                ('home_nq_sold_low', models.IntegerField(null=True)),
                ('home_nq_sold_count', models.IntegerField(null=True)),
                ('home_nq_sellers_count', models.IntegerField(null=True)),
                ('home_hq_sold_mean', models.FloatField(null=True)),
                ('home_hq_sold_median', models.FloatField(null=True)),
                ('home_hq_sold_mode', models.FloatField(null=True)),
                ('home_hq_sold_high', models.IntegerField(null=True)),
                ('home_hq_sold_low', models.IntegerField(null=True)),
                ('home_hq_sold_count', models.IntegerField(null=True)),
                ('home_hq_sellers_count', models.IntegerField(null=True)),
                ('home_nq_list_mean', models.FloatField(null=True)),
                ('home_nq_list_median', models.FloatField(null=True)),
                ('home_nq_list_mode', models.FloatField(null=True)),
                ('home_nq_list_high', models.IntegerField(null=True)),
                ('home_nq_list_low', models.IntegerField(null=True)),
                ('home_nq_list_count', models.IntegerField(null=True)),
                ('home_nq_listers_count', models.IntegerField(null=True)),
                ('home_hq_list_mean', models.FloatField(null=True)),
                ('home_hq_list_median', models.FloatField(null=True)),
                ('home_hq_list_mode', models.FloatField(null=True)),
                ('home_hq_list_high', models.IntegerField(null=True)),
                ('home_hq_list_low', models.IntegerField(null=True)),
                ('home_hq_list_count', models.IntegerField(null=True)),
                ('home_hq_listers_count', models.IntegerField(null=True)),
                ('best_nq_listing_in_region_price', models.IntegerField(null=True)),
                ('best_hq_listing_in_region_price', models.IntegerField(null=True)),
                ('best_nq_listing_in_datacenter_price', models.IntegerField(null=True)),
                ('best_hq_listing_in_datacenter_price', models.IntegerField(null=True)),
                ('best_hq_listing_in_datacenter_world', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='app.world')),
                ('best_hq_listing_in_region_world', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='app.world')),
                ('best_nq_listing_in_datacenter_world', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='app.world')),
                ('best_nq_listing_in_region_world', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='app.world')),
                ('datacenter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.datacenter')),
                ('home', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.world')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.item')),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.region')),
            ],
        ),
    ]
