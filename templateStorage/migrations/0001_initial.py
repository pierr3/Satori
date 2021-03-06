# Generated by Django 2.0.3 on 2018-03-18 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ContractTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_file', models.FileField(upload_to='')),
                ('text_content', models.TextField(blank=True, null=True)),
                ('name', models.CharField(max_length=200)),
                ('publisher_name', models.CharField(max_length=200)),
                ('pub_date', models.DateTimeField(verbose_name='date published')),
            ],
        ),
    ]
