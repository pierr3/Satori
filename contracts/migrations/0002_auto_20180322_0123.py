# Generated by Django 2.0.3 on 2018-03-22 01:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='importance',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contract',
            name='summary',
            field=models.TextField(default='test'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contract',
            name='value',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]