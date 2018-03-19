# Generated by Django 2.0.3 on 2018-03-19 00:34

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('templateStorage', '0004_auto_20180318_2321'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contracttemplate',
            name='original_file',
            field=models.FileField(upload_to='repository/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['docx'])]),
        ),
    ]
