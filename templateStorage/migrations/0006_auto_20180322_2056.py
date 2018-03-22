# Generated by Django 2.0.3 on 2018-03-22 20:56

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('templateStorage', '0005_auto_20180319_0034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contracttemplate',
            name='original_file',
            field=models.FileField(upload_to='templates/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['docx'])]),
        ),
    ]
