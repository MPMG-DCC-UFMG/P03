# Generated by Django 3.0.5 on 2020-11-20 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0017_auto_20201120_1049'),
    ]

    operations = [
        migrations.AddField(
            model_name='searchconfigs',
            name='id',
            field=models.AutoField(auto_created=True, default=1, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='searchconfigs',
            name='results_per_page',
            field=models.IntegerField(default=10),
        ),
    ]
