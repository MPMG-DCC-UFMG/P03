# Generated by Django 3.0.5 on 2020-10-21 18:11

from django.db import migrations

def insert_configs_data(apps, schema_editor):
        
        SearchConfigs = apps.get_model('services', 'SearchConfigs')
        for row in SearchConfigs.objects.all():
            row.delete()
        SearchConfigs(results_per_page = 10).save()

class Migration(migrations.Migration):

    dependencies = [
        ('services', '0011_auto_20201018_1925'),
    ]

    operations = [
        migrations.RunPython(insert_configs_data),
    ]
