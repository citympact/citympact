# Generated by Django 3.2.8 on 2021-12-08 09:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mainApp', '0007_auto_20211207_1941'),
    ]

    operations = [
        migrations.CreateModel(
            name='PetitionComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('validated', models.BooleanField()),
                ('name_displayed', models.BooleanField()),
                ('comment', models.TextField()),
                ('petition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainApp.petition')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('visitor', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='mainApp.visitor')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]