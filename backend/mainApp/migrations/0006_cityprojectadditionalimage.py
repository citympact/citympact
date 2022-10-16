# Generated by Django 3.2.8 on 2022-10-14 22:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mainApp', '0005_cityprojectanswer'),
    ]

    operations = [
        migrations.CreateModel(
            name='CityProjectAdditionalImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('image', models.ImageField(upload_to='')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainApp.cityproject')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
