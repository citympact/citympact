# Generated by Django 3.2.8 on 2021-11-12 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainApp', '0009_auto_20211105_1645'),
    ]

    operations = [
        migrations.AlterField(
            model_name='petition',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]